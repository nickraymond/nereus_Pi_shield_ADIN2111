"""Step 9f: the I2C0 pull-ups R26 (SCL) and R27 (SDA) move to the bottom side, 4 mm south of J2's pads
(Nick, 2026-11-10: soldering at the header must not disturb them).

- R27 at (168.10, 93.00), R26 at (169.90, 93.00), bottom side, upright; SDA / SCL pads north.
- SDA: bottom from J2 pin 15 straight south. SCL: bottom from J2 pin 16 through the pin gap at x 169.37.
- PI_3V3: top from J2 pin 13 to a via at (167.30, 94.20), then bottom to both resistors.
- Removed: the top tracks at the old place, and the I2C0_SCL via at (165.56, 91.85) with its Internal 1 stub.
- Silkscreen: with the resistors gone from the top, pins 11, 13 and 15 get their names straight below.
"""
import sys
import pcbnew
import boardio
from boardio import add_track, add_via, pad_xy, place, find_tracks, mm

F = pcbnew.FromMM
b = boardio.load()
fp = boardio.footprints(b)
tracks = list(b.GetTracks())
if fp["R26"].IsFlipped():
    sys.exit("step 9f already applied (R26 is on the bottom); nothing done")
T, B = "Top Layer", "6 Bottom Layer"
TOP = b.GetLayerID("Top Overlay")

box = (165.4, 88.2, 167.9, 91.9)
dead = find_tracks(b, tracks, "PI_3V3", T, box) + find_tracks(b, tracks, "I2C0_SCL", T, box) + find_tracks(b, tracks, "I2C0_SDA", T, box)
dead += find_tracks(b, tracks, "I2C0_SCL", "Internal 1", (165.5, 91.1, 165.6, 91.9))
dead += [t for t in tracks if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname().endswith("I2C0_SCL")
         and abs(mm(t.GetPosition().x) - 165.56) < 0.02 and abs(mm(t.GetPosition().y) - 91.85) < 0.02]
assert len(dead) == 3 + 1 + 2 + 1 + 1, len(dead)

for r, x in (("R27", 168.10), ("R26", 169.90)):
    f = fp[r]
    f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    place(f, x, 93.00, {"1": (x, 92.60), "2": (x, 93.40)})
    assert f.IsFlipped()
    ref = f.Reference()
    ref.SetTextAngleDegrees(0)
    ref.SetPosition(pcbnew.VECTOR2I(F(x + (-1.5 if r == "R27" else 1.5)), F(93.00)))
j = lambda n: pad_xy(b, "J2", n)
L = {}
L["I2C0_SDA"] = add_track(b, "I2C0_SDA", B, [j("15"), pad_xy(b, "R27", "1")])
x16, y16 = j("16")
L["I2C0_SCL"] = add_track(b, "I2C0_SCL", B, [(x16, y16), (x16 + 1.27, y16 + 1.27), (x16 + 1.27, 91.50), (169.90, 92.03), pad_xy(b, "R26", "1")])
v = (167.30, 94.20)
add_via(b, "PI_3V3", *v)
x13, y13 = j("13")
L["PI_3V3"] = add_track(b, "PI_3V3", T, [(x13, y13), (x13, v[1] - (v[0] - x13)), v])
L["PI_3V3"] += add_track(b, "PI_3V3", B, [pad_xy(b, "R26", "2"), pad_xy(b, "R27", "2"), v])

# ---- silkscreen under J2 pins 11, 13, 15
gone = 0
for d in list(b.GetDrawings()):
    if d.GetLayer() != TOP:
        continue
    x, y = mm(d.GetPosition().x), mm(d.GetPosition().y)
    if d.Type() == pcbnew.PCB_SHAPE_T and 89.5 < mm(d.GetStart().y) < 89.8 and 162.0 < mm(d.GetStart().x) < 166.5:
        b.Remove(d); gone += 1                                        # the bracket under pins 11 and 13
    elif d.Type() == pcbnew.PCB_TEXT_T and abs(y - 90.35) < 0.05:
        if d.GetText() == "3V3" and abs(x - 163.50) < 0.05:
            d.SetPosition(pcbnew.VECTOR2I(F(163.22), F(90.35))); gone += 1   # pin 11, clear of the via at (161.75, 89.75)
        elif d.GetText() == "SD0":
            d.SetPosition(pcbnew.VECTOR2I(F(168.10), F(90.35))); gone += 1
assert gone == 3 + 1 + 1, gone
t = pcbnew.PCB_TEXT(b)
t.SetText("3V3"); t.SetLayer(TOP)
t.SetTextSize(pcbnew.VECTOR2I(F(0.6), F(1.0))); t.SetTextThickness(F(0.15))
t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER); t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
t.SetPosition(pcbnew.VECTOR2I(F(x13), F(90.35)))
b.Add(t)

for t in dead:
    b.Remove(t)
boardio.save(b)
for n, v in L.items():
    print("  %-9s %.2f mm added" % (n, v))
boardio.report(["R26", "R27"])
