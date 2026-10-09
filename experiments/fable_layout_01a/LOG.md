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

## M2, session 2 — QE round 1 fixes and the rest of the shortfall (2026-10-08)

Session 2 (Fable 5.1) picked up PR #31 at 0aec75c after QE round 1 (`qe/S7b_01a_round1.md`, CHANGES REQUESTED). The
board was rebuilt from M0 on a fresh checkout (the M3 snapshot is git-ignored), then from the M1 snapshot after every
placement or copy change and from the M3 snapshot after every routing change: 5 routing rebuilds in all. Board frame as
before. Everything below is in `tools/`; the final board's md5 is in HANDOFF.md.

### 1. QE F1 (MAJOR): both ADIN pairs shorted P–N at the transformer pads

- **Cause, measured on the committed board:** `router.commit_pair` ended a pair by running each track from the path's
  last offset vertex straight to its pad centre. The port-1 path arrived at T1 diagonally, so BM1_DATA_P's last Top
  segment (2.217, 27.5)→(4.317, 29.6) crossed T1 pad 2 (BM1_DATA_N, 0.65 mm pitch, 1.2 × 0.41 pads); port 2 likewise
  (BM2_DATA_N through T2 pad 1). `drcexclude.py`'s shorting / mask patterns `of T[12] on Top Layer` matched any item
  touching a T pad, so the 4 errors were filed as Sofar's footprint. Re-classified with the tightened patterns, the
  committed 293dc11 board is **111 Sofar + 16 new** (the 11 swap-figure items, the 3V3 via vs R21.2, the 2 shorts and
  their 2 mask bridges); REPORT.md §1/§5/§6/§8 corrected accordingly (a new §6 row 0).
- **The second defect behind the swap figure:** the A* kept a spacing counter in its state so the next figure could not
  overlap the last; a cell could be revisited with another counter value, so the path looped back over its own vias
  (the 11 errors). Both are gone: a layer change is now a macro with straight runs on both sides (`STRAIGHT_RUN` /
  `SWAP_RUN`), the first steps after a figure continue straight (`EXIT_STRAIGHT`) and may not turn back past 90°, the
  pads' approach is a straight lane along the pads' entry direction (the pair spreads from ±0.2 to the pads' pitch over
  `PAD_SPLAY` 0.2 mm, finished at the pad edge), the lane and the pins' stub are forbidden cells for the A*, and every
  emitted pair is **checked on the board** (`m4_route.pair_check`: one cluster per net, P–N ≥ 0.15 on every shared
  layer) before it is kept; candidates (two swing sides × two start variants) are all emitted, measured and taken off
  again, and the one with the shortest longer net is kept.
- **Where the vias go, as Sofar's mote:** the only figure the A* places on the way is the swap; the layer changes at the
  ends are fixed geometry. Port 1 starts with two vias straight out of U1's pins (staggered along the exit direction,
  1.0 / 1.48 mm, because two 0.45 vias do not fit side by side at the 0.5 mm pin pitch, and the AVDD via at (−0.95,
  28.0) and pin 29 leave the P via no spot nearer than 1.43 mm) and arrives at T1 on Top; port 2 starts on Top and
  gets its via pair beside T2's approach (port 1's would land in the crystal Y1's bottom pad). Each fixed piece is
  checked exactly with pcbnew shapes (`seg_free_exact`, the hole-to-hole with the real 0.2 drill) because the cell
  maps' 0.07 mm margin rejected spots that clear by 0.2.
- **Placement:** the P2T region's east edge moved from mote x 139.2 to 138.6: Sofar's GND pour-stitching via at mote
  (138.751, 116.854) serves R23 of the U5 cell on the mote and landed 0.4 mm in front of T2's data pads after the 180°
  rotation, where it blocked the approach. T1 was tried 0.3 mm east (7.0) while the approach was 1.4 mm long and ran
  into Y1's via; with the 0.9 mm approach it clears from 6.7, so the M1 position stands.
- **Unit test:** `tools/test_pair.py` has 18 blank-board cases (the opposite pad modelled as copper of its net, so a
  crossing fails) and the real-board case (`route_pairs` on the M3 snapshot, both ports, checked for continuity, P–N,
  0.15 / 0.35 to every other net and the mote's lengths). It found, in order: the swap-figure loop, a via pair at a
  bend, the pins' vias in the AVDD via, the approach vertex folding back, and the first stagger's lengths.
- **Result:** pairs **9.46 / 8.80 / 17.98 / 18.62 mm** (limits 9.5 / 9.5 / 21.3 / 21.3), P–N 0.15 mm, 0.175 mm to
  every other net, no T-pad item in DRC but Sofar's own.

### 2. QE F2 (MINOR): the ADIN region clip cut Sofar's ~{ADIN_INT} fan-out

- Sofar's via at mote (156.571, 107.509) transforms to (−7.19, 29.93): 0.08 mm inside the board edge, inside the 0.5 mm
  edge clearance, so no region could keep it. `m3_copy.HAND_VIAS` re-adds it by hand at **(−6.75, 30.25)** (0.45/0.2),
  where both clipped lead-outs (Top to (−6.804, 30.3), Bottom to (−6.804, 30.2)) lie under it; the script proves it on
  the board: edge 0.525 mm, joins Top + Bottom, 0.207 mm from other-net copper (blocks.json "hand"). INT then needs no
  routing at all: U1.39 → Sofar's Top lead-out → the via → Sofar's Bottom lead-out → R1.1, as the mote.
- `motecopy.Mote.pad_paths` lists every copied item that is a bridge between pads of its block on the mote (pads +
  tracks + vias joined by touching geometry, pours not counted); `m3_copy.py` records their board geometry in
  blocks.json "protected" (ADIN 113, P1T 12, B33/B5V 26 each, SENSE 27, B18 21 …), and `dangling.py` refuses to trim a
  protected item: a dangling one would be a cut pad-to-pad path and is listed loudly in "protected_dangling" (**0** on
  this board). `dangling.py` also retries a round once when its child process dies (seen once: exit 1 after the work was
  saved).

### 3. The rest of REPORT §6

- **VBUS at U11 pin 1:** U11's VBUS ball is pre-stitched to the plane before U11's own signals take the row.
- **The 3V3 via 0.14 mm from R21 pad 2:** `via_free` / `via_free_exact` take the class's real via diameter and
  clearance (the map radius implied a diameter 0.03 mm under 0.45); the hole-to-hole test uses the real drill.
- **5V_PI:** the bottom pour reaches under the 5 V cell again (y 7.5–24), and a 5V_PI patch on Internal 2 covers the
  same rectangle, as the mote carries the buck's output on a plane island (3V3 on In4): every bottom-pour island (the
  dividers R37–R40 cut it) gets a via into the patch; `zone_stitch` only places a via where the net has copper on
  another layer (the dangling 5V_PI via of 293dc11), and the island-join only joins islands that hold no via and
  starts from cells that are free for the track (one GND join started 0.1 mm from a 1V8 track).
- **U2 / U3 fan-out first:** the first routing rebuild of this session left U2's 1V8 and ADIN_PWR balls sealed on the
  bottom (U3's fan-out vias west, the 3V3 track south, the port-2 pair above) with no via spot. `m4_route.fanout` now
  gives the regulators' non-GND balls their vias before the pairs, on the ball's own layer, in the pocket exit's
  south-west corner (x < −2.8, y > 38.5) so the pair's lane along y 37.4–38.3 stays free (the first two placements, due
  south of U2 and then a Top-layer fan-out across the lane, blocked port 2). U2.B2 found no spot within 1.7 mm and was
  routed normally afterwards. The 3V3 / 1V8 / ADIN_PWR corridors cost 2.0 on the bottom so they stay off U2's layer.
- **Escapes** (`router.escapes`) now scan past the pad's own copper (Sofar's 0.1 mm stub at U2's balls ended every
  escape) and are given only to pads narrower than 0.35 mm (`FINE_PAD`): test points and 0603s start their class-width
  track themselves (with escapes for every pad, 8 nets exceeded the 2 mm fan-out allowance).
- **The pair length check** of the real-board test compares arcs by polygon collision: `SHAPE::GetClearance` returns 0
  for an arc in 9.0.6.

### Result (`out/m4/`, `out/m5/drc_exclusions.md`)

check_fixed 0 failures; blockcheck 0 missing / 127 trimmed; pairs 9.46 / 8.80 / 17.98 / 18.62 mm; rules: 0 segments
below class, 0 thin links beyond a pad field, 0 class-clearance items, Kelvin yes / yes; DRC **111 errors = 111
Sofar-copied features with reasons, 0 of new copper**; **1 unconnected = J1's no-connect pair**; 4 parity (MP1–4 pin 1,
Sofar Q6); 254 warnings, none a copper defect (0 track_dangling / via_dangling); 35 stitching vias + 2 fan-out vias +
1 zone-island via. Open for the record: the bottom GND pour island near (37.1, 13.9) under C58 / TP38 holds no via
(none fits; it carries no pad and KiCad's island removal may drop it); Q7 (DRC exclusion keys) still a reviewed table;
M3 (DFM) not started. Renders `out/m4/render_top.png`, `render_bottom.png`, `out/m4/layers/*.svg`; region views for the
design review in `out/review/` (`tools/review_views.py`: the mote's copper under each block's transform beside ours).

## Session 2.b, step 1 — JLCPCB limits fetched and encoded; DRC on session 2's board (2026-10-08)

Session 2.b (Fable 5.1) started from 287468b (session 2's final board b22752f, md5 de2e14fb…) on a fresh checkout; a
baseline rebuild from M0 in a scratch copy reproduced session 2's result (pairs 9.46 / 8.80 / 17.98 / 18.62, exit 0) before
anything was touched. Nick's order of work (LESSONS §4): the fab's rules first, then the board.

- **Fetched, not typed:** JLCPCB's PCB capabilities page, the controlled-impedance stackup page (read in the browser; the
  JLC06161H-3313 rows transcribed in order), the assembly capabilities page and JLCPCB's fiducial article, all read
  2026-10-08 and cited per row in `DFM.md` (URL + date). Where a figure is not on JLCPCB's pages (courtyards, copper
  balance, pours, thermal relief, test points) the row says so and the brief's own figure or a design choice stands.
- **Encoded:** `tools/dfm.py rules` writes the limits into `board/*.kicad_pro` (design_settings.rules: min_clearance 0.09,
  min_through_hole_diameter 0.2, solder_mask_min_width 0.1, mask expansion 0 (1:1), min_silk_clearance 0.15, min_text_height
  1.0, min_text_thickness 0.15; the brief's / the mote's stricter values stay for track width 0.15, via 0.45 / ring 0.1,
  hole-to-hole 0.25, hole clearance 0.25, edge 0.5) and into `board/*.kicad_dru` (PTH annular ring 0.15, pad hole to pad hole
  0.45, PTH hole to copper 0.28 outer / 0.3 inner). Limits DRC cannot express (same-net gaps, silk line widths, fiducial
  distances, test-point gaps, via-in-pad, copper balance, the stackup text) are measured by `tools/dfm.py check`, which
  writes `DFM.md` (one row per item: limit, source, enforced-by, measured worst case with where, pass/fail, what changed).
- **DRC on the board as it is:** 118 errors = session 2's 111 + 7 new (the M3 housing holes' pads 0.25 mm from the inner
  planes; JLC asks 0.3), 358 warnings (254 + 104 silk/text), 1 unconnected, 4 parity. Table 22 pass / 9 fail (DFM.md
  History). Nothing on the board changed (md5 unchanged); the fixes go into the M1–M3 scripts in the steps that follow.
- The scratch copy's `tools/` path layout: `geom.MOTE` resolves two directories up, so a scratch copy must sit two levels
  below a directory holding (a link to) `KiCAD_reference_designs/`.

## Session 2.b, step 2 (in progress) — frame 49 × 68, inserts, the OPTIONS trials (2026-10-08)

Work in progress, committed so the record keeps up with the scratch trials (the board in `board/` is still session 2's;
every trial runs on a scratch copy via `tools/trial.sh`, two levels under a directory that links `KiCAD_reference_designs/`).

- **Frame** (`tools/geom.py`): 49 × 68, x −10.5 … 38.5, y 0 … 68. The extra width went WEST, not east: the first trial with it
  on the east had T2's bottom cap inside MP4's keep-out and T1 against J1's socket courtyard at once, while the strip east of
  J1 (whose parts did not move) gained nothing. The extra height went SOUTH and is spent on the band between the inductor
  envelopes (L1's envelope, J5 and the south band 3 mm south; the band 26.5 … 37.5 = 11 mm, J1's SPI pins at its latitude).
  Inserts 1.5 mm nearer the wall (x −6.31: ring copper on the brief's 0.5 mm edge line; JLCPCB's 0.2 would allow 1.8 mm);
  the port-1 pair 2.5 mm south (3 mm put MP2's courtyard 2.91 mm from the Pi's H3 keep-out). Housing holes follow the corners.
- **Scripts parametrised**: planes (`m4_route.make_planes`: slots and islands from the envelopes and the frame; inner planes
  0.3 mm from holes, DFM row 12), bus feeds from `geom.INSERTS` and the inductor pads, the pairs' exit / entry directions
  from the placement (`axis_dir`), fan-out spots as "anywhere but the two pairs' exit lanes", the prestitch skip area from
  the ADIN block's parts, the pocket's hand via relative to U1 and per variant, `VARIANT=centre|pocket` in `m2_place.py`.
- **Order of routing**: the SPI (SCK, MOSI, MISO, ~{CS}) first on Internal 2 (Internal 1 at 1.5×, Top only for the pin escape,
  Bottom forbidden), then the fan-out vias, the pairs, the rest (Nick, LESSONS §3/§4).
- **Router**: `Grid.straighten` (step 3) replaces every staircase sub-run by one orthogonal + one 45° segment when the new
  cells are free on the same maps; applied in `route` and `route_pair` (the figures' runs fixed); 18/18 blank-board pair
  tests still pass; the pocket trial's pair legs went from 25 / 40 to 15 / 18 segments. `PAIR_MARGIN` 0.3 mm (QE N2).
- **DFM fixes in the pipeline**: `tools/dfm_fix.py` after placement (silk lines ≥ 0.15, references 1.0 / 0.15 moved to a clear
  spot or hidden, lines over pads clipped, footprint silk texts); JLC's stackup in M1; fiducials ≥ 3.35 mm from the edge;
  outer pours drop islands without a via; the bus feeds start 3.31 mm from the insert centre (NPTH-to-track).
- **Trials so far** (scratch, both variants through M4 each time): pocket = session 2's layout moved with the frame: pairs
  9.59 / 8.97 / 19.93 / 20.61, SPI 34–41 mm, DRC 113 / 109, 1 unconnected, rules 0 / 0 / 0. Centre: trials 2–4 (U1 rot 270,
  SPI pins facing J1) gave SPI 8–14 mm and port 2 11–13 mm but port 1 9.7–10.0 (the port-1 pins sit south-WEST of U1 at that
  rotation, T1 can only stand south-east) and Sofar's fan-out vias on T1's pads; trials 5–6 (U1 at the mote's rotation,
  T1 at the mote's relative spot) failed both pairs on the swap figure's 2 mm straight run (the emitter cannot make the
  U-turn the A* found behind the pads); trial 7 (T1 / T2 1 mm further from U1, C19 / R14 split off T1's cluster, the
  half-plane behind the pads forbidden) is running, together with Nick's J5-west / L1-south variant (`J5WEST=1`).

## Session 2.b, steps 2–5 — the board rebuilt at 49 × 68 (2026-10-08)

Board md5 **f33491bc576a45f1a6c9f3d160e82dc1** (rebuilt from M0 with `VARIANT=pocket`, then once more from the M1 snapshot after the silk fix's last
change; the second run reproduced the first's pairs and DRC exactly). Full record of the trials in OPTIONS.md addendum A3 and the
step-2 entry above; the result in REPORT.md.

- **Step 2 (frame, inserts, OPTIONS addendum):** 49 × 68 with the width west and the height south (A1), inserts at x −6.31 (A2), U1
  in the centre tried in eight routed trials against the pocket in four (A3): the pocket is built (pairs 9.39 / 8.77 / 19.93 /
  20.61; the centre's port 1 9.7–10.0 or no pair). Both cut jumpers on top in the north band (A4); Nick's strip question (A5) and his
  J5-west / L1-south idea (A3, `J5WEST=1`, tried on the centre placement) answered in numbers.
- **Step 3 (router):** `Grid.straighten` in `route` and `route_pair`; `PAIR_MARGIN` 0.3; the pair A* may not enter the half-plane
  behind the transformer pads (trial 5's U-turn); a start-swap variant exists (the figure at the pins' exit; it connected the
  centre's pairs but around the block). Pair legs 15 / 15 / 18 / 18 segments (were 25 / 25 / 40 / 40).
- **Step 4 (corridors):** the SPI first on Internal 2 (34–41 mm, no edge), then the fan-out vias (anywhere but the pairs' exit
  lanes), the pairs, the rest; `~{ADIN_INT}` and `~{ADIN_RST}` after the pairs as before.
- **Step 5 (rebuild and checks):** `check_fixed` 0 failures; blockcheck 0 missing / 127 trimmed; `check_rules` 0 / 0 / 0, 4 of 4
  pairs within, Kelvin yes / yes; DRC 109 / 70 / 1 / 4, `drcexclude` 109 with reasons, 0 without; `test_pair` 18 + real board ALL OK;
  `dfm.py check` 30 pass / 1 fail; renders `out/m4/`; `tools/review_views.py` → `out/review/` (regions for the pocket layout);
  `tools/ba_data.py` + `tools/before_after.py` → `out/before_after/` (before = b22752f, after = this board: 79 footprints moved,
  19 nets changed by ≥ 2 mm); `tools/summary.py` → `out/m4/summary.json` (the numbers every page and the report quote).
- New tools this session: `dfm.py`, `dfm_fix.py`, `trial.sh`, `ba_data.py`, `summary.py`; `build_all.sh` runs `dfm_fix.py` and a
  DRC after placement and takes `VARIANT`.


## Session 2.b, QE round 3 fixes and Nick's two decisions from the renders (2026-10-08)

QE round 3 (`qe/S7b_01a_round3.md`): CHANGES REQUESTED — F1 MAJOR: DFM row 30 passed on a hard-coded True while 64 new vias (the
router's stitching and escape vias) sat in SMD solder pads; F2: row 29 named only U6 of four footprints under JLC's 0.25 mm pad;
N1–N4 nits. Fixed: `router.Grid.padvia` (no new via where its copper would touch an SMD pad; test pads and thermal pads > 4 mm²
excepted), DFM rows 29 / 30 measured (row 30 against the mote's copied vias: 34 vias touch pads, Sofar's 16 / test pads 10 / thermal
8, new in solder pads 0), the small-pad 0.2 mm stub rule for plane nets (`m4_route.small_stub_class`, `check_rules.py` counts them
per pad with the rail clearance: R41.1 was open with a 0.5 mm stub and no via in its pad), BRIEF §2 dated note, the BM1_N stub
exclusion reason 0.25 mm, row 4's text, the lib_footprint_mismatch note for Nick (REPORT §9).

Nick, from the first rebuild's renders (mid-run, recorded in OPTIONS A6): the keep-out is the fitted 20 W inductor's courtyard +
2 mm, not the 50 W envelope (`geom.INDUCTOR_HALF`; the band 25.55 … 38.45, 12.9 mm; BRIEF §3 superseded), and U1 goes 3 mm east
(x −1.7, 8.8 mm from the edge; T1 / T2 / R43 / TP8 with it; the ADIN region is the mote's full one, no hand via). Rebuilt from M0:
board md5 **3a4dbf328b93efb1f5d06ab63fe45648**; pairs 9.39 / 8.77 / 20.19 / 20.87 (15 / 15 / 24 / 24 segments), SPI 31.3 / 32.2 / 37.5 / 39.1, rules 0 / 0 / 0 (6
small-pad stubs listed), DRC 109 (109 with reasons) / 68 / 1 / 4, blockcheck 0 / 128, test_pair ALL OK, DFM 30 / 1, 37 references
hidden. Pages and the summary regenerated; QE round 4 requested.


## Session 2.b, QE round 4 — APPROVED WITH NITS, nits fixed (2026-10-08)

QE round 4 (`qe/S7b_01a_round4.md`, on b34293d): F1 / F2 of round 3 verified fixed on the committed board and on a from-m0
rebuild; every number reproduces but the warning count. N1: 70 on a clean copy vs the pipeline's 68 — the 2 are
nonmirrored_text_on_back_layer for the stock SOT-23-THIN footprint's '*' text on B.Fab under U5 / U10 (top parts), which the
worktree's `.kicad_prl` hid from DRC → `tools/dfm_fix.py` now mirrors every back-layer footprint text (55 on this board), and the
DRC summary is run last, on the saved file; a clean-copy DRC gives 68 as well. N2: DFM row 30's exemption class is "large power
pads > 4 mm²" (L1 / L2 / C23 / U11's exposed pad), listed, with JLC's plugged-via option noted. N3: U11.1's 0.3 mm stub is the IN
pin's payload current, declared (REPORT §9 #3b). N4: DESIGN D31 vs the 20 W keep-out is Nick's decision outside this folder
(REPORT §9 #3e, OPTIONS A6). Rebuilt from the M1 snapshot: board md5 **23e5e8f939e6bf5e0c6b609e6c7ee14d**; pairs 9.39 / 8.77 / 20.19 / 20.87, rules
0 / 0 / 0, DRC 109 (109 with reasons) / 68 / 1 / 4, blockcheck 0 / 128, test_pair ALL OK, DFM 30 / 1. Pages and the summary
regenerated; the design review published for Nick (out/review, out/before_after).

Nick (mid-run): "once you have something that passes, write the PR so I can review and merge; the files stay in the experiments
folder" → PR #31 re-targeted at main and marked ready for review (the board stays in `experiments/fable_layout_01a/`; nothing
in the live project changes).
