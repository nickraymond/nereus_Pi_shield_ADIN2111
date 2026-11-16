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

## Stage 4 (GPIO pads, test points; silkscreen on a scratch copy), 2026-11-16 morning, Pacific

- Job A, committed (2754e8f, then 3c74899 TP42 moved, 8c102d7 J13 moved); `scripts/stage4_gpio/run.sh` rebuilds it from 5f43210:
  J11 GPIO14 / 15 at (15.30 / 17.84, 9.60), J12 GPIO18 / 19 at (57.70, 7.40 / 9.94), J13 GPIO17 / 20 at (62.60, 18.80 / 21.34), J14 GND x 3 at
  (62.20, 32.90 / 35.44 / 37.98); TP40 MOTOR_IN1 (2.20, 37.85), TP41 MOTOR_OUT1 (2.50, 35.50), TP43 I2C0_SCL (31.13, 33.27) on the bottom, TP42
  MOTOR_OUT2 (11.60, 31.00) on the top. FID5 / FID6 (62.2, 33.0) -> (62.2, 30.6). ~ADC_ALERT's bottom piece at x 17.29 moved to x 16.57.
  DRC `drc_s4.json`: 3 skew_out_of_range + 16 items_not_allowed, 0 unconnected, parity 0, warnings 517 -> 538 (no new type; the new parts' own
  silkscreen and pad-stack items); ERC 39, same items; `lock4.py` PASS; `.kicad_pro` / `.kicad_dru` identical to d30920b.
  On the way: the first lanes at x 58.75 lay 0.10 mm from J12's pads (two DRC clearance errors; the pre-check had printed them); moved to x 58.8.
  Not fitted: GPIO7, GPIO21, PI_3V3 / PI_5V pads, a fourth GND pad, and test points for the other nets asked for (no clear site; the session's report has the table).
- Job B, scratch copy only (`stage4_gpio_silk/silk_scratch/board/`, built by `scripts/stage4_silk/run.sh`); the committed board's silkscreen is
  unchanged. Lesson: KiCad's box for a Menlo text is 1.633 x its height and 0.842 x its width per character (measured with pcbnew), and
  silk_overlap works on that box; the first pass used the ink size and its stacked labels were all flagged.

## Stage 5 (one pad row under J1; three review fixes), 2026-11-16 morning, Pacific

Scripts `scripts/stage5_gpio_row/` (`run.sh` rebuilds from the stage-4 board 397fdfd and the stage-3 schematic 5f43210). Outputs:
`~/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/stage5_gpio_row/`. Baseline (397fdfd, my run, `drc_baseline_397fdfd.json`): 3 skew_out_of_range +
16 items_not_allowed, 538 warnings, 0 unconnected, parity 0; ERC 39.

- Row: y 6.70, on J1's pin columns, 15 pads (1.7 mm / 1.0 mm, stock PinHeader footprints, no outline, courtyard or model, out of BOM and position files),
  west to east: J15 PI_5V (10.91), GND (13.45), GPIO14 (15.99), GPIO15 (18.53) | J16 PI_3V3 (26.15), PI_3V3 (28.69) | J17 GND (33.77), GPIO17 (36.31) |
  J18 GPIO18 (41.39), GPIO7 (43.93), GND (46.47), GND (49.01) | J19 GPIO19 (54.09), GPIO20 (56.63), GPIO21 (59.17). J11..J14 and their tracks are gone;
  FID5 / FID6 back at (62.2, 33.0).
- 15, not 16: one PI_5V pad is left out (lowest in the priority list). The 16th clear column, 31.23, takes a GND pad only, and that pad would merge with
  Sofar's GND via at (32.231, 6.864) (first build: KiCad flashed the pad on all six layers through that via; hole 0.06 mm from the pad's copper): the same
  defect the review lists, so it is not built. Columns 21.07 / 23.61: VBUS (1.0 mm, Internal 2) must pass north of Sofar's vias (22.28, 8.32) / (23.73, 8.06).
  38.85: R43 and Sofar's GND via. 51.55: Sofar's GND and ADIN_PWR vias. Row at y 6.6 was measured too: 0.13 mm between a row pad and the J1 pad above it; 6.7 gives 0.23.
- Channel re-routed round the row (list and rules in `step3_route.py`): 19 existing nets, 8 GPIO nets, the two supply pads. VBUS keeps 1.0 mm.
- On the way: (1) `Models().clear()` after removing footprint graphics fails in pcbnew: the stock footprint is now read from a temporary copy with the
  outline blocks cut out as text. (2) first plan had 16 pads and a courtyard: DRC gave a short (PI_3V3 on Internal 2 against J16 pad 3 at 31.23, flashed on
  inner layers through Sofar's via) and courtyards_overlap J15 / R40; pad dropped, courtyards left out. (3) J1 pin 26's no-connect flag sat at the end of a
  wire, not on the pin (ERC no_connect_connected); `step1_schematic.py` now looks there.
- Planes (`planes.py`, `planes_head.txt` / `planes_s5.txt`): no new piece on any plane zone. 3V3 plane 312.72 -> 294.42 mm2, 1 piece; PI_5V lane main piece
  64.93 -> 63.65 mm2, 3 pieces as before; Sofar's GND plane zone 6 -> 4 pieces (main 962.35 -> 960.03), S3 GND 6 -> 5 pieces; NoConnect_Left 2 -> 1 piece.
  Sofar's top-layer GND zone at (23.2..31.4, 5.0..10.9) loses 33.17 -> 24.18 mm2 to J16's two pads (1 piece).
- Review fixes (`step4_review.py`, `via_in_pad_before.txt` / `_after.txt`): our vias within 0.3 mm of a pad 16 -> 9 pairs; TP41 to (2.2, 34.2), TP40 to
  (2.2, 37.45), C62 to (4.4, 31.27), C64 to (3.95, 34.12). Left: C61 (two vias), U12 pad 3, U11 pad 11 (no site), and four pairs at 0.21..0.30 mm the
  review did not name (R50, U13 x 2, JP2).
- Final (`drc_s5.json`, `erc_s5.json`): errors 3 skew_out_of_range + 16 items_not_allowed (the skew figures are the same; KiCad now pins them on a pad of
  the same net); warnings 541, no new type (lib_footprint_mismatch + 5 for J15..J19; silk_over_copper 37 -> 38: J1's bottom outline and the J1 / R39 /
  TP41 reference texts now lie over row pads or copper); 0 unconnected; parity 0; ERC 39, same items; `lock5.py` PASS; `.kicad_pro` / `.kicad_dru`
  identical to d30920b. Plots `plots_s5/`, crops `s5_*.png`, renders `s5_render_top.png` / `_bottom.png`: all looked at.

## Stage 6 (electrical review fixes; converter heat spreading), 2026-11-16 morning, Pacific

Scripts `scripts/stage6_review_fixes/` (`run.sh` rebuilds from the stage-5 board 76d258b; `step1_review.py`, `step2_heat.py`, `lock6.py`, `checks.py`).
Outputs: `~/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/stage6_review_fixes/`. Review: `stage4_review/electrical/REVIEW_ELECTRICAL.md` (written
against 397fdfd; every place re-measured on 76d258b with `checks.py`, which uses the review's own methods: `checks_head.txt` / `checks_s6.txt`).
Baseline (76d258b, my run, `drc_baseline_76d258b.json`): 3 skew_out_of_range + 16 items_not_allowed, 541 warnings, 0 unconnected, parity 0; ERC 39.

- 1 MOTOR_IN1 (Internal 2): was x 45.3 / 44.2 past U1's east pads and under Y1. Now gap x 47.74 at the header, x 48.45 (west of Sofar's 3V3 via (48.98, 12.11)),
  x 49.1 beside MOTOR_IN2 (x 49.5), diagonal x + y = 77.4 to the old lane y 38.05. ~PAYLOAD_FAULT moved to the gap x 45.2. MOTOR_IN2's diagonal moved to
  x + y = 79.2: between Sofar's BM1_DATA vias (47.02, 28.86 / 29.51) and GND via (47.93, 30.46) there is room for one lane only (pre-check scan: a 0.2 mm
  track passes for x + y = 77.2..77.6, a 0.28 mm range of centre lines). Distances (plan view, edge to edge, my measurement with pcbnew): MOTOR_IN1 to U1 pads 23-28 4.52 mm, to Y1's crystal pads (1, 3) 2.18 mm, to Y1's
  GND pad 2 1.49 mm; MOTOR_IN2 5.07 / 3.46 / 2.77 mm. Both cross Sofar's east GND slot (0.6 / 0.5 mm at (49.1 / 49.5, 13.7..14.5)): a net from J1 pins 29-33 leaves
  the slotted area only over a slot or past the slot's end beside U1, where it was. No GND fill above: 7.4 -> 5.2 mm (pin antipads and the slot).
- 2 MOTOR_nSLEEP (Internal 1): straight at x 55.36 to y 34.3, in the 0.5 mm gap between the BM1_N (x 53.12..55.12) and BM1_P (55.62..57.62) trunks; under
  BM1_P 11.0 -> 1.3 mm (the short piece at L1 pad 3, which it has to cross, plus 0.8 mm under that pad and 0.4 mm at J10). I2C3_SCL / I2C3_SDA (Internal 1):
  x 8.03 / 8.36 for y 17.6..25.9, west of the BM2_N trunk (x 8.53..10.53); under BM2_N 9.1 / 9.9 -> 0 mm. The three west lanes are at 0.33 mm pitch (0.13 mm gaps).
- 3 R9 (bottom, (9.3, 37.5)) -> top, (44.381, 9.89), pad 2 on the ADIN_MISO track at (44.781, 9.89) (frozen board: top, (44.78, 9.49), pad 2 at (44.78, 9.89)).
  ADIN_MISO's own copper 72.1 -> 15.0 mm, no branch. CFG0_STRAP (static, to JP4) is now 72.1 mm: top 1.1, Internal 1 59.8 (lane y 8.6 south of ADIN_MOSI, then
  the old ADIN_MISO lane; x 10.75 in the west), bottom 11.2. It lies 5.6 mm under BM2_N where it crosses the trunk's two diagonal pieces, and crosses the west slot at (18, 8.4).
  R47 / R2 (U1 pin 19, P1_LED_0 / SPI_CFG1: R2 4.7 k to JP3, R47 1 k in series to ADIN_TIMER) stay at (9.3, 35.9) / (9.3, 34.0): their frozen site
  ((39.8, 35.41) / (41.13, 35.01), top) now holds the PI_3V3 via (41.15, 35.0), the I2C3_SDA via (39.6, 34.58) and, underneath, the Qwiic pull-ups R10 / R24,
  and I found no other free site beside U1's south side in the time box. The 39.7 mm Internal 1 run from U1 pin 19 stays, and so do the perimeter tours of
  finding 10 (own copper before -> after: I2C3_SCL 89.1 -> 90.6, I2C3_SDA 87.3 -> 88.9, MOTOR_nSLEEP 99.6 -> 99.6, ADIN_TIMER 80.7 -> 82.0, MOTOR_IN1 74.6 -> 79.8,
  MOTOR_IN2 72.3 -> 73.2, PAYLOAD_EN 79.5 unchanged): nothing got shorter.
- 4 5V_LIFEPO4: both outer layers are blocked between F1 and JP1 (bottom: the 1.0 mm 5V_PI track at x 7.15 and the J4 track; top: the BM2_N trunk), so it stays on
  Internal 2, 0.8 -> 2.0 mm, 13.1 mm, two vias per end: (4.267, 15.887) (the dangling via in F1 pad 1, now used) + (4.267, 17.687), and (11.3, 23.05) (new) + (11.3, 23.9).
  IPC-2221 I = k dT^0.44 A^0.725, A in mil2, k 0.024 (internal), copper 0.0152 mm (the board file's stackup, In3.Cu): 1.08 A at 10 degC, 1.46 A at 20 degC,
  21 degC rise at 1.5 A (before: 0.56 A, 96 degC). Bottom piece to JP1 0.8 mm, 35 um, k 0.048: 2.03 A at 10 degC. In plan view the wider track lies 3.9 mm
  within 0.15 mm of switch-node copper (`checks_s6.txt`; before 2.6 mm), with the GND plane between.
- 6 not done: no site for a second 0.6 / 0.3 via on U12 VIN or GND passes the six-layer pre-check (grid 0.05 mm, boxes (6.5..9.0, 36.8..39.0) and
  (3.0..5.6, 35.9..37.4)); the only 0.45 / 0.2 sites are inside U12 pad 3.
- 7 VBUS feed (Internal 2): 1.5 mm at y 8.3 for x 10.7..19.8 and at y 8.45 / x 29.75 for x 25.5..29.75 (19.2 mm); 1.0 mm stays for 7.0 mm between x 19.8 and 25.5,
  where Sofar's GND vias (22.28, 8.32) / (23.73, 8.06) and the holes of J15 pad 4 / J16 pad 1 leave 1.07 mm. One via at each end stays (the converter end is
  converter copper, Sofar's via at the other). By my arithmetic 29.8 -> 22.4 mOhm; the neck is still 0.65 A at 10 degC / 0.89 A at 20 degC.
- 9 ADIN_TIMER (Internal 1): x 9.3 for y 9.3..15.9; nothing within 0.3 mm of switch-node copper now (was 2.2 mm within 0.15 mm, 4.3 mm within 0.3 mm). South of
  that it is the west lane of three, x 7.70: 0.58 mm from L6 pad 1 for 1.2 mm (y 17.5..18.7; before 0.73 mm for 5.6 mm). I2C3_SCL / SDA: 0.91 / 1.24 mm from that pad.
- 11 partly: the Internal 1 link from the via at U11 pin 1 to C49 is 0.5 mm wide (was 0.2), same 6.3 mm and two vias. A bottom-layer link does not exist without
  moving parts: U11's exposed pad reaches y 37.7 and VBUS_OUT (0.5 mm, y 38.2) leaves pin 10 between C49 and pin 1.
- 12 removed (input items, listed by the lock check): 5V_PI top stub (1.221, 14.511)-(1.346, 14.386) and VBUS bottom stub (11.221, 10.194)-(10.726, 10.688).
  Left, all on carried copper: GND top (32.531, 7.164..8.837); GND bottom (20.483..21.731, 9.389) and (24.267, 5.878..6.728); VBUS top (32.386, 10.409);
  VBUS_OUT top (24.431..24.981, 10.419); ~ADIN_RST Internal 1 (52.706, 6.214..11.114); vias ADIN_PWR (51.656, 7.164), GND (32.681, 5.964), (41.195, 17.178), (51.756, 6.164).
- 8 slot crossings now (`checks_s6.txt`; the method does not see a crossing within 1.7 mm of a through hole, so the I2C3 / VBUS lanes at x 18, y 7.6..8.3
  beside J15 pad 4 are not in its list but are still there): west slot ADIN_TIMER (17.4, 0.85), CFG0_STRAP (18.0, 8.4), PI_3V3 (17.3, 3.5); east slot
  ~PAYLOAD_FAULT (46.45, 16.7..17.2), MOTOR_IN1, MOTOR_IN2, MOTOR_nSLEEP (52.85, 3.5).
- Job 2 (Nick, as quoted in this session's task: "Yes, build it"): GND zone "S3 GND converter heat spreader (stage 6)" on the bottom layer, solid connections,
  62.03 mm2 in one piece (first build with the drawn outline: 58.44 mm2 in two pieces, the via (8.901, 7.459) on a 0.13 mm2 sliver). Outline changed in two
  places to reach vias that are there: north edge y 7.5 -> 7.2, and a tab (10.7..12.0, 13.9..15.3) onto Sofar's GND copper shape. Ten GND vias in the fill
  (eight that were there, two new) plus Sofar's two at (12.331, 14.764 / 15.464) through that shape; R38 pad 2 joins it. New vias (4.55, 11.6) and (4.4, 12.75):
  clear on all six layers at the drawn sites, not within 0.3 mm of a pad (`via_in_pad_s6.txt`). Third site (11.4, 12.3) not built: on Internal 1 it lies on the
  CFG0_STRAP lane (before stage 6: on the ADIN_MISO lane), and the nearest clear site (11.75, 12.6) is outside the zone, with GND copper on the GND plane only.
- Final (`drc_s6.json`, `erc_s6.json`): errors 3 skew_out_of_range + 16 items_not_allowed; warnings 541 -> 533, no new type (track_dangling 8 -> 6, via_dangling 5 -> 4,
  silk_over_copper 38 -> 37, silk_overlap 62 -> 58); 0 unconnected; parity 0; ERC 39; `lock6.py` PASS (R9 moved; two stubs removed); `.kicad_pro` / `.kicad_dru`
  identical to d30920b. Planes (`planes_head.txt` / `planes_s6.txt`): same number of pieces everywhere; areas 3V3 294.42 -> 293.08, P_IN 173.85 -> 172.69,
  Sofar's GND 1021.36 -> 1019.43, S3 GND 870.45 -> 870.07, 5V_PI strip 141.16 -> 140.18 mm2 (new via antipads). Plots `plots_s6/`, renders `s6_render_top.png` /
  `_bottom.png`, crops `look/s6_*.png`: looked at.

## Stage 7 (silkscreen proposal, second round; scratch copy only), 2026-11-16, Pacific

Scripts `scripts/stage7_silk/` (`run.sh`, `silk.py`, `check.py`, `netcheck.py`, `split.py`, `crop.py`); the committed board is only read (a9d0778).
Scratch board and outputs: `~/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/stage7_silk/` (`silk_scratch/board/`, `run_log.txt`,
`silk_report.json`, `drc_silk_before.json` / `_after.json`, `silk_top.png` / `silk_bottom.png`, `zoom_*.png`).

- Sizes: function names 1.0 .. 1.5 mm; pad-row, LED and polarity labels 1.0 mm (JLC minimum, `jlc_rules_2026-11.md` line 24); designators 0.8 x 0.75 mm,
  the frozen board's size (its 128 visible designators, read by the script); pin names, test-point names 0.8 x 0.7, jumper end marks 0.8 x 0.65, J8's
  pin names 0.7 x 0.7: all under JLC's 1.0 mm.
- Lesson (corrects stage 4's): kicad-cli measures a text's glyphs, not its box, against the silk clearance (0.15 mm): a "0" 0.12 mm from JP3's outline
  was flagged with "actual 0.1203 mm". Ink of a Menlo Bold text, measured on the frozen board's stored outlines: 1.06 x height (0.63 h above the
  anchor, 0.44 h below), 0.842 x size-x per character less 0.16 x size-x. Texts are planned by ink + 0.17 mm against each other; no text-on-text warning.
- Via tenting: board setup front and back tented; 173 vias set "tented", 108 "from board"; none untented. Via holes (+ 0.1 mm) are obstacles all the same.
- LEDs: texts, offsets and size copied from the frozen board (ADIN over D8, BM2 / PWR / BM1 under D10 / D8 / D9); ADIN 0.15 mm further from D8 (via
  (36.6, 34.0)). `netcheck.py` traces the schematic netlist: D10 ~ADIN_P2_LED1 -> U1 pin 48 (P2_LED_1) -> port 2 line pins 4 / 5 -> J9 (BM2); D9
  ~ADIN_P1_LED1 -> U1 pin 21 -> pins 27 / 28 -> J10 (BM1).
- Jumper names read from the frozen board: 5V SEL (JP1), LED (JP2), CFG1 (JP3), CFG0 (JP4); end marks 1 = ADIN_VDDIO end, 0 = GND end (one 0 shared
  between JP3 and JP4, both ends there are GND). The frozen board has no names at the strap resistors.
- Did not fit: JP4's name beside JP4 (JP2 north, JP3 west, R49 / R50 east, edge south): CFG0 / JP4 stands over CFG1 / JP3. MOTOR at 1.0 mm with J7 beside
  it (six vias where a larger name would go). J8: pin names in one row in pin order at 0.7 mm, J8 at the connector's west corner. J3: one letter per pin
  (G 3 D C), QWIIC and J3 at its north-east corner. The 5V pad's top label 0.15 mm east of the pad. "GPIO" title on the top only. JP1's end names. Net
  names at TP1, TP2, TP5, TP7, TP20, TP21, TP22, TP23.
- Designators hidden for want of a clear place: 19 (U12 R26 R40 R36 C64 C63 C65 C67 R10 R34 R48 R49 C49 C56 C57 C66 TP40 TP41 TP43); with text allowed
  over tented via holes (`RELAX=via`) 11 (R40 C64 C63 C65 R10 R34 R49 U12 TP40 TP41 TP43). Hidden on purpose: FID1..6, H1..4, J15..J19 (pad names).
- Checks (`run_log.txt`): errors 3 skew_out_of_range + 16 items_not_allowed before and after; 0 unconnected, parity 0. Ours / Sofar's, before -> after:
  silk_overlap 52 / 6 -> 7 / 6, silk_over_copper 34 / 3 -> 5 / 3, silk_edge_clearance 5 / 0 -> 0 / 0, text_height 57 / 81 -> 76 / 81, text_thickness
  53 / 84 -> 121 / 78. The 7 + 5 left of ours are footprint outlines (U13 / R50 / C67, C63 / C64, U12 / C61; J1's outline over the row pads, R48 / C63 / C65
  outlines, U10's "*"), no text of this stage. text_thickness is 199 in total after every run and Sofar's share moved without his texts changing: not
  explained. `check.py`: tracks + vias 1809, zones 179, pads 484, footprints 163, outline items 8, copper drawings 17, footprint graphics 2336 identical;
  227 texts of the 81 locked footprints identical. Net check: 91 labels, 91 OK.

## Stage 8 (mounting holes; LCSC numbers; PWM lines round the north-west), 2026-11-16, Pacific

Scripts `scripts/stage8_pwm_holes/` (`run.sh <1|2|3>` rebuilds jobs 1..N from the stage-7 commit c9a67c8, then DRC, ERC, `lock8.py`, planes, `checks.py`,
project files). Outputs: `~/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/stage8_pwm_holes/`. Baseline (c9a67c8, my run,
`drc_baseline_c9a67c8.json`, `erc_baseline_c9a67c8.json`): 3 skew_out_of_range + 16 items_not_allowed, 533 warnings, 0 unconnected, parity 0; ERC 39; `lock6.py` PASS.

- Job 1 (Nick, as quoted in this session's task: "Make the mounting holes fit the spec on the pi please"): H1..H4 pad and drill 2.70 -> 2.75 mm, still
  np_thru_hole, same places (`job1_holes.py`). Source in the repo: `Nereus_Pi_Shield_Adin2111/Pi_Zero_outline.dxf`, layer MOUNT_HOLES, four circles of
  radius 1.375 at (3.5, 3.5), (61.5, 3.5), (3.5, 26.5), (61.5, 26.5); the script reads them and stops if they are not 2.75 mm. The footprints keep the
  library name `MountingHole_2.7mm_M2.5_ISO7380`. `drc_s8_job1.json`: 3 + 16 errors, 0 unconnected, parity 0; warnings 533 -> 537, all four
  lib_footprint_mismatch on H1..H4 (106 -> 110); no clearance or hole item. The board file differs in the eight size / drill lines only (zone fills
  identical after a refill). ERC 39 (`erc_s8_job1.json`; one multiple_net_names item names VBUS where the baseline run named 5V_Buck_Input, with no
  schematic change: KiCad's choice between labels on one net differs from run to run). `lock8.py` PASS (H1..H4 listed); planes same as head; `.kicad_pro` /
  `.kicad_dru` identical to d30920b.
- Job 2 (LCSC numbers, schematic fields; `job2_lcsc.py`, `job2_sync.py`): `PLANNED LCSC` filled on U12 C3681248, U13 C468683, C60 C408132, C64 C386109,
  R48 C137968, J7 / J9 / J10 C189895, J8 C514175. Source: `~/NereusData/.../pi_zero_fit_2026-11-15/stage7_lcsc/LCSC_LOOKUP.md` (JLC part pages read
  2026-11-16); the script compares its list with that file's Result table and stops on any difference. The nine had no `SOURCING` field: added, hidden,
  "JLC stock (read 2026-11-16)". `PLANNED NOTE`: "LCSC number not looked up" -> "LCSC number confirmed on JLC's part page (read 2026-11-16)" on all nine.
  Not changed: `PLANNED MPN` (JLC's names carry suffixes, the lookup's open point 2), `PLANNED MFR` (missing on U12, U13, C60, C64), U13's reel form.
  One `PLANNED LCSC` stays empty: J5 ("Wire pads", `PLANNED NOTE` "No part to buy", `SOURCING` "No part: wire pads"). The board's footprints carry the
  fields too: the nine footprints' fields follow the netlist (stage 2b's `apply`; place, side, turn and pad nets asserted unchanged).
  `drc_s8_job2.json`: 3 + 16 errors, 537 warnings (as after job 1), 0 unconnected, parity 0; ERC 39 (`erc_s8_job2.json`, same items but the label-name
  flip noted under job 1); `lock8.py` PASS; planes same as head; `.kicad_pro` / `.kicad_dru` identical to d30920b.
- Job 3, a trial (Nick, as quoted in this session's task: "Yes, trial it"): MOTOR_IN1 from J1 pin 32 (GPIO12) to pin 12 (GPIO18); J18 pad 1 (x 41.39) is GPIO12
  now, fed from pin 32; MOTOR_IN2 stays on pin 33 (GPIO13). Both PWM lines go north of the header, round the north-west corner and down the west part
  of the board on Internal 2. Scripts: `job3_schematic.py` (three labels renamed where they stand; J18's value and description), `job3_sync.py`
  (old Internal 2 copper of GPIO18 26.2 mm, MOTOR_IN1 77.2 mm, MOTOR_IN2 72.3 mm removed, all our own; J1 / J18 pad nets from the netlist; net GPIO18 gone),
  `job3_route.py` (path, and the reasons for the detour and the swap, in its header), `measure.py`, `nognd.py`, `look.sh`.
  Before -> after (`measure_head.txt` / `measure_s8_job3.txt`, plan view, copper edge to edge; `nognd_head.txt` / `nognd_s8_job3.txt`; `checks_*.txt`):
  | net | layers | length | vias | to Y1 crystal pads 1 / 3 (any Y1 pad) | to U1 pads | Internal track with no GND fill on the GND plane | slot crossings |
  |---|---|---|---|---|---|---|---|
  | MOTOR_IN1 | Internal 2 77.2 + bottom 2.6 -> Internal 2 61.0 + Internal 1 1.3 + bottom 2.6 | 79.8 -> 64.9 mm | 1 -> 3 | 2.18 (1.49) -> 27.90 (27.75) mm | 4.52 -> 20.50 mm | 4.8 -> 6.2 mm | east slot (49.1, 14.05..14.55) -> west slot (17.32..18.22, 0.98) |
  | MOTOR_IN2 | Internal 2 72.3 + bottom 0.9 -> Internal 2 90.2 + bottom 0.9 | 73.2 -> 91.2 mm | 1 -> 1 | 3.46 (2.77) -> 22.77 (22.77) mm | 5.07 -> 16.00 mm | 2.7 -> 3.5 mm | east slot (49.5, 13.64..14.14) -> west slot (17.31..18.21, 0.65) |
  Target (10 mm from Y1's pads, 5 mm outside U1's pad area): met by both. MOTOR_IN1's largest x is 21.07 (pin 12).
  What is not as asked, or doubtful:
  (1) Slot: both nets still cross one GND-plane slot each, now the west one. Both of Sofar's slots are open at the plane's north edge (read off the GND-plane plot `look/head_full_gnd.png`: the west one
  from about x 17.5 at the edge south to about y 12.4, the east one from about x 53), so a net from a header pin between them reaches the west side only over a slot or between
  the slots' south ends beside U1. `checks.py` lists MOTOR_IN2's crossing only: MOTOR_IN1's is within 1.7 mm of J1 pin 10's hole, which that method skips.
  (2) GND above the north lanes is a strip: the fill reaches from y 0.51 to y 1.02..1.08 north of each pin (wider between pins; my scan at twelve x
  positions); the lanes' copper is y 0.55..0.75 and 0.88..1.08, for 39.3 mm (MOTOR_IN2, x 7.6..46.89) and 12.5 mm (MOTOR_IN1, x 8.07..20.52).
  (3) Swap: MOTOR_IN1 changes lanes with MOTOR_IN2 through two new vias (14.1, 26.8) / (13.2, 25.9) and 1.27 mm on Internal 1 (inside its own vias'
  antipads, so with no GND fill above it; nothing on the top layer over it, `checks.py` reports no "under" length). With MOTOR_IN2 on pin 12 and
  MOTOR_IN1 on pin 33 the order at U12 would come out right with no swap: not built, the task names the pins.
  (4) Detour: Internal 2 has no lane between the 2.0 mm 5V_LIFEPO4 track (edge x 12.3) and the P_IN vias (first at 12.78), nor west of that track (J4's
  pads, H4's keep-out): the lanes go east of the last P_IN via (x 15.8 / 16.13 for y 21.4..24.8) and back.
  Other figures: nearest switch-node pad (U10 pad 2) 2.01 / 1.68 mm in plan view, the GND plane between; ADIN_TIMER untouched (0.58 mm from L6 pad 1, as before).
  On the way: the first build had MOTOR_IN1's 45 degree piece over the 5V_FB via (9.28, 8.27) (pre-check printed gap -0.120; DRC shorting_items); the
  bend moved 0.4 mm south. Nothing else was straightened: ~PAYLOAD_FAULT keeps its jog (J18 pad 3 lies right south of pin 31).
  Final (`run_log_job3.txt`, `drc_s8_job3.json`, `erc_s8_job3.json`): errors 3 skew_out_of_range + 16 items_not_allowed; warnings 537 (as after job 1, same
  counts per type); 0 unconnected; parity 0; ERC 39, same items as the baseline; `lock8.py` PASS (new: J1 pin 12 -> MOTOR_IN1, pin 32 -> GPIO12; H1..H4;
  662 own tracks + vias); `.kicad_pro` / `.kicad_dru` identical to d30920b. Planes: same number of pieces everywhere; P_IN 172.69 -> 170.62, Sofar's GND
  1019.43 -> 1017.99, S3 GND 870.07 -> 868.99 mm2 (the two vias' antipads). Vias within 0.3 mm of a pad: 119 pairs, ours 9, as stage 6.
  Plots `plots_s8/`, renders `s8_render_top.png` / `_bottom.png`, crops `look/s8_*.png` (six areas x six layers, montages `look/s8_six_*.png`): looked at.
- Silkscreen scratch copy rebuilt from this board (`scripts/stage7_silk/run.sh`; `stage7_silk/run_log.txt`, the stage-7 files kept as `run_log_before_stage8.txt` /
  `silk_report_before_stage8.json`). `silk.py` now reads each pad-row label from the pad's net and, for a GPIO pad, checks that the J1 pin on that net has
  the GPIO in its pin name: J18 pad 1 reads "12" (was "18") on both sides, same place. Net check 91 labels, 91 OK; `check.py` PASS (tracks + vias 1815);
  95 labels placed, 10 left out, 19 designators hidden, silk warning counts as in stage 7; the only differences in the report are the two J18 pad 1 labels.
  `silk_top.png` / `silk_bottom.png` looked at. The committed board's silkscreen is unchanged.

## Stage 9 (the two PWM inputs change pins; the swap vias go), 2026-11-16, Pacific

Scripts `scripts/stage9_pwm_swap/` (`run.sh` rebuilds from the stage-8 head 61e1a9d, then DRC, ERC, `lock9.py`, planes, stage 6's `checks.py`, `measure.py`,
`nognd.py`, project files; `HEADONLY=1 sh run.sh` measures the head board only). Outputs: `~/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/stage9_pwm_swap/`.
Baseline (61e1a9d, my run, `drc_head.json`, `erc_head.json`): 3 skew_out_of_range + 16 items_not_allowed, 537 warnings, 0 unconnected, parity 0; ERC 39.

- Change (Nick, as quoted in this session's task: "Yes, swap them"): MOTOR_IN1 from J1 pin 12 (GPIO18) to pin 33 (GPIO13); MOTOR_IN2 from pin 33 to pin 12.
  `step1_schematic.py`: two labels renamed where they stand, at (116.84, 120.65) and (165.1, 151.13) on the Top-Level sheet; the file keeps its size. No text
  on any sheet and nothing in BRIEF.md names the GPIO of either input (searched GPIO13, GPIO18, PWM, MOTOR_IN): nothing else edited.
  `step2_sync.py`: removed MOTOR_IN1 Internal 2 60.98 mm, Internal 1 1.27 mm and its two swap vias (14.1, 26.8) / (13.2, 25.9), MOTOR_IN2 Internal 2
  90.21 mm; J1 pads 12 / 33 take their nets from the netlist. The vias at U12 ((3.7, 38.2) MOTOR_IN1, (7.0, 38.0) MOTOR_IN2) and the bottom pieces stay.
  `step3_route.py`: the two lanes are rebuilt where they were from the header to the south end of the detour (x 15.8 / 16.13), with the nets changed
  places: the outer / west lane is MOTOR_IN1 now. From there the pair turns 45 degrees once, at y 23.3 / 23.44 (stage 8: 24.2 / 24.77), and runs on
  x + y = 39.1 (where MOTOR_IN1's last piece lay) and 39.57 at 0.33 mm pitch to (6.0, 33.57); then south at x 4.4 and x 6.0 (the two gaps in U12's via
  field) into the two vias. 0 / 45 / 90 only, 0.2 mm, pre-check hits 0. Nothing else was routed or moved.
- Before -> after (`measure_head.txt` / `measure_s9.txt`, `nognd_*.txt`, `checks_*.txt`; plan view, copper edge to edge):
  | net | J1 pin | layers | length | vias | to Y1 crystal pads 1 / 3 (any Y1 pad) | to U1 pads | Internal track with no GND fill on the GND plane | slot crossing |
  |---|---|---|---|---|---|---|---|---|
  | MOTOR_IN1 | 12 -> 33 | Internal 2 61.0 + Internal 1 1.3 + bottom 2.6 -> Internal 2 91.0 + bottom 2.6 | 64.9 -> 93.5 mm | 3 -> 1 | 27.90 (27.75) -> 22.77 (22.77) mm | 20.50 -> 16.00 mm | 6.2 -> 3.0 mm | west slot, (17.32..18.22, 0.98) -> (17.31..18.21, 0.65) |
  | MOTOR_IN2 | 33 -> 12 | Internal 2 90.2 + bottom 0.9 -> Internal 2 59.7 + bottom 0.9 | 91.2 -> 60.7 mm | 1 -> 1 | 22.77 (22.77) -> 28.11 (27.91) mm | 16.00 -> 20.50 mm | 3.5 -> 3.7 mm | west slot, (17.31..18.21, 0.65) -> (17.32..18.22, 0.98) |
  The two nets together: 156.1 -> 154.2 mm, 4 -> 2 vias, no-GND length 9.7 -> 6.7 mm. The figures per net mostly change places, because the copper
  north and west is the same and the names moved. Nearest switch-node pad (U10 pad 2): MOTOR_IN1 2.01 -> 1.68 mm, MOTOR_IN2 1.68 -> 2.01 mm.
  Still there, as in stage 8: one crossing of the west GND-plane slot per net (`checks.py` lists the outer lane's only, now under MOTOR_IN1; the inner
  lane's is within 1.7 mm of J1 pin 10's hole), the GND strip above the north lanes, the detour east of the P_IN vias.
- Gates (`run_log.txt`, `drc_s9.json`, `erc_s9.json`): errors 3 skew_out_of_range + 16 items_not_allowed; warnings 537, same counts per type as the head;
  0 unconnected; parity 0; ERC 39 (the same items but KiCad's run-to-run choice of label name in one multiple_net_names item, as noted in stage 8).
  `lock9.py` PASS: against the stage-2c board as `lock8.py` (J1 pin 12 -> MOTOR_IN2, pin 32 -> GPIO12, pin 33 -> MOTOR_IN1; 658 own tracks + vias, was
  662); against the head board: J1 pins 12 / 33 only, 29 tracks + vias of the two nets gone and 25 new, other differences 0. `.kicad_pro` / `.kicad_dru`
  identical to d30920b. Planes: same number of pieces everywhere; P_IN 170.62 -> 172.69, Sofar's GND 1017.99 -> 1019.43, S3 GND 868.99 -> 870.07 mm2
  (the two vias' antipads are gone: the areas are those of before stage 8, job 3).
  Plots `plots_s9/` and `plots_head/`, crops `look/` (head left, stage 9 right): `pair_west_in2.png`, `pair_south_w_in2.png`, `pair_south_w_in1.png`
  looked at: one parallel pair from the corner to U12, no via on it; the Internal 1 piece and both vias are gone, other Internal 1 copper as before.
- Silkscreen scratch copy rebuilt from this board (`scripts/stage7_silk/run.sh`; `stage7_silk/run_log.txt`, the stage-8 files kept as
  `run_log_before_stage9.txt` / `silk_report_before_stage9.json`): net check 91 labels, 91 OK; `check.py` PASS (tracks + vias 1811, was 1815); 95 labels
  placed, 10 left out; the report differs in the via count only (283 -> 281). The committed board's silkscreen is unchanged.

## Stage 11 (approved silkscreen on the board; logo and name on the bottom; J4 holes), 2026-11-16, Pacific

Scripts `scripts/stage11_silk_logo/` (`run.sh <1|2|3>` rebuilds jobs 1..N from the stage-9 head 2fd2945, then DRC, `drcdiff.py`, ERC, `lock11.py`,
project files; `run.sh head` measures the head). Outputs: `~/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/stage11_silk_logo/`.
Baseline (2fd2945, my run, `drc_head.json`, `erc_head.json`): 3 skew_out_of_range + 16 items_not_allowed, 537 warnings, 0 unconnected, parity 0; ERC 39.

- Job 1 (Nick, as quoted in this session's task: "Silk screen approved"; "No need for you to keep working on silkscreen"): the stage-7 proposal is on
  the committed board. `run.sh` runs `stage7_silk/silk.py` unchanged on a scratch copy of the board folder and copies the board file alone back (SaveBoard
  rewrites `.kicad_pro` in the scratch folder only). `same_silk.py`: the 863 silkscreen items and footprint texts of this build against the scratch
  board Nick saw (`stage7_silk/silk_scratch`, built 11:42 AM from 2fd2945), compared without ids: 0 different. `stage7_silk/check.py`, head board
  against the result: tracks + vias 1811, zones 179 (outline and filled area), pads 484, footprints 163, outline items 8, copper drawings 17, footprint
  graphics 2336 identical; 227 texts of the 81 locked footprints identical. `silk.py` net check 91 labels, 91 OK; `netcheck.py` the two LED traces OK.
  Gates (`run_log_job1.txt`, `drc_job1.json`, `erc_job1.json`): errors 3 + 16; 0 unconnected; parity 0; warnings 537 -> 539, no new type
  (silk_edge_clearance 5 -> 0, silk_over_copper 37 -> 8, silk_overlap 58 -> 13, text_height 138 -> 157, text_thickness 137 -> 199: more small texts,
  as stage 7 reported); ERC 39; `lock11.py` PASS (against the head: 163 footprints, 1811 tracks + vias, 179 zones, 17 copper graphics, 484 pads, no
  difference); `.kicad_pro` / `.kicad_dru` identical to d30920b; schematic identical to 2fd2945. No silkscreen tuning: Nick does the final pass by hand.
- Job 2 (Nick, as quoted in this session's task: "Please add back the Bristlemouth fish logo with the Pi Adin 2111 shield details - there is a spot on
  the bottom of the board where you can add this between A_PWR and TP35. Just make it as large as you can while fitting there."): `logo.py`, `freearea.py`.
  The frozen board stores the logo as two filled silkscreen polygons (3560 and 221 points, line width 0) and the name as two Menlo Bold texts,
  "Pi Shield" 2.6 x 2.2 mm and "ADIN2111 Rev0" 1.6 x 1.5 mm. The frozen logo is the mote file's logo x 1.15, a quarter turn on (largest point
  distance 0.0000 mm after turning back; 4.456 x 3.731 against 3.245 x 3.874 mm): the copy is turned back upright as in the mote file, mirrored
  left-right and scaled. Clear space (`freearea.py`: pads and mask openings + 0.15, via holes + 0.1, bottom silkscreen and Sofar's texts + 0.15, part
  bodies + 0.1): the largest rectangles free of everything are 7.80 x 4.60 mm (x 35.75..43.55, y 12.30..16.90) and 9.10 x 3.80 mm (x 35.25..44.35,
  y 12.75..16.55); with the via holes not counted it would be 14.00 x 7.05 mm (x 30.35..44.35, y 10.80..17.85): tented vias stand in it.
  With the frozen board's letter widths the name does not fit clear of the via holes at any size from 1.0 mm (second line 10.1 mm long): the letters
  are 0.8 x as wide (the stage-7 label proportion). Logo and name are placed each for itself, a further 0.15 mm off every obstacle; the logo by its
  drawn shape, so a via may stand in its open inside. Largest logo: right of the name 0.86 x the mote's size, above it 0.60, left of it 0.52.
  Built: logo 2.79 x 3.33 mm at x 31.36..34.15, y 13.65..16.98 (one tented via, (33.38, 14.51), inside the head); "Pi Shield" 1.75 x 1.185 mm and
  "ADIN2111 Rev0" 1.077 x 0.808 mm, line 0.15 mm, block x 35.41..44.20, y 12.95..16.38; one group ("Bristlemouth logo and board name"). Finest logo
  line 0.30 mm (0.35 mm in the mote file, cuts through the upright and the lowest bar), eye 0.36 mm; JLC's minimum is 0.15 mm.
  Gates (`run_log_job2.txt`, `drc_job2.json`): errors 3 + 16; 0 unconnected; parity 0; warnings 539 as after job 1, same counts per type (the two new
  texts are among the text_thickness items, as every Menlo text; that count stays 199 as stage 7 noted); no silk_overlap, silk_over_copper or
  silk_edge_clearance item at the new graphics (`near.py`); ERC 39; `lock11.py` PASS, no difference from the head in copper, pads, footprints, zones;
  `.kicad_pro` / `.kicad_dru` identical to d30920b. Render `job2_bottom_big.png`, crop `job2_logo_area.png`: looked at.
- Job 3 (Nick, as quoted in this session's task: "Aux 5v I was hoping to use twisted 20AWG - will that fit the pins? Else the hole can get bigger but
  the pads stay the same"): J4's two holes 1.1 -> 1.3 mm round, plated; pads 2.2 x 3.3 mm oval, same places (`j4_holes.py`, text edits: the board's J4
  block (footprint name, two drill lines, the footprint's descr), the library file renamed to `WirePads_1x02_P3.20mm_Oval2.2x3.3mm_Drill1.3mm.kicad_mod`
  with the same changes, J4's Footprint field on the Top-Level sheet (one line)). `j4_measure.py` (`j4_before.txt` / `j4_after.txt`): ring 0.55 -> 0.45 mm
  across the pad's width, 1.10 -> 1.00 mm along it; hole edge to hole edge 2.10 -> 1.90 mm (rule 0.45 mm); hole edge to the nearest copper of another
  net, per layer: pad 1 Top / Internal 1 / Internal 2 / Bottom 1.45 mm (J4 pad 2), GND plane 0.75 mm (GND fill), PWR plane 0.75 mm (5V_PI fill); pad 2
  Top / Internal 1 / GND plane / Internal 2 1.16 mm (a 5V_PI via), PWR plane 0.75 mm (5V_PI fill), Bottom 0.90 mm (5V_PI track); the rule "JLC
  through-hole pad: hole to copper" is 0.3 mm. `jlc_rules_2026-11.md` has no ring minimum for a plated pad hole: its only ring figure is the via's
  (JLC 0.05 mm, board setting 0.1 mm). J5 as it is: 4.2 x 2.6 mm oval pads, 1.3 mm round plated holes, ring 1.45 / 0.65 mm.
  Not changed: J4's Description field (schematic and board) still reads "5 V in ... 1.1 mm hole".
  `sh run.sh 3` rebuilds all three jobs but gives the new silkscreen items new ids; the committed board is the job-2 commit plus `sh run.sh j4only`
  (board diff: the four lines). Gates (`run_log_job3.txt`, `drc_job3.json`, `erc_job3.json`): errors 3 + 16; warnings 539, same counts per type as
  after job 1 and 2 (lib_footprint_mismatch 110, none on J4); 0 unconnected; parity 0; ERC 39; `lock11.py` PASS (J4 listed: footprint name, two
  drills; nothing else differs from the head in copper, pads, footprints, zones); `.kicad_pro` / `.kicad_dru` identical to d30920b; schematic: the one
  Footprint line. Renders `s11_render_top.png` / `s11_render_bottom.png`, crops `job2_logo_area.png`, `s11_j4_top.png`: looked at.
