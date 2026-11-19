"""Routing stage E, part 1: the motor driver's logic lines MOTOR_IN1, MOTOR_IN2, MOTOR_nSLEEP from U12 to the west
header J21 (P7, P8, P14), and the current-sense line MOTOR_VISEN from U12 to the ADC U13. The pot wiper is NOT in
this script.

KiCad's Python: stepE1_motor_logic.py <board .kicad_pcb (a copy outside git)>
Frame: X' = KiCad x - 100, y = 100 - KiCad y (mm). Positions read from the board after stage D (2026-11-18).
B = bottom, I2 = Internal 2, T = top. New vias 0.45 / 0.20 mm (the gap between U12 and TP41 is 0.9 mm).
- One via per logic line at U12: IN1 inside its test pad TP40 at (3.9, 37.3); nSLEEP at (3.1, 39.95) in the gap
  between U12 and TP41; IN2 at (2.55, 42.0) north-east of pin 10.
- Internal 2 from there to the header as three parallel lines 0.4 mm apart at X' 3.9 (IN2), 4.3 (IN1), 4.7 (nSLEEP)
  from y 36 to 22: east of the converter's GND via at (3.15, 29.7), west of the VBUS vias at X' 5.9. The only other
  vias in the wing are further west. The GND plane lies between these lines and the converter on top.
  DEVIATION from the routing plan, which put the three lines in a lane at X' -5.6..-4.6: from that lane the lines
  reach J21 in the order IN1, nSLEEP, IN2 (north to south), while the pins need nSLEEP or IN2 first and IN1 last, so
  two lines would have to cross on the one layer. The direct band has the right order and is about 9 mm shorter.
- At J21: IN2 and IN1 between the two pad columns (X' 2.6 and 3.2, 0.3 mm or more from every hole), nSLEEP east of
  the inner column (X' 5.1); 45 degrees into pins 10, 12 and 9.
- VISEN: bottom from pin 11 through the gap, north-east to y 43.95 (between the test pads TP44 and TP43), one via at
  (7.4, 43.95) under U13's body, top to U13 pin 4."""
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
PADS = {("U12", "1"): (2.045, 39.321), ("U12", "10"): (2.045, 41.329), ("U12", "11"): (2.299, 40.575), ("U12", "12"): (2.299, 40.075),
        ("TP40", "1"): (4.3, 37.3), ("U13", "4"): (9.57, 45.69), ("J21", "9"): (4.14, 9.21), ("J21", "10"): (1.60, 9.21), ("J21", "12"): (1.60, 6.67)}
for (r, num), (ex, ey) in PADS.items():
    p = [q for q in b.FindFootprintByReference(r).Pads() if q.GetNumber() == num][0]
    x, y = mm(p.GetPosition().x) - 100, 100 - mm(p.GetPosition().y)
    assert abs(x - ex) < 0.01 and abs(y - ey) < 0.01, ("pad moved", r, num, (x, y), (ex, ey))
W = 0.2
# MOTOR_IN1: pin 1, test pad TP40, via in the pad, Internal 2 to J21 pin 12
path("MOTOR_IN1", B, W, [(2.045, 39.321), (2.045, 38.6), (3.345, 37.3), (3.9, 37.3)]); via("MOTOR_IN1", 3.9, 37.3)
path("MOTOR_IN1", I2, W, [(3.9, 37.3), (4.3, 36.9), (4.3, 22.0), (3.2, 20.9), (3.2, 10.3), (2.87, 9.97), (2.87, 7.94), (1.60, 6.67)])
# MOTOR_IN2: pin 10, via, Internal 2 to J21 pin 10
path("MOTOR_IN2", B, W, [(2.045, 41.329), (2.045, 41.495), (2.55, 42.0)]); via("MOTOR_IN2", 2.55, 42.0)
path("MOTOR_IN2", I2, W, [(2.55, 42.0), (2.55, 37.55), (3.9, 36.2), (3.9, 22.4), (2.6, 21.1), (2.6, 10.6), (1.60, 9.6), (1.60, 9.21)])
# MOTOR_nSLEEP: pin 12, via in the gap, Internal 2 to J21 pin 9
path("MOTOR_nSLEEP", B, W, [(2.299, 40.075), (2.975, 40.075), (3.1, 39.95)]); via("MOTOR_nSLEEP", 3.1, 39.95)
path("MOTOR_nSLEEP", I2, W, [(3.1, 39.95), (3.1, 39.4), (4.7, 37.8), (4.7, 22.0), (5.1, 21.6), (5.1, 10.17), (4.14, 9.21)])
# MOTOR_VISEN: pin 11, bottom, via under U13, top to U13 pin 4
path("MOTOR_VISEN", B, W, [(2.299, 40.575), (2.9, 40.575), (3.1, 40.775), (3.1, 41.2), (5.85, 43.95), (7.4, 43.95)]); via("MOTOR_VISEN", 7.4, 43.95)
path("MOTOR_VISEN", T, W, [(7.4, 43.95), (7.4, 45.19), (7.9, 45.69), (9.57, 45.69)])
pcbnew.SaveBoard(sys.argv[1], b)
for n in sorted(total): print("  %-14s %.1f mm of new track" % (n, total[n]))
print("added %d track segments and %d vias" % (count["track"], count["via"]))
