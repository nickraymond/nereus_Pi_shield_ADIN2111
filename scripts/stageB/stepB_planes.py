"""Routing stage B: our planes and pours round Sofar's block. None of Sofar's zones, rule areas or copper is touched.

KiCad's Python: stepB_planes.py <board .kicad_pcb (a copy outside git)>
Frame: X' = KiCad x - 100, y = 100 - KiCad y (mm).

What Sofar's planes are on this board (read 2026-11-18 with zones.py and the plots of the stage A board): his GND-plane
zone is the old mote outline (X' 5.02..41.0, y -0.14..49.8, so it already covers the east strip from y 7.05 to 41.64),
with two slots that are notches open to the mote's old east edge (mouths at y 6.67..7.05 from X' 33.64, and at
y 41.64..42.02 from X' 34.61). His five power regions and two "NoConnect" islands tile the same outline on the PWR
plane. His 152 rule areas on the two planes forbid nothing (every keep-out flag is off), so they need no change.

Added here, all outside the mote outline M (= his GND-plane outline with the two slots closed):
  N6 GND plane     GND Plane   board minus M, grown 0.5 mm into M so that it joins his zone. The two slot mouths are
                               carried on to the board edge (his two ground halves are NOT bridged at the east edge:
                               the slot topology stays as on the mote until Sofar says what the slots are for).
  N6 5V            PWR Plane   west wing, X' -6.3..-2.2 from y 3.3 to 45.6 with a tongue to the VIN pin (1.56, 4.13).
                               Connected today only at the VIN pin; vias at L6 / C56..C58 and at U12's capacitors
                               are stage C.
  N6 GND PWR layer PWR Plane   the rest of board minus M (under the 5 V switch node too), less the bus corridors.
  N6 GND In1       Internal 1  board minus M, less the bus corridors.
  N6 GND top       Top Layer   board minus M, less the bus corridors.
  N6 GND bottom    Bottom      board minus M.
Pieces under 10 mm2 are dropped (the pocket shut in between the two BM2 tracks under J9). No pour inside a
fiducial's solder-mask opening.
Bus corridor = the top-layer tracks and connector pads of BM1_P/N and BM2_P/N grown by 1.0 mm: no pour of ours on the
top layer, Internal 1 or the PWR plane beside or under the bus outside the mote outline (the GND plane, 0.76 mm
below, stays solid there).
Zone settings: clearance 0.3, minimum width 0.25, solid connection to surface-mount pads, thermal spokes 0.5 with
0.3 gap at through-hole pads (the header pins are hand-soldered), islands removed (so a piece with
no GND pad or via in it does not fill: such pieces appear when later stages add their GND vias).
Also: the pads of J21 / J22 lose their copper on inner layers where nothing connects (KiCad's "remove unused
layers", top and bottom kept), so the planes can pass between the header pins."""
import sys
import pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); mm = pcbnew.ToMM; FM = pcbnew.FromMM
L = {n: b.GetLayerID(n) for n in ("Top Layer", "Internal 1", "GND Plane", "Internal 2", "PWR Plane", "6 Bottom Layer")}
assert all(v >= 0 for v in L.values()), L
ERR = FM(0.005)
def V(x, y): return pcbnew.VECTOR2I(FM(100 + x), FM(100 - y))
def rect(x0, x1, y0, y1):
    s = pcbnew.SHAPE_POLY_SET(); s.NewOutline()
    for p in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)): s.Append(V(*p))
    return s
def poly(pts):
    s = pcbnew.SHAPE_POLY_SET(); s.NewOutline()
    for p in pts: s.Append(V(*p))
    return s
def copy(s): return pcbnew.SHAPE_POLY_SET(s)
def grow(s, d):
    t = copy(s)
    if d >= 0: t.Inflate(FM(d), pcbnew.CORNER_STRATEGY_CHAMFER_ALL_CORNERS, ERR)
    else: t.Deflate(FM(-d), pcbnew.CORNER_STRATEGY_CHAMFER_ALL_CORNERS, ERR)
    return t
def sub(a, c): t = copy(a); t.BooleanSubtract(c); return t
def add(a, c): t = copy(a); t.BooleanAdd(c); return t
def isect(a, c): t = copy(a); t.BooleanIntersection(c); return t
def area(s): return s.Area() / 1e12
# the board outline and the mote outline
board = pcbnew.SHAPE_POLY_SET(); assert b.GetBoardPolygonOutlines(board, False)
his = [z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == "GND" and z.IsOnLayer(L["GND Plane"])]
assert len(his) == 1 and his[0].Outline().TotalVertices() == 225, "Sofar's GND-plane zone not found as expected"
M = grow(grow(copy(his[0].Outline()), 0.3), -0.3)          # closing: the two 0.38 mm slots are filled
print("board %.1f mm2; mote outline (slots closed) %.1f mm2, of which on the board %.1f mm2" % (area(board), area(M), area(isect(M, board))))
for z in b.Zones():
    if not z.GetIsRuleArea() and z.IsOnLayer(L["PWR Plane"]):
        o = sub(copy(z.Outline()), grow(M, 0.05)); assert area(o) < 0.01, ("a PWR-plane zone of Sofar's leaves the mote outline by more than 0.05 mm", z.GetNetname(), area(o))
outside = sub(board, M)
outside = grow(grow(outside, -0.25), 0.25)                 # opening: drops the slot mouths and other slivers under 0.5 mm
# slot mouths carried to the board edge (measured on his outline: south y 6.67..7.05 from X' 33.64; north y 41.64..42.02 from X' 34.61)
mouths = add(rect(33.0, 37.0, 6.67, 7.05), rect(34.0, 37.0, 41.64, 42.02))
# bus corridor
bus = pcbnew.SHAPE_POLY_SET()
for t in b.GetTracks():
    if t.Type() != pcbnew.PCB_VIA_T and t.GetLayer() == L["Top Layer"] and "/BM" in t.GetNetname():
        t.TransformShapeToPolygon(bus, L["Top Layer"], FM(1.0), ERR, pcbnew.ERROR_OUTSIDE)
for r in ("J9", "J10"):
    for p in b.FindFootprintByReference(r).Pads():
        if "/BM" in p.GetNetname(): p.TransformShapeToPolygon(bus, L["Top Layer"], FM(1.0), ERR, pcbnew.ERROR_OUTSIDE)
bus.Simplify()
print("bus corridor outside the mote outline: %.1f mm2" % area(isect(bus, outside)))
gnd_plane = sub(isect(grow(outside, 0.5), board), mouths)
five = isect(add(rect(-6.3, -2.2, 3.3, 45.6), rect(-2.3, 2.5, 3.3, 5.3)), outside)
quiet = sub(outside, bus)
# fiducials: no pour inside the solder-mask opening (1.0 mm pad + 0.5 mm margin), plus 0.3 mm
fid = {"Top Layer": pcbnew.SHAPE_POLY_SET(), "6 Bottom Layer": pcbnew.SHAPE_POLY_SET()}
for f in b.GetFootprints():
    if f.GetReference().startswith("FID"):
        for p in f.Pads():
            l = f.GetLayer()
            p.TransformShapeToPolygon(fid[b.GetLayerName(l)], l, p.GetSolderMaskExpansion(l) + FM(0.3), ERR, pcbnew.ERROR_OUTSIDE)
GND = b.FindNet("GND"); V5 = b.FindNet("/Top-Level Schematic/5V_PI"); assert GND and V5 and GND.GetNetCode() > 0 and V5.GetNetCode() > 0
made = []
def zone(name, layer, net, shape, prio):
    s = copy(shape); s.Simplify(); n = 0
    for i in range(s.OutlineCount()):
        one = pcbnew.SHAPE_POLY_SET(); one.AddOutline(s.Outline(i))
        for h in range(s.HoleCount(i)): one.AddHole(s.Hole(i, h))
        if area(one) < 10.0: print("   (a piece of %.3f mm2 of '%s' dropped)" % (area(one), name)); continue
        z = pcbnew.ZONE(b); z.SetLayer(L[layer]); z.SetNet(net); z.SetZoneName(name); z.SetAssignedPriority(prio)
        z.Outline().Append(one)
        z.SetLocalClearance(FM(0.3)); z.SetMinThickness(FM(0.25)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_THT_THERMAL)
        z.SetThermalReliefGap(FM(0.3)); z.SetThermalReliefSpokeWidth(FM(0.5)); z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        z.SetIsRuleArea(False); z.SetFillMode(pcbnew.ZONE_FILL_MODE_POLYGONS)
        b.Add(z); made.append(z); n += 1
        q = z.GetBoundingBox()
        print("   %-17s %-14s %-6s prio %d  %6.1f mm2  %3d vertices  %d holes  X' %.2f..%.2f y %.2f..%.2f" % (name, layer, net.GetNetname().split("/")[-1], prio, area(one), one.TotalVertices(), one.HoleCount(0),
              mm(q.GetLeft()) - 100, mm(q.GetRight()) - 100, 100 - mm(q.GetBottom()), 100 - mm(q.GetTop())))
    return n
print("zones added:")
zone("N6 GND plane", "GND Plane", GND, gnd_plane, 1)       # his zone has priority 0; KiCad wants overlapping zones to differ
zone("N6 5V", "PWR Plane", V5, five, 2)
zone("N6 GND PWR layer", "PWR Plane", GND, sub(quiet, grow(five, 0.0)), 1)
zone("N6 GND In1", "Internal 1", GND, quiet, 0)
zone("N6 GND top", "Top Layer", GND, sub(quiet, fid["Top Layer"]), 0)
zone("N6 GND bottom", "6 Bottom Layer", GND, sub(outside, fid["6 Bottom Layer"]), 0)
n = 0
for r in ("J21", "J22"):
    for p in b.FindFootprintByReference(r).Pads():
        if p.HasHole(): p.SetRemoveUnconnected(True); p.SetKeepTopBottom(True); n += 1
print("J21 / J22: %d through-hole pads set to drop unconnected inner-layer copper (top and bottom kept)" % n)
pcbnew.SaveBoard(sys.argv[1], b)
print("added %d zones" % len(made))
