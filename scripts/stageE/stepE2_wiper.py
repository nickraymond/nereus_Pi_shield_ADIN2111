"""Routing stage E, part 2: the pot wiper from connector J8 pin 2 to its filter (R51, C67) and the ADC U13 pin 5, and
the two short links at U13 that lie beside it: R50 to pin 1 (address) and R49 pad 2 to pin 2 (alert). All on top.
U13's GND pin, its N6 3V3 supply, the I2C lines and the GND pads of R50 / R51 / C67 are stage F and are NOT here
(there is no GND pour on top inside the mote outline, so those pads need vias).

KiCad's Python: stepE2_wiper.py <board .kicad_pcb (a copy outside git)>
Frame: X' = KiCad x - 100, y = 100 - KiCad y (mm). Pad boxes read from the board after stage E part 1 (2026-11-18).
- Wiper: U13 pin 5 straight north into R51 pad 1; C67 pad 1 straight east into R51 pad 1; from R51 pad 1 north,
  45 degrees past the corner of J8's mounting pad (0.25 mm or more), north at X' 11.3, into J8 pin 2 from the west. It stays
  2.4 mm or more from the BM2_P bus track (edge at X' 13.7) and more than 4 mm from the motor outputs."""
import sys, math
import pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); FM = pcbnew.FromMM; mm = pcbnew.ToMM
T = b.GetLayerID("Top Layer"); assert T >= 0
def net(suffix):
    c = [n for name, n in b.GetNetsByName().items() if str(name) == suffix or str(name).endswith("/" + suffix)]
    assert len(c) == 1 and c[0].GetNetCode() > 0, (suffix, len(c)); return c[0]
def V(x, y): return pcbnew.VECTOR2I(FM(100 + x), FM(100 - y))
count = 0; total = {}
def path(n, pts, w=0.2):
    global count
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        dx, dy = abs(x1 - x0), abs(y1 - y0); assert dx < 1e-6 or dy < 1e-6 or abs(dx - dy) < 1e-6, ("not straight or 45 deg", n, (x0, y0), (x1, y1))
        t = pcbnew.PCB_TRACK(b); t.SetStart(V(x0, y0)); t.SetEnd(V(x1, y1)); t.SetWidth(FM(w)); t.SetLayer(T); t.SetNet(net(n)); b.Add(t)
        count += 1; total[n] = total.get(n, 0) + math.hypot(x1 - x0, y1 - y0)
BOX = {("U13", "5"): (8.845, 10.295, 46.04, 46.34), ("R51", "1"): (9.684, 10.265, 47.274, 47.746), ("C67", "1"): (8.771, 9.286, 47.274, 47.746),
       ("J8", "2"): (11.895, 13.595, 53.145, 53.745), ("U13", "1"): (8.845, 10.295, 44.04, 44.34), ("R50", "1"): (9.441, 9.956, 42.509, 42.981),
       ("U13", "2"): (8.845, 10.295, 44.54, 44.84), ("R49", "2"): (11.047, 11.519, 44.432, 44.947)}
for (r, num), ex in BOX.items():
    p = [q for q in b.FindFootprintByReference(r).Pads() if q.GetNumber() == num][0]; q = p.GetBoundingBox()
    got = (mm(q.GetLeft()) - 100, mm(q.GetRight()) - 100, 100 - mm(q.GetBottom()), 100 - mm(q.GetTop()))
    assert all(abs(g - e) < 0.01 for g, e in zip(got, ex)), ("pad moved", r, num, got, ex)
path("POT_WIPER", [(9.975, 46.19), (9.975, 47.51)])
path("POT_WIPER", [(9.03, 47.51), (9.975, 47.51)])
path("POT_WIPER", [(9.975, 47.51), (9.975, 48.6), (11.3, 49.925), (11.3, 52.9), (11.845, 53.445), (12.745, 53.445)])
path("Net-(U13-ADDR)", [(9.7, 42.745), (9.7, 44.19)])
path("~{ADC_ALERT}", [(9.57, 44.69), (11.283, 44.69)])
pcbnew.SaveBoard(sys.argv[1], b)
for n in sorted(total): print("  %-16s %.1f mm of new track" % (n, total[n]))
print("added %d track segments, no via" % count)
