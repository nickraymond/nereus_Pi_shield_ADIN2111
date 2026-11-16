"""Stage 4, step 3: routing of the GPIO pads and the test-point stubs, with stage 3's Router (pre-check, 0 / 45 / 90 only).
Usage: <KiCad python> step3_route.py <board> <board out> [log.json]     env S3_BASE = the stage-2c board (commit d30920b)

All 0.2 mm (the net class width). One lane per signal layer along the north edge at y 0.85, outside the header (the lane ADIN_TIMER
uses on Internal 1 west of pin 36), round the north-east corner at x 57.75 between J1's last column and the H2 screw keep-out:
  GPIO18  Top         J1 pin 12 north, east along y 0.85, south at x 57.75 into J12 pad 1                       no via
  GPIO19  Bottom      J1 pin 35, between pins 36 / 38 to y 0.85, corner, east of J12 pad 1 at x 58.8, J12 pad 2  no via
  GPIO17  Internal 2  J1 pin 11, between pins 12 / 14 to y 0.85, corner, south at x 59.2 past J5, J13 pad 1     no via
  GPIO20  Internal 1  J1 pin 38 north to y 0.85, corner, south at x 58.8 past J5, J13 pad 2                     no via
  GPIO14  Bottom      J1 pin 8, between pins 5 / 7 (x 14.72), south, J11 pad 1                                   no via
  GPIO15  Bottom      J1 pin 10, between pins 9 / 11 (x 19.8), J11 pad 2                                         no via
~ADC_ALERT (own stage-3 track, bottom): its piece x 17.29, y 6.07..11.77 ran through J11 pad 2's place; it now runs between the two pads
at x 16.57 and rejoins its own diagonal at (17.29, 11.77). J14's three GND pads take the GND-plane fill; no track.
Test points: 0.2 mm stubs from the net's own copper, bottom (TP40, TP41, TP43) or top (TP42).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage3_routing'))
import s3lib
T, B, I1, I2 = 'Top Layer', '6 Bottom Layer', 'Internal 1', 'Internal 2'
s3lib.prestep(sys.argv[1], os.environ['S3_BASE'], removes=[('~{ADC_ALERT}', B, (17.29, 6.07, 17.29, 11.77), 'seg')])
r = s3lib.Router(sys.argv[1], '4'); C = 0.13
r.track('GPIO14', B, [(15.99, 2.23), (14.72, 3.5), (14.72, 9.02), (15.3, 9.6)], 0.2, clr=C)
r.track('GPIO15', B, [(18.53, 2.23), (19.8, 3.5), (19.8, 6.2), (18.84, 7.16), (18.84, 8.6), (17.84, 9.6)], 0.2, clr=C)
r.track('~{ADC_ALERT}', B, [(17.29, 6.07), (17.29, 6.4), (16.57, 7.12), (16.57, 11.05), (17.29, 11.77)], 0.2, clr=C, note='moved between the J11 pads')
r.track('GPIO18', T, [(21.07, 2.23), (21.07, 1.4), (21.62, 0.85), (57.3, 0.85), (57.75, 1.3), (57.75, 7.4)], 0.2, clr=C)
r.track('GPIO19', B, [(51.55, 4.77), (52.82, 3.5), (52.82, 1.4), (53.37, 0.85), (57.3, 0.85), (57.75, 1.3), (57.75, 4.8), (58.8, 5.85), (58.8, 8.84), (57.7, 9.94)], 0.2, clr=C)
r.track('GPIO17', I2, [(21.07, 4.77), (22.34, 3.5), (22.34, 1.4), (22.89, 0.85), (57.3, 0.85), (57.75, 1.3), (57.75, 4.8), (59.2, 6.25), (59.2, 16.45), (60.6, 17.85), (62.6, 17.85)], 0.2, clr=C)
r.track('GPIO20', I1, [(54.09, 2.23), (54.09, 1.4), (54.64, 0.85), (57.3, 0.85), (57.75, 1.3), (57.75, 4.8), (58.8, 5.85), (58.8, 18.59), (60.6, 20.39), (62.6, 20.39)], 0.2, clr=C)
r.track('MOTOR_IN1', B, [(3.7, 37.85), (2.2, 37.85)], 0.2, clr=C, note='TP40')
r.track('MOTOR_OUT1', B, [(2.75, 35.5), (2.5, 35.5)], 0.2, clr=C, note='TP41')
r.track('MOTOR_OUT2', T, [(8.35, 34.105), (8.35, 31.605)], 0.2, clr=C, note='TP42')
r.track('I2C0_SCL', B, [(30.6, 33.8), (31.13, 33.27)], 0.2, clr=C, note='TP43')
n = r.report_bad()
r.finish(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None); r.summary()
sys.exit(1 if n else 0)
