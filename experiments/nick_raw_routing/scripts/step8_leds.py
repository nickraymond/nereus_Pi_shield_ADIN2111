"""Step 8: the three status LEDs D9 / D8 / D10 on the south edge, with their resistors R45 / R44 / R46 underneath
and the LED supply jumper JP2. Nick approved the mock-up 2026-11-10.

- JP2 (ADIN_VDDIO -> ADIN_LED_VDD) moves from the east edge to (148.60, 124.30), between C23 and the LEDs.
  ADIN_VDDIO reaches it on top from the via at (152.55, 122.40); ADIN_LED_VDD leaves on top to a new via and
  feeds the three resistors on the bottom.
- ~ADIN_P1_LED1 (U1 pin 21 -> D9) and ~ADIN_P2_LED1 (U1 pin 48 -> D10) run on Internal 2 from Sofar's vias
  beside U1 to one new via each, then a short top track to the LED. They cross on different layers.
- Each LED anode meets its resistor through one new via beside the LED.
- D8's GND pad: top track along the south edge and up to JP3 pad 3 (GND). The GND plane stops at y 123 and has
  a slot at y 121.5 - 122.5, so there is no plane to drop a via into near the LEDs.
New vias 0.6 / 0.3 mm.
"""
import sys
import boardio
from boardio import add_track, add_via, pad_xy, place, via_xy

b = boardio.load()
fp = boardio.footprints(b)
tracks = list(b.GetTracks())
if abs(boardio.pos(fp["JP2"])[0] - 148.6) < 0.01:
    sys.exit("step 8 already applied (JP2 is at x 148.60); nothing done")
P1, P2, VDD = "~{ADIN_P1_LED1}", "~{ADIN_P2_LED1}", "ADIN_LED_VDD"
pad = lambda ref, n: pad_xy(b, ref, n)
T, B, I2 = "Top Layer", "6 Bottom Layer", "Internal 2"
L = {}

# ---- JP2 and the LED supply
place(fp["JP2"], 148.60, 124.30, {"1": (148.60, 122.85), "2": (148.60, 125.75)})
vio = via_xy(tracks, "ADIN_VDDIO", (152.55, 122.40))
L["ADIN_VDDIO"] = add_track(b, "ADIN_VDDIO", T, [vio, (150.40, 122.40), (149.95, 122.85), pad("JP2", "1")])
vL = (146.40, 125.20)
add_via(b, VDD, *vL)
L[VDD] = add_track(b, VDD, T, [pad("JP2", "2"), (146.95, 125.75), vL])
L[VDD] += add_track(b, VDD, B, [vL, (145.80, 125.80), pad("R45", "2")])
L[VDD] += add_track(b, VDD, B, [vL, (151.20, 125.20), (151.80, 125.80), pad("R46", "2")])
r44 = pad("R44", "2")
L[VDD] += add_track(b, VDD, B, [(150.30, 125.20), (150.30, r44[1] - 0.50), (149.80, r44[1]), r44])

# ---- link LEDs from U1, Internal 2
s1 = via_xy(tracks, P1, (155.25, 117.15)); v1 = (146.50, 126.80)
add_via(b, P1, *v1)
L[P1] = add_track(b, P1, I2, [s1, (155.25, 118.60), (155.50, 118.85), (155.50, 125.90), (154.60, 126.80), v1])
d9 = pad("D9", "1")
L[P1] += add_track(b, P1, T, [v1, (d9[0], v1[1] + v1[0] - d9[0]), d9])
s2 = via_xy(tracks, P2, (150.70, 108.89)); v2 = (150.70, 123.90)
add_via(b, P2, *v2)
L[P2] = add_track(b, P2, I2, [s2, v2])
d10 = pad("D10", "1")
L[P2] += add_track(b, P2, T, [v2, (150.70, 126.30), (d10[0], 126.30 + d10[0] - 150.70), d10])

# ---- anodes: LED (top) to resistor (bottom)
for led, lp, res, rp, vx in (("D9", "2", "R45", "1", 146.85), ("D8", "2", "R44", "1", 147.85), ("D10", "2", "R46", "1", 152.85)):
    a = pad(led, lp); r = pad(res, rp); net = "Net-(%s-A)" % led
    add_via(b, net, vx, a[1])
    k = abs(a[1] - r[1])
    L[net] = add_track(b, net, T, [a, (vx, a[1])])
    L[net] += add_track(b, net, B, [r, (vx - k if vx > r[0] else vx + k, r[1]), (vx, a[1])])

# ---- D8 cathode to GND at JP3 pad 3
g = pad("D8", "1"); j = pad("JP3", "3")
L["GND"] = add_track(b, "GND", T, [g, (g[0], 130.00), (g[0] + 0.50, 130.50), (154.70, 130.50), (155.40, 129.80), (155.40, 124.20),
                                   (j[0], 124.20 + j[0] - 155.40), j])

boardio.save(b)
for n, v in L.items():
    print("  %-18s %.2f mm added" % (n, v))
boardio.report(["JP2"])
