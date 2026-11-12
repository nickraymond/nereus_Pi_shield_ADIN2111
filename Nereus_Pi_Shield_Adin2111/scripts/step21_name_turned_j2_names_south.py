"""Step 21: the board name in the east strip is turned by 180 degrees; J2's north-row pin names move off J1's pads
(Nick, this session's chat, 2026-11-11: "the large BM shield silkscreen at the far right should be rotated 180 deg,
and move the silk screen for [the] dev header south a bit since it's real close to the J1 header. Make those
changes with the next round please").

- "Pi Shield" / "ADIN2111 Rev0" (top side, beside L1) turn by 180 degrees about the centre of what the two
  texts cover, (176.82, 112.34): the name now reads from the north down, starting under the Bristlemouth logo,
  and covers the same area as before (x 174.21..179.43, y 104.19..120.48). The logo keeps its place and stays
  upright: turned with the texts (tried on a scratch copy) it stood on its head at the south end.
- J2's twelve north-row pin names on the top side (ALR ... MO) move 0.30 mm south, to y 82.80. Their letters
  stood 0.16 mm from J1's pads and 0.73 mm from J2's outline; now 0.46 mm and 0.43 mm. The bottom-side names
  already stand between J1's outline (0.52 mm) and J2's pads (0.42 mm) and stay.
- Silkscreen only.
"""
import sys
import pcbnew
import boardio

FACE = "Menlo"
MM = pcbnew.FromMM
mm = pcbnew.ToMM
CENTRE = (176.82, 112.34)
NAMES = ["ALR", "GND", "CE1", "SC3", "GND", "GND", "GND", "SC0", "GND", "IN2", "GND", "MO"]

b = boardio.load()
TOP = b.GetLayerID("Top Overlay")
draw = [d for d in b.GetDrawings() if d.GetLayer() == TOP]
at = lambda d: (round(mm(d.GetPosition().x), 2), round(mm(d.GetPosition().y), 2))

name = {d.GetText(): d for d in draw if d.GetClass() == "PCB_TEXT" and d.GetText() in ("Pi Shield", "ADIN2111 Rev0")}
assert sorted(name) == ["ADIN2111 Rev0", "Pi Shield"], sorted(name)
if round(name["Pi Shield"].GetTextAngleDegrees()) % 360 == 270:
    sys.exit("step 21 already applied (the board name reads from the north down); nothing done")
assert at(name["Pi Shield"]) == (176.09, 112.3) and at(name["ADIN2111 Rev0"]) == (178.73, 112.3), (at(name["Pi Shield"]), at(name["ADIN2111 Rev0"]))
assert all(round(d.GetTextAngleDegrees()) == 90 for d in name.values())
logo = [d for d in draw if d.GetClass() == "PCB_SHAPE" and d.GetShape() == pcbnew.SHAPE_T_POLY
        and 174.9 < mm(d.GetBoundingBox().GetX()) and mm(d.GetBoundingBox().GetRight()) < 179.6
        and 99.1 < mm(d.GetBoundingBox().GetY()) and mm(d.GetBoundingBox().GetBottom()) < 103.1]
assert len(logo) == 2, len(logo)
row = sorted([d for d in draw if d.GetClass() == "PCB_TEXT" and at(d)[1] == 82.5 and 149 < at(d)[0] < 179.5], key=lambda d: at(d)[0])
assert [d.GetText() for d in row] == NAMES, [d.GetText() for d in row]
faces = open(boardio.BOARD).read().count('(face "%s")' % FACE)

c = pcbnew.VECTOR2I(MM(CENTRE[0]), MM(CENTRE[1]))
for d in name.values():
    d.Rotate(c, pcbnew.EDA_ANGLE(180, pcbnew.DEGREES_T))
for d in row:
    d.SetPosition(pcbnew.VECTOR2I(d.GetPosition().x, MM(82.80)))

boardio.save(b)
kept = open(boardio.BOARD).read().count('(face "%s")' % FACE)
assert kept == faces, (faces, kept)
print("  board name turned 180 degrees about (%.2f, %.2f); 'Pi Shield' now at %s, angle %d" % (
    CENTRE[0], CENTRE[1], at(name["Pi Shield"]), round(name["Pi Shield"].GetTextAngleDegrees())))
print("  J2 north-row names on the top side: y 82.50 -> 82.80 (%d texts)" % len(row))
