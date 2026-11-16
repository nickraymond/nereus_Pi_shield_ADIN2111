"""Stage 5, step 4: three fixes from the manufacturability review. Usage: <KiCad python> step4_review.py <board> <board out> [log.json]   env S3_BASE

1. Via holes of our own making inside or at exposed pads (list: via_in_pad.py, before / after in the NereusData folder).
   Moved, to 0.3 mm or more between the hole and the pad's copper:
     TP41            the test point moves, not the vias: (2.5, 35.5) -> (2.2, 34.2); it sat on the two MOTOR_OUT1 vias (2.75 / 3.4, 35.5)
     C66 pad 1       5V_PI vias (7.15, 28.6) and (7.15, 29.45) -> (7.15, 28.25) and (7.15, 29.1), same 1.0 mm track
     C62 / C66 rails 5V_PI vias (5.5 / 6.1, 30.1) -> (5.65 / 6.25, 30.1); GND vias (5.8 / 6.5, 32.0) -> (5.65 / 6.25, 32.0): centred between the two capacitors
     L6 pad 2        5V_PI via (1.346, 12.8) -> (1.346, 12.55), same track
     U12 pad 10      MOTOR_IN2 via (6.8, 37.9) -> (7.0, 38.0), with its two stubs
   Left (no site within 1.2 mm passes the pre-check and the 0.3 mm pad rule; viasites.py in the NereusData folder):
     C61 pad 1 5V_PI via (8.05, 37.9), C61 pad 2 GND via (8.0, 36.25), U12 pad 3 GND via (5.15, 36.75), U11 pad 11 via (47.3, 35.3) in the exposed pad.
   Carried from the frozen board (not ours, not touched): F1 pad 1 (4.267, 15.887), C57 pad 1 (3.4, 8.137) and (3.4, 10.057), and the rest of via_in_pad.py's "carried" list.
2. C62: 0.22 mm south, to (4.4, 31.27): its courtyard was 0.145 mm inside the south-west screw keep-out (r 3.0), now 0.075 mm outside.
   C64 goes 0.12 mm south, to (3.95, 34.12), to keep the two courtyards apart (0.07 mm; C64 to U12 0.09 mm). No track is changed:
   every track still ends inside its pad (the 1.0 mm 5V_PI rail and the 0.5 mm GND rail are shared with C66 and stay straight).
3. TP40: 0.4 mm north, to (2.2, 37.45) (the place TP41 left): courtyard to the corner arc 0.19 -> 0.49 mm.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage3_routing'))
import s3lib
T, B, I1, I2 = 'Top Layer', '6 Bottom Layer', 'Internal 1', 'Internal 2'
s3lib.prestep(sys.argv[1], os.environ['S3_BASE'],
    removes=[('MOTOR_OUT1', B, (2.75, 35.5, 2.5, 35.5), 'seg'), ('MOTOR_IN1', B, (3.7, 37.85, 2.2, 37.85), 'seg'),
             ('5V_PI', '*', (7.1, 28.5, 7.2, 29.5)), ('5V_PI', '*', (1.3, 12.75, 1.4, 12.85)), ('5V_PI', '*', (5.4, 30.05, 6.2, 30.15)),
             ('GND', '*', (5.7, 31.95, 6.6, 32.05)), ('MOTOR_IN2', '*', (6.5, 37.6, 7.55, 38.65))],
    moves=[('C62', (4.4, 31.27)), ('C64', (3.95, 34.12)), ('TP40', (2.2, 37.45)), ('TP41', (2.2, 34.2))])
r = s3lib.Router(sys.argv[1], '5 review'); C = 0.13
for p in ((7.15, 28.25), (7.15, 29.1), (5.65, 30.1), (6.25, 30.1), (1.346, 12.55)): r.via('5V_PI', p, clr=C)
for p in ((5.65, 32.0), (6.25, 32.0)): r.via('GND', p, clr=C)
r.via('MOTOR_IN2', (7.0, 38.0), clr=C)
r.track('MOTOR_IN2', B, [(6.55, 37.65), (6.65, 37.65), (7.0, 38.0)], 0.2, clr=C)
r.track('MOTOR_IN2', I2, [(7.0, 38.0), (7.0, 38.1), (7.5, 38.6)], 0.2, clr=C)
r.track('MOTOR_OUT1', B, [(2.75, 35.5), (2.75, 34.75), (2.2, 34.2)], 0.2, clr=C, note='TP41')
r.track('MOTOR_IN1', B, [(3.7, 37.85), (2.6, 37.85), (2.2, 37.45)], 0.2, clr=C, note='TP40')
n = r.report_bad()
r.finish(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None); r.summary()
sys.exit(1 if n else 0)
