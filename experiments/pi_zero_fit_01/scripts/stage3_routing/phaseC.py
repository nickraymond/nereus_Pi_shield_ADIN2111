"""Stage 3 phase C: power, west end. Usage: <KiCad python> phaseC.py <in board> <out board> [log.json]

Width basis: docs/design-review/power_budget.md section 4 (1.0 mm, 1 oz outer: 2.4 A at 10 degC rise) and the frozen
board's widths for the same nets (5V_PI 1.0 mm top, Net-(J4-Pin_1) 1.0 mm, 5V_LIFEPO4 1.0 mm, VBUS 0.6 / 1.0 mm). Vias 0.6 / 0.3 mm.
Not in this phase (see the report): the payload switch group (VBUS -> U11, VBUS_OUT -> J5), 3V3 to U13 / J8 / LEDs, U12's pins.

5V_PI (Pi <= 1 A, D15; motor 0.5 A steady, 1.24 A limit):
  converter output -> PWR-plane fill "S3 5V_PI west strip" through three vias: the group's own via (4.267, 14.087), now tied to
  L6 pad 2 by a 1.0 mm top track with a second via on it, and one on the converter's 1.0 mm output track at (1.346, 12.8).
  The fill necks to 1.1 mm beside the H4 keep-out, so a 1.0 mm bottom track runs in parallel past it (x 7.15, y 20.2..29.6),
  stitched to the fill by two vias at each end; JP1 pad 2 and TP38 join that track.
  South of it the track feeds the motor capacitor bank between the two 0805 columns (0.5 mm for 2.6 mm: the gap is 1.65 mm
  and C61's ground return shares it), then C66 -> C61 -> C62 -> C60 and U12 pin 9 (VIN) by short links.
PI_5V: JP1 pad 1 -> two vias -> PWR-plane lane "S3 PI_5V lane" -> J1 pins 2 / 4 (thermal spokes). No track in parallel: see the report.
VBUS to the converter (0.56 A at 16 V for 1.5 A out, review_G_routing S3): 1.0 mm on Internal 2 from the group's own VBUS via
  (10.726, 10.688) along y 7.1 to Sofar's VBUS via at (29.981, 12.764). 0.5 oz inner copper: about 0.65 A at 10 degC rise (IPC-2221 inner).
AUX path: Net-(J4-Pin_1) F1 pad 2 -> J4 pad 1, 1.0 mm bottom; 5V_LIFEPO4 via (4.267, 17.687) -> Internal 2, 0.8 mm -> via -> JP1 pad 3.
"""
import sys, s3lib
r = s3lib.Router(sys.argv[1], 'C'); T, B, I1, I2 = 'Top Layer', '6 Bottom Layer', 'Internal 1', 'Internal 2'
# --- 5V_PI: converter output into the plane
r.track('5V_PI', T, [(4.267, 14.087), (2.196, 14.087)], 1.0, note="the group's via to L6 pad 2")
r.via('5V_PI', (3.45, 14.087)); r.via('5V_PI', (1.346, 12.8))
# --- 5V_PI: parallel track past the H4 keep-out, JP1, TP38
r.via('5V_PI', (7.15, 20.2)); r.via('5V_PI', (7.15, 21.05)); r.via('5V_PI', (7.15, 28.6)); r.via('5V_PI', (7.15, 29.45))
r.track('5V_PI', B, [(7.15, 20.2), (7.15, 29.6), (6.6, 30.15), (6.6, 31.3)], 1.0, note='parallel to the 1.1 mm neck of the plane fill')
r.track('5V_PI', B, [(8.6, 26.0), (7.15, 26.0)], 0.6, note='JP1 pad 2')
r.track('5V_PI', B, [(9.4, 22.4), (7.15, 22.4)], 0.3, note='TP38')
# --- 5V_PI: motor capacitor bank and U12 VIN
r.track('5V_PI', B, [(6.6, 31.3), (6.6, 33.3), (7.2, 33.9)], 0.5, note='between C62 and C66 to C66 pad 1')
r.track('5V_PI', B, [(7.3, 34.5), (6.86, 34.94), (5.64, 34.94), (5.2, 34.5)], 0.3, note='C66 - C61 - C62')
r.track('5V_PI', B, [(6.55, 34.94), (6.55, 36.3)], 0.2, note='U12 pin 9 (pad is 0.2 mm wide)')
r.track('5V_PI', B, [(4.2, 34.6), (3.05, 34.6)], 0.3, note='C62 - C60')
# --- GND of the capacitor bank: one via per 22 uF, C61 and C60 return through C62's pad
r.track('GND', B, [(4.68, 32.3), (4.68, 31.2)], 0.5); r.via('GND', (4.68, 31.2))
r.track('GND', B, [(7.9, 32.3), (7.9, 31.15)], 0.5); r.via('GND', (7.9, 31.15))
r.track('GND', B, [(6.23, 34.18), (5.85, 33.8), (5.85, 32.95), (5.2, 32.3)], 0.25, note='C61 pad 2 to C62 pad 2')
r.track('GND', B, [(3.05, 33.6), (3.05, 32.75), (3.5, 32.3), (4.2, 32.3)], 0.3, note='C60 pad 2 to C62 pad 2')
# --- PI_5V: JP1 pad 1 into the lane
r.track('PI_5V', B, [(8.875, 27.5), (8.875, 28.25)], 0.6); r.track('PI_5V', B, [(8.45, 28.25), (9.3, 28.25)], 0.6)
r.via('PI_5V', (8.45, 28.25)); r.via('PI_5V', (9.3, 28.25))
# --- VBUS to the converter
r.track('VBUS', I2, [(10.726, 10.688), (10.726, 8.1), (11.726, 7.1), (28.6, 7.1), (29.981, 8.481), (29.981, 12.764)], 1.0, note='converter input feed')
# --- AUX path
r.track('Net-(J4-Pin_1)', B, [(7.0, 16.6), (7.0, 18.5), (6.5, 19.0), (1.9, 19.0), (1.9, 21.55)], 1.0)
r.track('5V_LIFEPO4', I2, [(4.267, 17.687), (8.0, 17.687), (11.3, 20.987), (11.3, 23.9)], 0.8)
r.via('5V_LIFEPO4', (11.3, 23.9)); r.track('5V_LIFEPO4', B, [(11.3, 23.9), (10.5, 24.7), (9.2, 24.7)], 0.8)
n = r.report_bad()
r.finish(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None); r.summary()
sys.exit(1 if n else 0)
