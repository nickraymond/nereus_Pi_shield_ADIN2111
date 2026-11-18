# N6 shield: hand-over after the first pass (2026-11-17, about 6 PM Pacific)

State: study, mocks and plan are done and pushed on `n6-shield`. **No file in `N6_Shield_ADIN2111/` has changed yet.**
Next: stage 0 of `STAGE0_PLAN.md` (schematic first), approved by Nick in the first-pass session's chat
("Go with the rest of your suggestions").

Read in this order: `BRIEF.md`, `STAGE0_PLAN.md`, `PIN_MAP.md`, the mock P sections at the end of section 3 of
`FIRST_PASS.md`, `mocks/review/ROUTING_PLAN_P.md` and `REVIEW_P.md`, `N6_FACTS.md`. Then the rules on `development`
(`CLAUDE.md`, `docs/TRACKER.md`, `docs/SPEC.md`) and the top of `experiments/pi_zero_fit_01/LOG.md`.

What is settled (Nick's words are quoted in the files named):
- Board: OpenMV N6. Layout: mock P, 42.16 x 62.0 mm; east edge = the N6's edge; south edge 1.4 mm past the N6;
  both headers through-hole, pins soldered to the N6 with 5 mm spacers; three 2.7 mm bare holes; connectors
  top-entry, 3 mm between bodies; coordinates in `scripts/n6_rough_board.py` (mock "P").
- Pin map with INT on P6 and reset on P9; pot and ADC on the N6's 3V3; AUX pads, jumper, fuse, load switch go.
- Straps JP3 / JP4 stay, on the N6-facing side of the west wing; default 0 / 0.

Traps found in this session:
- `n6_rough_board.py` builds MOCKS: it drops all zones, our routing and our small parts, and uses library footprints
  without nets. It is the source of coordinates, not a stage script.
- Keep footprints by object, not by reference (new parts reused H1..H4); Sofar's 17 copper shapes must turn with
  the block; collect "old" drawings before adding new ones.
- Sofar's only T1-to-L1 copper on the bus nets is a 0.2 mm data track: the bus enters at L1's and L2's own pads.
- In zsh, `$d:path` eats the path's first letter: write `"${d}:path"`.
- pdftotext / poppler are not installed here: PDFs cannot be read with the Read tool.

Open, not verified: a real N6 (header left / right sense, row spacing); the header part for a 5 mm gap; Sofar's
ground-slot purpose; ADIN2111 Rev. B; ST's pin limits; the 33 ohm part; heat and potting.

Outside git: `~/NereusData/nereus_Pi_shield_ADIN2111/n6_shield/` (scratch boards `step_rough/mock_*`, renders,
`review_L/`, `review_P/` with plots and scripts, `n6_research_raw.md`, `sources/`).
