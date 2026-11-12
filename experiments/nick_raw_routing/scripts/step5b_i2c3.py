"""Step 5b: I2C3 (Pi GPIO27 / GPIO22 -> J2 pins 8 / 7 -> Qwiic connector J3) with its pull-ups. Nick approved the mock-up 2026-11-10.

- SCL: top layer, J1 pin 13 -> channel lane y 82.60 -> J2 pin 8.
- SDA: bottom layer, J1 pin 15 -> channel lane y 83.15 -> J2 pin gap x 156.67 -> J2 pin 7.
- To J3: on the bottom from J2 pins 7 / 8 west below J2 and J6 to two vias south of J6, then on Internal 1
  past the 5 V converter (its 5V_PI and VBUS tracks wall off the bottom layer there) and down to two vias
  beside J3. All four vias 0.6 / 0.3 mm. SDA passes between the 5V_FB via and the VBUS via, SCL south of both.
- Pull-ups R10 (SDA) and R24 (SCL) move to the bottom side beside J3's vias (on top R10's courtyard would
  overlap J3's). Below J2 they do not fit: SCL comes down between SDA's pin 7 and PI_3V3 pin 9.
- Removed: all of the mote's old copper on the two I2C3 nets (it belonged to R10 / R24's former place) and the
  PI_3V3 feed that only served those two resistors (Internal 2 trunk at x 146.98, its via and bottom tracks).
"""
import sys
import pcbnew
import boardio
from boardio import add_track, add_via, pad_xy, place, mm

b = boardio.load()
fp = boardio.footprints(b)
tracks = list(b.GetTracks())
sn = lambda t: t.GetNetname().split("/")[-1]
if abs(boardio.pos(fp["R10"])[0] - 125.0) < 0.01:
    sys.exit("step 5b already applied (R10 is beside J3); nothing done")
P = 1.27
j1 = lambda n: pad_xy(b, "J1", n)
j2 = lambda n: pad_xy(b, "J2", n)
j3 = lambda n: pad_xy(b, "J3", n)

# ---- old copper to remove
dead = [t for t in tracks if sn(t) in ("I2C3_SCL", "I2C3_SDA")]
assert len(dead) == 38, len(dead)                      # 36 segments and the two vias at (152.08, 95.43), (145.10, 95.45)
def at(t, x, y):
    return abs(mm(t.GetPosition().x) - x) < 0.02 and abs(mm(t.GetPosition().y) - y) < 0.02
for t in tracks:
    if sn(t) != "PI_3V3":
        continue
    if t.Type() == pcbnew.PCB_VIA_T:
        if at(t, 146.98, 98.08):
            dead.append(t)
        continue
    xs = sorted([mm(t.GetStart().x), mm(t.GetEnd().x)]); ys = sorted([mm(t.GetStart().y), mm(t.GetEnd().y)])
    layer = b.GetLayerName(t.GetLayer())
    if layer == "Internal 2" and xs[1] > 146.9 and xs[1] < 147.1 and ys[1] > 84.5:      # the trunk and its diagonal from J1 pin 17
        dead.append(t)
    if layer == "6 Bottom Layer" and xs[0] > 146.9 and xs[1] < 149.0 and ys[0] > 97.3:
        dead.append(t)
assert len(dead) == 38 + 1 + 2 + 4, len(dead)

# ---- pull-ups beside J3, both on the bottom
place(fp["R24"], 123.90, 102.25, {"2": (123.90, 101.87), "1": (123.90, 102.63)})
place(fp["R10"], 125.00, 101.72, {"2": (125.00, 101.34), "1": (125.00, 102.10)})
assert fp["R24"].IsFlipped() and fp["R10"].IsFlipped()

L = {}
# ---- Pi -> J2
x13, y13 = j1("13"); x15, y15 = j1("15")
L["I2C3_SCL"] = add_track(b, "I2C3_SCL", "Top Layer",
    [(x13, y13), (x13, 82.00), (x13 + 0.60, 82.60), (j2("8")[0] - 0.45, 82.60), (j2("8")[0], 83.05), j2("8")])
g = j2("8")[0] - P                                                 # x 156.67
L["I2C3_SDA"] = add_track(b, "I2C3_SDA", "6 Bottom Layer",
    [(x15, y15), (x15, 82.55), (x15 + 0.60, 83.15), (g - 0.85, 83.15), (g, 84.00), (g, 86.37), j2("7")])
# ---- J2 -> vias south of J6, bottom
x7, y7 = j2("7"); x8, y8 = j2("8")
VA = {"I2C3_SDA": (141.30, 90.30), "I2C3_SCL": (143.00, 90.60)}     # bottom -> Internal 1
VJ = {"I2C3_SDA": (125.90, 102.10), "I2C3_SCL": (124.70, 103.10)}   # Internal 1 -> J3
for n in VA:
    add_via(b, n, *VA[n]); add_via(b, n, *VJ[n])
L["I2C3_SDA"] += add_track(b, "I2C3_SDA", "6 Bottom Layer",
    [(x7, y7), (x7, 88.90), (x7 - 0.40, 89.30), (142.30, 89.30), VA["I2C3_SDA"]])
L["I2C3_SCL"] += add_track(b, "I2C3_SCL", "6 Bottom Layer",
    [(x8, y8), (x8 + P, y8 + P), (x8 + P, 89.30), (x8 + P - 0.45, 89.75), (143.85, 89.75), VA["I2C3_SCL"]])
# ---- past the 5 V converter to J3, Internal 1
L["I2C3_SDA"] += add_track(b, "I2C3_SDA", "Internal 1",
    [VA["I2C3_SDA"], (138.70, 92.90), (129.70, 92.90), (129.20, 93.40), (129.20, 101.60), (128.70, 102.10), VJ["I2C3_SDA"]])
L["I2C3_SCL"] += add_track(b, "I2C3_SCL", "Internal 1",
    [VA["I2C3_SCL"], (139.30, 94.30), (130.50, 94.30), (130.00, 94.80), (130.00, 102.60), (129.50, 103.10), VJ["I2C3_SCL"]])
# ---- at J3
L["I2C3_SDA"] += add_track(b, "I2C3_SDA", "Top Layer", [j3("3"), (VJ["I2C3_SDA"][0], j3("3")[1])])
L["I2C3_SCL"] += add_track(b, "I2C3_SCL", "Top Layer", [j3("4"), (VJ["I2C3_SCL"][0], j3("4")[1])])
L["I2C3_SDA"] += add_track(b, "I2C3_SDA", "6 Bottom Layer", [pad_xy(b, "R10", "1"), VJ["I2C3_SDA"]])
L["I2C3_SCL"] += add_track(b, "I2C3_SCL", "6 Bottom Layer", [pad_xy(b, "R24", "1"), (124.37, 103.10), VJ["I2C3_SCL"]])
L["PI_3V3"] = add_track(b, "PI_3V3", "6 Bottom Layer", [pad_xy(b, "R24", "2"), (123.90, 101.10)], 0.25)
L["PI_3V3"] += add_track(b, "PI_3V3", "6 Bottom Layer", [pad_xy(b, "R10", "2"), (124.76, 101.10), (123.90, 101.10)], 0.25)

for t in dead:
    b.Remove(t)
boardio.save(b)
for n, v in L.items():
    print("  %-9s %.2f mm added" % (n, v))
print("  removed: %d old tracks and vias" % len(dead))
boardio.report(["R10", "R24"])
