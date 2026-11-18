"""Full comparison of Sofar's mote reference board with a board of this project, item by item, by GEOMETRY (not by
uuid, so it does not lean on the lock checks of the stages).

KiCad's Python: motediff.py <mote reference .kicad_pcb> <starting board .kicad_pcb (325599c)> <board to check .kicad_pcb>

Three boards: REF = Sofar's mote (KiCAD_reference_designs/20250409_BM_Mote_000639-AB on development), START = the
board this branch started from (the Pi Zero shield, commit 325599c; the mote block sits at the reference's own
coordinates there), NOW = the board to check (the block is turned a quarter turn; the transform is taken from U1 and
L1 and must then reproduce everything else).
For every track, via, zone, rule area, copper drawing, footprint and pad of REF the script says: same in NOW, changed
in NOW, or missing in NOW, and for a missing or changed item whether START already differed (work before this
branch) or not (work of this branch). It also lists the copper that is in NOW inside the mote's outline and not in REF.
Frame of the printed coordinates: X' = KiCad x - 100, y = 100 - KiCad y on the NOW board (mm)."""
import sys, collections
import pcbnew
R, S, N = (pcbnew.LoadBoard(p) for p in sys.argv[1:4])
mm = pcbnew.ToMM
def P(*a): print(*a); sys.stdout.flush()
short = lambda n: str(n).split("/")[-1] or "(no net)"
def fpmap(b): return {f.GetReference(): f for f in b.GetFootprints()}
rf, sf, nf = fpmap(R), fpmap(S), fpmap(N)
u, l, u2, l2 = rf["U1"], rf["L1"], nf["U1"], nf["L1"]
assert sf["U1"].GetPosition() == u.GetPosition() and sf["L1"].GetPosition() == l.GetPosition(), "START does not hold the block at the reference's coordinates"
MATS = {90: (0, -1, 1, 0), -90: (0, 1, -1, 0), 0: (1, 0, 0, 1), 180: (-1, 0, 0, -1)}
dx, dy = l.GetPosition().x - u.GetPosition().x, l.GetPosition().y - u.GetPosition().y
ex, ey = l2.GetPosition().x - u2.GetPosition().x, l2.GetPosition().y - u2.GetPosition().y
rot = [k for k, m in MATS.items() if (m[0] * dx + m[1] * dy, m[2] * dx + m[3] * dy) == (ex, ey)]
assert len(rot) == 1, rot
M = MATS[rot[0]]
def T(x, y):
    x, y = x - u.GetPosition().x, y - u.GetPosition().y
    return (M[0] * x + M[1] * y + u2.GetPosition().x, M[2] * x + M[3] * y + u2.GetPosition().y)
I = lambda x, y: (x, y)
def XY(p): return "(%.3f, %.3f)" % (mm(p[0]) - 100, 100 - mm(p[1]))
P("transform REF -> NOW from U1 and L1: turn matrix %s; U1 %s on NOW" % (M, XY((u2.GetPosition().x, u2.GetPosition().y))))

# ---------------------------------------------------------------- net names: REF (Altium import) -> NOW, from the pads
# of the footprints that are on both boards. The two boards name nets differently, so nets are compared through this map.
ra, na = collections.defaultdict(set), collections.defaultdict(set); r2n = collections.defaultdict(collections.Counter)
for ref, f in rf.items():
    g = nf.get(ref)
    if g is None: continue
    gp = collections.defaultdict(set)
    for p in g.Pads(): gp[p.GetNumber()].add(short(p.GetNetname()))
    for p in f.Pads():
        a_ = short(p.GetNetname())
        for b_ in gp.get(p.GetNumber(), ()):
            ra[a_].add((ref, p.GetNumber())); na[b_].add((ref, p.GetNumber())); r2n[a_][b_] += 1
P("\nNETLIST among the mote's parts that are on both boards (%d parts, %d pads, %d REF nets):" % (sum(1 for r_ in rf if r_ in nf), sum(len(v) for v in ra.values()), len(ra)))
split = {a_: c for a_, c in r2n.items() if len(c) > 1 and a_ != "(no net)"}
n2r = collections.defaultdict(set)
for a_, c in r2n.items():
    for b_ in c: n2r[b_].add(a_)
merge = {b_: v for b_, v in n2r.items() if len(v) > 1 and b_ != "(no net)"}
P("  REF nets whose pads are on more than one net in NOW (a connection of the mote was cut): %d" % len(split))
for a_, c in sorted(split.items()):
    for b_ in c: P("    %s -> %s: %s" % (a_, b_, " ".join(sorted("%s.%s" % x for x in ra[a_] & na[b_]))))
P("  NOW nets that join pads of more than one REF net (two nets of the mote were joined): %d" % len(merge))
for b_, v in sorted(merge.items()):
    for a_ in sorted(v): P("    %s <- %s: %s" % (b_, a_, " ".join(sorted("%s.%s" % x for x in ra[a_] & na[b_]))))
P("  REF nets with the same pads and another name in NOW (renamed only): %d; same name: %d" % (
    sum(1 for a_, c in r2n.items() if len(c) == 1 and list(c)[0] != a_), sum(1 for a_, c in r2n.items() if len(c) == 1 and list(c)[0] == a_)))
def samenet(a_, b_): return a_ == b_ or b_ in r2n.get(a_, ()) or a_ not in r2n
NP = {True: "the net still has pads in NOW", False: "no pad of this net is left in NOW"}

# ---------------------------------------------------------------- tracks and vias
def titems(b, tf):
    out = []
    for t in b.GetTracks():
        ln = lambda l_: b.GetLayerName(l_)
        if t.Type() == pcbnew.PCB_VIA_T:
            p = tf(t.GetPosition().x, t.GetPosition().y)
            geo = ("via", p); prop = (t.GetWidth(pcbnew.F_Cu), t.GetDrill(), ln(t.TopLayer()), ln(t.BottomLayer()), short(t.GetNetname()))
        else:
            a, c = tf(t.GetStart().x, t.GetStart().y), tf(t.GetEnd().x, t.GetEnd().y)
            ends = tuple(sorted([a, c]))
            if t.Type() == pcbnew.PCB_ARC_T:
                geo = ("arc", ln(t.GetLayer()), ends, tf(t.GetMid().x, t.GetMid().y))
            else: geo = ("track", ln(t.GetLayer()), ends)
            prop = (t.GetWidth(), short(t.GetNetname()))
        out.append((geo, prop))
    return out
def index(items):
    d = collections.defaultdict(list)
    for g, p in items: d[g].append(p)
    return d
rt, st, nt = titems(R, T), index(titems(S, T)), index(titems(N, I))
def tdesc(g, p):
    if g[0] == "via": return "via %s dia %.2f drill %.2f %s..%s net %s" % (XY(g[1]), mm(p[0]), mm(p[1]), p[2], p[3], p[4])
    a, c = g[2]; L = ((a[0] - c[0]) ** 2 + (a[1] - c[1]) ** 2) ** 0.5
    return "%s on %s %s to %s, %.2f mm long, width %.3f, net %s" % (g[0], g[1], XY(a), XY(c), mm(L), mm(p[0]), p[1])
cnt = collections.Counter(); rows = []; nopad = collections.Counter()
def netof(g, p): return p[4] if g[0] == "via" else p[1]
def eq(g, p, q): return p[:-1] == q[:-1] and samenet(netof(g, p), netof(g, q))
def length(g): return 0.0 if g[0] == "via" else mm(((g[2][0][0] - g[2][1][0]) ** 2 + (g[2][0][1] - g[2][1][1]) ** 2) ** 0.5)
for g, p in rt:
    kind = "vias" if g[0] == "via" else "tracks"
    cnt[kind] += 1
    inS, inN = st.get(g, []), nt.get(g, [])
    if any(eq(g, p, q) for q in inN):
        cnt[kind + " same in NOW"] += 1
        if netof(g, p) not in r2n: nopad[(netof(g, p), netof(g, [q for q in inN if eq(g, p, q)][0]))] += 1
        continue
    sS = any(p[:-1] == q[:-1] for q in inS)
    rows.append(("CHANGED" if inN else "MISSING", "this branch" if sS else "before this branch", netof(g, p), g, p, inN))
P("\nCOPPER. REF tracks: %d, the same in NOW (ends, layer, width, net through the map): %d" % (cnt["tracks"], cnt["tracks same in NOW"]))
P("REF vias: %d, the same in NOW (place, pad, drill, layers, net through the map): %d" % (cnt["vias"], cnt["vias same in NOW"]))
P("kept REF copper on nets that have no pad on both boards (name on REF -> name on NOW, items): %s" % ("; ".join("%s -> %s (%d)" % (k[0], k[1], v) for k, v in sorted(nopad.items())) or "none"))
for when in ("this branch", "before this branch"):
    for what in ("CHANGED", "MISSING"):
        sel = [r_ for r_ in rows if r_[0] == what and r_[1] == when]
        P("\n%s in NOW, START %s: %d items" % (what, "had them as REF (so: changed on THIS BRANCH)" if when == "this branch" else "already differed (work BEFORE this branch)", len(sel)))
        bynet = collections.defaultdict(list)
        for r_ in sel: bynet[r_[2]].append(r_)
        alive = {n_: bool(r2n.get(n_)) for n_ in bynet}
        for live in (True, False):
            nets = sorted(n_ for n_ in bynet if alive[n_] == live)
            if not nets: continue
            P("  %s (%d nets, %d items):" % (NP[live], len(nets), sum(len(bynet[n_]) for n_ in nets)))
            for n_ in nets:
                it = bynet[n_]; lay = collections.Counter("via" if r_[3][0] == "via" else r_[3][1] for r_ in it)
                P("    %-22s -> %-34s %3d items, %6.1f mm of track; %s" % (n_, ",".join(sorted(r2n.get(n_, {}))) or "-", len(it), sum(length(r_[3]) for r_ in it),
                  ", ".join("%s %d" % kv for kv in sorted(lay.items()))))
                if when == "this branch" or what == "CHANGED":
                    for r_ in it: P("        %s%s" % (tdesc(r_[3], r_[4]), ("  | NOW: %s" % (r_[5],)) if r_[5] else ""))

# ---------------------------------------------------------------- zones and rule areas
def zitems(b, tf):
    out = []
    for z in b.Zones():
        o = z.Outline(); pts = tuple(tf(o.CVertex(i).x, o.CVertex(i).y) for i in range(o.TotalVertices()))
        k = pts.index(min(pts)) if pts else 0
        cyc = pts[k:] + pts[:k]
        geo = (tuple(sorted(b.GetLayerName(l_) for l_ in z.GetLayerSet().Seq())), z.GetIsRuleArea(), frozenset(pts), len(pts))
        prop = dict(net=short(z.GetNetname()) if not z.GetIsRuleArea() else "", name=z.GetZoneName(), prio=z.GetAssignedPriority(), clearance=z.GetLocalClearance(),
                    minwidth=z.GetMinThickness(), padconn=z.GetPadConnection(), thgap=z.GetThermalReliefGap(), thspoke=z.GetThermalReliefSpokeWidth(),
                    island=z.GetIslandRemovalMode(), fillmode=z.GetFillMode(),
                    keepout=(z.GetDoNotAllowZoneFills(), z.GetDoNotAllowTracks(), z.GetDoNotAllowVias(), z.GetDoNotAllowPads(), z.GetDoNotAllowFootprints()) if z.GetIsRuleArea() else ())
        area = {}
        if not z.GetIsRuleArea():
            for l_ in z.GetLayerSet().Seq():
                try: area[b.GetLayerName(l_)] = round(z.GetFilledPolysList(l_).Area() / 1e12, 2)
                except Exception as e: area[b.GetLayerName(l_)] = "?"
        out.append((geo, prop, area))
    return out
rz, sz, nz = zitems(R, T), zitems(S, T), zitems(N, I)
sidx = collections.defaultdict(list); nidx = collections.defaultdict(list)
for g, p, a in sz: sidx[g].append(p)
for g, p, a in nz: nidx[g].append((p, a))
zc = collections.Counter(); P("")
fillrows = []
for g, p, a in rz:
    kind = "rule areas" if g[1] else "zones"; zc[kind] += 1
    cand = nidx.get(g, [])
    same = [c for c in cand if {k: v for k, v in c[0].items() if k != 'net'} == {k: v for k, v in p.items() if k != 'net'} and samenet(p['net'], c[0]['net'])]
    if same:
        zc[kind + " same"] += 1
        if not g[1]: fillrows.append((p["name"] or "(unnamed)", p["net"], a, same[0][1]))
        continue
    before = "START has %s" % [{k: q[k] for k in q if q[k] != p[k]} for q in sidx.get(g, [])]
    if cand:
        diff = {k: (p[k], cand[0][0][k]) for k in p if p[k] != cand[0][0][k]}
        P("  ZONE CHANGED: %s on %s, %d corners: %s | %s" % (p["name"] or kind, ",".join(g[0]), g[3], diff, before))
    else:
        P("  ZONE MISSING: %s net %s on %s, %d corners | %s" % (p["name"] or kind, p["net"], ",".join(g[0]), g[3], before))
P("REF zones: %d, same outline, layers and settings in NOW: %d.  REF rule areas: %d, same in NOW: %d" % (zc["zones"], zc["zones same"], zc["rule areas"], zc["rule areas same"]))
P("filled area of Sofar's zones, mm2 per layer, REF -> NOW (NOW is clipped by the new outline and refilled round new copper):")
for name, net_, a, c in sorted(fillrows, key=lambda r_: (r_[0], r_[1], str(r_[2]))):
    P("  %-22s %-12s %s" % (name, net_, "; ".join("%s %s -> %s" % (k, a[k], c.get(k)) for k in sorted(a))))

# ---------------------------------------------------------------- copper drawings
def ditems(b, tf):
    out = collections.Counter()
    for d in b.GetDrawings():
        if not pcbnew.IsCopperLayer(d.GetLayer()): continue
        q = d.GetBoundingBox(); c = [tf(x, y) for x in (q.GetLeft(), q.GetRight()) for y in (q.GetTop(), q.GetBottom())]
        out[(d.GetClass(), b.GetLayerName(d.GetLayer()), min(p[0] for p in c), min(p[1] for p in c), max(p[0] for p in c), max(p[1] for p in c),
             short(d.GetNetname()) if hasattr(d, "GetNetname") else "")] += 1
    return out
rd, sd, nd = ditems(R, T), ditems(S, T), ditems(N, I)
okd = 0
for k, v in rd.items():
    hit_ = [k2 for k2 in nd if k2[:-1] == k[:-1] and samenet(k[-1], k2[-1])]
    if hit_: okd += v; continue
    P("  COPPER DRAWING MISSING OR CHANGED: %s | NOW has %s | START has %s" % (k, [k2 for k2 in nd if k2[:-1] == k[:-1]], [k2 for k2 in sd if k2[:-1] == k[:-1]]))
P("\nREF drawings on copper layers: %d, same box, layer and net (through the map) in NOW: %d" % (sum(rd.values()), okd))

# ---------------------------------------------------------------- footprints and pads
def padsig(p, tf, b):
    q = p.GetBoundingBox(); c = [tf(x, y) for x in (q.GetLeft(), q.GetRight()) for y in (q.GetTop(), q.GetBottom())]
    return (tf(p.GetPosition().x, p.GetPosition().y), (min(x for x, y in c), min(y for x, y in c), max(x for x, y in c), max(y for x, y in c)),
            p.GetDrillSize().x, p.GetDrillSize().y, p.GetAttribute(), tuple(sorted(b.GetLayerName(l_) for l_ in p.GetLayerSet().CuStack())))
turn = (u2.GetOrientationDegrees() - u.GetOrientationDegrees()) % 360
fc = collections.Counter(); netchg = []; P("")
for ref, f in sorted(rf.items()):
    fc["footprints"] += 1
    g = nf.get(ref); s = sf.get(ref)
    s_same = s is not None and s.GetPosition() == f.GetPosition() and s.GetLayer() == f.GetLayer() and abs(s.GetOrientationDegrees() - f.GetOrientationDegrees()) < 0.1
    before = "START had it as REF: this branch" if s_same else "START already differed"
    if g is None: P("  FOOTPRINT MISSING: %s (%s) | %s" % (ref, f.GetValue(), before)); fc["missing"] += 1; continue
    place = (g.GetPosition().x, g.GetPosition().y) == T(f.GetPosition().x, f.GetPosition().y) and g.GetLayer() == f.GetLayer() \
        and abs(((g.GetOrientationDegrees() - f.GetOrientationDegrees()) - turn + 180) % 360 - 180) < 0.001
    if not place: P("  FOOTPRINT MOVED: %s now at %s | %s" % (ref, XY((g.GetPosition().x, g.GetPosition().y)), before)); fc["moved"] += 1; continue
    meta = (g.GetFPIDAsString() == f.GetFPIDAsString(), g.GetValue() == f.GetValue())
    if not all(meta): P("  FOOTPRINT VALUE OR LIBRARY ID CHANGED: %s %s / %s -> %s / %s" % (ref, f.GetFPIDAsString(), f.GetValue(), g.GetFPIDAsString(), g.GetValue()))
    pa = collections.defaultdict(list); pb = collections.defaultdict(list)
    for p in f.Pads(): pa[p.GetNumber()].append((padsig(p, T, R), short(p.GetNetname())))
    for p in g.Pads(): pb[p.GetNumber()].append((padsig(p, I, N), short(p.GetNetname())))
    okgeo = sorted(pa) == sorted(pb) and all(sorted(x[0] for x in pa[k]) == sorted(x[0] for x in pb[k]) for k in pa)
    if not okgeo:
        ps = collections.defaultdict(list)
        for p in s.Pads(): ps[p.GetNumber()].append(padsig(p, T, S))
        sgeo = sorted(ps) == sorted(pb) and all(sorted(ps[k]) == sorted(x[0] for x in pb[k]) for k in ps)
        P("  PAD GEOMETRY CHANGED: %s | START's pads %s NOW's (library id on START %s)" % (ref, "equal" if sgeo else "differ from", s.GetFPIDAsString())); fc["pad geometry changed"] += 1
    else: fc["same place and pads"] += 1
    for k in sorted(pa):
        na, nb = sorted({x[1] for x in pa[k]}), sorted({x[1] for x in pb.get(k, [])})
        fc["pads"] += len(pa[k])
        if na != nb: netchg.append("%s.%s %s -> %s" % (ref, k, ",".join(na), ",".join(nb)))
P("REF footprints: %d; in NOW at the turned place with the same pads (position, size box, drill, type, copper layers): %d; missing %d; moved %d; pad geometry changed %d" % (
    fc["footprints"], fc["same place and pads"], fc["missing"], fc["moved"], fc["pad geometry changed"]))

# ---------------------------------------------------------------- copper in NOW inside the mote outline that REF does not have
q = R.GetBoardEdgesBoundingBox(); c = [T(x, y) for x in (q.GetLeft(), q.GetRight()) for y in (q.GetTop(), q.GetBottom())]
bx = (min(p[0] for p in c), min(p[1] for p in c), max(p[0] for p in c), max(p[1] for p in c))
P("\nmote outline box on NOW: X' %.2f..%.2f, y %.2f..%.2f" % (mm(bx[0]) - 100, mm(bx[2]) - 100, 100 - mm(bx[3]), 100 - mm(bx[1])))
refset = collections.defaultdict(list)
for g, p in rt: refset[g].append(p)
def inbox(p): return bx[0] <= p[0] <= bx[2] and bx[1] <= p[1] <= bx[3]
new = collections.Counter(); refnets = set(n2r)
for g, ps in nt.items():
    for p in ps:
        if any(eq(g, rp, p) for rp in refset.get(g, [])): continue
        pts = [g[1]] if g[0] == "via" else list(g[2])
        if not any(inbox(q_) for q_ in pts): continue
        netn = p[4] if g[0] == "via" else p[1]
        new[(netn, "via" if g[0] == "via" else g[1], "a net of the mote's parts" if netn in refnets else "not on a mote part")] += 1
P("copper in NOW with an end inside that box that REF does not have (net, layer, count):")
for k, v in sorted(new.items()): P("  %-28s %-16s %-18s %d" % (k[0], k[1], k[2], v))
P("total: %d items on %d nets" % (sum(new.values()), len({k[0] for k in new})))

# ---------------------------------------------------------------- START's copper that is not REF's (the Pi Zero work's own)
sidx2 = collections.defaultdict(lambda: [0, 0, 0.0, 0.0])
for g, ps in st.items():
    for p in ps:
        if any(p[:-1] == rp[:-1] for rp in refset.get(g, [])): continue
        k = netof(g, p); e = sidx2[k]; e[0] += 1; e[2] += length(g)
        if any(q[:-1] == p[:-1] for q in nt.get(g, [])): e[1] += 1; e[3] += length(g)
P("\nSTART's copper that REF does not have (the Pi Zero shield work's own routing), by START net: items, mm of track, and how much of it is still in NOW at the turned place:")
for k, e in sorted(sidx2.items()): P("  %-36s %4d items %7.1f mm; in NOW %4d items %7.1f mm" % (k, e[0], e[2], e[1], e[3]))
P("total: %d items, in NOW %d" % (sum(e[0] for e in sidx2.values()), sum(e[1] for e in sidx2.values())))

# ---------------------------------------------------------------- REF copper that is missing in NOW, on nets that still have
# pads: joined into connected pieces (shared ends, vias), and for each piece which pads of the mote it touched.
inplace, moved = set(), set()
for ref, f in rf.items():
    g = nf.get(ref)
    if g is None: continue
    ok = (g.GetPosition().x, g.GetPosition().y) == T(f.GetPosition().x, f.GetPosition().y) and g.GetLayer() == f.GetLayer()
    (inplace if ok else moved).add(ref)
rpads = []
for ref, f in rf.items():
    for p in f.Pads():
        q = p.GetBoundingBox(); c = [T(x, y) for x in (q.GetLeft(), q.GetRight()) for y in (q.GetTop(), q.GetBottom())]
        rpads.append((ref, p.GetNumber(), min(x for x, y in c), min(y for x, y in c), max(x for x, y in c), max(y for x, y in c),
                      {R.GetLayerName(l_) for l_ in p.GetLayerSet().CuStack()}, short(p.GetNetname())))
def pads_at(pt, layer, net_):
    return {(r_[0], r_[1]) for r_ in rpads if r_[7] == net_ and r_[2] - 1000 <= pt[0] <= r_[4] + 1000 and r_[3] - 1000 <= pt[1] <= r_[5] + 1000 and (layer is None or layer in r_[6])}
keptpts = collections.defaultdict(set)
miss = [r_ for r_ in rows if r_[0] == "MISSING"]; missgeo = {(r_[3], r_[4]) for r_ in miss}
for g, p in rt:
    if (g, p) in missgeo: continue
    n_ = netof(g, p)
    if g[0] == "via": keptpts[n_].add((None, g[1]))
    else:
        for e_ in g[2]: keptpts[n_].add((g[1], e_))
par = list(range(len(miss)))
def find_(i):
    while par[i] != i: par[i] = par[par[i]]; i = par[i]
    return i
at = collections.defaultdict(list)
for i, r_ in enumerate(miss):
    g = r_[3]
    for pt in ([g[1]] if g[0] == "via" else list(g[2])): at[(r_[2], pt)].append(i)
for (n_, pt), ids in at.items():
    lays = collections.defaultdict(list); vias = [i for i in ids if miss[i][3][0] == "via"]
    for i in ids:
        if miss[i][3][0] != "via": lays[miss[i][3][1]].append(i)
    for L_, li in lays.items():
        for i in li[1:]: par[find_(i)] = find_(li[0])
    if vias:
        for i in ids: par[find_(i)] = find_(vias[0])
pieces = collections.defaultdict(list)
for i in range(len(miss)): pieces[find_(i)].append(miss[i])
P("\nREF copper missing in NOW, on nets that still have pads in NOW, as connected pieces (all of it was already missing on START):")
tot = collections.Counter(); detail = []
for root_, it in pieces.items():
    n_ = it[0][2]
    if not r2n.get(n_): continue
    pads = set(); onkept = False
    for r_ in it:
        g = r_[3]
        for pt in ([g[1]] if g[0] == "via" else list(g[2])):
            L_ = None if g[0] == "via" else g[1]
            pads |= pads_at(pt, L_, n_)
            if (L_, pt) in keptpts[n_] or (None, pt) in keptpts[n_] or (L_ is None and any(k[1] == pt for k in keptpts[n_])): onkept = True
    ip = sorted("%s.%s" % x for x in pads if x[0] in inplace); mv = sorted("%s.%s" % x for x in pads if x[0] in moved); gone_ = sorted("%s.%s" % x for x in pads if x[0] not in nf)
    nv = sum(1 for r_ in it if r_[3][0] == "via"); L = sum(length(r_[3]) for r_ in it)
    cls = "touches a pad of a part that is still in its place" if ip else ("touches only parts that were removed or moved" if (mv or gone_) else "touches no pad (a via or a stub on its own)")
    tot[(n_, cls)] += 1; tot[(n_, cls, "items")] += len(it)
    if ip or not (mv or gone_): detail.append((n_, cls, ip, mv, gone_, nv, L, onkept, it))
for n_ in sorted({k[0] for k in tot}):
    P("  %-12s %s" % (n_, "; ".join("%s: %d pieces, %d items" % (k[1], v, tot[k + ("items",)]) for k, v in sorted(tot.items()) if k[0] == n_ and len(k) == 2)))
P("\nthe pieces that touch a part still in its place, or no pad at all (REF net, pads still in place | moved | removed, vias, mm, joins kept REF copper):")
for n_, cls, ip, mv, gone_, nv, L, onkept, it in sorted(detail, key=lambda d: (d[0], d[1])):
    pts = [XY(r_[3][1]) if r_[3][0] == "via" else XY(r_[3][2][0]) for r_ in it]
    lays = sorted({"via" if r_[3][0] == "via" else r_[3][1] for r_ in it})
    P("  %-10s %-18s | %-12s | %-18s %d vias %5.1f mm, %s, near %s%s" % (n_, " ".join(ip) or "-", " ".join(mv) or "-", " ".join(gone_)[:60] or "-", nv, L, "/".join(lays), pts[0],
      "; joins kept copper" if onkept else ""))
