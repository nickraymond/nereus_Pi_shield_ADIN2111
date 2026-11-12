"""Step 23: the logo turns with the board name; the bottom-side notes move to the edge and both note blocks get a
box (Nick, this session's chat, 2026-11-11, with a picture of the first trial of step 21: "This is the way the logo
should look please"; "move the 'Threaded insert...' silk screen block farther [east] on the bottom so that it's
closer to the [edge] and leaves space from the J1 [and] C53 silk screen? Also draw a box around the note blocks so
they stand out more. You can move the 'Bus 24V' farther south as needed").

- Top: name and logo now stand as one group turned by 180 degrees about (176.85, 109.86), the centre of what
  the group covered before step 21: the name reads from the north down and the logo follows it at the south
  end, turned with it. Step 21 had turned the name alone and left the logo upright at the north end. The two
  texts move by (+0.06, -4.96); the logo's two polygons turn about the group centre.
- Bottom, notes behind JP1 ("THREADED INSERTS M3" ... "WHILE JP1 FEEDS IT"): 2.40 mm towards the west edge
  (the right-hand edge in the bottom view) and 0.35 mm south, in a box x 116.95..131.45, y 82.60..89.32,
  0.70 mm from the board edge. The fiducial that stood there left in step 22. J1's and C53's designators now
  stand 1.9 mm and 1.4 mm from the box (their boxes overlapped the notes' before).
- Bottom, ratings under J2 ("BUS 24V (16-32V)" ... "JP1 5V TO PI/AUX"): 0.80 mm south, in a box
  x 154.20..178.20, y 95.80..101.25, clear of R26's designator above it.
- Box lines 0.2 mm, as the AUX OUT and VBUS OUT boxes. Silkscreen only.
"""
import sys
import pcbnew
import boardio

FACE = "Menlo"
MM = pcbnew.FromMM
mm = pcbnew.ToMM
CENTRE = (176.85, 109.86)
NOTES = ["THREADED INSERTS M3", "MOUNTING HOLES M2.5", "NO USB POWER ON THE PI", "WHILE JP1 FEEDS IT"]
RATINGS = ["BUS  24V (16-32V)", "PORT 0.89A 20W", "5V OUT  1A CONT", "VBUS OUT 0.73A", "VBUS ON=GPIO26 HI", "JP1 5V TO PI/AUX"]
BOXES = [((116.95, 82.60), (131.45, 89.32)), ((154.20, 95.80), (178.20, 101.25))]

b = boardio.load()
TOP, BOT = b.GetLayerID("Top Overlay"), b.GetLayerID("Bottom Overlay")
draw = list(b.GetDrawings())
at = lambda d: (round(mm(d.GetPosition().x), 2), round(mm(d.GetPosition().y), 2))
texts = lambda layer, names: {d.GetText(): d for d in draw if d.GetClass() == "PCB_TEXT" and d.GetLayer() == layer and d.GetText() in names}

name = texts(TOP, ["Pi Shield", "ADIN2111 Rev0"])
notes, ratings = texts(BOT, NOTES), texts(BOT, RATINGS)
assert len(name) == 2 and len(notes) == 4 and len(ratings) == 6, (len(name), len(notes), len(ratings))
if at(name["Pi Shield"]) == (177.61, 107.42):
    sys.exit("step 23 already applied (the name stands where the group rotation puts it); nothing done")
assert at(name["Pi Shield"]) == (177.55, 112.38) and round(name["Pi Shield"].GetTextAngleDegrees()) % 360 == 270, at(name["Pi Shield"])
logo = [d for d in draw if d.GetLayer() == TOP and d.GetClass() == "PCB_SHAPE" and d.GetShape() == pcbnew.SHAPE_T_POLY
        and 174.9 < mm(d.GetBoundingBox().GetX()) and mm(d.GetBoundingBox().GetRight()) < 179.6
        and 99.1 < mm(d.GetBoundingBox().GetY()) and mm(d.GetBoundingBox().GetBottom()) < 103.1]
assert len(logo) == 2, len(logo)
assert all(at(d)[0] == 126.6 for d in notes.values()), [at(d) for d in notes.values()]
assert at(ratings["BUS  24V (16-32V)"])[1] == 96.2 and at(ratings["JP1 5V TO PI/AUX"])[1] == 99.4, [at(d) for d in ratings.values()]
faces = open(boardio.BOARD).read().count('(face "%s")' % FACE)

for d in name.values():
    d.Move(pcbnew.VECTOR2I(MM(0.06), MM(-4.96)))
c = pcbnew.VECTOR2I(MM(CENTRE[0]), MM(CENTRE[1]))
for d in logo:
    d.Rotate(c, pcbnew.EDA_ANGLE(180, pcbnew.DEGREES_T))
for d in notes.values():
    d.Move(pcbnew.VECTOR2I(MM(-2.40), MM(0.35)))
for d in ratings.values():
    d.Move(pcbnew.VECTOR2I(0, MM(0.80)))
for (x0, y0), (x1, y1) in BOXES:
    r = pcbnew.PCB_SHAPE(b, pcbnew.SHAPE_T_RECT)
    r.SetLayer(BOT)
    r.SetStart(pcbnew.VECTOR2I(MM(x0), MM(y0)))
    r.SetEnd(pcbnew.VECTOR2I(MM(x1), MM(y1)))
    r.SetWidth(MM(0.2))
    b.Add(r)

boardio.save(b)
kept = open(boardio.BOARD).read().count('(face "%s")' % FACE)
assert kept == faces, (faces, kept)
print("  top: name moved (+0.06, -4.96), logo turned 180 degrees about (%.2f, %.2f); 'Pi Shield' at %s" % (CENTRE[0], CENTRE[1], at(name["Pi Shield"])))
print("  bottom: notes (-2.40, +0.35), ratings (0, +0.80), 2 boxes added")
