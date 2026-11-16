"""Stage 3 phase J (third session): motor driver group re-placed and routed. Usage: <KiCad python> phaseJ.py <in> <out> [log.json]

Why: with U12 as placed, OUT1 left the part to the south and OUT2 to the north, and J7's pads (top) sit above the capacitor row, so
the two outputs could not reach J7 without crossing. Here U12 is turned so that OUT1 (pin 2) faces west and OUT2 (pin 8) faces east,
the same order as J7's pins 1-2 / 3-4, and stands just south of J7's pad row:
  U12   (6.3, 37.2) -> (5.2, 36.9), turned 90 deg. West pins N->S: V3P3, GND, OUT1, IN1. East: ISET, OUT2, VIN, IN2. North: (nc), VCC. South: nSLEEP, VISEN.
  OUT1  0.2 mm for 0.15 mm past the pad, then a 0.6 mm bar north at x 3.4 to two vias (2.75, 35.5) (3.4, 35.5); top: 0.6 mm bar y 35.5 into J7 pads 1 and 2.
  OUT2  0.2 mm neck 0.45 mm, 0.5 mm bar north at x 6.95, 0.6 mm to two vias (6.75, 35.5) (7.4, 35.5); top: 0.6 mm bar y 35.5 into J7 pads 3 and 4.
        1 oz outer copper, 10 degC rise, IPC-2221 as power_budget.md s.4: 0.5 mm = 1.45 A, 0.6 mm = 1.65 A (limit 1.24 A).
  GND   pin 3: one via between the pad rows of U12 (5.15, 36.75), into the GND plane.
  VIN   pin 9: 0.2 mm 0.2 mm long, 0.3 mm to C61 (100 nF, 0.8 mm from the pad), 0.4 mm to a via (8.05, 37.9) into the 5V_PI fill of the PWR plane
        (0.1 mm under the bottom layer). C61's ground: its own via (8.0, 36.25).
  Bulk  C62, C66 (22 uF) and C60 (10 uF) in a row north of J7's pads on a 1.0 mm 5V_PI rail (y 30.1, fed by the phase C trunk and two more
        vias into the PWR-plane fill), ground pads on a 0.5 mm rail (y 32.0) with two vias. 6 mm from VIN through the plane.
  C64 (V3P3), C63 (VCC), R48 (ISET): in a row north of U12, north of their pins (C63 0.3 mm west of VCC so the courtyards clear); their ground ends run north onto the ground rail.
  Signals: IN1 via (3.7, 38.2), Internal 2 y 37.35 to its trunk (y 38.05); IN2 via (6.8, 37.9), Internal 2 to its trunk (y 38.6);
        VISEN bottom lane y 38.55, north at x 8.6, via (8.6, 36.75), Internal 2 45 deg to its trunk (y 34.55); nSLEEP bottom to a via (4.4, 38.62) (phase K takes it on).
Removes stage-3 copper of the group's nets only (uuid check against d30920b, $S3_BASE).
"""
import sys, os, s3lib
T, B, I1, I2 = 'Top Layer', '6 Bottom Layer', 'Internal 1', 'Internal 2'
BOX = (0.0, 29.9, 11.0, 39.5); WIDE = (0.0, 29.9, 35.0, 39.5)
s3lib.prestep(sys.argv[1], os.environ['S3_BASE'],
    removes=[('GND', '*', BOX), ('5V_PI', B, BOX), ('MOTOR_IN1', '*', WIDE), ('MOTOR_IN2', '*', BOX), ('MOTOR_VISEN', '*', WIDE),
             ('Net-(U12-ISET)', '*'), ('Net-(U12-VCC)', '*'), ('Net-(U12-V3P3)', '*')],
    moves=[('U12', (5.2, 36.9), 2, (4.321, 37.15)), ('C62', (4.4, 31.05), 1, (4.4, 30.1)), ('C66', (7.5, 31.05), 1, (7.5, 30.1)),
           ('C60', (9.4, 31.2), 1, (9.4, 30.632)), ('C61', (7.6, 36.92), 1, (7.6, 37.299)), ('C63', (5.17, 34.32), 1, (5.17, 34.699)),
           ('R48', (6.15, 34.32), 1, (6.15, 34.699)), ('C64', (3.95, 34.0), 1, (3.95, 34.568))])
r = s3lib.Router(sys.argv[1], 'J'); C = 0.13
# --- outputs
r.track('MOTOR_OUT1', B, [(4.3, 37.15), (3.4, 37.15)], 0.2, clr=C, note='neck')
r.track('MOTOR_OUT1', B, [(3.4, 37.15), (3.4, 35.5), ], 0.6, clr=C); r.track('MOTOR_OUT1', B, [(2.75, 35.5), (3.4, 35.5)], 0.6, clr=C)
r.via('MOTOR_OUT1', (2.75, 35.5), clr=C); r.via('MOTOR_OUT1', (3.4, 35.5), clr=C)
r.track('MOTOR_OUT1', T, [(2.75, 35.5), (5.85, 35.5)], 0.6, clr=C); r.track('MOTOR_OUT1', T, [(4.6, 35.5), (4.6, 34.5)], 0.6, clr=C); r.track('MOTOR_OUT1', T, [(5.85, 35.5), (5.85, 34.5)], 0.6, clr=C)
r.track('MOTOR_OUT2', B, [(6.1, 36.65), (6.75, 36.65), (6.95, 36.45)], 0.2, clr=C, note='neck')
r.track('MOTOR_OUT2', B, [(6.95, 36.45), (6.95, 35.5)], 0.5, clr=C); r.track('MOTOR_OUT2', B, [(6.75, 35.5), (7.4, 35.5)], 0.6, clr=C)
r.via('MOTOR_OUT2', (6.75, 35.5), clr=C); r.via('MOTOR_OUT2', (7.4, 35.5), clr=C)
r.track('MOTOR_OUT2', T, [(6.75, 35.5), (8.35, 35.5)], 0.6, clr=C); r.track('MOTOR_OUT2', T, [(7.1, 35.5), (7.1, 34.5)], 0.6, clr=C); r.track('MOTOR_OUT2', T, [(8.35, 35.5), (8.35, 34.5)], 0.6, clr=C)
# --- ground pin, VIN, C61
r.track('GND', B, [(4.3, 36.65), (5.05, 36.65), (5.15, 36.75)], 0.2, clr=C); r.via('GND', (5.15, 36.75), clr=C)
r.track('5V_PI', B, [(6.1, 37.15), (6.75, 37.15)], 0.2, clr=C, note='neck'); r.track('5V_PI', B, [(6.75, 37.15), (7.6, 37.15)], 0.3, clr=C)
r.track('5V_PI', B, [(7.6, 37.45), (8.05, 37.9)], 0.4, clr=C); r.via('5V_PI', (8.05, 37.9), clr=C)
r.track('GND', B, [(7.7, 36.55), (8.0, 36.25)], 0.3, clr=C); r.via('GND', (8.0, 36.25), clr=C)
# --- bulk capacitors: 5 V rail y 30.1, ground rail y 32.0
r.track('5V_PI', B, [(6.6, 30.15), (6.65, 30.1)], 1.0, clr=C); r.track('5V_PI', B, [(4.4, 30.1), (7.5, 30.1)], 1.0, clr=C)
r.track('5V_PI', B, [(7.5, 30.1), (8.87, 30.1), (9.4, 30.63)], 0.5, clr=C)
r.via('5V_PI', (5.5, 30.1), clr=C); r.via('5V_PI', (6.1, 30.1), clr=C)
r.track('GND', B, [(4.4, 32.0), (7.5, 32.0)], 0.5, clr=C); r.via('GND', (5.8, 32.0), clr=C); r.via('GND', (6.5, 32.0), clr=C)
r.track('GND', B, [(7.5, 32.0), (9.17, 32.0), (9.4, 31.77)], 0.3, clr=C)
# --- C64, C63, R48
r.track('Net-(U12-V3P3)', B, [(3.95, 36.15), (3.95, 34.57)], 0.2, clr=C); r.track('GND', B, [(3.95, 33.43), (3.95, 32.2)], 0.25, clr=C)
r.track('Net-(U12-VCC)', B, [(5.45, 35.9), (5.45, 35.1), (5.25, 34.9)], 0.2, clr=C); r.track('GND', B, [(5.17, 33.94), (5.17, 32.0)], 0.25, clr=C)
r.track('Net-(U12-ISET)', B, [(6.15, 36.15), (6.15, 34.7)], 0.2, clr=C); r.track('GND', B, [(6.15, 33.94), (6.15, 32.0)], 0.25, clr=C)
# --- signals
r.track('MOTOR_IN1', B, [(4.2, 37.65), (3.9, 37.65), (3.7, 37.85), (3.7, 38.2)], 0.2, clr=C); r.via('MOTOR_IN1', (3.7, 38.2), clr=C)
r.track('MOTOR_IN1', I2, [(3.7, 38.2), (4.55, 37.35), (9.6, 37.35), (10.3, 38.05), (34.2, 38.05)], 0.2)
r.track('MOTOR_IN2', B, [(6.2, 37.65), (6.55, 37.65), (6.8, 37.9)], 0.2, clr=C); r.via('MOTOR_IN2', (6.8, 37.9), clr=C)
r.track('MOTOR_IN2', I2, [(6.8, 37.9), (7.5, 38.6), (8.1, 38.6)], 0.2)
r.track('MOTOR_VISEN', B, [(5.45, 38.15), (5.45, 38.35), (5.65, 38.55), (8.4, 38.55), (8.6, 38.35), (8.6, 36.75)], 0.2, clr=C); r.via('MOTOR_VISEN', (8.6, 36.75), clr=C)
r.track('MOTOR_VISEN', I2, [(8.6, 36.75), (10.8, 34.55), (21.6, 34.55)], 0.2); r.via('MOTOR_VISEN', (21.6, 34.55)); r.track('MOTOR_VISEN', B, [(21.6, 34.55), (22.8, 34.55)], 0.2)
r.track('MOTOR_nSLEEP', B, [(4.95, 38.15), (4.95, 38.42), (4.75, 38.62), (4.4, 38.62)], 0.2, clr=C); r.via('MOTOR_nSLEEP', (4.4, 38.62), clr=C)
n = r.report_bad()
r.finish(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None); r.summary()
sys.exit(1 if n else 0)
