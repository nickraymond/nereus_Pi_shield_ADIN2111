"""Step 19: the three vias at L6 land on a 5 V fill, as the mote's do at L3 (review finding M-S4; mocked on a
scratch copy first; Nick's comments on the summary doc, 2026-11-11: "Make them useful like the mote, so they help
with thermal", then on the mock: "Approved, but instead of [fingers] how [about] a polygon like Sofar did under
[the] large L1 L2 inductors?").

On the mote the converter's output vias at L3 drop into the 3V3 fill on the PWR Plane: one sits under the
inductor's body between its pads, 0.76 mm from pad 2, two stand at the pad's end. On this board the three 5V_PI
vias at L6 (127.90 / 128.46 / 128.99, 84.2) met 5V_PI copper on the top layer only, overlapped the top edge of
L6 pad 2 and stood 0.23 / 0.26 mm hole to hole. The PWR Plane under them is the PI_5V pour (the Pi's rail on the
far side of JP1), which they must not join.

- The three vias move under L6's body, between its pads: (124.60 / 126.40 / 128.20, 87.15), 0.6 / 0.3 mm,
  1.8 mm apart, 0.99 mm from pad 2's edge and 0.90 mm from pad 1's. One copper polygon on the top layer joins
  them to pad 2, drawn as Sofar's polygons at L1, L2 and L3 are (a net-tied shape with 0.25 mm chamfers):
  x 124.10..128.70, from inside the pad (y 85.00) to y 87.60, 0.75 mm from pad 1. The mock had three 0.6 mm
  necks in its place.
- New zone "5V_PI fill under L6 (converter output)" on the PWR Plane, x 123.55..131.00, y 86.75..95.00 with the
  south-east corner cut. The PWR Plane was empty there. Its outline stays 0.35 mm from the PI_5V pour's
  outline, 0.5 mm from Sofar's no-net zone NoConnect_Left and 0.69 mm from Sofar's 3V3 fill, so none of them
  changes shape; its priority (1) is below Sofar's zones (7).
- Nothing else moves. The zones are refilled by the DRC run that follows this script
  (kicad-cli pcb drc --refill-zones --save-board).
"""
import sys
import pcbnew
import boardio
from boardio import add_via, pad_xy, mm

MM = pcbnew.FromMM
NAME = "5V_PI fill under L6 (converter output)"
OLD = [(127.90, 84.23), (128.46, 84.25), (128.99, 84.23)]
NEW = [(124.60, 87.15), (126.40, 87.15), (128.20, 87.15)]
PATCH = [(124.10, 85.00), (128.70, 85.00), (128.70, 87.35), (128.45, 87.60), (124.35, 87.60), (124.10, 87.35)]
OUTLINE = [(123.55, 86.75), (131.00, 86.75), (131.00, 93.00), (129.00, 95.00), (123.55, 95.00)]

b = boardio.load()
zones = {z.GetZoneName(): z for z in b.Zones() if z.GetZoneName()}
if NAME in zones:
    sys.exit("step 17 already applied (the 5V_PI fill exists); nothing done")
tracks = list(b.GetTracks())
pwr = b.GetLayerID("PWR Plane")
assert pwr >= 0

# what the positions were drawn against
p2 = pad_xy(b, "L6", "2")
p1 = pad_xy(b, "L6", "1")
assert abs(p2[0] - 126.40) < 0.01 and abs(p2[1] - 85.08) < 0.01 and abs(p1[1] - 89.13) < 0.01, (p1, p2)
pour = zones["PI_5V north pour"]
po = pour.Outline()
pts = [(round(mm(po.CVertex(i).x), 2), round(mm(po.CVertex(i).y), 2)) for i in range(po.TotalVertices())]
assert (144.6, 86.4) in pts and (123.2, 86.4) in pts and (123.2, 88.1) in pts, pts
left = zones["NoConnect_Left"]
lo = left.Outline()
lpts = {(round(mm(lo.CVertex(i).x), 2), round(mm(lo.CVertex(i).y), 2)) for i in range(lo.TotalVertices())}
assert {(131.31, 93.4), (128.6, 96.1)} <= lpts, "NoConnect_Left has moved"
assert left.GetAssignedPriority() > 1
# nothing else may sit on the PWR Plane inside the new outline
box = pcbnew.BOX2I(pcbnew.VECTOR2I(MM(123.55), MM(86.75)), pcbnew.VECTOR2I(MM(7.45), MM(8.25)))
for z in b.Zones():
    if z.GetIsRuleArea() or not z.IsOnLayer(pwr) or not z.HasFilledPolysForLayer(pwr):
        continue
    polys = z.GetFilledPolysList(pwr)
    for i in range(polys.OutlineCount()):
        assert not polys.Outline(i).BBox().Intersects(box) or z.GetZoneName() in ("PI_5V north pour", "NoConnect_Left"), z.GetZoneName()

old = []
for near in OLD:
    hits = [t for t in tracks if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname().split("/")[-1] == "5V_PI"
            and abs(mm(t.GetPosition().x) - near[0]) < 0.02 and abs(mm(t.GetPosition().y) - near[1]) < 0.02]
    assert len(hits) == 1, (near, len(hits))
    old.append(hits[0])

# ---- new vias and the copper polygon that joins them to pad 2, with the settings of Sofar's polygon at L3
like = [d for d in b.GetDrawings() if d.GetClass() == "PCB_SHAPE" and d.GetLayer() == pcbnew.F_Cu and d.GetShape() == pcbnew.SHAPE_T_POLY
        and d.GetNetname().split("/")[-1] == "3V3"]
assert len(like) == 1, len(like)
like = like[0]
for x, y in NEW:
    add_via(b, "5V_PI", x, y)
patch = pcbnew.PCB_SHAPE(b, pcbnew.SHAPE_T_POLY)
patch.SetLayer(pcbnew.F_Cu)
patch.SetPolyPoints([pcbnew.VECTOR2I(MM(x), MM(y)) for x, y in PATCH])
patch.SetWidth(like.GetWidth())
patch.SetFillMode(like.GetFillMode())
patch.SetNet(boardio.net_of(b, "5V_PI"))
b.Add(patch)

# ---- the fill
z = pcbnew.ZONE(b)
z.SetZoneName(NAME)
z.SetNet(boardio.net_of(b, "5V_PI"))
z.SetLayer(pwr)
z.SetAssignedPriority(1)
z.SetLocalClearance(pour.GetLocalClearance())
z.SetMinThickness(pour.GetMinThickness())
z.SetPadConnection(pour.GetPadConnection())
z.SetThermalReliefGap(pour.GetThermalReliefGap())
z.SetThermalReliefSpokeWidth(pour.GetThermalReliefSpokeWidth())
z.SetIslandRemovalMode(pour.GetIslandRemovalMode())
o = z.Outline()
o.NewOutline()
for x, y in OUTLINE:
    o.Append(MM(x), MM(y))
b.Add(z)

# ---- old vias out (collected above; removal last)
for v in old:
    b.Remove(v)

boardio.save(b)
print("  3 vias moved from y 84.2 to (124.60 / 126.40 / 128.20, 87.15); top-layer 5V_PI polygon added, %d points" % len(PATCH))
print("  zone added on the PWR Plane: %s, %d outline points; refill follows with the DRC run" % (NAME, len(OUTLINE)))
