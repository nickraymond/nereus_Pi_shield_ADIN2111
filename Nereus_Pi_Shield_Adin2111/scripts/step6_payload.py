"""Step 6: PAYLOAD_EN (Pi GPIO26, J1 pin 37) and ~PAYLOAD_FAULT (Pi GPIO6, J1 pin 31) to the load switch U11,
and PAYLOAD_EN to its test pad TP19. Nick approved the mock-up 2026-11-10.

- Both leave J1 on Internal 1, come down a J2 pin gap (161.75 / 171.91) to a new via south of J2, and run
  west on the bottom (lanes y 93.40 and y 97.50), south of the I2C3 pair.
- ~PAYLOAD_FAULT: new via at (144.60, 93.40), then Internal 2 around the GND vias to Sofar's via at
  (137.03, 98.49) (the bottom layer is walled off there by the VBUS track).
- PAYLOAD_EN: the bottom lane ends on Sofar's via at (143.90, 97.95). From that via Internal 2 goes south to a
  new via beside TP19 (east of the plane slot at x 138.4), then 1.5 mm of bottom track to the pad.
- Removed: a dead 3V3 stub on the bottom (4 segments from the via at (143.80, 95.25) to an open end at
  (144.55, 97.69); DRC listed the open end) that sat in PAYLOAD_EN's way, and its via, which served nothing else.
New vias 0.6 / 0.3 mm.
"""
import sys
import pcbnew
import boardio
from boardio import add_track, add_via, pad_xy, find_tracks, via_xy, mm

b = boardio.load()
tracks = list(b.GetTracks())
sn = lambda t: t.GetNetname().split("/")[-1]
FAULT, EN = "~{PAYLOAD_FAULT}", "PAYLOAD_EN"
if any(sn(t) == EN and b.GetLayerName(t.GetLayer()) == "Internal 1" for t in tracks):
    sys.exit("step 6 already applied (PAYLOAD_EN has Internal 1 copper); nothing done")
P = 1.27
j1 = lambda n: pad_xy(b, "J1", n)

dead = find_tracks(b, tracks, "3V3", "6 Bottom Layer", (143.7, 95.2, 144.6, 97.75))
assert len(dead) == 4, len(dead)
dead += [t for t in tracks if t.Type() == pcbnew.PCB_VIA_T and sn(t) == "3V3"
         and abs(mm(t.GetPosition().x) - 143.80) < 0.02 and abs(mm(t.GetPosition().y) - 95.25) < 0.02]
assert len(dead) == 5, len(dead)

L = {}
# ---- ~PAYLOAD_FAULT
x, y = j1("31")                                   # (162.77, 80.87)
g = 161.75                                        # J2 pin gap between pins 9/10 and 11/12
vF1, vF2 = (g, 89.75), (144.60, 93.40)
sF = via_xy(tracks, FAULT, (137.03, 98.49))
add_via(b, FAULT, *vF1); add_via(b, FAULT, *vF2)
L[FAULT] = add_track(b, FAULT, "Internal 1", [(x, y), (x, 81.95), (g, x - g + 81.95), vF1])
L[FAULT] += add_track(b, FAULT, "6 Bottom Layer", [vF1, (g, 92.80), (g - 0.60, 93.40), vF2])
L[FAULT] += add_track(b, FAULT, "Internal 2", [vF2, (139.60, 93.40), (138.60, 94.40), (138.60, sF[1] - 0.60), (138.00, sF[1]), sF])

# ---- PAYLOAD_EN
x, y = j1("37")                                   # (170.39, 80.87)
g = 171.91                                        # J2 pin gap between pins 17/18 and 19/20
vE1, vT = (g, 89.30), (139.40, 107.33)
sE = via_xy(tracks, EN, (143.90, 97.95))
add_via(b, EN, *vE1); add_via(b, EN, *vT)
L[EN] = add_track(b, EN, "Internal 1", [(x, y), (x, 82.48), (g, g - x + 82.48), vE1])
L[EN] += add_track(b, EN, "6 Bottom Layer", [vE1, (g, 96.90), (g - 0.60, 97.50), (sE[0] + 0.45, 97.50), sE])
L[EN] += add_track(b, EN, "Internal 2", [sE, (142.30, sE[1] + sE[0] - 142.30), (142.30, 104.43), vT])
L[EN] += add_track(b, EN, "6 Bottom Layer", [vT, pad_xy(b, "TP19", "1")])

for t in dead:
    b.Remove(t)
boardio.save(b)
for n, v in L.items():
    print("  %-18s %.2f mm added" % (n, v))
print("  removed: dead 3V3 stub, %d segments and 1 via" % (len(dead) - 1))
