# N6 shield: hand-over (2026-11-18, about 10:45 AM Pacific)

State: the real project `N6_Shield_ADIN2111/` is an N6 shield, placed per mock P, with routing stages A, B, C and D
done and J21 moved to the model's header spacing. **All of it is committed locally only; `origin/n6-shield` is at
`af83088`. Nothing is pushed, no pull request is open, no QE review has run.** The routing session (second session
on this branch) took over on 2026-11-18. Nick's words for its run (its own chat, 2026-11-18): "go, and move J21 and
keep moving forward.", in answer to "Go for stage C part 2 on the N6 shield board, and is KiCad closed?" (KiCad was
not running by `pgrep` before each run). Pushing and the draft pull request still need his word.

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
| next commit | stage D part 3: ADIN_PWR to P13 | same errors, 45 unconnected; 3 new tracks, 1 new via |

Every stage: one script, run on a copy outside git, zones refilled by kicad-cli, then DRC against the board before,
the lock check (`scripts/stageA/lockcheck_all.py`: every item that was on the board before is unchanged, by uuid),
the plane check (`scripts/stageB/planecheck.py`) and the bus check (`scripts/stageA/buscheck.py`).
Run: `sh scripts/stageA/run_A.sh`, `sh scripts/stageB/run_B.sh`, `sh scripts/stageC/run_C.sh stepC1_converter.py C1`,
`sh scripts/stageC/run_C.sh stepC2_motor.py C2`, `ALLOW_REF=J21 sh scripts/stageC/run_C.sh stepJ21_move.py J21`,
`sh scripts/stageC/run_C.sh ../stageD/stepD1_east.py D1`, `sh scripts/stageC/run_C.sh ../stageD/stepD2_reset.py D2`,
`sh scripts/stageC/run_C.sh ../stageD/stepD3_adinpwr.py D3`
(each takes the commit before it as base; default HEAD; `ALLOW_REF` names one footprint the lock check lets change).
Outputs and plots: `~/NereusData/nereus_Pi_shield_ADIN2111/n6_shield/stageA`, `stageB`, `stageC1`, `stageC2`, `stageJ21`, `stageD1`, `stageD2`, `stageD3`
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
- The top GND pour is now in five pieces instead of three (the MOTOR_OUT1 trunk and the two test-point branches cut
  it); each piece has a GND via or pad, no new isolated-copper warning.
- Not connected on the board: U12 pin 5 (nSLEEP_LDO). The datasheet gives it an internal pull-down (3.3 V regulator
  off). That is the schematic's choice, not a routing matter.

## What stage D did (commits `d818176`, `058fede` and the ADIN_PWR commit after them; scripts in `scripts/stageD/`)

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
- An independent sub-agent review of stages C part 2 and D part 1 was started on 2026-11-18; its findings are in
  the session's report to Nick and, if they led to changes, in later commits.

## Next: stages E to H

Left over from stage D for later stages:
- R52 pad 1 (ADIN_VDDIO) and R9 pad 1 (CFG0_STRAP) wait for stage G; R26 / R27 pad 2 (N6_3V3) for stage F.
- One unconnected item that no stage of the plan names: BM1_P, Sofar's via at (20.06, 7.46) against his bottom
  track at (22.73, 5.73). Read it before stage G's "0 unconnected" gate.

Notes for stage E (motor logic and sense), from the copper now round U12:
- Free on the bottom: pin 1 (IN1) can leave south or east at y 39.15 towards TP40; pin 10 (IN2) must turn north-east
  right after the pin (C61 pad 1 is 0.09 mm from its line); pins 11 / 12 (VISEN, nSLEEP) leave east into the 0.9 mm
  gap before TP41.
- Vias near U12 must miss the top copper of MOTOR_OUT1 (trunk X' -1.2..-0.6, branch y 39.175..39.425 from X' -0.9
  to 3.3) and of MOTOR_OUT2's test branch (y 42.475..42.725 from X' 0.0 to 4.0).
- Internal 2 is still empty in the wing. Lines west from U12 fit at y 39.4..40.2 (the vias at y 41.07 start at
  y 40.77) or south of the MOTOR_OUT1 vias (below y 37.15).
- Keep the Internal 2 lane X' -5.6..-4.6, y 16..37.6 free of vias.

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
- Earlier traps still hold: `n6_rough_board.py` builds mocks only; in zsh write `"${d}:path"`; no poppler here.

Read first: `BRIEF.md`, `STAGE0_PLAN.md` (stage 0 results), `mocks/review/ROUTING_PLAN_P.md`, `PIN_MAP.md`,
`N6_FACTS.md`; then the rules on `development` (`CLAUDE.md`, `docs/TRACKER.md`, `docs/SPEC.md`).
