"""Via holes inside, cutting or close to exposed pads. For every via and every pad on an outer layer: the gap between the via's hole
and the pad's copper outline (negative = the hole is inside the pad or cuts its edge). Lists gaps under LIMIT (default 0.3 mm) and says
whose via it is: "ours" (stage 3 / 4 / 5: its uuid is not in the stage-2c board, commit d30920b), else "carried" (in the stage-2c
board), with "frozen" added when the same uuid is also in the frozen JLC board. Pads are taken as their bounding box (exact for the
rectangles, a little large for rounded ones and circles), circles as circles.
Usage: <KiCad python> via_in_pad.py <board> <stage-2c board> <frozen board> [limit]"""
import pcbnew, sys, re, math
DX, DY = 113.47, 89.34; mm = pcbnew.ToMM
uu = lambda p: set(re.findall(r'\(uuid "([0-9a-f-]{36})"\)', open(p).read()))
base, frozen = uu(sys.argv[2]), uu(sys.argv[3]); LIMIT = float(sys.argv[4]) if len(sys.argv) > 4 else 0.3
b = pcbnew.LoadBoard(sys.argv[1]); N = lambda p: (mm(p.x) - DX, mm(p.y) - DY)
pads = []
for f in b.GetFootprints():
    for p in f.Pads():
        if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH: continue
        bb = p.GetBoundingBox(); x0, y0 = N(bb.GetPosition()); x1, y1 = N(bb.GetEnd()); c = N(p.GetPosition())
        circ = p.GetShape(pcbnew.F_Cu) == pcbnew.PAD_SHAPE_CIRCLE
        pads.append((f.GetReference(), p.GetNumber(), p.GetNetname().split('/')[-1], x0, y0, x1, y1, c, circ, p.GetDrillSize().x > 0))
rows = []
for t in b.GetTracks():
    if t.GetClass() != 'PCB_VIA': continue
    v = N(t.GetStart()); hr = mm(t.GetDrillValue()) / 2; u = t.m_Uuid.AsString()
    for ref, num, net, x0, y0, x1, y1, c, circ, th in pads:
        if circ: d = math.hypot(v[0] - c[0], v[1] - c[1]) - (x1 - x0) / 2
        else:
            ox, oy = max(x0 - v[0], 0, v[0] - x1), max(y0 - v[1], 0, v[1] - y1)
            d = math.hypot(ox, oy) if (ox or oy) else -min(v[0] - x0, x1 - v[0], v[1] - y0, y1 - v[1])
        if d - hr < LIMIT: rows.append((ref, num, net, v, t.GetNetname().split('/')[-1], mm(t.GetWidth(pcbnew.F_Cu)), hr * 2, d - hr, 'ours' if u not in base else 'carried' + (' (also frozen)' if u in frozen else ''), u[:8]))
for r in sorted(rows, key=lambda r: (r[8], r[0], r[1])):
    print('%-22s %-5s pad %-3s %-16s via (%.3f, %.3f) %-14s d %.2f hole %.2f  hole-to-pad gap %+.3f mm  %s' % (r[8], r[0], r[1], r[2][:16], r[3][0], r[3][1], r[4][:14], r[5], r[6], r[7], r[9]))
print('%d via / pad pairs under %.2f mm; ours: %d' % (len(rows), LIMIT, sum(1 for r in rows if r[8] == 'ours')))
