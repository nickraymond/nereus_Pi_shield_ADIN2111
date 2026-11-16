"""Stage 3 phase H: signals, small feeds and ground vias. Usage: <KiCad python> phaseH.py <in board> <out board> [log.json]

Every path here was written out by hand as 0 / 45 / 90 degree segments; for the longer ones a grid search (hint.py) proposed the
corridor and only proposals with a few long segments were taken. 0.2 mm tracks (the net class), 0.6 / 0.3 mm vias.
Groups, in the order of the body:
  ADC (U13)        local links on the bottom; 3V3 from Sofar's 3V3 via at (25.15, 24.98) straight south on Internal 2; I2C0 from Sofar's
                   two vias at U4 on Internal 2; POT_WIPER to J8 through one via.
  LEDs             each LED (top) to its resistor (bottom) through one via; ADIN_LED_VDD bus on the bottom (y 36.95), on to JP2.
  Qwiic (J3)       pull-ups, PI_3V3, I2C3 from R10 / R24 to the connector (top). NOT routed: I2C3 from the header.
  Motor control    MOTOR_IN2, MOTOR_IN1: Internal 2, south strip, 45 deg, then north through two one-lane corridors (x 49.5; x 44.2 / 45.3)
                   to J1. MOTOR_VISEN to the ADC on Internal 2. NOT routed: MOTOR_nSLEEP, and U12's outputs / ground pin.
  Straps           CFG0 / CFG1 to JP4 / JP3 on the bottom, ADIN_VDDIO to the three jumpers on Internal 1 (south of J9, not under bus
                   copper). NOT routed: ADIN_TIMER, ADIN_MISO to R9, the U1 pin 19 strap net to R2 / R47.
  Payload          PAYLOAD_EN straight down Internal 2 at x 54.09; ~PAYLOAD_FAULT Internal 1 past the U11 lanes (it passes under T1's
                   bus-side pads for about 1 mm), then Internal 2 to J1 pin 31; both to their test points / pull-up on the bottom;
                   VBUS_OUT on to Sofar's stub (C50, R11).
  ADIN_PWR, PI_3V3 (pin 1 to pin 17 on top between the rows, then Internal 2 south), ~ADC_ALERT, ground vias.
"""
import sys, s3lib
r = s3lib.Router(sys.argv[1], 'H'); T, B, I1, I2 = 'Top Layer', '6 Bottom Layer', 'Internal 1', 'Internal 2'
C = 0.13
# ---- body ----
# --- ADC group (U13, bottom): local links
r.track('~{ADC_ALERT}', B, [(22.75, 35.5), (21.04, 35.5)], 0.2, clr=C)
r.track('Net-(U13-ADDR)', B, [(22.62, 36.0), (22.62, 37.44)], 0.2, clr=C)
r.track('POT_WIPER', B, [(22.35, 34.0), (22.35, 32.68), (23.29, 32.68)], 0.2, clr=C)
r.track('POT_WIPER', B, [(23.29, 32.68), (23.29, 32.28), (23.59, 31.98)], 0.2, clr=C); r.via('POT_WIPER', (23.59, 31.98), clr=C)
r.track('POT_WIPER', T, [(23.59, 31.98), (25.44, 33.83), (25.44, 34.1)], 0.2, clr=C)
r.track('3V3', B, [(27.05, 35.0), (28.6, 35.0)], 0.2, clr=C)
r.track('3V3', B, [(26.5, 35.0), (24.854, 35.0), (24.354, 35.5), (24.354, 37.7), (24.054, 38.0), (21.3, 38.0), (21.04, 37.74), (21.04, 36.26)], 0.2, clr=C)
r.via('3V3', (24.354, 35.5), clr=C); r.track('3V3', T, [(24.354, 35.5), (24.354, 34.6)], 0.2, clr=C)
r.track('I2C0_SDA', B, [(27.05, 35.55), (29.6, 35.55)], 0.2, clr=C)
r.track('I2C0_SCL', B, [(27.05, 36.0), (28.0, 36.95), (30.5, 36.95), (30.85, 36.6), (30.85, 34.05), (30.6, 33.8), (29.6, 33.8)], 0.2, clr=C)
r.track('PI_3V3', B, [(29.6, 34.6), (30.1, 34.6), (30.3, 34.8), (30.3, 36.2), (30.1, 36.4), (29.6, 36.4)], 0.2, clr=C); r.via('PI_3V3', (30.3, 35.5), clr=C)
# --- LEDs: each LED (top) to its resistor (bottom) through a via 1.0 mm east of it; ADIN_LED_VDD bus on the bottom, y 36.95
r.via('Net-(D8-A)', (36.3, 34.9), clr=C); r.track('Net-(D8-A)', T, [(35.3, 34.9), (36.3, 34.9)], 0.2, clr=C); r.track('Net-(D8-A)', B, [(35.3, 34.9), (36.3, 34.9)], 0.2, clr=C)
r.via('Net-(D9-A)', (37.3, 36.2), clr=C); r.track('Net-(D9-A)', T, [(38.3, 36.2), (37.3, 36.2)], 0.2, clr=C); r.track('Net-(D9-A)', B, [(38.3, 36.2), (37.3, 36.2)], 0.2, clr=C)
r.via('Net-(D10-A)', (33.3, 36.2), clr=C); r.track('Net-(D10-A)', T, [(32.3, 36.2), (33.3, 36.2)], 0.2, clr=C); r.track('Net-(D10-A)', B, [(32.3, 36.2), (33.3, 36.2)], 0.2, clr=C)
r.track('ADIN_LED_VDD', B, [(32.3, 35.12), (31.7, 35.12), (31.5, 35.32), (31.5, 36.75), (31.7, 36.95), (38.75, 36.95), (38.95, 36.75), (38.95, 35.32), (38.75, 35.12), (38.3, 35.12)], 0.2, clr=C)
r.track('ADIN_LED_VDD', B, [(35.3, 36.08), (35.3, 36.95)], 0.2, clr=C)
r.track('GND', T, [(35.3, 36.4), (34.3, 36.4)], 0.2, clr=C); r.via('GND', (34.3, 36.4), clr=C)
# --- 3V3, I2C0 south branch (Internal 2 from Sofar vias), LED cathodes, Qwiic
r.track('3V3', I2, [(25.154, 24.979), (24.354, 25.779), (24.354, 35.5)], 0.2)
r.track('I2C0_SDA', I2, [(34.46, 28.74), (27.65, 35.55), (25.9, 35.55)], 0.2); r.via('I2C0_SDA', (25.9, 35.55))
r.track('I2C0_SDA', B, [(25.9, 35.55), (27.05, 35.55)], 0.2)
r.track('I2C0_SCL', I2, [(34.66, 28.01), (34.4, 28.01), (29.6, 32.81)], 0.2); r.via('I2C0_SCL', (29.6, 32.81))
r.track('I2C0_SCL', B, [(29.6, 32.81), (29.6, 33.8)], 0.2)
r.track('~{ADIN_P1_LED1}', B, [(41.43, 29.06), (41.43, 29.16), (40.73, 29.86)], 0.2); r.via('~{ADIN_P1_LED1}', (40.73, 29.86))
r.track('~{ADIN_P1_LED1}', T, [(40.73, 29.86), (40.73, 32.36), (38.33, 34.76)], 0.2)
r.track('~{ADIN_P2_LED1}', B, [(37.13, 20.21), (37.13, 18.91)], 0.2); r.via('~{ADIN_P2_LED1}', (37.13, 18.91))
r.track('~{ADIN_P2_LED1}', I2, [(37.13, 18.91), (37.13, 27.61), (32.33, 32.41), (32.33, 32.61)], 0.2); r.via('~{ADIN_P2_LED1}', (32.33, 32.61))
r.track('~{ADIN_P2_LED1}', T, [(32.33, 32.61), (32.33, 34.81)], 0.2)
r.track('ADIN_LED_VDD', B, [(31.5, 36.5), (29.6, 38.4), (21.2, 38.4), (20.1, 37.3), (20.1, 34.9), (19.5, 34.3)], 0.2)
r.track('PI_3V3', B, [(40.3, 33.82), (40.65, 33.82), (40.85, 34.02), (40.85, 35.42), (40.65, 35.62), (40.3, 35.62)], 0.2)
r.track('I2C3_SDA', B, [(40.3, 34.58), (39.6, 34.58)], 0.2); r.via('I2C3_SDA', (39.6, 34.58))
r.track('I2C3_SDA', T, [(39.6, 34.58), (41.4, 32.78), (45.4, 32.78), (46.0, 33.38), (46.0, 33.88)], 0.2)
r.track('I2C3_SCL', B, [(40.3, 36.38), (43.7, 36.38)], 0.2); r.via('I2C3_SCL', (43.7, 36.38))
r.track('I2C3_SCL', T, [(43.7, 36.38), (44.2, 36.88), (45.5, 36.88), (46.7, 35.68), (46.7, 34.18), (47.0, 33.88)], 0.2)
r.track('PI_3V3', B, [(40.85, 34.7), (41.15, 35.0)], 0.2); r.via('PI_3V3', (41.15, 35.0))
r.track('PI_3V3', T, [(41.15, 35.0), (44.35, 35.0), (45.05, 34.3), (45.05, 33.9)], 0.2)
# --- motor driver control pins (U12, bottom): vias east of the part, the south lane and the centre are left free for the outputs
r.track('MOTOR_IN2', B, [(7.05, 36.2), (7.05, 35.6), (7.25, 35.4), (7.9, 35.4)], 0.2); r.via('MOTOR_IN2', (7.9, 35.4))
r.track('MOTOR_IN1', B, [(7.05, 37.95), (8.3, 37.95), (8.4, 38.05)], 0.2); r.via('MOTOR_IN1', (8.4, 38.05))
r.track('MOTOR_VISEN', B, [(7.3, 36.95), (7.75, 36.95), (8.15, 36.55), (8.4, 36.55)], 0.2); r.via('MOTOR_VISEN', (8.4, 36.55))
# --- straps and jumpers (bottom, south-west)
r.track('CFG1_STRAP', B, [(9.3, 33.6), (9.3, 33.2), (9.5, 33.0), (12.6, 33.0), (13.0, 33.4), (13.0, 37.4)], 0.2)
r.track('Net-(U1A-P1_LED_0{slash}SPI_CFG1)', B, [(9.12, 34.4), (9.12, 35.7)], 0.2)
r.track('GND', B, [(14.3, 37.4), (16.7, 37.4)], 0.2); r.track('GND', B, [(15.5, 37.4), (15.5, 35.45)], 0.2); r.via('GND', (15.5, 35.45))
r.track('CFG0_STRAP', B, [(9.3, 37.1), (9.7, 37.1), (11.0, 38.4), (17.4, 38.4), (18.0, 37.8), (18.0, 37.4)], 0.2)
# --- ADIN_VDDIO to the three jumpers: Internal 1 (not under bus copper: it runs south of J9), one via at each jumper
r.track('ADIN_VDDIO', I1, [(39.756, 27.839), (39.756, 28.839), (32.456, 36.139), (11.5, 36.139)], 0.2); r.via('ADIN_VDDIO', (18.95, 36.139))
r.track('ADIN_VDDIO', B, [(18.95, 36.139), (19.3, 36.489), (19.3, 37.0)], 0.2); r.via('ADIN_VDDIO', (16.55, 36.139))
r.track('ADIN_VDDIO', B, [(16.55, 36.139), (16.55, 35.5)], 0.2); r.via('ADIN_VDDIO', (11.5, 36.139))
r.track('ADIN_VDDIO', B, [(11.5, 36.139), (11.5, 36.9)], 0.2)
# --- long nets from the south-west (Internal 2): MOTOR_VISEN to the ADC; MOTOR_IN2 along the south strip (y 38.6), 45 deg, then north at x 49.5 (a one-lane corridor between Sofar vias) to J1 pin 33; MOTOR_IN1 the same way at x 44.2 / 45.3 to pin 32
r.track('MOTOR_VISEN', I2, [(8.4, 36.55), (10.4, 34.55), (21.6, 34.55)], 0.2); r.via('MOTOR_VISEN', (21.6, 34.55))
r.track('MOTOR_VISEN', B, [(21.6, 34.55), (22.8, 34.55)], 0.2)
r.track('MOTOR_IN2', I2, [(7.9, 35.4), (7.6, 35.7), (7.6, 38.1), (8.1, 38.6), (39.0, 38.6), (49.5, 28.1), (49.5, 5.26), (49.01, 4.77)], 0.2)
r.track('MOTOR_IN1', I2, [(8.4, 38.05), (34.2, 38.05), (44.2, 28.05), (44.2, 13.85), (45.3, 12.75), (45.3, 3.45), (46.5, 2.25)], 0.2)
# --- payload control and status: PAYLOAD_EN straight down Internal 2 at x 54.09 from J1 pin 37; VBUS_OUT to the Sofar stub (C50, R11) on the bottom; ADIN_PWR; PI_3V3
r.track('~{PAYLOAD_FAULT}', B, [(48.9, 36.5), (49.75, 36.5), (49.85, 36.6)], 0.2); r.via('~{PAYLOAD_FAULT}', (49.85, 36.6))
r.track('PAYLOAD_EN', I2, [(54.09, 4.77), (54.09, 34.75)], 0.2)
r.track('VBUS_OUT', B, [(33.331, 11.314), (34.531, 11.314), (38.531, 15.314), (55.631, 15.314), (56.931, 14.014), (59.131, 14.014)], 0.2)
r.track('ADIN_PWR', B, [(26.15, 2.23), (27.25, 1.13), (39.35, 1.13), (39.95, 1.73), (39.95, 8.03)], 0.2)
r.track('PI_3V3', T, [(8.37, 4.77), (9.47, 3.67), (27.57, 3.67), (28.67, 4.77)], 0.2)
r.track('PI_3V3', I2, [(28.69, 4.77), (30.79, 6.87), (30.79, 17.37), (33.99, 20.57), (33.99, 23.47), (35.19, 24.67), (35.19, 28.97), (30.29, 33.87), (30.29, 35.47)], 0.2)
r.track('PI_3V3', I2, [(30.3, 35.5), (31.8, 34.0), (36.6, 34.0)], 0.2); r.via('PI_3V3', (36.6, 34.0))
r.track('PI_3V3', B, [(36.6, 34.0), (40.6, 34.0), (40.85, 34.25)], 0.2)
# --- ~PAYLOAD_FAULT: Internal 1 north from the via at U11 (it has to cross the three Internal 2 lanes of the U11 group), Internal 2 from y 19.3 to J1 pin 31; ADIN_PWR from R43 to the Sofar via; PAYLOAD_EN to TP19 on the bottom
r.track('~{PAYLOAD_FAULT}', I1, [(49.85, 36.6), (49.85, 22.7), (46.45, 19.3)], 0.2); r.via('~{PAYLOAD_FAULT}', (46.45, 19.3))
r.track('~{PAYLOAD_FAULT}', I2, [(46.45, 19.3), (46.45, 4.79), (46.47, 4.77)], 0.2)
r.track('PAYLOAD_EN', B, [(24.156, 17.989), (42.556, 17.989), (42.856, 17.689), (47.756, 17.689), (52.756, 22.689), (54.09, 22.689)], 0.2); r.via('PAYLOAD_EN', (54.09, 22.689))
# --- ADIN_PWR from R43 to the Sofar via; ~ADC_ALERT from J1 pin 7; small parts at U12; ground vias (one per part or pair, into the GND plane)
r.track('ADIN_PWR', B, [(39.97, 8.0), (47.87, 8.0)], 0.2); r.via('ADIN_PWR', (47.87, 8.0))
r.track('ADIN_PWR', I1, [(47.87, 8.0), (47.87, 13.4), (47.631, 13.639)], 0.2)
r.track('~{ADC_ALERT}', I2, [(15.99, 4.77), (17.29, 6.07)], 0.2); r.via('~{ADC_ALERT}', (17.29, 6.07))
r.track('~{ADC_ALERT}', B, [(17.29, 6.07), (17.29, 11.77), (20.49, 14.97), (20.49, 34.97), (20.99, 35.47)], 0.2)
r.track('Net-(U12-ISET)', B, [(5.55, 36.1), (4.04, 36.1)], 0.2)
r.track('Net-(U12-VCC)', B, [(5.3, 37.0), (4.04, 37.0)], 0.2)
r.track('Net-(U12-V3P3)', B, [(5.55, 38.2), (3.87, 38.2)], 0.2)
r.track('GND', B, [(3.28, 36.1), (3.28, 37.17), (2.9, 37.55), (2.9, 38.2)], 0.2)
r.track('GND', B, [(3.28, 36.1), (2.5, 36.1), (2.3, 35.9), (2.3, 33.8), (2.5, 33.6), (3.05, 33.6)], 0.25)
r.track('GND', B, [(23.61, 2.23), (24.71, 3.33), (24.71, 6.29), (24.27, 6.73)], 0.2)
r.track('GND', B, [(39.23, 8.0), (38.81, 7.58), (38.81, 6.94)], 0.2)
r.track('GND', B, [(23.2, 35.0), (23.6, 35.0), (23.75, 35.15), (23.75, 36.45), (23.55, 36.65), (23.55, 37.44)], 0.2); r.via('GND', (23.55, 36.85))
r.track('GND', B, [(21.61, 32.68), (21.61, 31.75)], 0.2); r.via('GND', (21.61, 31.75))
r.track('GND', B, [(24.05, 32.68), (26.61, 32.68), (26.69, 32.6)], 0.2)
r.track('GND', B, [(28.6, 34.24), (28.6, 33.3)], 0.2); r.via('GND', (28.6, 33.3))
r.track('GND', T, [(26.69, 33.5), (26.69, 32.6)], 0.2); r.via('GND', (26.69, 32.6))
r.track('GND', B, [(42.5, 33.6), (41.5, 33.6)], 0.2); r.via('GND', (41.5, 33.6))
r.track('GND', T, [(41.5, 33.6), (44.03, 33.6)], 0.2)
r.track('GND', B, [(54.7, 37.33), (55.5, 37.33)], 0.2); r.via('GND', (55.5, 37.33))
# --- ~PAYLOAD_FAULT to TP35 / R35 (the pull-up) on the bottom, joined to the Internal 2 trunk at x 46.45
r.track('~{PAYLOAD_FAULT}', B, [(24.156, 13.539), (27.856, 17.239), (40.356, 17.239), (41.656, 15.939), (46.156, 15.939)], 0.2); r.via('~{PAYLOAD_FAULT}', (46.156, 15.939))
r.track('~{PAYLOAD_FAULT}', I2, [(46.156, 15.939), (46.45, 15.645)], 0.2)
# ---- end ----
n = r.report_bad()
r.finish(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None); r.summary()
sys.exit(1 if n else 0)
