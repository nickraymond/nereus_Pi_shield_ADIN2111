"""Stage 3 phase D (part): ADIN header signals through the channel. Usage: <KiCad python> phaseD.py <in board> <out board> [log.json]

Sofar's fan-out to the old connector ends in a row of stubs at x 43.78..47.28 (0.5 mm pitch), pointing north. The Pi header pins
are 2.4..16 mm west of them and in a different order, so the eight nets are split over layers such that no two cross on a layer;
each is: out of the pin, one horizontal run in the channel (y 6.9..8.7, 0.4 mm pitch), down into its stub. 0.2 mm tracks
(the net class), 45 degree corners. Row-2 pins (y 2.23) leave between two row-1 pads (x 29.96, 35.04, 40.12).
  Top         ADIN_MISO (pin 21), I2C0_SCL (28), I2C0_SDA (27): straight onto Sofar's top stubs at y 10.289.
  Internal 1  ADIN_MOSI (19) onto Sofar's Internal 1 stub; ~ADIN_INT (22), one via at (47.281, 9.7) up to its top stub.
  Internal 2  ADIN_SCK (23), ~ADIN_CS (24) into Sofar's vias at (44.281, 12.045) and (43.781, 12.514).
  Bottom      ~ADIN_RST (18): y 8.7 east, then down to a via ON Sofar's remaining Internal 1 track (x 52.706, y 6.214..11.114) at y 10.406, as review_G_routing F1 asks.
"""
import sys, s3lib
r = s3lib.Router(sys.argv[1], 'D'); T, B, I1, I2 = 'Top Layer', '6 Bottom Layer', 'Internal 1', 'Internal 2'
W = 0.2
r.track('ADIN_MISO', T, [(33.77, 4.77), (33.77, 6.7), (34.77, 7.7), (43.781, 7.7), (44.781, 8.7), (44.781, 10.289)], W)
r.track('I2C0_SCL', T, [(41.39, 2.23), (40.12, 3.5), (40.12, 6.3), (41.12, 7.3), (44.781, 7.3), (45.781, 8.3), (45.781, 10.289)], W)
r.track('I2C0_SDA', T, [(41.39, 4.77), (41.39, 5.9), (42.39, 6.9), (45.281, 6.9), (46.281, 7.9), (46.281, 10.289)], W)
r.track('ADIN_MOSI', I1, [(31.23, 4.77), (31.23, 7.1), (32.23, 8.1), (44.268, 8.1), (45.268, 9.1), (45.268, 12.163)], W)
r.track('~{ADIN_INT}', I1, [(33.77, 2.23), (35.04, 3.5), (35.04, 6.7), (36.04, 7.7), (46.281, 7.7), (47.281, 8.7), (47.281, 9.7)], W)
r.via('~{ADIN_INT}', (47.281, 9.7)); r.track('~{ADIN_INT}', T, [(47.281, 9.7), (47.281, 10.289)], W)
r.track('ADIN_SCK', I2, [(36.31, 4.77), (36.31, 6.7), (37.31, 7.7), (43.281, 7.7), (44.281, 8.7), (44.281, 12.045)], W)
r.track('~{ADIN_CS}', I2, [(36.31, 2.23), (35.04, 3.5), (35.04, 7.1), (36.04, 8.1), (42.781, 8.1), (43.781, 9.1), (43.781, 12.514)], W)
r.track('~{ADIN_RST}', B, [(28.69, 2.23), (29.96, 3.5), (29.96, 7.9), (30.76, 8.7), (51.0, 8.7), (52.706, 10.406)], W)
r.via('~{ADIN_RST}', (52.706, 10.406))   # at y 8.7 a 0.6 mm via would sit 0.05 mm from Sofar's ADIN_PWR track (x 52.256, Internal 1)
n = r.report_bad()
r.finish(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None); r.summary()
sys.exit(1 if n else 0)
