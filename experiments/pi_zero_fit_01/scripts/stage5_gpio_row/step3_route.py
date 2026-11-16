"""Stage 5, step 3: the channel between J1 and the mote core is re-routed round the pad row (y 6.70), with stage 3's Router
(pre-check, 0 / 45 / 90 only). Usage: <KiCad python> step3_route.py <board> <board out> [log.json]    env S3_BASE = the stage-2c board

Only stage 3 / 4's own tracks are removed (prestep refuses anything that is in the stage-2c board). All signal tracks 0.2 mm.
Rules used for the plan: an inner-layer track stays 0.9 mm from a row hole's centre (0.5 hole + 0.3 JLC hole-to-copper + 0.1), an
outer-layer track 1.08 mm from a row pad's centre (0.85 + 0.127 + 0.1). A net that starts at a J1 pin with a row pad right under it
leaves the pin at 45 degrees into the gap beside the pad (x = pin +/- 1.27) and goes south there. East-west lanes south of the row
are at y 7.8 / 8.2 (8.15 / 8.5 on the top layer, which has three).

West (x 10..30)
  PI_5V     bottom   J15 pad 1 joins the 0.5 mm path at x 12.18 (0.5 mm), and takes the PI_5V lane on the PWR plane; the path's 45 degree piece moves 0.6 mm south, clear of J15 pad 2 (GND)
  GPIO14/15 bottom   J1 pin 8 / 10, between the pins (x 14.72 / 19.8), 45 degrees into J15 pad 3 / 4
  ~ADC_ALERT bottom  J1 pin 7, 45 degrees to x 17.29, straight south between pads 3 / 4 (stage 3's lane; stage 4's detour and via go)
  I2C3_SCL / I2C3_SDA / ADIN_MISO  Internal 1   the three-lane bus keeps y 6.65 / 7.05 / 7.45 east of x 20 (north of Sofar's vias at
            (22.28, 8.32) and (23.73, 8.06)) and steps 0.95 mm south at x 19..20.3, to y 7.6 / 8.0 / 8.4 under J15's holes.
            SDA leaves pin 15 at 45 degrees (J16 pad 1 is under it). MISO passes under J16 pad 1 at y 7.6 (a 0.15 mm step at x 25.4).
  VBUS      Internal 2, 1.0 mm (unchanged width)  y 8.1 under J15 and J16's holes, y 7.1 (the old lane) between x 21.0 and 24.2
            where the same two vias leave no room south of it
  PI_3V3    the link pin 1 - pin 17 moves from the top layer to Internal 2 (same lane between the pin rows, y 3.5), to let GPIO17
            out of pin 11 on the top layer; J16 pads 1-2 from pin 17 on the bottom, 0.5 mm; the Internal 2 run south leaves pin 17
            between J16 pads 2 / 3 at x 30.3
Middle and east (x 30..60)
  GPIO17    top         pin 11, between pins 11 / 13, lane y 0.85 north of the header (stage 4's lane), south between pins 23 / 25, J16 pad 5
  GPIO18    Internal 2  pin 12, lane y 0.85, south between pins 25 / 27 (x 40.12), J17 pad 1
  GPIO7     Internal 1  pin 26, between the pin rows (y 3.5) to x 42.66, south between pins 27 / 29, J17 pad 2
  GPIO19 / 20 / 21  bottom   45 degrees from pin 35 into J18 pad 1; pins 38 / 40 between the pins (x 55.36 / 57.9) into pads 2 / 3
  ADIN_MOSI Internal 1  pin 19 (J16 pad 3 under it): 45 degrees to x 29.96, lane y 8.2
  ~ADIN_INT Internal 1  lane y 7.8          ~ADIN_CS  Internal 2  lane y 8.2        ADIN_SCK  Internal 2  pin 23: 45 degrees to x 37.58, lane y 7.8
  ADIN_MISO top   pin 21: 45 degrees to x 35.04, lane y 8.5       I2C0_SCL top  x 40.12, lane y 8.15       I2C0_SDA top  pin 27: 45 degrees to x 42.66, lane y 7.8
  ~PAYLOAD_FAULT / MOTOR_IN2 / PAYLOAD_EN  Internal 2  pins 31 / 33 / 37: 45 degrees to x 47.74 / 50.28 / 55.36, back to the old lane south of the row
Not touched: ADIN_PWR, ~ADIN_RST, MOTOR_IN1, MOTOR_nSLEEP, ADIN_TIMER, the two short GND tracks (they pass between the pads as they are).
GND pads (J16 3-4, J17 3-4) take the GND plane; no track. FID5 / FID6 back to (62.2, 33.0).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage3_routing'))
import s3lib
T, B, I1, I2 = 'Top Layer', '6 Bottom Layer', 'Internal 1', 'Internal 2'
G = ['GPIO14', 'GPIO15', 'GPIO17', 'GPIO18', 'GPIO19', 'GPIO20']
rm = [(g, '*') for g in G] + [
    ('~{ADC_ALERT}', '*', (15, 4, 18, 12)),
    ('ADIN_MISO', T, (33, 4, 45, 10.4)), ('ADIN_MISO', I1, (11, 4, 28, 12.1)),
    ('ADIN_MOSI', I1, (30, 4, 46, 12.2)),
    ('I2C3_SCL', I1, (9, 6, 23.1, 7.3)), ('I2C3_SCL', I1, (9.83, 7.25, 9.83, 37.29), 'seg'),
    ('I2C3_SDA', I1, (10, 4, 27, 7.7)), ('I2C3_SDA', I1, (10.19, 7.65, 10.19, 37.14), 'seg'),
    ('~{ADIN_INT}', I1, (35, 3.4, 47.3, 9.8)),
    ('ADIN_SCK', I2, (36, 4, 44.3, 12.1)), ('~{ADIN_CS}', I2, (35, 3.4, 43.8, 12.6)),
    ('MOTOR_IN2', I2, (49.5, 28.1, 49.5, 5.26), 'seg'), ('MOTOR_IN2', I2, (49.5, 5.26, 49.01, 4.77), 'seg'),
    ('PAYLOAD_EN', I2, (54.09, 4.77, 54.09, 34.75), 'seg'),
    ('~{PAYLOAD_FAULT}', I2, (46.45, 4.79, 46.47, 4.77), 'seg'), ('~{PAYLOAD_FAULT}', I2, (46.45, 19.3, 46.45, 4.79), 'seg'),
    ('PI_3V3', T, (8, 3, 29, 5)), ('PI_5V', B, (13.45, 8.27, 12.18, 7.0), 'seg'),
    ('VBUS', I2, (10, 7, 30.1, 12.8)),
    ('I2C0_SCL', T, (40, 2, 46, 10.4)), ('I2C0_SDA', T, (41, 4, 46.3, 10.4)),
]
s3lib.prestep(sys.argv[1], os.environ['S3_BASE'], removes=rm, moves=[('FID5', (62.2, 33.0)), ('FID6', (62.2, 33.0))])
r = s3lib.Router(sys.argv[1], '5'); C = 0.13; Y = 6.7
# the row's pads have copper on the outer layers only, and on an inner layer where a track of this script ends on them
ROW = {'J15': (10.91, 4), 'J16': (26.15, 2), 'J17': (33.77, 2), 'J18': (41.39, 4), 'J19': (54.09, 3)}
INNER = {(I2, 'J18.1'), (I1, 'J18.2')}
for L in (I1, I2, 'GND Plane', 'PWR Plane'):
    r.geo.L[L] = [e for e in r.geo.L[L] if not (e[4].startswith('pad J1') and e[4].split()[1].split('.')[0] in ROW and (L, e[4].split()[1]) not in INNER)]
P = lambda ref, n: (round(ROW[ref][0] + 2.54 * (n - 1), 4), Y)
# ---- west
r.track('PI_5V', B, [P('J15', 1), (12.18, 6.7)], 0.5, clr=C, note='J15 pad 1 to the path at x 12.18')
r.track('PI_5V', B, [(12.18, 7.0), (12.18, 7.6), (12.85, 8.27), (13.45, 8.27)], 0.5, clr=C, note='0.6 mm further south, clear of J15 pad 2 (GND)')
r.track('GPIO14', B, [(15.99, 2.23), (14.72, 3.5), (14.72, 5.43), P('J15', 3)], 0.2, clr=C)
r.track('GPIO15', B, [(18.53, 2.23), (19.8, 3.5), (19.8, 5.43), P('J15', 4)], 0.2, clr=C)
r.track('~{ADC_ALERT}', B, [(15.99, 4.77), (17.29, 6.07), (17.29, 11.77)], 0.2, clr=C)
r.track('I2C3_SCL', I1, [(23.01, 6.65), (19.95, 6.65), (19.0, 7.6), (10.43, 7.6), (9.83, 8.2), (9.83, 37.29)], 0.2, clr=C)
r.track('I2C3_SDA', I1, [(26.15, 4.77), (23.87, 7.05), (20.116, 7.05), (19.166, 8.0), (10.79, 8.0), (10.19, 8.6), (10.19, 37.14)], 0.2, clr=C)
r.track('ADIN_MISO', I1, [(27.42, 4.1), (27.42, 7.0), (26.82, 7.6), (25.5, 7.6), (25.35, 7.45), (20.28, 7.45), (19.33, 8.4), (12.2, 8.4), (11.6, 9.0), (11.6, 12.0)], 0.2, clr=C)
r.track('VBUS', I2, [(10.726, 10.688), (10.726, 9.1), (11.726, 8.1), (20.0, 8.1), (21.0, 7.1), (24.2, 7.1), (25.2, 8.1), (29.2, 8.1), (29.981, 8.881), (29.981, 12.764)], 1.0, clr=C)
r.track('PI_3V3', I2, [(8.37, 4.77), (9.64, 3.5), (27.42, 3.5), (28.69, 4.77)], 0.2, clr=C, note='link pin 1 - pin 17, was on the top layer')
r.track('PI_3V3', B, [(28.69, 4.77), P('J16', 2), P('J16', 1)], 0.5, clr=C)
# ---- middle and east
r.track('GPIO17', T, [(21.07, 4.77), (22.34, 3.5), (22.34, 1.4), (22.89, 0.85), (37.03, 0.85), (37.58, 1.4), (37.58, 5.43), P('J17', 2)], 0.2, clr=C)
r.track('GPIO18', I2, [(21.07, 2.23), (21.07, 1.4), (21.62, 0.85), (39.57, 0.85), (40.12, 1.4), (40.12, 5.43), P('J18', 1)], 0.2, clr=C)
r.track('GPIO7', I1, [(38.85, 2.23), (40.12, 3.5), (42.16, 3.5), (42.66, 4.0), (42.66, 5.43), P('J18', 2)], 0.2, clr=C)
r.track('GPIO19', B, [(51.55, 4.77), (53.48, 6.7), P('J19', 1)], 0.2, clr=C)
r.track('GPIO20', B, [(54.09, 2.23), (55.36, 3.5), (55.36, 5.43), P('J19', 2)], 0.2, clr=C)
r.track('GPIO21', B, [(56.63, 2.23), (57.9, 3.5), (57.9, 5.43), P('J19', 3)], 0.2, clr=C)
r.track('ADIN_MOSI', I1, [(31.23, 4.77), (31.23, 7.2), (32.23, 8.2), (44.368, 8.2), (45.268, 9.1), (45.268, 12.163)], 0.2, clr=C)
r.track('~{ADIN_INT}', I1, [(35.04, 3.5), (35.04, 6.9), (35.94, 7.8), (46.381, 7.8), (47.281, 8.7), (47.281, 9.7)], 0.2, clr=C)
r.track('~{ADIN_CS}', I2, [(35.04, 3.5), (35.04, 7.2), (36.04, 8.2), (42.881, 8.2), (43.781, 9.1), (43.781, 12.514)], 0.2, clr=C)
r.track('ADIN_SCK', I2, [(36.31, 4.77), (37.58, 6.04), (37.58, 7.3), (38.08, 7.8), (43.381, 7.8), (44.281, 8.7), (44.281, 12.045)], 0.2, clr=C)
r.track('ADIN_MISO', T, [(33.77, 4.77), (35.04, 6.04), (35.04, 7.5), (36.04, 8.5), (44.431, 8.5), (44.781, 8.85), (44.781, 10.289)], 0.2, clr=C)
r.track('I2C0_SCL', T, [(41.39, 2.23), (40.12, 3.5), (40.12, 7.35), (40.92, 8.15), (45.431, 8.15), (45.781, 8.5), (45.781, 10.289)], 0.2, clr=C)
r.track('I2C0_SDA', T, [(41.39, 4.77), (42.66, 6.04), (42.66, 7.4), (43.06, 7.8), (45.881, 7.8), (46.281, 8.2), (46.281, 10.289)], 0.2, clr=C)
r.track('~{PAYLOAD_FAULT}', I2, [(46.47, 4.77), (47.74, 6.04), (47.74, 7.0), (46.45, 8.29), (46.45, 19.3)], 0.2, clr=C)
r.track('MOTOR_IN2', I2, [(49.01, 4.77), (50.28, 6.04), (50.28, 7.7), (49.5, 8.48), (49.5, 28.1)], 0.2, clr=C)
r.track('PAYLOAD_EN', I2, [(54.09, 4.77), (55.36, 6.04), (55.36, 7.7), (54.09, 8.97), (54.09, 34.75)], 0.2, clr=C)
n = r.report_bad()
r.finish(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None); r.summary()
sys.exit(1 if n else 0)
