"""Stage 8, job 3: routing (stage 3's Router: pre-check, 0 / 45 / 90 only; all tracks 0.2 mm). New-frame mm.
Usage: <KiCad python> job3_route.py <board> <board out> [log.json]     (job3_sync.py --rip has removed the old Internal 2 copper)

Both PWM lines leave the header to the north, run west along the strip between the board edge and J1's northern pin row, turn south between
H1's keep-out and J1 pins 1 / 2, and go down the west part of the board to U12, on Internal 2 (GND plane above, PWR plane below), as a
two-lane bus at 0.33 mm pitch. Their vias at U12 ((3.7, 38.2) and (7.0, 38.0)) and the bottom pieces there stay.

 GPIO12     J1 pin 32 (46.47, 2.23), 45 degrees into the lane between the pin rows (y 3.5), south between pins 27 / 29 (x 42.66), 45 degrees
            into J18 pad 1 (41.39, 6.70): the mirror image of the GPIO18 piece it replaces (that one came from the west).
 MOTOR_IN2  J1 pin 33 (49.01, 4.77), north between pins 32 / 34 (x 47.74), outer lane y 0.65 (0.55 mm from the edge; rule 0.5), west lane
            x 6.75 past H1 (keep-out r 3.0 reaches x 6.5), 45 degrees to x 9.35 (west of the VBUS feed, x 9.98, and of the 5V_FB via (9.28, 8.27)),
            south to y 15.0, 45 degrees to x 15.8, south to y 24.2, 45 degrees to x 6.0, south to y 37.0, 45 degrees into its via.
 MOTOR_IN1  J1 pin 12 (21.07, 2.23), inner lane y 0.98, east lane x 7.08 / 9.68 / 16.13 beside MOTOR_IN2, then the swap (below), 45 degrees
            to x 4.4, south to y 37.5, 45 degrees into its via.
Why the detour to x 15.8 / 16.13: on Internal 2 the 2.0 mm 5V_LIFEPO4 track (stage 6) lies across the west side from (4.27, 15.9) to (11.3, 23.9),
with J4's pads and H4's keep-out west of it; east of it the four P_IN vias (12.78 .. 15.18, 22.16; 0.8 mm pitch) leave 0.25 mm between the
track's edge (12.3) and the first via: no lane. The first clear lane is east of the last via (x 15.71 or more).
Why the swap: the lane order is fixed at the header (MOTOR_IN2 passes north of pin 12, so MOTOR_IN1 is the inner lane = the east lane on the
west side), and U12 wants the opposite (IN1 pad 1 west, IN2 pad 10 east; both lanes reach it from the north through the two gaps in its via
field, x 3.95 .. 4.6 and 5.7 .. 6.2). MOTOR_IN1 therefore crosses MOTOR_IN2 once: via (14.1, 26.8), 1.27 mm on Internal 1, via (13.2, 25.9),
between the two BM2 trunks on the top layer. No site for a via passes the six-layer pre-check nearer U12 (x 5 .. 8, y 31.5 .. 34 scanned).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage3_routing'))
import s3lib
T, B, I1, I2 = 'Top Layer', '6 Bottom Layer', 'Internal 1', 'Internal 2'
r = s3lib.Router(sys.argv[1], '8 job 3'); C = 0.13
ROW = ('J15', 'J16', 'J17', 'J18', 'J19'); INNER = {(I2, 'J18.1'), (I1, 'J18.2')}      # the row's pads have copper on the outer layers only (stage 5)
for L in (I1, I2, 'GND Plane', 'PWR Plane'):
    r.geo.L[L] = [e for e in r.geo.L[L] if not (e[4].startswith('pad J1') and e[4].split()[1].split('.')[0] in ROW and (L, e[4].split()[1]) not in INNER)]
r.track('GPIO12', I2, [(46.47, 2.23), (45.2, 3.5), (43.16, 3.5), (42.66, 4.0), (42.66, 5.43), (41.39, 6.7)], 0.2, clr=C)
D = 0.33 * 2 ** 0.5           # shift along x (or y) of a 45 degree piece for a lane pitch of 0.33 mm
# west lane (outer): MOTOR_IN2; east lane (inner): MOTOR_IN1, its bends shifted by D so that the lanes stay 0.33 mm apart
r.track('MOTOR_IN2', I2, [(49.01, 4.77), (47.74, 3.5), (47.74, 1.5), (46.89, 0.65), (7.6, 0.65), (6.75, 1.5), (6.75, 7.0), (9.35, 9.6), (9.35, 15.0), (15.8, 21.45),
                          (15.8, 24.2), (6.0, 34.0), (6.0, 37.0), (7.0, 38.0)], 0.2, clr=C)
a = 7.6 + D; b = 7.0 - D + 0.33; c = 15.0 - D + 0.33
r.track('MOTOR_IN1', I2, [(21.07, 2.23), (21.07, 1.53), (20.52, 0.98), (a, 0.98), (7.08, 0.98 + a - 7.08), (7.08, b), (9.68, b + 2.6), (9.68, c), (16.13, c + 6.45),
                          (16.13, 24.77), (14.1, 26.8)], 0.2, clr=C)
r.via('MOTOR_IN1', (14.1, 26.8), clr=C, note='swap: MOTOR_IN1 crosses MOTOR_IN2 on Internal 1')
r.track('MOTOR_IN1', I1, [(14.1, 26.8), (13.2, 25.9)], 0.2, clr=C)
r.via('MOTOR_IN1', (13.2, 25.9), clr=C)
r.track('MOTOR_IN1', I2, [(13.2, 25.9), (4.4, 34.7), (4.4, 37.5), (3.7, 38.2)], 0.2, clr=C)
n = r.report_bad()
r.finish(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None); r.summary()
sys.exit(1 if n else 0)
