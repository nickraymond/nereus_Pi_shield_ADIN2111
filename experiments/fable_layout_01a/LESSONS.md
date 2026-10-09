# LESSONS — layout experiment 1.a, sessions 1 and 2 (2026-10-08)

*Written at the wind-down of session 2 for Nick's review and for session 2.b. The numbers are from `out/m4/`,
`out/before_after/` and the two QE reports in `qe/`. The before/after page (`out/before_after/index.html`) and the
design review (`out/review/index.html`) are the pictures behind this text.*

## 1. What the experiment answered

- **Can an agent reach the brief's bar by moving blocks and routing at the class widths?** Yes for everything the
  brief measures: 0 open links but J1's no-connect pair, 0 new segments below class, 0 thin links beyond a pad field,
  0 class-clearance items, 0 DRC errors of new copper (111 errors, all Sofar's copied features with reasons), 0
  dangling copper, pairs 9.46 / 8.80 / 17.98 / 18.62 mm against 9.5 / 9.5 / 21.3 / 21.3, Kelvin by track, blocks
  rigid and complete. QE round 2: APPROVED WITH NITS.
- **Did it produce a board a person would sign?** Not yet. Two things a reviewer sees at once are not in the brief's
  bar: the 45° runs are 0.1 mm-grid staircases (25–40 segments per pair leg), and two SPI nets (ADIN_MISO, ~{ADIN_CS})
  detour 25 mm down the west edge past the inserts instead of running straight under U1 to J1's SPI pins. Both are
  router behaviour, not placement, and both are fixable (§4).
- **Nothing moved between the start and the end of session 2.** 138 footprints in the same positions; all change
  is copper. The before/after page shows the measured items getting better and the SPI nets getting longer.

## 2. What cost the most time, and why

1. **A pair emitter that was never checked on the board.** Session 1's `commit_pair` passed its blank-board unit
   test and shipped two P–N shorts at the transformer pads, hidden by an exclusion pattern that matched any item
   touching a T pad. Lesson: every emitter's output is checked on the real board with pcbnew shapes before it is kept
   (`pair_check`), the exclusion classifier must name the specific items it excuses, and a unit test on a blank board
   proves geometry, not placement. Session 2's real-board test found five further defects the blank board could not.
2. **Figures that interact.** A straight via pair followed by a swap, with a turn between them, put vias 0.48 mm apart
   although each figure alone was clean, and a spacing counter in the A* state let the path loop back over its own
   vias. Lesson: a layer change is a macro with straight runs on both sides, the first steps after it continue
   straight, and only one mid-route figure (the swap) is placed by the search; the layer changes at the ends are
   fixed geometry (vias straight out of the pins, a via pair beside the pads' approach), as Sofar's mote has them.
3. **Conservative cell maps.** The 0.1 mm grid carries a 0.07 mm margin and assumes a 0.3 mm drill; it rejected the
   pins' vias and stubs that clear by 0.2 mm. Lesson: fixed geometry is checked exactly (`seg_free_exact`,
   `hole_free_exact`, `via_free_exact` with the class's real sizes); the maps are for the search, not the verdict.
4. **The pocket's exits.** U1 sits in a 10 × 12.6 mm pocket between the insert keep-outs; its south exit (x −4 … 3,
   y 37.4 … 38.8) must carry the port-2 pair, U2/U3's fan-out vias and four Internal 2 corridors. Each fix there moved
   something else (three routing rebuilds went to this one spot), and the SPI finally left by the west edge. Lesson:
   reserve corridors before routing (the SPI lane under U1 to J1, the fan-out vias) instead of letting the shortest
   path win net by net; and give the pocket room (Nick's decision, §3).
5. **Stale snapshots.** Pours and patches are created in the M3 step; a `START=m4` rerun restored the old snapshot and
   a routing rebuild was spent on a pour that was not there. Lesson is written into `build_all.sh`'s comment and
   HANDOFF: anything in `make_planes` needs `START=m2`.
6. **Autonomous iteration without pictures.** Nick could not tell from the log whether the board was getting better
   or worse. Lesson: render the regions after every rebuild (`tools/review_views.py`, `tools/before_after.py`) and
   put the mote's copper beside ours; the numbers alone do not show a 25 mm detour.

## 3. Nick's decisions at the wind-down (2026-10-08)

- **Board 3 mm wider and 3 mm taller** (49 × 68). The brief's growth allowance (2 mm south) is superseded; the frame,
  `geom.OUTLINE`, the fixed positions and the keep-outs move with it in 2.b.
- **Inserts 1–2 mm closer to the west wall.** Measured on the mote: the corner inserts' centres sit 3.5 mm from the
  edge (MP1/MP3; MP2/MP4 7.0 mm), so their Ø7.4 ring copper reaches the outline there. Ours sit 5.69 mm from the edge
  (copper to edge 2.0 mm). With the brief's 0.5 mm copper-to-edge rule the centre can come to 4.19 mm from the edge
  (a 1.5 mm shift); 2 mm needs the edge clearance relaxed to 0 at the rings, as the mote. 2.b decides after fetching
  JLCPCB's figure. Sofar's keep-out radius (4.8 mm, no other-net copper) is unchanged by the shift.
- **SPI is critical** (it is how the Pi talks to the ADIN). The SPI nets go straight from U1 to J1's SPI pins on a
  reserved Internal 2 lane, routed first; no edge detour. Length matching is **not** required (§5).
- **JLCPCB's design rules before any further edit.** M3's DFM fetch moves to the front of 2.b: every limit from
  JLCPCB's published pages, cited in `DFM.md`, encoded in the design rules, DRC re-run, before the board changes.
- **Routing style:** straight lines and 45° angles, collinear steps merged, no back-and-forth; the staircases are
  removed in the emitter, not by hand.
- **"The ADIN should be in the middle of the board"** (Nick, at the wind-down). Experiment 01 put U1 in the west pocket
  only because its 9.12 mm courtyard did not fit the 8.0 mm band between the two inductor envelopes (01 BRIEF §2 /
  DEV_LOG 2026-10-07). With 3 mm more height spent on that band it becomes ≈ 11 mm, U1 fits between the ports as on
  the mote (each transformer beside its own inductor, port 1 south, port 2 north), the pairs get shorter and
  symmetric, the SPI runs straight east to J1 with no pocket exit, and the pocket's crowding (§2.4) disappears. The
  cost: the ADIN block's bottom-side parts (U2, U3, Y1, the decoupling) go under the band, where the T1/T2 clusters and
  B18 sit today, and the 1V8 / 3V3 / PWR corridors re-plan. Nick's reasons: central to everything it talks to (both
  inductors / transformers, the header), and **away from the board edge, where strain and deflection concentrate**:
  a 48-pin 0.5 mm-pitch QFN is the part on this board most sensitive to flex, and the west pocket puts it between the
  housing hole, the inserts and the free edge. 2.b evaluates the centre first, as M0 did, with a trial placement
  through M2 on a scratch copy (centre vs pocket, numbers side by side); the centre is the preferred answer unless
  the trial shows it cannot meet the bar.

- **Cut jumpers visible and reachable.** JP1 (5 V to the Pi) and JP2 (the LED supply) go on the top side near a
  board edge with no tall part beside them, so a user can see them and cut them. Today JP1 is on top at the strip's
  north end between L6 (an inductor) and J1; JP2 is on the bottom under the LEDs. 2.b places both at an edge on top
  and says what their nets' routing costs.

- **A power LED at the payload connector** (Nick): an LED + resistor on VBUS_OUT beside J5 so a user sees when the
  payload is powered. This is a circuit change (BRIEF rule 4: no schematic edit in the experiment), so it goes to the
  live project as a schematic task (capture in docs/TRACKER.md from a main-based session; it also needs a sofar_brief
  row). 2.b only reserves room for an 0603 LED + resistor on the top side next to J5, visible from the payload edge,
  and notes it in REPORT as an open circuit item.

## 4. What 2.b has to do, in order

1. Fetch and encode JLCPCB's limits (BRIEF §6 list) into `.kicad_pro` / `.kicad_dru`; `DFM.md` with URL + date per
   row; DRC on the current board to see what the real rules say about it before anything moves.
2. Grow the board to 49 × 68 and move the inserts west (decide the shift from the fetched edge rule); re-derive the
   fixed items and keep-outs (`geom.py`, `m1_fixed.py`, `check_fixed.py`) and prove them. Write an OPTIONS addendum:
   U1 in the centre of the widened band vs U1 in the pocket, each tried through M2 on a scratch copy, with the pair
   lengths, the SPI lengths, the pocket/band occupancy and the courtyard result side by side; recommend; Nick decides.
3. Router: emit 45° runs as single segments (merge collinear steps in `Grid.polyline` and in `commit_pair`), keep the
   pair lengths under the limits (BM1_DATA_P has 0.04 mm of margin today; the wider pocket should give more).
4. Reserve corridors before routing: an Internal 2 SPI lane under U1 to J1 pins 19/21/23 (+ ~{CS} 24), the fan-out
   vias, then the pairs, then the rest; the SPI must not use the west edge.
5. Rebuild from M1 (the placement changes), full checks, renders, the review pages, QE round 3, Nick's review.

## 5. SPI length matching (Nick's question)

Not needed. The ADIN2111's SPI clock is in the tens of MHz (the exact maximum is the datasheet's figure, to be
quoted in 2.b, not typed here); even at 25 MHz a 25 mm difference between two traces is about 0.15 ns of skew against
a 40 ns clock period, under 1 % of a bit. What matters for SPI on this board: keep SCK, MOSI, MISO and ~{CS} short
and on one reference plane (the GND plane In2 is next to Internal 1; Internal 2 sits between the GND and PWR planes,
both fine), keep them 0.35 mm from the bus nets and away from the 10BASE-T1L pairs (they share no layer with the pairs
when SPI is on Internal 2), and do not run them along a board edge, which is what the detour did. Equal length is a
requirement for the Ethernet pairs' P and N legs, not for SPI; the pairs are within 0.7 mm of each other here, which
at 7.5 MBaud is irrelevant too, but the brief holds them to the mote's lengths and they meet it.

## 6. Things to keep (they work)

`tools/test_pair.py` (18 cases + the real board), `pair_check`, the fan-out-first step, the protected mote pad-to-pad
items, the hand-via mechanism with its proof, the exact checks for fixed geometry, the DRC exclusion table with one
reason per item, the review and before/after page generators, the pipeline's snapshots and restarts.
