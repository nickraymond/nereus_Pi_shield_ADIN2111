"""Stage 12, job 3 (re-review N4 / N9): the PWM pair's first bend moves away from the converter's feedback via. New-frame mm.
Usage: <KiCad python> job3_pwm.py <board> <stage-2c board> [log.json]

The pair (Internal 2, 0.2 mm, 0.33 mm pitch; MOTOR_IN1 west / outer, MOTOR_IN2 east / inner) comes south at x 6.75 / 7.08, turns 45 degrees to
x 9.35 / 9.68 and goes on south. The 45 degree piece passes south-west of the 5V_FB via (9.279, 8.267; 0.6 mm pad): MOTOR_IN2 at 0.163 mm.
The bend moves SHIFT = 0.50 mm south: both lanes keep their x, the 45 degree pieces lie 0.354 mm further from the via (MOTOR_IN2 0.52 mm,
MOTOR_IN1 0.85 mm), the pair stays parallel at 0.33 mm. Only the six pieces at the bend are replaced; nothing of the converter moves.
5V_FB has copper on Internal 2's neighbours (GND plane, PWR plane) only as this via."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage3_routing'))
import s3lib
I1, I2 = 'Internal 1', 'Internal 2'; SHIFT = float(os.environ.get('SHIFT', '0.5'))
D = 0.33 * 2 ** 0.5; a = 7.6 + D; b = round(7.0 - D + 0.33, 4); c = round(15.0 - D + 0.33, 4)      # stage 9's figures: MOTOR_IN2's corners
old = {'MOTOR_IN1': [(6.75, 1.5), (6.75, 7.0), (9.35, 9.6), (9.35, 15.0)], 'MOTOR_IN2': [(7.08, round(0.98 + a - 7.08, 4)), (7.08, b), (9.68, round(b + 2.6, 4)), (9.68, c)]}
new = {n: [p[0], (p[1][0], round(p[1][1] + SHIFT, 4)), (p[2][0], round(p[2][1] + SHIFT, 4)), p[3]] for n, p in old.items()}
rm = [(n, I2, (p[0], p[1], q[0], q[1]), 'seg') for n, pts in old.items() for p, q in zip(pts, pts[1:])]
s3lib.prestep(sys.argv[1], sys.argv[2], removes=rm)
r = s3lib.Router(sys.argv[1], '12 job 3'); C = 0.13
ROW = ('J15', 'J16', 'J17', 'J18', 'J19'); INNER = {(I2, 'J18.1'), (I1, 'J18.2')}
for L in (I1, I2, 'GND Plane', 'PWR Plane'):
    r.geo.L[L] = [e for e in r.geo.L[L] if not (e[4].startswith('pad J1') and e[4].split()[1].split('.')[0] in ROW and (L, e[4].split()[1]) not in INNER)]
for n in new: r.track(n, I2, new[n], 0.2, clr=C)
nb = r.report_bad()
r.finish(sys.argv[1], sys.argv[3] if len(sys.argv) > 3 else None); r.summary()
assert len(rm) == 6
sys.exit(1 if nb else 0)
