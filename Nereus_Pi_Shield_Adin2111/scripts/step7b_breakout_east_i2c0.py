"""Step 7b and step 5 (I2C0): the six east breakout nets and I2C0 with its pull-ups.

East breakout, J1 pin -> J2 pin, 0.2 mm, no via:
  top layer   (north -> south)  MOTOR_IN2 82.65 | MOTOR_IN1 83.10 | MOTOR_nSLEEP 83.55
  Internal 2  (north -> south)  SPI1_SCLK 82.90 | SPI1_MOSI 83.40 | SPI1_MISO 83.90
  SPI1_SCLK passes east of J2 to reach pin 23; its lane stays 3.3 mm from H2 (keep-out radius 3.0 mm).

I2C0: Sofar's two top stubs end at (159.25 / 159.75, 99.63), walled in by INT on the top layer. Each gets a small
via (0.45 / 0.2 mm, beside the SPI vias of the same size) and continues on an inner layer: SCL on Internal 1,
SDA on Internal 2. North through J2's pin gap at x 159.21 to J1 pins 28 / 27; east below J2 to J2 pins 16 / 15.

R26 / R27 (4.7 k pull-ups to PI_3V3) sat on old 3V3 copper of the mote, which shorted 3V3 to PI_3V3. They move
below J2 beside pin 13 (PI_3V3) and pin 15 (SDA). One 0.6 / 0.3 mm via brings SCL up to R26. The 1.47 mm of
old 3V3 track that joined their former pads is removed.
"""
import sys
import pcbnew
import boardio
from boardio import add_track, add_via, find_tracks, pad_xy, place

b = boardio.load()
fp = boardio.footprints(b)
tracks = list(b.GetTracks())
if any(t.GetNetname().endswith("MOTOR_IN1") for t in tracks):
    sys.exit("step 7b already applied (MOTOR_IN1 has copper); nothing done")
P = 1.27
j1 = lambda n: pad_xy(b, "J1", n)
j2 = lambda n: pad_xy(b, "J2", n)
ROW = (j1("1")[1] + j1("2")[1]) / 2
BOT_ROW, GAP_IN, GAP_OUT = j1("1")[1], 84.00, 86.37

def lane(pin, gap_x, lane_y):
    x, y = j1(pin)
    if abs(y - BOT_ROW) < 0.01:
        return [(x, y), (x, lane_y - 0.60), (x + 0.60, lane_y)]
    return [(x, y), (gap_x, ROW), (gap_x, lane_y - 1.00), (gap_x + 1.00, lane_y)]

def south_pin(pin, lane_y):
    """Leave the lane into the J2 pin gap west of a south-row pin, then 45 degrees into the pin."""
    x, y = j2(pin)
    g = x - P
    return [(g - (GAP_IN - lane_y), lane_y), (g, GAP_IN), (g, GAP_OUT), (x, y)]

def north_pin(pin, lane_y, run=0.45):
    x, y = j2(pin)
    return [(x - run, lane_y), (x, lane_y + run), (x, y)]

L = {}
# ---- east breakout, top
L["MOTOR_nSLEEP"] = add_track(b, "MOTOR_nSLEEP", "Top Layer", lane("29", None, 83.55) + south_pin("17", 83.55))
L["MOTOR_IN1"] = add_track(b, "MOTOR_IN1", "Top Layer", lane("32", j1("31")[0] - P, 83.10) + south_pin("19", 83.10))
L["MOTOR_IN2"] = add_track(b, "MOTOR_IN2", "Top Layer", lane("33", None, 82.65) + north_pin("20", 82.65))
# ---- east breakout, Internal 2
L["SPI1_MISO"] = add_track(b, "SPI1_MISO", "Internal 2", lane("35", None, 83.90) + south_pin("21", 83.90))
L["SPI1_MOSI"] = add_track(b, "SPI1_MOSI", "Internal 2", lane("38", j1("37")[0] + P, 83.40) + north_pin("24", 83.40, 0.50))
xe = j2("24")[0] + P + 0.07                                       # x 179.60: east of J2
L["SPI1_SCLK"] = add_track(b, "SPI1_SCLK", "Internal 2",
    lane("40", j1("39")[0] + P, 82.90) + [(xe - 0.70, 82.90), (xe, 83.60), (xe, j2("23")[1] - 0.70), (xe - 0.70, j2("23")[1]), j2("23")])

# ---- I2C0
GX = j2("8")[0] + P                                               # x 159.21: the J2 pin gap used by INT on top
add_via(b, "I2C0_SCL", 159.25, 91.70, 0.45, 0.2)
add_via(b, "I2C0_SDA", 159.75, 92.60, 0.45, 0.2)
L["I2C0_SCL"] = add_track(b, "I2C0_SCL", "Top Layer", [(159.25, 99.63), (159.25, 91.70)])
L["I2C0_SDA"] = add_track(b, "I2C0_SDA", "Top Layer", [(159.75, 99.63), (159.75, 92.60)])
g28 = j1("27")[0] + P                                             # x 158.96: J1 pin gap for pin 28
L["I2C0_SCL"] += add_track(b, "I2C0_SCL", "Internal 1",
    [(159.25, 91.70), (GX, 91.20), (GX, 83.20), (g28, 82.95), (g28, ROW), j1("28")])
g16 = j2("16")[0] + P                                             # x 169.37
L["I2C0_SCL"] += add_track(b, "I2C0_SCL", "Internal 1",
    [(GX, 91.20), (g16 - 1.00, 91.20), (g16, 90.20), (g16, GAP_OUT), j2("16")])
L["I2C0_SDA"] += add_track(b, "I2C0_SDA", "Internal 2",
    [(159.75, 92.60), (159.75, 90.60), (GX, 90.06), (GX, 83.50), (j1("27")[0], 81.98), j1("27")])
L["I2C0_SDA"] += add_track(b, "I2C0_SDA", "Internal 2",
    [(159.75, 90.60), (j2("15")[0] - 1.10, 90.60), (j2("15")[0], 89.50), j2("15")])

# ---- R26 / R27 below J2
old_3v3 = find_tracks(b, tracks, "3V3", "Top Layer", (147.2, 108.3, 149.1, 108.8))
assert len(old_3v3) == 1, len(old_3v3)
p13, p15 = j2("13"), j2("15")
place(fp["R27"], 166.83, 89.40, {"2": (166.43, 89.40), "1": (167.23, 89.40)})
place(fp["R26"], p13[0], 90.60, {"2": (p13[0], 90.20), "1": (p13[0], 91.00)})
L["PI_3V3"] = add_track(b, "PI_3V3", "Top Layer", [(166.43, 89.40), (165.95, 88.92), (p13[0] + 0.30, 88.30)])
L["PI_3V3"] += add_track(b, "PI_3V3", "Top Layer", [(p13[0], 90.20), (p13[0], 88.30)])
L["I2C0_SDA"] += add_track(b, "I2C0_SDA", "Top Layer", [(167.23, 89.40), (167.71, 88.92), (p15[0] - 0.30, 88.30)])
add_via(b, "I2C0_SCL", p13[0], 91.85)
L["I2C0_SCL"] += add_track(b, "I2C0_SCL", "Top Layer", [(p13[0], 91.00), (p13[0], 91.85)])
L["I2C0_SCL"] += add_track(b, "I2C0_SCL", "Internal 1", [(p13[0], 91.85), (p13[0], 91.20)])

for t in old_3v3:
    b.Remove(t)
boardio.save(b)
for n, v in L.items():
    print("  %-13s %.2f mm added" % (n, v))
boardio.report(["R26", "R27"])
