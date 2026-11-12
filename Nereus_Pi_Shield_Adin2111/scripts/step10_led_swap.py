"""Step 10: port LEDs beside their own ports (Nick approved the mock on 2026-11-11: "Yes, build it").

Port 1 (ADIN pin 21, ~ADIN_P1_LED1) goes to BM1 on the east side, port 2 (pin 48) to BM2 on the west side,
but step 8 had put D9 (port 1) west and D10 (port 2) east. Now each LED sits beside its own port's inserts
and the power LED D8 stays in the middle. Only step 8's LED copper changes; the schematic stays as it is.

- D9 / R45 swap places with D10 / R46 (same rotations).
- The copper between each LED and its resistor stays where it is and takes the other LED's net.
- Port 2: Internal 2 goes on from (150.70, 123.90) to the lane at y 126.80 and west to the via at
  (146.50, 126.80), which becomes port 2's with its top stub. The old via at (150.70, 123.90) and its three
  top tracks to the east LED are removed.
- Port 1: the Internal 2 lane now ends at a new via at (152.60, 126.80), 0.6 / 0.3 mm, with a top track to
  the east LED's cathode pad.
- Silkscreen: the names P1 / P2 swap; the four moved designators get the places their counterparts had.
"""
import sys
import pcbnew
import boardio
from boardio import add_track, add_via, mm, move_to

F = pcbnew.FromMM
V = lambda x, y: pcbnew.VECTOR2I(F(x), F(y))
b = boardio.load()
fp = boardio.footprints(b)
tracks = list(b.GetTracks())
sn = lambda t: t.GetNetname().split("/")[-1]
P1, P2, A9, A10 = "~{ADIN_P1_LED1}", "~{ADIN_P2_LED1}", "Net-(D9-A)", "Net-(D10-A)"
net = {n: boardio.net_of(b, n) for n in (P1, P2, A9, A10)}
if boardio.pos(fp["D9"])[0] > 150:
    sys.exit("step 10 already applied (D9 is the east LED); nothing done")
assert boardio.pos(fp["D9"]) == (145.8, 128.6) and boardio.pos(fp["D10"]) == (151.8, 128.6), (boardio.pos(fp["D9"]), boardio.pos(fp["D10"]))


def seg(t, layer, a, c):
    if t.Type() == pcbnew.PCB_VIA_T or b.GetLayerName(t.GetLayer()) != layer:
        return False
    e = [(mm(t.GetStart().x), mm(t.GetStart().y)), (mm(t.GetEnd().x), mm(t.GetEnd().y))]
    near = lambda p, q: abs(p[0] - q[0]) < 0.02 and abs(p[1] - q[1]) < 0.02
    return (near(e[0], a) and near(e[1], c)) or (near(e[0], c) and near(e[1], a))


def via(t, x, y):
    return t.Type() == pcbnew.PCB_VIA_T and abs(mm(t.GetPosition().x) - x) < 0.02 and abs(mm(t.GetPosition().y) - y) < 0.02


# ---- parts swap places
for a, c in (("D9", "D10"), ("R45", "R46")):
    assert fp[a].GetOrientationDegrees() == fp[c].GetOrientationDegrees() and fp[a].IsFlipped() == fp[c].IsFlipped(), (a, c)
    pa, pc = boardio.pos(fp[a]), boardio.pos(fp[c])
    move_to(fp[a], *pc); move_to(fp[c], *pa)
# designators: each takes its counterpart's old place; D10 is one character wider than D9, so both keep
# the same gap to their LED (0.632 mm per character at 0.75 mm width)
fp["D10"].Reference().SetPosition(V(143.852, 128.185))      # west LED, text ends where "D9" ended
fp["D9"].Reference().SetPosition(V(153.422, 128.585))       # east LED, text starts where "D10" started
fp["R46"].Reference().SetPosition(V(146.200, 130.298))
fp["R45"].Reference().SetPosition(V(151.800, 130.298))

# ---- anode links keep their copper and take the other LED's net (a via and 3 tracks each)
n9 = [t for t in tracks if sn(t) == A9]; n10 = [t for t in tracks if sn(t) == A10]
assert len(n9) == 4 and len(n10) == 4, (len(n9), len(n10))
for t in n9:
    t.SetNet(net[A10])
for t in n10:
    t.SetNet(net[A9])

# ---- the west stub (via, 2 top tracks) and the west part of the Internal 2 lane become port 2's
west = [t for t in tracks if sn(t) == P1 and (via(t, 146.50, 126.80) or seg(t, "Top Layer", (146.50, 126.80), (145.80, 127.50))
                                             or seg(t, "Top Layer", (145.80, 127.50), (145.80, 127.81)))]
assert len(west) == 3, len(west)
lane = [t for t in tracks if sn(t) == P1 and seg(t, "Internal 2", (154.60, 126.80), (146.50, 126.80))]
assert len(lane) == 1, len(lane)
for t in west + lane:
    t.SetNet(net[P2])
lane[0].SetStart(V(150.30, 126.80)); lane[0].SetEnd(V(146.50, 126.80))
L2 = add_track(b, P2, "Internal 2", [(150.70, 123.90), (150.70, 126.40), (150.30, 126.80)])

# ---- port 1 ends at a new via beside the east LED
L1 = add_track(b, P1, "Internal 2", [(154.60, 126.80), (152.60, 126.80)])
add_via(b, P1, 152.60, 126.80)
L1 += add_track(b, P1, "Top Layer", [(152.60, 126.80), (151.80, 127.60), (151.80, 127.81)])

# ---- port 2's old way to the east LED goes
dead = [t for t in tracks if sn(t) == P2 and (via(t, 150.70, 123.90) or seg(t, "Top Layer", (150.70, 123.90), (150.70, 126.30))
                                             or seg(t, "Top Layer", (150.70, 126.30), (151.80, 127.40)) or seg(t, "Top Layer", (151.80, 127.40), (151.80, 127.81)))]
assert len(dead) == 4, len(dead)

# ---- silkscreen names follow the LEDs
names = [d for d in b.GetDrawings() if d.Type() == pcbnew.PCB_TEXT_T and d.GetText() in ("P1", "P2")]
assert len(names) == 2, len(names)
for d in names:
    d.SetText("P2" if d.GetText() == "P1" else "P1")

for t in dead:
    b.Remove(t)
boardio.save(b)
print("  D9 / R45 at %s, D10 / R46 at %s" % (boardio.pos(fp["D9"]), boardio.pos(fp["D10"])))
print("  removed: 1 via, 3 top tracks; added: 1 via, port 1 %.2f mm, port 2 %.2f mm; 8 anode items and 4 port items change net" % (L1, L2))
boardio.report(["D9", "D10", "R45", "R46"])
