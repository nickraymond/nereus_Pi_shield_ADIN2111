# Stage 2c (Nick's schematic changes of the evening + board parity), experiment pi_zero_fit_01: report

Written 2026-11-15, 9:58 PM Pacific. Scratch only: `stage3_scratch/`. Nothing was written in the git repo (`git status` clean).
Rebuild from the pristine stage-2b project: `sh scripts_2c/run_all.sh` (restores `board/` from `board_in_stage2b/`, runs
steps 1-6, ERC, net diff, lock check, DRC, renders). Log of the last run: `build_2c/run_all.log`. No routing was done.

## Gates (numbers read from the last run)

| Gate | Result | Evidence |
|---|---|---|
| ERC | **39 items** (input 39). Same items; one Power-sheet warning names "3V3_Buck_Input and 5V_Buck_Input" in one run and "3V3_Buck_Input and VBUS" in another (same net, same warning; the wording flip the stage-2 and 2b reports describe, it flipped between my own runs of the unchanged input too). No new item, none gone | `erc_stage2c.json`, `ercdiff_stage2c.txt` |
| Net diff | **154 parts (151 + C66, C67, R51), 121 nets, none added or removed.** 3 nets changed: 5V_PI +C66.1; POT_WIPER +R51.1, C67.1; GND +C66.2, C67.2, R51.2. 118 nets identical pin for pin; no kept pin changed net, name or type. 8 parts changed fields: R48, C62, C61, C63, C65, R49, R50 (changes 1-3) and J4 (Description, change 5) | `netdiff_stage2c.txt` (against the stage-2b input); `build_2c/netdiff_vs_stage2_scratch.txt` (against `stage2_scratch/netlist_stage2.net`: the same, plus J4's Footprint that stage 2b set) |
| Schematic parity | **0** | `drc_stage2c.json`, `build_2c/gates.txt` |
| DRC errors | **3 skew_out_of_range + 16 items_not_allowed, nothing else** | same |
| Unconnected | **137** (input 131; + 6 = the two pads each of C66, R51, C67; nothing is routed) | same |
| DRC warnings | 550 (input 515); all 35 extra are silkscreen / text: silk_overlap 54 -> 68, silk_over_copper 27 -> 32, text_height 126 -> 134, text_thickness 129 -> 137 (the mote-library footprints carry small reference texts). No courtyard, clearance, edge or hole item | same |
| Lock check | **PASS**: 81 mote footprints, 0 changed; 1156 tracks + vias (205 vias) identical; 171 zones identical (outlines, layers, nets, priority; refilled) | `build_2c/lock_check.txt` |
| Other parts | moved or re-footprinted: only C60-C65, R48-R50 (the two new groups); graphics changed: those and J4. U12, U13 not moved | same |
| Project rules | `.kicad_pro`, `.kicad_dru`, both lib tables byte-identical; changed files: the Top-Level sheet, the board, J4's `.kicad_mod` | end of `build_2c/run_all.log` |
| Renders | `top.png`, `bottom.png` (overwritten) and crops `build_2c/bottom_motor.png`, `bottom_adc.png`, `crop_motor.png`, `crop_adc.png` (schematic): looked at, parts where the table says, none on another | |

## What changed in the schematic (`scripts_2c/step1_schematic.py`; only the Top-Level sheet)

1. **R48 = 4.02 kΩ 1 %**, MPN **RC0402FR-074K02L** (Yageo RC0402FR-07, the series of R34 / R23 / R1 / R22 on this board),
   footprint `Vault:FP-RC0402-0_4-IPC_C` (R34's). **LCSC number not looked up**; this value is not in `bom.csv`.
   Limit by the formula stage 2 cited: 0.5 V / (100 µA/A x 4.02 kΩ) = 1.24 A; VISEN 0.402 V/A (arithmetic). Sheet notes updated.
2. **Pot**: **R51** 100 kΩ 1 % RMCF0402FT100K (Stackpole, LCSC C7055151, `Vault:FP-RMCF0402-IPC_C`, as R21 / R35 / R36)
   and **C67** 100 nF 25 V CL05A104KA5NNNC (Samsung, C100072, `Vault:FP-CL278-IPC_C`) **DNP**, both POT_WIPER to GND,
   drawn right of J8 with a note. Untested fix (Urchin bring-up bench finding); Nick tests it.
3. **C62 = 22 µF 16 V 0805** GRM21BR61C226ME44L (Murata, C86817, `Capacitor_SMD:C_0805_2012Metric`, as C56 / C57) and
   **C66**, the same, in parallel: 44 µF nominal. The 5V_PI label moved to the rail's new west end.
5. **J4** Description now says 2.2 x 3.3 mm oval, 1.1 mm hole, 3.2 mm pitch.

MPN / manufacturer / LCSC of the vetted parts are copied from `docs/design-review/bom.csv` (read this session).

### Stage-2 passives checked against this board's vetted parts

| Ref | Was | Now | |
|---|---|---|---|
| C61, C63, C65 | 100 nF 50 V CC0402KRX5R9BB104, hand-solder 0402 | **CL05A104KA5NNNC** 100 nF 25 V, `Vault:FP-CL278-IPC_C` (C1, C3, C9-C15, C28, C53) | switched (rating 50 V -> 25 V, on 5 V / 3.3 V nets) |
| R49, R50 | RC0402JR-0710KL, hand-solder 0402 | same part, `Vault:FP-RC0402-0_4-IPC_C` + LCSC C60489 (R7, R10, R24) | footprint switched |
| R48 | 4.99 kΩ, no MPN, hand-solder 0402 | see 1 | switched |
| C62 | 47 µF, no MPN, 1206 | see 3 | switched |
| **C60** | 10 µF 10 V GRM155R61A106ME11D, hand-solder 0402 (Urchin) | unchanged | **left**: this board's only 10 µF 0402 is GRJ155R60J106ME11D (C32), rated 6.3 V; on the 5 V motor rail I did not lower the rating. Nick's call |
| **C64** | 470 nF 50 V UMK105ABJ474KV-F, hand-solder 0402 (Urchin) | unchanged | **left**: no 470 nF 0402 on this board (C16 etc. are 0805 100 V; C5 / C6 are 680 nF) |
| U12, U13, J7-J10 | | unchanged | left: no equivalent on this board |

## I2C addresses (change 4: no schematic change; both read by me from the PDFs)

- **U4 INA232AIDDFR: 0x41.** A0 (pin 7) is on shield `3V3`, the same net as VS (pin 4) (netlist). TI SBOSAA2 (Dec 2022),
  p. 15, Table 7-1: A0 = VS -> 1000001 for the "INA232A device option". https://www.ti.com/lit/ds/symlink/ina232.pdf
  That the "A" in INA232AIDDFR is that device option is my reading of the part number; the table does not spell out the
  orderable name. The B option with A0 = VS would be 1001001 = 0x49: still not 0x48.
- **U13 ADS1115: 0x48.** ADDR (pin 1) goes to GND through R50 (10 kΩ). TI SBAS444E (Dec 2024), p. 20, Table 7-2:
  ADDR = GND -> 1001000b. https://www.ti.com/lit/ds/symlink/ads1115.pdf
- **They differ (0x41 / 0x48).** U13 stays on I2C0_SDA / SCL (J1 pins 27 / 28) with U4 and R26 / R27; J1 pins 3 / 5 unconnected.
- Not verified: that 10 kΩ in the ADDR line is a valid "GND" (the Urchin does the same; the datasheet's input leakage and
  VIL figures were read only through a fetch helper, not by me: ±10 µA, VIL max 0.3 VDD, which would give 0.1 V against 0.99 V).

## Board (`step2_remove.py` ... `step6_fill.py`): all bottom side; centre in new-frame mm

| Ref | Value | Footprint | Centre x, y | Turn | Courtyard x / y |
|---|---|---|---|---|---|
| U12 | MP6550 | urchin:MP6550GG | 6.30, 37.20 (not moved) | 90 | 4.55..8.06 / 35.45..38.96 |
| C61 | 100nF 25V | FP-CL278-IPC_C | 6.23, 34.56 | 90 | 5.81..6.65 / 33.78..35.34 |
| C66 (new) | 22uF 16V | C_0805_2012Metric | 7.78, 33.25 | 90 | 6.76..8.81 / 31.51..35.00 |
| C62 | 22uF 16V | C_0805_2012Metric | 4.68, 33.25 | 90 | 3.66..5.71 / 31.51..35.00 |
| C60 | 10uF 10V | C_0402 HandSolder | 3.045, 34.165 | 90 | 2.54..3.55 / 33.03..35.30 |
| R48 | 4.02k 1% | FP-RC0402-0_4-IPC_C | 3.66, 36.10 | 180 | 2.88..4.44 / 35.56..36.65 |
| C63 | 100nF 25V | FP-CL278-IPC_C | 3.66, 37.17 | 180 | 2.88..4.44 / 36.75..37.59 |
| C64 | 470nF 50V | C_0402 HandSolder | 3.305, 38.20 | 180 | 2.17..4.44 / 37.70..38.71 |
| U13 | ADS1115IDGS | TSSOP-10 | 24.90, 35.00 (not moved) | 0 | 21.73..28.08 / 33.21..36.80 |
| R51 (new) | 100k 1% | FP-RMCF0402-IPC_C | 21.98, 32.68 | 180 | 21.18..22.78 / 32.26..33.10 |
| C67 (new, DNP) | 100nF 25V | FP-CL278-IPC_C | 23.67, 32.68 | 0 | 22.89..24.45 / 32.26..33.10 |
| C65 | 100nF 25V | FP-CL278-IPC_C | 28.60, 34.62 | 90 | 28.18..29.02 / 33.84..35.40 |
| R49 | 10k 5% | FP-RC0402-0_4-IPC_C | 21.04, 35.88 | 90 | 20.49..21.58 / 35.10..36.66 |
| R50 | 10k 5% | FP-RC0402-0_4-IPC_C | 23.00, 37.445 | 0 | 22.22..23.78 / 36.90..37.99 |

**Motor group** (x 2.17..8.81, y 31.51..38.96): a row north of U12, west to east C60, C62, C61, C66, all with the VIN pad
south. Edge to edge from U12's VIN pad: **C61 0.65 mm, C66 1.21 mm, C62 1.55 mm**, C60 3.18 mm (stage 2b: C62 about 2.3 mm).
R48, C63, C64 stay in a column west of U12 at pins 7, 6, 4.
**ADC group** (x 20.49..29.02, y 32.26..37.99): R51 and C67 in a row north of U13, wiper pads side by side straight above
the AIN1 pad, 0.93 mm from it, ground pads outwards.

Margins printed by step 3 (`build_2c/step3_placement.txt`; pad bounding boxes):
- courtyard to courtyard: smallest **0.103 mm** (several at 0.10 to 0.11; all group parts >= 0.10). DRC: no courtyard item;
- courtyard to the board outline, 3 mm corners included: smallest **0.545 mm** (U12, south; unchanged); pads: 0.89 mm (C64);
- group pad to another net's pad / via / bottom track: smallest 0.48 mm (C63 to C64); to a drilled hole 2.29 mm. No via and
  no bottom-layer track lies under either group.

**J4** (`step4_j4_silk.py`): the library footprint got a silkscreen outline (0.12 mm line, between fab outline and
courtyard), "+" and "GND" (1 mm text, 0.15 mm, as in the library's other WirePads footprint); the same three items were
added to the board's J4. Pads, position, courtyard: asserted unchanged.

## Flags

1. **DC bias of the 22 µF parts: Murata's figure not found.** Murata's product pages for GRM21BR61C226ME44 returned empty
   pages or 404 to the fetch helper; SimSurfing was not reached. So "44 µF nominal" is all I can state; I do not know the
   capacitance at 5 V. To find out: Murata SimSurfing, part GRM21BR61C226ME44, DC bias 5 V. The same question applies to
   C60 (10 µF 0402 at 5 V).
2. **The motor group grew north to y 31.5** (brief: "around y 33..39"); the two 0805 stand upright so their VIN pads face
   U12. FID1's pad (centre 2.2, 31.1) is about 1.4 mm from C62's ground pad. Say if the strip y 31.5..33 is needed for routing.
3. **Escapes at U12's north side** (routing stage): C61's VIN pad sits above the OUT2 pin; OUT2 leaves west through the
   0.67 mm gap between the pad row and the pins (one 0.2 mm track at 0.2 mm clearance fits; motor current on it), ISET
   west from the side of its pin, IN2 east. Not routed, not proven.
4. **"+" on J4 is not beside pad 1**: no room there (board edge west, L6 north, 1 mm between the pads). It sits under the
   outline's south-west corner, just north of mounting hole H4 (a screw head may cover part of it); "GND" is east of pad 2.
   Nick to judge on `top.png`.
5. **Silkscreen of the two groups is still not done** (the 35 extra warnings): reference texts overlap; the mote-library
   footprints bring 0.x mm reference texts like the other mote parts.
6. R48's LCSC number, and LCSC numbers for C60, C64, U12, U13, J7-J10: not looked up.
7. Library symbol names are now stale labels only: C62 / C66 use `urchin:CAP_47uF_bulk`, R51 uses `urchin:Res_10k_0402_5p`
   (value, footprint and fields are right; the names show only in the symbol's properties).
8. C61 / C63 / C65 keep the value text "100nF 25V" (stage 2's style), not the MPN as the mote parts do; a BOM grouped by
   value will list them apart from C1 etc. although the MPN field is the same.
9. The JP1 note on the sheet still says "JST-PH" for J4 (stage 2 flagged it; not in this stage's list).
10. Carried over from stage 2b, unchanged: I2C order at U13 against R26 / R27; R15 / R16 pin names; heights under the board;
    131 -> 137 unconnected is expected, nothing is routed.
11. No QE review.

## Files

`board/` (result project), `board_in_stage2b/` (pristine input), `scripts_2c/` (`run_all.sh`, `step1_schematic.py`,
`step2_remove.py`, `step3_place.py`, `step4_j4_silk.py`, `step5_parity.py`, `step6_fill.py`, `verify_locks.py`,
`netdiff.py`, `ercdiff.py`, `drc_summary.py`, `render_sch.sh`, `dump_area.py`, `dump_j4.py`, `s2lib.py`, `s3lib.py`,
`netparse.py`, `repo_tools/` = the repo's `tools/schedit.py` etc., unchanged), `netlist_stage2c.net`, `erc_stage2c.json`,
`drc_stage2c.json`, `netdiff_stage2c.txt`, `ercdiff_stage2c.txt`, `schematic_stage2c.pdf`, `top.png`, `bottom.png`, `build_2c/`.
