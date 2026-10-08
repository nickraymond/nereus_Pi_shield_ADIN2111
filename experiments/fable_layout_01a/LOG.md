# LOG — layout experiment 1.a

*One entry per milestone, newest last. Board frame = KiCad board coordinates (mm): the Pi Zero's north-west corner is
(0, 0), x east, y south (BRIEF §2). Experiment 01's record is beside this one in `experiments/fable_layout_01/`.*

## M0 — options review (2026-10-08)

- Read CLAUDE.md, the brief, experiment 01's BRIEF/REPORT/LOG and its four QE reports, and every script in `tools/`
  (3,244 lines); measured 01's final board and Sofar's mote with pcbnew (U1's pins by net, every block's bottom-side
  parts relative to its anchor, the buck cells' pad sides, U11's pinout, the mote's pair geometry: 0.2 mm tracks,
  0.2 mm gap, via pairs 0.61–0.78 mm apart; Sofar's copper under U1 by layer: 44 mm on Internal 1, 15.8 mm on
  Internal 2).
- Trial placements on a scratch copy of this directory (pipeline through M2, kicad-cli DRC, `check_fixed.py`), not
  on the board here: the first try failed on TP35 inside MTG4's keep-out and five courtyard overlaps (C16/C8, C18/C8
  → T1 0.8 mm further east; TP19/D3; R34 and JP1 inside the M3 holes' ±4.25 mm courtyards → R34 beside U11, JP1
  0.6 mm south and the whole strip stack with it); the second try: 0 failures, 0 new overlaps (TP19 moved once more).
- `OPTIONS.md` written: Q1 T1/T2 moved toward U1 + a pair router; Q2 B18 to the band's bottom; Q3 the strip
  re-ordered (JP1 top at the north end, 5 V cell under it, C23 rotated, U11 rotated to face its loads) + pad-field
  escapes + no fallback classes; Q4 assumption kept and the alternative costed; Q5 ADIN block 0.3 mm west with the
  copy region clipped; Q6 JP1 on top, LEDs at the north edge with their resistors and JP2 under them; Q7 marker
  positions to be tried in M2.
- Nothing in `board/` changed (its md5 e6938b5828278a48a50f1042a007e202 is still experiment 01's final board).

## M1 — placement (2026-10-08)

- `tools/m2_place.py` carries the moves of OPTIONS §3 (block transforms) and the fresh positions; `check_fixed.py`'s
  U1 allowance removed (the ADIN block is 0.3 mm west, its copy region clipped 0.3 mm at mote y 107.9). Pipeline run
  `HEIGHTS=heights.json tools/build_all.sh m2`: ERC 494 / 0 / 494 (the schematic copy is unchanged), 138 footprints,
  12 blocks (83 parts) + 41 fresh parts, 0 parked.
- `check_fixed.py --heights`: **0 failures** (positions, J1 pins from the top, rings, insert pull-backs, keep-outs,
  envelope clearance 2.0 for every top part incl. U1, bottom heights ≤ 1.5 mm).
- kicad-cli DRC (`out/m1/drc_summary.txt`): courtyard overlaps **12 = Sofar's 10 intra-block pairs + MTG1/H1 and
  MTG3/H3** (0 new); the other errors are the insert contact and the parked-no-more leftovers of the empty board
  (unconnected 261: nothing is routed yet). TP19 moved once more (its courtyard touched D3's) after the M0 trial.
- Renders: `out/m1/render_top.png`, `render_bottom.png`: U1 in the pocket, T1 and T2 close to it, the LEDs on the
  north edge with JP2/R44–R46 under them, JP1 top at the strip's north end over L6, C23/C22 rotated in the strip, U11
  at the strip's south end facing J5, B18 under the band's east end.

## M2 — block copper, planes, routing (2026-10-08) — stopped short of its bar on Nick's instruction

Nick asked for a wind-down after ~2 h ("get a QE to review the work thus far"). M2 is committed as it stands, with the
shortfall in numbers (REPORT.md §9); M3 (the JLCPCB DFM sweep) was not started.

- **Pipeline changes** (all in `tools/`, every check still running): `build_all.sh` restarts from a snapshot of the
  milestone before (`START=m2` from `out/m1/`, `START=m4` from `out/m3/`; a restart on the board as left by a later step
  doubled the copper once); `m2_place.py` replaces its blocks in `blocks.json` on a rerun; a new `m3b_planes.py` adds the
  plane zones right after the copper copy and `dangling.py m3 --all` trims Sofar's clipped lead-outs before routing (182
  items on the first pass: the SPI / RST / PWR / INT stubs toward the mote's processor, which blocked the pocket's exits
  in 01), so the post-route trim only touches the router's own tails.
- **Router** (`router.py`): exact distance-based occupancy maps instead of inflated cells + integer-disk dilation (the
  grid build went from 268 s to 19 s and no longer over-blocks by ≈ 0.2 mm, so 0.2 mm tracks thread U1's thermal vias);
  net-coded cross-class maps (a power-class net's own pad no longer blocks its own 0.15 mm escape); pad-field escapes
  (≤ 1 mm 0.15 mm stubs to the first cell where the class width fits) instead of fallback classes; per-layer corridor
  costs; the insert pull-backs stamped as keep-outs (no clearance, no cross-class bits); Sofar's Hole_M3 rule areas
  honoured by their flags and layers; fiducial mask apertures blocked; a near-miss exact geometry check for via spots;
  `route_pair` / `commit_pair`: an ADIN pair as one 0.6 mm virtual track (two 0.2 mm tracks, 0.2 mm gap, the mote's
  geometry) with a parity-aware A* whose layer change is a macro step — a straight via pair, or the swap figure (two
  0.45 vias 0.6 mm apart along the track, the tracks exchanging sides, either side) — validated by a unit test on a blank
  board (7 cases: straight, diagonal, turns, both sides, swap then an immediate turn).
- **m4_route.py**: U11's signals before the payload path (its vias otherwise land under the pin row); 3V3 to U3 before
  the other pocket rails; INT first among the pocket's nets; rails at the brief's 0.2 mm; GND stitched with 0.2 mm /
  0.45 vias; a bottom-side GND pour as the mote's bottom layer with solid pad connections (Sofar's setting: the mote's
  GND pours are ZONE_CONNECTION FULL); the 5V_PI pour x 29.7–38, y 7.5–24 (solid); connectivity through pours per
  layer and per island (an outer-layer island counts only with a via / PTH in it); a zone-island via step; every
  cluster pair tried once so one failed link no longer aborts a net.
- **Result** (`out/m4/`): check_fixed 0 failures; blockcheck 0 missing / 135 trimmed; pairs **10.7 / 8.59 / 18.24 /
  18.88 mm** (limits 9.5 / 9.5 / 21.3 / 21.3: port 1 P over by 1.2 mm — the run before this one had 8.95 / 9.11 but the
  same figure defect); rules: 0 segments below class, 0 thin links beyond a pad field, 6 class-clearance items (all
  VBUS_OUT's 0.6 mm escapes at U11 / J5 against neighbours at 0.15–0.25); DRC 127 errors = 115 Sofar-copied features
  with reasons + **12 of the new copper** (11 are the port-1 pair's swap figure colliding with itself on Internal 1 at
  (0.1–0.6, 27.1–27.5): the figure passes the unit tests but a case on the real board does not — a turn or the second
  via figure too close; 1 is a 3V3 stitching via 0.14 mm from R21's FB pad); 1 via_dangling (a zone-island via with no
  copper on another layer); unconnected **4**: J1's no-connect pair (by design), ~{ADIN_INT} U1.39 (no via spot in
  Sofar's crowded west fan-out: VDDIO's bottom track at (−5.58 … −6.47, 30.84) covers the only exit), VBUS U11.1 (no
  0.5 mm path from the pin's escape to the plane after the signals), and the two 5V_PI pours (the copied Top output
  pour and the bottom pour share no via; the bottom pour is split into islands by U10's dividers and the islands could
  not be joined at 1.0 mm).
- Not done: M3 DFM sweep, `DFM.md`, Q7 (the exclusion keys); the 01 renders of the mote for comparison are in
  `../fable_layout_01/out/m5/mote_layers/`.
