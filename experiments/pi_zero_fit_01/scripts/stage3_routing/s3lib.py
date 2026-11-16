"""Stage 3 (routing) helpers for experiment pi_zero_fit_01. Run with KiCad's own python (pcbnew).

All coordinates in the scripts are "new frame" mm: board coordinate - (113.47, 89.34).
What is here:
  Geo          a plain-geometry model of the copper on the board, used to pre-check a planned track or via against
               other nets BEFORE it is added (kicad-cli DRC is the judge afterwards; this only saves round trips).
  Router       adds tracks / vias / zones (only ever adds), keeps a list of what it added, fills zones, saves.
  snapshot / verify_lock   every footprint, track, via and zone of the input board must still be there, unchanged.
"""
import pcbnew, math, json, sys, hashlib

DX, DY, W, H, RAD = 113.47, 89.34, 65.0, 39.5, 3.0
mm, IU = pcbnew.ToMM, pcbnew.FromMM
V = lambda x, y: pcbnew.VECTOR2I(IU(x + DX), IU(y + DY))
N = lambda p: (round(mm(p.x) - DX, 4), round(mm(p.y) - DY, 4))
sn = lambda n: n.split('/')[-1]
HOLES = ((3.5, 3.5), (61.5, 3.5), (3.5, 26.5), (61.5, 26.5))      # Pi mounting holes
HOLE_KEEP_OUTER, HOLE_KEEP_INNER = 3.0, 3.0                        # screw keep-out rule areas (phase B) are r 3.0 on every copper layer
EDGE = 0.5                                                         # min_copper_edge_clearance in the .kicad_pro
SIG = ('Top Layer', 'Internal 1', 'Internal 2', '6 Bottom Layer')
PLANES = ('GND Plane', 'PWR Plane')

# ---------- plain geometry ----------
def _pt_seg(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay; L = dx * dx + dy * dy
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)
def _ccw(a, b, c): return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
def seg_seg(a, b, c, d):
    if (a != b and c != d):
        d1, d2, d3, d4 = _ccw(c, d, a), _ccw(c, d, b), _ccw(a, b, c), _ccw(a, b, d)
        if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)) and d1 * d2 != 0 and d3 * d4 != 0: return 0.0
    return min(_pt_seg(a[0], a[1], c[0], c[1], d[0], d[1]), _pt_seg(b[0], b[1], c[0], c[1], d[0], d[1]),
               _pt_seg(c[0], c[1], a[0], a[1], b[0], b[1]), _pt_seg(d[0], d[1], a[0], a[1], b[0], b[1]))
def in_poly(p, pts):
    x, y = p; c = False; n = len(pts); j = n - 1
    for i in range(n):
        xi, yi = pts[i]; xj, yj = pts[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi: c = not c
        j = i
    return c
def seg_poly(a, b, rings):
    """distance from segment a-b to a filled polygon (rings[0] outline, rest holes); 0 if inside."""
    if in_poly(a, rings[0]) and not any(in_poly(a, h) for h in rings[1:]): return 0.0
    best = 1e9; lo = (min(a[0], b[0]), min(a[1], b[1])); hi = (max(a[0], b[0]), max(a[1], b[1]))
    for r in rings:
        n = len(r)
        for i in range(n):
            c, d = r[i], r[(i + 1) % n]
            if min(c[0], d[0]) - hi[0] > best or lo[0] - max(c[0], d[0]) > best or min(c[1], d[1]) - hi[1] > best or lo[1] - max(c[1], d[1]) > best: continue
            s = seg_seg(a, b, c, d)
            if s < best: best = s
    return best
def edge_margin(p):
    """how far point p is inside the board outline (negative = outside)."""
    cx = min(max(p[0], RAD), W - RAD); cy = min(max(p[1], RAD), H - RAD)
    return RAD - math.hypot(p[0] - cx, p[1] - cy)

_CU = None
class Geo:
    def __init__(self, board, skip_zone_nets=()):
        self.L = {}       # layer name -> list of (kind, net, bbox, data, desc);  kind: cap (a, b, r) | rect (x0,y0,x1,y1) | poly rings
        self.holes = []   # (x, y, r, need, net, desc): drilled holes, 'need' = hole clearance to other copper
        global _CU
        if _CU is None: _CU = list(board.GetEnabledLayers().CuStack())     # asked once: a second call after Remove() upsets SWIG
        cu = [board.GetLayerName(l) for l in _CU]
        for n in cu: self.L[n] = []
        for t in board.GetTracks():
            net = sn(t.GetNetname())
            if t.GetClass() == 'PCB_VIA':
                p = N(t.GetStart()); r = mm(t.GetWidth(pcbnew.F_Cu)) / 2
                for n in cu: self._add(n, 'cap', net, (p, p, r), 'via %s (%.2f, %.2f)' % (net, *p))
                self.holes.append((p[0], p[1], mm(t.GetDrillValue()) / 2, 0.25, net, 'via hole %s (%.2f, %.2f)' % (net, *p)))
            else:
                a, b = N(t.GetStart()), N(t.GetEnd())
                self._add(t.GetLayerName(), 'cap', net, (a, b, mm(t.GetWidth()) / 2), 'track %s %s (%.2f, %.2f)-(%.2f, %.2f)' % (net, t.GetLayerName(), *a, *b))
        for f in board.GetFootprints():
            for p in f.Pads():
                net = sn(p.GetNetname()); bb = p.GetBoundingBox(); x0, y0 = N(bb.GetPosition()); x1, y1 = N(bb.GetEnd())
                desc = 'pad %s.%s %s' % (f.GetReference(), p.GetNumber(), net)
                th = p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH)
                if th and p.GetDrillSize().x > 0:
                    c = N(p.GetPosition()); ds = p.GetDrillSize()
                    self.holes.append((c[0], c[1], mm(max(ds.x, ds.y)) / 2, 0.3, net, desc + ' hole'))
                if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH: continue
                w, h = x1 - x0, y1 - y0; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
                try: shp = p.GetShape(pcbnew.F_Cu)
                except TypeError: shp = p.GetShape()
                if shp in (pcbnew.PAD_SHAPE_CIRCLE, pcbnew.PAD_SHAPE_OVAL):
                    r = min(w, h) / 2
                    item = ('cap', ((cx - (w / 2 - r), cy - (h / 2 - r)), (cx + (w / 2 - r), cy + (h / 2 - r)), r))
                else: item = ('rect', (x0, y0, x1, y1))
                for l in p.GetLayerSet().CuStack(): self._add(board.GetLayerName(l), item[0], net, item[1], desc)
        cuset = set(_CU)
        for d in board.GetDrawings():                      # Sofar's copper polygons / rectangles drawn as graphics
            if d.GetLayer() not in cuset or d.GetClass() != 'PCB_SHAPE': continue
            net = sn(d.GetNetname()); bb = d.GetBoundingBox(); x0, y0 = N(bb.GetPosition()); x1, y1 = N(bb.GetEnd())
            desc = 'copper shape %s %s (%.2f, %.2f)-(%.2f, %.2f)' % (net, d.GetLayerName(), x0, y0, x1, y1)
            ps = d.GetPolyShape() if d.GetShape() == pcbnew.SHAPE_T_POLY else None
            if ps is not None and ps.OutlineCount():
                self._add(d.GetLayerName(), 'poly', net, [[N(ps.Outline(0).CPoint(k)) for k in range(ps.Outline(0).PointCount())]], desc)
            else: self._add(d.GetLayerName(), 'rect', net, (x0, y0, x1, y1), desc)
        for f in board.GetFootprints():                    # copper graphics inside footprints (jumper bridges): no net, always an obstacle
            for d in f.GraphicalItems():
                if d.GetLayer() in cuset:
                    bb = d.GetBoundingBox(); x0, y0 = N(bb.GetPosition()); x1, y1 = N(bb.GetEnd())
                    self._add(d.GetLayerName(), 'rect', '', (x0, y0, x1, y1), 'copper graphic in %s' % f.GetReference())
        for z in board.Zones():
            if z.GetIsRuleArea() or sn(z.GetNetname()) in skip_zone_nets and z.GetZoneName().startswith('S3 '): continue
            if z.GetZoneName().startswith('S3 '): continue          # our own new fills give way to tracks; never an obstacle
            for l in z.GetLayerSet().CuStack():
                ps = z.GetFilledPolysList(l)
                for i in range(ps.OutlineCount()):
                    rings = [[N(ps.Outline(i).CPoint(k)) for k in range(ps.Outline(i).PointCount())]]
                    for hh in range(ps.HoleCount(i)):
                        rings.append([N(ps.Hole(i, hh).CPoint(k)) for k in range(ps.Hole(i, hh).PointCount())])
                    self._add(board.GetLayerName(l), 'poly', sn(z.GetNetname()), rings, 'zone fill %s %s' % (sn(z.GetNetname()) or '(no net)', z.GetZoneName()))
    def _add(self, layer, kind, net, data, desc):
        if kind == 'cap': (a, b, r) = data; bb = (min(a[0], b[0]) - r, min(a[1], b[1]) - r, max(a[0], b[0]) + r, max(a[1], b[1]) + r)
        elif kind == 'rect': bb = data
        else: xs = [p[0] for p in data[0]]; ys = [p[1] for p in data[0]]; bb = (min(xs), min(ys), max(xs), max(ys))
        if layer in self.L: self.L[layer].append((kind, net, bb, data, desc))
    def add_track(self, layer, net, a, b, w): self._add(layer, 'cap', net, (a, b, w / 2), 'S3 track %s %s (%.2f, %.2f)-(%.2f, %.2f)' % (net, layer, *a, *b))
    def add_via(self, net, p, d, drill):
        for n in self.L: self._add(n, 'cap', net, (p, p, d / 2), 'S3 via %s (%.2f, %.2f)' % (net, *p))
        self.holes.append((p[0], p[1], drill / 2, 0.25, net, 'S3 via hole %s (%.2f, %.2f)' % (net, *p)))

    def seg_gaps(self, layer, a, b, r, net, clr, zones=True):
        """items of other nets closer than clr to the capsule a-b radius r on layer. Returns [(gap, desc)]."""
        out = []; m = r + clr + 0.01
        lo = (min(a[0], b[0]) - m, min(a[1], b[1]) - m); hi = (max(a[0], b[0]) + m, max(a[1], b[1]) + m)
        for kind, n2, bb, data, desc in self.L[layer]:
            if n2 == net and net: continue
            if bb[0] > hi[0] or bb[2] < lo[0] or bb[1] > hi[1] or bb[3] < lo[1]: continue
            if kind == 'cap': g = seg_seg(a, b, data[0], data[1]) - data[2] - r
            elif kind == 'rect':
                x0, y0, x1, y1 = data; g = seg_poly(a, b, [[(x0, y0), (x1, y0), (x1, y1), (x0, y1)]]) - r
            else:
                if not zones: continue
                g = seg_poly(a, b, data) - r
            if g < clr - 1e-6: out.append((round(g, 3), desc))
        for hx, hy, hr, need, n2, desc in self.holes:
            if n2 == net and net: continue
            g = _pt_seg(hx, hy, a[0], a[1], b[0], b[1]) - hr - r
            if g < need - 1e-6: out.append((round(g, 3), desc + ' [hole clearance %.2f]' % need))
        keep = HOLE_KEEP_OUTER if layer in ('Top Layer', '6 Bottom Layer') else HOLE_KEEP_INNER
        for hx, hy in HOLES:
            g = _pt_seg(hx, hy, a[0], a[1], b[0], b[1]) - r - keep
            if g < -1e-6: out.append((round(g, 3), 'Pi hole keep-out r %.1f at (%.1f, %.1f)' % (keep, hx, hy)))
        for p in (a, b):
            g = edge_margin(p) - r - EDGE
            if g < -1e-6: out.append((round(g, 3), 'board edge (0.5 mm rule)'))
        return out
    def path(self, layer, pts, w, net, clr=0.15, zones=True):
        out = []
        for a, b in zip(pts, pts[1:]): out += self.seg_gaps(layer, a, b, w / 2, net, clr, zones)
        return sorted(set(out))
    def via(self, p, d, drill, net, clr=0.15, layers=None):
        out = []
        for layer in (layers or self.L):
            for g, desc in self.seg_gaps(layer, p, p, d / 2, net, clr, zones=layer not in PLANES):
                out.append((g, layer + ': ' + desc))
        for hx, hy, hr, need, n2, desc in self.holes:                 # our hole against their copper is covered above by their 'cap';
            g = math.hypot(hx - p[0], hy - p[1]) - hr - drill / 2      # hole to hole
            if 0 < math.hypot(hx - p[0], hy - p[1]) and g < 0.25: out.append((round(g, 3), 'hole to hole: ' + desc))
        return sorted(set(out))
    def window(self, layer, x0, y0, x1, y1, nets=None):
        for kind, n2, bb, data, desc in self.L[layer]:
            if bb[0] > x1 or bb[2] < x0 or bb[1] > y1 or bb[3] < y0: continue
            if nets and n2 not in nets: continue
            if kind == 'cap': print('   %-60s r %.3f' % (desc, data[2]))
            elif kind == 'rect': print('   %-60s box %.2f %.2f %.2f %.2f' % ((desc,) + tuple(data)))
            else: print('   %-60s poly bb %.2f %.2f %.2f %.2f' % ((desc,) + tuple(bb)))

# ---------- path shapes (45-degree corners) ----------
def vhv(a, b, m):
    """a -> vertical -> 45 -> horizontal at y = m -> 45 -> vertical -> b; chamfers sized to fit. Returns points or None."""
    return _three(a, b, m, False)
def hvh(a, b, m):
    return _three(a, b, m, True)
def _three(a, b, m, swap):
    if swap: a, b = (a[1], a[0]), (b[1], b[0])
    (ax, ay), (bx, by) = a, b; pts = [a]
    dxs = 1 if bx >= ax else -1
    c1 = min(abs(m - ay), abs(bx - ax) / 2, 1.0 if abs(m - ay) > 1.0 else abs(m - ay)); c2 = min(abs(by - m), abs(bx - ax) / 2, 1.0 if abs(by - m) > 1.0 else abs(by - m))
    s1 = 1 if m >= ay else -1; s2 = 1 if by >= m else -1
    if c1 + c2 > abs(bx - ax) + 1e-9: return None
    pts += [(ax, m - s1 * c1), (ax + dxs * c1, m), (bx - dxs * c2, m), (bx, m + s2 * c2), b]
    out = [pts[0]]
    for p in pts[1:]:
        if math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > 1e-6: out.append(p)
    out = [(round(x, 4), round(y, 4)) for x, y in out]
    return [(y, x) for x, y in out] if swap else out
def length(pts): return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))
def angles_ok(pts):
    for a, b in zip(pts, pts[1:]):
        dx, dy = abs(b[0] - a[0]), abs(b[1] - a[1])
        if not (dx < 1e-4 or dy < 1e-4 or abs(dx - dy) < 2e-3): return False
    return True

# ---------- board edits ----------
def prestep(path, base_path, removes=(), moves=()):
    """Run BEFORE Router(path), in a child process (pcbnew's SWIG layer does not survive Remove() followed by more queries, or a
    second LoadBoard, in one session). removes: [(net, layer | '*' (all layers and vias), optional box)] - tracks of that net which stage 3 itself added
    (uuid not in the board at base_path, commit d30920b) are removed. moves: [(ref, (x, y))] for non-core footprints."""
    import subprocess
    out = subprocess.run([sys.executable, __file__, '--pre', path, base_path, json.dumps([list(removes), list(moves)])], capture_output=True, text=True)
    print(out.stdout.strip())
    if out.returncode: raise SystemExit('prestep failed: ' + out.stderr[-800:])
def _prestep(path, base_path, spec):
    removes, moves = json.loads(spec); base = base_uuids(base_path); b = pcbnew.LoadBoard(path)
    for ref, pos in moves:
        f = b.FindFootprintByReference(ref); old = N(f.GetPosition()); f.SetPosition(V(*pos)); print('   moved %s %s -> %s' % (ref, old, tuple(pos)))
    kill = []; cnt = {}                      # one GetTracks() call, then the removals: nothing is queried after the first Remove()
    for t in b.GetTracks():
        if t.m_Uuid.AsString() in base: continue
        for spec in removes:
            net, layer = spec[0], spec[1]; box = spec[2] if len(spec) > 2 else None
            if sn(t.GetNetname()) != net: continue
            if layer and (t.GetClass() == 'PCB_VIA' or t.GetLayerName() != layer) and layer != '*': continue
            if box and not all(box[0] <= p[0] <= box[2] and box[1] <= p[1] <= box[3] for p in (N(t.GetStart()), N(t.GetEnd()))): continue
            kill.append(t); cnt[net] = cnt.get(net, 0) + 1; break
    for t in kill: b.Remove(t)
    print('   removed stage-3 items: %s' % cnt)
    pcbnew.SaveBoard(path, b)
def base_uuids(path, _c={}):
    """uuids of the tracks / vias in a board file, read as text (loading a second board in one pcbnew session upsets SWIG)."""
    if path not in _c:
        import re; _c[path] = set(re.findall(r'\(uuid "([0-9a-f-]{36})"\)', open(path).read()))
    return _c[path]
class Router:
    def __init__(self, path, phase):
        self.path, self.phase = path, phase
        self.b = pcbnew.LoadBoard(path)
        self.geo = Geo(self.b)
        self.lid = {self.b.GetLayerName(l): l for l in _CU}
        self.nets = {}
        for name, ni in self.b.GetNetsByName().items(): self.nets[sn(str(name))] = ni
        self.log = []      # dicts: net, layer, w, pts, len / via
        self.bad = []
    def net(self, name):
        if name not in self.nets: raise SystemExit('no such net: ' + name)
        return self.nets[name]
    def track(self, net, layer, pts, w, clr=0.15, note='', zones=True, allow=()):
        """add a polyline. Refuses (raises) if a segment is off the 0/45/90 grid; records pre-check hits in self.bad."""
        pts = [(round(x, 4), round(y, 4)) for x, y in pts]
        if not angles_ok(pts): raise SystemExit('%s: segment not on 0/45/90: %s' % (net, pts))
        hits = [h for h in self.geo.path(layer, pts, w, net, clr, zones) if not any(s in h[1] for s in allow)]
        if hits: self.bad.append((net, layer, pts, hits))
        ni = self.net(net)
        for a, b in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(self.b); t.SetStart(V(*a)); t.SetEnd(V(*b)); t.SetWidth(IU(w)); t.SetLayer(self.lid[layer]); t.SetNet(ni)
            self.b.Add(t); self.geo.add_track(layer, net, a, b, w)
        self.log.append({'net': net, 'layer': layer, 'w': w, 'pts': pts, 'len': round(length(pts), 2), 'note': note})
    def via(self, net, p, d=0.6, drill=0.3, clr=0.15, note='', allow=()):
        p = (round(p[0], 4), round(p[1], 4))
        hits = [h for h in self.geo.via(p, d, drill, net, clr) if not any(s in h[1] for s in allow)]
        if hits: self.bad.append((net, 'via', [p], hits))
        v = pcbnew.PCB_VIA(self.b); v.SetPosition(V(*p)); v.SetWidth(pcbnew.F_Cu, IU(d)) if _via_w_layer else v.SetWidth(IU(d))
        v.SetDrill(IU(drill)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(self.net(net))
        self.b.Add(v); self.geo.add_via(net, p, d, drill)
        self.log.append({'net': net, 'via': p, 'd': d, 'drill': drill, 'note': note})
    def zone(self, net, layer, pts, name, prio=1, clr=0.3, minw=0.25, solid=False):
        """a new filled zone, settings as the frozen board's own added zones (clearance 0.3, min width 0.25, thermal
        spokes 0.5 with 0.3 gap on pads, islands removed). Names start with 'S3 '."""
        z = pcbnew.ZONE(self.b); z.SetLayer(self.lid[layer]); z.SetNet(self.net(net)); z.SetZoneName('S3 ' + name)
        o = z.Outline(); o.NewOutline()
        for x, y in pts: o.Append(V(x, y).x, V(x, y).y)
        z.SetAssignedPriority(prio); z.SetLocalClearance(IU(clr)); z.SetMinThickness(IU(minw))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL if solid else pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetThermalReliefGap(IU(0.3)); z.SetThermalReliefSpokeWidth(IU(0.5))
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        self.b.Add(z); self.log.append({'zone': name, 'net': net, 'layer': layer, 'pts': pts, 'prio': prio})
        return z
    def keepout(self, centre, r, name, n=64):
        """screw keep-out as on the frozen board: all copper layers; tracks, vias and copper pour not allowed."""
        z = pcbnew.ZONE(self.b); z.SetIsRuleArea(True); z.SetZoneName('S3 ' + name)
        ls = pcbnew.LSET()
        for l in self.lid.values(): ls.AddLayer(l)
        z.SetLayerSet(ls); o = z.Outline(); o.NewOutline()
        for i in range(n):
            a = 2 * math.pi * i / n; p = V(centre[0] + r * math.cos(a), centre[1] + r * math.sin(a)); o.Append(p.x, p.y)
        z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True); z.SetDoNotAllowZoneFills(True); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
        self.b.Add(z); self.log.append({'zone': name, 'net': '', 'layer': 'all copper', 'pts': [centre], 'prio': 0})
        return z
    def report_bad(self):
        for net, layer, pts, hits in self.bad:
            print('PRE-CHECK %s %s %s' % (net, layer, pts if len(pts) < 4 else '%s..%s' % (pts[0], pts[-1])))
            for g, d in hits[:8]: print('      gap %.3f  %s' % (g, d))
        return len(self.bad)
    def finish(self, out=None, logfile=None):
        pcbnew.ZONE_FILLER(self.b).Fill(self.b.Zones())
        for z in self.b.Zones():
            if z.GetZoneName().startswith('S3 ') and not z.GetIsRuleArea():
                z.CalculateFilledArea(); ps = z.GetFilledPolysList(z.GetLayer())
                print('   zone %-34s %-10s %-9s filled %.1f mm2 in %d piece(s)' % (z.GetZoneName(), sn(z.GetNetname()), z.GetLayerName(), z.GetFilledArea() / 1e12, ps.OutlineCount()))
        pcbnew.SaveBoard(out or self.path, self.b)
        if logfile: json.dump(self.log, open(logfile, 'w'), indent=0)
        tr = [e for e in self.log if 'pts' in e and 'zone' not in e and 'net' in e]; vi = [e for e in self.log if 'via' in e]
        print('phase %s: %d polylines (%.1f mm), %d vias, %d zones added; pre-check hits: %d' % (
            self.phase, len(tr), sum(e['len'] for e in tr), len(vi), len([e for e in self.log if 'zone' in e]), len(self.bad)))
    def summary(self):
        """per net: layer, width, length, vias (for the report)."""
        nets = {}
        for e in self.log:
            if 'zone' in e or 'removed' in e or 'moved' in e: continue
            d = nets.setdefault(e['net'], {'seg': {}, 'vias': 0})
            if 'via' in e: d['vias'] += 1
            else: k = (e['layer'], e['w']); d['seg'][k] = d['seg'].get(k, 0) + e['len']
        for n in sorted(nets):
            print('| %s | %s | %d |' % (n, '; '.join('%s %.2f mm wide, %.1f mm' % (k[0], k[1], v) for k, v in sorted(nets[n]['seg'].items())), nets[n]['vias']))
try:
    _v = pcbnew.PCB_VIA(None); _v.SetWidth(pcbnew.F_Cu, 1000); _via_w_layer = True
except Exception: _via_w_layer = False

# ---------- lock check ----------
def snapshot(board):
    s = {}
    for f in board.GetFootprints():
        pads = sorted((p.GetNumber(), p.GetPosition().x, p.GetPosition().y, p.GetNetname(), p.GetSize().x if not _via_w_layer else p.GetBoundingBox().GetWidth()) for p in f.Pads())
        s['F ' + f.m_Uuid.AsString()] = (f.GetReference(), f.GetPosition().x, f.GetPosition().y, round(f.GetOrientationDegrees(), 3), f.IsFlipped(), f.GetFPIDAsString(), hashlib.md5(repr(pads).encode()).hexdigest())
    for t in board.GetTracks():
        if t.GetClass() == 'PCB_VIA': sig = ('via', t.GetStart().x, t.GetStart().y, t.GetWidth(pcbnew.F_Cu) if _via_w_layer else t.GetWidth(), t.GetDrillValue(), t.GetNetname())
        else: sig = (t.GetClass(), t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y, t.GetWidth(), t.GetLayer(), t.GetNetname())
        s['T ' + t.m_Uuid.AsString()] = sig
    for z in board.Zones():
        o = z.Outline(); pts = [(o.CVertex(i).x, o.CVertex(i).y) for i in range(o.TotalVertices())]
        s['Z ' + z.m_Uuid.AsString()] = (z.GetNetname(), tuple(z.GetLayerSet().Seq()), z.GetAssignedPriority(), z.GetIsRuleArea(), z.GetZoneName(), hashlib.md5(repr(pts).encode()).hexdigest())
    cuset = set(board.GetEnabledLayers().CuStack())
    for d in board.GetDrawings():
        if d.GetLayer() in cuset:
            bb = d.GetBoundingBox(); s['D ' + d.m_Uuid.AsString()] = (d.GetClass(), d.GetLayer(), bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom())
    return s
MOVED_OK = ('J5', 'FID2', 'FID4')    # non-core footprints stage 3 was told to move (design session, BM1 trunk fix); pads and nets must still be the same
def verify_lock(ref_board_path, new_board_path, quiet=False):
    a, b = snapshot(pcbnew.LoadBoard(ref_board_path)), snapshot(pcbnew.LoadBoard(new_board_path))
    missing = [k for k in a if k not in b]; changed = [k for k in a if k in b and a[k] != b[k]]; added = [k for k in b if k not in a]
    moved = [k for k in changed if k[0] == 'F' and a[k][0] in MOVED_OK and a[k][3:6] == b[k][3:6]]
    changed = [k for k in changed if k not in moved]
    for k in moved: print('  moved on instruction (not core): %s (%.2f, %.2f) -> (%.2f, %.2f)' % (a[k][0], mm(a[k][1]) - DX, mm(a[k][2]) - DY, mm(b[k][1]) - DX, mm(b[k][2]) - DY))
    cnt = lambda ks, c: sum(1 for k in ks if k[0] == c)
    print('lock check against %s' % ref_board_path.split('/')[-1])
    print('  input items: %d footprints, %d tracks+vias, %d zones, %d copper graphics' % (cnt(a, 'F'), cnt(a, 'T'), cnt(a, 'Z'), cnt(a, 'D')))
    print('  missing: %d   changed: %d   added: %d footprints, %d tracks+vias, %d zones' % (len(missing), len(changed), cnt(added, 'F'), cnt(added, 'T'), cnt(added, 'Z')))
    for k in (missing + changed)[:20]: print('   !', k, a[k], b.get(k))
    ok = not missing and not changed and cnt(added, 'F') == 0
    print('  LOCK', 'PASS' if ok else 'FAIL')
    return ok

if __name__ == '__main__' and len(sys.argv) > 4 and sys.argv[1] == '--pre': _prestep(sys.argv[2], sys.argv[3], sys.argv[4])
