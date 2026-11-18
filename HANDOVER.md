# N6 shield: hand-over (2026-11-18, about 11:10 AM Pacific)

State: the real project `N6_Shield_ADIN2111/` is an N6 shield, placed per mock P, with routing stages A, B, C, D and E
done and J21 moved to the model's header spacing. **Pushed up to `602830d` as branch `claude/n6-shield-first-pass-afa1eb`; draft pull request 39 against
`n6-shield` (base `af83088`) is open for the QE review (Nick, routing session's chat, 2026-11-18: "Push, open draft
PR"). Commits after `602830d` are local until Nick says push. The QE review has not run yet.** The routing session (second session
on this branch) took over on 2026-11-18. Nick's words for its run (its own chat, 2026-11-18): "go, and move J21 and
keep moving forward.", in answer to "Go for stage C part 2 on the N6 shield board, and is KiCad closed?" (KiCad was
not running by `pgrep` before each run). Every further push still needs his word.

| Commit | What | Gate result (kicad-cli 10.0.7, DRC with schematic parity) |
|---|---|---|
| `9fdada4` | stage 0a + 0b: schematic | ERC 0 errors, 2 warnings (the starting design's) |
| `d9f7e32` | stage 0c: board per mock P | 3 skew + 16 items_not_allowed (inherited), parity 0, 127 unconnected |
| `8859f01` | stage A: BM2 bus tracks, top layer | same errors, 123 unconnected; 9 new tracks; all 8 bus pins reach their inductor pads on top |
| `3c4f76a` | stage B: our planes round Sofar's block | same errors, 95 unconnected; 9 new zones; none of Sofar's zones touched |
| `2fb0497` | stage C part 1: the 5 V converter | same errors, 79 unconnected; 48 new tracks, 11 new vias |
| `9541a01` | stage C part 2: the motor driver U12 | same errors, 64 unconnected; 35 new tracks, 15 new vias, 1 new zone |
| `e20079c` | J21 moved 0.04 mm east | same errors, 64 unconnected; lock check PASS with J21 allowed; header check: 0.00 mm offset |
| `d818176` | stage D part 1: east channel (SPI, INT, I2C to the header, R43) | same errors, 47 unconnected; 61 new tracks, 5 new vias; dangling warnings 14 + 5 down to 9 + 2 |
| `058fede` | stage D part 2: reset to P9 | same errors, 46 unconnected; 3 new tracks |
| `c46af62` | stage D part 3: ADIN_PWR to P13 | same errors, 45 unconnected; 3 new tracks, 1 new via |
| `3d056ac` | stage E part 1: motor logic and current sense | same errors, 40 unconnected; 35 new tracks, 4 new vias |
| `328363a` | stage E part 2: pot wiper, two links at U13 | same errors, 36 unconnected; 9 new tracks |
| `e3c8688` | fixes after the sub-agent review (three defects of stages C part 2, D part 1 and E part 2) | same errors, 33 unconnected; 13 new tracks, 3 new vias, 4 of this session's SDA segments replaced; pour check 0 untied pieces (was 2) |

Every stage: one script, run on a copy outside git, zones refilled by kicad-cli, then DRC against the board before,
the lock check (`scripts/stageA/lockcheck_all.py`: every item that was on the board before is unchanged, by uuid),
the plane check (`scripts/stageB/planecheck.py`), the bus check (`scripts/stageA/buscheck.py`) and, since `e3c8688`,
the pour check (`scripts/review1/pourcheck.py`: every filled piece of our GND pours has a GND via or through-hole pad).
Run: `sh scripts/stageA/run_A.sh`, `sh scripts/stageB/run_B.sh`, `sh scripts/stageC/run_C.sh stepC1_converter.py C1`,
`sh scripts/stageC/run_C.sh stepC2_motor.py C2`, `ALLOW_REF=J21 sh scripts/stageC/run_C.sh stepJ21_move.py J21`,
`sh scripts/stageC/run_C.sh ../stageD/stepD1_east.py D1`, `sh scripts/stageC/run_C.sh ../stageD/stepD2_reset.py D2`,
`sh scripts/stageC/run_C.sh ../stageD/stepD3_adinpwr.py D3`,
`sh scripts/stageC/run_C.sh ../stageE/stepE1_motor_logic.py E1`, `sh scripts/stageC/run_C.sh ../stageE/stepE2_wiper.py E2`,
`sh scripts/stageC/run_C.sh ../review1/stepR1_fixes.py R1`
(each takes the commit before it as base; default HEAD; `ALLOW_REF` names one footprint the lock check lets change).
Outputs and plots: `~/NereusData/nereus_Pi_shield_ADIN2111/n6_shield/stageA`, `stageB`, `stageC1`, `stageC2`, `stageJ21`, `stageD1`, `stageD2`, `stageD3`, `stageE1`, `stageE2`, `stageR1`
(a `_trial` folder beside a stage is the same step run on a scratch copy before the board was touched).

## What stage B found and decided (differs from `mocks/review/ROUTING_PLAN_P.md` section 1)

- Sofar's GND-plane zone is the old mote outline (X' 5.02..41.0, y -0.14..49.8). It already covers the east strip
  from y 7.05 to 41.64. His two slots are notches open to the mote's old east edge.
- His 152 rule areas on the two planes forbid nothing (all keep-out flags off): they do not block our zones and
  were left alone. **No outline of his was re-cut.** KiCad clips his fills at the new board edge.
- Our GND on the GND plane joins his with 0.5 mm overlap. **His two slots are carried on to the board edge** (no
  ground bridge across the slot mouths at the east edge), so his slot topology is as on the mote. The review's
  proposal was to end the slots at the block edge; that waits for Sofar's answer on what the slots are for.
- No pour of ours on top, Internal 1 or the PWR plane within 1.0 mm of the bus tracks outside the mote outline.
- J21 / J22 pads drop inner-layer copper where nothing connects (two more footprint-differs-from-library warnings).
- The review's "0.5 mm from zones to header pads" needs a rule in the `.kicad_dru` (Nick's word); not done. A pad
  clearance on the header pads would also block the one-track-per-gap routes between the pins.
- Pours on top, Internal 1 and bottom fill only where a GND pad or via lies in them; more stitching vias come with
  later stages.

## What stage C part 2 did (commit `9541a01`, script `scripts/stageC/stepC2_motor.py`)

- U12 has twelve pads and no centre pad; the MP6550 datasheet (Rev. 1.0, 7/16/2019) has no layout section, gives
  theta JA 80 C/W on a JESD51-7 board, and its pin table agrees with the board's nets. Heat leaves through the pins.
- 5 V: C62 / C66 / C60 joined on the bottom at X' -5.2 with three vias into the stage B 5 V area. **New zone
  "N6 5V U12" on the PWR plane** (priority 3): joins the stage B area over y 42.6..45.6, a band y 44.3..46.3, a tab
  X' 1.25..3.0 down to C61; two vias north of C61 pad 1. A 5 V track on an outer layer would cross a motor output.
- MOTOR_OUT1: bottom from pin 2 south, two vias at (1.195, 37.45) and (0.395, 37.45), then TOP: trunk at X' -0.9
  from y 38.35 to 44.4, 45 degrees to the lane X' 3.4 between J7's mounting pad and its pins, pins 1 / 2 from the
  west. TP41 (bottom): top branch at y 39.3 and a via inside the test pad at (3.95, 39.95).
- MOTOR_OUT2: bottom from pin 8, west at y 42.08 between the pin row and C61, trunk at X' 0.0 north to y 51.4,
  45 degrees to two vias at (3.3, 54.7) and (3.3, 55.95), top into pins 3 / 4. TP42 (top): via on the trunk at
  (0.0, 42.6) and a top branch at y 42.6.
- GND vias: (0.845, 38.45) for pin 3, (0.85, 43.6) for C61, (-3.4, 41.07) and (-2.55, 41.07) at the bulk capacitors.
  C64 / C63 / R48 pad 2 connect through the bottom pour.
- The top GND pour is now in more pieces (the MOTOR_OUT1 trunk and the two test-point branches cut it). **This left
  one piece with R38 pad 2 and R40 pad 1 and no via: the 5 V feedback divider's ground was open. Found by the
  sub-agent review, fixed in `e3c8688`.** KiCad's isolated-copper warning does not catch a pour piece that touches
  only surface-mount pads; the DRC showed it only as a zone-to-zone unconnected item.
- Not connected on the board: U12 pin 5 (nSLEEP_LDO). The datasheet gives it an internal pull-down (3.3 V regulator
  off). That is the schematic's choice, not a routing matter.

## What stage D did (commits `d818176`, `058fede`, `c46af62`; scripts in `scripts/stageD/`)

- East channel, one track per gap between J22's inner pads (gap centre lines y 18.10, 13.02, 10.48, 7.94, 5.40,
  2.86; MOSI passes above row 1 at y 20.55), then 45 degrees into the outer pin.
- MISO on top (stub, R9 pad 2, R54). MOSI on Internal 1 to a new via at (28.75, 19.671). SCK and CS on Internal 2
  from Sofar's vias to new vias at (29.0, 12.35) and (28.95, 10.25). R52 pad 2 and R56 pad 1 joined on top.
- SCL: via (28.85, 14.083), bottom at X' 29.6, branch to R26 pad 1, P4. SDA: via (28.65, 13.315), bottom at
  X' 28.3 to R27 pad 1, P5. INT: top at X' 28.382 south, P6. All five new vias are 0.45 / 0.20 mm (Sofar's size).
- R43: pad 2 to Sofar's GND via (31.732, 21.058); pad 1 on the bottom (X' 30.0, then y 14.7) to test pad TP8.
- Reset: Internal 1 from Sofar's corner (10.007, 15.633) through the gap y 13.02 of J21 into pin 8, no via.
- ADIN_PWR: one new via (0.45 / 0.20 mm) at (21.0, 15.728) on Sofar's Internal 1 track, then Internal 2: south-west
  to y 10.5, west, and 45 degrees into J21 pin 11; 20.6 mm (`scripts/stageD/stepD3_adinpwr.py`).
- **Deviations from the routing plan, for the QE review and Nick:**
  1. SPI copper from U1 to the header pin (`scripts/stageD/spilen.py`, branches included): MOSI 23.5, MISO 20.8,
     SCK 21.7, CS 26.4 mm. The plan proposed 20 mm or less and a spread of 5 mm or less. MOSI, MISO and SCK lie
     within 2.7 mm of each other. Sofar's own part is 9 to 15 mm of each line and the pins are on the header's outer
     column, so 20 mm is out of reach with the resistors where stage 0 placed them.
  2. No GND via beside the three new SPI vias: top, Internal 1 and Internal 2 all have the GND plane as their
     nearest plane in the east strip (no pour of ours there), so no line changes its reference plane, and a via
     touching only the GND plane is reported as dangling.
  3. N6_MOSI on top passes 0.18 mm from Sofar's GND via at (31.732, 21.058) and 0.23 mm from J22's row 1 inner pad
     (`stageD1/clearcheck.txt`); everything else new is 0.2 mm or more from other nets.
- An independent sub-agent review of stages C part 2 and D part 1 ran on 2026-11-18 (record:
  `~/NereusData/nereus_Pi_shield_ADIN2111/n6_shield/stageR1/subagent_review_2026-11-18.md`). Three defects, each
  confirmed on the board and fixed in `e3c8688` (`scripts/review1/stepR1_fixes.py`): the open divider ground above;
  ADIN_PWR's track ended 0.07 mm outside the round test pad TP8; R26 pad 2 (N6_3V3) was shut in, so SDA's bottom
  run moved to X' 27.9 and R27 pad 2 is joined to R26 pad 2 at X' 28.4. The review agreed with deviation 2 (no GND
  via) and saw no current concern at 1.24 A. It did not review stage E or the fixes.

## What stage E did (commits `3d056ac`, `328363a`; scripts in `scripts/stageE/`)

- MOTOR_IN1: bottom from U12 pin 1 into test pad TP40, via inside the pad at (3.9, 37.3). MOTOR_nSLEEP: via at
  (3.1, 39.95) in the 0.9 mm gap between U12 and TP41. MOTOR_IN2: via at (2.55, 42.0). All 0.45 / 0.20 mm.
- From the vias on Internal 2 as three parallel lines 0.4 mm apart at X' 3.9 (IN2), 4.3 (IN1), 4.7 (nSLEEP) from
  y 36 to 22; at J21, IN2 and IN1 run between the pad columns (X' 2.6 and 3.2) into pins 10 and 12, nSLEEP east of
  the inner column (X' 5.1) into pin 9. 33 to 35 mm each.
- **Deviation from the routing plan:** the plan's lane for these lines is X' -5.6..-4.6. From that lane they reach
  J21 in the order IN1, nSLEEP, IN2 (north to south), but the pins need IN1 last, so two lines would cross on the
  one layer. The direct band has the right order, is about 9 mm shorter, stays on Internal 2 under the GND plane and
  passes 0.35 mm east of the converter's GND via (3.15, 29.7) and 1.1 mm or more from the switch-node via
  (2.47, 33.75). No logic line is on an outer layer between y 22 and 37.5 (the plan's gate).
- MOTOR_VISEN: bottom from pin 11 through the gap, north-east to y 43.95 between TP44 and TP43, via at
  (7.4, 43.95) under U13, top to U13 pin 4. It is 0.33 mm from the nSLEEP via and 0.35 mm from TP41 (MOTOR_OUT1)
  at U12, where the plan asks 0.5 mm: the pins are 0.5 mm apart and TP41 stands 0.9 mm from them.
- Pot wiper on top: U13 pin 5, R51 pad 1, C67 pad 1, north past J8's mounting pad, J8 pin 2. R50 to U13 pin 1 and
  R49 pad 2 to U13 pin 2.

## Next: stages F to H

33 connections are left (`stageR1/drcsum.txt`, `drc.json`). By group:
- Stage F: I2C branches (U13 pins 9 / 10 and TP43 from Sofar's bus stubs on the bottom at about (10.3, 26.7) and
  (10.6, 26.0); QWIIC J3 pins 3 / 4), N6_3V3 (eight connections: both header 3V3 pins, the R26 / R27 pair, U13 pin 8,
  C65, C68, R49, J8 pin 1, J3 pin 2), U13's GND pin (no pour reaches it; under U13 the bottom holds TP43 and TP44).
- Stage G: CFG0_STRAP (R9 pad 1 to JP4), CFG1_STRAP, ADIN_VDDIO (R52 pad 1, JP2 / JP3 / JP4), the LED nets, the
  pin 19 net (R2, R47), ADIN_TIMER (TP45), ALERT's test pad TP44.
- One unconnected item that no stage of the plan names: BM1_P, Sofar's via at (20.06, 7.46) against his bottom
  track at (22.73, 5.73). Read it before stage G's "0 unconnected" gate.

## For Nick

- Decide: push and open the draft pull request for QE now, or after more routing stages.
- Settled 2026-11-18: the header footprints stay as they are (Nick: "the headers you have know are sufficient for
  our needs to solder").
- Settled 2026-11-18: J21 moved 0.04 mm east (Nick: "go, and move J21 and keep moving forward."), commit `e20079c`.
- Ask Sofar: what the two GND-plane slots are for, and whether they must stay open to the board edge.
- Settled 2026-11-18 by the maker's front-view pinout image: P0 to P6 are on the left seen from the front, so the
  board's assumption holds; all 32 header pads agree with the image (`N6_FACTS.md`, `scripts/n6_header_check.py`).
- Still out of date in the schematic: Pi wording on the cover page and notes, the net name `5V_PI`, the title.
- Not in the schematic yet: test points on SCK, MISO, INT and VBUS.

## Traps

- `pcbnew.SaveBoard` rewrites the `.kicad_pro`: always work on a copy and copy only the `.kicad_pcb` back.
- A "KiCad is running" check with `pgrep -f KiCad` also matches the shell that runs the check when the command
  text contains the KiCad path. `run_C.sh` uses `pgrep -x kicad` / `pcbnew` / `eeschema`.
- KiCad wants overlapping zones to have different priorities even on the same net (our GND-plane zone is 1, his 0).
- Net names carry the sheet path for some nets (`/Top-Level Schematic/5V_PI`, `/Top-Level Schematic/BM2_P`) and
  not for others (`VBUS`, `GND`, `5V_FB`).
- kicad-cli's SVG with `--page-size-mode 2` has its origin at the outline's corner (X' -6.6, y 60.6), not KiCad's.
- No PDF tool is installed; a datasheet's text can be read with macOS PDFKit through `osascript -l JavaScript`.
- The test-point pads (TP8, TP40..TP44) are round, 1.5 mm; a pad's bounding box is not its copper.
- A new track or via through a GND pour can cut a piece off from every via: read the pour check's last line.
- Earlier traps still hold: `n6_rough_board.py` builds mocks only; in zsh write `"${d}:path"`; no poppler here.

Read first: `BRIEF.md`, `STAGE0_PLAN.md` (stage 0 results), `mocks/review/ROUTING_PLAN_P.md`, `PIN_MAP.md`,
`N6_FACTS.md`; then the rules on `development` (`CLAUDE.md`, `docs/TRACKER.md`, `docs/SPEC.md`).
