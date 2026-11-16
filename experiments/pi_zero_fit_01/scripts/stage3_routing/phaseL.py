"""Stage 3 phase L (fourth session): TP24 ground, a second path for PI_5V, U12 VIN widened. Usage: <KiCad python> phaseL.py <in> <out> [log.json]

TP24 (GND test point, bottom, under J10's pads so no via fits at it): 0.2 mm on the bottom, 45 deg east, south at x 56.2 between the
       U11 group's via column (x 55.5) and the 1.0 mm VBUS_OUT track (x 57.6), into the ground via (55.5, 37.33) of phase H.
PI_5V  JP1 pad 1 -> J1 pins 4 / 2, a track on the bottom (1 oz) in parallel with the PWR-plane lane (0.5 oz):
       0.5 mm east out of JP1 pad 1 and north at x 12.09 (the one lane between the 5V_LIFEPO4 via / track at (11.3, 23.9) and the
       L_IN via row at y 22.16: 0.78 mm of room), 45 deg east, 1.0 mm north at x 13.45 (east of Sofar's ground polygon at
       (11.5..12.8, 14.4..15.8)), 0.5 mm 45 deg west and north between J1 pins 3 and 5 (x 12.18; the pads leave 0.84 mm),
       45 deg into pin 4; 0.6 mm pin 4 to pin 2.
       IPC-2221 outer layer, 1 oz, 10 degC rise (formula as docs/design-review/power_budget.md [IPC]): 0.5 mm 1.45 A, 0.6 mm 1.65 A, 1.0 mm 2.4 A.
U12    VIN: the 0.3 mm piece between the pin's 0.2 mm neck and C61 is now 0.4 mm (1.23 A at 10 degC; 0.5 mm would leave 0.10 mm to C61's
       ground pad), the 0.4 mm piece from C61 to the via 0.5 mm (1.45 A). Current limit 1.24 A.
"""
import sys, os, s3lib
T, B, I1, I2 = 'Top Layer', '6 Bottom Layer', 'Internal 1', 'Internal 2'
s3lib.prestep(sys.argv[1], os.environ['S3_BASE'], removes=[('5V_PI', B, (6.7, 37.0, 8.1, 38.0))])
r = s3lib.Router(sys.argv[1], 'L'); C = 0.13
# ---- body ----
r.track('GND', B, [(55.0, 34.0), (56.2, 35.2), (56.2, 36.9), (55.77, 37.33), (55.5, 37.33)], 0.2, clr=C, note='TP24')
r.track('PI_5V', B, [(9.2, 27.3), (11.49, 27.3), (12.09, 26.7), (12.09, 21.3), (13.45, 19.94)], 0.5, clr=C, note='second path, south part')
r.track('PI_5V', B, [(13.45, 19.94), (13.45, 8.27)], 1.0, clr=C, note='second path')
r.track('PI_5V', B, [(13.45, 8.27), (12.18, 7.0), (12.18, 3.5), (10.91, 2.23)], 0.5, clr=C, note='between J1 pins 3 and 5')
r.track('PI_5V', B, [(10.91, 2.23), (8.37, 2.23)], 0.6, clr=C, note='pin 4 to pin 2')
r.track('5V_PI', B, [(6.75, 37.15), (7.6, 37.15)], 0.4, clr=C, note='U12 VIN to C61')
r.track('5V_PI', B, [(7.6, 37.45), (8.05, 37.9)], 0.5, clr=C, note='C61 to the via into the PWR-plane fill')
# ---- end ----
n = r.report_bad()
r.finish(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None); r.summary()
sys.exit(1 if n else 0)
