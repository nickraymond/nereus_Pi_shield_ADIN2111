"""Routing stage G, part 3: the three long lines: the CFG0 strap from JP4 to R9, the LED line ~ADIN_P2_LED1 from D10
to U1, and ADIN_VDDIO to R52 (the pull-up of ~ADIN_CS in the east strip).

KiCad's Python: stepG3_long.py <board .kicad_pcb (a copy outside git)>
Frame: X' = KiCad x - 100, y = 100 - KiCad y (mm). Positions read from the board at commit 0c7c3f6 (2026-11-18).
T = top, B = bottom, I2 = Internal 2. New vias 0.45 / 0.20 mm. Signal track 0.2 mm, VDDIO 0.3 mm.
- CFG0_STRAP (JP4 pad 2 to R9 pad 1, 35 mm apart, across Sofar's block): bottom from JP4 pad 2 north, east at y 15.1,
  through the header gap at y 15.56, a via at (5.9, 15.56). Internal 2 east at y 15.77: between the crystal's two
  vias (0.5 mm from each), between U1's south via row and its thermal vias, then two short 45 degree steps to pass
  north of the DVDD1 via (19.674, 16.308) and between the VDDIO via (19.776, 17.677) and the INT via (20.502, 16.762),
  0.25 mm from each; east at y 17.7; south-east to a via at (28.0, 16.55), north of the CS via; top into R9 pad 1.
- ~ADIN_P2_LED1: top all the way to one via: from D10 pad 1 west, north along the board's west edge at X' -5.95
  (0.55 mm from the edge, 0.175 mm from the LED pads), east at y 21.3 north of the LED parts and of the header, to a
  via at (5.6, 23.0) north of TP45; Internal 2 east at y 22.639 into Sofar's via at (19.122, 22.639) beside U1 pin
  48. The LED_VDD rail shuts D10 off to the east, and the bottom below it holds the jumpers.
- ADIN_VDDIO to R52 pad 1: top east to a via at (30.2, 8.921) between R52 and the header; Internal 2 north at X' 30.2
  (east of the SPI and I2C vias, 0.6 mm from the header's pin holes), west at y 18.25, 0.3 mm north of the CFG0 line,
  south-west into Sofar's VDDIO via at (19.776, 17.677). West of X' 29.2 the direct way is shut by this session's CS
  and SCK lines on Internal 2 and Sofar's GND vias."""
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
expect({("JP4", "2"): (-3.855, 13.895), ("R9", "1"): (28.78, 15.883), ("D10", "1"): (-5.2, 12.012), ("TP45", "1"): (5.6, 21.8), ("R52", "1"): (29.6, 8.921)})
expect_via("~{ADIN_P2_LED1}", 19.122, 22.639); expect_via("ADIN_VDDIO", 19.776, 17.677); expect_via("~{ADIN_INT}", 20.502, 16.762)
expect_via("DVDD1_1P1", 19.674, 16.308); expect_via("~{ADIN_CS}", 26.157, 16.083); expect_via("~{ADIN_P1_LED1}", 5.95, 18.083)
C0, P2, VD = "CFG0_STRAP", "~{ADIN_P2_LED1}", "ADIN_VDDIO"
# CFG0_STRAP
path(C0, B, 0.2, [(-3.6, 13.895), (-3.6, 14.9), (-3.4, 15.1), (-1.0, 15.1), (-0.54, 15.56), (5.9, 15.56)]); via(C0, 5.9, 15.56)
path(C0, I2, 0.2, [(5.9, 15.56), (6.11, 15.77), (18.0, 15.77), (19.22, 16.99), (19.909, 16.99), (20.619, 17.7), (26.85, 17.7), (28.0, 16.55)]); via(C0, 28.0, 16.55)
path(C0, T, 0.2, [(28.0, 16.55), (28.667, 15.883), (28.78, 15.883)])
# ~ADIN_P2_LED1
path(P2, T, 0.2, [(-5.2, 12.012), (-5.75, 12.012), (-5.95, 12.212), (-5.95, 21.1), (-5.75, 21.3), (3.5, 21.3), (5.2, 23.0), (5.6, 23.0)]); via(P2, 5.6, 23.0)
path(P2, I2, 0.2, [(5.6, 23.0), (5.961, 22.639), (19.122, 22.639)])
# ADIN_VDDIO to R52
path(VD, T, 0.25, [(29.6, 8.921), (30.2, 8.921)]); via(VD, 30.2, 8.921)
path(VD, I2, 0.3, [(30.2, 8.921), (30.2, 17.55), (29.5, 18.25), (20.349, 18.25), (19.776, 17.677)])
done()
