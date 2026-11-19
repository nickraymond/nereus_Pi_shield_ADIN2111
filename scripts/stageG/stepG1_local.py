"""Routing stage G, part 1: the LED parts in the west wing (the ADIN_LED_VDD rail and the three anode links), the timer
test pad, the pin 19 net and the ALERT test pad. The strap lines, ADIN_VDDIO and the two LED signal lines are parts 2
and 3.

KiCad's Python: stepG1_local.py <board .kicad_pcb (a copy outside git)>
Frame: X' = KiCad x - 100, y = 100 - KiCad y (mm). Positions read from the board at commit 4dc6f74 (2026-11-18).
T = top, B = bottom, I1 = Internal 1. All new track 0.2 mm. New vias 0.45 / 0.20 mm.
- ADIN_LED_VDD: a top rail at X' -2.85, east of the resistor column, from JP2 pad 2 north to R44 pad 2, with a stub
  west into pad 2 of R46, R45 and R44.
- Anode links, top: from each LED's pad 2 east, south in the 0.8 mm gap between the LED column and the resistor
  column (X' -4.325, 0.3 mm from the pads on both sides), into pad 1 of its resistor. D10 / R46, D9 / R45, D8 / R44.
- ADIN_TIMER, top: R47 pad 1 west and north at X' 5.6, between R47 and the header's inner column, into TP45.
- Pin 19 net (U1 P1_LED_0 / SPI_CFG1): top from R47 pad 2 east and south at X' 7.09 between R47 and C21, south-west
  round R47 pad 1, south at X' 6.6 west of Sofar's GND via (7.257, 16.783), east at y 16.1 into R2 pad 1. One via at
  (6.6, 17.3) on that track, then Internal 1 north-east and east at y 19.345 into Sofar's via (10.794, 19.345), which
  his top track joins to U1 pin 19. On top and bottom that via is shut in (crystal nets, C21, the VDDIO tracks).
- ~ADC_ALERT to its test pad TP44 (bottom, round, centre (7.4, 42.7)): top from U13 pin 2 west under U13's body to a
  via at (8.35, 44.5), bottom south and into the pad. The via is 0.2 mm from the test pad TP43 (SCL).
- The rail and the links shut the top GND pour round D8 pad 1 (the power LED's cathode) off from the rest: one GND
  via at (-5.2, 17.9) between D9 and D8 ties it to the GND plane (found by the pour check on the trial run)."""
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
expect({("JP2", "2"): (-4.4, 9.45), ("R46", "1"): (-3.6, 12.325), ("R46", "2"): (-3.6, 13.275), ("R45", "1"): (-3.6, 15.725), ("R45", "2"): (-3.6, 16.675),
        ("R44", "1"): (-3.6, 19.125), ("R44", "2"): (-3.6, 20.075), ("D10", "2"): (-5.2, 13.588), ("D9", "2"): (-5.2, 16.988), ("D8", "2"): (-5.2, 20.388),
        ("R47", "1"): (6.4, 18.825), ("R47", "2"): (6.4, 19.775), ("TP45", "1"): (5.6, 21.8), ("R2", "1"): (8.9, 16.4), ("U13", "2"): (9.57, 44.69), ("TP44", "1"): (7.4, 42.7), ("D8", "1"): (-5.2, 18.812)})
expect_via("SPI_CFG1)", 10.794, 19.345); expect_via("GND", 7.257, 16.783); expect_via("I2C0_SCL", 6.85, 45.2)
W = 0.2
LV = "ADIN_LED_VDD"
path(LV, T, W, [(-3.4, 9.45), (-3.05, 9.45), (-2.85, 9.65), (-2.85, 20.075), (-3.6, 20.075)])
path(LV, T, W, [(-2.85, 13.275), (-3.6, 13.275)])
path(LV, T, W, [(-2.85, 16.675), (-3.6, 16.675)])
for d, y in (("D10", 13.588), ("D9", 16.988), ("D8", 20.388)):
    path("Net-(%s-A)" % d, T, W, [(-5.2, y), (-4.5, y), (-4.325, y - 0.175), (-4.325, y - 1.088), (-4.15, y - 1.263), (-3.6, y - 1.263)])
path("ADIN_TIMER", T, W, [(6.4, 18.825), (5.85, 18.825), (5.6, 19.075), (5.6, 21.8)])
P19 = "Net-(U1A-P1_LED_0{slash}SPI_CFG1)"
path(P19, T, W, [(6.4, 19.775), (6.9, 19.775), (7.09, 19.585), (7.09, 18.2), (6.6, 17.71), (6.6, 16.3), (6.8, 16.1), (8.6, 16.1), (8.9, 16.4)])
via(P19, 6.6, 17.3)
path(P19, I1, W, [(6.6, 17.3), (8.645, 19.345), (10.794, 19.345)])
AL = "~{ADC_ALERT}"
path(AL, T, W, [(9.57, 44.69), (8.54, 44.69), (8.35, 44.5)]); via(AL, 8.35, 44.5)
path(AL, B, W, [(8.35, 44.5), (8.35, 43.4), (7.93, 42.98)])
path("GND", T, 0.25, [(-5.2, 18.812), (-5.2, 17.9)]); via("GND", -5.2, 17.9)
done()
