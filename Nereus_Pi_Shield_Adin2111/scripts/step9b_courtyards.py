"""Step 9b: the three courtyard overlaps at the 5 V converter (C55 / C54 / U10).

- C55 moves 0.50 mm west, C54 0.30 mm south. Both stay on the same VBUS and GND copper as before.
- C55's GND via would sit under the moved pad's corner, so it moves to (127.55, 91.60), west of the pad;
  C54's GND pad joins the same via.
"""
import sys
import pcbnew
import boardio
from boardio import add_track, add_via, pad_xy, move_to, move_vertex, mm

b = boardio.load()
fp = boardio.footprints(b)
tracks = list(b.GetTracks())
x55, y55 = boardio.pos(fp["C55"]); x54, y54 = boardio.pos(fp["C54"])
if abs(x55 - 129.10) < 0.01:
    sys.exit("step 9b already applied (C55 is at x 129.10); nothing done")
top = b.GetLayerID("Top Layer")
old1 = pad_xy(b, "C55", "1"); old54 = pad_xy(b, "C54", "1")

# GND copper of the two capacitors at the old place: 5 top segments and the via
dead = [t for t in tracks if t.GetNetname() == "GND" and (
        (t.Type() == pcbnew.PCB_VIA_T and abs(mm(t.GetPosition().x) - 128.835) < 0.02 and abs(mm(t.GetPosition().y) - 91.062) < 0.02)
        or (t.Type() != pcbnew.PCB_VIA_T and t.GetLayer() == top
            and all(128.7 < mm(p.x) < 129.0 and 90.9 < mm(p.y) < 92.9 for p in (t.GetStart(), t.GetEnd()))))]
assert len(dead) == 6, len(dead)

move_to(fp["C55"], x55 - 0.50, y55)
move_to(fp["C54"], x54, y54 + 0.30)
# VBUS: the track ends follow the pads
n1 = pad_xy(b, "C55", "1"); n54 = pad_xy(b, "C54", "1")
move_vertex(tracks, "VBUS", top, old1, n1, expect=1)
move_vertex(tracks, "VBUS", top, old54, n54, expect=1)
move_vertex(tracks, "VBUS", top, (130.846, 92.7837), (130.546, n54[1]), expect=2)
# GND: one via west of C55, both GND pads to it
g55 = pad_xy(b, "C55", "2"); g54 = pad_xy(b, "C54", "2")
v = (127.55, g55[1])
add_via(b, "GND", *v)
add_track(b, "GND", "Top Layer", [g55, v], 0.5)
add_track(b, "GND", "Top Layer", [g54, (128.00, g54[1]), (v[0], g54[1] - 0.45), v])
for t in dead:
    b.Remove(t)
boardio.save(b)
boardio.report(["C54", "C55"])
