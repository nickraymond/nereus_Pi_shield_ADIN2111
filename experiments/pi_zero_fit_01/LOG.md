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
