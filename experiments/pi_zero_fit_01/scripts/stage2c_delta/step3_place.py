"""Stage 2c, step 3: the two new groups on the bottom side, re-packed. New parts (C66, C67, R51) and the parts whose
footprint changed (step 2 removed them) come from the library; C60 and C64 keep their footprints and move; U12 and U13
stay where stage 2b put them. Nets, fields and the DNP flag come from the netlist. No routing.
Positions are new-frame mm (board - (113.47, 89.34)). Usage: <KiCad python> step3_place.py <board in> <netlist> <board out>"""
import sys
from s3lib import *
b = pcbnew.LoadBoard(sys.argv[1]); comps = load_netlist(sys.argv[2]); fps = by_ref(b)
# ref: (centre x, y, pad that fixes the turn, where that pad lies from the centre (dx, dy), why)
PLACE = {
    # motor group. U12's north side, west to east: ISET (x 5.55), OUT2 (6.05), VIN (6.55), IN2 (7.05); pad tops at y 35.85.
    'U12': (6.30, 37.20, '9', (0.25, -0.88), 'not moved'),
    'C61': (6.23, 34.56, '1', (0, 0.379), '100 nF: VIN pad 0.67 mm north of U12 pin 9'),
    'C66': (7.78, 33.25, '1', (0, 0.95), '22 uF: VIN pad north-east of pin 9'),
    'C62': (4.68, 33.25, '1', (0, 0.95), '22 uF: VIN pad north-west of pin 9'),
    'C60': (3.045, 34.165, '1', (0, 0.57), '10 uF: west end of the row, VIN pad south'),
    'R48': (3.66, 36.10, '1', (0.379, 0), 'ISET resistor: west of pin 7'),
    'C63': (3.66, 37.17, '1', (0.379, 0), 'VCC capacitor: west of pin 6'),
    'C64': (3.305, 38.20, '1', (0.57, 0), 'V3P3 capacitor: west of pin 4'),
    # ADC group. U13's west side, north to south: AIN1 (pot, y 34.0), AIN0, GND, ALERT, ADDR; east: AIN2, AIN3, VDD, SDA, SCL.
    'U13': (24.90, 35.00, '8', (2.15, 0), 'not moved'),
    'R51': (21.98, 32.68, '1', (0.366, 0), 'pot pull-down: wiper pad straight north of the AIN1 pad'),
    'C67': (23.67, 32.68, '1', (-0.379, 0), 'DNP 100 nF: wiper pad straight north of the AIN1 pad, beside R51'),
    'C65': (28.60, 34.621, '1', (0, 0.379), '100 nF: 3V3 pad level with VDD pin 8'),
    'R49': (21.037, 35.879, '2', (0, -0.379), 'ALERT pull-up: ALERT pad level with pin 2'),
    'R50': (23.00, 37.445, '1', (-0.379, 0), 'ADDR resistor: south of pin 1'),
}
FIXED = ('U12', 'U13')
missing = sorted(r for r in comps if r not in fps)
assert set(missing) <= set(PLACE) and not [r for r in fps if r not in comps and not fps[r].GetAttributes() & pcbnew.FP_BOARD_ONLY], missing
print('  from the library:', ', '.join(missing)); print('  moved:', ', '.join(r for r in PLACE if r in fps and r not in FIXED))
new = {}
for r, (x, y, pad, (dx, dy), why) in PLACE.items():
    if r in fps:
        f = fps[r]; assert fpid_str(f) == comps[r]['fpid'] and f.IsFlipped(), r
        if r in FIXED: assert N(f.GetPosition()) == (x, y), (r, N(f.GetPosition()))
        else: f.SetPosition(V(x, y))
    else:
        f = lib_footprint(comps[r]['fpid']); b.Add(f); f.SetPosition(V(x, y)); f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    if r not in FIXED:
        best = None
        for rot in (0, 90, 180, 270):
            f.SetOrientationDegrees(rot)
            p = [q for q in f.Pads() if q.GetNumber() == pad][0].GetPosition()
            e = (mm(p.x - f.GetPosition().x) - dx) ** 2 + (mm(p.y - f.GetPosition().y) - dy) ** 2
            if best is None or e < best[0]: best = (e, rot)
        assert best[0] < 0.0004, (r, best)
        f.SetOrientationDegrees(best[1])
    apply(b, f, r, comps[r]); assert not diff_one(f, comps[r]), (r, diff_one(f, comps[r])); new[r] = f
    assert f.IsFlipped() and f.GetLayer() == pcbnew.B_Cu

# --- checks on the placement (DRC is the gate; this prints the margins) ---
def court(f):
    f.BuildCourtyardCaches(); c = f.GetCourtyard(pcbnew.B_CrtYd if f.IsFlipped() else pcbnew.F_CrtYd).BBox()
    return (mm(c.GetLeft()) - DX, mm(c.GetTop()) - DY, mm(c.GetRight()) - DX, mm(c.GetBottom()) - DY)
def edge_gap(x, y):          # distance from a point to the board outline (inside positive), 3 mm corners
    cx, cy = min(max(x, RAD), W - RAD), min(max(y, RAD), H - RAD)
    if (x < RAD or x > W - RAD) and (y < RAD or y > H - RAD): return RAD - ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
    return min(x, W - x, y, H - y)
corners = lambda r: ((r[0], r[1]), (r[2], r[1]), (r[0], r[3]), (r[2], r[3]))
print('\n  ref   value         footprint                          centre (new frame)  turn  courtyard x..x / y..y            DNP  pads')
for r, f in new.items():
    c = court(f)
    print('  %-5s %-13s %-34s (%6.3f, %6.3f)  %4.0f  %6.3f..%6.3f / %6.3f..%6.3f  %-3s  %s' % (r, f.GetValue(), fpid_str(f)[:34], *N(f.GetPosition())[:2], f.GetOrientationDegrees(), c[0], c[2], c[1], c[3], 'DNP' if f.IsDNP() else '',
          ' '.join('%s:%s@%.2f,%.2f' % (p.GetNumber(), p.GetNetname().split('/')[-1][:12], *N(p.GetPosition())) for p in f.Pads()) if len(f.Pads()) < 3 else ''))
newu = {f.m_Uuid.AsString() for f in new.values()}
# courtyards: each group part against every bottom-side footprint, and against the outline
worst, wce, gaps = (9, ''), (9, ''), []
bot = [f for f in b.GetFootprints() if f.IsFlipped()]
for r, f in new.items():
    c = court(f)
    g = min(edge_gap(*p) for p in corners(c))
    if g < wce[0]: wce = (g, r)
    for g in bot:
        if g.m_Uuid.AsString() == f.m_Uuid.AsString(): continue
        q = court(g)
        if q[2] <= q[0]: continue
        d = rect_rect(c, q)
        if d < 0.3 and r < g.GetReference() or (d < 0.3 and g.m_Uuid.AsString() not in newu): gaps.append('%s / %s %.3f' % (r, g.GetReference(), d))
        if d < worst[0]: worst = (d, '%s to %s' % (r, g.GetReference()))
        assert d > 0, 'courtyards overlap: %s / %s' % (r, g.GetReference())
print('\n  courtyard gaps under 0.3 mm:', '; '.join(gaps))
print('  smallest courtyard gap, group part to any bottom-side part: %.3f mm (%s)' % worst)
print('  smallest gap, group courtyard corner to the board outline (3 mm corners included): %.3f mm (%s)' % wce)
# copper: every group pad against vias (all are through vias), bottom-layer tracks, and other footprints' pads on the bottom layer / through-hole
wc, wh, we = (9, ''), (9, ''), (9, '')
for r, f in new.items():
    for p in f.Pads():
        pr = pad_rect(p); nn = p.GetNetname()
        for cx, cy in corners(pr):
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
print('  smallest copper gap, group pad to existing via / bottom track / other pad of another net (pad boxes): %.3f mm (%s)' % wc)
print('  smallest gap, group pad to a drilled hole: %.3f mm (%s)' % wh)
print('  smallest gap, group pad corner to the board outline: %.3f mm (%s)' % we)
pad = lambda r, n: pad_rect([p for p in new[r].Pads() if p.GetNumber() == n][0])
vin = pad('U12', '9'); ain1 = pad('U13', '5')
for r in ('C61', 'C66', 'C62', 'C60'): print('  U12 VIN pad to %s pad 1 (edge to edge): %.2f mm' % (r, rect_rect(vin, pad(r, '1'))))
for r in ('R51', 'C67'): print('  U13 AIN1 pad to %s pad 1 (edge to edge): %.2f mm' % (r, rect_rect(ain1, pad(r, '1'))))
assert wc[0] >= 0.2 and wh[0] >= 0.3 and we[0] >= 0.5 and wce[0] >= 0.5 and worst[0] >= 0.0995
pcbnew.SaveBoard(sys.argv[3], b); print('saved', sys.argv[3])
