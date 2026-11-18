"""Fixes after the independent sub-agent review of stages C part 2 and D part 1 (2026-11-18). Each finding was first
confirmed on the board in the routing session (scripts/review1/pourcheck.py; pad shapes and positions read with pcbnew).

KiCad's Python: stepR1_fixes.py <board .kicad_pcb (a copy outside git)>
Frame: X' = KiCad x - 100, y = 100 - KiCad y (mm).
1. Top GND pour, piece X' -0.30..6.52, y 33.41..42.17: stage C part 2's MOTOR_OUT1 trunk and test-point branches cut
   it off from every GND via, so R38 pad 2 (the 5 V feedback divider's ground) and R40 pad 1 (the UVLO divider's
   ground) were tied to ground through nothing. Two GND vias (0.45 / 0.20 mm) into that piece: (3.5, 38.17) beside
   R38 pad 2 with a short track, and (4.6, 38.87). Both sites keep 0.2 mm from all other-net copper on all layers
   (pourcheck.py --sites).
2. Top GND pour, piece X' 10.38..12.90, y 45.09..51.64 (R51 pad 2, the wiper filter's ground): no via either.
   One GND via at (11.45, 47.51) with a track from R51 pad 2.
3. ADIN_PWR, bottom: stage D part 1's track ended at (26.0, 11.9), 0.07 mm outside test pad TP8, which is round
   (1.5 mm, centre (25.457, 11.283)), not square. One more segment, 45 degrees, to (25.457, 11.357) inside the pad.
4. R26 pad 2 (N6_3V3, bottom, (29.0, 9.6)) was shut in by stage D part 1: the CS via 0.2 mm north, SDA at X' 28.3
   west, SCL at X' 29.6 east, R26 pad 1 south. SDA's bottom run moves 0.4 mm west to X' 27.9 (four of this session's
   own track segments are replaced; their uuids are written to <board>.removed for the lock check), and R27 pad 2 and
   R26 pad 2 are joined on the bottom at X' 28.4 between SDA and the resistors' pads. R27 pad 2 stays reachable from
   the south and east for stage F's N6_3V3 feed."""
import sys, math
import pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); FM = pcbnew.FromMM; mm = pcbnew.ToMM
T, B = b.GetLayerID("Top Layer"), b.GetLayerID("6 Bottom Layer"); assert min(T, B) >= 0
def net(suffix):
    c = [n for name, n in b.GetNetsByName().items() if str(name) == suffix or str(name).endswith("/" + suffix)]
    assert len(c) == 1 and c[0].GetNetCode() > 0, (suffix, len(c)); return c[0]
def V(x, y): return pcbnew.VECTOR2I(FM(100 + x), FM(100 - y))
count = {"track": 0, "via": 0}
def path(n, layer, w, pts):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        dx, dy = abs(x1 - x0), abs(y1 - y0); assert dx < 1e-6 or dy < 1e-6 or abs(dx - dy) < 1e-6, ("not straight or 45 deg", n, (x0, y0), (x1, y1))
        t = pcbnew.PCB_TRACK(b); t.SetStart(V(x0, y0)); t.SetEnd(V(x1, y1)); t.SetWidth(FM(w)); t.SetLayer(layer); t.SetNet(net(n)); b.Add(t); count["track"] += 1
def via(n, x, y, d=0.45, h=0.2):
    v = pcbnew.PCB_VIA(b); v.SetPosition(V(x, y)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(T, B)
    v.SetWidth(pcbnew.F_Cu, FM(d)); v.SetDrill(FM(h)); v.SetNet(net(n)); b.Add(v); count["via"] += 1
def pad(r, num): return [q for q in b.FindFootprintByReference(r).Pads() if q.GetNumber() == num][0]
def at(p, x, y): return abs(mm(p.GetPosition().x) - 100 - x) < 0.01 and abs(100 - mm(p.GetPosition().y) - y) < 0.01
assert at(pad("R38", "2"), 2.929, 38.4) and at(pad("R51", "2"), 10.705, 47.51) and at(pad("TP8", "1"), 25.457, 11.283)
assert at(pad("R26", "2"), 29.0, 9.6) and at(pad("R27", "2"), 29.0, 7.1) and at(pad("R27", "1"), 29.0, 6.3)
assert pad("TP8", "1").GetShape(pcbnew.F_Cu) == pcbnew.PAD_SHAPE_CIRCLE or pad("TP8", "1").GetShape(pcbnew.B_Cu) == pcbnew.PAD_SHAPE_CIRCLE
# 1
path("GND", T, 0.3, [(2.929, 38.4), (3.27, 38.4), (3.5, 38.17)]); via("GND", 3.5, 38.17); via("GND", 4.6, 38.87)
# 2
path("GND", T, 0.3, [(10.705, 47.51), (11.45, 47.51)]); via("GND", 11.45, 47.51)
# 3
path("ADIN_PWR", B, 0.2, [(26.0, 11.9), (25.457, 11.357)])
# 4
OLD = [((28.65, 13.315), (28.3, 12.965)), ((28.3, 12.965), (28.3, 6.7)), ((28.3, 6.7), (28.7, 6.3)), ((28.7, 6.3), (29.0, 6.3))]
sda = net("I2C0_SDA").GetNetCode(); gone = []
def key(p): return (round(mm(p.x) - 100, 3), round(100 - mm(p.y), 3))
for t in list(b.GetTracks()):
    if t.Type() != pcbnew.PCB_VIA_T and t.GetLayer() == B and t.GetNet().GetNetCode() == sda and (key(t.GetStart()), key(t.GetEnd())) in OLD:
        gone.append(t.m_Uuid.AsString()); b.Remove(t)
assert len(gone) == 4, ("this session's four SDA segments not found", len(gone))
open(sys.argv[1] + ".removed", "w").write(" ".join(gone))
path("I2C0_SDA", B, 0.2, [(28.65, 13.315), (27.9, 12.565), (27.9, 6.7), (28.3, 6.3), (29.0, 6.3)])
path("N6_3V3", B, 0.2, [(29.0, 7.1), (28.6, 7.1), (28.4, 7.3), (28.4, 9.4), (28.6, 9.6), (29.0, 9.6)])
pcbnew.SaveBoard(sys.argv[1], b)
print("removed 4 of this session's SDA segments; added %d track segments and %d vias" % (count["track"], count["via"]))
