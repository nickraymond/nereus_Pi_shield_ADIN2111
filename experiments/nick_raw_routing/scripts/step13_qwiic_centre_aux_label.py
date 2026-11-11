"""NOT YET APPLIED TO THE BOARD: a mock run on a scratch copy on 2026-11-11, waiting for Nick's go (TRACKER).

Step 13: Qwiic connector J3 on the board's east-west centre line; J4 "AUX OUT" labelled like J5 "VBUS OUT"
(Nick, 2026-11-11: "is there a way to place it along the center line of the board?", "move the connector
southward so there is more room for the silk screen of the AUX OUT", "the silkscreen of the AUX Out to match
the VBUS Out where the functional name is above the pads").

- J4 (5 V AUX OUT wire pads) moves 2.15 mm south to (119.00, 94.25): F1 sits right above J4, so the name row
  needs the pads to move. Its feed from F1 grows by 2.15 mm. Box and texts as J5's: name above the pads,
  "+5V" / J4 / "GND" beside them, box x 116.60-124.55, y 90.40-99.85, on both sides.
- VBUS_OUT's bottom track turned south at (120.30, 99.60), under J4's new GND pad; it now turns at
  (122.30, 99.60) and runs 45 degrees to (120.30, 101.60).
- J3 moves 2.50 mm south to the centre line y 104.10 and 0.70 mm west (mounting pads 0.63 mm from the board
  edge, J4's pads are at 0.60): the west shift keeps its pads 1.21 mm from the BM2_N trace (0.71 mm without).
  The 3V3, SDA and SCL vias, the pull-ups R10 / R24 and the inner-layer feeds stay; only the top tracks from
  the pads to the vias are re-laid. GND gets a new via beside pin 1 at (122.80, 101.40); the old one at
  (124.30, 98.40), now under J4's box line, goes. "I2C3" / J3 stay under the connector.
"""
import sys
import pcbnew
import boardio
from boardio import add_track, add_via, mm, place

F = pcbnew.FromMM
V = lambda x, y: pcbnew.VECTOR2I(F(x), F(y))
FACE = "Menlo"
b = boardio.load()
fp = boardio.footprints(b)
tracks = list(b.GetTracks())
sn = lambda t: t.GetNetname().split("/")[-1]
SILK = (pcbnew.F_SilkS, pcbnew.B_SilkS)
near = lambda p, q: abs(p[0] - q[0]) < 0.02 and abs(p[1] - q[1]) < 0.02
if near(boardio.pos(fp["J3"]), (119.70, 104.10)):
    sys.exit("step 13 already applied (J3 is on the centre line); nothing done")
assert near(boardio.pos(fp["J4"]), (119.00, 92.10)) and near(boardio.pos(fp["J3"]), (120.40, 101.60)), (boardio.pos(fp["J4"]), boardio.pos(fp["J3"]))
faces = open(boardio.BOARD).read().count('(face "%s")' % FACE)


def seg(t, net, layer, a, c):
    if t.Type() == pcbnew.PCB_VIA_T or sn(t) != net or b.GetLayerName(t.GetLayer()) != layer:
        return False
    e = [(mm(t.GetStart().x), mm(t.GetStart().y)), (mm(t.GetEnd().x), mm(t.GetEnd().y))]
    return (near(e[0], a) and near(e[1], c)) or (near(e[0], c) and near(e[1], a))


OLD = [("Net-(J4-Pin_1)", "Top Layer", (120.20, 91.40), (120.20, 92.10)),
       ("VBUS_OUT", "6 Bottom Layer", (125.60, 99.60), (120.30, 99.60)), ("VBUS_OUT", "6 Bottom Layer", (120.30, 99.60), (120.30, 119.90)),
       ("GND", "Top Layer", (122.40, 100.10), (123.40, 100.10)), ("GND", "Top Layer", (123.40, 100.10), (123.40, 99.30)), ("GND", "Top Layer", (123.40, 99.30), (124.30, 98.40)),
       ("PI_3V3", "Top Layer", (123.90, 101.10), (122.40, 101.10)),
       ("I2C3_SDA", "Top Layer", (122.40, 102.10), (125.90, 102.10)), ("I2C3_SCL", "Top Layer", (122.40, 103.10), (124.70, 103.10))]
dead = [t for t in tracks if any(seg(t, *o) for o in OLD)]
assert len(dead) == len(OLD), (len(dead), len(OLD))
n_old = len(dead)

# ---- J4 2.15 mm south, its feed, VBUS_OUT's bottom track around its GND pad
ref4 = fp["J4"].Reference()
place(fp["J4"], 119.00, 94.25, {"1": (119.00, 94.25), "2": (119.00, 98.06)})
L = add_track(b, "Net-(J4-Pin_1)", "Top Layer", [(120.20, 91.40), (120.20, 94.25)], 1.0)
L += add_track(b, "VBUS_OUT", "6 Bottom Layer", [(125.60, 99.60), (122.30, 99.60), (120.30, 101.60), (120.30, 119.90)], 1.0)

# ---- J3 to the centre line, 0.70 mm west; top tracks from its pads to the vias that stay
ref3 = fp["J3"].Reference()
place(fp["J3"], 119.70, 104.10, {"1": (121.70, 102.60), "2": (121.70, 103.60), "3": (121.70, 104.60), "4": (121.70, 105.60)})
L += add_track(b, "GND", "Top Layer", [(121.70, 102.60), (122.50, 102.60), (122.80, 102.30), (122.80, 101.40)], 0.3)
add_via(b, "GND", 122.80, 101.40)          # into the north-west GND fill (its south edge is y 103.20)
old_via = [t for t in tracks if t.Type() == pcbnew.PCB_VIA_T and sn(t) == "GND" and near((mm(t.GetPosition().x), mm(t.GetPosition().y)), (124.30, 98.40))]
assert len(old_via) == 1, len(old_via)     # J3's old GND via: only the removed stub ended on it
dead += old_via
L += add_track(b, "PI_3V3", "Top Layer", [(121.70, 103.60), (122.70, 103.60), (123.45, 102.85), (123.45, 101.55), (123.90, 101.10)], 0.25)
L += add_track(b, "I2C3_SDA", "Top Layer", [(121.70, 104.60), (122.70, 104.60), (123.95, 103.35), (123.95, 102.45), (124.30, 102.10), (125.90, 102.10)])
L += add_track(b, "I2C3_SCL", "Top Layer", [(121.70, 105.60), (122.90, 105.60), (124.70, 103.80), (124.70, 103.10)])

# ---- silkscreen, both sides: J4's box and texts as J5's; I2C3 / J3 under the connector
BOX = {(116.60, 90.40): (116.60, 90.40), (127.60, 90.40): (124.55, 90.40), (127.60, 97.55): (124.55, 99.85), (116.60, 97.55): (116.60, 99.85)}
key = lambda p: next((k for k in BOX if near((mm(p.x), mm(p.y)), k)), None)
moved = {"line": 0, "text": 0}
for d in b.GetDrawings():
    if d.GetLayer() not in SILK:
        continue
    if d.GetClass() == "PCB_SHAPE" and key(d.GetStart()) and key(d.GetEnd()):
        a, c = BOX[key(d.GetStart())], BOX[key(d.GetEnd())]
        d.SetStart(V(*a)); d.SetEnd(V(*c)); moved["line"] += 1
    elif d.GetClass() == "PCB_TEXT":
        at = (mm(d.GetPosition().x), mm(d.GetPosition().y))
        new = {("+5V", (123.00, 92.10)): (122.85, 94.25), ("GND", (123.00, 95.91)): (122.85, 98.06), ("AUX OUT", (124.45, 94.00)): (120.50, 91.60),
               ("I2C3", (120.40, 106.65)): (119.70, 109.15)}
        hit = [v for (s, p), v in new.items() if d.GetText() == s and near(at, p)]
        if hit:
            d.SetPosition(V(*hit[0])); moved["text"] += 1
            if d.GetText() == "AUX OUT":
                d.SetTextSize(V(1.0, 1.5))      # VBUS OUT's size
assert moved == {"line": 6, "text": 7}, moved      # 3 lines a side; +5V, GND, AUX OUT on both sides, I2C3 on top
ref4.SetPosition(V(122.85, 96.15))
ref3.SetPosition(V(119.70, 110.70))
fp["R10"].Reference().SetPosition(V(126.90, 101.72))    # bottom side: off J4's box line

for d in dead:
    b.Remove(d)
boardio.save(b)
kept = open(boardio.BOARD).read().count('(face "%s")' % FACE)
assert kept == faces, (faces, kept)
print("  J4 at %s, J3 at %s; %d segments and 1 via removed, %.2f mm and 1 via added; %d box lines and %d texts moved; %d texts in %s Bold" % (
    boardio.pos(fp["J4"]), boardio.pos(fp["J3"]), n_old, L, moved["line"], moved["text"], kept, FACE))
boardio.report(["J3", "J4"])
