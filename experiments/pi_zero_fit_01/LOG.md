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
- Phase B (planes): errors 3 skew + 16 items_not_allowed; 120 unconnected; parity 0; lock PASS. New zones "S3 ...": one
  U-shaped GND zone on the GND plane (936 mm2), 5V_PI west strip (159 mm2) and a PI_5V lane (55 mm2) on the PWR plane,
  four screw keep-outs (r 3.0). Lessons: two same-net zones of equal priority give a `zones_intersect` error; with
  priority 1 KiCad cuts Sofar's fill back to the new outline and the fills abut (measured: they meet when grown by 1 um).
  The first outline left real gaps where it did not reach Sofar's fill (NW / NE chamfers, the y 27 notch edges): seen on
  the plot, outline moved 0.3..0.8 mm into Sofar's area. The 5V_PI fill is flagged `isolated_copper` until phase C ties
  its via at (4.27, 14.09) to the converter output.
- Phase B revised (two commits: scripts, then the board; my `git add` of the first one named only the scripts folder, so
  phase C first ran on the old board; seen in the printed zone areas, redone): PWR-plane lanes redrawn round the converter's vias.
- Phase C (power, west end): errors 3 skew + 16 items_not_allowed; 104 unconnected; parity 0; lock PASS. Routed: 5V_PI
  (converter -> plane -> JP1 / TP38 / motor capacitor bank / U12 pin 9), PI_5V (JP1 -> lane -> J1 pins 2 / 4), VBUS to the
  converter (Internal 2, 1.0 mm), Net-(J4-Pin_1), 5V_LIFEPO4. Not routed: payload switch group, 3V3 branch, U12's other pins.
- Phase D (part): eight ADIN header nets; errors 3 skew + 16 items_not_allowed; 96 unconnected; parity 0; lock PASS.
  ~ADIN_RST's via first sat 0.05 mm from Sofar's ADIN_PWR track (DRC clearance error, my pre-check had flagged it); moved to y 10.406.
- Stopped at 10:30 PM Pacific with 96 connections open (context ran out). Final DRC `drc_final_recheck.json`; renders and plots
  written, not all looked at. Report: `reports/STAGE3_REPORT.md`.
