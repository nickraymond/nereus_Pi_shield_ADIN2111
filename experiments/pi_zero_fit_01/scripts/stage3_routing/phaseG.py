"""Stage 3 phase G: payload power. Usage: <KiCad python> phaseG.py <in board> <out board> [log.json]

Payload switch U11 (bottom, south-east) with every net of its group, and VBUS_OUT to J5 at its new place. Widths: 1.0 mm outer = 2.4 A at 10 degC rise (power_budget.md s.4);
below that my own IPC-2221 arithmetic for 1 oz outer copper at 10 degC rise: 0.4 mm about 1.2 A, 0.5 mm about 1.45 A, 0.6 mm about 1.6 A.

U11 group. The parts stand on both sides of U11 (C49, the R36 / R34 / C59 column and R41 / R42 east; pins 1-5 west), so five nets
have to cross it; they cross on Internal 2 (VBUS and ~PAYLOAD_FAULT on Internal 1), each with a via at both ends:
  VBUS      bottom 0.6 mm from C20 pad 1 (Sofar's VBUS at TP22 / C20) along y 32.2, south at x 44.5, 0.24 mm neck into pin 1 (the pad
            is 0.24 mm wide); via (44.5, 37.45) -> Internal 1 -> via (50.7, 37.75) at C49 pad 1 -> via (55.5, 36.51) at R41 pad 2.
  VBUS_OUT  pin 10: 0.24 mm neck, then 0.4 mm along the south edge (y 38.72, between R36 / R42 and the edge rule), 1.0 mm north at
            x 57.6, 45 deg past the south-east screw keep-out, north at x 59.1 between TP3 and J5 pad 2, into J5 pad 1. 0.74 A.
            Branch to D3 pad 1, 0.5 mm, y 38.2.
  U11_RTN   pins 3 / 5 into the thermal pad; via in the thermal pad (47.3, 35.3) -> Internal 2 -> via (51.9, 35.4) -> R34 pad 1,
            lane x 52.12 to R36 pad 1, lane x 53.4 to C59 pad 2.
  ISET, dVdT   bottom, north round C49 (lanes x 49.5 / 49.9, then y 32.9 / 33.3).
  UVLO      via (45.25, 36.3) -> Internal 2 y 36.0 -> vias at R36 pad 2 and R41 pad 1.
  PAYLOAD_EN   via (45.25, 35.4) -> Internal 2 y 34.75 -> via (55.6, 38.07) -> R42 pad 1. (To the header: phase H.)
  GND       pin 6 and C49 pad 2: one via each to the GND plane.
"""
import sys, s3lib
r = s3lib.Router(sys.argv[1], 'G'); T, B, I1, I2 = 'Top Layer', '6 Bottom Layer', 'Internal 1', 'Internal 2'
C = 0.13
# ---------------- U11 group ----------------
r.track('VBUS_OUT', B, [(48.9, 37.0), (49.25, 37.0)], 0.24, clr=C, note='neck at pin 10')
r.track('VBUS_OUT', B, [(49.25, 37.0), (49.6, 37.35), (49.6, 37.9), (50.42, 38.72), (56.88, 38.72), (57.6, 38.0)], 0.4, clr=C, note='south edge lane')
r.track('VBUS_OUT', B, [(49.6, 37.6), (49.0, 38.2), (43.5, 38.2)], 0.5, clr=C, note='D3 pad 1')
r.track('VBUS_OUT', B, [(57.6, 38.0), (57.6, 24.5), (59.1, 23.0), (59.1, 12.1), (60.6, 10.6)], 1.0, clr=0.2, note='to J5 pad 1')
r.track('U11_RTN', B, [(46.1, 36.0), (46.9, 36.0)], 0.2, clr=C); r.track('U11_RTN', B, [(46.1, 35.0), (46.9, 35.0)], 0.2, clr=C)
r.track('GND', B, [(48.9, 35.0), (48.9, 33.9)], 0.2, clr=C); r.via('GND', (48.9, 33.9), clr=C)
r.track('GND', B, [(50.8, 35.27), (50.8, 34.1)], 0.2, clr=C); r.via('GND', (50.8, 34.1), clr=C)
r.track('VBUS', B, [(37.43, 31.0), (38.63, 32.2), (44.2, 32.2), (44.5, 32.5), (44.5, 37.45)], 0.6, clr=C, note='feed to U11')
r.track('VBUS', B, [(44.5, 37.0), (46.1, 37.0)], 0.24, clr=C, note='neck at pin 1')
r.via('VBUS', (44.5, 37.45), clr=C); r.via('VBUS', (50.7, 37.75), clr=C); r.via('VBUS', (55.5, 36.51), clr=C)
r.track('VBUS', I1, [(44.5, 37.45), (50.4, 37.45), (50.7, 37.75), (51.45, 37.0), (55.01, 37.0), (55.5, 36.51)], 0.2, clr=C)
r.track('VBUS', B, [(50.7, 37.75), (50.7, 36.9)], 0.2, clr=C); r.track('VBUS', B, [(55.5, 36.51), (54.7, 36.51)], 0.2, clr=C)
r.track('ISET', B, [(48.9, 35.5), (49.5, 35.5), (49.5, 33.1), (49.7, 32.9), (53.4, 32.9), (53.8, 33.3), (53.8, 36.0), (53.42, 36.38), (52.8, 36.38)], 0.2, clr=C)
r.track('Net-(U11-dVdT)', B, [(48.9, 36.0), (49.9, 36.0), (49.9, 33.7), (50.3, 33.3), (51.9, 33.3), (52.1, 33.5), (52.1, 34.3), (52.38, 34.58), (52.8, 34.58)], 0.2, clr=C)
r.track('U11_RTN', B, [(52.8, 33.82), (53.2, 33.82), (53.4, 34.02), (53.4, 35.42), (53.2, 35.62), (52.8, 35.62)], 0.2, clr=C)
r.track('U11_RTN', B, [(52.8, 35.62), (52.12, 35.62), (52.12, 37.13), (52.32, 37.33), (52.8, 37.33)], 0.2, clr=C)
r.track('U11_RTN', B, [(52.12, 35.62), (51.9, 35.4)], 0.2, clr=C); r.via('U11_RTN', (51.9, 35.4), clr=C); r.via('U11_RTN', (47.3, 35.3), clr=C, note='in the thermal pad')
r.track('U11_RTN', I2, [(47.3, 35.3), (47.4, 35.4), (51.9, 35.4)], 0.2, clr=C)
r.track('Net-(U11-UVLO)', B, [(46.1, 36.5), (45.45, 36.5), (45.25, 36.3)], 0.2, clr=C)
r.via('Net-(U11-UVLO)', (45.25, 36.3), clr=C); r.via('Net-(U11-UVLO)', (53.6, 38.07), clr=C); r.via('Net-(U11-UVLO)', (55.5, 35.49), clr=C)
r.track('Net-(U11-UVLO)', I2, [(45.25, 36.3), (45.55, 36.0), (54.99, 36.0), (55.5, 35.49)], 0.2, clr=C)
r.track('Net-(U11-UVLO)', I2, [(51.53, 36.0), (53.6, 38.07)], 0.2, clr=C)
r.track('Net-(U11-UVLO)', B, [(53.6, 38.07), (52.8, 38.07)], 0.2, clr=C); r.track('Net-(U11-UVLO)', B, [(55.5, 35.49), (54.7, 35.49)], 0.2, clr=C)
r.track('PAYLOAD_EN', B, [(46.1, 35.5), (45.35, 35.5), (45.25, 35.4)], 0.2, clr=C)
r.via('PAYLOAD_EN', (45.25, 35.4), clr=C); r.via('PAYLOAD_EN', (55.6, 38.07), clr=C)
r.track('PAYLOAD_EN', I2, [(45.25, 35.4), (45.9, 34.75), (55.65, 34.75), (56.3, 35.4), (56.3, 37.37), (55.6, 38.07)], 0.2, clr=C)
r.track('PAYLOAD_EN', B, [(55.6, 38.07), (54.7, 38.07)], 0.2, clr=C)
n = r.report_bad()
r.finish(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None); r.summary()
sys.exit(1 if n else 0)
