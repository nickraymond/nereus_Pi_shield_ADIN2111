"""Step 18: top-side ground copper and two more ground vias at U10, as Sofar has at U5 (review finding R-S1; mocked
on a scratch copy first; Nick's comments on the summary doc, 2026-11-11: "I like the idea, show me a mock of how
this will look. What thermal vias, if any, should be added?", then on the mock: "approved").

Sofar's U5 (the 3.3 V converter U10 is a copy of) stands in a top-layer GND fill of 16 mm2 that runs under its body
and is tied down by ground vias around it. U10's GND pin 1 left on one 0.5 mm track to one via at (130.07, 89.13);
there was no top-side ground copper.

- New zone "GND top fill at U10" on the top layer: from the via at (130.07, 89.13) through pin 1, under U10's
  body, north through the gap between the SW via and the bootstrap via to the ground pads of the output
  capacitors C56, C57 and C58. Settings copied from Sofar's top GND fill at U5 (solid pad connection).
- Two new ground vias, 0.6 / 0.3 mm: (132.70, 90.10) under U10's body, 0.7 mm from pin 1, and (133.14, 87.75) in
  the neck between U10 and the capacitors. With the three vias already there, (130.07, 89.13), (132.23, 86.28)
  and (134.15, 86.28), pin 1 reaches the ground plane through five vias joined by the fill.
- No part or track moves. The zones are refilled by the DRC run that follows this script
  (kicad-cli pcb drc --refill-zones --save-board).
"""
import sys
import pcbnew
import boardio
from boardio import add_via, pad_xy, via_xy, mm

MM = pcbnew.FromMM
NAME = "GND top fill at U10"
VIAS = [(132.70, 90.10), (133.14, 87.75)]
OUTLINE = [(130.40, 85.65), (135.10, 85.65), (135.10, 86.95), (133.85, 86.95), (133.85, 91.60), (132.15, 91.60),
           (132.15, 89.50), (129.65, 89.50), (129.65, 88.60), (132.45, 88.60), (132.45, 86.95), (130.40, 86.95)]

b = boardio.load()
if any(z.GetZoneName() == NAME for z in b.Zones()):
    sys.exit("step 18 already applied (the top GND fill at U10 exists); nothing done")
tracks = list(b.GetTracks())
top = b.GetLayerID("Top Layer")

# what the outline and the vias were drawn against
for ref, num, xy in (("U10", "1", (131.52, 89.15)), ("U10", "2", (131.52, 90.10)), ("U10", "6", (134.28, 89.15)),
                     ("C56", "1", (131.20, 86.28)), ("C57", "1", (133.20, 86.28)), ("C58", "2", (134.70, 85.81)),
                     ("C53", "1", (132.64, 89.10)), ("R37", "2", (132.77, 91.10))):
    got = pad_xy(b, ref, num)
    assert abs(got[0] - xy[0]) < 0.02 and abs(got[1] - xy[1]) < 0.02, (ref, num, got)
for net, xy in (("GND", (130.07, 89.13)), ("GND", (132.23, 86.28)), ("GND", (134.15, 86.28)),
                ("5V_Buck_SW", (132.17, 88.23)), ("Net-(U10-CB)", (134.10, 88.56))):
    via_xy(tracks, net, xy)

# Sofar's top GND fill at U5: the pattern for the settings
like = [z for z in b.Zones() if not z.GetIsRuleArea() and z.IsOnLayer(top) and z.GetNetname().split("/")[-1] == "GND"
        and z.GetBoundingBox().Contains(pcbnew.VECTOR2I(MM(141.45), MM(113.68)))]
assert len(like) == 1, len(like)
like = like[0]

for x, y in VIAS:
    add_via(b, "GND", x, y)

z = pcbnew.ZONE(b)
z.SetZoneName(NAME)
z.SetNet(boardio.net_of(b, "GND"))
z.SetLayer(top)
z.SetAssignedPriority(0)
z.SetLocalClearance(like.GetLocalClearance())
z.SetMinThickness(like.GetMinThickness())
z.SetPadConnection(like.GetPadConnection())
z.SetThermalReliefGap(like.GetThermalReliefGap())
z.SetThermalReliefSpokeWidth(like.GetThermalReliefSpokeWidth())
z.SetIslandRemovalMode(like.GetIslandRemovalMode())
o = z.Outline()
o.NewOutline()
for x, y in OUTLINE:
    o.Append(MM(x), MM(y))
b.Add(z)

boardio.save(b)
print("  zone added on the top layer: %s, %d outline points (clearance %.2f mm, min width %.2f mm, pad connection %d, as Sofar's fill at U5)" % (
    NAME, len(OUTLINE), mm(like.GetLocalClearance() or 0), mm(like.GetMinThickness()), like.GetPadConnection()))
print("  2 GND vias added: %s; refill follows with the DRC run" % ", ".join("(%.2f, %.2f)" % v for v in VIAS))
