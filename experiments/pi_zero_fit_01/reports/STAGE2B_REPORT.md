# Stage 2b (board parity), experiment pi_zero_fit_01: report

Written 2026-11-15, 9:35 PM Pacific. Scratch only: `stage3_scratch/`. Nothing was written in the git repo.
Rebuild from the pristine inputs: `sh scripts/run_all.sh` (restores `board_in_stage1.kicad_pcb`, `sch_in/`, `proj_in/`,
`lib_in/`; runs steps 1-6, ERC, lock check, DRC, renders). Log of the last run: `build/run_all.log`.
Result board: `board/Nereus_Pi_Shield_Adin2111.kicad_pcb`. No routing was done.

## Gates (numbers read from the last run)

| Gate | Result | Evidence |
|---|---|---|
| Schematic parity | **0 issues** (input board: 46) | `drc_stage2b.json`, `build/gates.txt` |
| DRC errors | **3 skew_out_of_range + 16 items_not_allowed, nothing else** (same as the input board) | same |
| Unconnected | **131** (input board: 90, measured by me on the input; nothing is routed) | same |
| DRC warnings | 515 (input 472). All 43 extra are silkscreen: silk_overlap 24 -> 54, silk_over_copper 16 -> 27, silk_edge_clearance 5 -> 7, text_height 125 -> 126; lib_footprint_issues 1 -> 0 (J4's footprint now exists in the library). No courtyard, clearance, edge or hole warning or error | same |
| Lock check | **PASS**: 81 mote footprints, 0 changed; 1156 tracks + vias (205 vias) identical; 171 zones, outlines / layers / nets / priority identical (fills were refilled, step 6) | `build/lock_check.txt` |
| Stage-1 parts | none of the other 59 moved, turned or flipped | same |
| ERC after the J4 field edit | **39 items** (input 39) | `erc_stage2b.json` |
| Project rules | `.kicad_pro`, `.kicad_dru`, both lib tables byte-identical to the input | end of `build/run_all.log` |
| Renders | `top.png`, `bottom.png`, looked at: both groups sit under their connectors, no part on another | |

ERC note: in one of my two full runs one Power-sheet warning named "3V3_Buck_Input and VBUS" instead of
"3V3_Buck_Input and 5V_Buck_Input" (the wording flip the stage-2 report describes); in the last run all 39 items match
the input word for word.

Footprints: 140 -> **151** (netlist: 151 parts). Schematic files: only the Top-Level sheet differs, by one line (J4's Footprint).

## Step 1: diff of the input board against the netlist (before any change; full text in `build/step1_diff_before.txt`)

- **To delete: 0.** Every footprint on the stage-1 board is in the schematic.
- **To add: 11**: U12, C60, C61, C62, C63, C64, R48 (motor driver); U13, C65, R49, R50 (ADC).
- **To link (no symbol link, bare library footprints): J7, J8, J9, J10.** Each: value (stage 1 wrote the function name,
  the schematic's value is SM04B-GHS / SM03B-GHS), library nickname `Connector_JST:` on the footprint ID, symbol path,
  sheet name `/Top-Level Schematic/`, sheet file, fields FUNCTION / PLANNED MPN / PLANNED MFR / PLANNED LCSC /
  PLANNED NOTE / Description, pad nets and pin names. Mounting pads (MP): no pin in the symbol, so no net.
- **Pad nets to change on existing parts: J1 only**, 7 pads: 8, 10, 11, 12, 35, 38, 40 lose UART_TX, UART_RX,
  ~SPI1_CE1, ~SPI1_CE0, SPI1_MISO, SPI1_MOSI, SPI1_SCLK and get KiCad's `unconnected-(J1-...)` nets, pin type
  `+no_connect`. No renamed net.
- **J4**: footprint ID on the board (3.20 mm oval pads) against the schematic's (3.81 mm) -> step 4.
- Pin name / type missing on the pads of J4, J5 (set) and of **R15, R16 (locked mote parts: left as they are**, it is
  metadata only and the parity check does not flag it).
- Nets: 7 gone from the schematic (the seven above), 18 new (4 MOTOR / POT nets, 4 local U12 / U13 nets, 10 no-connect nets).
- Totals: 22 pad nets, 24 fields, 4 values, 5 footprint IDs, 4 symbol links, 30 pin names on 9 footprints.

## What was done

| Step | Script | Result |
|---|---|---|
| 2 | `step2_link_connectors.py` | J7-J10 linked; nets: J7 1+2 MOTOR_OUT1, 3+4 MOTOR_OUT2; J8 1 3V3, 2 POT_WIPER, 3 GND; J9 1+2 BM2_N, 3+4 BM2_P; J10 1+2 BM1_N, 3+4 BM1_P. Positions unchanged |
| 3 | `step3_add_parts.py` | 11 parts added, bottom side (table below) |
| 4 | `step4_j4_footprint.py` | `nereus.pretty/WirePads_1x02_P3.20mm_Oval2.2x3.3mm_Drill1.1mm.kicad_mod` written; J4's Footprint field set in the Top-Level sheet; J4 on the board got the library's fab outline and "+" / "GND" fab marks (pads, position, courtyard unchanged) |
| 5 | `step5_nets.py` | J1's 7 pads; pin names on J4, J5; no footprint to remove; the 7 dead nets removed |
| 6 | `step6_fill.py` | 171 zones refilled (154 are rule areas), saved |

### New parts (all bottom side; centre in new-frame mm; "turn" = KiCad orientation)

| Ref | Value | Footprint | Centre x, y | Turn | Courtyard x / y |
|---|---|---|---|---|---|
| U12 | MP6550 | urchin:MP6550GG | 6.30, 37.20 | 90 | 4.54..8.06 / 35.44..38.96 |
| C61 | 100nF 50V | C_0402 HandSolder | 6.55, 34.25 | 90 | 6.05..7.06 / 33.11..35.38 |
| C60 | 10uF 10V | C_0402 HandSolder | 7.60, 34.25 | 90 | 7.09..8.11 / 33.11..35.38 |
| C62 | 47uF TBD | C_1206_3216Metric | 3.45, 34.20 | 180 | 1.11..5.80 / 33.00..35.39 |
| R48 | 4.99k 1% | R_0402 HandSolder | 3.35, 35.95 | 180 | 2.20..4.50 / 35.44..36.47 |
| C63 | 100nF 50V | C_0402 HandSolder | 3.37, 37.00 | 180 | 2.23..4.50 / 36.49..37.50 |
| C64 | 470nF 50V | C_0402 HandSolder | 3.37, 38.05 | 180 | 2.23..4.50 / 37.55..38.55 |
| U13 | ADS1115IDGS | TSSOP-10_3x3mm_P0.5mm | 24.90, 35.00 | 0 | 21.72..28.07 / 33.20..36.80 |
| C65 | 100nF 50V | C_0402 HandSolder | 28.60, 34.18 | 90 | 28.09..29.10 / 33.05..35.31 |
| R49 | 10k 5% | R_0402 HandSolder | 21.15, 36.10 | 90 | 20.63..21.66 / 34.94..37.25 |
| R50 | 10k 5% | R_0402 HandSolder | 23.00, 37.40 | 0 | 21.84..24.16 / 36.88..37.91 |

**Motor group** (x 1.11..8.11, y 33.00..38.96, under J7): U12 in the south-east of the block. Its north side, west to
east: ISET (5.55), OUT2 (6.05), VIN (6.55), IN2 (7.05), pad ends at y 35.85. C61's VIN pad is straight north of the VIN
pin (0.67 mm between pad edges), C60 beside it, C62's VIN pad (4.35..5.50, 33.3..35.1) 1 mm west of that, about 2.3 mm
from the pin. R48, C63, C64 in a column west of U12, signal pads towards pins 7, 6, 4, ground pads to the west.
South side west to east: V3P3, GND, OUT1, IN1; east side: VISEN, nSLEEP; west side: VCC, nSLEEP_LDO (no connect).

**ADC group** (x 20.63..29.10, y 33.05..37.91, under J8): U13's east side north to south: AIN2, AIN3 (no connect), VDD,
SDA, SCL; west side: AIN1 (pot), AIN0 (VISEN), GND, ALERT, ADDR. C65's 3V3 pad sits about 0.5 mm east of the VDD pin; R49
west with its ALERT pad level with pin 2; R50 south-west under pin 1.

Margins printed by step 3 (pad bounding boxes, so slightly conservative; `build/step3_placement.txt`):
- new pad to any existing via, bottom-layer track or other part's pad: smallest 0.42 mm (R48 to C63, both new); no
  via and no bottom-layer track lies inside either block; nearest drilled hole 1.68 mm (C65 to the P_IN via at 28.86, 31.41);
- new pad to the board outline, 3 mm corner included: smallest 0.95 mm (U12 pin 1); courtyards: south 0.54 mm (U12), west 1.11 mm (C62);
- courtyard to courtyard: smallest 0.02 mm (U13 to C65), 0.05 to 0.07 mm at R49 / U13, C65 / R26, C60 / R47. DRC reports no courtyard overlap.

## Did not fit / assumed / flags

1. **The motor block is larger than "x 2..9, y 33..38.8"**: it uses x 1.11..8.11, y 33.00..38.96. The 1206 for C62 is
   the reason (courtyard 4.7 x 2.4); the east limit is R47's courtyard at x 8.22, so the block grew west and 0.16 mm
   south. U12's courtyard ends 0.54 mm from the south edge.
2. **C62 is about 2.3 mm from the VIN pin, not touching it.** C61 (100 nF) and C60 (10 uF) are nearer. C62 is still
   "47uF TBD" on a placeholder 1206; a smaller case would let it move closer.
3. **OUT2 and IN2 escape past the capacitors**: the gaps beside C61's VIN pad are 0.74 mm (west, to C62) and 0.43 mm
   (east, to C60's pad). The west one takes a 0.2 mm track at 0.2 mm clearance; OUT2 carries motor current through it
   (U12's pads are 0.2 mm wide anyway). Routing stage to confirm.
4. **I2C order**: U13 has SDA north of SCL, R26 (SCL) is north of R27 (SDA), 2.3 mm east. The two cross unless one
   uses a via or R26 / R27 swap places. Not swapped: stage-1 parts were not to be moved.
5. Courtyard gaps of 0.02 to 0.07 mm are legal but leave no slack for a part change.
6. **Silkscreen is not done**: the new parts keep their library reference texts, which overlap each other and pads
   (the 43 extra warnings); U12's reference and its pin-1 star hang over the south edge. J4's library footprint has a
   fab outline and fab polarity marks but **no silkscreen**: there is no free space around J4 for a "+" (L6 north,
   board edge west, screw keep-out south).
7. J4's schematic **Description** still says "4.2 x 2.6 mm oval, 1.3 mm hole" (only the Footprint field was allowed to change).
8. J4's library footprint has its origin midway between the pads, pad 1 at x -1.6 (as stage 1 built it on the board);
   the older WirePads footprint has pad 1 at the origin.
9. Clearance used for my own margin check: 0.2 mm (the project's Default net class), stricter than the 0.127 mm in the brief.
10. Unconnected count on the input board is 90 by my run of DRC; the BRIEF says 103 for stage 1. I did not look into the difference.
11. R15, R16 (locked) still lack pin names on their pads; "Update PCB from Schematic" in KiCad would write them.
12. Heights under the board, and the MP6550 / ADS1115 against the Pi's connectors below the overhang: not checked.

## Files

`board/` (result project), `board_in_stage1.kicad_pcb`, `sch_in/`, `proj_in/`, `lib_in/` (pristine inputs),
`scripts/` (`s3lib.py`, `netparse.py`, `step1_diff.py` ... `step6_fill.py`, `verify_locks.py`, `drc_summary.py`, `run_all.sh`),
`netlist_stage2b.net`, `erc_in.json`, `erc_stage2b.json`, `drc_in.json`, `drc_stage2b.json`, `top.png`, `bottom.png`,
`build/` (logs, diffs before / after, board after each step).
