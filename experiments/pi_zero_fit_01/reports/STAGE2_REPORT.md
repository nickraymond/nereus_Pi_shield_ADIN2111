# Stage 2 (schematic), experiment pi_zero_fit_01: report

Written 2026-11-15, 9:22 PM Pacific. Scratch copy only: `stage2_scratch/board/`. The repo and
`stage1_placement.kicad_pcb` were not written (`git status` clean; six of the seven sheet files are byte-identical to
the baseline, only `Nereus_Pi_Shield_Adin2111_TopLevel.kicad_sch` changed).

Rebuild from the baseline: `sh scripts/run_all.sh` (restores `board_baseline/`, runs steps 0-5, ERC, netlist, diffs, PDF).

## Gates

| Gate | Result | Evidence |
|---|---|---|
| 1 ERC loads and runs | **PASS**: 39 items, the same 39 as the baseline, none new, none vanished | `erc_stage2.json`, `ercdiff_stage2.txt` |
| 2 Net diff shows only A-F | **PASS**: 151 parts (143 - 7 + 15), 121 nets (110 + 11); 85 nets identical pin for pin | `netdiff_stage2.txt` |
| 3 New parts: footprint resolves, value / MPN filled | **PASS** for 13 of 15; R48 and C62 have a value and a footprint but **no MPN (parts to choose)** | `new_parts_stage2.md` |
| 4 PDF exported and looked at | **PASS**: Top-Level sheet rendered and checked area by area, no overlaps found | `schematic_stage2.pdf`, `render/crop_*.png` |

ERC note: in one earlier run of the same edits one Power-sheet warning read "3V3_Buck_Input and VBUS" instead of
"3V3_Buck_Input and 5V_Buck_Input" (same net, same warning, KiCad named a different pair of its three names). The
final run matches the baseline word for word; the wording can flip again on a rebuild.

Extra check: a throwaway copy re-saved by KiCad itself (`kicad-cli sch upgrade --force`) gives an identical netlist
and 39 ERC items (`render/roundtrip/`).

## What changed, per item

**A. Removed** (step 1): MP1-MP4, J2, J6, TP36, with their wires, labels, power symbols and the two section titles.
J1 pins that only served J2 now carry no-connect flags: 8 (UART_TX), 10 (UART_RX), 11 (~SPI1_CE1), 12 (~SPI1_CE0),
35 (SPI1_MISO), 38 (SPI1_MOSI), 40 (SPI1_SCLK). **J4, F1 and JP1 pad 3 (5V_LIFEPO4) are untouched** (scope change):
their nets are in the "identical" list.

**B. Bus connectors** (step 2): J10 "BM1" and J9 "BM2", SM04B-GHS, copied from the Urchin's J3. Pins 1+2 = N,
3+4 = P. Insert nets confirmed from the baseline netlist: MP1 BM1_P, MP2 BM1_N, MP3 BM2_P, MP4 BM2_N. Mounting pins:
the Urchin symbol has no mounting-pin pin and its two MP pads carry no net; done the same here.

**C. Motor driver** (step 3), Urchin -> here: U1 -> U12 MP6550; C7 -> C60 10 uF 10 V and C31 -> C61 100 nF (VIN);
C5 -> C63 100 nF (VCC); C6 -> C64 470 nF (V3P3); R3 2 kOhm -> **R48 4.99 kOhm 1 %** (ISET); new **C62 47 uF** bulk
on VIN. VIN = `5V_PI`. IN1 = MOTOR_IN1 (J1 pin 32), IN2 = MOTOR_IN2 (pin 33), nSLEEP_HB = MOTOR_nSLEEP (pin 29): the
same three Pi pins as on the Urchin (GPIO12, 13, 5). nSLEEP_LDO: no-connect flag (Urchin: test point only).
VISEN -> MOTOR_VISEN -> ADC AIN0.

**C. ADC** (step 4): U2 -> U13 ADS1115IDGS on shield `3V3`; C8 -> C65 100 nF; R4 -> R49 10 kOhm pull-up on
`~{ADC_ALERT}` (J1 pin 7) to shield 3V3; R5 -> R50 10 kOhm ADDR to GND (address 0x48). SCL / SDA on
`I2C0_SCL` / `I2C0_SDA` (J1 pins 28 / 27). AIN0 = MOTOR_VISEN (as Urchin), AIN1 = POT_WIPER, AIN2 / AIN3 no-connect.

**D. Connectors**: J7 "MOTOR" SM04B-GHS, pins 1+2 = OUT1, 3+4 = OUT2 (the Urchin's J3 pinout). J8 "POT" SM03B-GHS:
1 = 3V3, 2 = POT_WIPER, 3 = GND.

**E. Cancelled** (scope change): J5 keeps `WirePads_1x02_P3.81mm_Oval4.2x2.6mm_Drill1.3mm`. No SMD footprint was made.

**F. Kept**: everything else. No existing net renamed. Sofar's sheets untouched.

Also: step 5 updates the sheet's own notes (ADC now on the board, VISEN scale 499 mV/A, J2 line replaced).
Step 0 adds a symbol library `urchin.kicad_sym` and a footprint library `urchin.pretty` (nickname `urchin` in both
tables).

## Net diff (full list in `netdiff_stage2.txt`)

- Gone: UART_TX, UART_RX, ~SPI1_CE0, ~SPI1_CE1, SPI1_MISO, SPI1_MOSI, SPI1_SCLK (each was J1 pin + J2 pin; the J1 pin
  is now an `unconnected-(J1-...)` net).
- New: MOTOR_OUT1 (J7.1, J7.2, U12.2), MOTOR_OUT2 (J7.3, J7.4, U12.8), MOTOR_VISEN (U12.11, U13.4), POT_WIPER
  (J8.2, U13.5), Net-(U12-ISET) (R48.1, U12.7), Net-(U12-V3P3) (C64.1, U12.4), Net-(U12-VCC) (C63.1, U12.6),
  Net-(U13-ADDR) (R50.1, U13.1), and three no-connect nets: U12.5, U13.6, U13.7.
- Changed: 5V_PI (+C60.1 C61.1 C62.1 U12.9); BM1_N (-MP2.1 +J10.1 J10.2); BM1_P (-MP1.1 +J10.3 J10.4);
  BM2_N (-MP4.1 +J9.1 J9.2); BM2_P (-MP3.1 +J9.3 J9.4); I2C0_SCL (-J2.16 +U13.10); I2C0_SDA (-J2.15 +U13.9);
  I2C3_SCL (-J2.8); I2C3_SDA (-J2.7); MOTOR_IN1 (-J2.19 +U12.1); MOTOR_IN2 (-J2.20 +U12.10);
  MOTOR_nSLEEP (-J2.17 +U12.12); PI_5V (-J6.1 J6.3 J6.5); ~ADC_ALERT (-J2.2 +R49.2 U13.2);
  3V3 (+C65.1 J8.1 R49.1 U13.8); GND (-6 J2 pins, -3 J6 pins, +11 new pins); PI_3V3 (-J2.9 J2.11 J2.13);
  VBUS_OUT (-TP36.1).
- Sofar's mote nets: pin for pin identical except the four bus nets (inserts replaced) and the rails / GND that the
  new parts join.

## New parts

| Ref | Value | MPN | Footprint | Source |
|---|---|---|---|---|
| U12 | MP6550 | MP6550GG | urchin:MP6550GG (extracted from the Urchin board, U1) | Urchin U1 |
| U13 | ADS1115IDGS | ADS1115IDGS | Package_SO:TSSOP-10_3x3mm_P0.5mm | Urchin U2 |
| C60 | 10uF 10V | GRM155R61A106ME11D | Capacitor_SMD:C_0402_1005Metric_Pad0.74x0.62mm_HandSolder | Urchin C7 |
| C61, C63, C65 | 100nF 50V | CC0402KRX5R9BB104 | same 0402 | Urchin C31, C5, C8 |
| C64 | 470nF 50V | UMK105ABJ474KV-F | same 0402 | Urchin C6 |
| **C62** | 47uF TBD | **to choose** | Capacitor_SMD:C_1206_3216Metric (placeholder) | new, review G S3 |
| **R48** | 4.99kΩ 1% | **to choose** | Resistor_SMD:R_0402_1005Metric_Pad0.72x0.64mm_HandSolder | Urchin R3, value changed |
| R49, R50 | 10kΩ 5% | RC0402JR-0710KL | same 0402 | Urchin R4, R5 |
| J7, J9, J10 | SM04B-GHS | SM04B-GHS-TB | Connector_JST:JST_GH_SM04B-GHS-TB_1x04-1MP_P1.25mm_Horizontal | Urchin J3 |
| J8 | SM03B-GHS | SM03B-GHS-TB | Connector_JST:JST_GH_SM03B-GHS-TB_1x03-1MP_P1.25mm_Horizontal | symbol derived from Urchin J3 |

The Urchin schematic carries MPNs only inside its Description fields ("p/n ...") and no LCSC numbers; they are copied
into `PLANNED MPN`, `PLANNED LCSC` is empty on all 15. All stock footprints load from KiCad's libraries.
`urchin:MP6550GG`: 12 pads, no exposed pad; the Urchin instance sits on the back and was flipped to the front; the
script asserts the pads run counter-clockwise from the front (not mirrored).

## ISET calculation

Source: MPS MP6550 datasheet Rev. 1.0, 7/16/2019, https://docs.rs-online.com/67b6/A700000013717563.pdf
- p. 11, Current Limit: the limit is reached when the VISEN pin reaches 0.5 V; with 5 kOhm from ISET to ground VISEN
  is about 0.5 V/A, so the trip is at 1 A.
- p. 11, Current Sensing: 100 uA is sourced per 1 A of output current.
- p. 4: ISET current 95 / 100 / 105 uA/A; trip voltage (rising) 475 / 500 / 525 mV.

I_limit = 0.5 V / (100 uA/A x R).
- Urchin, 2 kOhm: **2.5 A** (above the part's 2 A rating; p. 1).
- 5 kOhm is not an E96 value; nearest 1 % value **4.99 kOhm: 1.002 A typical**, VISEN 0.499 V/A.
- With the datasheet's spreads and 1 % on the resistor: about **0.90 A to 1.12 A**.

**Flag:** Nick's bench figure is "under 1 A spikes". A limit that can be as low as 0.90 A may clip those spikes (the
driver chops the current; it is not a fault). 4.02 kOhm would give 1.24 A typical. Nick's call.

Other datasheet facts used: nSLEEP_LDO has an internal pull-down, low = LDO off (p. 3, p. 12); V3P3 0.47 uF, VCC
0.1 to 10 uF (p. 3); VIN 1.8 to 22 V (p. 3).
ADS1115: TI SBAS444E (Dec 2024), https://www.ti.com/lit/ds/symlink/ads1115.pdf : ADDR to GND = 1001000b (Table 7-2);
ALERT/RDY open drain, pull-up (Table 4-1); unused inputs may float (9.1.4); analog inputs at most VDD + 0.3 V and
SDA / SCL / ADDR / ALERT up to 5.5 V (abs. max.).

## Assumptions and disagreements

1. **ADC bus = I2C0 (J1 pins 27 / 28).** DESIGN's pin map names no bus for the ADC. The Top-Level sheet's own note
   says "I2C0 GPIO0/1 = shield: INA232 0x41, ADS1115 0x48", and I2C0 is the bus with U4 and the pull-ups R26 / R27.
   On the Urchin the ADC sits on the Pi's GPIO2 / GPIO3 bus, which is unconnected on this schematic. The Urchin's
   bus pull-ups R1 / R2 are not copied. INA232's 0x41 is the sheet note's figure; I did not check it.
2. **Pot on AIN1.** The Urchin has no pot (AIN1 is a test point there); AIN1 follows the sheet note ("AIN1 = shaft pot").
3. **J8 pin order** 1 = 3V3, 2 = wiper, 3 = GND: the design session's assumption; the Urchin has no 3-pin connector.
4. **R49 pull-up goes to shield 3V3** (the ADC's supply, as on the Urchin). With the shield on and the Pi off this
   feeds 0.33 mA into GPIO4 (3.3 V / 10 kOhm; arithmetic). I2C0's pull-ups stay on PI_3V3 as before.
5. **C62**: no 47 uF ceramic in this project's or the Urchin's BOM. The project's only 47 uF part is the aluminium
   electrolytic EEEFT1H470AP (C22 / C23, 50 V), not used here (SPEC constraint 8 for new parts). 1206 is a
   placeholder footprint. Alternative from the BOM: two GRM21BR61C226ME44L (22 uF 16 V 0805, C56 / C57's part).
6. **Urchin test points not copied**: TP1 (nSLEEP_LDO), TP5-TP7 (AIN1-3), TP8 (ALERT), TP16 / TP18 / TP21 (motor
   control). Say if any should come back.
7. **DESIGN.md pin map against the schematic's J1 wiring** (the schematic wins; nothing in DESIGN was edited):
   - pins 3 / 5: DESIGN I2C1_SDA / SCL with R27 / R26 to shield 3V3; schematic: no-connect flags.
   - pins 27 / 28: DESIGN "avoid (HAT EEPROM)"; schematic I2C0_SDA / SCL with U4, R27 / R26 (to PI_3V3), now U13.
   - pin 36: DESIGN PAYLOAD_EN; schematic ADIN_TIMER. PAYLOAD_EN is on pin 37.
   - pin 38: DESIGN ~PAYLOAD_FAULT; schematic SPI1_MOSI (now no-connect). ~PAYLOAD_FAULT is on pin 31.
   - pins 13 / 15: DESIGN unused; schematic I2C3_SCL / SDA (Qwiic).
   - pin 7: DESIGN unused; schematic ~ADC_ALERT.
   - pins 29 / 32 / 33: DESIGN "reserved (motor)" and also in its no-connect list; schematic MOTOR_nSLEEP / IN1 / IN2.
   - pins 1 / 17: DESIGN "unconnected in the live project"; schematic PI_3V3.
   - DESIGN counts 17 no-connect GPIO pins; the schematic now has 10 (3, 5, 8, 10, 11, 12, 26, 35, 38, 40).
8. Stale notes left as found (not in A-F): the J5 note still says "JST GH"; the JP1 note says "JST-PH" for J4.
9. Tooling: the project files are KiCad 10 format; the Urchin copy in `urchin_ref/` was upgraded with
   `kicad-cli sch upgrade` before copying parts (its netlist is identical before and after). The repo's
   `tools/fpextract.py` fails on KiCad 10's pcbnew (`Duplicate()` needs an argument), so `step0_footprint.py` does
   the extraction.

## Not done

- Board parity: `stage1_placement.kicad_pcb` was not updated to this schematic (not edited, as instructed).
- R48 and C62 part choice; LCSC numbers for all 15 new parts.
- The BRIEF's "five Sofar items at J1 pins 13 and 35": not a schematic item in A-F; I2C3_SCL stays on pin 13.
- DESIGN.md, TRACKER and the sofar_brief are not updated (repo read-only).
- No QE review.
