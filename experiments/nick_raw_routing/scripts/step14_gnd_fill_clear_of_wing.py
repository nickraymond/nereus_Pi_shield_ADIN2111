"""Step 14: the north-west GND fill stays clear of Sofar's west ground wing (review finding R-S4; mocked on a
scratch copy first; Nick's comment on the proposal in the summary doc, 2026-11-11: "Proposal approved").

On the mote the ground under L2 (the west wing) is cut off from the main ground by a 0.38 mm slot in Sofar's GND
zone (x 131.31-131.69 from y 93.40 to 101.60, then east along y 101.81-102.20 to x 138.40, then south to about
y 113.6) and joins it only at the slot's south end. The zone "GND north-west fill" added for the 5 V converter,
J4 and J3 lay over the wing's north tip and across the slot's north end, so the wing was joined at the north too.

- The fill's outline is redrawn 0.5 mm or more outside the wing's edge and the slot. Sofar's zone is not
  edited; its copper refills the wing. The fill still joins the main ground north of the wing's tip
  (x 131.69-132.90, y 87.50-92.89) and the strip under the Pi header.
- No part, track or via changes. The zones are refilled by the DRC run that follows this script
  (kicad-cli pcb drc --refill-zones --save-board).
"""
import sys
import pcbnew
import boardio

F = pcbnew.FromMM
mm = pcbnew.ToMM
b = boardio.load()
zs = [z for z in b.Zones() if z.GetZoneName() == "GND north-west fill (5 V converter, J4, J3)"]
assert len(zs) == 1, len(zs)
z = zs[0]
o = z.Outline()
old = [(round(mm(o.CVertex(i).x), 2), round(mm(o.CVertex(i).y), 2)) for i in range(o.TotalVertices())]
# Sofar's wing edge runs (124.08, 104.26) - (125.01, 102.64) - arc - (125.11, 101.35) - (128.60, 97.85) - (128.60, 96.10) - (131.31, 93.40);
# the slot is x 131.31-131.69 south of that tip. Each new edge lies 0.5 mm or more outside it.
NEW = [(116.80, 87.50), (132.90, 87.50), (132.90, 92.89), (131.10, 92.89), (128.10, 95.89), (128.10, 97.65), (124.50, 101.25), (124.50, 102.45), (124.10, 103.20), (116.80, 103.20)]
if old == [(round(x, 2), round(y, 2)) for x, y in NEW]:
    sys.exit("step 14 already applied (the fill has the new outline); nothing done")
assert old == [(116.8, 87.5), (132.9, 87.5), (132.9, 96.0), (129.9, 96.0), (129.9, 98.4), (126.8, 101.4), (125.4, 103.2), (116.8, 103.2)], old
# the wing edge this outline was drawn against must still be in Sofar's zone
main = [z2 for z2 in b.Zones() if not z2.GetIsRuleArea() and z2.GetZoneName() == "" and z2.GetNetname().split("/")[-1] == "GND" and z2.IsOnLayer(b.GetLayerID("GND Plane"))]
assert len(main) == 1, len(main)
mo = main[0].Outline()
pts = {(round(mm(mo.CVertex(i).x), 2), round(mm(mo.CVertex(i).y), 2)) for i in range(mo.TotalVertices())}
assert {(125.11, 101.35), (128.6, 97.85), (128.6, 96.1), (131.31, 93.4), (131.69, 87.01)} <= pts, "Sofar's wing edge has moved"
o.RemoveAllContours()
o.NewOutline()
for x, y in NEW:
    o.Append(F(x), F(y))
z.UnFill()
z.SetNeedRefill(True)
boardio.save(b)
print("  north-west GND fill redrawn, %d -> %d outline points; refill follows with the DRC run" % (len(old), len(NEW)))
