"""J4 (and J5, for the record): pads, drills, annular ring, hole to hole, and on every copper layer the distance from each hole's edge to the nearest
copper of another net (tracks, vias, pads, zone fills as they are stored). Usage: <KiCad python> j4_measure.py <board.kicad_pcb>"""
import sys, math, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); mm = pcbnew.ToMM; DX, DY = 113.47, 89.34
def dseg(px, py, ax, ay, bx, by):
    vx, vy = bx - ax, by - ay; L = vx * vx + vy * vy; t = 0 if L == 0 else max(0, min(1, ((px - ax) * vx + (py - ay) * vy) / L)); return math.hypot(px - ax - t * vx, py - ay - t * vy)
layers = [l for l in b.GetEnabledLayers().CuStack()]
for ref in ('J4', 'J5'):
    f = [f for f in b.GetFootprints() if f.GetReference() == ref][0]; pads = list(f.Pads())
    print('%s  %s  at (%.2f, %.2f) %s deg' % (ref, f.GetFPIDAsString(), mm(f.GetPosition().x) - DX, mm(f.GetPosition().y) - DY, f.GetOrientationDegrees()))
    for p in pads:
        sx, sy = mm(p.GetSize(pcbnew.F_Cu).x), mm(p.GetSize(pcbnew.F_Cu).y); bb = p.GetBoundingBox(); w, h = mm(bb.GetWidth()), mm(bb.GetHeight()); d = mm(p.GetDrillSize().x), mm(p.GetDrillSize().y)
        print('   pad %s (%.2f, %.2f) net %s: %s %.2f x %.2f mm (on the board %.2f wide x %.2f high), drill %.2f x %.2f mm %s, %s, layers %s; ring %.3f mm across the board x, %.3f mm across y'
              % (p.GetNumber(), mm(p.GetPosition().x) - DX, mm(p.GetPosition().y) - DY, p.GetNetname().split('/')[-1], p.ShowPadShape(pcbnew.F_Cu) if hasattr(p, 'ShowPadShape') else p.GetShape(pcbnew.F_Cu), sx, sy, w, h, d[0], d[1],
                 'round' if p.GetDrillShape() == pcbnew.PAD_DRILL_SHAPE_CIRCLE else 'slot', 'plated' if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH else 'NOT plated', 'all copper' if all(p.IsOnLayer(l) for l in layers) else 'some copper', (w - d[0]) / 2, (h - d[1]) / 2))
    if len(pads) == 2:
        c = math.hypot(pads[0].GetPosition().x - pads[1].GetPosition().x, pads[0].GetPosition().y - pads[1].GetPosition().y); print('   hole edge to hole edge: %.3f mm (rule "JLC pad hole to pad hole" 0.45 mm)' % (mm(c) - mm(pads[0].GetDrillSize().x) / 2 - mm(pads[1].GetDrillSize().x) / 2))
    if ref != 'J4': continue
    for p in pads:
        px, py = p.GetPosition().x, p.GetPosition().y; r = p.GetDrillSize().x / 2; net = p.GetNetCode()
        for l in layers:
            best = (1e18, '')
            for t in b.GetTracks():
                if t.GetNetCode() == net: continue
                if t.GetClass() == 'PCB_VIA': d = math.hypot(px - t.GetPosition().x, py - t.GetPosition().y) - t.GetWidth(l) / 2; what = 'via ' + t.GetNetname().split('/')[-1]
                elif t.GetLayer() == l: d = dseg(px, py, t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y) - t.GetWidth() / 2; what = 'track ' + t.GetNetname().split('/')[-1]
                else: continue
                best = min(best, (d - r, what))
            for f2 in b.GetFootprints():
                for q in f2.Pads():
                    if q.GetNetCode() == net and q.GetNetCode() != 0 or q is p or (f2.GetReference() == ref and q.GetNumber() == p.GetNumber()) or not q.IsOnLayer(l): continue
                    bb = q.GetBoundingBox(); d = math.hypot(max(bb.GetLeft() - px, 0, px - bb.GetRight()), max(bb.GetTop() - py, 0, py - bb.GetBottom())); best = min(best, (d - r, 'pad %s.%s %s (its box)' % (f2.GetReference(), q.GetNumber(), q.GetNetname().split('/')[-1])))
            for z in b.Zones():
                if z.GetIsRuleArea() or z.GetNetCode() == net or not z.IsOnLayer(l): continue
                ps = z.GetFilledPolysList(l)
                for i in range(ps.OutlineCount()):
                    for o in [ps.Outline(i)] + [ps.Hole(i, k) for k in range(ps.HoleCount(i))]:
                        n = o.PointCount(); pts = [(o.CPoint(k).x, o.CPoint(k).y) for k in range(n)]
                        for k in range(n):
                            (ax, ay), (bx, by) = pts[k], pts[(k + 1) % n]
                            if min(ax, bx) - px > best[0] + r or px - max(ax, bx) > best[0] + r: continue
                            best = min(best, (dseg(px, py, ax, ay, bx, by) - r, 'zone fill ' + z.GetNetname().split('/')[-1]))
            print('   pad %s hole to other-net copper on %-16s %.3f mm  (%s)' % (p.GetNumber(), b.GetLayerName(l) + ':', mm(best[0]), best[1]))
