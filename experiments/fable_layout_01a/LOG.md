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
