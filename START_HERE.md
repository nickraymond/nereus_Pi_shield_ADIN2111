# START HERE: development branch

This branch holds everything that is not one specific board: the reference designs, the decision record, the
checks and scripts, and the history of how the Pi shields were made. Use it to start a new board (for example an
N6 adapter) without relearning what these boards taught.

## Branches of this repository (2026-11-17)

| Branch | What it is |
|---|---|
| `main` | The released board. Becomes the Pi Zero side-entry shield when M's review is closed and Nick releases it by pull request |
| `pi-zero-side-entry` | Pi Zero-size shield (65 x 39.5 mm) with motor driver and ADC, side-entry connectors. In review |
| `pi-zero-top-entry-incomplete` | Stopped top-entry connector variant. Do not build. Notes: `experiments/pi_zero_fit_01/reports/TOP_ENTRY_VARIANT.md` |
| `pi-full` | Full-size Pi shield (65 x 56 mm), frozen 2026-11-11 and ordered at JLC |
| `development` | This branch |

Each board branch holds one folder with the KiCad project and its libraries, a README and a short CLAUDE.md, and
nothing else. The project files keep the name `Nereus_Pi_Shield_Adin2111.*` on every branch (Nick, 2026-11-17:
formal part numbers and names come later, once designs ship).

## Where things are on this branch

| Path | What |
|---|---|
| `CLAUDE.md`, `.claude/` | Rules for agent sessions, the session-start ritual, the QE reviewer |
| `docs/SPEC.md` | Goal, verified facts, hard constraints, open questions |
| `docs/DESIGN.md` | Decision log (D1 ...), pin map, sheet hierarchy |
| `docs/TRACKER.md` | Sprint ladder and the rules agents work by |
| `docs/design-review/` | Power budget, JLC rule record, BOM reviews and purchase records, check outputs, QE reports |
| `docs/SOFAR_QUESTIONS.md` | Open questions for Sofar and their answers |
| `tools/check.sh` | Runs every check (ERC, DRC, net check, BOM export) on the full-size project |
| `KiCAD_reference_designs/` | Sofar's Bristlemouth mote and the other reference projects (read-only) |
| `Archive/`, `Outlines/` | Older material and outline drawings |
| `Nereus_Pi_Shield_Adin2111/` | The full-size board's project as on `pi-full`, plus its `scripts/`, `history/`, `layout_ref/` |
| `experiments/pi_zero_fit_01/` | The Pi Zero shield: `board/` (project as on `pi-zero-side-entry` at the time of the clean-up), `BRIEF.md` (decisions with Nick's words), `LOG.md` (every stage and its lessons), `scripts/` (one folder per stage), `reports/` (stage reports, the hand-over for M, the top-entry notes) |
| `experiments/fable_layout_01*/` | Earlier layout experiments |

The folders were left where the tools and documents expect them: `tools/check.sh`, the docs and the stage scripts
refer to these paths. The board branches are the place to edit a board; the copies here are reference snapshots
and will drift from the board branches. When they matter, compare with the board branch first.

Outputs that are not in git (check results, renders, gerbers, the fab package and the review reports of
2026-11-15 to 17) are on Nick's machine under `~/NereusData/nereus_Pi_shield_ADIN2111/`.

## Starting a new board from this

1. Read `docs/SPEC.md` (constraints), `docs/DESIGN.md` (what was decided and why) and
   `experiments/pi_zero_fit_01/BRIEF.md` (how a variant was specified).
2. Make a new branch from the board branch closest to the new design, not from `development`, and give the
   project its own folder. Keep `.kicad_pro` and `.kicad_dru` with the board: they carry the JLC rule set.
3. Keep Sofar's mote core as a locked block (footprints and his copper unchanged) and build around it. The lock
   check used here compares every footprint, track, via and zone with a snapshot (`scripts/stage3_routing/s3lib.py`,
   `verify_lock`).
4. Work in stages, each a script that rebuilds from the previous committed board and then runs DRC with schematic
   parity, ERC and the lock check (`experiments/pi_zero_fit_01/scripts/stage3_routing/run.sh` is the pattern).
5. Review before release: one electrical review, one manufacturability review, then a re-review of the changes.

## What these boards taught (each with where it is recorded)

- **Reuse proven blocks.** The 5 V converter is a copy of Sofar's 3.3 V converter; the motor driver and ADC come
  from the Urchin board, which JLC has built (Nick, 2026-11-16). `docs/DESIGN.md` D4, D13; `BRIEF.md`.
- **The 5 V rail is limited by heat, not by the 3 A chip.** Design target 1.5 A continuous (Pi 1.0 A + motor
  0.5 A); bench check of U10's temperature still open. Copper around the regulator matters: an older board with
  about five times the outer-layer ground copper ran the same circuit without trouble.
  `docs/design-review/power_budget.md`; the schematic's cover page.
- **Bus limits.** 12 W own load per module; 0.89 A through the port inductors for own load plus pass-through
  together. `docs/design-review/power_budget.md`.
- **JLC rules.** The rule files encode JLC's 6-layer values; an audit on 2026-11-16 added the missing ones
  (plated-hole ring, hole sizes, SMD pad spacing, pad to silkscreen, mask to copper). Without the `.kicad_pro` /
  `.kicad_dru` KiCad shows several hundred false errors. `docs/design-review/jlc_rules_2026-11.md`, `LOG.md`.
- **Inherited DRC items.** 16 `items_not_allowed` (an Altium plane cut-out imported as a no-via area under the
  ADIN2111) and 3 `skew_out_of_range` (the project's own length-matching rule on Sofar's data pairs) come with the
  mote block on every board. `experiments/pi_zero_fit_01/reports/HANDOVER_FOR_M.md`.
- **ERC is clean on the Pi Zero board** (0 errors) after no-connect flags on the fiducials and corrected pin
  types on the converters; the full-size board still shows the older 39 items. `LOG.md` stage 18.
- **Connector choice drives the south strip.** Side-entry connectors leave the board under their bodies free for
  vias; top-entry ones need that area for pads. Decide the entry direction before routing.
  `reports/TOP_ENTRY_VARIANT.md`.
- **Keep fast or switching lines away from the ADIN2111's crystal.** The motor PWM pair was moved to GPIO13 /
  GPIO18 and routed round the north and west for this reason. `LOG.md` stages 8 and 9.
- **A pad row beside a pin header needs clearance for soldering.** 0.43 mm to the header pads here, with the 5 V
  pad next to a GPIO pin: a wider gap or a different place is better on a new board. `LOG.md` stage 12.
- **Scripted edits of KiCad files.** `pcbnew.SaveBoard` rewrites the `.kicad_pro`; objects go stale after
  `Remove`; a "dangling" track can be the tail of a live one, so remove dead copper by trial on a copy with a
  connectivity check after each step. `experiments/pi_zero_fit_01/LOG.md` (top) and stage 20.
- **Working with Nick on a shared branch.** He edits and pushes from his own checkout: fetch and ask before each
  push, and keep scripted changes reproducible so they can be re-applied on top of his commit.
- **Still open for a next revision of the Pi Zero board:** most of the requested test points did not fit; the two
  spare ADC inputs are not brought out; single vias on the motor driver's supply and ground; a 1.0 mm neck in the
  VBUS feed; the PWM pair crosses a ground-plane slot. `reports/HANDOVER_FOR_M.md`.
