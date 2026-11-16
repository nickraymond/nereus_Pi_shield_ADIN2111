# pi_zero_fit_01: log (newest at the bottom)

## Stage 3 (routing), 2026-11-15 evening, Pacific

Scripts: `scripts/stage3_routing/` (`run.sh <phase>` rebuilds a phase from the previous phase's committed board, runs DRC,
the lock check and the project-file check). DRC JSON, logs, plots: `~/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/stage3_routing/`.
Report: `reports/STAGE3_REPORT.md`.

- Baseline (board of commit d30920b, my own run): errors 3 skew_out_of_range + 16 items_not_allowed; 137 unconnected; parity 0.
- Lesson: `pcbnew.SaveBoard` writes the `.kicad_pro` next to the board. Loading the input from a folder without the project
  and saving into `board/` replaced the JLC rule set with defaults (DRC then showed 484 errors). Caught by `git status`,
  restored with `git checkout`, and `run.sh` now copies the input into `board/` first and compares `.kicad_pro` /
  `.kicad_dru` / the schematic with d30920b after every run.
- Phase A (bus trunks): errors 3 skew + 16 items_not_allowed (same); 128 unconnected; parity 0; lock PASS.
  BM1_P does not go round the east as the brief planned: J5's pads leave 1.27 mm there; both BM1 trunks pass between
  L1's pads at 1.2 mm instead (report, phase A).
