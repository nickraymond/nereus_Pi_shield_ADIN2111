"""Routing stage C, part 2: the motor driver U12 (MP6550, bottom layer): its 5 V supply, the two motor outputs to
connector J7 and the test points TP41 / TP42, and its small parts. The motor logic lines and VISEN are stage E and
are NOT in this script.

KiCad's Python: stepC2_motor.py <board .kicad_pcb (a copy outside git)>
Frame: X' = KiCad x - 100, y = 100 - KiCad y (mm). Pad boxes read from the stage C part 1 board with
scripts/stageA/window.py (2026-11-18). T = top layer, B = bottom layer. Vias 0.6 / 0.3 mm (the project's default).
U12's pins (MP6550 datasheet Rev. 1.0, 7/16/2019, "Pin Functions"; they agree with the board's nets): 1 IN1, 2 OUT1,
3 GND, 4 V3P3, 5 nSLEEP_LDO, 6 VCC, 7 ISET, 8 OUT2, 9 VIN, 10 IN2, 11 VISEN, 12 nSLEEP_HB. The package has twelve
pads and no centre pad on the board, so the heat leaves through the pins: OUT1, OUT2, VIN and GND each get copper
and vias next to the chip.
- 5 V at the bulk capacitors: C62, C66, C60 pad 1 joined by a 0.8 mm bottom track at X' -5.2, with three vias into the
  5 V area of the PWR plane.
- 5 V to U12: a new 5 V area on the PWR plane ("N6 5V U12") that joins the stage B area over y 42.6..45.6, runs east
  as a band y 44.3..46.3 and comes down as a tab X' 1.25..3.0 to C61 pad 1; two vias north of that pad; pin 9
  straight north into the pad. The area is cut back round the GND via of C61 and the test-point via of MOTOR_OUT2,
  so that the plane under them stays GND. A track on an outer layer would have to cross a motor output.
- MOTOR_OUT1 (pin 2, south side): 0.2 mm, then 0.4 mm south, two vias, then 0.6 mm on TOP: west of U12 at X' -0.9,
  north, 45 degrees to the lane between J7's mounting pad and its pins (X' 3.4), into pins 1 and 2 from the west.
  TP41 (bottom): a 0.25 mm top branch at y 39.3 and one via inside the test pad.
- MOTOR_OUT2 (pin 8, north side): 0.2 mm, west between the pin row and C61 (0.3 mm), then 0.6 mm on the BOTTOM at
  X' 0.0 north under J7, 45 degrees to two vias west of pins 3 and 4, short top tracks into the pins.
  TP42 (top): one via on the trunk at y 42.6 and a 0.25 mm top branch.
- Small parts: pin 4 to C64, pin 6 to C63, pin 7 to R48, 0.2 mm on the bottom. Their GND pads and the bulk
  capacitors' GND pads join through the bottom GND pour, with two vias between C62 and C66.
- Ground: pin 3 to a via south-west of the pin; C61 pad 2 to a via north of it."""
import sys, math
import pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); FM = pcbnew.FromMM
T, B = b.GetLayerID("Top Layer"), b.GetLayerID("6 Bottom Layer"); PWR = b.GetLayerID("PWR Plane")
assert min(T, B, PWR) >= 0
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
def via(n, x, y):
    v = pcbnew.PCB_VIA(b); v.SetPosition(V(x, y)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(T, B)
    v.SetWidth(pcbnew.F_Cu, FM(0.6)); v.SetDrill(FM(0.3)); v.SetNet(net(n)); b.Add(v); count["via"] += 1
# the pads this script relies on must be where they were read (0.01 mm), else stop
EXPECT = {("U12", "2"): (1.545, 39.446), ("U12", "3"): (1.045, 39.446), ("U12", "4"): (0.545, 39.321), ("U12", "6"): (0.291, 40.575),
          ("U12", "7"): (0.545, 41.329), ("U12", "8"): (1.045, 41.204), ("U12", "9"): (1.545, 41.204), ("C61", "1"): (1.694, 42.725),
          ("C61", "2"): (0.936, 42.725), ("C62", "1"): (-5.285, 39.525), ("C66", "1"): (-5.505, 42.625), ("C60", "1"): (-4.972, 44.525),
          ("C64", "1"): (-0.918, 39.075), ("C63", "1"): (-0.906, 40.295), ("R48", "1"): (-0.906, 41.275), ("TP41", "1"): (4.3, 40.3),
          ("TP42", "1"): (4.3, 42.1), ("J7", "1"): (4.795, 52.2), ("J7", "2"): (4.795, 53.45), ("J7", "3"): (4.795, 54.7), ("J7", "4"): (4.795, 55.95)}
for (r, num), (ex, ey) in EXPECT.items():
    p = [q for q in b.FindFootprintByReference(r).Pads() if q.GetNumber() == num][0]
    x, y = pcbnew.ToMM(p.GetPosition().x) - 100, 100 - pcbnew.ToMM(p.GetPosition().y)
    assert abs(x - ex) < 0.01 and abs(y - ey) < 0.01, ("pad moved", r, num, (x, y), (ex, ey))
V5, O1, O2 = "5V_PI", "MOTOR_OUT1", "MOTOR_OUT2"
# 5 V at the bulk capacitors
path(V5, B, 0.8, [(-5.2, 39.525), (-5.2, 45.2)])
via(V5, -5.2, 41.07); via(V5, -5.2, 43.78); via(V5, -5.2, 45.2)
# 5 V area on the PWR plane from the stage B area to C61
z5 = [z for z in b.Zones() if z.GetZoneName() == "N6 5V"]; assert len(z5) == 1 and z5[0].GetAssignedPriority() == 2
z = pcbnew.ZONE(b); z.SetLayer(PWR); z.SetNet(net(V5)); z.SetZoneName("N6 5V U12"); z.SetAssignedPriority(3)
o = pcbnew.SHAPE_POLY_SET(); o.NewOutline()
for p in ((-2.7, 42.6), (-1.2, 42.6), (-1.2, 44.3), (1.25, 44.3), (1.25, 42.3), (3.0, 42.3), (3.0, 46.3), (-2.7, 46.3)): o.Append(V(*p))
z.Outline().Append(o)
z.SetLocalClearance(FM(0.3)); z.SetMinThickness(FM(0.25)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS); z.SetIsRuleArea(False); z.SetFillMode(pcbnew.ZONE_FILL_MODE_POLYGONS)
b.Add(z); print("  zone 'N6 5V U12' added on the PWR plane, priority 3 (the stage B 5 V area has 2, the GND pour of that layer 1)")
# 5 V at U12: pin 9 into C61 pad 1, two vias north of the pad
path(V5, B, 0.2, [(1.545, 41.204), (1.545, 41.85)])
path(V5, B, 0.3, [(1.545, 41.85), (1.545, 42.725)])
path(V5, B, 0.5, [(1.694, 42.725), (1.694, 44.25)])
via(V5, 1.694, 43.55); via(V5, 1.694, 44.25)
# MOTOR_OUT1
path(O1, B, 0.2, [(1.545, 39.446), (1.545, 38.5)])
path(O1, B, 0.4, [(1.545, 38.5), (1.545, 37.8)])
path(O1, B, 0.6, [(1.545, 37.8), (1.195, 37.45), (0.395, 37.45)])
via(O1, 1.195, 37.45); via(O1, 0.395, 37.45)
path(O1, T, 0.6, [(1.195, 37.45), (0.0, 37.45), (-0.9, 38.35), (-0.9, 44.4), (3.4, 48.7), (3.4, 53.45)])
path(O1, T, 0.6, [(3.4, 52.2), (4.795, 52.2)])
path(O1, T, 0.6, [(3.4, 53.45), (4.795, 53.45)])
path(O1, T, 0.25, [(-0.9, 39.3), (3.3, 39.3), (3.95, 39.95)]); via(O1, 3.95, 39.95)
# MOTOR_OUT2
path(O2, B, 0.2, [(1.045, 41.204), (1.045, 41.85), (0.815, 42.08)])
path(O2, B, 0.3, [(0.815, 42.08), (0.0, 42.08)])
path(O2, B, 0.6, [(0.0, 42.08), (0.0, 51.4), (3.3, 54.7), (3.3, 55.95)])
via(O2, 3.3, 54.7); via(O2, 3.3, 55.95)
path(O2, T, 0.6, [(4.795, 54.7), (3.3, 54.7), (3.3, 55.95), (4.795, 55.95)])
via(O2, 0.0, 42.6); path(O2, T, 0.25, [(0.0, 42.6), (4.0, 42.6)])
# small parts
path("Net-(U12-V3P3)", B, 0.2, [(0.545, 39.2), (-0.918, 39.2)])
path("Net-(U12-VCC)", B, 0.2, [(0.291, 40.575), (-0.35, 40.575), (-0.63, 40.295), (-0.906, 40.295)])
path("Net-(U12-ISET)", B, 0.2, [(0.545, 41.3), (-0.906, 41.3)])
# ground
path("GND", B, 0.2, [(1.045, 39.446), (1.045, 38.65), (0.845, 38.45)]); via("GND", 0.845, 38.45)
path("GND", B, 0.3, [(0.85, 42.725), (0.85, 43.6)]); via("GND", 0.85, 43.6)
via("GND", -3.4, 41.07); via("GND", -2.55, 41.07)
pcbnew.SaveBoard(sys.argv[1], b)
for n in sorted(total): print("  %-16s %.1f mm of track" % (n, total[n]))
print("added %d track segments, %d vias and 1 zone" % (count["track"], count["via"]))
