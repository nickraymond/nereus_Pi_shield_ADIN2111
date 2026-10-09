# blockcheck — copied blocks vs the mote

| Block | transform (src → dst, rot) | pads | tracks | arcs | vias | zones | trimmed | missing | extra |
|---|---|---|---|---|---|---|---|---|---|
| RING_MP3 | (176.001, 120.004) → (-6.3100000000000005, 12.0), 0° | 0/0 | 0/0 | 1/1 | 7/7 | 0/0 | 0 | 0 | 0 |
| RING_MP4 | (176.001, 120.004) → (-6.3100000000000005, 21.4), 0° | 0/0 | 0/0 | 1/1 | 7/7 | 0/0 | 0 | 0 | 0 |
| RING_MP1 | (176.001, 120.004) → (-6.3100000000000005, 46.1), 0° | 0/0 | 0/0 | 1/1 | 7/7 | 0/0 | 0 | 0 | 0 |
| RING_MP2 | (176.001, 120.004) → (-6.3100000000000005, 55.5), 0° | 0/0 | 0/0 | 1/1 | 7/7 | 0/0 | 0 | 0 | 0 |
| P1L | (165.501, 108.754) → (12.74, 47.25), 90° | 16/16 | 33/48 | 0/0 | 13/19 | 0/0 | 21 | 0 | 12 |
| P2L | (131.679, 108.279) → (12.74, 16.75), 90° | 12/12 | 16/28 | 0/0 | 14/18 | 0/0 | 16 | 0 | 12 |
| B33 | (140.501, 115.054) → (31.551, 34.44), 0° | 22/22 | 81/88 | 0/0 | 19/19 | 2/2 | 7 | 0 | 23 |
| B5V | (140.501, 115.054) → (31.551, 21.24), 0° | 22/22 | 81/88 | 0/0 | 18/19 | 2/2 | 8 | 0 | 12 |
| SENSE | (146.351, 115.704) → (19.8, 15.0), 0° | 15/15 | 58/77 | 0/0 | 4/5 | 0/0 | 20 | 0 | 14 |
| DAMP3 | (146.001, 116.904) → (33.5, 40.95), 90° | 2/2 | 0/0 | 0/0 | 0/0 | 0/0 | 0 | 0 | 0 |
| DAMP1 | (154.201, 119.204) → (8.9, 60.5), 90° | 5/5 | 7/8 | 0/0 | 0/0 | 0/0 | 1 | 0 | 2 |
| DAMP2 | (151.301, 103.604) → (33.5, 48.6), 0° | 2/2 | 32/36 | 0/0 | 7/7 | 0/0 | 4 | 0 | 3 |
| ADIN | (154.001, 113.004) → (-4.7, 33.75), 90° | 103/103 | 215/252 | 0/0 | 47/47 | 2/2 | 37 | 0 | 87 |
| P1T | (161.601, 117.504) → (3.7, 29.45), 0° | 11/11 | 22/27 | 0/0 | 5/5 | 0/0 | 5 | 0 | 7 |
| P1C | (163.851, 114.104) → (5.95, 26.05), 0° | 4/4 | 0/0 | 0/0 | 0/0 | 0/0 | 0 | 0 | 0 |
| P2T | (135.501, 117.504) → (10.7, 33.75), 180° | 15/15 | 31/33 | 0/0 | 5/5 | 0/0 | 2 | 0 | 6 |
| B18 | (144.501, 110.329) → (19.0, 32.9), 90° | 13/13 | 37/43 | 0/0 | 0/0 | 0/0 | 6 | 0 | 6 |

Total missing: 0; trimmed: 127 (copied items KiCad's DRC called dangling, removed; listed below). Tolerance 0.001 mm. 'extra' = board copper on the block's nets inside its region not explained by the mote (new routing or a mistake).
Totals matched/expected: pads 242/242, tracks 613/728, arcs 4/4, vias 160/172, zones 6/6; copper items 910.

## P1L: trimmed (dangling stub removed by tools/dangling.py, see blocks.json)
- track (18.642, 41.425)-(18.986, 41.081) w1.5 Top Layer /Top-Level Schematic/BM1_P (clipped)
- track (16.433, 47.125)-(13.098, 47.125) w2.0 Top Layer /Top-Level Schematic/BM1_P
- track (17.89, 42.1)-(18.565, 41.425) w2.0 Top Layer /Top-Level Schematic/BM1_P
- track (16.433, 47.125)-(16.433, 47.125) w2.0 Top Layer /Top-Level Schematic/BM1_P
- track (17.89, 45.668)-(17.89, 42.1) w2.0 Top Layer /Top-Level Schematic/BM1_P
- track (16.433, 47.125)-(17.89, 45.668) w2.0 Top Layer /Top-Level Schematic/BM1_P
- via (9.49, 41.65) 0.6/0.3 /Top-Level Schematic/BM1_P
- via (11.94, 46.875) 0.6/0.3 /Top-Level Schematic/BM1_P
- via (9.49, 42.4) 0.6/0.3 /Top-Level Schematic/BM1_P
- via (9.49, 43.15) 0.6/0.3 /Top-Level Schematic/BM1_P
- track (9.265, 43.375)-(9.49, 43.15) w0.5 6 Bottom Layer /Top-Level Schematic/BM1_P
- track (9.517, 41.65)-(9.49, 41.65) w0.5 6 Bottom Layer /Top-Level Schematic/BM1_P
- track (9.676, 41.809)-(9.517, 41.65) w0.5 6 Bottom Layer /Top-Level Schematic/BM1_P
- track (9.265, 45.15)-(9.265, 43.375) w0.5 6 Bottom Layer /Top-Level Schematic/BM1_P
- track (18.986, 47.1)-(12.257, 47.1) w0.2 Internal 2 /Top-Level Schematic/BM1_P (clipped)
- track (12.257, 47.1)-(12.057, 46.9) w0.2 Internal 2 /Top-Level Schematic/BM1_P
- track (12.057, 46.9)-(11.94, 46.9) w0.2 Internal 2 /Top-Level Schematic/BM1_P
- track (18.986, 47.45)-(12.165, 47.45) w0.2 Internal 2 /Top-Level Schematic/BM1_N (clipped)
- track (11.565, 48.05)-(12.165, 47.45) w0.2 Internal 2 /Top-Level Schematic/BM1_N
- via (15.89, 51.9) 0.6/0.3 VBUS
- via (15.89, 52.65) 0.6/0.3 VBUS

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

## B33: trimmed (dangling stub removed by tools/dangling.py, see blocks.json)
- track (35.101, 36.614)-(35.35, 36.863) w0.2032 6 Bottom Layer VBUS (clipped)
- track (35.101, 36.614)-(35.101, 35.811) w0.2032 6 Bottom Layer VBUS
- track (35.101, 35.811)-(35.35, 35.562) w0.2032 6 Bottom Layer VBUS (clipped)
- track (37.051, 32.286)-(37.051, 31.392) w0.5 Top Layer GND (clipped)
- track (33.126, 33.215)-(35.35, 33.215) w0.2 Internal 1 3V3 (clipped)
- track (29.674, 33.706)-(32.635, 33.706) w0.2 Internal 1 3V3
- track (32.635, 33.706)-(33.126, 33.215) w0.2 Internal 1 3V3

## B5V: trimmed (dangling stub removed by tools/dangling.py, see blocks.json)
- track (35.101, 23.414)-(35.35, 23.663) w0.2032 6 Bottom Layer VBUS (clipped)
- track (35.101, 23.414)-(35.101, 22.611) w0.2032 6 Bottom Layer VBUS
- track (35.101, 22.611)-(35.35, 22.362) w0.2032 6 Bottom Layer VBUS (clipped)
- track (37.051, 19.086)-(37.051, 18.192) w0.5 Top Layer GND (clipped)
- via (34.817, 20.615) 0.45/0.2 GND
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
- track (10.408, 58.453)-(10.408, 58.201) w0.381 Top Layer GND (clipped)

## DAMP2: trimmed (dangling stub removed by tools/dangling.py, see blocks.json)
- track (30.0, 45.85)-(30.0, 45.396) w0.6 Top Layer GND (clipped)
- track (29.45, 46.4)-(30.0, 45.85) w0.6 Top Layer GND
- track (31.95, 46.3)-(31.95, 45.55) w0.6 Top Layer GND
- track (31.95, 45.55)-(32.104, 45.396) w0.6 Top Layer GND (clipped)

## ADIN: trimmed (dangling stub removed by tools/dangling.py, see blocks.json)
- track (-4.65, 39.3)-(-4.975, 39.3) w0.2 6 Bottom Layer 1V8
- track (-5.226, 39.551)-(-4.975, 39.3) w0.2 6 Bottom Layer 1V8 (clipped)
- track (-9.418, 35.15)-(-9.804, 35.15) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_CS} (clipped)
- track (-8.85, 34.5)-(-9.725, 34.5) w0.2 Internal 1 /Top-Level Schematic/ADIN_SCK
- track (-9.725, 34.5)-(-9.804, 34.421) w0.2 Internal 1 /Top-Level Schematic/ADIN_SCK (clipped)
- track (0.3, 30.05)-(-0.8, 30.05) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST}
- track (-0.476, 33.098)-(0.8, 31.822) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST}
- track (0.8, 30.55)-(0.3, 30.05) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST}
- track (-7.711, 30.239)-(-8.156, 29.794) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST}
- track (-1.3, 30.55)-(-0.8, 30.05) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST}
- track (-7.4, 30.55)-(-7.711, 30.239) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST}
- track (-8.156, 29.794)-(-9.804, 29.794) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST} (clipped)
- track (-7.711, 30.239)-(-7.711, 30.239) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST}
- track (0.8, 31.822)-(0.8, 30.55) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST}
- track (-1.3, 30.55)-(-7.4, 30.55) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST}
- track (-3.889, 39.551)-(-4.141, 39.3) w0.2 6 Bottom Layer /Top-Level Schematic/ADIN_PWR (clipped)
- track (-6.7, 37.7)-(-6.175, 37.175) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-8.0, 30.879)-(-8.733, 30.146) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-8.0, 37.55)-(-8.0, 30.879) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-3.604, 39.046)-(-4.075, 38.575) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR (clipped)
- track (-7.95, 38.975)-(-8.425, 38.5) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-8.733, 30.146)-(-9.804, 30.146) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR (clipped)
- track (-4.075, 38.575)-(-4.075, 37.55) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-6.956, 38.975)-(-7.95, 38.975) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-6.7, 39.245)-(-6.7, 37.7) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-8.425, 38.5)-(-8.425, 37.975) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-6.719, 39.212)-(-6.956, 38.975) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-4.45, 37.175)-(-6.175, 37.175) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-8.425, 37.975)-(-8.0, 37.55) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-4.075, 37.55)-(-4.45, 37.175) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-9.675, 32.829)-(-9.804, 32.701) w0.2 Internal 1 /Top-Level Schematic/ADIN_MOSI (clipped)
- track (-9.372, 33.5)-(-9.675, 33.197) w0.2 Internal 1 /Top-Level Schematic/ADIN_MOSI
- track (-8.85, 33.5)-(-9.372, 33.5) w0.2 Internal 1 /Top-Level Schematic/ADIN_MOSI
- track (-9.675, 33.197)-(-9.675, 32.829) w0.2 Internal 1 /Top-Level Schematic/ADIN_MOSI
- track (-9.518, 33.976)-(-9.804, 33.691) w0.2 Internal 1 /Top-Level Schematic/ADIN_MISO (clipped)
- track (-9.175, 39.551)-(-9.175, 38.875) w0.381 Top Layer 3V3 (clipped)
- track (-8.101, 39.551)-(-7.15, 38.6) w0.2 6 Bottom Layer 3V3 (clipped)

## P1T: trimmed (dangling stub removed by tools/dangling.py, see blocks.json)
- track (7.35, 27.895)-(7.499, 27.746) w0.2 Internal 2 /Top-Level Schematic/BM1_P (clipped)
- track (6.955, 28.626)-(7.35, 28.231) w0.2 Internal 2 /Top-Level Schematic/BM1_P
- track (7.35, 28.231)-(7.35, 27.895) w0.2 Internal 2 /Top-Level Schematic/BM1_P
- track (7.4, 27.35)-(7.4, 27.146) w0.2 Internal 2 /Top-Level Schematic/BM1_N (clipped)
- track (6.8, 27.95)-(7.4, 27.35) w0.2 Internal 2 /Top-Level Schematic/BM1_N

## P2T: trimmed (dangling stub removed by tools/dangling.py, see blocks.json)
- track (13.19, 35.205)-(13.19, 35.69) w0.2 Top Layer Net-(C25-Pad2)
- track (13.201, 35.701)-(13.19, 35.69) w0.2 Top Layer Net-(C25-Pad2) (clipped)

## B18: trimmed (dangling stub removed by tools/dangling.py, see blocks.json)
- track (21.05, 29.725)-(21.05, 29.3) w0.2 6 Bottom Layer 1V8
- track (21.05, 29.3)-(21.249, 29.101) w0.2 6 Bottom Layer 1V8 (clipped)
- track (17.125, 34.0)-(17.071, 33.946) w0.2 6 Bottom Layer 3V3 (clipped)
- track (17.7, 34.0)-(17.125, 34.0) w0.2 6 Bottom Layer 3V3
- track (18.225, 29.25)-(18.374, 29.101) w0.2 6 Bottom Layer 3V3 (clipped)
- track (18.225, 29.25)-(17.575, 29.25) w0.2 6 Bottom Layer 3V3
