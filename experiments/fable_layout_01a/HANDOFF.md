# HANDOFF — layout experiment 1.a, for the session that continues it

*Updated 2026-10-08 by session 2.b (the 49 × 68 board, M3 done, QE round 4 APPROVED WITH NITS from the standing S7 QE session, which
sends its report to the design session named in the request). Start with CLAUDE.md, BRIEF.md, OPTIONS.md, REPORT.md and
LOG.md "M2, session 2"; this file is only the practical part.*

## State

- Branch `experiment/fable-layout-01a`, PR #31 (draft, never merge), base `experiment/fable-layout-01`. Board md5
  **23e5e8f939e6bf5e0c6b609e6c7ee14d** (session 2.b, 49 × 68, `VARIANT=pocket`, the 20 W inductor keep-out, U1 at x −1.7).
- M2 and M3 at their bar (REPORT.md §1, §6): DRC 109 errors all Sofar's with reasons, 1 unconnected (J1's no-connect pair), 68
  warnings, rules 0 / 0 / 0, pairs 9.39 / 8.77 / 20.19 / 20.87, DFM 30 / 31 (the small pads of U6 / U2 / U3 / U11 declared), 0 new
  vias in solder pads. Declared: REPORT §9. QE round 3 CHANGES REQUESTED (fixed), round 4 APPROVED WITH NITS (fixed).
- Session 2.b closed with the OPTIONS addendum (A1–A6), DFM.md, the review pages (`out/review/`, `out/before_after/`; published
  as the artifact https://claude.ai/artifact/8RuEpJyDHQBx8BE6XTskSG, `tools/publish_pages.py` packages them), QE round 4
  APPROVED WITH NITS (fixed) and PR #31 re-targeted at main for Nick's review and merge.
- Next for the centre placement (`VARIANT=centre`, kept in `m2_place.py`): a pair emitter that enters the transformer pads from
  the body side through a staggered via pair (REPORT §10).

## How to run

- Full rebuild `HEIGHTS=heights.json tools/build_all.sh m4` (≈ 7 min; `VARIANT=pocket` is the default, `centre` the other
  placement, `J5WEST=1` Nick's J5-west / L1-south option). Trials on a scratch copy: `SCRATCH=<dir> tools/trial.sh <name> <variant> m2|m4`. `START=m4 …` reruns the routing from
  `out/m3/snapshot.kicad_pcb` (git-ignored: the first run on a fresh checkout must be from m0). `START=m2` restarts from
  `out/m1/snapshot.kicad_pcb`. **Never run a milestone script on the board as left by a later step.** Anything in
  `m4_route.make_planes` (pours, patches) is created in the M3 step: a change there needs `START=m2`, not `START=m4`
  (session 2 lost a rebuild to that).
- Checks: `tools/check_fixed.py --heights heights.json`, `tools/blockcheck.py out/m4/blockcheck.md`,
  `tools/check_rules.py out/m4/rules.md`, `tools/drc_summary.py m4`, `tools/drcexclude.py` (writes
  `out/m5/drc_exclusions.md`), `tools/test_pair.py` (18 blank-board cases + the real-board case on the M3 snapshot, ≈ 90 s;
  `--quick` skips the real board). Renders: `kicad-cli pcb render --side top|bottom`, `tools/render_layers.py`,
  `tools/review_views.py out/review`.
- Routing ≈ 5.5 min; the grid builds in 17 s. `out/m4/routing.json` has "failed", "notes" (every pair candidate with its
  board-check result), "stitch" (incl. the fan-out vias).

## Pitfalls met (cost real time)

- `geom.load()` / `geom.save()` bind their default path at import; use `pcbnew.LoadBoard(path)` in a harness.
- A second `pcbnew.LoadBoard` in one process returns dead SWIG proxies; one board per process.
- `SHAPE::GetClearance` returns 0 against an arc shape in 9.0.6 (`Collide` works; `test_pair.py` uses a polygon).
- The cell maps carry a 0.07 mm margin and a 0.3 mm assumed drill: fixed geometry (the pairs' pin stubs and vias) is
  checked exactly (`seg_free_exact`, `hole_free_exact`, `via_free_exact` with the class's real sizes) or it is rejected
  although it clears by 0.2 mm.
- The pair A*: the only mid-route figure that is safe is the swap; a mid-route straight via pair is still allowed but
  tends to fail the board check (the candidates are all checked and the failed ones removed, so it cannot ship a
  short). Keep the ends on fixed via pairs (pins / pads' approach).
- The pocket's south exit (x −4 … 3, y 37.4 … 38.8) is the tightest place on the board: the port-2 pair (Top / In1),
  U2's fan-out vias and the In3 corridors for 3V3 / 1V8 / ADIN_PWR / ~{CS} all cross it. Anything new there moves the
  others.
- kicad-cli DRC's JSON gives item positions, not marker positions (Q7).

## Next (session 2.b, in this order: LESSONS §4)

1. JLCPCB limits fetched, cited in `DFM.md`, encoded in the design rules; DRC on the current board.
2. Board 49 × 68, inserts west; fixed items and keep-outs re-derived and proven.
3. Router: single-segment 45° runs; pair margins. 4. Reserved SPI lane under U1 to J1, fan-out, pairs, the rest.
5. Rebuild from M1, checks, renders, review + before/after pages, REPORT with the DFM table, QE round 3.
