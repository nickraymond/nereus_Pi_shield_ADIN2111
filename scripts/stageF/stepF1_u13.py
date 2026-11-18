"""Routing stage F, part 1: the I2C bus to the ADC U13 and to its test pad TP43, U13's ground pin, and the N6 3V3
link between C68, C65 and U13 pin 8. The lines to the QWIIC connector and the N6 3V3 feed are parts 2 and 3.

KiCad's Python: stepF1_u13.py <board .kicad_pcb (a copy outside git)>
Frame: X' = KiCad x - 100, y = 100 - KiCad y (mm). Positions read from the board at commit edfa070 (2026-11-18).
T = top, I2 = Internal 2. New vias 0.45 / 0.20 mm (Sofar's size).
- SDA and SCL start on Internal 2 at Sofar's own bus vias beside U4, (9.932, 25.408) and (10.657, 25.208); no new
  via there. Two parallel lines 0.15 mm wide, 0.35 mm apart (Sofar's I2C tracks in the block are 0.15 mm): north at
  X' 10.15 / 10.5 between the GND and UVLO vias at X' 9.557 and the ALERT via at (11.082, 28.683); north-west at 45
  degrees through the gap between the UVLO via (9.557, 31.533) and the VBUS via (9.707, 33.433), the widest gap
  there (1.3 mm between the via pads); north at X' 6.3 (SDA) and 6.85 (SCL) under T2 to U13. They stay 1.5 mm or
  more east of the motor logic lines at X' 3.9..4.7.
- One via per line under U13's body: SDA at (6.3, 44.69), in line with pin 9; SCL at (6.85, 45.2), on the edge of the
  bottom test pad TP43 (round, 1.5 mm, centre (7.4, 45.2)), so the one via also joins the test pad. Top from the vias
  into pins 9 and 10 from the east; SCL runs 0.35 mm west of the VISEN track at X' 7.4.
- U13 pin 3 (GND): top, east out of the pin row at y 45.19, north at X' 10.7 into R51 pad 2, whose GND via at
  (11.45, 47.51) then serves the ADC and its input filter (R51, C67) together. A via of its own east of the pin would
  stand in the way of part 3's lines.
- N6 3V3 on top at y 45.19: C68 pad 1, C65 pad 1, U13 pin 8 (0.3 mm, 0.25 mm into the pin).
- That track shuts the top GND pour south of U13 off from the pour north of it; the piece holds R50 pad 2 (U13's
  address resistor). One GND via at (8.94, 43.5) north of that pad ties it to the GND plane (found by the pour check
  on the trial run)."""
import sys, math
import pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); FM = pcbnew.FromMM; mm = pcbnew.ToMM
T, B, I2 = (b.GetLayerID(n) for n in ("Top Layer", "6 Bottom Layer", "Internal 2")); assert min(T, B, I2) >= 0
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
SDA, SCL, V3 = "I2C0_SDA", "I2C0_SCL", "N6_3V3"
expect({("U13", "3"): (9.57, 45.19), ("U13", "8"): (5.27, 45.19), ("U13", "9"): (5.27, 44.69), ("U13", "10"): (5.27, 44.19), ("TP43", "1"): (7.4, 45.2),
        ("C65", "1"): (3.72, 45.19), ("C68", "1"): (2.6, 45.221), ("R51", "2"): (10.705, 47.51), ("R50", "2"): (8.941, 42.745)})
expect_via(SDA, 9.932, 25.408); expect_via(SCL, 10.657, 25.208); expect_via("MOTOR_VISEN", 7.4, 43.95); expect_via("GND", 11.45, 47.51)
W = 0.15
# the two diagonals are the lines x + y = 41.87 (SDA) and 42.36 (SCL): 0.35 mm apart
path(SDA, I2, W, [(9.932, 25.408), (10.15, 25.626), (10.15, 31.72), (6.3, 35.57), (6.3, 44.69)]); via(SDA, 6.3, 44.69)
path(SCL, I2, W, [(10.657, 25.208), (10.5, 25.365), (10.5, 31.86), (6.85, 35.51), (6.85, 45.2)]); via(SCL, 6.85, 45.2)
path(SDA, T, 0.2, [(6.3, 44.69), (5.27, 44.69)])
path(SCL, T, 0.2, [(6.85, 45.2), (6.85, 44.44), (6.6, 44.19), (5.27, 44.19)])
path("GND", T, 0.25, [(9.57, 45.19), (10.7, 45.19), (10.7, 47.51)])
path("GND", T, 0.25, [(8.94, 42.745), (8.94, 43.5)]); via("GND", 8.94, 43.5)
path(V3, T, 0.3, [(2.6, 45.19), (4.3, 45.19)])
path(V3, T, 0.25, [(4.3, 45.19), (5.27, 45.19)])
done()
