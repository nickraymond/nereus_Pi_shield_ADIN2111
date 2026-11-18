# Mock L (N6 shield, 45.56 x 56.2 mm): independent placement review

Written 2026-11-17, 5:10 PM PT. Reviewer: independent agent, read-only. Nothing in the git worktree or in the mock
was changed (mock file MD5 before and after: `522c6048154cde871a15363a5c569c8f`); all work was done on a copy in
`review_L/copy/`.

**Verdict: ROUTABLE WITH CHANGES. Three things must be fixed before any routing (stray holes and copper in the
mock file, the motor driver's position, the gap between the boards); the rest of the board routes in a trial at the
project's rules, including all four bus trunks at 2.0 mm and SPI at 15 to 18 mm.**

How to read the evidence:
- Frame: X' from the N6's VIN-side edge towards its P0 column, y from the N6's USB-end edge towards the camera end,
  mm (KiCad x = 100 + X', KiCad y = 100 - y). N6 outline X' 0..35.56, y 0..44.45. Shield outline X' -10..35.56,
  y -7.3..48.9.
- "Measured" = read from the mock copy with pcbnew (`scripts/dump.py`, `dump2.py`) or computed on a 0.05 mm raster
  of its copper (`scripts/rast.py`, `corridors.py`, `measure.py`; output in `out/measure.txt`).
- "Trial" = my grid router (`scripts/route.py`): track clearance 0.127 mm, vias 0.6 / 0.3 mm, hole clearance 0.3 mm
  (plated pad holes) and 0.25 mm (vias, mounting holes), edge clearance 0.5 mm, Sofar's copper and his outer-layer
  and Internal 2 zone fills (from the starting board) kept as obstacles, nets routed one after another. A trial path
  proves that a path exists; it is not a layout. Plot: `out/trial_routes.png`.
- "Starting board" = `N6_Shield_ADIN2111/Nereus_Pi_Shield_Adin2111.kicad_pcb` in the worktree. Its zones were mapped
  into the mock frame with the block's own quarter turn (checked on U1, L1, L2, U5: 0.0 mm error). Plots:
  `out/L3_gnd.png`, `out/L5_pwr.png` and the other `out/L*.png`.
- "My arithmetic" marks numbers I calculated from sourced values.

## Findings, ranked

| # | Rank | Finding | Evidence | Change I recommend |
|---|---|---|---|---|
| B1 | Blocker | The mock file still holds the Pi Zero board's four 2.75 mm mounting holes and 17 copper shapes. One hole is inside the board at (16.97, 7.16), under L1: it cuts both BM1 data tracks on Internal 2 and touches D2's VBUS pad, L1 pad 4 and C17. A BM2_N copper polygon lies in the south strip (top X' 27.8..31.1, y -7.6..-4.5; bottom X' 28.5..31.1, y -7.9..-5.6), a GND one at (24.95..26.25, -5.15..-3.75) | `kicad-cli pcb drc` on the copy: 6 hole-clearance errors at that hole, 2 edge-clearance errors on the BM2_N polygons (`out/drc_mock_L.json`); `scripts/shapes.py` lists the shapes and three holes outside the outline. Cause: `n6_rough_board.py` keeps footprints by reference, and the new holes reuse H1..H4; it removes tracks and zones but not copper graphics | Remove the old holes and the copper graphics in the script before this file becomes the base of the real board. Any STEP or drill file exported from mock L today contains them |
| B2 | Blocker | The motor driver U12 cannot be wired where it sits (N6-facing side, under J7, centre (-2.10, 2.42)). Its east pads end 1.46 mm from the header's pad copper, and four nets (IN1, IN2, nSLEEP, VISEN) leave on that side. Through-vias cannot be placed at it because J7's pads are on the other face | Trial: with the PWM lines routed first, VISEN has no path; with VISEN first, nSLEEP has no path. Motor outputs route only at 0.3 mm (no path at 1.0 or 0.6 mm). Area where a GND via centre may sit: 0.01 mm2 within 1.5 mm of U12's centre, 1.0 mm2 within 1.5 mm of its GND pin (`out/measure.txt` section 7) | Move U12 about 3 mm west and 2.6 mm north, to about (-5.0, 5.0): under J7's housing but clear of J7's pads (signal pads y 1.05..2.75, tab pads X' below -8.2 and above -1.75). That gives about 4.3 mm to the header pads and via sites on all sides. Then two or more vias on GND, 5 V and each output |
| B3 | Blocker | The gap between the boards is not proven. A plain header gives about 2.5 mm (FIRST_PASS). The N6's LiPo connector leads stand 2.09 mm proud at X' 22.56..28.56, y 0.2..7.9 and face D4 and TP3 of the mote block; its microSD socket (1.46 mm, X' 0.56..11.96, y 21.2..33.1) faces 13 mote parts (C5, C10, C20, C28, R7, R8, R20, R22, R23, TP1, TP2, TP22, U4). With mote parts of about 1.3 mm (FIRST_PASS) the stack needs 3.4 mm and 2.8 mm | `out/measure.txt` section 4; N6 positions from `n6_research_raw.md` (3D model r3), mirrored X' = 35.56 - x. The heights of the individual mote parts were not checked | Choose the header part and spacer first and set the gap to 4 mm or more, or prove each overlap in CAD. The gap also sets how far the N6's pins stand above the shield's top face |
| M1 | Major | The bus trunks are 6 to 17 mm long, not "about 2 mm". The bus pads of L1 and L2 (pads 2 and 3) are on the inductors' east side. J9 sits west of L2 behind L2's P_IN and GND pads; J10's pin row is on the far (south) side of its land pattern | Pad to pad: BM1_P 6.1 mm, BM1_N 14.7 mm, BM2_P 13.2 mm, BM2_N 15.4 mm. Trial at 2.0 mm: 6.2 / 15.2 / 15.0 / 16.7 mm. Both N lines need Internal 1 (0.5 oz) and two layer changes; on the top layer alone BM2_N passes only at 0.6 mm (no path at 1.0 mm) | Turn J10 half a turn (pin row at y about -1.7, BM1_P then about 3 mm). Accept the N trunks on Internal 1 at 2.0 mm with four or more vias at each end (16.6 mm is 9.4 mohm, 8 mV at 0.89 A, my arithmetic). Leave the PWR layer empty under the new trunks, as Sofar does under his bus copper (his "NoConnect" islands). Give both ports the same pin order |
| M2 | Major | Both N6 ground pins are in header row 8 (y 1.59). Sofar's south GND-plane slot runs from (14.4, 15.1) over (20.2, 15.1), (25.5, 9.5), (27.4, 6.85) and, on the starting board, on to the east edge at y 6.7..7.0. Carried to the edge again, it puts P5 (34.0, 6.67) and the PWR WKUP pin in the slot and the east ground pin on the far side of it from the SPI pins | Slot rule areas of the starting board mapped into the mock frame (`out/L3_gnd.png`, `out/measure.txt` section 2). The SPI return from P0..P3 to the east ground pin would then go round the slot's root at X' 14.4: about 34 mm of detour (my arithmetic) | End that slot at the block's edge (X' about 28). Make the east strip (X' 28..35) one unbroken GND area from row 1 to row 8, joined to the main plane north of the slot. Ask Sofar what the two slots are for before changing anything inside the block |
| M3 | Major | Two ADIN control lines are mapped to the west header (INT on P9, ADIN_PWR on P13) although every stub Sofar left for them ends on the east side (X' 25.0..28.4) | Trial: INT to P9 19.9 mm on Internal 2, under U1 and past the crystal side (route at y 16.1..16.9, Y1 at X' 8.9..12.0, y 13.6..16.5), under three PWR-plane regions. ADIN_PWR to P13 19.2 mm, through T1's footprint on the top layer. Reset to P6 on the east: 6.6 mm | Put INT on P6 (east, about 6 to 7 mm) and reset on P9, or drop the reset line (the pin may float, SPEC). Route ADIN_PWR on Internal 2, not under T1 |
| M4 | Major | Power states of the SPI pins are not handled. ADIN2111 CS, SCLK and SDI have internal pull-downs, so CS is low (selected) whenever the N6's pins float. The schematic has no pull-up on CS and no series resistors. SPI and INT pins are rated to VDDIO + 0.3 V, and VDDIO is 0 V while ADIN_PWR is low | ADIN2111 Rev. 0 Table 8 and absolute maximum table (`dl2/a_comp.txt`); nets of the starting board (`scripts/startnets.py`): ~ADIN_CS has only U1.45 and the header; ADIN_PWR has R43 100 k | Add 10 k from CS to ADIN_VDDIO (the switched rail, so it cannot back-feed); check it against the internal pull-down, whose value I did not find. Add 0402 series resistors: SCK, MOSI, CS at the N6 header, MISO at U1 after R9's tap, 33 ohm to start. Keep R43. Firmware: hold SCK, MOSI, CS low or floating until ADIN_PWR is high and the chip is up |
| M5 | Major | Heat is a whole-board question at full pass-through current, and the wing gives less copper than stated. Free for a pour in the wing above the header: 245 mm2 on top, 278 mm2 on the N6-facing side (box 287 mm2), not about 400 mm2 per face: J9 took the north end of that strip in mock L | `out/measure.txt` section 6. By TI SNVA419 Eq. 9 (as quoted in FIRST_PASS) the whole 2560 mm2 board carries 1.67 W at 40 degC rise. Losses from `power_budget.md` and FIRST_PASS add to about 0.8 W typical (20 degC) and about 2.2 W with 0.89 A through both inductors and 1 A at 5 V (54 degC), free air (my arithmetic). The N6 adds 0.75 W 2.5 mm behind | Keep 200 mm2 or more of GND copper per face at U10 (available), with no signal tracks on the outer layers of the wing. Join the wing's planes to Sofar's GND plane along the whole length y 21..41. Put eight or more GND vias within 3 mm of U10's GND pin (room measured: 14 mm2). Measure U10 and L1 / L2 temperatures on the bench before potting |
| M6 | Major, if the card is used | The west wing covers the N6's microSD slot from behind. The socket is at X' 0.56..11.96, y 21.2..33.1 and opens towards the N6's VIN-side edge; the wing extends 10 mm past that edge with L6 and U10 on one face and JP4 on the other | N6 research notes (model r3) and OpenMV's pinout image, which labels the slot on that edge | Decide whether the card must be reachable with the shield fitted (question 8 of FIRST_PASS). If yes, notch the wing over y 21..33 or move the converter |
| m1 | Minor | North edge: Sofar's GND via at (23.56, 48.16) is 0.44 mm from the edge (rule 0.5 mm); L2's courtyard is 0.41 mm and 32 V copper (L2's pad) 0.74 mm from it | DRC on the copy; `out/measure.txt` section 5 | Move the north edge 0.3 to 0.5 mm out |
| m2 | Minor | Mounting holes sit 2.3 mm from the edges with a 3 mm corner radius: 1.25 mm of board to a straight edge and 0.96 mm towards the rounded corner (my geometry). The camera hangs from this board | Hole positions from the mock; outline from the script | Holes 3.0 mm or more from both edges, if the housing allows |
| m3 | Minor | Strap legend: text is 0.8 mm high and 0.13 mm thick (project rule 1.0 / 0.15 mm), and two legends run past the west edge | DRC: `silk_edge_clearance` on "ADIN SPI STRAPS 0 \| 1" and "0 / 0 = OPEN ALLIANCE + CRC" | Three or more short lines at 1.0 mm |
| m4 | Minor | No fiducials or tooling features; parts on both faces (68 N6-facing parts inside the N6 outline, two of them ours: R37, R38); J7's body 0.85 mm from the west edge, J10's 1.85 mm from the south edge | `scripts/shapes.py`, `scripts/fab.py` | Three fiducials per face; ask JLC for assembly rails; move R37, R38 and C53 to the top face |
| m5 | Minor | SPI and I2C pass between the N6's live Ethernet pins (inner east column): 0.84 mm between pads. The trial tracks passed 0.13 to 0.31 mm from those pads | `out/measure.txt` section 3 | One track per gap, centred (0.32 mm each side), on Internal 2 |
| m6 | Minor | The plane next to the converter is P_IN (before the shunt R8), not VBUS. Nearest VBUS copper is Sofar's via at (9.71, 33.43), 6.4 mm from C54; P_IN vias are closer | `out/L5_pwr.png`; trial VBUS route 6.4 mm at 1.5 mm | Take VBUS from that via or from the VBUS plane south of y 29; mark P_IN as keep-off, or the power monitor will not see the converter's current |
| m7 | Minor | Header pads: with the unused inner-layer pads kept, the plane web between two header holes is about 0.44 mm; without them 0.94 mm (my arithmetic). On the starting board Sofar's VBUS plane edge is 0.14 mm from the P14 pad copper and his 3V3 plane covers the east inner column | `out/measure.txt` section 1 | Remove unused pad layers on J21 / J22; pull Sofar's PWR-plane regions back 0.5 mm or more from every header pad |
| m8 | Minor | U13 and the pot are fed from the mote's 3V3 rail in the schematic; the nearest mote 3V3 copper is 18.7 mm away (trial 21.0 mm, three layers), the N6's 3V3 pin about 11 mm | Trial; pad positions | Decide the rail at schematic time; the N6's pin is the shorter feed |

## 1. Routing feasibility, net by net

Header pin positions used (from `N6_FACTS.md`, pads measured in the mock: 1.70 mm pads, 1.00 mm holes, 0.84 mm
between pads): rows y 19.37 (row 1) down to 1.59 (row 8) in 2.54 mm steps.

| Column | X' | Rows 1 to 8 |
|---|---|---|
| East outer | 34.00 | P0 MOSI, P1 MISO, P2 SCK, P3 CS, P4 SCL, P5 SDA, P6, 3V3 |
| East inner | 31.46 | Ethernet LED, B-, B+, A-, A+, PWR WKUP, RAW, GND |
| West inner | 4.10 | Ethernet C+, C-, D+, D-, P14, P13, BOOT0, 3V3 |
| West outer | 1.56 | RESET, P11, P10, P9, P8, P7, VIN, GND |

The mock's columns are 0.04 mm further apart than the model's (32.44 against 32.40 mm outer to outer).

**Left / right sense.** I checked the assumption against a second source: OpenMV's pinout image shows the camera
side with P0..P6 on the left and the USB-C connector right of centre, and the model has P0 at x 1.56 and USB-C at
x 18.9..28.5. So the model's x runs left to right seen from the camera side, and P0 is on the right seen from the
back, as the mock assumes. This is two documents agreeing, not a measurement on a board. If it were mirrored: the
SPI pins would be on the west, 17 mm or more across the block from Sofar's stubs and past the crystal; VIN, P7, P8
and P14 would be on the east, away from the converter and the motor driver; the wing would have to move to the
other side or the block turn half a turn (U1 then sits at y 26..34, above the header rows). Mock L would not survive.

**Channels beside the block** (`scripts/corridors.py`, raw copper, rows y 0.3..20.6):

| Channel | Top | Internal 1 | Internal 2 | Bottom | Top parts | Bottom parts |
|---|---|---|---|---|---|---|
| West: header pad edge X' 4.95 to Sofar's copper, minimum | 2.00 mm | 2.00 | 2.00 | 2.00 | 2.25 | 2.05 |
| East: header pad edge X' 30.61 to Sofar's copper, minimum | 2.10 mm | 2.95 | 3.75 | 3.75 | 2.45 | 4.25 |

The channels are free on every layer; the minimum on the west is one via at y 16.7. Sofar's plane fills still have
to be cut back from them.

| Net | Pad to pad | Trial result | What is in the way | Verdict |
|---|---|---|---|---|
| BM1_P: L1 pad 3 to J10 | 6.1 mm | 6.2 mm, top, 2.0 mm | nothing | clear |
| BM1_N: L1 pad 2 to J10 | 14.7 mm | 15.2 mm at 2.0 mm, 13.2 mm of it on Internal 1 under L1, 2 layer changes; top only: 18.5 to 20.8 mm round L1's east side | L1's own pads 3 and 4 (1.27 mm between them) | tight |
| BM2_P: L2 pad 3 to J9 | 13.2 mm | 15.0 mm, top, 2.0 mm, along Sofar's 2 mm stub between L2's pads | T2 and its vias | clear |
| BM2_N: L2 pad 2 to J9 | 15.4 mm | 16.7 mm at 2.0 mm on Internal 1; top only 0.6 mm at most | L2 pad 1 (P_IN), four P_IN vias, the north edge 0.74 mm from the pad | tight |
| VBUS to U10 | 6.4 mm to Sofar's via (9.71, 33.43) | 6.4 mm, top, 1.5 mm | six P_IN vias 0.2 mm beside the path | clear |
| 5 V: L6 / C56 / C57 to VIN | 22.6 mm | 24.4 mm at 2.0 mm (top 5.2, Internal 1 19.2) | nothing; a plane is the better answer | clear |
| 5 V to U12 | 0.7 mm to the trunk | 4.0 mm at 1.0 mm | see B2 | clear after B2 |
| Motor outputs to J7 | 3.4 and 0.4 mm | 0.3 mm only | U12's 0.2 mm pads, J7's pads on the other face | blocked as placed (B2) |
| MOTOR_IN1 / IN2 / nSLEEP to P7 / P8 / P14 | 4.9 / 5.3 / 7.7 mm | 5.5 / 7.7 mm; nSLEEP no path (or VISEN no path, by order) | 1.46 mm between U12 and the header pads | blocked as placed (B2) |
| MOTOR_VISEN: U12 to U13 | 10.6 mm | 11.8 mm, bottom, when routed first | same | blocked as placed (B2) |
| SCK to P2 | 6.4 mm from Sofar's via | 6.7 mm; total from U1 16.8 mm | Ethernet pads | clear |
| MOSI to P0 | 7.8 mm | 8.2 mm; total 18.4 mm | Ethernet pads | clear |
| MISO to P1 | 5.0 mm | 5.4 mm; total 15 to 17 mm | Ethernet pads | clear |
| CS to P3 | 8.0 mm | 8.5 mm; total 18.4 mm | Ethernet pads | clear |
| INT to P9 (west) | 16.2 mm | 19.9 mm, Internal 2, under U1 | the block itself, the crystal side | tight (M3) |
| Reset to P6 (east) | 6.3 mm | 6.6 mm, Internal 1 | crosses the south GND slot's line | clear |
| ADIN_PWR to P13 (west) | 16.3 mm | 19.2 mm, top, through T1's footprint | the block | tight (M3) |
| SCL / SDA: Sofar's stubs to P4 / P5 | 6.5 / 8.1 mm | 7.1 / 8.5 mm | P5 sits on the slot's line (M2) | clear |
| SCL / SDA to U13 | 19.0 / 18.3 mm from Sofar's bus at U4 | 31.6 / 28.9 mm, Internal 2 and bottom, 2 vias each | round the north end of the west header | clear, long |
| SCL / SDA to QWIIC | 6.0 / 5.7 mm | 6.6 / 6.8 mm | nothing | clear |
| Pot wiper: U13 to J8 | 2.1 mm | 2.5 mm | nothing | clear |
| CFG1 strap: JP3 to U1 pin 19 | 16.3 mm | 16.9 mm | west header's north end | clear |
| CFG0 strap: JP4 to MISO at U1 | 24.2 mm | 26.2 mm, under U1 on Internal 2 | the block | clear, long |
| ADIN_VDDIO to JP3 / JP4 | 13.5 mm | 16.1 mm at 0.3 mm | nothing | clear |
| ADIN LEDs | not routed: D8..D10 and their resistors have no place. Sofar's vias: P1_LED1 (10.86, 18.08), P2_LED1 (19.12, 22.64) | | | not checked |

Where Sofar's copper leaves no room: nowhere in the channels. The limits are our own placement (U12), the
inductors' pad order (bus N lines) and the Ethernet pins of the N6 header.

## 2. Power planes and stackup

Stackup read from the starting board: top 0.035 mm; prepreg 0.0994; Internal 1 0.0152; core 0.55; GND Plane 0.0152;
prepreg 0.1088; Internal 2 0.0152; core 0.55; PWR Plane 0.0152; prepreg 0.0994; bottom 0.035; ENIG. Internal 2 is
the only signal layer close to the GND plane (0.11 mm); Internal 1 is 0.55 mm from it and 0.10 mm under the top.

| Layer | Block (Sofar) | West wing | South strip and east strip |
|---|---|---|---|
| Top | his parts and copper, untouched | parts; GND pour for U10 and U12; no long tracks | BM1_P trunk; GND elsewhere |
| Internal 1 | his signals (SPI stubs run here) | GND pour (heat, shield under the converter) or the 5 V trunk | BM1_N trunk under L1; SPI and I2C ends |
| GND Plane | his plane with his two slots | solid GND joined to his plane over y 21..41 | solid; east strip unbroken from row 1 to row 8 (M2) |
| Internal 2 | free except his two bus data pairs and one short track | all our long logic: I2C to U13, straps, PWM | INT or reset, SPI ends |
| PWR Plane | his VBUS, 3V3, P_IN, AVDD, VDDIO regions, pulled back from the header pads | 5 V from L6 down to VIN and U12; GND under the switch node | no copper under the bus trunks |
| Bottom | his parts | GND pour; U12, U13, straps | GND |

- **Sofar's zones after the quarter turn.** The starting board carries his GND plane, five PWR-plane regions (VBUS, 3V3, P_IN,
  AVDD, VDDIO), two unconnected islands and 152 rule areas on the two plane layers (49 on GND, 103 on PWR). Most rule areas are bands along the mote's old outline
  (for example X' 4.0..6.5 from y -4.7 to 54.3); two are real slots in the GND plane: the south one described in
  M2 and a north one from (14.4, 34.9) over (26.0, 34.9) and (26.0, 41.8) to the east edge at y 41.6..42.0. Carry
  the slots, drop the outline bands, or the wing's planes will not join his.
- **Return paths over splits.** SPI stays north-east of the south slot (Sofar's stub ends are 4.2 to 5.9 mm from it,
  the P3 pad 4.9 mm; the P4 pad is 2.4 mm from its line). Reset to P6
  crosses the slot's line; it is static. I2C to U13 and both strap lines pass under several PWR-plane regions on
  Internal 2, which is referenced to the GND plane 0.11 mm away, so that is acceptable. Tracks on the bottom layer
  are referenced to the PWR plane 0.10 mm above them: keep PWM and I2C off the bottom layer where that plane
  changes region. INT on Internal 2 under U1 passes under three regions (VDDIO, AVDD, VBUS) (M3).
- **Necks.** Header holes: 0.94 mm of plane between antipads if unused pads are removed (m7). Mounting holes: with
  0.25 mm hole clearance and 0.5 mm edge clearance only 0.5 mm of copper is left between hole and edge; leave that
  ring bare. 32 V copper is 7.4 mm or more from every mounting hole.
- **Stitching.** A GND via beside every layer change of SCK, MOSI, MISO, CS (ADIN2111 layout advice); a row of GND
  vias where the wing's planes meet the block (X' 5..6.5, y 21..41); a 3 to 5 mm grid in the wing, which is also
  the heat path.

## 3. SPI robustness

- **Length and skew.** U1 pad to header pad: SCK 16.8, MOSI 18.4, MISO 15 to 17 (depending on which of Sofar's two stub
  ends is used), CS 18.4 mm (Sofar's copper
  9.9 to 10.2 mm plus the trial ends). Spread under 4 mm. The ADIN2111 asks for 5 ns data setup and hold and gives
  SDO 12 ns after the falling clock edge into 10 pF (Rev. 0 SPI timing table); at 25 MHz the half period is 20 ns,
  at 10 MHz 50 ns. The N6's own trace lengths and its SPI setup time were not found.
- **Reference.** Sofar's SPI section is on Internal 1, 0.55 mm above the GND plane and 0.10 mm under C22's pads.
  It is his vetted copper. Put the new ends on Internal 2 with a GND via at the change.
- **Series resistors.** The runs are short against any plausible edge, so the resistors are for edge rate and
  fault current, not matching: the ADIN2111's inputs are specified with 5 ns edges, the only ground pins are 10 to
  18 mm down the header from the SPI pins, and the tracks pass between live Ethernet pins. 22 to 47 ohm, 33 ohm
  first; at the source of each line. The east channel has room: 2.45 mm free of top courtyards, 4.25 mm on the
  N6-facing side.
- **Aggressors** (2-D distance to the SPI copper, any layer): 3.3 V switch node 10.1 mm; 5 V switch node 19.6 mm;
  crystal nets 6.3 mm, on the far side of U1; motor PWM 19.8 mm. Nearest are Sofar's own: CLK25_REF 1.6 mm from CS
  at the chip, and his I2C tracks cross his SPI tracks on another layer. Nothing of ours is close.
- **Unpowered cases.** See M4. With R43 (100 k) the ADIN is off whenever the N6's P13 floats, so MISO and INT
  cannot drive an unpowered N6. The opposite case is open: an N6 pin driven high into an ADIN whose VDDIO is 0 V.
  The N6's pin limits were not found.
- **Power-up.** Supplies up to SPI ready: 50 ms at most; after a reset 90 ms (SPEC). INT asserts after every reset
  and needs R1 (1.5 k to VDDIO), which is in the schematic. CS: add the pull-up.
- **Straps.** R9 (4.7 k) on MISO and R2 / R47 on pin 19 must stay within about 2 mm of U1 so they add no stub; only
  their DC side runs to JP3 / JP4 (16.9 and 26.2 mm in the trial, harmless). SDO goes high-impedance 15 ns after
  CS rises, so R9 sets the level when the pin is read. A wrong strap selects another protocol (Table 22: generic
  SPI, or OPEN Alliance without protection); the host then gets no valid answer. It does no damage.
- **Placement changes for a cleaner SPI:** INT to the east header (M3); the east strip as one GND area (M2);
  series resistors in the east channel; nothing else of ours within 10 mm of the SPI ends, which is the case today.

## 4. Thermal

| Part | Loss | Copper in this mock | Via room | Note |
|---|---|---|---|---|
| U10 | 0.39 W at 0.65 A, 0.53 W at 1 A | wing above the header: 245 mm2 top, 278 mm2 N6-facing side free for a pour (182 / 269 mm2 outside all courtyards) | 3.7 mm2 within 1.5 mm of the GND pin, 14.4 mm2 within 3 mm | C53, R37, R38 sit on the other face under U10 and take via room |
| U12 | 0.06 to 0.34 W | south-west corner: 77 mm2 top, 79 mm2 N6-facing side | none as placed (B2) | 80 degC/W junction to ambient (MP6550 datasheet): 27 degC at 0.34 W |
| L1, L2 | up to 0.52 W each | Sofar's copper, unchanged | his | L1 is over the N6; L2 straddles the N6's camera-end edge |
| U5 | within the 0.30 W allowance for the 3.3 V domain | Sofar's | 2.7 mm2 within 3 mm | fixed with the block |

- Hot parts cluster in the north-west: U10 to L6 7.2 mm, U10 to U5 13.7 mm, U5 to L2 11.1 mm, U10 to L2 20.9 mm.
  The south-west and the east are cool.
- U10's own rise by `power_budget.md`: 42 / 31 degC at 0.39 W and 57 / 42 degC at 0.53 W (107.8 / 80 degC/W),
  on top of the board's average rise in M5.
- Potting fills the 2.5 mm gap and couples the shield's heat to the N6 (0.75 W of its own). SPEC constraint 8
  applies: free-air figures cannot be trusted. Not modelled.

## 5. JLC manufacturability of the placement

- DRC on the copy (`out/drc_mock_L.json`): 657 items, 169 unconnected. Errors: 6 hole clearance and 3 mask bridges
  at the stray hole (B1), 3 edge clearance (m1 and the stray polygons), 3 skew (Sofar's data pairs, known). No
  courtyard overlap. The project ignores "hole inside courtyard" checks, so I checked courtyards separately:
  closest pairs are J21 / U12 0.08 mm and J22 / R15 0.03 mm, no overlap.
- Connector bodies (KiCad's fab outlines): J7 to J8 3.60 mm, J8 to J3 3.65 mm. J9 is 2.55 mm from L2's courtyard
  and 2.6 mm from T2; J10 2.1 mm from L1's courtyard. All meet the 2 to 3 mm wish.
- Through-hole soldering from the top face: nearest top copper to the west header's pads is J7's tab pad, 1.46 mm
  away; J7's body is 1.04 mm from the header's body outline. Tight for an iron beside a mated-height connector,
  workable. The east header is clear.
- Header pads: ring 0.35 mm, hole 1.00 mm, hole to hole 1.54 mm: inside the project's rules.
- Both faces are populated; nothing of ours is under a through-hole pad. JP3 is directly under J3.

## 6. Other risks

- ESD parts at MOTOR, POT and QWIIC: not checked in the schematic.
- With the N6's stacking pins (9.19 mm behind the N6 in the model) and a 2.5 mm gap, about 5.1 mm of pin would
  stand above the shield's top face among the connectors (my arithmetic). Trim, or choose the header to suit.
- No test points of ours are placed. SCK, MISO, INT, 5 V and VBUS need one each for bring-up.
- U10's input capacitor C54: VBUS pad 2.4 mm from the VIN pin, GND pad 4.8 mm from the GND pin, as carried over
  from the Pi Zero board. TI asks for it "as close as possible". Not compared with TI's layout figure.

## Not checked

- No real N6 was measured; all N6 geometry is from the r3 model and OpenMV's pinout image.
- Heights of the mote's N6-facing parts; the header part, its pin size against the 1.00 mm holes, the real gap.
- The purpose of Sofar's two GND slots and of his "NoConnect" islands.
- ST's pin limits and SPI timing for the STM32N657; the ADIN2111's internal pull-down values; Rev. B of its
  datasheet (I read the Rev. 0 text).
- JST's GH drawings (the PDF is encrypted and could not be read): land patterns and body sizes are KiCad's.
- JLC's rules for fiducials, assembly rails and hole-to-edge distance: not in `jlc_rules_2026-11.md`, not fetched.
- Thermal behaviour in potting; any simulation; coupling from the converter into the bus.
- The trial router cannot taper a track or place several vias, so widths at fine-pitch pins are pessimistic and
  via counts for the 2 mm trunks are not proven. Parts of ours that are not in the mock (LEDs, pull-ups, strap
  resistors, test points, series resistors) were not placed.
- I2C bus capacitance and rise time with the 4.7 k pull-ups; the LED nets.

## Files

- `REVIEW_L.md` (this report); `scripts/` (all measurement and trial scripts); `out/measure.txt`;
  `out/drc_mock_L.json`; `out/trial_routes.png` and crops; `out/L1_top.png` .. `out/L6_bottom.png`;
  `copy/` (the copy of mock L that was analysed).
