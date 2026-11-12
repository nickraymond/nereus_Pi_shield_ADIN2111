"""Step 2 of the routing plan: ADIN control nets and the two SPI-configuration straps.

Routes
- ~ADIN_INT   top:    J1.22 -> J1 gap x 151.34 -> channel lane y 83.0 -> J2 gap x 159.21 -> Sofar's stub at (160.75, 99.63)
- ADIN_PWR    bottom: J1.16 -> J1 gap x 143.72 -> lane y 83.3 -> J2 gap x 164.29 -> Sofar's via (165.13, 96.50)
- ~ADIN_RST   bottom: J1.18 -> J1 gap x 146.26 -> lane y 82.7 -> J2 gap x 166.83 -> Sofar's via (165.13, 94.50)
  (two nets on one layer in the header channel cross unless their order at J1 equals their order at J2;
  PWR and RST keep theirs, INT is alone on the top layer)
- ADIN_TIMER  bottom: R47.1 -> via -> south of U1 east along y 121.6 -> north along x 176.99 (a J2 pin gap) -> J2.22
              -> lane y 83.0 -> J1 gap x 169.12 -> J1.36. U1 pin 19 is on U1's south side and the two header pins are in
              the north-east corner, so this net is long (about 78 mm) whichever end R47 sits at.

Strap CFG0 (U1 pin 43, SDO / MISO): at the SPI landing
- R9 goes to the top side onto the end of Sofar's MISO stub; JP4 at (154.6, 96.4): pad 1 GND to the existing GND via
  (152.28, 96.28), pad 3 ADIN_VDDIO through a new via and Internal 2 to Sofar's ADIN_VDDIO via (155.66, 108.23).
- The old CFG0_STRAP bottom track from R9's former place (12.6 mm, dead end) is removed.

Strap CFG1 (U1 pin 19): south of U1
- R2 cannot be reached where it was: its CFG1_STRAP pad is boxed in under U1 with no room for a via. R2, R47 and JP3
  move together to free board south of U1; the pin-19 node comes to them on Internal 2 from its existing via
  (153.99, 117.22). JP3 at (154.6, 122.4): pad 1 ADIN_VDDIO through a new via and Internal 2 to Sofar's via
  (153.23, 117.18), pad 3 GND to the existing GND via (156.55, 120.75).
New vias are 0.6 mm with a 0.3 mm hole. Tracks 0.2 mm.
"""
import sys
import pcbnew
import boardio
from boardio import add_track, add_via, find_tracks, pad_xy, via_xy, place

b = boardio.load()
fp = boardio.footprints(b)
tracks = list(b.GetTracks())
if any(t.GetNetname().endswith("ADIN_TIMER") for t in tracks):
    sys.exit("step 2 already applied (ADIN_TIMER has copper); nothing done")
N19 = "Net-(U1A-P1_LED_0{slash}SPI_CFG1)"   # U1 pin 19, P1_LED_0 / SPI_CFG1
P = 1.27

# ---- placements
place(fp["JP4"], 154.60, 96.40, {"1": (153.30, 96.40), "3": (155.90, 96.40)})
place(fp["R9"], 158.25, 98.83, {"1": (158.25, 98.43), "2": (158.25, 99.23)}, top=True)
place(fp["JP3"], 154.60, 122.40, {"1": (153.30, 122.40), "3": (155.90, 122.40)})
place(fp["R2"], 154.60, 124.35, {"2": (154.60, 123.95), "1": (154.60, 124.75)}, top=True)
place(fp["R47"], 153.27, 124.75, {"1": (152.79, 124.75), "2": (153.75, 124.75)})

# ---- dead copper to remove
dead = find_tracks(b, tracks, "CFG0_STRAP", "6 Bottom Layer", (143.5, 99.0, 147.0, 109.5))
assert len(dead) == 11, len(dead)
dead_n19 = find_tracks(b, tracks, N19, "6 Bottom Layer", (153.5, 116.0, 155.0, 117.5))
assert len(dead_n19) == 3, len(dead_n19)

L = {}
# ---- ~ADIN_INT on top
j1 = lambda n: pad_xy(b, "J1", n)
row_mid = (j1("22")[1] + j1("21")[1]) / 2
g = j1("21")[0] + P                                            # 151.34
L["~{ADIN_INT}"] = add_track(b, "~{ADIN_INT}", "Top Layer", [
    j1("22"), (g, row_mid), (g, 82.10), (g + 0.90, 83.00), (158.42, 83.00), (159.21, 83.79), (159.21, 88.90),
    (160.75, 90.44), (160.75, 99.63)])
# ---- ADIN_PWR and ~ADIN_RST on the bottom
v_pwr = via_xy(tracks, "ADIN_PWR", (165.13, 96.50))
v_rst = via_xy(tracks, "~{ADIN_RST}", (165.13, 94.50))
g = j1("15")[0] + P                                            # 143.72
L["ADIN_PWR"] = add_track(b, "ADIN_PWR", "6 Bottom Layer", [
    j1("16"), (g, row_mid), (g, 82.10), (g + 1.20, 83.30), (163.50, 83.30), (164.29, 84.09), (164.29, 88.90),
    (163.90, 89.29), (163.90, 95.90), (164.50, 96.50), v_pwr])
g = j1("17")[0] + P                                            # 146.26
L["~{ADIN_RST}"] = add_track(b, "~{ADIN_RST}", "6 Bottom Layer", [
    j1("18"), (g, row_mid), (g, 82.10), (g + 0.60, 82.70), (166.03, 82.70), (166.83, 83.50), (166.83, 92.80), v_rst])

# ---- strap CFG0 at the SPI landing
L["ADIN_MISO"] = add_track(b, "ADIN_MISO", "Top Layer", [(158.25, 99.63), (158.25, 99.23)])
L["CFG0_STRAP"] = add_track(b, "CFG0_STRAP", "Top Layer", [(158.25, 98.43), (154.60, 98.43), (154.60, 96.40)])
v_gnd = via_xy(tracks, "GND", (152.28, 96.28))
L["GND"] = add_track(b, "GND", "Top Layer", [(153.30, 96.40), v_gnd])
add_via(b, "ADIN_VDDIO", 155.90, 94.90)
v_vd = via_xy(tracks, "ADIN_VDDIO", (155.66, 108.23))
L["ADIN_VDDIO"] = add_track(b, "ADIN_VDDIO", "Top Layer", [(155.90, 96.40), (155.90, 94.90)])
L["ADIN_VDDIO"] += add_track(b, "ADIN_VDDIO", "Internal 2", [(155.90, 94.90), (155.90, 107.60), (v_vd[0], 107.84), v_vd])

# ---- strap CFG1 south of U1
v_19 = via_xy(tracks, N19, (153.99, 117.22))
add_via(b, N19, 154.60, 125.75)
L[N19] = add_track(b, N19, "Internal 2", [v_19, (v_19[0], 124.00), (154.60, 124.61), (154.60, 125.75)])
L[N19] += add_track(b, N19, "Top Layer", [(154.60, 125.75), (154.60, 124.75), (153.75, 124.75)])
L["CFG1_STRAP"] = add_track(b, "CFG1_STRAP", "Top Layer", [(154.60, 122.40), (154.60, 123.95)])
v_vd2 = via_xy(tracks, "ADIN_VDDIO", (153.23, 117.18))
add_via(b, "ADIN_VDDIO", 152.55, 122.40)
L["ADIN_VDDIO"] += add_track(b, "ADIN_VDDIO", "Internal 2", [v_vd2, (v_vd2[0], 117.90), (152.55, 118.58), (152.55, 122.40)])
L["ADIN_VDDIO"] += add_track(b, "ADIN_VDDIO", "Top Layer", [(152.55, 122.40), (153.30, 122.40)])
v_gnd2 = via_xy(tracks, "GND", (156.55, 120.75))
L["GND"] += add_track(b, "GND", "Top Layer", [(155.90, 122.40), (155.90, 121.40), v_gnd2])

# ---- ADIN_TIMER
add_via(b, "ADIN_TIMER", 151.90, 124.75)
j2_22 = pad_xy(b, "J2", "22")
gt = j1("35")[0] + P                                           # 169.12
L["ADIN_TIMER"] = add_track(b, "ADIN_TIMER", "Top Layer", [(152.79, 124.75), (151.90, 124.75)])
L["ADIN_TIMER"] += add_track(b, "ADIN_TIMER", "6 Bottom Layer", [
    (151.90, 124.75), (155.05, 121.60), (176.19, 121.60), (176.99, 120.80), (176.99, j2_22[1] + P), j2_22,
    (j2_22[0], 84.00), (j2_22[0] - 1.00, 83.00), (gt + 1.00, 83.00), (gt, 82.00), (gt, row_mid), j1("36")])

for t in dead + dead_n19:
    b.Remove(t)
boardio.save(b)
for n, v in L.items():
    print("  %-12s %.2f mm added" % (n, v))
print("  removed: %d dead CFG0_STRAP segments, %d dead pin-19 segments; 4 vias added" % (len(dead), len(dead_n19)))
boardio.report(["JP3", "JP4", "R2", "R9", "R47"])
