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
