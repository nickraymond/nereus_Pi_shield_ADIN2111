"""Stage 3 phase K (fourth session): the orphan via goes, and the six long nets from the south-west and the header are routed
as buses on Internal 1. Usage: <KiCad python> phaseK.py <in> <out> [log.json]

Orphan via   Sofar's via on U11_RTN at (28.431, 6.214) (uuid 90140fec-...) is removed: Nick, 2026-11-16, "Yes delete the orphan via".
             Before it goes, the script prints every piece of copper within 0.6 mm of it on every layer (expected: nothing of its net).
Parts turned R47 by 180 deg and 0.2 mm south (ADIN_TIMER pad now west, at (8.825, 35.9)); R9 by 180 deg in place (ADIN_MISO pad now
             north, at (9.3, 37.1)). Reason: with the pads as they were, no via site for ADIN_MISO clears J7's mounting pad (top), the
             MOTOR_IN1 / MOTOR_VISEN lanes (Internal 2) and R9's other pad at the same time, and the three nets' vias have to stand
             in the order the buses leave: TIMER west, strap and MISO east.
Internal 1   West corridor (between the SW screw keep-out and L2), lanes west to east:
               ADIN_TIMER x 7.85 | I2C3_SCL x 9.83 | I2C3_SDA x 10.19 | ADIN_MISO x 10.6 (x 11.6 north of y 12, past the VBUS via
               at (10.73, 10.69); x 11.5 south of y 33) | strap x 10.85 (south of y 33.8 only)
             Channel under J1: SCL y 6.65, SDA y 7.05, MISO y 7.45 (0.4 mm pitch).
             South strip (south of ADIN_VDDIO's line y 36.139), north to south: strap y 37.4, SDA y 37.8, SCL y 38.2, MOTOR_nSLEEP y 38.62.
  I2C3_SCL   J1 pin 13 - channel - west corridor - south strip - 45 deg into the existing via (43.7, 36.38) at R24.
  I2C3_SDA   J1 pin 15 - the same way one lane inside - north at x 39.6 into the existing via (39.6, 34.58) at R10.
  strap      Net-(U1A-P1_LED_0/SPI_CFG1): R2 / R47 - via (10.85, 33.8) - south strip - 45 deg (x + y = 72.0) - Sofar's via (40.52, 27.88).
  ADIN_MISO  R9 - via (11.5, 35.2) - north at x 10.6 - channel - north between J1 pins 15 / 17 - between the pin rows (y 3.5) - J1 pin 21.
  ADIN_TIMER R47 - via (9.15, 35.1) - north at x 7.85 - west of J1 pin 1 - along the north edge above the header (y 0.85) - J1 pin 36.
  MOTOR_nSLEEP  the phase J via (4.4, 38.62) - south strip to x 55.9 - north at x 56.25 / 55.36 - between J1 pins 37 / 39 -
             between the pin rows (y 3.5) - J1 pin 29.
No via is added except the three at R2 / R47 / R9. All 0.2 mm, 0 / 45 / 90 degrees.
"""
import sys, os, math, s3lib
T, B, I1, I2 = 'Top Layer', '6 Bottom Layer', 'Internal 1', 'Internal 2'
ST = 'Net-(U1A-P1_LED_0{slash}SPI_CFG1)'; ORPHAN = '90140fec-db47-45b4-9b63-10910261351e'; OP = (28.431, 6.214)
# --- what is near the orphan via, on every layer (read this before believing it is an orphan)
g0 = s3lib.Geo(s3lib.pcbnew.LoadBoard(sys.argv[1])); n = 0; own = 0
for layer in g0.L:
    for kind, net, bb, data, desc in g0.L[layer]:
        if 'via U11_RTN (28.43, 6.21)' in desc: continue
        if kind == 'cap': d = s3lib._pt_seg(OP[0], OP[1], data[0][0], data[0][1], data[1][0], data[1][1]) - data[2]
        elif kind == 'rect': d = math.hypot(max(data[0] - OP[0], 0, OP[0] - data[2]), max(data[1] - OP[1], 0, OP[1] - data[3]))
        else: d = s3lib.seg_poly(OP, OP, data)
        if d < 0.6 + 0.225: n += 1; own += net == 'U11_RTN'; print('   near the orphan via: %.3f mm from its centre, %s: %s' % (d, layer, desc))
print('orphan via U11_RTN %s: %d other copper items within 0.6 mm of its pad on any layer; U11_RTN items among them: %d' % (OP, n, own))
if own: raise SystemExit('the via is not an orphan: stop')
del g0
s3lib.prestep(sys.argv[1], os.environ['S3_BASE'],
    removes=[(ST, B, (8.0, 34.0, 10.0, 36.0)), ('CFG0_STRAP', B, (9.0, 36.9, 11.1, 38.5))],
    moves=[('R47', (9.3, 35.9), 1, (8.825, 35.9), 'keep_ref'), ('R9', (9.3, 37.5), 2, (9.3, 37.1), 'keep_ref')], drop=[ORPHAN])
r = s3lib.Router(sys.argv[1], 'K'); C = 0.13
# ---- body ----
# --- bottom, at the three resistors
r.track('CFG0_STRAP', B, [(9.3, 37.9), (10.5, 37.9), (11.0, 38.4)], 0.2, clr=C)
r.track(ST, B, [(9.775, 35.9), (9.775, 34.875), (9.3, 34.4)], 0.2, clr=C)
r.track(ST, B, [(9.3, 34.4), (10.25, 34.4), (10.85, 33.8)], 0.2, clr=C); r.via(ST, (10.85, 33.8), clr=C)
r.track('ADIN_TIMER', B, [(8.825, 35.9), (9.15, 35.575), (9.15, 35.1)], 0.2, clr=C); r.via('ADIN_TIMER', (9.15, 35.1), clr=C)
r.track('ADIN_MISO', B, [(9.3, 37.1), (10.2, 37.1), (10.85, 36.45), (10.85, 35.85), (11.5, 35.2)], 0.2, clr=C); r.via('ADIN_MISO', (11.5, 35.2), clr=C)
# --- Internal 1 buses
r.track('MOTOR_nSLEEP', I1, [(4.4, 38.62), (55.87, 38.62), (56.25, 38.24), (56.25, 23.2), (55.36, 22.31), (55.36, 4.5), (54.36, 3.5), (45.2, 3.5), (43.93, 4.77)], 0.2, clr=C)
r.track('I2C3_SCL', I1, [(23.61, 4.77), (23.61, 6.05), (23.01, 6.65), (10.43, 6.65), (9.83, 7.25), (9.83, 37.29), (10.74, 38.2), (41.88, 38.2), (43.7, 36.38)], 0.2, clr=C)
r.track('I2C3_SDA', I1, [(26.15, 4.77), (26.15, 6.45), (25.55, 7.05), (10.79, 7.05), (10.19, 7.65), (10.19, 37.14), (10.85, 37.8), (39.2, 37.8), (39.6, 37.4), (39.6, 34.58)], 0.2, clr=C)
r.track(ST, I1, [(10.85, 33.8), (10.85, 37.0), (11.25, 37.4), (34.6, 37.4), (41.3, 30.7), (41.3, 28.66), (40.52, 27.88)], 0.2, clr=C)
r.track('ADIN_MISO', I1, [(11.5, 35.2), (11.5, 33.0), (10.6, 32.1), (10.6, 13.0), (11.6, 12.0), (11.6, 8.05), (12.2, 7.45), (26.82, 7.45), (27.42, 6.85), (27.42, 4.1), (28.02, 3.5), (32.5, 3.5), (33.77, 4.77)], 0.2, clr=C)
r.track('ADIN_TIMER', I1, [(9.15, 35.1), (7.85, 33.8), (7.85, 7.85), (7.0, 7.0), (7.0, 1.7), (7.85, 0.85), (52.93, 0.85), (51.55, 2.23)], 0.2, clr=C)
# ---- end ----
n = r.report_bad()
r.finish(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None); r.summary()
sys.exit(1 if n else 0)
