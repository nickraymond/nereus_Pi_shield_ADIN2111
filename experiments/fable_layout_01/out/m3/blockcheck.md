# blockcheck — copied blocks vs the mote

| Block | transform (src → dst, rot) | pads | tracks | arcs | vias | zones | trimmed | missing | extra |
|---|---|---|---|---|---|---|---|---|---|
| RING_MP3 | (176.001, 120.004) → (-1.81, 12.0), 0° | 0/0 | 0/0 | 1/1 | 7/7 | 0/0 | 0 | 0 | 0 |
| RING_MP4 | (176.001, 120.004) → (-1.81, 21.4), 0° | 0/0 | 0/0 | 1/1 | 7/7 | 0/0 | 0 | 0 | 0 |
| RING_MP1 | (176.001, 120.004) → (-1.81, 43.6), 0° | 0/0 | 0/0 | 1/1 | 7/7 | 0/0 | 0 | 0 | 0 |
| RING_MP2 | (176.001, 120.004) → (-1.81, 53.0), 0° | 0/0 | 0/0 | 1/1 | 7/7 | 0/0 | 0 | 0 | 0 |
| ADIN | (154.001, 113.004) → (-1.4, 32.8), 90° | 103/103 | 233/267 | 0/0 | 50/50 | 2/2 | 34 | 0 | 174 |
| P1L | (165.501, 108.754) → (12.74, 44.25), 90° | 16/16 | 37/48 | 0/0 | 11/19 | 0/0 | 19 | 0 | 15 |
| P1T | (161.601, 117.504) → (8.7, 28.4), 0° | 15/15 | 20/27 | 0/0 | 5/5 | 0/0 | 7 | 0 | 13 |
| P2L | (131.679, 108.279) → (12.74, 16.75), 90° | 12/12 | 22/28 | 0/0 | 12/18 | 0/0 | 12 | 0 | 21 |
| P2T | (135.501, 117.504) → (16.0, 32.3), 180° | 15/15 | 33/34 | 0/0 | 5/6 | 0/0 | 2 | 0 | 16 |
| B33 | (140.501, 115.054) → (31.551, 17.704), 0° | 22/22 | 84/88 | 0/0 | 15/19 | 2/2 | 8 | 0 | 3 |
| B5V | (140.501, 115.054) → (31.551, 31.4), 0° | 22/22 | 85/88 | 0/0 | 14/19 | 2/2 | 8 | 0 | 26 |
| SENSE | (146.351, 115.704) → (19.8, 15.0), 0° | 15/15 | 51/75 | 0/0 | 5/5 | 0/0 | 24 | 0 | 15 |
| DAMP3 | (146.001, 116.904) → (33.5, 40.0), 0° | 2/2 | 0/0 | 0/0 | 0/0 | 0/0 | 0 | 0 | 0 |
| DAMP1 | (154.201, 119.204) → (8.9, 57.5), 90° | 5/5 | 8/8 | 0/0 | 0/0 | 0/0 | 0 | 0 | 2 |
| DAMP2 | (151.301, 103.604) → (33.9, 48.2), 0° | 2/2 | 17/36 | 0/0 | 7/7 | 0/0 | 19 | 0 | 7 |
| B18 | (144.501, 110.329) → (20.7, 47.2), 90° | 13/13 | 37/43 | 0/0 | 0/0 | 0/0 | 6 | 0 | 16 |

Total missing: 0; trimmed: 139 (copied items KiCad's DRC called dangling, removed; listed below). Tolerance 0.001 mm. 'extra' = board copper on the block's nets inside its region not explained by the mote (new routing or a mistake).
Totals matched/expected: pads 242/242, tracks 627/742, arcs 4/4, vias 152/176, zones 6/6; copper items 928.

## ADIN: trimmed (dangling stub removed by tools/dangling.py, see blocks.json)
- track (-2.025, 38.801)-(-2.025, 38.7) w0.2 6 Bottom Layer 1V8 (clipped)
- track (-2.025, 38.7)-(-1.675, 38.35) w0.2 6 Bottom Layer 1V8
- track (-6.118, 34.2)-(-6.804, 34.2) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_CS} (clipped)
- track (-5.55, 33.55)-(-6.425, 33.55) w0.2 Internal 1 /Top-Level Schematic/ADIN_SCK
- track (-6.425, 33.55)-(-6.804, 33.171) w0.2 Internal 1 /Top-Level Schematic/ADIN_SCK (clipped)
- track (-6.59, 28.844)-(-6.804, 28.63) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST} (clipped)
- track (3.6, 29.1)-(2.5, 29.1) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST}
- track (4.1, 29.6)-(3.6, 29.1) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST}
- track (-4.411, 29.289)-(-4.856, 28.844) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST}
- track (2.0, 29.6)-(2.5, 29.1) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST}
- track (-4.1, 29.6)-(-4.411, 29.289) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST}
- track (-4.856, 28.844)-(-6.59, 28.844) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST}
- track (-4.411, 29.289)-(-4.411, 29.289) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST}
- track (4.1, 30.872)-(4.1, 29.6) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST}
- track (2.0, 29.6)-(-4.1, 29.6) w0.2 Internal 1 /Top-Level Schematic/~{ADIN_RST}
- track (-4.7, 29.929)-(-5.433, 29.196) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-4.7, 36.6)-(-4.7, 29.929) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-4.65, 38.025)-(-5.125, 37.55) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-5.433, 29.196)-(-6.804, 29.196) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR (clipped)
- track (-3.656, 38.025)-(-4.65, 38.025) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-5.125, 37.55)-(-5.125, 37.025) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-3.419, 38.262)-(-3.656, 38.025) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-5.125, 37.025)-(-4.7, 36.6) w0.2032 Internal 1 /Top-Level Schematic/ADIN_PWR
- track (-6.375, 31.879)-(-6.804, 31.451) w0.2 Internal 1 /Top-Level Schematic/ADIN_MOSI (clipped)
- track (-6.072, 32.55)-(-6.375, 32.247) w0.2 Internal 1 /Top-Level Schematic/ADIN_MOSI
- track (-5.55, 32.55)-(-6.072, 32.55) w0.2 Internal 1 /Top-Level Schematic/ADIN_MOSI
- track (-6.375, 32.247)-(-6.375, 31.879) w0.2 Internal 1 /Top-Level Schematic/ADIN_MOSI
- track (-6.218, 33.026)-(-6.804, 32.441) w0.2 Internal 1 /Top-Level Schematic/ADIN_MISO (clipped)
- track (-3.85, 38.775)-(-4.35, 38.775) w0.5 Top Layer GND
- track (6.022, 30.839)-(6.196, 30.665) w0.381 Top Layer GND (clipped)
- track (-4.376, 38.801)-(-4.35, 38.775) w0.5 Top Layer GND (clipped)
- track (5.675, 34.448)-(5.675, 30.925) w0.381 6 Bottom Layer GND
- track (5.675, 30.925)-(6.196, 30.404) w0.381 6 Bottom Layer GND (clipped)
- track (-5.875, 38.801)-(-5.875, 37.925) w0.381 Top Layer 3V3 (clipped)

## P1L: trimmed (dangling stub removed by tools/dangling.py, see blocks.json)
- track (18.642, 38.425)-(18.986, 38.081) w1.5 Top Layer /Top-Level Schematic/BM1_P (clipped)
- track (16.433, 44.125)-(13.098, 44.125) w2.0 Top Layer /Top-Level Schematic/BM1_P
- track (17.89, 39.1)-(18.565, 38.425) w2.0 Top Layer /Top-Level Schematic/BM1_P
- track (16.433, 44.125)-(16.433, 44.125) w2.0 Top Layer /Top-Level Schematic/BM1_P
- track (17.89, 42.668)-(17.89, 39.1) w2.0 Top Layer /Top-Level Schematic/BM1_P
- track (16.433, 44.125)-(17.89, 42.668) w2.0 Top Layer /Top-Level Schematic/BM1_P
- via (9.49, 38.65) 0.6/0.3 /Top-Level Schematic/BM1_P
- track (18.986, 44.1)-(12.257, 44.1) w0.2 Internal 2 /Top-Level Schematic/BM1_P (clipped)
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
- track (12.35, 26.845)-(12.499, 26.696) w0.2 Internal 2 /Top-Level Schematic/BM1_P (clipped)
- track (11.955, 27.576)-(12.35, 27.181) w0.2 Internal 2 /Top-Level Schematic/BM1_P
- track (12.35, 27.181)-(12.35, 26.845) w0.2 Internal 2 /Top-Level Schematic/BM1_P
- track (12.4, 26.3)-(12.4, 26.096) w0.2 Internal 2 /Top-Level Schematic/BM1_N (clipped)
- track (11.8, 26.9)-(12.4, 26.3) w0.2 Internal 2 /Top-Level Schematic/BM1_N
- track (8.542, 30.658)-(8.542, 29.858) w0.381 6 Bottom Layer GND
- track (8.504, 30.696)-(8.542, 30.658) w0.381 6 Bottom Layer GND (clipped)

## P2L: trimmed (dangling stub removed by tools/dangling.py, see blocks.json)
- track (17.461, 20.103)-(16.317, 20.103) w0.5 6 Bottom Layer /Top-Level Schematic/PoDL/Power Monitor/P_IN (clipped)
- track (17.461, 16.427)-(11.819, 16.427) w0.203 Internal 2 /Top-Level Schematic/BM2_P (clipped)
- track (11.629, 16.617)-(11.819, 16.427) w0.203 Internal 2 /Top-Level Schematic/BM2_P
- track (10.506, 18.978)-(5.961, 18.978) w2.0 Top Layer /Top-Level Schematic/BM2_N (clipped)
- track (11.115, 17.628)-(11.965, 16.778) w0.2 Internal 2 /Top-Level Schematic/BM2_N
- track (17.461, 16.778)-(11.965, 16.778) w0.2 Internal 2 /Top-Level Schematic/BM2_N (clipped)
- via (8.915, 23.253) 0.6/0.3 GND
- via (15.965, 12.096) 0.6/0.3 GND
- via (15.965, 11.295) 0.6/0.3 GND
- via (15.965, 12.895) 0.6/0.3 GND
- via (9.265, 22.628) 0.6/0.3 GND
- via (15.965, 13.695) 0.6/0.3 GND

## P2T: trimmed (dangling stub removed by tools/dangling.py, see blocks.json)
- via (12.925, 34.65) 0.45/0.2 GND
- track (12.75, 32.95)-(12.301, 32.95) w0.2 6 Bottom Layer GND (clipped)

## B33: trimmed (dangling stub removed by tools/dangling.py, see blocks.json)
- track (35.101, 19.878)-(35.35, 20.127) w0.2032 6 Bottom Layer VBUS (clipped)
- track (35.101, 19.878)-(35.101, 19.075) w0.2032 6 Bottom Layer VBUS
- track (35.101, 19.075)-(35.35, 18.826) w0.2032 6 Bottom Layer VBUS (clipped)
- track (37.051, 15.55)-(37.051, 14.656) w0.5 Top Layer GND (clipped)
- via (34.817, 17.079) 0.45/0.2 GND
- via (34.251, 13.354) 0.6/0.3 GND
- via (35.194, 11.537) 0.6/0.3 GND
- via (29.626, 17.804) 0.45/0.2 GND

## B5V: trimmed (dangling stub removed by tools/dangling.py, see blocks.json)
- track (35.101, 33.574)-(35.101, 32.771) w0.2032 6 Bottom Layer VBUS
- track (35.101, 32.771)-(35.35, 32.522) w0.2032 6 Bottom Layer VBUS (clipped)
- track (37.051, 29.246)-(37.051, 28.352) w0.5 Top Layer GND (clipped)
- via (34.817, 30.775) 0.45/0.2 GND
- via (34.251, 27.05) 0.6/0.3 GND
- via (35.194, 25.233) 0.6/0.3 GND
- via (29.626, 31.5) 0.45/0.2 GND
- via (36.026, 28.25) 0.6/0.3 /Top-Level Schematic/5V_PI

## SENSE: trimmed (dangling stub removed by tools/dangling.py, see blocks.json)
- track (17.923, 17.469)-(18.544, 17.469) w0.2032 6 Bottom Layer /Top-Level Schematic/PoDL/Power Monitor/P_IN
- track (18.925, 14.589)-(18.925, 13.776) w0.2032 6 Bottom Layer /Top-Level Schematic/PoDL/Power Monitor/P_IN
- track (18.758, 14.756)-(18.925, 14.589) w0.2032 6 Bottom Layer /Top-Level Schematic/PoDL/Power Monitor/P_IN
- track (17.849, 14.85)-(17.943, 14.756) w0.2032 6 Bottom Layer /Top-Level Schematic/PoDL/Power Monitor/P_IN (clipped)
- track (17.943, 14.756)-(18.758, 14.756) w0.2032 6 Bottom Layer /Top-Level Schematic/PoDL/Power Monitor/P_IN
- track (18.544, 17.469)-(18.725, 17.65) w0.2032 6 Bottom Layer /Top-Level Schematic/PoDL/Power Monitor/P_IN
- track (18.725, 17.975)-(18.725, 17.65) w0.2032 6 Bottom Layer /Top-Level Schematic/PoDL/Power Monitor/P_IN
- track (17.849, 17.396)-(17.923, 17.469) w0.2032 6 Bottom Layer /Top-Level Schematic/PoDL/Power Monitor/P_IN (clipped)
- track (18.076, 17.1)-(19.05, 17.1) w0.2032 6 Bottom Layer VBUS
- track (17.849, 16.873)-(18.076, 17.1) w0.2032 6 Bottom Layer VBUS (clipped)
- track (19.425, 17.975)-(19.425, 17.475) w0.2032 6 Bottom Layer VBUS
- track (19.05, 17.1)-(19.425, 17.475) w0.2032 6 Bottom Layer VBUS
- track (22.15, 15.289)-(22.337, 15.102) w0.15 Top Layer /Top-Level Schematic/I2C1_SDA
- track (22.337, 13.674)-(22.449, 13.562) w0.15 Top Layer /Top-Level Schematic/I2C1_SDA (clipped)
- track (22.15, 16.747)-(22.15, 15.289) w0.15 Top Layer /Top-Level Schematic/I2C1_SDA
- track (22.337, 15.102)-(22.337, 13.674) w0.15 Top Layer /Top-Level Schematic/I2C1_SDA
- track (21.85, 16.375)-(21.85, 15.164) w0.15 Top Layer /Top-Level Schematic/I2C1_SCL
- track (22.037, 14.978)-(22.037, 13.55) w0.15 Top Layer /Top-Level Schematic/I2C1_SCL
- track (21.85, 15.164)-(22.037, 14.978) w0.15 Top Layer /Top-Level Schematic/I2C1_SCL
- track (22.037, 13.55)-(22.091, 13.496) w0.15 Top Layer /Top-Level Schematic/I2C1_SCL (clipped)
- track (21.575, 16.65)-(21.85, 16.375) w0.15 Top Layer /Top-Level Schematic/I2C1_SCL
- track (19.45, 13.7)-(19.45, 11.696) w0.5 Top Layer GND (clipped)
- track (17.849, 13.125)-(18.75, 13.125) w0.2 Internal 1 3V3 (clipped)
- track (18.75, 13.125)-(20.179, 11.696) w0.2 Internal 1 3V3 (clipped)

## DAMP2: trimmed (dangling stub removed by tools/dangling.py, see blocks.json)
- track (30.4, 45.45)-(30.4, 44.996) w0.6 Top Layer GND (clipped)
- track (29.85, 46.0)-(30.4, 45.45) w0.6 Top Layer GND
- track (32.35, 45.9)-(32.35, 45.15) w0.6 Top Layer GND
- track (32.35, 45.15)-(32.504, 44.996) w0.6 Top Layer GND (clipped)
- track (29.6, 46.95)-(29.625, 46.925) w0.2 6 Bottom Layer GND
- track (29.625, 46.375)-(29.773, 46.227) w0.2 6 Bottom Layer GND
- track (32.9, 46.15)-(33.075, 46.325) w0.2 6 Bottom Layer GND
- track (29.399, 46.101)-(29.423, 46.077) w0.2 6 Bottom Layer GND (clipped)
- track (32.708, 46.15)-(32.9, 46.15) w0.2 6 Bottom Layer GND
- track (37.264, 51.114)-(37.264, 50.014) w0.2 6 Bottom Layer GND
- track (33.075, 46.925)-(33.075, 46.325) w0.2 6 Bottom Layer GND
- track (32.6, 46.95)-(32.6, 46.202) w0.2 6 Bottom Layer GND
- track (29.423, 46.077)-(29.773, 46.077) w0.2 6 Bottom Layer GND
- track (33.075, 46.925)-(33.1, 46.95) w0.2 6 Bottom Layer GND
- track (30.075, 46.925)-(30.1, 46.95) w0.2 6 Bottom Layer GND
- track (32.1, 46.95)-(32.1, 46.202) w0.2 6 Bottom Layer GND
- track (36.85, 49.6)-(37.264, 50.014) w0.2 6 Bottom Layer GND
- track (29.625, 46.925)-(29.625, 46.375) w0.2 6 Bottom Layer GND
- track (30.075, 46.925)-(30.075, 46.259) w0.2 6 Bottom Layer GND

## B18: trimmed (dangling stub removed by tools/dangling.py, see blocks.json)
- track (22.75, 44.025)-(22.75, 43.6) w0.2 6 Bottom Layer 1V8
- track (22.75, 43.6)-(22.949, 43.401) w0.2 6 Bottom Layer 1V8 (clipped)
- track (19.258, 47.51)-(19.768, 47.0) w0.2 6 Bottom Layer GND
- track (19.258, 47.557)-(19.258, 47.51) w0.2 6 Bottom Layer GND
- track (18.825, 48.3)-(18.771, 48.246) w0.2 6 Bottom Layer 3V3 (clipped)
- track (19.4, 48.3)-(18.825, 48.3) w0.2 6 Bottom Layer 3V3
