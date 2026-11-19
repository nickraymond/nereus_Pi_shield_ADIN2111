"""Routing stage D, part 3: ADIN_PWR to the N6's P13 (J21 pin 11, the west header's inner column).

KiCad's Python: stepD3_adinpwr.py <board .kicad_pcb (a copy outside git)>
Frame: X' = KiCad x - 100, y = 100 - KiCad y (mm). Positions read from the board after stage D part 2 (2026-11-18).
Sofar's ADIN_PWR copper nearest to the pin is his Internal 1 track from (19.040, 15.728) to (21.499, 15.728). A scan of
that track (scratch script viasite: a 0.45 mm via against all other-net copper on all six layers at 0.2 mm) leaves
X' 20.68..21.29 free. One new via (0.45 / 0.20 mm) at (21.0, 15.728), then Internal 2: south-west to y 10.5 (between
his VBUS via at (16.107, 11.733) and his GND via at (15.132, 9.333)), west along y 10.5, and 45 degrees into pin 11 at
(4.14, 6.67). Internal 2 holds nothing else on that path; his BM1 pair on Internal 2 lies at y 7.68 / 8.03 from
X' 11.3 to 20.4, south of it. The line is static (it enables the ADIN2111's two supply switches)."""
import sys, math
import pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); FM = pcbnew.FromMM; mm = pcbnew.ToMM
T, B, I1, I2 = (b.GetLayerID(n) for n in ("Top Layer", "6 Bottom Layer", "Internal 1", "Internal 2")); assert min(T, B, I1, I2) >= 0
n = [x for name, x in b.GetNetsByName().items() if str(name).endswith("/ADIN_PWR") or str(name) == "ADIN_PWR"]; assert len(n) == 1; n = n[0]
def V(x, y): return pcbnew.VECTOR2I(FM(100 + x), FM(100 - y))
p = [q for q in b.FindFootprintByReference("J21").Pads() if q.GetNumber() == "11"][0]
assert abs(mm(p.GetPosition().x) - 104.14) < 0.01 and abs(100 - mm(p.GetPosition().y) - 6.67) < 0.01 and p.GetNet().GetNetCode() == n.GetNetCode()
seg = [t for t in b.GetTracks() if t.Type() != pcbnew.PCB_VIA_T and t.GetLayer() == I1 and t.GetNet().GetNetCode() == n.GetNetCode()
       and abs(100 - mm(t.GetStart().y) - 15.728) < 0.01 and abs(100 - mm(t.GetEnd().y) - 15.728) < 0.01]
assert len(seg) == 1 and min(mm(seg[0].GetStart().x), mm(seg[0].GetEnd().x)) - 100 < 20.7 and max(mm(seg[0].GetStart().x), mm(seg[0].GetEnd().x)) - 100 > 21.3, "Sofar's Internal 1 track at y 15.728 not found"
v = pcbnew.PCB_VIA(b); v.SetPosition(V(21.0, 15.728)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(T, B); v.SetWidth(pcbnew.F_Cu, FM(0.45)); v.SetDrill(FM(0.2)); v.SetNet(n); b.Add(v)
pts = [(21.0, 15.728), (15.772, 10.5), (7.97, 10.5), (4.14, 6.67)]; tot = 0
for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
    dx, dy = abs(x1 - x0), abs(y1 - y0); assert dx < 1e-6 or dy < 1e-6 or abs(dx - dy) < 1e-6
    t = pcbnew.PCB_TRACK(b); t.SetStart(V(x0, y0)); t.SetEnd(V(x1, y1)); t.SetWidth(FM(0.2)); t.SetLayer(I2); t.SetNet(n); b.Add(t); tot += math.hypot(x1 - x0, y1 - y0)
pcbnew.SaveBoard(sys.argv[1], b)
print("  ADIN_PWR: 1 via at (21.0, 15.728), %.1f mm of new track on Internal 2, 3 segments" % tot)
