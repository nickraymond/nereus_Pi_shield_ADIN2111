# N6 shield: first pass (what changes, size study, questions)

2026-11-17. Study and mocks only: no file in `N6_Shield_ADIN2111/` has changed. Companion files: `N6_FACTS.md`
(the N6, with sources S1 ...), `PIN_MAP.md` (pins and the explore questions). Mock images and data are outside git in
`~/NereusData/nereus_Pi_shield_ADIN2111/n6_shield/`. Scripts that produced the numbers: `scripts/n6_*.py`.

## 1. What goes and what changes, against the starting design

**Removed**

| Item | Parts | Note |
|---|---|---|
| VBUS out control | U11 (TPS26621), C59, R34, R36, R41, R42, D3, C49, pads J5; nets PAYLOAD_EN, ~PAYLOAD_FAULT, VBUS_OUT | all our own parts |
| The same circuit's parts inside Sofar's block | R35, C50, R11 (already not fitted), test points TP19, TP35 | these five sit at Sofar's positions (`scripts/n6_mote_extent.py` lists them in the 81). Removing them changes the locked block: question 5 |
| 5 V jumper and fuse | JP1, F1; net 5V_LIFEPO4 | U10's output goes straight to the N6's VIN pin |
| AUX 5 V pads | J4 | only if Nick agrees: question 3 |
| Pi header and pad rows | J1 (2x20), J15 to J19 | replaced by two 2x8 sockets for the N6 |
| Signals with no N6 pin | ~ADC_ALERT, ADIN_TIMER (to a test pad), the spare GPIOs, I2C3 as a separate bus | `PIN_MAP.md` |

**Changed**

| Item | Change |
|---|---|
| Sofar's mote block | turned a quarter turn as one rigid group with its copper; its inner-layer planes re-cut to the new outline, as on the Pi Zero board |
| 5 V converter U10 + L6 | same circuit, moved as a group, with much more ground copper (below) |
| Motor driver U12 | same circuit, more copper on its supply, ground and output pins, two or more vias where the Pi Zero board has one (open item in `HANDOVER_FOR_M.md`) |
| Header nets | re-mapped to the N6 (`PIN_MAP.md`); pull-up and Qwiic supply from the N6's 3V3 pin |
| Connectors | BM1, BM2, MOTOR, POT (JST GH) and QWIIC (JST SH): entry direction to be decided from the mocks |

**Kept as is:** power monitor U4, ADC U13 with the pot circuit, the LEDs D8 to D10 with JP2, strap jumpers JP3 / JP4.

## 2. Copper for the 5 V converter and the motor driver (first estimate)

Loads. The N6 draws 750 mW when active (S9), so 0.15 A at 5 V. The motor: 0.5 A steady, under 1 A in rare spikes
(Nick's bench figures, Pi Zero `BRIEF.md`). The 5 V rail therefore carries about 0.65 A steady, against 1.5 A on the
Pi Zero board.

Heat. U10's loss is 0.39 W at 0.65 A and 0.53 W at 1.0 A (`power_budget.md` section 3, U10's share). The MP6550's
loss is I² x (0.24 ohm typical, 0.34 ohm maximum): 0.06 to 0.09 W at 0.5 A, 0.24 to 0.34 W at 1 A (MP6550 datasheet
Rev. 1.0, p. 4).

Rule used. TI SNVA419C (AN-2020), Eq. 9: board area of 15.29 cm² per watt gives a 40 °C rise, for a two-sided board
with solid copper on both sides in still air. TI's LMR51430 datasheet (SLUSEF4A section 9.4.1) says the GND, VIN and
SW pins are the heat path, asks for those areas "as large as possible" and for a via array from the top ground
copper to the ground planes; it gives no area figure. Neither part has an exposed pad.

| Part | Loss used | Board area by Eq. 9 | Outer-layer copper today (measured) | First estimate |
|---|---|---|---|---|
| U10 | 0.39 W (0.53 W at 1 A) | 600 mm² (810 mm²) | 12 mm² top + 62 mm² bottom = 74 mm² | about 200 mm² of ground copper on each outer face (400 mm² in all, five times today's, the ratio of Nick's older board), with a via array into the ground plane so the rest of the board (2200 mm² and more) shares the heat |
| U12 | 0.09 W steady (0.34 W at 1 A) | 130 mm² (520 mm²) | not measured separately | about 100 mm² on each outer face, on the VIN, GND and both output pins, each with two or more vias |

This is an estimate from a rule of thumb for free air, not a thermal design; potting changes it (SPEC constraint 8).
The bench check of U10's temperature from the Pi boards stays open.

## 3. Size study

**The N6** is 35.56 x 44.45 mm = 1581 mm². Its two 2x8 headers occupy only the 20.6 mm nearest the USB end; the pads
of the two inner pin columns are 25.6 mm apart (`N6_FACTS.md`).

**Sofar's mote block**, measured on the starting board against Sofar's reference board
(`scripts/n6_mote_extent.py`): 81 footprints, courtyards 47.48 x 23.25 mm; with the copper that travels with it
46.92 x 25.80 mm; 47.5 x 25.8 mm in all. Top side: 15 parts including the tall ones (L1, L2, L3, C22, C23); bottom
side: 66 small parts over the whole area. Its last 20 mm at the L1 end are at most 21.3 mm wide.

**Result.**
- Turned a quarter turn, the block fits between the header rows: with its L1 end at the USB end, the gap from the
  block's copper and parts to the inner header pads is 1.9 mm on one side and 2.1 mm on the other
  (`scripts/n6_mocks.py` prints it). The ADIN2111 then sits right beside the SPI pins P0 to P3.
- The block is 47.5 mm long, so it is already 3 to 4 mm longer than the N6 (44.45 mm).
- The block fills the board between the headers on both faces. Beside it, beyond the headers, the N6's width leaves
  strips of 6.3 mm and 3.4 mm: room for connectors and the ADC, not for the 5 V converter (its group is
  10.2 x 12.6 mm, the inductor L6 alone 7 mm) or its copper.
- **So the shield cannot be the N6's size.** The converter, the motor driver and their copper need about 500 mm²
  more, either as extra length or as extra width.

| Mock | Outline | Area | Against the N6 |
|---|---|---|---|
| A, long | 35.56 x 62.5 mm | 2222 mm² | same width; 14 mm past the USB end, 4 mm past the camera end; +41 % area |
| B, wing | 48.6 x 53.5 mm (48.6 x 48.5 if the BM1 bus tracks fit in the 2 mm beside the block between the headers) | 2600 mm² (2357 mm²) | 13 mm wider on the VIN side, 4 mm past the camera end, 5 mm past the USB end; +64 % (+49 %) |
| C, east wing (Nick's idea, 2026-11-17) | 48.6 x 48.5 mm | 2357 mm² | nothing past the USB end; 13 mm wider on the P0 side, 4 mm past the camera end (the mote's own length); +49 % area |

**Mock C** puts the 5 V converter, the motor driver and the BM1 and MOTOR connectors in a 13 mm wing on the east
(P0 to P6) side; BM2, POT and QWIIC stay on the west edge. What it costs:
- The BM1 bus tracks must run from L1 (at the USB end, between the headers) through the 2.1 mm channel between the
  block and the east header pads for about 12 mm, then out to the wing: two tracks of about 1.4 mm on two layers.
  A 2 mm track cannot pass between header pads (0.84 mm between pads). Sofar's own copper is clear of that channel
  on every layer (the profile in `scripts/n6_mocks.py` counts all layers); his plane fills there would be re-cut.
  Not proven: no track was drawn or rule-checked. The Pi Zero board has a 1.4 mm neck in BM1 for 2.9 mm only.
- The motor inputs (P7, P8) and the sleep line come from the west header and VIN is on the west header, so three
  logic tracks and the N6's 5 V feed (0.15 A) cross the board. They are thin enough to pass between header pads.
  The motor's own current stays inside the wing.
- The converter is no longer beside the VIN pin, and the SPI pins P0 to P3 now have the converter 5 mm away on
  their other side.

**Mocks D, E and F** (Nick's ideas, 2026-11-17)

| Mock | Outline | Area | What it is |
|---|---|---|---|
| D, tall | 35.56 x 60.5 mm | 2151 mm² | N6 width, through-hole headers. South section of 12 mm: BM1 in the south-west corner, the 5 V converter on the south wall, motor driver and MOTOR connector in the south-east. POT with the ADC in the north-east corner beside L2, BM2 in the north-west corner, QWIIC on the west edge. Side or top entry |
| E, SMD headers | 45.0 x 54.5 mm | 2453 mm² | surface-mount headers on the N6-facing side, so the top face over the headers is free. Top-entry connectors lying east-west in two columns (BM1, QWIIC, BM2 west; MOTOR, POT east), the 5 V converter over the VIN header, four mounting holes |
| F, one column | 45.6 x 54.5 mm | 2485 mm² | as E, with all five connectors in one column on the east edge and the motor driver in that column; the 5 V converter alone on the west, over the VIN header |

- **D is the smallest outline so far** and keeps the N6's width. The BM1 bus tracks are about 8 mm long. The motor
  driver sits on the east as asked, so its three control lines cross the south section from P7 / P8 / P14 on the
  west header (about 30 mm, below the header rows). The south section's width is fully used (33.7 of 35.56 mm).
- **E and F: the surface-mount headers fit, with little room.** With KiCad's generic 2x8 SMD socket pattern (pads
  3.0 x 1.0 mm at 2.52 mm either side of the header centre; the real part is not chosen), the pads reach 4.0 mm
  inboard of each header centre. The mote block's bottom-side copper and parts between the headers are 19.9 mm wide,
  the pads leave 21.9 mm: about 1.0 mm each side once the block is moved 0.9 mm east. Not rule-checked.
- **E and F cannot be only as tall as the N6.** The mote block alone is 47.5 mm against 44.45 mm, and the two
  mounting holes at the USB end collide with the last header rows unless they sit in a 6 mm strip past the USB end
  (drawn) or the board gets about 6 mm wider instead. The holes are drawn at 2.7 mm with a 5.1 mm keep-out because
  the N6's own hole size was not found; smaller holes shrink that strip.
- **F answers "all connectors on one side".** It is 0.6 mm wider than E. Both bus runs are about 7 mm; the motor
  driver is beside its connector; only the N6's 5 V feed (0.15 A) and the motor's three control lines cross the
  board. The converter is beside the VIN pin.
- Open for E and F: the mated height of 7.3 mm plus wire bend above the shield; the strength of surface-mount
  headers when the camera hangs from the shield (the shield is screwed to the housing, the N6 hangs on the solder
  joints); which header part (socket for the N6's pins, or pins soldered into the N6) and its real land pattern.

**Rough boards and STEP files for mock D (top entry) and mock F** (Nick, 2026-11-17: "get me STEP files from KiCAD
with the rough layout"; header choice: "Pins soldered to the N6"). `scripts/n6_rough_board.py` builds them on scratch
copies outside git (`n6_shield/step_rough/`): the mote block turned as one group with Sofar's tracks, the converter,
motor driver and ADC groups, KiCad's library footprints for the top-entry JST parts, pin headers on the N6-facing
side (surface-mount on F) and four 2.7 mm holes on F. No zones, no routing of ours, small parts of ours left out.
What the real footprints showed:
- The top-entry JST land patterns are larger than the bodies drawn in the mocks: GH 4-pin 9.55 x 6.69 mm with its
  solder tabs, GH 3-pin 8.29 x 6.69, SH 4-pin 7.89 x 5.29 (courtyards of KiCad's footprints).
- **Mock D** still fits 35.56 x 60.5 mm, but only with the motor driver on the N6-facing side partly under the MOTOR
  connector; the south section is full.
- **Mock F** grows to 46.5 x 54.5 mm (2534 mm²); the five connectors fill the east column from the USB end to L2.
- On F the 5 V converter's three bottom-side parts (C53, R37, R38) land on the west header's pads: they must move
  to the top face when the converter is laid out again.
- **Gap between the boards, to check first in CAD.** A plain 2.54 mm pin header holds the boards about 2.5 mm apart
  (KiCad's model; the real part is not chosen). The N6's tallest back-side part is 2.09 mm (S5) and the mote's
  bottom-side parts face it. A taller spacer header may be needed.
- The STEP origin is the N6's board corner at the USB end on the VIN side; +X towards the P0 column, +Y towards
  the camera end. U12's 3D model file is missing from the project, so the 2 x 2 mm chip is not in the STEP.

**Mock G: mock F made narrower** (Nick, 2026-11-17: BM connectors and MOTOR on the west wall; pot, motor driver
and ADC on the south wall; rounded corners; "Connector spacing is 2-3mm between connectors", after the Blue Robotics
Ethernet Switch, https://bluerobotics.com/store/comm-control-power/tether-interface/ethswitch/, which uses the same
BM04B-GHS-TBT headers on a 64 x 46 mm board). Built as a rough board only (`n6_rough_board.py ... G`), 3 mm corners:
- **40.1 x 56.0 mm (2246 mm²)**: 6.4 mm narrower than F and 1.5 mm taller. The width is set by the top-entry GH
  land pattern (9.55 mm) west of the mote block and by the surface-mount header pads on the east (they reach 1.3 mm
  past the N6's edge).
- West wall, top face, from the USB end: MOTOR, BM1, QWIIC, then the 5 V converter with L6, then BM2. Connector
  bodies are 3.0 mm apart (land patterns 1.26 mm apart). BM1 is beside L1, BM2 beside L2. With this pitch the
  converter fits on the west wall too, clear of the header pads, 0.1 mm from the mote block's courtyards (tight).
- South wall (7.5 mm past the USB end): motor driver on the N6-facing side below the MOTOR connector, POT, and the
  ADC on the N6-facing side.
- Distances: converter to VIN about 17 mm; motor driver to P7 / P8 about 10 mm. Nothing but SPI crosses the board.
- Copper for the converter: the west strip beside it is narrow (10 mm), so its 200 mm² per face must come from the
  strip's length (about 20 mm) and the planes. Not laid out.
- With 3 mm between bodies, mock F's single east column also works: five connectors need 37 mm of its 48 mm.

**Mock H: after Nick's CAD check of mock G** (2026-11-17, screenshot of the shield over the N6 in his camera shell:
"make the mounting holes 2.1mm"; "shift the openMV board to south east corner while leaving room for the smaller
mounting screws"; then, asked: the N6 position in the screenshot is the target, and the outline may change).
Read from the screenshot, roughly (scaled from the board's known size, about 1 mm uncertain): the N6 sits about
3.7 mm from the shield's USB-end edge and flush with its P0-side edge. Built as a rough board (`... H`):
- **38.56 x 60.3 mm (2325 mm²)**, 3 mm corners. East edge = the N6's P0-side edge. South edge 4.6 mm past the N6's
  USB end. West edge 3.0 mm past the N6. North edge 11.25 mm past the N6's camera end.
- **Holes 2.1 mm**, centres 2.3 mm in from the edges: (-0.7, -2.3), (33.26, -2.3), (-0.7, 53.4), (33.26, 53.4) in
  the N6 frame (X' from the VIN-side edge, y from the USB-end edge). The two southern holes are 2.3 mm south of the
  N6's edge, the northern ones 8.95 mm north of it. Screw head and standoff sizes are not known to me.
- **East header through-hole, west header surface-mount.** Surface-mount pads would overhang the N6's edge by
  1.3 mm, which the flush east edge does not allow. Nothing of ours sits over the east header.
- **Everything of ours on the west wall, top face, from the USB end:** BM1, MOTOR, POT, QWIIC, the 5 V converter,
  BM2; connector bodies 3.0 mm apart. BM1 is beside L1, BM2 beside L2. The motor driver and the ADC are on the
  N6-facing side of the same strip, above the header (motor driver under POT / QWIIC, ADC next to it, partly under
  the converter: the converter's three bottom-side parts must move to the top face anyway).
- The south wall is empty: 4.6 mm is too shallow for a connector land pattern (6.69 mm).
- The height comes from the west column: four GH, one SH and the converter need 51 mm. With 2.0 mm between
  connector bodies it would be 5 mm less.
- Not checked: the N6 parts under the west strip (gap between the boards), copper for the converter and the motor
  driver now that they share the west strip, and all routing.

**Mock I: both headers through-hole** (Nick, 2026-11-17: through-hole "is better for alignment and shear stress
resistance"; "keep the BM1 and BM2 connectors on the west side with the 5V reg, then move the other connectors to
the east wall"). Built as a rough board (`... I`), 2.1 mm holes, 3 mm corners:
- **43.7 x 59.5 mm (2600 mm²)**. West edge 4.3 mm past the N6, east edge 3.8 mm past the N6's P0-side edge, south
  edge 4.6 mm past the USB end, north edge 10.45 mm past the camera end.
- **Why it is wider than H.** Through-hole pads go through the board, so nothing of ours can sit over a header on
  either face. Both columns therefore start above the header rows (y 21 mm and up). On the east, the mote block
  leaves only 3.4 mm inside the N6's width, so a connector (6.69 mm across when turned along the wall) needs the
  board 3.8 mm past the N6's edge: **the east edge is no longer flush with the N6.**
- West wall, from the header upward: BM1, the 5 V converter, BM2. East wall: MOTOR, POT, QWIIC, turned so their pin
  rows run along the wall, bodies 3.0 mm apart. Motor driver under MOTOR and ADC under POT, on the N6-facing side.
- The mote block goes back to the centre between the pad rows: 1.9 mm and 2.1 mm to the pads, as in mocks A to D.
- **What this arrangement costs electrically (not routed, to weigh before choosing):**
  - BM1 sits above the header, so its two bus tracks run about 7 mm from L1 through the 1.9 mm channel between
    the mote block and the west header pads (the unproven channel of mock C, shorter).
  - The motor driver is on the east, the 5 V converter and the PWM pins P7 / P8 on the west: the motor's 5 V supply
    (0.5 A) and three control lines cross the board, round the south or north end, about 60 mm. The Pi Zero board
    has PWM runs of 58 to 62 mm (`review_G_routing.md`), so there is a precedent, not a proof.
- Alternative that keeps the east edge flush with the N6: put MOTOR, POT and QWIIC on a north wall instead
  (about 39.9 x 60.6 mm). Not built.

**Mock J: mock I with the BM connectors at the north and south ends, east edge flush** (Nick, 2026-11-17: "the BM
connectors should move to the north and south ends, so make the shortest possible traces between the inductors";
"how can we make it so the east edge is flush again"; "Consider routing"). Built as a rough board (`... J`), both
headers through-hole, 2.1 mm holes, 3 mm corners:
- **35.56 x 66.8 mm (2375 mm²): exactly the N6's width, flush on the east and the west.** South edge 7.3 mm past
  the USB end, north edge 15.05 mm past the camera end.
- South strip: MOTOR and BM1 on top, the motor driver under MOTOR. North strip: the 5 V converter and BM2.
  Pocket beside L2: POT on top, ADC under it. West strip above the header: QWIIC.
- The east edge is flush because nothing of ours is on the east: inside the N6's width the mote block leaves only
  3.4 mm there.

Routing considered (lengths from the placement coordinates; **nothing is routed or rule-checked**):

| Net | Run in mock J | Verdict |
|---|---|---|
| BM1, BM2 bus tracks (2 mm wide) | about 2 mm each, L1 to BM1 and L2 to BM2, no channel beside the block | best of all mocks |
| ADIN SPI | about 16 mm to P0..P3, unchanged | fine |
| Motor outputs | about 2 mm, driver under its connector | fine |
| Motor PWM and sleep (P7, P8, P14) | about 12 to 15 mm south from the west header. Three tracks must pass the header: 0.84 mm between the two pad columns, or the 1.9 mm channel beside the mote block. They run away from the ADIN's crystal (which sits 4 mm inside the block's west edge, level with header rows 2 and 3) | fits, tight |
| 5 V, converter to VIN and to the motor driver | about 50 to 55 mm down the west side, 0.65 A steady. About 27 mOhm and 18 mV on a 1 mm, 1 oz track (my arithmetic), or on the power plane. The motor's bulk capacitors stay at the driver, so the long run carries the average current | longest power run of any mock |
| VBUS to the converter | about 15 mm past L2 on an inner layer; Sofar's VBUS plane ends at about y 35 mm | fine |
| I2C to the ADC (north-east) | about 35 mm up the 3.4 mm east strip from P4 / P5 | fine, slow bus |
| I2C and 3.3 V to QWIIC (west) | about 40 mm round the north end from P4 / P5 | long but slow; QWIIC has no better place at this width |

- Why the converter is north and the motor south, not the other way round: with the motor in the north its PWM
  lines would run 50 mm up the west side within about 3.5 mm of the ADIN's crystal (the Pi Zero lesson). Putting
  the converter, BM1 and MOTOR all in the south strip would be best for power, but they need 34.2 mm in a row and
  the strip has 26.4 mm between the two mounting holes.
- If 1 to 4 mm more width on the west is acceptable, the converter can sit on the west wall above the header (as
  in mock I): the 5 V runs shrink to about 25 and 35 mm and the board to about 39.9 x 63.5 mm. Not built.

**Mock K: the layout Nick reviewed in CAD, with through-hole headers** (Nick, 2026-11-17, with a screenshot of
mock H behind the N6: "leverage this reference layout, with the thru- headers"; "the BM connectors go north and
south, the 5V reg fits on the west side where there is room to go wider to allow for sufficient copper width, then
motor + pot + QWicc connectors goes on the west side horizontally"). Built as a rough board (`... K`), both headers
through-hole, 2.1 mm holes in the corners, 3 mm corner radius:
- **45.56 x 63.3 mm (2884 mm²).** East edge flush with the N6, as in mock H. West edge 10.0 mm past the N6 (mock
  H: 3.0), south edge 7.3 mm past the USB end (H: 4.6), north edge 11.55 mm past the camera end (H: 11.25).
- South strip: BM1 centred on L1. North strip: BM2 centred on L2. The south strip grew by 2.7 mm because a
  connector land pattern is 6.69 mm deep.
- West side, beside the west header (through-hole pads allow nothing over the header): MOTOR, POT, QWIIC lying
  east-west, bodies 3.0 mm apart; the motor driver under MOTOR and the ADC under POT, on the N6-facing side but
  outside the N6's outline, so the gap between the boards does not limit them.
- West side, above the header: the 5 V converter alone, in a strip about 16 mm wide and 25 mm long: about 400 mm²
  of copper per outer face is available, twice the first estimate.
- Why 10 mm on the west: a connector lying east-west is 9.55 mm across and must clear the header pads.

Routing considered for mock K (from the placement coordinates; nothing routed or rule-checked):

| Net | Run in mock K | Verdict |
|---|---|---|
| BM1, BM2 bus tracks | about 2 mm each | as short as it gets |
| Motor PWM and sleep (P7, P8, P14) | about 3 to 6 mm west from the header to the driver under MOTOR | much better than mock J |
| Motor outputs | about 2 mm | fine |
| 5 V, converter to VIN | about 22 mm down the west side | fine |
| 5 V, converter to the motor driver | about 20 mm, on the wide west strip | fine |
| VBUS to the converter | a few mm: Sofar's VBUS plane lies beside it | fine |
| ADIN SPI | about 16 mm to P0..P3, unchanged | fine |
| I2C to the ADC and QWIIC (P4, P5 are on the east header) | about 45 mm round the south end | long but slow |

**Mock L: mock K, shorter** (Nick, 2026-11-17: "minimize the height if you can by shifting the north BM connector
to the west wall"). Built as a rough board (`... L`):
- **45.56 x 56.2 mm (2560 mm²)**: 7.1 mm shorter than K, same width. The north edge is now 4.45 mm past the N6's
  camera end, just past the mote block (which ends 4.04 mm past it).
- BM2 sits in the free pocket west of L2, lying east-west, 2 mm from L2's pads and 3 mm north of the 5 V converter.
  Its bus tracks stay about 2 mm long. The two northern holes sit in the pockets either side of L2.
- Everything else is as in K. The height is now the mote block (47.5 mm) plus the south strip for BM1 (7.3 mm)
  plus margins. A further 2.7 mm would come off only by moving BM1 off the south end as well; the column beside
  the west header is full (MOTOR, POT, QWIIC), so that needs more width or one connector fewer. Not built.

**SPI configuration straps on mock L** (Nick, 2026-11-17: "bring back the straps for SPI CFG config ... on the bottom
somewhere with large area for silkscreen and then room to make the solder connections"). The straps were never
removed from the schematic; the rough boards had left them out with the other small parts. On mock L the two
three-pad solder jumpers JP3 (SPI_CFG1) and JP4 (SPI_CFG0) now sit on the N6-facing side in the west wing, at
X' -8.4 to -3.7 mm, y 17.6 to 24.6 mm: outside the N6's outline, so they can be reworked with the N6 soldered on,
with about 9 x 10 mm of free board around them for silkscreen. Default 0 / 0 = OPEN Alliance SPI with protection
(ADIN2111 Table 22, `docs/SPEC.md`). Their resistors (R2 and R47 at U1 pin 19, R9 on MISO) stay at the chip, as on
the Pi boards (DESIGN D38); only the DC side of each strap runs to the jumpers. Not placed in the mock.

**Mock M: mock L with a narrower west side** (Nick, 2026-11-17: "is it possible to reduce the width by 2-4 mm by
rotating the connectors 90 deg and moving one or two to the north and south ends?"). Built as a rough board (`... M`):
- **42.36 x 56.2 mm (2381 mm²)**: 3.2 mm narrower than L, same height. West edge 6.8 mm past the N6 (L: 10.0).
- What set L's west width: a connector lying east-west beside the through-hole west header. Its land pattern is
  9.55 mm across and must clear the header pads; the 5 V converter needs less (its group is 10.25 mm wide but may
  reach 6.2 mm inside the N6's outline above the header rows, so it needs the board only 4.3 mm past the N6).
- Changes: MOTOR and QWIIC move into the south strip beside BM1; POT is turned so its pin row runs along the west
  wall (6.69 mm across). Motor driver under MOTOR, ADC under POT: the two are 2 mm apart, beside P7 / P8 and VIN.
  QWIIC is at the east end of the south strip, about 12 mm from its I2C pins P4 / P5. Straps under the west wing.
- The converter's strip is now 13 mm wide (L: 16 mm): about 320 mm² of copper per face against the 200 mm² target.
- Going narrower still: with POT in the south strip too (in place of QWIIC, which would go beside L2 in the
  north-east), the west edge could come in to 4.3 mm past the N6 (39.9 mm wide), set by the converter. That leaves
  the converter a 10.5 mm strip. Not built.

**Which header carries what** (seen from behind, `PIN_MAP.md`):

| West header (VIN side) | East header (P0 side) |
|---|---|
| VIN: 5 V from the converter | P0, P1, P2, P3: ADIN SPI (MOSI, MISO, SCK, CS) |
| P7, P8: motor PWM (IN1, IN2) | P4, P5: I2C (power monitor, ADC, QWIIC) |
| P14: motor sleep | P6: ADIN reset, or spare |
| P9: ADIN interrupt | 3V3, GND |
| P13: ADIN power enable | not connected: RAW, PWR WKUP, Ethernet LED and pairs A / B |
| 3V3, GND | |
| not connected: RESET, P11, P10, BOOT0, Ethernet pairs C / D | |

So 5 V and every motor signal are on the west header: the converter, the motor driver and MOTOR belong on the west
or south-west, as Nick suspected. The ADC's two analog inputs (motor current from the driver, pot wiper with its
100 k pull-down) are the sensitive lines, so the ADC and POT stay beside the driver and the ADC's slow I2C is what
crosses to the east header. QWIIC is I2C only, so it is the one connector that prefers the east side.

**Independent review of mock L, 2026-11-17, and corrections to this file.** A separate review agent measured the
mock L scratch board (pcbnew, copper raster, a grid-router trial as existence proof, DRC on a copy). Full report
outside git: `~/NereusData/nereus_Pi_shield_ADIN2111/n6_shield/review_L/REVIEW_L.md`. Verdict: ROUTABLE WITH CHANGES.

Corrections to statements above (mine, wrong; the review measured them, and I re-checked the first two):
- **Every STEP file made before this commit contained the Pi Zero board's four 2.75 mm mounting holes** at their old
  positions, and left 17 of Sofar's copper shapes behind instead of turning them with the block.
  `n6_rough_board.py` kept footprints by name (the new holes reuse H1..H4) and did not move copper graphics. Fixed;
  all nine STEP files are regenerated and checked (4 holes, or none on D; no copper shape outside the outline).
- **"Bus tracks about 2 mm" is wrong for mocks J to M.** L1's and L2's bus pads are on the inductors' east side
  (mock L: BM1_P at X' 21.0, y 3.6; BM1_N at 21.0, 12.1; BM2_P at 21.4, 37.4; BM2_N at 21.4, 45.9), and a connector's
  pin row is on the far side of its land pattern. The review's trial routes at 2.0 mm: BM1_P 6.2, BM1_N 15.2,
  BM2_P 15.0, BM2_N 16.7 mm, the N lines on Internal 1 with vias.
- **"About 400 mm² of copper per face" at the converter in mocks K / L is wrong:** 245 mm² (top) and 278 mm²
  (N6-facing side) are free in mock L. Still above the 200 mm² estimate.
- **"Sofar's VBUS plane lies beside the converter" is wrong:** that plane is P_IN (before the shunt R8). The nearest
  VBUS copper is 6.4 mm away, and the converter must take VBUS, or the power monitor will not see its current.

Changes the review calls for (each to be decided by Nick; none is built):

| # | Rank | Change |
|---|---|---|
| B2 | Blocker | Motor driver not directly under the MOTOR connector's pads and not 1.5 mm from the header pads: no room for vias or for its four control nets. Move it beside the connector, clear of both |
| B3 | Blocker | Board gap: a plain header gives about 2.5 mm, but the N6's LiPo leads (2.09 mm) and microSD socket (1.46 mm) face mote parts of about 1.3 mm. Choose a header that gives 4 mm or more, or prove each overlap in CAD |
| M1 | Major | Turn BM1's connector half a turn so its pins face L1; accept the N lines on Internal 1 at 2.0 mm with four or more vias per end |
| M2 | Major | End Sofar's south ground-plane slot at the block's edge instead of carrying it to the board edge, so the SPI return path to the N6's ground pins is not cut (ask Sofar what the slot is for) |
| M3 | Major | Put the ADIN interrupt on P6 (east, 6.6 mm in the trial) instead of P9 (west, 19.9 mm past the crystal); reset on P9 or dropped. ADIN_PWR to P13 is 19.2 mm through T1's footprint: revisit |
| M4 | Major | SPI power states: 10 k pull-up on CS to ADIN_VDDIO (the ADIN's CS, SCLK and SDI have internal pull-downs, so CS reads selected while the N6's pins float), 22 to 47 ohm series resistors on the SPI lines at the driving ends, keep R43, and a firmware hold-off until VDDIO is up |
| M5 | Major | Thermal: keep the wing's outer layers free of tracks, eight or more ground vias at U10; at full pass-through current the whole board dissipates about 2.2 W (reviewer's arithmetic, free air) |
| M6 | Major if used | The west wing covers the N6's microSD slot |
| m | Minor | North edge 0.3 to 0.5 mm further out; holes 3.0 mm from the edges (2.3 mm leaves 0.96 mm of board at the rounded corners); strap legend at 1.0 mm text inside the outline; three fiducials per face; R37, R38, C53 to the top face; one centred track per gap between the live Ethernet pins; remove unused inner pads on the headers; feed U13 / pot from the N6's 3V3 pin |

Checked and fine in the review: the channels beside the block are 2.0 mm (west) and 2.1 mm (east) on every layer;
SPI runs 15 to 18 mm with under 4 mm spread and nothing of ours within 10 mm of its ends; no courtyard overlaps;
OpenMV's pinout image agrees with the model on the left / right sense of the header.

**Mock N: the review's placement changes built in** (Nick, 2026-11-17: "Yes, build it"). Rough board (`... N`),
both headers through-hole, 2.1 mm holes now 3.0 mm in from the edges, 3 mm corners. DRC on the scratch copy under
the project's rules: only the 3 inherited skew errors; 122 unconnected (nothing of ours is routed).
- **46.36 x 56.6 mm (2624 mm²).** West edge 10.8 mm past the N6, east edge flush, south edge 7.3 mm past the USB
  end, north edge 4.85 mm past the camera end (0.4 mm more than L, for the edge clearance of Sofar's via).
- **It is back to mock L's width, not mock M's.** The review's rule "no part of ours on the opposite face of a
  connector's pads" means the motor driver and the ADC each need their own stretch of the west wing instead of
  hiding under a connector; with M's 6.8 mm wing that stretch does not exist (the wing would have to hold 59 mm of
  parts in 46 mm). A narrower board is possible only by putting parts on both faces at the same spot again.
- West wing beside the header, from the USB end: MOTOR (top), motor driver (N6-facing side, 1.36 mm from the
  header pads, beside the connector and not under it), POT (top). Above the header: the ADC (N6-facing side) in a
  west column beside the 5 V converter, the strap jumpers JP3 / JP4 under the wing with a 1.0 mm legend, then BM2.
- South strip: BM1 turned half a turn (pins 5.3 mm from L1's BM1_P pad), and QWIIC east of it.
- BM2 is unchanged, west of L2: its bus pads are on L2's east side, so its tracks stay about 15 mm with the N line
  on an inner layer. Shorter tracks need BM2 north of L2 again (mock K: about 7 mm taller). Nick's choice.
- Not placement, so not in the mock: the pin-map and schematic changes (`PIN_MAP.md`, last section), the plane
  slot (M2), the via arrays and keep-clear copper for the converter (M5), fiducials, moving R37 / R38 / C53 to the
  top face, and the two decisions that are Nick's: the header that sets the board gap (B3) and whether the microSD
  slot must stay reachable (M6).

**Smallest outline that holds everything: mock D, 35.56 x 60.5 mm.** Mock A is 2 mm longer; mock C is wider and 12 mm shorter. The converter and the motor
driver sit next to the pins they use (VIN, P7, P8) in mocks A and B. Images: `mock_A_long_side_entry.png`,
`mock_A_long_top_entry.png`, `mock_B_wing_side_entry.png`, `mock_B_wing_top_entry.png`,
`mock_C_east_wing_side_entry.png`, `mock_C_east_wing_top_entry.png`, `mock_D_tall_side_entry.png`,
`mock_D_tall_top_entry.png`, `mock_E_smd_headers_top_entry.png`, `mock_F_one_column_top_entry.png`.

**Connectors, both ways** (JST catalogue sheets eGH.pdf and eSH.pdf, jst-mfg.com, read 2026-11-17):

| | Side entry (SM..B) | Top entry (BM..B) |
|---|---|---|
| GH 4-pin on the board | 8.25 x 4.85 mm | 8.25 x 4.95 mm |
| Mated | 4.35 mm high; the plug reaches about 3.1 mm past the body, along the board | 7.3 mm high, against 6.0 mm for L1 / L2 (Pi Zero `BRIEF.md`) |
| In the mocks | must sit on an edge; the cable leaves sideways and adds to the footprint of the assembly | can sit anywhere on the outer face; the cable leaves backwards and the stack is 1.3 mm taller than the inductors |

Both styles fit both mocks. The Pi Zero lesson applies: choose before routing, because top-entry parts need the
board under their bodies for pads.

**What does not fit or is not settled**
- The N6's size itself, see above.
- Height between the boards: the N6's pins stand 9.19 mm out of its back and its tallest back-side part is 2.09 mm
  (S5). The shield's socket part and so the gap are not chosen; the mote's bottom-side parts (about 1.3 mm) face the
  N6. To check once a socket is picked.
- Mounting: the N6 has no free mounting holes (S5), so the shield hangs on the two headers unless the enclosure
  holds it. Mock A's 14 mm overhang is a lever on those headers.
- Mock A covers the N6's microSD slot edge and LiPo connector area from behind; access with the shield fitted was
  not checked.
- Test points, fiducials, the strap jumpers and the LEDs are not placed in the mocks.
- All N6 geometry is from OpenMV's "r3" 3D model, not a drawing, and the left / right sense of the header from the
  back is assumed (`N6_FACTS.md`).

## 4. Questions for Nick, each with a recommendation

1. **Outline.** Which mock: A, B, C, D (tall, 35.56 x 60.5), E or F (SMD headers, mounting holes, top wiring)?
   *Recommendation: F if you want to mount the camera by the shield and plug all harnesses from behind; D if the
   smallest board matters most.* Is an overhang past the USB end acceptable, and what are the enclosure's
   inner dimensions?
2. **Connector entry.** Side or top? *Recommendation: top entry on the outer face if the enclosure has 7.3 mm plus
   wire bend behind the shield; otherwise side entry, which costs about 3 mm around the edges.*
3. **5 V to the N6 and the AUX pads.** *Recommendation: U10's output directly to VIN, no jumper, no fuse; drop J4.*
   The N6's ideal diode lets USB be plugged in at the same time (S1, S2), which the Pi could not. Keep J4 only if
   you want to power the N6 and motor from a bench supply without the bus.
4. **ADC.** Keep the ADS1115 for motor current and pot, or use the N6's single ADC pin for one of them and drop the
   other? *Recommendation: keep the ADS1115.*
5. **Leftovers of the VBUS-out circuit inside Sofar's block** (R35, C50, R11, TP19, TP35). *Recommendation: remove
   the parts and leave Sofar's copper untouched, so the block still matches his board track for track.*
6. **Pins.** Is the map in `PIN_MAP.md` acceptable, in particular: no UART left on the header, ADIN_TIMER and
   ADC_ALERT not connected, one shared I2C bus, P6 for the ADIN reset? *Recommendation: yes; drop the reset line
   instead if you want P6 free.*
7. **LEDs.** Port LEDs switched by the ADIN's own register over SPI, power LED behind the cut-able jumper, no pin
   spent? *Recommendation: yes.*
8. **Do you use the N6's Ethernet, microSD or LiPo connector with the shield fitted?** It decides what the shield
   may cover and whether P15 to P18 could ever be freed.
9. **An N6 on the bench.** Can you confirm two things on a real board: which column is P0 to P6 when looking at the
   back, and the distance between the header rows (27.32 mm inner to inner in the model)? Or send a STEP or drawing
   if you have one.
10. **Potting.** Is this board potted like the Pi boards? It decides how far the free-air copper estimate can be
    trusted and whether the PPTC ban matters (it no longer does if F1 goes).
