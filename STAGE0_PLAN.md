# N6 shield: stage 0 plan (schematic first), for Nick's go

2026-11-17. **Plan only: nothing in `N6_Shield_ADIN2111/` has changed.** This is the "Plan" nibble of the project's
rules (`docs/TRACKER.md` on `development`): exact edits, then Nick's go, then edit and check. Basis: mock P
(`FIRST_PASS.md`), the pin map (`PIN_MAP.md`), the routing plan (`mocks/review/ROUTING_PLAN_P.md`, section 4).
Part references and nets are those of the starting design, read from the board file in this session
(`scripts/n6_read_board.py`, `scripts/n6_groups.py`).

## Where the work would happen

- Project `N6_Shield_ADIN2111/` on branch `n6-shield`, file names unchanged. KiCad closed while I edit.
- Scripted edits only, one script per step, each followed by: kicad-cli loads the schematic, ERC, netlist export,
  and a net diff against the starting design that shows only the intended changes (SPEC constraint 3: every kept
  net still matches the mote).
- Then a draft pull request and a QE review in its own session before you look at it in KiCad.

## Step 0a: remove what goes

| Edit | Parts | Nets that disappear |
|---|---|---|
| VBUS-out switch (sheet "Load Switch") | U11, C59, R34, R36, R41, R42, D3, C49, J5 | PAYLOAD_EN, ~PAYLOAD_FAULT, VBUS_OUT, U11_RTN, ISET |
| Its parts inside Sofar's block | R35, C50, R11, TP19, TP35: **decision 1** | |
| 5 V jumper, fuse, AUX pads | JP1, F1, J4: **decision 2** for J4 | 5V_LIFEPO4; PI_5V and 5V_PI become one net |
| Pi header and pad rows | J1, J15 to J19 | GPIO7, 12, 14, 15, 17, 19, 20, 21 |
| Second I2C bus | R10, R24 (they are the 10 k pull-ups of I2C3_SDA / I2C3_SCL to PI_3V3) | I2C3_SDA, I2C3_SCL |

## Step 0b: add and re-map

| Edit | Detail |
|---|---|
| N6 headers | J21 (west) and J22 (east), 2 x 8, 2.54 mm, through-hole. Fifteen positions get no net: the nine Ethernet positions, RAW, BOOT0, PWR WKUP, P10, P11, RESET |
| Pin map | P0 ADIN_MOSI, P1 ADIN_MISO, P2 ADIN_SCK, P3 ~ADIN_CS, P4 I2C SCL, P5 I2C SDA, P6 ~ADIN_INT, P7 MOTOR_IN1, P8 MOTOR_IN2, P9 ~ADIN_RST, P13 ADIN_PWR, P14 MOTOR_nSLEEP, VIN = 5 V from U10, both 3V3 pins = N6_3V3 (was PI_3V3), both GND |
| CS pull-up | new 10 k 0402 (reuse RC0402JR-0710KL, the part of R7 / R49), ~ADIN_CS to ADIN_VDDIO |
| SPI series resistors | four new 33 ohm 0402 on SCK, MOSI, CS (header side of Sofar's stub) and MISO (after R9's tap). **Part number to choose: decision 3** (no 33 ohm 0402 is on the board today) |
| I2C | one bus: I2C0_SCL / I2C0_SDA to P4 / P5; R26, R27 (4.7 k) to N6_3V3; QWIIC J3 pins GND, N6_3V3, SDA, SCL |
| No longer on a pin | ~ADC_ALERT (R49 stays as its pull-up, with a test pad); ADIN_TIMER ends at R47 and a test pad |
| Connectors | J7, J9, J10 to BM04B-GHS-TBT (LCSC C161692), J8 to BM03B-GHS-TBT (C161691), J3 to BM04B-SRSS-TB (C160390): numbers from `TOP_ENTRY_VARIANT.md`, read on JLC 2026-11-17. Pin order kept: N on pins 1, 2, P on pins 3, 4 |
| Mounting holes | three 2.7 mm holes in place of the four Pi holes: **decision 4** (bare or grounded) |
| Kept as they are | Sofar's block; U10 and its parts (R38 stays 13.3 k: 5.11 V nominal, inside the N6's 4.7 to 5.7 V); U12 and its parts; U13, the pot circuit; U4; R1, R43, R9, R2, R47; JP2, JP3, JP4; D8 to D10 with R44 to R46 |

## Step 0c: board

Import the schematic into the board, place per mock P (script `n6_rough_board.py` holds the coordinates), turn
Sofar's block with his tracks, vias, copper shapes **and zones** as one group (the mock dropped the zones), draw the
outline and holes. Gate: DRC shows only the 3 inherited skew errors plus the 16 inherited no-via-area items that
come back with Sofar's rule areas; schematic parity 0; the lock check passes (81 footprints, 870 tracks, 185 vias,
17 shapes of Sofar's, per the routing plan). Routing stages A to H follow, each with its own gate.

## Decisions needed before step 0a

| # | Decision | My recommendation |
|---|---|---|
| 1 | The VBUS-out leftovers inside Sofar's block (R35, C50, R11, TP19, TP35) | remove the parts, leave Sofar's copper untouched |
| 2 | AUX 5 V pads J4 | remove: the N6's ideal diode lets USB and VIN coexist, and the mock has no place for them |
| 3 | 33 ohm 0402 part for the SPI lines | a JLC basic part; I will propose one with its page before using it |
| 4 | Mounting holes bare or tied to ground | bare (no plating), as on the Pi boards' M2.5 holes |
| 5 | U13 and pot supply | **N6 3V3 pin** (Nick, 2026-11-17: "I'd like to not interfere with the mote circuit if we can avoid it"). Today both are on the mote's own 3V3 (starting board: J8 pin 1 = 3V3, U13 pin 8 = 3V3, C65, R49; the Pi's rail is the separate net PI_3V3). Change: J8 pin 1, U13 VDD, C65 and R49 to N6_3V3; about 44 mm from the west header's 3V3 pin in mock P; add a 1 uF capacitor at U13. Not 5 V: the N6 has no 5 V output (VIN is an input fed by our own converter), and a 5 V pot would put up to 5 V on the inputs of an ADC running at 3.3 V |
| 6 | Header part for a 5 mm gap | yours: pin length must cover 5 mm + 1.6 mm + 1.3 mm + solder; about 2.6 mm of the N6's own pins would stand above the shield if its fitted header is used (reviewer's arithmetic) |
| 7 | Your go for step 0a to 0c, with KiCad closed | |

## Not verified, carried from the reviews

A real N6 (which column is P0 to P6 from the back, row spacing); Sofar's ground-slot purpose; ADIN2111 datasheet
Rev. B for the pull-downs and LED registers; ST's pin limits; potting and heat.
