# Mock P: routing plan

Written 2026-11-17, evening PT, by the independent review agent. Companion to `REVIEW_P.md`; evidence in `out/`.
This is a plan, not a layout. Coordinates are in the mock's frame (X' from the N6's VIN-side edge towards P0, y
from the N6's USB-end edge towards the camera end, mm; KiCad x = 100 + X', y = 100 - y). "Trial" = the grid-router
run of `scripts/route.py` on a copy of mock P (`out/trial_log.txt`, `out/trial_extra_log.txt`,
`out/trial_routes_P.png`, `out/trial_routes_P_extra.png`); a trial path proves that a path exists at the project's
rules, nothing more. Corridors below are taken from the trial paths and from measured free space; where a number is
a proposal of mine and not a measurement it says so.

**Marked "UNVERIFIED" below: every place where the plan rests on something nobody has checked yet.** In one list:
1. A real N6: outline, header positions, which side P0 is on (two documents agree, no board measured).
2. The header part for a 5 mm gap: pin length, plastic, hole size, and whether the N6's own 9.19 mm pins are used.
3. The purpose of Sofar's two GND slots and of his two unconnected PWR-plane islands.
4. ADIN2111 datasheet Rev. B (pin pulls, SPI timing and strap table were read in Rev. 0), and the size of the
   internal pull-downs on CS, SCLK, SDI.
5. ST's limits for the STM32N657 pins (voltage on an unpowered pin, injection current, SPI setup time).
6. Heights of the mote's N6-facing parts; the screw and its head for the 2.7 mm holes.

## 1. Layers

Stackup JLC06161H-3313 as stored in the starting board: Top 35 um; 0.0994 prepreg; Internal 1 15.2 um; 0.55 core;
GND Plane 15.2 um; 0.1088 prepreg; Internal 2 15.2 um; 0.55 core; PWR Plane 15.2 um; 0.0994 prepreg; Bottom 35 um.
Internal 2 is the only signal layer next to the GND plane.

| Layer | Block (X' 5..30, y 0..48.5) | West wing (X' -6.1..5) | North row (y 48.8..58.8) | East strip (X' 28..35) |
|---|---|---|---|---|
| Top | Sofar's, locked. New: BM1 and BM2 tracks only | parts; one GND pour; 5 V trunk | connector pads; BM2 ends; GND pour | SPI series resistors; short ends |
| Internal 1 | Sofar's signals, locked | GND pour (shield under the converter) | GND pour | spare; at most single ends |
| GND Plane | Sofar's zone with his two slots | solid GND, joined to his over y 21.5..48.5 | solid GND | solid GND, one piece from row 1 to row 8 (UNVERIFIED 3) |
| Internal 2 | free but for two bus data pairs and one short track; our through-routes | motor logic lane, I2C lane, strap lines | I2C to QWIIC | SPI and control ends, N6 3V3 feed |
| PWR Plane | Sofar's five regions and two islands, pulled back from header pads | 5 V region from L6 to VIN and to U12; GND under the switch node | none under the BM2 tracks; GND elsewhere | Sofar's 3V3 region trimmed off the header pads |
| Bottom | Sofar's, locked | parts; one GND pour | GND pour | GND |

**Sofar's zones after the quarter turn.** The mock has none: the script deletes all zones. The starting board has
them: one GND-plane zone; on the PWR plane VBUS, 3V3, P_IN, ADIN_AVDD, ADIN_VDDIO and the islands NoConnect_Left /
NoConnect_Right; six small zones on the top layer, one on Internal 2, one on the bottom; and 152 unnamed rule areas
on the two planes (49 GND, 103 PWR). Plan:
- Turn the zones with the block in the build script, exactly as the footprints, tracks and the 17 copper shapes are
  turned now (same pivot, same move), instead of deleting them. My mapping of the starting board into the mock frame
  (`scripts/dump2.py`: rotation by a quarter turn, offset taken from U1, error 0.0 mm on L1, L2, U5) can serve as the
  check: zone outlines must land where `out/L3_gnd.png` and `out/L5_pwr.png` show them.
- Rule areas: keep those that lie inside the block, including the two slots (south: (14.4, 15.1) - (20.2, 15.1) -
  (25.5, 9.5) - (27.4, 6.85); north: (14.4, 34.9) - (26.0, 34.9) - (26.0, 41.8)). Drop the bands that follow the
  mote's old outline (X' 4.0..6.5 on the west, the ones beyond X' 28 on the east), or our new planes will not join
  his. End both slots at the block's edge (X' about 28). UNVERIFIED 3: ask Sofar first; if he wants the slots
  carried to the board edge, the SPI return path must be re-thought (REVIEW_P P2).
- Do not include the Pi Zero board's own zones (names beginning "S3", "GND top fill at U10") or its four screw
  keep-outs.
- Header pads: on the starting board Sofar's VBUS region ends 0.14 mm from the P14 pad copper and his 3V3 region
  covers the east inner column. Remove the unused inner-layer pads of J21 / J22 and hold every zone 0.5 mm from
  header pad copper and 0.3 mm from header holes (a rule in the `.kicad_dru`, which needs Nick's word, or by
  trimming the outlines).
- Our new zones, named so the lock check can tell them from his (the Pi work used "S3 ..."): GND on the GND plane
  for the wing, the north row and the east strip, overlapping his zone by 0.5 mm or more; GND on Top, Internal 1
  and Bottom in the wing and the north row; 5 V on the PWR plane in the wing. Settings as the Pi Zero board's added
  zones (clearance 0.3, minimum width 0.25, spokes 0.5 / 0.3, per `STAGE3_REPORT.md`); solid connection at the
  converter's and the motor driver's GND pads and at heat vias.

## 2. Net classes

Project default today: track 0.2 mm, clearance 0.127 mm, via 0.6 / 0.3 mm (`jlc_rules_2026-11.md`). Proposed
classes; the widths are checked against IPC-2221 (my arithmetic in `scripts/bm1.py`: external 35 um, 2.0 mm 3.95 A,
1.4 mm 3.05 A, 0.6 mm 1.65 A, each at 10 degC rise; internal 15.2 um, 2.0 mm 1.08 A, 1.0 mm 0.65 A).

| Class | Nets | Width | Clearance to other nets | Vias | Other constraint |
|---|---|---|---|---|---|
| Bus | BM1_P, BM1_N, BM2_P, BM2_N (connector to inductor) | 2.0 mm; neck 1.4 mm at most 3 mm long; 0.6 mm only between a connector's two pins | 0.127 mm by rule, 0.3 mm wherever there is room (as drawn the minimum is 0.18 mm) | none: top layer only | Sofar's 0.2 mm data branches untouched. No PWR-plane copper under new bus track outside the block. 0.5 mm to the board edge |
| 5 V | 5V_PI: L6, C56..C58, VIN pin, U12 | 2.0 mm on top, or the PWR-plane region plus 4 vias at each end | 0.2 mm | 0.6 / 0.3, 4 or more per layer change | bulk capacitor at U12 stays at U12 |
| VBUS feed | VBUS: Sofar's copper to C54, C55, U10 pin 3 | 1.0 mm (input current 0.37 A at 16 V and 1 A load, `power_budget.md`) | 0.3 mm, and 0.3 mm to every P_IN item | 2 if it changes layer | must start on VBUS, never on P_IN (the shunt R8 lies between) |
| Motor out | MOTOR_OUT1, MOTOR_OUT2 | 0.6 mm; 0.2 mm for the first 1 mm at U12's pads | 0.2 mm | 2 per layer change | 1 A in spikes (BRIEF). Keep 1 mm from VISEN and the wiper |
| Motor logic | MOTOR_IN1, MOTOR_IN2, MOTOR_nSLEEP | 0.2 mm | 0.2 mm between them, 0.5 mm to other signals | 1 at each end | Internal 2 in the wing. PWM up to 100 kHz (MP6550 datasheet). Not on an outer layer within 3 mm of the 5 V switch node |
| SPI | ADIN_SCK, ADIN_MOSI, ADIN_MISO, ~ADIN_CS | 0.2 mm | 0.4 mm between SPI tracks where they run side by side (my proposal); 0.127 mm at pads | at most 1 new per net, with a GND via within 1 mm | total 20 mm or less from U1 to the header pad (trial 15 to 18 mm); spread 5 mm or less; one track per gap between header pads, centred; Internal 2 for the new part |
| ADIN control | ~ADIN_INT, ~ADIN_RST, ADIN_PWR | 0.2 mm | 0.2 mm | 1 | static or slow; not on the top layer under T1 |
| I2C | I2C0_SCL, I2C0_SDA (one bus: U4, U13, QWIIC, P4 / P5) | 0.2 mm | 0.2 mm; 0.5 mm to motor nets | 2 at most per branch | Internal 2 under the north row; pull-ups at the east header on the N6's 3V3 |
| Analog | MOTOR_VISEN, POT_WIPER, U12's ISET net | 0.2 mm | 0.5 mm to motor outputs, motor logic, 5 V switch node | 1 | shortest path (8 and 6 mm in the trial); GND on the plane below |
| Straps | CFG0_STRAP, CFG1_STRAP, ADIN_VDDIO to JP3 / JP4 | 0.2 mm (VDDIO 0.3 mm) | 0.2 mm | 3 at most | DC only; R9 and R2 / R47 stay within 2 mm of their U1 pins |
| LEDs | ~ADIN_P1_LED1, ~ADIN_P2_LED1, ADIN_LED_VDD, the pin 19 net | 0.2 mm | 0.2 mm | 2 | parts not placed yet; Sofar's vias at (10.86, 18.08) and (19.12, 22.64) |
| N6 3V3 | the N6's 3V3 pins to pull-ups and QWIIC pin 2 | 0.4 mm | 0.2 mm | 1 | never joined to the mote's 3V3 (SPEC constraint 4) |

## 3. Routing stages

Baseline of the mock as it is (my DRC on the copy): 3 errors (data-pair skew, inherited), 122 unconnected. The
unconnected count will change when the schematic is updated, so stage 0 must record its own baseline. Lock set to
protect in every stage: the 81 mote footprints, Sofar's 870 track segments and 185 vias, his 17 copper shapes, and
his zones once they are in. Each stage: one script, one commit, then DRC, lock check, project-file check, as in the
Pi Zero work (`run.sh <phase>`).

| Stage | Nets | Corridor and layer | Gate before the next stage | Trial support |
|---|---|---|---|---|
| 0. Base | none | schematic of section 4 imported; placement changes of section 5 made; Sofar's zones turned in | DRC: the 3 skew errors and nothing else; record unconnected and parity; lock check written and PASS against the starting board; `out/L3_gnd.png`-style plot of every plane looked at | none |
| A. Bus | BM1_P, BM1_N (drawn in the mock), BM2_N, BM2_P | Top only. BM1: as drawn, start at the pads' east ends; neck BM1_N to 1.6 mm between the via at (20.06, 7.46) and L1 pad 1. BM2_N: L2 pad 2 straight north, X' 19.7..21.7, y 48.2..52.5, to J9 pins 1, 2. BM2_P: along Sofar's stub to about (17.9, 42.5), north at X' 14.9 from y 44.3 to 49.6, then under J9's body to pins 3, 4 | DRC as base; each connector pin reported connected to its inductor pad; no bus copper under 0.18 mm from another net (aim 0.3); 0.5 mm to the edge; lock PASS | BM1: DRC clean as drawn. BM2: 3.7 mm and 21.5 mm at 2.0 mm, top only, no via; five other row arrangements tried, none better |
| B. Planes | GND, 5V_PI region, Sofar's regions re-cut | section 1 | zones refilled; DRC as base; no new isolated copper; GND fill of the GND plane is one island apart from Sofar's own count; the east strip is one piece from y 0.3 to 21; the 15 unused N6 pins touch no zone; plots of all six layers looked at | not trialled (the router has no zones of ours) |
| C. Power | VBUS feed; 5 V to VIN; 5 V to U12; motor outputs; converter heat vias | VBUS: from Sofar's VBUS copper at R8 pad 1 / the vias at (6.7..7.4, 23.5..25.6), bottom layer, about (7.4, 27.8) - (5.8, 29.7) - (5.8, 31.3), to C54 pad 1; 0.3 mm from the P_IN vias at (7.26..8.21, 29.9..32.1). 5 V: top, X' -1.8 from y 24.8 to 7.4, then to VIN at (1.56, 4.13) north of hole H1's keep-out, plus the PWR-plane region. Outputs: U12 to J7, top and bottom, X' 1.5..2.3, y 40..54. Eight or more GND vias within 3 mm of U10 pin 1 | DRC as base; unconnected down by these nets; VBUS feed touches no P_IN item; lock PASS | VBUS 4.8 mm at 1.5 mm; 5 V 21.3 mm at 2.0 mm; U12 supply 3.5 mm at 1.5 mm; outputs 13.0 and 14.3 mm (at 0.3 mm only: router limit at the 0.2 mm pads) |
| D. SPI and ADIN control | SCK, MOSI, MISO, CS; INT, reset, ADIN_PWR; SCL / SDA from Sofar's stubs to P4 / P5 | From Sofar's stub ends at X' 26.2..28.4, y 12.6..16.1 through the series resistors in the east channel (X' 28.6..30.5) to P0..P3; new part on Internal 2. INT to P6: (28.4, 12.4) - (28.4, 10.6) - (31.2, 7.9) - P6. Reset to P9: from Sofar's via (10.81, 18.68), Internal 1, (9.4, 16.1) - (7.5, 16.1) - (4.6, 13.3). ADIN_PWR to P13: Internal 2, (15.9, 14.4) - (12.9, 12.9) - (10.8, 12.9) - (4.9, 7.0), under the BM1 tracks. MOSI's stub ends on Internal 1 at (26.51, 14.60) without a via: add one there | DRC as base; SPI lengths U1 to pad listed and within the class limits; no SPI track over a slot or a PWR-region edge on the bottom layer; a GND via beside each new SPI via; lock PASS | SCK 6.7, MOSI 8.2, MISO 5.4, CS 8.5 mm; INT to P6 10.1 mm; reset to P9 8.7 mm; ADIN_PWR 19.2 mm; SCL 7.1, SDA 8.5 mm. Depends on the pin swap being accepted (else INT to P9: 19.9 mm under U1) |
| E. Motor logic and sense | MOTOR_IN1, IN2, nSLEEP; VISEN; pot wiper | Logic: from U12 west at y 37.8, down the lane X' -5.6..-4.6 on Internal 2 from y 37.6 to about 16, then south-east to P7 (1.56, 6.67), P8 (1.56, 9.21), P14 (4.10, 9.21). VISEN: bottom, (3.8, 40.7) - (8.3, 45.2), one via to U13 pin 4. Wiper: top, U13 pin 5 to J8 pin 2 | DRC as base; none of the three logic lines on an outer layer between y 22 and 37.5; 0.5 mm from VISEN to any motor net; lock PASS | lane proven with the direct path blocked: 38.0 to 39.5 mm each, one line per layer in the trial (three side by side on Internal 2 need 0.85 mm of the lane's 1.7 mm, my arithmetic); straight path 30 to 32 mm; VISEN 8.3 mm; wiper 6.3 mm |
| F. I2C branches and N6 3V3 | SCL / SDA to U13 and to QWIIC; N6 3V3 to the pull-ups and QWIIC pin 2; mote 3V3 to U13 (if that rail is kept) | To U13: from Sofar's bus vias at (9.93, 25.41) and (10.66, 25.21), Internal 2, north through the block's west side to U13 pins 9, 10 at (5.27, 44.2..44.7). To QWIIC: Internal 2, (6.5, 45.1) - (13.7, 45.1) - (16.2, 47.6) - (20.6, 47.7) - (26.5, 53.6). N6 3V3: Internal 2, X' 32.8 between the east header's two pad columns from y 4.0 to 47.2, then to J3 pin 2. Mote 3V3 to U13 pin 8: top, from (13.1, 37.3) | DRC as base; N6 3V3 and mote 3V3 are different nets with no copper in common (SPEC constraint 4); lock PASS | to U13 25.9 and 32.6 mm; to QWIIC 22.3 to 24.8 mm; N6 3V3 52.7 mm at 0.4 mm; mote 3V3 9.8 mm |
| G. Straps, LEDs, test points | CFG0_STRAP, CFG1_STRAP, ADIN_VDDIO to JP3 / JP4; LED nets; test points | Straps: bottom in the wing, then Internal 1 / Internal 2 round the north end of the west header to U1's west side. LEDs: not placed yet | DRC as base; 0 unconnected; lock PASS; ERC and schematic parity 0 | CFG1 17.4 mm; CFG0 27.9 mm (3 vias); VDDIO 18.2 mm. LEDs and test points not trialled |
| H. Finish | silkscreen, fiducials, heat-copper check, review | silkscreen inside the edges (three labels are clipped today); 1.0 / 0.15 mm text | DRC warnings read one by one; independent review; then Nick | none |

Order of stages A, B, C follows the Pi Zero work (trunks, planes, power, then signals), so that the wide copper
and the plane cuts are fixed before thin tracks depend on them.

## 4. Schematic changes to make first

References and nets are those of the starting board (read with `scripts/startnets.py`, `startconn.py`) and of
`FIRST_PASS.md` section 1. New parts have no reference yet.

| # | Change | Parts | Nets |
|---|---|---|---|
| 1 | Remove the VBUS-out switch | U11, C59, R34, R36, R41, R42, D3, C49, pads J5. Inside the block, on Nick's decision (FIRST_PASS question 5): R35, C50, R11, TP19, TP35 | PAYLOAD_EN, ~PAYLOAD_FAULT, VBUS_OUT go |
| 2 | Remove the 5 V jumper, fuse and AUX pads | JP1, F1, J4 | 5V_LIFEPO4 goes; PI_5V and 5V_PI become one net from L6 to the N6's VIN pin and U12 |
| 3 | Remove the Pi header and pad rows | J1, J15..J19 | spare GPIO nets go; ~ADC_ALERT loses its pin (R49 stays as its pull-up or goes with it); ADIN_TIMER ends at R47 and a test pad; the second I2C bus (I2C3) goes |
| 4 | Add the two N6 headers | J21 (west), J22 (east), 2 x 8 through-hole, pins as in `N6_FACTS.md` | 15 positions without a net: nine Ethernet, RAW, BOOT0, PWR WKUP, P10, P11, RESET (16 if the reset line is dropped). UNVERIFIED 1, 2 |
| 5 | Pin map | header pins | P0 MOSI, P1 MISO, P2 SCK, P3 CS, P4 SCL, P5 SDA, P7 MOTOR_IN1, P8 MOTOR_IN2, P14 MOTOR_nSLEEP, P13 ADIN_PWR, VIN 5 V, both GND. Proposed and open: P6 ~ADIN_INT, P9 ~ADIN_RST (PIN_MAP's last section) |
| 6 | CS pull-up | new 10 k, 0402 | ~ADIN_CS to ADIN_VDDIO. UNVERIFIED 4 |
| 7 | SPI series resistors | four new 0402, 33 ohm to start | SCK, MOSI, CS between header pin and Sofar's stub; MISO between the stub (after R9's tap) and the header pin |
| 8 | Keep | R43 (100 k on ADIN_PWR), R1 (1.5 k INT pull-up), R9, R2, R47, JP2..JP4, D8..D10, R44..R46 | |
| 9 | I2C | R26, R27 (4.7 k) now to the N6's 3V3 pin; QWIIC J3: GND, N6 3V3, SDA, SCL on the one bus | I2C0_SCL, I2C0_SDA; PI_3V3 renamed for the N6. R10 and R24 (10 k on PI_3V3): I did not find what they pull; check before keeping |
| 10 | U13 and pot supply | decision: mote 3V3 (9 mm away in this mock) or N6 3V3 (44 mm) | changes what the pot is measured against |
| 11 | Connector symbols | J7, J8, J9, J10 to the top-entry parts (BM04B / BM03B-GHS-TBT), J3 to BM04B-SRSS-TB | pin order kept: N on pins 1, 2, P on pins 3, 4 |
| 12 | Mounting holes | three 2.7 mm holes; decide whether they are bare or grounded | |

After the change: ERC, netlist diff against the mote for every kept net (SPEC constraint 3), and schematic parity 0
on the stage 0 board.

## 5. Placement changes before routing

| # | Change | From | To (proposal) | Why |
|---|---|---|---|---|
| 1 | J10 (BM1) | origin (8.74, 3.67) | 0.5 mm east: (9.24, 3.67); 0.09 mm then remains to L1's courtyard | bus pads 0.96 mm from the N6's 3V3 / BOOT0 pin pads (REVIEW_P P1) |
| 2 | U12 group (N6 side) | U12 at (1.29, 40.33) | U12 at about (-2.0, 45.0), its capacitors round it; keep 3 mm to hole H2's keep-out (y 53.3) | 6.4 mm from U10 today; about 12 mm after (my arithmetic). Optional |
| 3 | SPI series resistors and CS pull-up (new) | not placed | top face, east channel, X' 28.6..30.5, one each level with P0, P2, P3 and at MISO's stub end (28.38, 15.08) | 2.45 mm free of top courtyards there (measured); 0402 across the channel is tight, along it is safe |
| 4 | R26, R27 (I2C pull-ups) | not placed | east strip beside P4 / P5, N6-facing side | fed from the east 3V3 pin 5 to 8 mm away |
| 5 | R37, R38 (converter feedback) | N6 side under U10 | top face, north of U10 (y 36.7..38.4 is free on top) | frees via room under U10; C53 must stay where it bridges pins 2 and 6 |
| 6 | Small parts not in the mock | | R9 at MISO's stub as on the Pi board; R2, R47 at U1 pin 19's via (10.79, 19.34); R1, R43 where the Pi board has them relative to the block; LEDs and JP2 in the wing beside the header (109 mm2 free on top) | none has a place yet |
| 7 | Fiducials and test points | none | three fiducials per face; test points on SCK, MISO, INT, 5 V, VBUS, GND | bring-up and JLC assembly |

## 6. Risks, and what would force a change of outline

| Risk | Sign | Effect on the outline |
|---|---|---|
| UNVERIFIED 1: the header is mirrored on the real N6 | P0 found on the left seen from the back | the wing must go to the other side or the block turn half a turn; mock P is void |
| UNVERIFIED 2: the header part needs a wider land or its plastic hits J10 or the parts beside the header | part chosen | J10 moves east (0.09 mm left after change 1) or the south edge grows; the 5 mm gap may change |
| Sofar wants the GND slots carried to the edge (UNVERIFIED 3) | his answer | no outline change; the SPI return needs another answer (for example stitching capacitors across the slot at the east header) |
| BM1_P at the south edge | fab house or potting needs more than 0.5 mm of edge | south edge 0.2 to 0.5 mm further out |
| Heat: converter, motor driver and L2 in one quadrant | bench temperature of U10 or L1 / L2 too high before potting | more copper means a wider wing (west edge) or a longer north end |
| Screw head at H2 against J7, or at H1 against the 5 V trunk | screw chosen | holes move; the west edge follows (it was set by the holes) |
| QWIIC or POT cable ESD into the I2C bus and the ADC | no protection parts in the schematic (not checked) | none; parts fit in the north row's free 69 mm2 on top |
| JLC assembly rails | their answer | none to the board; panel only |
| The 15 unused N6 pins shorted by a plane | stage B gate | none |

What does not threaten the outline: the bus (both ports route at 2.0 mm on top), SPI (unchanged from L), the
channels beside the block (2.0 mm west, 2.1 mm east at the narrowest, every layer).
