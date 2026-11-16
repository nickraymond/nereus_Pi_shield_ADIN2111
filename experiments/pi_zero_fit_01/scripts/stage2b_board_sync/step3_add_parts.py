"""Step 3: add the motor driver (U12, C60-C64, R48) and the ADC (U13, C65, R49, R50) on the bottom side under the
south connector row, with their nets. No routing. Positions are new-frame mm (board - (113.47, 89.34)).
Usage: <KiCad python> step3_add_parts.py <board in> <netlist> <board out>"""
import sys
from s3lib import *
b = pcbnew.LoadBoard(sys.argv[1]); comps = load_netlist(sys.argv[2]); fps = by_ref(b)
# ref: (centre x, y, pad that fixes the turn, where that pad must lie from the centre (dx, dy), why)
PLACE = {
    # motor driver group, under J7 (MOTOR). U12's north side, west to east: ISET, OUT2, VIN, IN2.
    'U12': (6.30, 37.20, '9', (0.25, -0.88), 'VIN pin on the north side, facing its capacitors'),
    'C61': (6.55, 34.25, '1', (0, 0.57), '100 nF: VIN pad straight north of U12 pin 9'),
    'C60': (7.60, 34.25, '1', (0, 0.57), '10 uF: beside C61, VIN pad south'),
    'C62': (3.45, 34.20, '1', (1.475, 0), '47 uF bulk: VIN pad at its east end, towards pin 9'),
    'R48': (3.35, 35.95, '1', (0.6, 0), 'ISET resistor: west of pin 7'),
    'C63': (3.37, 37.00, '1', (0.57, 0), 'VCC capacitor: west of pin 6'),
    'C64': (3.37, 38.05, '1', (0.57, 0), 'V3P3 capacitor: west of pin 4'),
    # ADC group, under J8 (POT). U13's east side, north to south: AIN2, AIN3, VDD, SDA, SCL; west: AIN1, AIN0, GND, ALERT, ADDR.
    'U13': (24.90, 35.00, '8', (2.15, 0), 'VDD / I2C side to the east (R26, R27), analogue inputs to the west'),
    'C65': (28.60, 34.18, '1', (0, 0.57), '100 nF: 3V3 pad right at VDD pin 8'),
    'R49': (21.15, 36.10, '2', (0, -0.6), 'ALERT pull-up: ALERT pad level with pin 2'),
    'R50': (23.00, 37.40, '1', (-0.6, 0), 'ADDR resistor: south of pin 1'),
}
assert sorted(PLACE) == sorted(r for r in comps if r not in fps), 'the parts to add are not the parts this script places'
new = {}
for r, (x, y, pad, (dx, dy), why) in PLACE.items():
    f = lib_footprint(comps[r]['fpid']); b.Add(f)
    f.SetPosition(V(x, y)); f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    best = None
    for rot in (0, 90, 180, 270):
        f.SetOrientationDegrees(rot)
        p = [q for q in f.Pads() if q.GetNumber() == pad][0].GetPosition()
        e = (mm(p.x - f.GetPosition().x) - dx) ** 2 + (mm(p.y - f.GetPosition().y) - dy) ** 2
        if best is None or e < best[0]: best = (e, rot)
    assert best[0] < 0.01, (r, best)
    f.SetOrientationDegrees(best[1]); apply(b, f, r, comps[r]); assert not diff_one(f, comps[r]); new[r] = f
    assert f.IsFlipped() and f.GetLayer() == pcbnew.B_Cu

# --- checks on the placement (DRC is the gate; this prints the margins) ---
def court(f):
    f.BuildCourtyardCaches(); c = f.GetCourtyard(pcbnew.B_CrtYd if f.IsFlipped() else pcbnew.F_CrtYd).BBox()
    return (mm(c.GetLeft()) - DX, mm(c.GetTop()) - DY, mm(c.GetRight()) - DX, mm(c.GetBottom()) - DY)
def edge_gap(x, y):          # distance from a point to the board outline (inside positive), 3 mm corners
    cx, cy = min(max(x, RAD), W - RAD), min(max(y, RAD), H - RAD)
    if (x < RAD or x > W - RAD) and (y < RAD or y > H - RAD): return RAD - ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
    return min(x, W - x, y, H - y)
print('\n  ref   value         footprint                                    centre (new frame)  turn  courtyard x..x / y..y            pads')
for r, f in new.items():
    c = court(f)
    print('  %-5s %-13s %-44s (%5.2f, %5.2f)  %4.0f  %5.2f..%5.2f / %5.2f..%5.2f   %s' % (r, f.GetValue(), fpid_str(f)[:44], *N(f.GetPosition())[:2], f.GetOrientationDegrees(), c[0], c[2], c[1], c[3],
          ' '.join('%s:%s@%.2f,%.2f' % (p.GetNumber(), p.GetNetname().split('/')[-1][:12], *N(p.GetPosition())) for p in f.Pads()) if len(f.Pads()) < 3 else ''))
for r in ('U12', 'U13'):
    print('  %s pads: %s' % (r, '  '.join('%s %s (%.2f, %.2f)' % (p.GetNumber(), p.GetNetname().split('/')[-1], *N(p.GetPosition())) for p in new[r].Pads())))
newu = {f.m_Uuid.AsString() for f in new.values()}
# courtyards: new against every bottom-side footprint
worst = (9, '')
bot = [f for f in b.GetFootprints() if f.IsFlipped()]
for r, f in new.items():
    c = court(f)
    for g in bot:
        if g.m_Uuid.AsString() == f.m_Uuid.AsString(): continue
        q = court(g)
        if q[2] <= q[0]: continue
        d = rect_rect(c, q)
        if d < worst[0]: worst = (d, '%s to %s' % (r, g.GetReference()))
        assert d > 0, 'courtyards overlap: %s / %s' % (r, g.GetReference())
print('\n  smallest courtyard gap, new part to any bottom-side part: %.3f mm (%s)' % worst)
# copper: every new pad against vias (all are through vias), bottom-layer tracks, and other footprints' pads on the bottom layer / through-hole
wc, wh, we = (9, ''), (9, ''), (9, '')
for r, f in new.items():
    for p in f.Pads():
        pr = pad_rect(p); nn = p.GetNetname()
        for cx, cy in ((pr[0], pr[1]), (pr[2], pr[1]), (pr[0], pr[3]), (pr[2], pr[3])):
            g = edge_gap(cx, cy)
            if g < we[0]: we = (g, '%s pad %s' % (r, p.GetNumber()))
        for t in b.GetTracks():
            a, c = N(t.GetStart()), N(t.GetEnd())
            if t.GetClass() == 'PCB_VIA':
                d0 = rect_pt(pr, *a); d = d0 - mm(t.GetWidth(pcbnew.B_Cu)) / 2; h = d0 - mm(t.GetDrill()) / 2
                if h < wh[0]: wh = (h, '%s pad %s to via hole %s at %s' % (r, p.GetNumber(), t.GetNetname().split('/')[-1], a))
            elif t.GetLayer() == pcbnew.B_Cu: d = rect_seg(pr, a, c) - mm(t.GetWidth()) / 2
            else: continue
            if d < wc[0]: wc = (d, '%s pad %s to %s %s at %s' % (r, p.GetNumber(), t.GetClass(), t.GetNetname().split('/')[-1], a))
        for g in b.GetFootprints():
            if g.m_Uuid.AsString() == f.m_Uuid.AsString(): continue
            for q in g.Pads():
                if not q.IsOnLayer(pcbnew.B_Cu): continue
                if q.GetNetname() == nn and nn and g.m_Uuid.AsString() in newu: continue      # same net inside the new groups
                d = rect_rect(pr, pad_rect(q))
                if d < wc[0]: wc = (d, '%s pad %s to %s pad %s' % (r, p.GetNumber(), g.GetReference(), q.GetNumber()))
                if q.GetDrillSize().x:
                    h = rect_pt(pr, *N(q.GetPosition())) - mm(q.GetDrillSize().x) / 2
                    if h < wh[0]: wh = (h, '%s pad %s to hole of %s pad %s' % (r, p.GetNumber(), g.GetReference(), q.GetNumber()))
print('  smallest copper gap, new pad to existing via / bottom track / other pad (pad boxes): %.3f mm (%s)' % wc)
print('  smallest gap, new pad to a drilled hole: %.3f mm (%s)' % wh)
print('  smallest gap, new pad corner to the board outline: %.3f mm (%s)' % we)
zb = [z for z in b.Zones() if not z.GetIsRuleArea() and z.IsOnLayer(pcbnew.B_Cu)]
for z in zb:
    bb = z.GetBoundingBox(); zr = (mm(bb.GetLeft()) - DX, mm(bb.GetTop()) - DY, mm(bb.GetRight()) - DX, mm(bb.GetBottom()) - DY)
    print('  bottom-layer fill %s x %.2f..%.2f y %.2f..%.2f: nearest new pad %.2f mm' % (z.GetNetname(), zr[0], zr[2], zr[1], zr[3], min(rect_rect(pad_rect(p), zr) for f in new.values() for p in f.Pads())))
assert wc[0] >= 0.2 and wh[0] >= 0.3 and we[0] >= 0.5
pcbnew.SaveBoard(sys.argv[3], b); print('saved', sys.argv[3])
