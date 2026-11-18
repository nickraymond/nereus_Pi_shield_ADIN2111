"""Routing stage A: the two BM2 bus tracks, top layer only, no via. BM1's two tracks were drawn in step 0c and are not touched.

KiCad's Python: stepA_bus.py <board .kicad_pcb (a copy outside git: SaveBoard rewrites the .kicad_pro beside it)>
Frame: X' = KiCad x - 100, y = 100 - KiCad y (mm), as in mocks/review/ROUTING_PLAN_P.md. Coordinates below were set
against the pads and copper read from the stage 0c board with dumpA.py and window.py (2026-11-18):
- BM2_N: L2 pad 2 (X' 20.367..22.526, y 43.661..48.157) straight north to J9 pins 1 and 2 (X' 19.845..21.545,
  y 52.2 and 53.45). 2.0 mm, then 0.6 mm between the two pins (as BM1 at J10).
- BM2_P: from the west end of Sofar's 2.0 mm stub at (16.332, 41.683), north-west to X' 14.7, north between Sofar's
  P_IN copper (from X' 16.057) and the GND via at (12.982, 42.483); necked to 1.6 mm for 2.9 mm through the 2.35 mm
  gap between J8's pads (to X' 13.595) and J9's south mounting pad (from X' 15.945); then under J9's body, between
  its two mounting pads, to pins 3 and 4 from the west. 0.6 mm between the two pins.
Every new track gets the stage's name in no field (tracks have none): the lock check lists them as the only new items."""
import sys, math
import pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); TOP = b.GetLayerID("Top Layer")
def net(n):
    c = b.FindNet("/Top-Level Schematic/" + n); assert c and c.GetNetCode() > 0, n; return c
def V(x, y): return pcbnew.VECTOR2I(pcbnew.FromMM(100 + x), pcbnew.FromMM(100 - y))
new = []
def path(n, pts):
    """pts: (X', y, width of the segment that ENDS here)"""
    for (x0, y0, _), (x1, y1, w) in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(b); t.SetStart(V(x0, y0)); t.SetEnd(V(x1, y1)); t.SetWidth(pcbnew.FromMM(w)); t.SetLayer(TOP); t.SetNet(net(n)); b.Add(t); new.append(t)
        print("  %-6s w %.1f (%.3f, %.3f) -> (%.3f, %.3f)  %.2f mm" % (n, w, x0, y0, x1, y1, math.hypot(x1 - x0, y1 - y0)))
print("BM2_N")
path("BM2_N", [(20.8, 46.5, 0), (20.8, 52.2, 2.0)])
path("BM2_N", [(20.8, 52.2, 0), (20.8, 53.45, 0.6)])
print("BM2_P")
D = 1.0 / math.sqrt(2)
path("BM2_P", [(16.332, 41.683, 0), (14.7, 43.315, 2.0), (14.7, 49.45, 2.0), (14.7, 51.37, 1.6), (14.7 + D, 51.37 + D, 1.6),
               (18.655, 55.325, 2.0), (20.145, 55.325, 2.0)])
path("BM2_P", [(20.145, 54.7, 0), (20.145, 55.95, 0.6)])
pcbnew.SaveBoard(sys.argv[1], b)
print("added %d track segments, top layer, 0 vias" % len(new))
