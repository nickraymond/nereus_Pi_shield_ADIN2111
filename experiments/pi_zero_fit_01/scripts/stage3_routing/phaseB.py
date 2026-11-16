"""Stage 3 phase B: planes for the new board areas. Usage: <KiCad python> phaseB.py <in board> <out board> [log.json]

Sofar's plane outlines follow the mote's shape and are not touched. New zones (names start "S3 "), settings as the frozen
board's own added zones ("GND north strip", "5V_PI fill under L6": clearance 0.3, min width 0.25, thermal spokes):
  GND Plane   one U-shaped GND zone: west end, south strip, east end, the SW / SE notches and the NW / NE corners (J1 pins 6
              and 39). It overlaps Sofar's GND zone by 0.3..0.8 mm along its edge; KiCad cuts Sofar's fill back to this zone's outline there,
              so the two fills abut with no gap (zone_touch.py measures it) and are one piece of copper.
              It stays west of Sofar's west slot (x 17.84..18.22) and east of the east slot (x 52.82..53.20).
  PWR Plane   5V_PI in the west strip (the fill the converter group lost in the move, D47), and a PI_5V lane beside it from
              J1 pins 2 / 4 to JP1. Both stay 0.35 mm or more west of Sofar's P_IN / NoConnect_Left outlines (x 10.06).
  Keep-outs   the four screw keep-outs of the frozen board (r 3.0 mm, all copper layers; tracks, vias, pour not allowed).
"""
import sys, s3lib
r = s3lib.Router(sys.argv[1], 'B')
for i, c in enumerate(s3lib.HOLES): r.keepout(c, 3.0, 'H%d screw keep-out' % (i + 1))
r.zone('GND', 'GND Plane', [(0, 0), (17.3, 0), (17.3, 7.0), (12.0, 12.3), (12.0, 14.5), (11.2, 15.3), (11.2, 26.4), (19.0, 26.4), (19.0, 31.9), (51.4, 31.9), (51.4, 26.4),
                            (59.2, 26.4), (59.2, 15.5), (58.2, 14.5), (58.2, 12.2), (53.7, 7.7), (53.7, 0), (65, 0), (65, 39.5), (0, 39.5)], 'GND west / south / east (new board areas)')
r.zone('5V_PI', 'PWR Plane', [(0, 12.4), (7.6, 12.4), (7.6, 29.0), (9.7, 29.0), (9.7, 39.5), (0, 39.5)], '5V_PI west strip (converter output, motor)')
r.zone('PI_5V', 'PWR Plane', [(6.0, 0), (12.3, 0), (12.3, 6.3), (9.7, 6.3), (9.7, 28.6), (8.0, 28.6), (8.0, 6.3), (6.0, 6.3)], 'PI_5V lane (J1 pins 2 / 4 to JP1)')
r.finish(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
