"""Stage 9: routing (stage 3's Router: pre-check, 0 / 45 / 90 only; all tracks 0.2 mm). New-frame mm.
Usage: <KiCad python> step3_route.py <board> <board out> [log.json]     (step2_sync.py --rip has removed the two nets' Internal 2 / Internal 1 copper)

Same corridor as stage 8, job 3 (north of the header, round the north-west corner, down the west part, east of the last P_IN via, diagonal to
U12), on Internal 2, two lanes at 0.33 mm pitch. The lanes are where they were from the header to the detour's south end; the nets on them
have changed places (stage 9: MOTOR_IN1 on J1 pin 33, MOTOR_IN2 on J1 pin 12), so the outer / west lane is MOTOR_IN1 and the pair reaches U12
in pad order (IN1 pad 1 west, IN2 pad 10 east): no swap, no vias but the two at U12, nothing on Internal 1.

 MOTOR_IN1  J1 pin 33 (49.01, 4.77), north between pins 32 / 34 (x 47.74), outer lane y 0.65, west lane x 6.75 past H1, 45 degrees to x 9.35,
            south to y 15.0, 45 degrees to x 15.8, south to y 23.3, 45 degrees (line x + y = 39.1, where MOTOR_IN1's last piece lay in stage 8)
            to x 4.4, south to y 37.5, 45 degrees into its via (3.7, 38.2).
 MOTOR_IN2  J1 pin 12 (21.07, 2.23), inner lane y 0.98, east lane x 7.08 / 9.68 / 16.13, 45 degrees beside MOTOR_IN1 (0.33 mm pitch) to
            x 6.0, south to y 37.0, 45 degrees into its via (7.0, 38.0).
The pair is parallel at 0.33 mm from x 20.52 on the north strip to (6.0, 33.57); from there the lanes go south 1.6 mm apart, through the two
gaps in U12's via field (x 3.95 .. 4.6 and 5.7 .. 6.2, stage 8). Stage 8's pieces on x + y = 40.0 / 40.9 are not rebuilt: the new pair lies
between x + y = 39.1 and 39.57, inside the old envelope."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage3_routing'))
import s3lib
I1, I2 = 'Internal 1', 'Internal 2'
r = s3lib.Router(sys.argv[1], '9'); C = 0.13
ROW = ('J15', 'J16', 'J17', 'J18', 'J19'); INNER = {(I2, 'J18.1'), (I1, 'J18.2')}      # the row's pads have copper on the outer layers only (stage 5)
for L in (I1, I2, 'GND Plane', 'PWR Plane'):
    r.geo.L[L] = [e for e in r.geo.L[L] if not (e[4].startswith('pad J1') and e[4].split()[1].split('.')[0] in ROW and (L, e[4].split()[1]) not in INNER)]
D = 0.33 * 2 ** 0.5           # shift along x (or y) of a 45 degree piece for a lane pitch of 0.33 mm
K = 39.1                      # the pair's last 45 degree piece: MOTOR_IN1 on x + y = K, MOTOR_IN2 on x + y = K + D
# west lane (outer): MOTOR_IN1; east lane (inner): MOTOR_IN2, its bends shifted so that the lanes stay 0.33 mm apart
r.track('MOTOR_IN1', I2, [(49.01, 4.77), (47.74, 3.5), (47.74, 1.5), (46.89, 0.65), (7.6, 0.65), (6.75, 1.5), (6.75, 7.0), (9.35, 9.6), (9.35, 15.0), (15.8, 21.45),
                          (15.8, K - 15.8), (4.4, K - 4.4), (4.4, 37.5), (3.7, 38.2)], 0.2, clr=C)
a = 7.6 + D; b = 7.0 - D + 0.33; c = 15.0 - D + 0.33
r.track('MOTOR_IN2', I2, [(21.07, 2.23), (21.07, 1.53), (20.52, 0.98), (a, 0.98), (7.08, 0.98 + a - 7.08), (7.08, b), (9.68, b + 2.6), (9.68, c), (16.13, c + 6.45),
                          (16.13, K + D - 16.13), (6.0, K + D - 6.0), (6.0, 37.0), (7.0, 38.0)], 0.2, clr=C)
n = r.report_bad()
r.finish(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None); r.summary()
sys.exit(1 if n else 0)
