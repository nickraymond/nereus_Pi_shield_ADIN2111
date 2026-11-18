"""Routing stage G, part 2: ADIN_VDDIO to the three jumpers in the west wing, the CFG1 strap from JP3 to R2, and the
LED line ~ADIN_P1_LED1 from D9 to U1. CFG0, ~ADIN_P2_LED1 and R52's VDDIO are part 3.

KiCad's Python: stepG2_west.py <board .kicad_pcb (a copy outside git)>
Frame: X' = KiCad x - 100, y = 100 - KiCad y (mm). Positions read from the board at commit d39a491 (2026-11-18).
T = top, B = bottom, I1 = Internal 1, I2 = Internal 2. New vias 0.45 / 0.20 mm. Signal track 0.2 mm, VDDIO 0.3 mm.
The west header J21 lies between the wing and U1. On Internal 2 the three motor logic lines run north to south
through it, so nothing crosses it there; these lines cross on the bottom through the gaps between the header's pad
rows (one track per gap, on the gap's centre line) or on Internal 1 north of the header.
- ADIN_VDDIO in the wing: JP3 pad 1 to JP4 pad 3 on the bottom, in the band between the two jumpers. JP2 pad 1 (top)
  to JP3 pad 1 (bottom) through a via at (-5.45, 8.0), west of JP2's bridge. Feed: a via at (-1.6, 13.895) east of JP4
  pad 3, Internal 1 north at X' -1.6, east at y 20.6 north of the header (0.63 mm from the pin holes), into Sofar's
  VDDIO via at (10.832, 20.108) beside U1 pin 18. On the bottom that via is shut in by his GND track at X' 7.932.
- CFG1_STRAP: bottom from JP3 pad 2 south, east at y 8.9, through the header gap at y 10.48, a via at (6.6, 10.48);
  top north at X' 6.6, east at y 15.56 under R2 pad 1, into R2 pad 2 from the south-west.
- ~ADIN_P1_LED1: top from D9 pad 1 to a via at (-4.325, 15.1) in the gap between the LED and resistor columns (the
  LED_VDD rail east of the resistors shuts the top off); bottom north-east and through the header gap at y 18.083; a
  via at (5.95, 18.083); Internal 2 straight east into Sofar's via at (10.857, 18.083) beside U1 pin 21.
- The new bottom tracks shut the bottom GND pour round JP3 pad 3 off from the rest: one GND via at (-1.5, 10.295)
  east of that pad ties it to the GND plane (found by the pour check on the trial run)."""
import sys, math
import pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); FM = pcbnew.FromMM; mm = pcbnew.ToMM
T, B, I1, I2 = (b.GetLayerID(n) for n in ("Top Layer", "6 Bottom Layer", "Internal 1", "Internal 2")); assert min(T, B, I1, I2) >= 0
def net(suffix):
    c = [n for name, n in b.GetNetsByName().items() if str(name) == suffix or str(name).endswith("/" + suffix)]
    assert len(c) == 1 and c[0].GetNetCode() > 0, (suffix, len(c)); return c[0]
def V(x, y): return pcbnew.VECTOR2I(FM(100 + x), FM(100 - y))
count = {"track": 0, "via": 0}; total = {}
def path(n, layer, w, pts):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        dx, dy = abs(x1 - x0), abs(y1 - y0); assert dx < 1e-6 or dy < 1e-6 or abs(dx - dy) < 1e-6, ("not straight or 45 deg", n, (x0, y0), (x1, y1))
        t = pcbnew.PCB_TRACK(b); t.SetStart(V(x0, y0)); t.SetEnd(V(x1, y1)); t.SetWidth(FM(w)); t.SetLayer(layer); t.SetNet(net(n)); b.Add(t)
        count["track"] += 1; total[n] = total.get(n, 0) + math.hypot(x1 - x0, y1 - y0)
def via(n, x, y, d=0.45, h=0.2):
    v = pcbnew.PCB_VIA(b); v.SetPosition(V(x, y)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(T, B)
    v.SetWidth(pcbnew.F_Cu, FM(d)); v.SetDrill(FM(h)); v.SetNet(net(n)); b.Add(v); count["via"] += 1
def expect(pads):
    for (r, num), (ex, ey) in pads.items():
        p = [q for q in b.FindFootprintByReference(r).Pads() if q.GetNumber() == num][0]
        x, y = mm(p.GetPosition().x) - 100, 100 - mm(p.GetPosition().y)
        assert abs(x - ex) < 0.01 and abs(y - ey) < 0.01, ("pad moved", r, num, (x, y), (ex, ey))
def expect_via(n, x, y):
    assert any(t.Type() == pcbnew.PCB_VIA_T and t.GetNetname().endswith(n) and abs(mm(t.GetPosition().x) - 100 - x) < 0.005 and abs(100 - mm(t.GetPosition().y) - y) < 0.005 for t in b.GetTracks()), ("via not found", n, x, y)
def done():
    pcbnew.SaveBoard(sys.argv[1], b)
    for n in sorted(total): print("  %-14s %.1f mm of new track" % (n, total[n]))
    print("added %d track segments and %d vias" % (count["track"], count["via"]))
expect({("JP2", "1"): (-4.4, 6.549), ("JP3", "1"): (-5.155, 10.295), ("JP3", "2"): (-3.855, 10.295), ("JP4", "3"): (-2.555, 13.895),
        ("R2", "2"): (9.7, 16.4), ("R2", "1"): (8.9, 16.4), ("D9", "1"): (-5.2, 15.412), ("JP3", "3"): (-2.555, 10.295)})
expect_via("ADIN_VDDIO", 10.832, 20.108); expect_via("~{ADIN_P1_LED1}", 10.857, 18.083); expect_via("SPI_CFG1)", 6.6, 17.3)
VD, C1, P1 = "ADIN_VDDIO", "CFG1_STRAP", "~{ADIN_P1_LED1}"
# ADIN_VDDIO
path(VD, B, 0.3, [(-5.155, 10.295), (-5.155, 11.6), (-4.455, 12.3), (-3.3, 12.3), (-2.555, 13.045), (-2.555, 13.895)])
via(VD, -5.45, 8.0)
path(VD, T, 0.3, [(-5.45, 8.0), (-5.45, 7.0)])
path(VD, B, 0.3, [(-5.45, 8.0), (-5.45, 9.6)])
path(VD, B, 0.3, [(-2.555, 13.895), (-1.6, 13.895)]); via(VD, -1.6, 13.895)
path(VD, I1, 0.3, [(-1.6, 13.895), (-1.6, 20.0), (-1.0, 20.6), (10.34, 20.6), (10.832, 20.108)])
# CFG1_STRAP
path(C1, B, 0.2, [(-3.855, 10.295), (-3.855, 9.2), (-3.555, 8.9), (-1.9, 8.9), (-0.32, 10.48), (6.6, 10.48)]); via(C1, 6.6, 10.48)
path(C1, T, 0.2, [(6.6, 10.48), (6.6, 15.26), (6.9, 15.56), (9.06, 15.56), (9.7, 16.2), (9.7, 16.4)])
# ~ADIN_P1_LED1
path(P1, T, 0.2, [(-5.2, 15.412), (-4.637, 15.412), (-4.325, 15.1)]); via(P1, -4.325, 15.1)
path(P1, B, 0.2, [(-4.325, 15.1), (-4.325, 15.6), (-1.842, 18.083), (5.95, 18.083)]); via(P1, 5.95, 18.083)
path(P1, I2, 0.2, [(5.95, 18.083), (10.857, 18.083)])
path("GND", B, 0.25, [(-2.555, 10.295), (-1.5, 10.295)]); via("GND", -1.5, 10.295)
done()
