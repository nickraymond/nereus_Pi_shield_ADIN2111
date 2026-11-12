"""Step 9e: JP3 (SPI_CFG1 strap) moves from south of U1 to the open north-east corner, in one row with JP4
(Nick, 2026-11-10: both straps near each other and easy to reach). R2 and R47 stay at U1.

- JP3 at (168.60, 96.40), turned 180 degrees: GND pad west, ADIN_VDDIO pad east, the same order as JP4
  ("0" west, "1" east).
- CFG1_STRAP (the jumper side of R2): top from R2 to a via at (153.40, 121.40), then Internal 1 east along
  y 122.40, north along x 177.00 (over ADIN_TIMER's bottom track, 1.7 mm from the BM1_P trunk) and west
  along y 98.20 to a via under JP3 pad 2. About 56 mm; the net is a DC level behind R2 (4.7 k).
- ADIN_VDDIO: bottom from the via at JP4 (155.90, 94.90) east along y 97.06, between the ADIN_PWR via and
  the PAYLOAD_EN lane, to a via beside JP3 pad 1.
- GND: top track south to a via at (167.90, 99.80). Sofar's GND plane follows the mote's outline and has no
  copper in most of this corner; the via sits where the fill map shows plane.
- The GND tracks at JP3's old pad 3 stay: they carry D8's cathode to the via at (156.55, 120.75).
New vias 0.6 / 0.3 mm.
"""
import sys
import pcbnew
import boardio
from boardio import add_track, add_via, pad_xy, place, find_tracks, via_xy, mm

F = pcbnew.FromMM
b = boardio.load()
fp = boardio.footprints(b)
tracks = list(b.GetTracks())
if abs(boardio.pos(fp["JP3"])[0] - 168.6) < 0.01:
    sys.exit("step 9e already applied (JP3 is at x 168.60); nothing done")
T, B, I1 = "Top Layer", "6 Bottom Layer", "Internal 1"
r2 = pad_xy(b, "R2", "2")
assert abs(r2[0] - 154.60) < 0.01 and abs(r2[1] - 123.95) < 0.01, r2

# copper that only served JP3 at its old place
dead = find_tracks(b, tracks, "CFG1_STRAP", T, (154.5, 122.3, 154.7, 124.0))
dead += find_tracks(b, tracks, "ADIN_VDDIO", T, (152.5, 122.3, 153.4, 122.5))
assert len(dead) == 2, len(dead)

place(fp["JP3"], 168.60, 96.40, {"3": (167.30, 96.40), "2": (168.60, 96.40), "1": (169.90, 96.40)})
p1, p2, p3 = (pad_xy(b, "JP3", n) for n in "123")
L = {}
# ---- CFG1_STRAP
s1, s2 = (153.40, 121.40), (p2[0], 98.20)
add_via(b, "CFG1_STRAP", *s1); add_via(b, "CFG1_STRAP", *s2)
L["CFG1_STRAP"] = add_track(b, "CFG1_STRAP", T, [r2, (154.60, 122.60), s1])
L["CFG1_STRAP"] += add_track(b, "CFG1_STRAP", I1, [s1, (154.40, 122.40), (176.50, 122.40), (177.00, 121.90), (177.00, 98.70),
                                                    (176.50, 98.20), s2])
L["CFG1_STRAP"] += add_track(b, "CFG1_STRAP", T, [s2, p2])
# ---- ADIN_VDDIO
v0 = via_xy(tracks, "ADIN_VDDIO", (155.90, 94.90)); vv = (166.95, 95.25)
add_via(b, "ADIN_VDDIO", *vv)
L["ADIN_VDDIO"] = add_track(b, "ADIN_VDDIO", B, [v0, (155.90, 96.60), (156.36, 97.06), (166.19, 97.06), (166.95, 96.30), vv])
L["ADIN_VDDIO"] += add_track(b, "ADIN_VDDIO", T, [vv, (167.20, 95.00), (p1[0] - 0.25, 95.00), (p1[0], 95.25), p1])
# ---- GND
vg = (167.90, 99.80)
add_via(b, "GND", *vg)
L["GND"] = add_track(b, "GND", T, [p3, (p3[0], 99.20), vg])

# ---- silkscreen: the strap's name and its 1 / 0 ends follow it
moved = 0
for d in b.GetDrawings():
    if d.Type() == pcbnew.PCB_TEXT_T and abs(mm(d.GetPosition().y) - 122.40) < 0.05:
        new = {"0": (165.95, 96.40), "1": (171.60, 96.40), "CFG1": (176.90, 96.40)}.get(d.GetText())
        if new:
            d.SetPosition(pcbnew.VECTOR2I(F(new[0]), F(new[1]))); moved += 1
assert moved == 3, moved
fp["JP3"].Reference().SetPosition(pcbnew.VECTOR2I(F(173.90), F(96.40)))

for t in dead:
    b.Remove(t)
boardio.save(b)
for n, v in L.items():
    print("  %-12s %.2f mm added" % (n, v))
boardio.report(["JP3"])
