# blockcheck — copied blocks vs the mote

| Block | transform (src → dst, rot) | pads | tracks | arcs | vias | zones | trimmed | missing | extra |
|---|---|---|---|---|---|---|---|---|---|
| RING_MP3 | (176.001, 120.004) → (-1.81, 12.0), 0° | 0/0 | 0/0 | 1/1 | 7/7 | 0/0 | 0 | 0 | 0 |
| RING_MP4 | (176.001, 120.004) → (-1.81, 21.4), 0° | 0/0 | 0/0 | 1/1 | 7/7 | 0/0 | 0 | 0 | 0 |
| RING_MP1 | (176.001, 120.004) → (-1.81, 43.6), 0° | 0/0 | 0/0 | 1/1 | 7/7 | 0/0 | 0 | 0 | 0 |
| RING_MP2 | (176.001, 120.004) → (-1.81, 53.0), 0° | 0/0 | 0/0 | 1/1 | 7/7 | 0/0 | 0 | 0 | 0 |
| ADIN | (154.001, 113.004) → (-1.7, 32.8), 90° | 103/103 | 206/252 | 0/0 | 47/47 | 2/2 | 46 | 0 | 11 |
| P1L | (165.501, 108.754) → (12.74, 44.25), 90° | 16/16 | 31/48 | 0/0 | 8/19 | 0/0 | 28 | 0 | 3 |
| P1T | (161.601, 117.504) → (6.7, 28.4), 0° | 15/15 | 20/27 | 0/0 | 5/5 | 0/0 | 7 | 0 | 3 |
| P2L | (131.679, 108.279) → (12.74, 16.75), 90° | 12/12 | 16/28 | 0/0 | 7/18 | 0/0 | 23 | 0 | 2 |
| P2T | (135.501, 117.504) → (13.7, 32.5), 180° | 15/15 | 31/34 | 0/0 | 5/6 | 0/0 | 4 | 0 | 2 |
| B33 | (140.501, 115.054) → (31.551, 34.44), 0° | 22/22 | 81/88 | 0/0 | 15/19 | 2/2 | 11 | 0 | 8 |
| B5V | (140.501, 115.054) → (31.551, 21.24), 0° | 22/22 | 81/88 | 0/0 | 13/19 | 2/2 | 13 | 0 | 2 |
| SENSE | (146.351, 115.704) → (19.8, 15.0), 0° | 15/15 | 58/77 | 0/0 | 4/5 | 0/0 | 20 | 0 | 3 |
| DAMP3 | (146.001, 116.904) → (33.5, 40.95), 90° | 2/2 | 0/0 | 0/0 | 0/0 | 0/0 | 0 | 0 | 0 |
| DAMP1 | (154.201, 119.204) → (8.9, 57.5), 90° | 5/5 | 6/8 | 0/0 | 0/0 | 0/0 | 2 | 0 | 1 |
| DAMP2 | (151.301, 103.604) → (33.5, 48.6), 0° | 2/2 | 17/36 | 0/0 | 7/7 | 0/0 | 19 | 0 | 5 |
| B18 | (144.501, 110.329) → (19.0, 31.4), 90° | 13/13 | 34/43 | 0/0 | 0/0 | 0/0 | 9 | 0 | 2 |

Total missing: 0; trimmed: 182 (copied items KiCad's DRC called dangling, removed; listed below). Tolerance 0.001 mm. 'extra' = board copper on the block's nets inside its region not explained by the mote (new routing or a mistake).
Totals matched/expected: pads 242/242, tracks 581/729, arcs 4/4, vias 139/173, zones 6/6; copper items 912.

## ADIN: trimmed (dangling stub removed by tools/dangling.py, see blocks.json)
- track (-1.65, 38.35)-(-1.975, 38.35) w0.2 6 Bottom Layer 1V8
- track (-2.226, 38.601)-(-1.975, 38.35) w0.2 6 Bottom Layer 1V8 (clipped)
- track (-6.418, 34.2)-(-6.804, 34.2) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_CS} (clipped)
- track (-5.85, 33.55)-(-6.725, 33.55) w0.2 Internal 1 /Top-Level Schematic/ADIN_SCK
- track (-6.725, 33.55)-(-6.804, 33.471) w0.2 Internal 1 /Top-Level Schematic/ADIN_SCK (clipped)
- track (3.3, 29.1)-(2.2, 29.1) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST}
- track (2.524, 32.148)-(3.8, 30.872) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST}
- track (3.8, 29.6)-(3.3, 29.1) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST}
- track (-4.711, 29.289)-(-5.156, 28.844) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST}
- track (1.7, 29.6)-(2.2, 29.1) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST}
- track (-4.4, 29.6)-(-4.711, 29.289) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST}
- track (-5.156, 28.844)-(-6.804, 28.844) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST} (clipped)
- track (-4.711, 29.289)-(-4.711, 29.289) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST}
- track (3.8, 30.872)-(3.8, 29.6) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST}
- track (1.7, 29.6)-(-4.4, 29.6) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST}
- track (-0.889, 38.601)-(-1.141, 38.35) w0.2 6 Bottom Layer /Top-Level Schematic/ADIN_PWR (clipped)
- track (-3.7, 36.75)-(-3.175, 36.225) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-5.0, 29.929)-(-5.733, 29.196) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-5.0, 36.6)-(-5.0, 29.929) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-0.604, 38.096)-(-1.075, 37.625) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR (clipped)
- track (-4.95, 38.025)-(-5.425, 37.55) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-5.733, 29.196)-(-6.804, 29.196) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR (clipped)
- track (-1.075, 37.625)-(-1.075, 36.6) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-3.956, 38.025)-(-4.95, 38.025) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-3.7, 38.295)-(-3.7, 36.75) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-5.425, 37.55)-(-5.425, 37.025) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-3.719, 38.262)-(-3.956, 38.025) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-1.45, 36.225)-(-3.175, 36.225) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-5.425, 37.025)-(-5.0, 36.6) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-1.075, 36.6)-(-1.45, 36.225) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-6.675, 31.879)-(-6.804, 31.751) w0.2 Internal 1 /Top-Level Schematic/ADIN_MOSI (clipped)
- track (-6.372, 32.55)-(-6.675, 32.247) w0.2 Internal 1 /Top-Level Schematic/ADIN_MOSI
- track (-5.85, 32.55)-(-6.372, 32.55) w0.2 Internal 1 /Top-Level Schematic/ADIN_MOSI
- track (-6.675, 32.247)-(-6.675, 31.879) w0.2 Internal 1 /Top-Level Schematic/ADIN_MOSI
- track (-6.518, 33.026)-(-6.804, 32.741) w0.2 Internal 1 /Top-Level Schematic/ADIN_MISO (clipped)
- track (-5.85, 31.05)-(-6.3, 30.6) w0.2032 Top Layer /Top-Level Schematic/~{ADIN_INT}
- track (-5.1, 31.05)-(-5.85, 31.05) w0.2032 Top Layer /Top-Level Schematic/~{ADIN_INT}
- track (-6.3, 30.6)-(-6.804, 30.6) w0.2032 Top Layer /Top-Level Schematic/~{ADIN_INT} (clipped)
- track (-4.774, 30.629)-(-5.053, 30.35) w0.2032 6 Bottom Layer /Top-Level Schematic/~{ADIN_INT}
- track (-4.774, 31.001)-(-4.774, 30.629) w0.2032 6 Bottom Layer /Top-Level Schematic/~{ADIN_INT}
- …

## P1L: trimmed (dangling stub removed by tools/dangling.py, see blocks.json)
- track (18.642, 38.425)-(18.986, 38.081) w1.5 Top Layer /Top-Level Schematic/BM1_P (clipped)
- track (16.433, 44.125)-(13.098, 44.125) w2.0 Top Layer /Top-Level Schematic/BM1_P
- track (17.89, 39.1)-(18.565, 38.425) w2.0 Top Layer /Top-Level Schematic/BM1_P
- track (16.433, 44.125)-(16.433, 44.125) w2.0 Top Layer /Top-Level Schematic/BM1_P
- track (17.89, 42.668)-(17.89, 39.1) w2.0 Top Layer /Top-Level Schematic/BM1_P
- track (16.433, 44.125)-(17.89, 42.668) w2.0 Top Layer /Top-Level Schematic/BM1_P
- via (9.49, 38.65) 0.6/0.3 /Top-Level Schematic/BM1_P
- via (11.94, 43.875) 0.6/0.3 /Top-Level Schematic/BM1_P
- via (9.49, 39.4) 0.6/0.3 /Top-Level Schematic/BM1_P
- via (9.49, 40.15) 0.6/0.3 /Top-Level Schematic/BM1_P
- track (9.265, 40.375)-(9.49, 40.15) w0.5 6 Bottom Layer /Top-Level Schematic/BM1_P
- track (9.517, 38.65)-(9.49, 38.65) w0.5 6 Bottom Layer /Top-Level Schematic/BM1_P
- track (9.676, 38.809)-(9.517, 38.65) w0.5 6 Bottom Layer /Top-Level Schematic/BM1_P
- track (9.265, 42.15)-(9.265, 40.375) w0.5 6 Bottom Layer /Top-Level Schematic/BM1_P
- track (18.986, 44.1)-(12.257, 44.1) w0.2 Internal 2 /Top-Level Schematic/BM1_P (clipped)
- track (12.257, 44.1)-(12.057, 43.9) w0.2 Internal 2 /Top-Level Schematic/BM1_P
- track (12.057, 43.9)-(11.94, 43.9) w0.2 Internal 2 /Top-Level Schematic/BM1_P
- track (18.986, 44.45)-(12.165, 44.45) w0.2 Internal 2 /Top-Level Schematic/BM1_N (clipped)
- track (11.565, 45.05)-(12.165, 44.45) w0.2 Internal 2 /Top-Level Schematic/BM1_N
- via (15.89, 48.9) 0.6/0.3 VBUS
- via (15.89, 49.65) 0.6/0.3 VBUS
- via (6.892, 44.755) 0.6/0.3 GND
- via (7.19, 46.0) 0.6/0.3 GND
- via (7.39, 45.3) 0.6/0.3 GND
- via (15.94, 39.0) 0.6/0.3 GND
- via (15.94, 38.25) 0.6/0.3 GND
- track (17.69, 45.6)-(17.096, 45.6) w0.3 6 Bottom Layer GND
- track (17.69, 45.6)-(18.09, 45.2) w0.3 6 Bottom Layer GND

## P1T: trimmed (dangling stub removed by tools/dangling.py, see blocks.json)
- track (10.35, 26.845)-(10.499, 26.696) w0.2 Internal 2 /Top-Level Schematic/BM1_P (clipped)
- track (9.955, 27.576)-(10.35, 27.181) w0.2 Internal 2 /Top-Level Schematic/BM1_P
- track (10.35, 27.181)-(10.35, 26.845) w0.2 Internal 2 /Top-Level Schematic/BM1_P
- track (10.4, 26.3)-(10.4, 26.096) w0.2 Internal 2 /Top-Level Schematic/BM1_N (clipped)
- track (9.8, 26.9)-(10.4, 26.3) w0.2 Internal 2 /Top-Level Schematic/BM1_N
- track (6.542, 30.658)-(6.542, 29.858) w0.381 6 Bottom Layer GND
- track (6.504, 30.696)-(6.542, 30.658) w0.381 6 Bottom Layer GND (clipped)

## P2L: trimmed (dangling stub removed by tools/dangling.py, see blocks.json)
- track (17.161, 20.103)-(16.317, 20.103) w0.5 6 Bottom Layer /Top-Level Schematic/PoDL/Power Monitor/P_IN (clipped)
- track (12.915, 16.778)-(11.105, 14.968) w2.0 Top Layer /Top-Level Schematic/BM2_P
- track (16.14, 16.778)-(12.915, 16.778) w2.0 Top Layer /Top-Level Schematic/BM2_P
- track (17.161, 17.799)-(16.14, 16.778) w2.0 Top Layer /Top-Level Schematic/BM2_P (clipped)
- via (11.34, 16.528) 0.6/0.3 /Top-Level Schematic/BM2_P
- track (17.161, 16.427)-(11.819, 16.427) w0.203 Internal 2 /Top-Level Schematic/BM2_P (clipped)
- track (11.616, 16.604)-(11.416, 16.604) w0.203 Internal 2 /Top-Level Schematic/BM2_P
- track (11.416, 16.604)-(11.34, 16.528) w0.203 Internal 2 /Top-Level Schematic/BM2_P
- track (11.629, 16.617)-(11.616, 16.604) w0.203 Internal 2 /Top-Level Schematic/BM2_P
- track (11.629, 16.617)-(11.819, 16.427) w0.203 Internal 2 /Top-Level Schematic/BM2_P
- track (10.506, 18.978)-(5.961, 18.978) w2.0 Top Layer /Top-Level Schematic/BM2_N (clipped)
- via (11.115, 18.369) 0.6/0.3 /Top-Level Schematic/BM2_N
- via (11.115, 17.628) 0.6/0.3 /Top-Level Schematic/BM2_N
- via (10.415, 18.378) 0.6/0.3 /Top-Level Schematic/BM2_N
- track (11.115, 17.628)-(11.965, 16.778) w0.2 Internal 2 /Top-Level Schematic/BM2_N
- track (17.161, 16.778)-(11.965, 16.778) w0.2 Internal 2 /Top-Level Schematic/BM2_N (clipped)
- via (8.915, 23.253) 0.6/0.3 GND
- via (8.565, 22.628) 0.6/0.3 GND
- via (15.965, 12.096) 0.6/0.3 GND
- via (15.965, 11.295) 0.6/0.3 GND
- via (15.965, 12.895) 0.6/0.3 GND
- via (9.265, 22.628) 0.6/0.3 GND
- via (15.965, 13.695) 0.6/0.3 GND

## P2T: trimmed (dangling stub removed by tools/dangling.py, see blocks.json)
- track (16.19, 33.955)-(16.19, 34.44) w0.2 Top Layer Net-(C25-Pad2)
- track (16.201, 34.451)-(16.19, 34.44) w0.2 Top Layer Net-(C25-Pad2) (clipped)
- via (10.625, 34.85) 0.45/0.2 GND
- track (10.45, 33.15)-(10.001, 33.15) w0.2 6 Bottom Layer GND (clipped)

## B33: trimmed (dangling stub removed by tools/dangling.py, see blocks.json)
- track (35.101, 36.614)-(35.35, 36.863) w0.2032 6 Bottom Layer VBUS (clipped)
- track (35.101, 36.614)-(35.101, 35.811) w0.2032 6 Bottom Layer VBUS
- track (35.101, 35.811)-(35.35, 35.562) w0.2032 6 Bottom Layer VBUS (clipped)
- track (37.051, 32.286)-(37.051, 31.392) w0.5 Top Layer GND (clipped)
- via (34.817, 33.815) 0.45/0.2 GND
- via (34.251, 30.09) 0.6/0.3 GND
- via (35.194, 28.273) 0.6/0.3 GND
- via (29.626, 34.54) 0.45/0.2 GND
- track (33.126, 33.215)-(35.35, 33.215) w0.2 Internal 1 3V3 (clipped)
- track (29.674, 33.706)-(32.635, 33.706) w0.2 Internal 1 3V3
- track (32.635, 33.706)-(33.126, 33.215) w0.2 Internal 1 3V3

## B5V: trimmed (dangling stub removed by tools/dangling.py, see blocks.json)
- track (35.101, 23.414)-(35.35, 23.663) w0.2032 6 Bottom Layer VBUS (clipped)
- track (35.101, 23.414)-(35.101, 22.611) w0.2032 6 Bottom Layer VBUS
- track (35.101, 22.611)-(35.35, 22.362) w0.2032 6 Bottom Layer VBUS (clipped)
- track (37.051, 19.086)-(37.051, 18.192) w0.5 Top Layer GND (clipped)
- via (34.817, 20.615) 0.45/0.2 GND
- via (34.251, 16.89) 0.6/0.3 GND
- via (35.194, 15.073) 0.6/0.3 GND
- via (29.626, 21.34) 0.45/0.2 GND
- via (36.026, 18.09) 0.6/0.3 /Top-Level Schematic/5V_PI
- via (35.276, 18.09) 0.6/0.3 /Top-Level Schematic/5V_PI
- track (33.126, 20.015)-(35.35, 20.015) w0.2 Internal 1 /Top-Level Schematic/5V_PI (clipped)
- track (29.674, 20.506)-(32.635, 20.506) w0.2 Internal 1 /Top-Level Schematic/5V_PI
- track (32.635, 20.506)-(33.126, 20.015) w0.2 Internal 1 /Top-Level Schematic/5V_PI

## SENSE: trimmed (dangling stub removed by tools/dangling.py, see blocks.json)
- track (22.446, 15.629)-(22.449, 15.626) w0.2032 6 Bottom Layer Net-(U4-ALERT) (clipped)
- track (21.8, 15.629)-(22.446, 15.629) w0.2032 6 Bottom Layer Net-(U4-ALERT)
- track (22.0, 16.075)-(22.449, 15.626) w0.2032 Internal 1 Net-(U4-ALERT) (clipped)
- track (18.317, 16.075)-(22.0, 16.075) w0.2032 Internal 1 Net-(U4-ALERT)
- track (21.375, 17.375)-(21.625, 17.125) w0.15 Top Layer /Top-Level Schematic/I2C1_SDA
- track (22.15, 15.289)-(22.337, 15.102) w0.15 Top Layer /Top-Level Schematic/I2C1_SDA
- track (21.772, 17.125)-(22.15, 16.747) w0.15 Top Layer /Top-Level Schematic/I2C1_SDA
- track (22.337, 13.674)-(22.449, 13.562) w0.15 Top Layer /Top-Level Schematic/I2C1_SDA (clipped)
- track (22.15, 16.747)-(22.15, 15.289) w0.15 Top Layer /Top-Level Schematic/I2C1_SDA
- track (21.625, 17.125)-(21.772, 17.125) w0.15 Top Layer /Top-Level Schematic/I2C1_SDA
- track (22.337, 15.102)-(22.337, 13.674) w0.15 Top Layer /Top-Level Schematic/I2C1_SDA
- track (21.85, 16.375)-(21.85, 15.164) w0.15 Top Layer /Top-Level Schematic/I2C1_SCL
- track (22.037, 14.978)-(22.037, 13.55) w0.15 Top Layer /Top-Level Schematic/I2C1_SCL
- track (21.85, 15.164)-(22.037, 14.978) w0.15 Top Layer /Top-Level Schematic/I2C1_SCL
- track (22.037, 13.55)-(22.091, 13.496) w0.15 Top Layer /Top-Level Schematic/I2C1_SCL (clipped)
- track (21.575, 16.65)-(21.85, 16.375) w0.15 Top Layer /Top-Level Schematic/I2C1_SCL
- track (19.45, 13.7)-(19.45, 11.696) w0.5 Top Layer GND (clipped)
- via (21.172, 14.382) 0.45/0.2 3V3
- track (17.849, 13.125)-(18.75, 13.125) w0.2 Internal 1 3V3 (clipped)
- track (18.75, 13.125)-(20.179, 11.696) w0.2 Internal 1 3V3 (clipped)

## DAMP1: trimmed (dangling stub removed by tools/dangling.py, see blocks.json)
- track (10.408, 55.453)-(10.408, 55.201) w0.381 Top Layer GND (clipped)
- track (9.775, 55.825)-(10.399, 55.201) w0.381 6 Bottom Layer GND (clipped)

## DAMP2: trimmed (dangling stub removed by tools/dangling.py, see blocks.json)
- track (30.0, 45.85)-(30.0, 45.396) w0.6 Top Layer GND (clipped)
- track (29.45, 46.4)-(30.0, 45.85) w0.6 Top Layer GND
- track (31.95, 46.3)-(31.95, 45.55) w0.6 Top Layer GND
- track (31.95, 45.55)-(32.104, 45.396) w0.6 Top Layer GND (clipped)
- track (29.2, 47.35)-(29.225, 47.325) w0.2 6 Bottom Layer GND
- track (29.225, 46.775)-(29.373, 46.627) w0.2 6 Bottom Layer GND
- track (32.5, 46.55)-(32.675, 46.725) w0.2 6 Bottom Layer GND
- track (28.999, 46.501)-(29.023, 46.477) w0.2 6 Bottom Layer GND (clipped)
- track (32.308, 46.55)-(32.5, 46.55) w0.2 6 Bottom Layer GND
- track (36.864, 51.514)-(36.864, 50.414) w0.2 6 Bottom Layer GND
- track (32.675, 47.325)-(32.675, 46.725) w0.2 6 Bottom Layer GND
- track (32.2, 47.35)-(32.2, 46.602) w0.2 6 Bottom Layer GND
- track (29.023, 46.477)-(29.373, 46.477) w0.2 6 Bottom Layer GND
- track (32.675, 47.325)-(32.7, 47.35) w0.2 6 Bottom Layer GND
- track (29.675, 47.325)-(29.7, 47.35) w0.2 6 Bottom Layer GND
- track (31.7, 47.35)-(31.7, 46.602) w0.2 6 Bottom Layer GND
- track (36.45, 50.0)-(36.864, 50.414) w0.2 6 Bottom Layer GND
- track (29.225, 47.325)-(29.225, 46.775) w0.2 6 Bottom Layer GND
- track (29.675, 47.325)-(29.675, 46.659) w0.2 6 Bottom Layer GND

## B18: trimmed (dangling stub removed by tools/dangling.py, see blocks.json)
- track (21.05, 28.225)-(21.05, 27.8) w0.2 6 Bottom Layer 1V8
- track (21.05, 27.8)-(21.249, 27.601) w0.2 6 Bottom Layer 1V8 (clipped)
- track (18.6, 31.2)-(18.068, 31.2) w0.2 6 Bottom Layer GND
- track (17.558, 31.71)-(18.068, 31.2) w0.2 6 Bottom Layer GND
- track (17.558, 31.757)-(17.558, 31.71) w0.2 6 Bottom Layer GND
- track (17.125, 32.5)-(17.071, 32.446) w0.2 6 Bottom Layer 3V3 (clipped)
- track (17.7, 32.5)-(17.125, 32.5) w0.2 6 Bottom Layer 3V3
- track (18.225, 27.75)-(18.374, 27.601) w0.2 6 Bottom Layer 3V3 (clipped)
- track (18.225, 27.75)-(17.575, 27.75) w0.2 6 Bottom Layer 3V3
