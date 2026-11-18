# N6 shield: hand-over (2026-11-18, about 8 AM Pacific)

State: the real project `N6_Shield_ADIN2111/` is an N6 shield, placed per mock P, with routing stages A, B and the
first part of C done. **All of it is committed locally only; `origin/n6-shield` is at `af83088`. Nothing is pushed,
no pull request is open, no QE review has run.** Nick's words for this run (first-pass session's chat, 2026-11-18):
"no keep working, what is next", in answer to "Open a draft pull request against n6-shield for the QE review?".

| Commit | What | Gate result (kicad-cli 10.0.7, DRC with schematic parity) |
|---|---|---|
| `9fdada4` | stage 0a + 0b: schematic | ERC 0 errors, 2 warnings (the starting design's) |
| `d9f7e32` | stage 0c: board per mock P | 3 skew + 16 items_not_allowed (inherited), parity 0, 127 unconnected |
| `8859f01` | stage A: BM2 bus tracks, top layer | same errors, 123 unconnected; 9 new tracks; all 8 bus pins reach their inductor pads on top |
| `3c4f76a` | stage B: our planes round Sofar's block | same errors, 95 unconnected; 9 new zones; none of Sofar's zones touched |
| (next) | stage C part 1: the 5 V converter | same errors, 79 unconnected; 48 new tracks, 11 new vias |

Every stage: one script, run on a copy outside git, zones refilled by kicad-cli, then DRC against the board before,
the lock check (`scripts/stageA/lockcheck_all.py`: every item that was on the board before is unchanged, by uuid),
the plane check (`scripts/stageB/planecheck.py`) and the bus check (`scripts/stageA/buscheck.py`).
Run: `sh scripts/stageA/run_A.sh`, `sh scripts/stageB/run_B.sh`, `sh scripts/stageC/run_C.sh stepC1_converter.py C1`
(each takes the commit before it as base; default HEAD). Outputs and plots:
`~/NereusData/nereus_Pi_shield_ADIN2111/n6_shield/stageA`, `stageB`, `stageC1`.

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

## Next: stage C part 2 (not started), then D to H of the routing plan

Open nets after part 1: 5V_PI at U12 (C60, C62, C66, C61, U12 pin 9), MOTOR_OUT1 / OUT2 to J7 and TP41 / TP42,
U12's small parts (C63, C64, R48, pin 3 GND), then the signal stages. Notes for part 2, from the pad positions
read in this session (verify before use):
- 5 V from the PWR-plane area up to the bottom-side capacitors: a bottom track at X' -5.2 joins C62.1, C66.1, C60.1;
  vias fit at (-5.2, 41.07) and (-5.2, 43.78), between the pads. A GND via fits at (-3.4, 41.07).
- From there to C61.1 (1.69, 42.73) and U12 pin 9 (1.55, 41.2): not laid out. The motor outputs want the same
  corridor (X' 1.5..2.3, y 40..54 in the plan), so lay both out together. U12 is a 0.5 mm pitch part: 0.2 mm
  tracks at its pins.
- Keep the Internal 2 lane X' -5.6..-4.6, y 16..37.6 free of vias (motor logic, stage E).

## For Nick

- Decide: push and open the draft pull request for QE now, or after more routing stages.
- Decide: the header part for the 5 mm gap (decision 6 of `STAGE0_PLAN.md`).
- Ask Sofar: what the two GND-plane slots are for, and whether they must stay open to the board edge.
- Confirm on a real N6: which header column is P0 to P6 seen from the back.
- Still out of date in the schematic: Pi wording on the cover page and notes, the net name `5V_PI`, the title.
- Not in the schematic yet: test points on SCK, MISO, INT and VBUS.

## Traps

- `pcbnew.SaveBoard` rewrites the `.kicad_pro`: always work on a copy and copy only the `.kicad_pcb` back.
- A "KiCad is running" check with `pgrep -f KiCad` also matches the shell that runs the check when the command
  text contains the KiCad path. `run_C.sh` uses `pgrep -x kicad` / `pcbnew` / `eeschema`.
- KiCad wants overlapping zones to have different priorities even on the same net (our GND-plane zone is 1, his 0).
- Net names carry the sheet path for some nets (`/Top-Level Schematic/5V_PI`, `/Top-Level Schematic/BM2_P`) and
  not for others (`VBUS`, `GND`, `5V_FB`).
- Earlier traps still hold: `n6_rough_board.py` builds mocks only; in zsh write `"${d}:path"`; no poppler here.

Read first: `BRIEF.md`, `STAGE0_PLAN.md` (stage 0 results), `mocks/review/ROUTING_PLAN_P.md`, `PIN_MAP.md`,
`N6_FACTS.md`; then the rules on `development` (`CLAUDE.md`, `docs/TRACKER.md`, `docs/SPEC.md`).
