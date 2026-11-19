"""Routing stage D, part 2: the ADIN2111's reset line to the N6's P9 (J21 pin 8, the west header's outer column).
ADIN_PWR to P13 (J21 pin 11) is NOT in this script: its nearest copper is on Internal 1 at about (19.0, 15.7), 14 mm
east of the pin under the ADIN2111, and its path is not laid out yet.

KiCad's Python: stepD2_reset.py <board .kicad_pcb (a copy outside git)>
Frame: X' = KiCad x - 100, y = 100 - KiCad y (mm). Positions read from the board after stage D part 1 (2026-11-18).
Sofar's reset line runs on Internal 1 from his via at U1 (10.809, 18.681) by the corners (9.507, 17.404),
(9.507, 16.133) and (10.007, 15.633) to the east. The new track leaves his corner at (10.007, 15.633) at a right
angle, runs south-west on Internal 1 (0.99 mm from his GND via at (7.607, 14.633), 1.38 mm from the BM1 data via at
(9.158, 12.836)), west on the centre line of the gap between J21's inner pads of rows 3 and 4 (y 13.02), and
45 degrees into pin 8 at (1.60, 11.75). No via. The line is static (the chip has its own power-on reset)."""
import sys, math
import pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); FM = pcbnew.FromMM; mm = pcbnew.ToMM
I1 = b.GetLayerID("Internal 1"); assert I1 >= 0
n = [x for name, x in b.GetNetsByName().items() if str(name).endswith("~{ADIN_RST}")]; assert len(n) == 1; n = n[0]
def V(x, y): return pcbnew.VECTOR2I(FM(100 + x), FM(100 - y))
p = [q for q in b.FindFootprintByReference("J21").Pads() if q.GetNumber() == "8"][0]
assert abs(mm(p.GetPosition().x) - 101.60) < 0.01 and abs(100 - mm(p.GetPosition().y) - 11.75) < 0.01 and p.GetNetname().endswith("~{ADIN_RST}")
ends = [(round(mm(e.x) - 100, 3), round(100 - mm(e.y), 3)) for t in b.GetTracks() if t.Type() != pcbnew.PCB_VIA_T and t.GetLayer() == I1 and t.GetNet().GetNetCode() == n.GetNetCode() for e in (t.GetStart(), t.GetEnd())]
assert ends.count((10.007, 15.633)) == 2, "Sofar's corner at (10.007, 15.633) not found"
pts = [(10.007, 15.633), (7.394, 13.02), (2.87, 13.02), (1.60, 11.75)]; tot = 0
for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
    dx, dy = abs(x1 - x0), abs(y1 - y0); assert dx < 1e-6 or dy < 1e-6 or abs(dx - dy) < 1e-6
    t = pcbnew.PCB_TRACK(b); t.SetStart(V(x0, y0)); t.SetEnd(V(x1, y1)); t.SetWidth(FM(0.2)); t.SetLayer(I1); t.SetNet(n); b.Add(t); tot += math.hypot(x1 - x0, y1 - y0)
pcbnew.SaveBoard(sys.argv[1], b)
print("  ~{ADIN_RST}: %.1f mm of new track on Internal 1, 3 segments, no via" % tot)
