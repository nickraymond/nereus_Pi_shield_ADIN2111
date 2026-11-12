"""Step 7a: make room in the header channel, then the five west breakout nets (Pi -> J2).

Rule used throughout the channel between J1 and J2: two nets on one layer cross unless their west-to-east order
at J1 equals their order at J2; the net that enters further west takes the lane further south.

Lanes (y, mm) after this step        north ............................ south
  top layer                          INT 82.15 | (I2C3_SCL 82.60, later) | CE1 83.05 | UART_RX 83.50
  bottom layer                       RST 82.25 | ADIN_PWR 82.70 | (I2C3_SDA 83.15, later) | CE0 83.60
  Internal 1                         ADC_ALERT 83.00 | UART_TX 83.60
  Internal 2                         PI_3V3 link 82.90 (west of x 144.7)

1. Re-lane: INT moves from y 83.00 to 82.15 (top), ADIN_PWR from 83.30 to 82.70 and RST from 82.70 to 82.25 (bottom).
2. TP38 moves to the bottom side at (136.60, 90.20), on Sofar-style test-pad duty beside the 5V_PI track: on the
   top side it sat in the channel, in the way of every lane.
3. UART_TX and ADC_ALERT on Internal 1, UART_RX and SPI1_CE1 on top, SPI1_CE0 on the bottom. Tracks 0.2 mm, no via.
"""
import sys
import pcbnew
import boardio
from boardio import add_track, find_tracks, move_vertex, pad_xy, move_to

b = boardio.load()
fp = boardio.footprints(b)
tracks = list(b.GetTracks())
if any(t.GetNetname().endswith("UART_TX") for t in tracks):
    sys.exit("step 7a already applied (UART_TX has copper); nothing done")
TOP, BOT = b.GetLayerID("Top Layer"), b.GetLayerID("6 Bottom Layer")
P = 1.27
j1 = lambda n: pad_xy(b, "J1", n)
j2 = lambda n: pad_xy(b, "J2", n)
ROW = (j1("1")[1] + j1("2")[1]) / 2          # y between the two J1 rows
BOT_ROW, GAP_IN, GAP_OUT = j1("1")[1], 84.00, 86.37

# ---- 1. re-lane INT, ADIN_PWR, RST
g = j1("21")[0] + P
move_vertex(tracks, "~{ADIN_INT}", TOP, (g, 82.10), (g, 81.85))
move_vertex(tracks, "~{ADIN_INT}", TOP, (g + 0.90, 83.00), (g + 0.30, 82.15))
move_vertex(tracks, "~{ADIN_INT}", TOP, (158.42, 83.00), (158.37, 82.15))
move_vertex(tracks, "~{ADIN_INT}", TOP, (159.21, 83.79), (159.21, 82.99))
g = j1("15")[0] + P
move_vertex(tracks, "ADIN_PWR", BOT, (g + 1.20, 83.30), (g + 0.60, 82.70))
move_vertex(tracks, "ADIN_PWR", BOT, (163.50, 83.30), (162.90, 82.70))
g = j1("17")[0] + P
move_vertex(tracks, "~{ADIN_RST}", BOT, (g + 0.60, 82.70), (g + 0.15, 82.25))
move_vertex(tracks, "~{ADIN_RST}", BOT, (166.03, 82.70), (165.58, 82.25))

# ---- 2. TP38 to the bottom side
old_stub = find_tracks(b, tracks, "5V_PI", "Top Layer", (133.4, 82.5, 133.7, 84.4))
assert len(old_stub) == 1, len(old_stub)
tp = fp["TP38"]
assert not tp.IsFlipped()
tp.Flip(tp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
move_to(tp, 136.60, 90.20)
L = {"5V_PI": add_track(b, "5V_PI", "6 Bottom Layer", [(136.60, 90.20), (135.40, 90.20)], 0.3)}

# ---- 3. west breakout
def lane(pin, gap_x, lane_y):
    """From a J1 pin down into the channel lane: top-row pins drop through the pin gap at gap_x."""
    x, y = j1(pin)
    if abs(y - BOT_ROW) < 0.01:                                   # bottom-row pin: straight down
        return [(x, y), (x, lane_y - 0.60), (x + 0.60, lane_y)]
    return [(x, y), (gap_x, ROW), (gap_x, lane_y - 1.00), (gap_x + 1.00, lane_y)]

j2w = j2("2")[0] - P - 0.15                                       # x 148.90: west of J2
L["UART_TX"] = add_track(b, "UART_TX", "Internal 1",
    lane("8", j1("7")[0] - P, 83.60) + [(j2w - 1.00, 83.60), (j2w, 84.60), (j2w, j2("1")[1] - 0.70), (j2w + 0.70, j2("1")[1]), j2("1")])
L["~{ADC_ALERT}"] = add_track(b, "~{ADC_ALERT}", "Internal 1",
    lane("7", None, 83.00) + [(j2("2")[0] - 0.90, 83.00), (j2("2")[0], 83.90), j2("2")])
L["UART_RX"] = add_track(b, "UART_RX", "Top Layer",
    lane("10", j1("9")[0] + P, 83.50) + [(j2("2")[0] + P - 0.70, 83.50), (j2("2")[0] + P, 84.20), (j2("2")[0] + P, GAP_OUT), j2("3")])
L["~{SPI1_CE1}"] = add_track(b, "~{SPI1_CE1}", "Top Layer",
    lane("11", None, 83.05) + [(j2("6")[0] - 0.45, 83.05), (j2("6")[0], 83.50), j2("6")])
L["~{SPI1_CE0}"] = add_track(b, "~{SPI1_CE0}", "6 Bottom Layer",
    lane("12", j1("11")[0] + P, 83.60) + [(j2("4")[0] + P - 0.40, 83.60), (j2("4")[0] + P, GAP_IN), (j2("4")[0] + P, GAP_OUT), j2("5")])

for t in old_stub:
    b.Remove(t)
boardio.save(b)
for n, v in L.items():
    print("  %-13s %.2f mm added" % (n, v))
boardio.report(["TP38"])
