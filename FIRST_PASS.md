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
