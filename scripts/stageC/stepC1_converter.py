"""Routing stage C, part 1: the 5 V converter (U10, L6 and their parts) and its feeds. U12's supply and the motor
outputs are part 2 and are NOT in this script.

KiCad's Python: stepC1_converter.py <board .kicad_pcb (a copy outside git)>
Frame: X' = KiCad x - 100, y = 100 - KiCad y (mm). Pad boxes read from the stage B board with window.py (2026-11-18).
T = top layer, B = bottom layer. Vias 0.6 / 0.3 mm (the project's default).
- Switch node: U10 pin 2 to L6 pad 1 on top (0.5 mm at the pin, 0.8 mm after); one via under U10 to the boot
  capacitor C53 on the bottom. Boot pin 6 to C53 by one via west of the pin.
- VBUS feed: from the corner of Sofar's two 1.0 mm VBUS tracks on the bottom at (7.082, 26.783), which is on the
  load side of the shunt R8, 1.0 mm on the bottom up X' 5.9 (0.36 mm from his P_IN track, whose edge is at
  X' 6.757), two vias, then on top to C54, C55, U10 pin 3 and R39.
- 5 V output: L6 pad 2 to C56, C57, C58 on top; three vias into the 5 V area of the PWR plane (two between L6 and
  C56, one beside C58), which carries it to the N6's VIN pin; test point TP38 on the bottom from one of the vias.
- Feedback: taken at C58 (after the output capacitors), 0.2 mm to R37; R37 / R38 to pin 4.
- UVLO divider R39 / R40 to pin 5, under U10's body.
- Ground: vias at U10 pin 1, C56, C57 and C55 / C54 into the planes; a short track from R40 into the top pour."""
import sys, math
import pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); FM = pcbnew.FromMM
T, B = b.GetLayerID("Top Layer"), b.GetLayerID("6 Bottom Layer")
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
# switch node and boot capacitor
path("5V_Buck_SW", T, 0.5, [(2.47, 32.67), (2.47, 31.7)])
path("5V_Buck_SW", T, 0.8, [(2.47, 31.7), (1.7, 30.93), (1.7, 29.8)])
path("5V_Buck_SW", T, 0.3, [(2.47, 32.67), (2.47, 33.75)]); via("5V_Buck_SW", 2.47, 33.75)
path("5V_Buck_SW", B, 0.3, [(2.47, 33.75), (1.55, 33.75)])
path("Net-(U10-CB)", T, 0.3, [(1.52, 35.42), (0.65, 35.42)]); via("Net-(U10-CB)", 0.65, 35.42)
path("Net-(U10-CB)", B, 0.25, [(0.65, 35.42), (0.65, 34.95), (1.05, 34.55), (1.4, 34.55)])
# VBUS feed
path("VBUS", B, 1.0, [(7.082, 26.783), (5.9, 27.965), (5.9, 33.0)])
via("VBUS", 5.9, 32.25); via("VBUS", 5.9, 33.0)
path("VBUS", T, 0.6, [(5.9, 33.0), (5.9, 32.25), (5.45, 31.8)])
path("VBUS", T, 0.3, [(5.27, 32.73), (5.27, 31.6)])
path("VBUS", T, 0.6, [(5.2, 31.1), (3.97, 31.1)])
path("VBUS", T, 0.5, [(3.97, 31.1), (3.42, 31.65), (3.42, 32.67)])
# 5 V output
path("5V_PI", T, 0.9, [(-3.05, 29.5), (-3.05, 30.98), (-3.05, 34.6)])
path("5V_PI", T, 0.6, [(-3.05, 30.98), (-3.4, 30.98)]); via("5V_PI", -3.4, 30.98)
path("5V_PI", T, 0.6, [(-3.05, 30.98), (-2.65, 30.98)]); via("5V_PI", -2.65, 30.98)
path("5V_PI", T, 0.5, [(-3.05, 34.6), (-2.8, 34.85), (-2.8, 35.84)])
path("5V_PI", T, 0.6, [(-3.05, 34.6), (-3.55, 35.1), (-3.55, 35.65)]); via("5V_PI", -3.55, 35.65)
path("5V_PI", B, 0.4, [(-2.65, 30.98), (-2.65, 31.9)])
# feedback
path("5V_PI", T, 0.2, [(-2.8, 35.84), (-2.8, 36.4), (-2.6, 36.6), (1.4, 36.6), (2.0, 37.2)])
path("5V_FB", T, 0.2, [(2.87, 37.2), (3.42, 36.65), (3.42, 35.42)])
path("5V_FB", T, 0.2, [(2.87, 37.2), (2.87, 37.675), (2.77, 37.775), (2.17, 37.775), (2.07, 37.875), (2.07, 38.4)])
# UVLO
path("5V_UVLO", T, 0.2, [(5.27, 33.78), (5.27, 34.62), (5.15, 34.5), (2.9, 34.5), (2.47, 34.93), (2.47, 35.42)])
# ground
path("GND", T, 0.4, [(1.52, 32.67), (0.55, 32.67)]); via("GND", 0.55, 32.67)
path("GND", T, 0.6, [(-1.355, 32.34), (-0.3, 32.34)]); via("GND", -0.3, 32.34)
path("GND", T, 0.6, [(-1.355, 34.34), (-0.3, 34.34)]); via("GND", -0.3, 34.34)
path("GND", T, 0.4, [(5.2, 29.7), (3.97, 29.7), (3.15, 29.7)]); via("GND", 3.15, 29.7)
path("GND", T, 0.3, [(5.27, 35.37), (4.5, 35.37)])
# the 5 V area of stage B: solid connection at the VIN pin (with spokes, KiCad reports the pin's connection as starved,
# because only the west spoke reaches the main area; the area is 15 um inner copper, so soldering the pin is not at stake)
z5 = [z for z in b.Zones() if z.GetZoneName() == "N6 5V"]; assert len(z5) == 1
z5[0].SetPadConnection(pcbnew.ZONE_CONNECTION_FULL); print("  zone 'N6 5V': pad connection set to solid")
pcbnew.SaveBoard(sys.argv[1], b)
for n in sorted(total): print("  %-14s %.1f mm of track" % (n, total[n]))
print("added %d track segments and %d vias" % (count["track"], count["via"]))
