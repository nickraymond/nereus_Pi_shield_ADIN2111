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

## Stage 3, second session, 2026-11-15 late evening, Pacific

- Phase F (BM1 fix): J5 to (61.9, 10.6), FID4 / FID2 to (62.6, 7.7); BM1_N 2.0 mm on the frozen path under L1; BM1_P 2.0 mm east of L1 with a
  1.4 mm neck for 2.9 mm. Errors 3 skew + 16 items_not_allowed; 96 unconnected; parity 0; lock PASS (three footprints moved on instruction).
  Lesson: after `board.Remove()` (or a second `LoadBoard`) pcbnew's Python layer stops returning usable objects; removals now run in a child
  process, one `GetTracks()` call, nothing queried afterwards.
- Phase G (U11 group, VBUS_OUT to J5): same errors; 79 unconnected. One pre-check hit (PAYLOAD_EN against a UVLO via) was also a DRC clearance error; lane moved.
- Phase H (signals, feeds, ground): same errors; 13 unconnected. One short on the way (a ~PAYLOAD_FAULT via on Sofar's ~ADIN_RST Internal 1 track; the
  pre-check had printed it and I had not read it): via moved, DRC clean. `hint.py` (grid search) proposes corridors only; its first version missed the screw
  keep-outs (bounding box too small), seen when a proposal ran through one; fixed before anything was placed.
- Final: DRC `drc_final2.json` 3 + 16 errors, 13 unconnected, parity 0; ERC 39; lock PASS; plots `plots_final2/`, renders `final2_*.png`.
  Open: U12 outputs (placement), MOTOR_nSLEEP, ADIN_TIMER, ADIN_MISO to R9, strap net to R2 / R47, I2C3 from the header, TP24 ground, orphan U11_RTN via; PI_5V unchanged.
  Report: `reports/STAGE3_REPORT.md`, second part.

## Stage 3, third session, 2026-11-15 night, Pacific (written by the fourth session from commit d7da363 and `phaseJ.py`; that session was cut off)

- Phase J (motor group): U12 (6.3, 37.2) -> (5.2, 36.9) and turned so OUT1 faces west and OUT2 east, as J7's pins 1-2 / 3-4; C60, C61, C62, C63,
  C64, C66, R48 re-placed round it (list with coordinates in the lock check's output). Outputs 0.5 / 0.6 mm with two vias each to J7; VIN from the
  PWR-plane 5V_PI fill with C61 at the pin; bulk capacitors on a 1.0 mm rail north of J7's pads. Commit message: 3 skew + 16 items_not_allowed,
  8 unconnected, parity 0, lock PASS. My own DRC of that commit (`drc_s3_baseline_d7da363.json`) gives the same.

## Stage 3, fourth session, 2026-11-16 morning, Pacific

- Baseline (d7da363, my run): errors 3 skew_out_of_range + 16 items_not_allowed; warnings 520; 8 unconnected; parity 0. The 8: TP24 ground,
  I2C3_SDA, I2C3_SCL (J1 pins 15 / 13), strap net R2 to Sofar's via (40.52, 27.88), ADIN_MISO to R9, MOTOR_nSLEEP (J1 pin 29 to U12),
  ADIN_TIMER (R47 to J1 pin 36), and the orphan U11_RTN via (28.43, 6.21).
- Phase K: the orphan via is removed (Nick, 2026-11-16, quoted in this session's task: "Yes delete the orphan via"). Before removing it the script
  lists all copper within 0.6 mm of its pad on every layer: 11 items, none on U11_RTN (J1 pin 17, GND / 3V3 fills, the VBUS track on Internal 2).
  **The lock check's expected list changed for exactly this one item**: `REMOVED_OK` in `s3lib.py` holds its uuid (90140fec-...), `verify_lock`
  prints it as "removed on instruction" and still fails on any other missing item. Six nets routed on Internal 1 as buses. R47 turned 180 deg and
  0.2 mm south, R9 turned 180 deg in place (their reference texts stay where they were). Result: same 19 errors, 1 unconnected, parity 0, lock PASS.
  On the way: ADIN_MISO's first lane (x 11.9) ran through three ground vias at (11.7..12.3, 14.8..15.5); the pre-check printed it, DRC showed
  9 errors and the lock check failed (KiCad had put the vias on the track's net). Lane moved to x 10.6, rerun clean. Turning R47 / R9 also turned
  their reference texts onto copper (one more silk_over_copper warning); `prestep` got a `keep_ref` option.
- Phase L: TP24 ground on the bottom; PI_5V second path on the bottom; U12 VIN 0.3 -> 0.4 mm and 0.4 -> 0.5 mm. 0 unconnected. On the way: the
  first PI_5V lane shorted to the 5V_LIFEPO4 via (I had read its position off a picture, 11.1 for 11.3; the pre-check printed it); lane moved to
  x 12.09 at 0.5 mm, and the 1.0 mm part to x 13.45 clear of Sofar's ground polygon. A text replace of mine with an empty search string blew
  `phaseL.py` up to 1.5 MB; rewritten whole before anything was committed.
- Phase M: clean-up, see the report. `prestep` can now remove one exact segment (`'seg'`).
- Final (commit of phase M, `drc_final3.json`, `erc_final3.json`): errors 3 skew_out_of_range + 16 items_not_allowed; warnings 517; 0 unconnected;
  parity 0; ERC 39; lock PASS; `.kicad_pro`, `.kicad_dru`, all schematic files identical to d30920b (`git diff --stat d30920b -- board/` lists the
  `.kicad_pcb` only). Plots `plots_final3/`, renders `final3_top.png` / `final3_bottom.png`, all eight looked at. Report: third part.

## Stage 4 (GPIO pads, test points; silkscreen first pass on a scratch copy), 2026-11-16 morning, Pacific

- Job A, committed (2754e8f), `scripts/stage4_gpio/run.sh` rebuilds it from 5f43210: J11 GPIO14 / 15 at (15.30 / 17.84, 9.60), J12 GPIO18 / 19 at
  (57.70, 7.40 / 9.94), J13 GPIO17 / 20 at (62.60, 17.85 / 20.39), J14 GND x 3 at (62.20, 32.90 / 35.44 / 37.98); TP40 MOTOR_IN1, TP41 MOTOR_OUT1,
  TP42 MOTOR_OUT2, TP43 I2C0_SCL. FID5 / FID6 (62.2, 33.0) -> (62.2, 30.6). ~ADC_ALERT's bottom piece at x 17.29 moved to x 16.57.
  DRC `drc_s4.json`: 3 skew_out_of_range + 16 items_not_allowed, 0 unconnected, parity 0, warnings 517 -> 539 (no new type; the new parts' own
  silkscreen and pad-stack items); ERC 39, same items; `lock4.py` PASS; `.kicad_pro` / `.kicad_dru` identical to d30920b.
  Not fitted: GPIO7, GPIO21, PI_3V3 / PI_5V pads, a fourth GND pad, and test points for the other nets asked for (no clear site; see the session's report).
- Job B, scratch copy only (`stage4_gpio_silk/silk_scratch/board/`, built by `scripts/stage4_silk/run.sh`): a first pass, not finished. The committed
  board's silkscreen is unchanged.
