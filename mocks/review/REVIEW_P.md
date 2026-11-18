# Mock P (N6 shield, 42.16 x 60.7 mm): independent placement and routing review

Written 2026-11-17, evening PT. Reviewer: independent agent, read-only. The worktree and the mock were not changed
(mock file MD5 before and after: `66b5e7c74849714bce48a32c9d95202e`); all work was done on `review_P/copy/`.
Companion: `ROUTING_PLAN_P.md` (the plan the designer can execute).

**Verdict: ROUTABLE, NO BLOCKER. Every net group routed in a trial at the project's rules, both bus ports at
2.0 mm on the top layer without vias. One placement change should be made before routing (BM1's bus pads are
0.96 mm from the N6's 3V3 and BOOT0 pins); the open items from the mock L review that concern planes, pins and
the schematic still stand.**

Method, frame and terms are those of `review_L/REVIEW_L.md`: X' from the N6's VIN-side edge towards its P0 column,
y from the N6's USB-end edge towards the camera end; "measured" = read from the mock copy or its 0.05 mm raster;
"trial" = my grid router (clearance 0.127 mm, vias 0.6 / 0.3 mm, hole clearance 0.3 / 0.25 mm, edge 0.5 mm, nets
one after another), an existence proof and not a layout. New in this run: Sofar's 17 copper shapes are part of the
obstacle set, because they now sit at their true places. Plot: `out/trial_routes_P.png`; log: `out/trial_log.txt`;
numbers: `out/measure.txt`, `out/bm1.txt`; DRC: `out/drc_mock_P.json`.

DRC on the copy (`kicad-cli pcb drc`, all severities): 3 errors, the inherited data-pair skew ones; 122 unconnected
items; no clearance, hole or edge error. One of the unconnected items is on BM1_P, between a bottom track and a via
of Sofar's; the two new BM1 tracks are not in the list.

## What happened to the mock L findings

| L finding | Status on mock P | Evidence |
|---|---|---|
| B1 stray holes and copper | **Closed** | no hole inside the block; the 17 shapes sit on L1, L2, C22, C23 and neighbours; DRC has no error at them |
| B2 motor driver cannot be wired | **Closed** | U12 now at (1.29, 40.33): IN1, IN2, nSLEEP, VISEN all route (32.1, 31.7, 30.4, 8.3 mm). Two corrections to my L report below |
| B3 board gap | **Closed on paper** by the 5 mm gap (3.4 mm needed). Depends on a header part that does not exist in the project yet | FIRST_PASS; heights of the mote's parts still not checked |
| M1 bus trunks long, inner layers | **Closed for BM1** (drawn, DRC clean). **Closed for BM2 once drawn**: trial 3.7 mm and 21.5 mm, both 2.0 mm, top layer, no via | `out/bm1.txt`, trial |
| M2 south GND slot and the east strip | **Open, unchanged** | same block, same header |
| M3 INT / reset pin swap | **Open, a decision**; the swap works on this outline: INT to P6 10.1 mm, reset to P9 8.7 mm. Without it INT to P9 is 19.9 mm under U1 | trial, both variants |
| M4 CS pull-up, series resistors, firmware hold-off | **Open** (schematic) | recorded in `PIN_MAP.md` as proposals |
| M5 heat | **Open, changed**: see P5 | `out/measure.txt` section 6 |
| M6 microSD slot covered | **Mostly closed**: the wing is 6.6 mm wide, the gap 5 mm, and nothing of ours is on the N6-facing side of the wing between y 21 and 33 | bottom-side plot `out/L6_bottom.png` |
| m1 north edge | no longer applies (edge moved to y 59.3) | |
| m2 mounting holes | **Closed**: 2.7 mm holes 3.0 mm from the edges, 1.65 mm of board to each edge | pad positions |
| m3 strap legend | text size now 1.0 / 0.15 mm; **still clipped** by the west edge ("0\|1  0/0=OA+CRC"), and "POT" and "BM2" are clipped by the north edge | DRC `silk_edge_clearance` |
| m4 fiducials; R37, R38, C53 on the N6 side | **Open** | |
| m5 one centred track between Ethernet pins | **Open** (a routing rule; in the plan) | |
| m6 the plane beside the converter is P_IN | **Open, tighter**: C54's VBUS pad is 1.06 mm from Sofar's P_IN vias; nearest VBUS copper 4.1 mm | trial VBUS route 4.8 mm |
| m7 inner header pads, plane pull-back | **Open** | `out/measure.txt` section 1 |
| m8 U13 supply | **Reversed**: the mote's 3V3 is now the near one (9.0 mm; trial 9.8 mm on top); the N6's 3V3 pin is about 44 mm away | trial |

Two corrections to my mock L report (B2). The figure "0.01 mm2 for a via within 1.5 mm of U12's centre" is a
property of the 2 x 2 mm package, not of that placement: it is the same here. And "motor outputs route only at
0.3 mm" is a limit of my router, which cannot widen a track after leaving a 0.2 mm pad: it is the same here. What
stood in L and is gone in P is the failed route (four nets in 1.46 mm).

## Findings on mock P, ranked

| # | Rank | Finding | Evidence | Change I recommend |
|---|---|---|---|---|
| P1 | Major | BM1's pads and track ends are 0.96 mm from the pad copper of the N6's 3V3 and BOOT0 pins and 1.22 mm from P13. Those header pins are soldered by hand on this face, after JLC has fitted J10, whose body stands 1.99 mm from them. A solder bridge puts up to 32 V on the N6's 3.3 V rail | `out/measure.txt` section 5; `scripts/fab.py`. J10's courtyard overlaps the header's by 0.51 mm in plan (other face, so DRC is silent) | Move J10 0.5 mm east (0.59 mm is free to L1's courtyard) and start the 2 mm tracks at the pads' east ends, not at the pin centres: about 1.5 mm to the header pads. Put the lower-voltage polarity question aside: both P pins are next to 3V3 and BOOT0 whatever the order. Add a note for assembly: header first is not possible, so inspect these four joints |
| P2 | Major | Open from L (M2): how Sofar's south GND slot ends decides the SPI return path. Unchanged geometry: slot from (14.4, 15.1) to (27.4, 6.85); P5 and PWR WKUP on its line; both N6 ground pins in row 8 | `review_L/out/L3_gnd.png`; `out/measure.txt` section 2 | As in L: end the slot at X' about 28, east strip one GND area from row 1 to row 8. Stage 2 of the plan |
| P3 | Major | Open from L (M4): no CS pull-up, no series resistors, no rule for SPI pins while the ADIN is off | ADIN2111 Rev. 0 Table 8; nets of the starting board | Schematic list in the plan, section 4 |
| P4 | Major | The three motor logic lines now run 30 to 32 mm from the driver to P7, P8, P14, and the straight path lies under the 5 V converter: the trial put them at X' 2.1 to 2.7, under U10's switch pin (2.47, 32.67) and L6's switch pad (X' 0.7..2.3) | trial segments in `out/routes_all.json`; in mock L these runs were 5 to 8 mm | Route them on Internal 2 only, in the lane X' -5.6..-4.6 west of L6, with the GND plane above; cross to the header south of y 20. Keep them off the outer layers under the converter |
| P5 | Minor | The converter and the motor driver now share one copper area and are 6.4 mm apart (33.7 mm in L). Free for a pour in the wing above the header: 258 mm2 top, 279 mm2 N6 side (box 300 mm2); the converter's own part (y 21.5..37.5) has 139 / 173 mm2. With the wing beside the header (109 / 98 mm2) the wing gives 367 / 377 mm2 if it stays one piece | `out/measure.txt` sections 6 and 8 | One GND pour per outer face over the whole wing, no tracks across it on the outer layers. Move U12 north-west to about (-2.0, 45.0), about 12 mm from U10 (my arithmetic). Whole-board figure unchanged from L: 2559 mm2, about 1.67 W at 40 degC rise by SNVA419 Eq. 9 |
| P6 | Minor | BM1 tracks as drawn pass the rules with little to spare: BM1_N is 0.18 mm from a BM1_P via at (20.06, 7.46) and 0.21 mm from L1's VBUS pad; BM1_P is 0.23 mm from L1's GND pad and exactly 0.50 mm from the south edge | `out/bm1.txt` | Neck BM1_N to 1.6 mm for about 2 mm where it passes between that via and L1 pad 1 (0.4 mm each side). Keep the south edge where it is or 0.2 mm further out |
| P7 | Minor | BM2's two tracks differ by 17.8 mm (N 3.7 mm, P 21.5 mm). No inner layer and no neck is needed, and no other order of the row does better | trial of six arrangements, below | Keep J9 where it is. Draw P along Sofar's stub and west of L2 |
| P8 | Minor | North row: J7's and J9's courtyards are 0.45 mm from the north edge (bodies 1.05 mm); J7's courtyard is 0.10 mm from hole H2's; all three row gaps are 1.26 mm between courtyards and 3.5 to 3.6 mm between bodies; the row is 0.81 mm from L2's courtyard | `scripts/fab.py` output | Fine for JLC's edge rule. Check the screw head at H2 against J7's body (3.89 mm from the hole centre) once the screw is chosen |
| P9 | Minor | In the trial the I2C branch to QWIIC ran on Internal 1 under L2's pads and the BM2_N track, 0.10 mm below them | `out/routes_all.json` | Plan stage 7: Internal 2 along y 49.4..51.0 under the connector row, GND plane between it and the bus |
| P10 | Minor | With the N6's own pins (9.19 mm behind the N6 in the model) and a 5 mm gap, 2.6 mm of pin stands above the top face, 1 mm from BM1's pads (my arithmetic) | N6 research notes | Settle the header part; trim or cover |

## Detail on what is new

### BM1 as drawn

| | BM1_N | BM1_P |
|---|---|---|
| New copper, top layer | 2.0 mm, 19.7 mm in the mock's total; 0.6 mm link between the two pins | 2.0 mm for 15.4 mm, 1.4 mm neck for 2.7 mm, 0.6 mm link |
| Resistance of the wide parts (35 um), at 0.89 A | 6.0 mohm, 5.3 mV, 4.7 mW | 5.1 mohm, 4.6 mV, 4.1 mW |
| Nearest foreign copper, top | BM1_P via 0.18; L1 pad 1 (VBUS) 0.21; T1 pad 6 0.35; GND via 0.52 mm | L1 pad 4 (GND) 0.23; T1 pad 7 0.28; Sofar's GND shape 0.33; GND via 0.43; J10's tab pad 0.48 mm |
| Under it, Internal 1 | nothing; ~ADIN_RST passes 0.65 mm beside | nothing |
| Under it, Internal 2 | Sofar's own 0.2 mm BM1_P data track, behind the GND plane | nothing; BM1_N data track 0.53 mm beside |
| Under it, N6 side | D2, C16, C17 and a GND track (other face, three planes between) | C16 |
| Holes and edges | 1.31 mm to the nearest header hole | 1.32 mm; south edge 0.50 mm |

- Current capacity, IPC-2221 external conductor, 35 um (my arithmetic, `scripts/bm1.py`): 2.0 mm carries 3.95 A
  at 10 degC rise, the 1.4 mm neck 3.05 A, the 0.6 mm links 1.65 A. At 0.89 A the rise is 0.3, 0.6 and 2.5 degC;
  each link carries half the current. JST GH contacts are rated 1.0 A each (SPEC) and two share each polarity.
- Planes beneath: both tracks lie over Sofar's GND plane south of his slot and over his VBUS region of the PWR
  plane, which the GND plane screens. They need no plane cut. They do not cross either slot.
- The corridor is also needed by ADIN_PWR to P13 and nSLEEP to P14 (inner west column). Both routed in the trial
  on Internal 2 under the tracks. The top layer between the header and J10 is closed for anything else.

### BM2: is another place or turn of J9 better?

Trial, top layer only, N then P, widths tried 2.0 / 1.5 / 1.0 / 0.6 mm (`scripts/route.py ... bm2`, variants built
by moving J9's pads in a copy of the geometry):

| Arrangement of the row | BM2_N | BM2_P |
|---|---|---|
| **As placed: MOTOR, POT, BM2, QWIIC, J9's pins east** | **3.7 mm at 2.0** | **21.5 mm at 2.0** |
| J9 turned half a turn in place | 9.4 mm at 1.5 (no path at 2.0) | 15.9 mm at 2.0 |
| BM2 and POT swapped | 20.7 mm at 1.5 | 25.8 mm at 1.5 |
| swapped with POT and turned | 21.9 mm at 1.5 | 17.6 mm at 1.5 |
| BM2 and QWIIC swapped (BM2 last) | 8.5 mm at 2.0 | 18.8 mm at 2.0 |
| swapped with QWIIC and turned | 16.2 mm at 2.0 | 29.9 mm at 1.5 |

The placed arrangement is the only one with the shortest total at full width. "BM2 last" is the only other one at
2.0 mm on both and is better balanced (10.3 mm difference); it puts BM2 beside hole H3 and QWIIC further from P4 / P5.
BM2_P's path as placed: Sofar's 2 mm stub west between L2's pads, north at X' 14.9 from y 44.3 to 49.6, then under
J9's body to pins 3 and 4. J9's tab pad is 1.69 mm north of L2's P_IN pad.

### Motor driver and ADC

- U12 (N6 side, inside the N6's outline, 5 mm gap): via room within 3 mm of its GND pin 12.9 mm2, of its 5 V pin
  13.1 mm2. Outputs to J7: 12.3 and 13.1 mm pad to pad (trial 13.0 and 14.3 mm). VISEN to U13: 8.0 mm (trial 8.3 mm).
  5 V from the converter's output capacitors: 3.3 mm (trial 3.5 mm).
- U13 (top, X' 4.25..10.60, y 43.4..47.0): pot wiper to J8 pin 2 5.7 mm (trial 6.3 mm); I2C from Sofar's bus at U4
  18.5 mm (trial 25.9 and 32.6 mm through the block's inner layers; the plan gives a cleaner lane).
- 5 V to VIN: 20.0 mm, trial 21.3 mm at 2.0 mm on the top layer down the wing at X' -1.8, past hole H1's keep-out.
- South-west hole H1 (-3.6, 1.6): hole wall 2.96 mm from the GND and VIN pads' copper; 32 V copper 8.1 mm away.

### SPI on this outline

Unchanged from L, because the block and the east header did not move: SCK 6.7 mm, MOSI 8.2, MISO 5.4, CS 8.5 mm of
new track; totals 15 to 18 mm; east channel 2.10 mm (top) to 3.75 mm free; 2.45 mm free of top courtyards for the
series resistors. 5 V switch node now 16.3 mm from the SPI copper (19.6 in L), 3.3 V switch node 10.1 mm.

## Worse than in mock L

- Motor logic lines 30 to 32 mm instead of 5 to 8 mm, past the converter (P4).
- Converter and motor driver share the wing's copper (P5).
- 32 V copper 0.96 mm from N6 header pins (P1); in L the nearest was 2.5 mm.
- BM1_P at the south edge with no margin (P6).

## Not checked

- Everything listed under "Not checked" in `REVIEW_L.md` still applies: no real N6, heights of the mote's parts,
  Sofar's slots and islands, ST's pin limits, ADIN2111 pull-down values and Rev. B, JST drawings, JLC's fiducial
  and rail rules, potting, thermal simulation.
- The header part for a 5 mm gap, its pin length and plastic; the spacer method; the screw and its head size.
- The six BM2 arrangements were tried by moving pads in the geometry, not by rebuilding the board: courtyards of
  the moved connectors were not re-checked.
- Parts that are still not in the mock: LEDs, pull-ups, strap and series resistors, test points.
- Whether the schematic matches the board (no parity check: the schematic is still the Pi Zero one).

## Files

`REVIEW_P.md`, `ROUTING_PLAN_P.md`, `scripts/`, `out/measure.txt`, `out/bm1.txt`, `out/trial_log.txt`,
`out/drc_mock_P.json`, `out/trial_routes_P.png` (and crops `_north`, `_wing`, `_sw`, `_east`), `out/L1_top.png` ..
`out/L6_bottom.png`, `copy/`.
