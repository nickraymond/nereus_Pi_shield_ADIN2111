# HANDOFF — layout experiment 1.a, for the session that continues it

*Updated 2026-10-08 by session 2 (M2 brought to its bar; QE round 2 requested from the standing S7 QE session, which
sends its report to the design session named in the request). Start with CLAUDE.md, BRIEF.md, OPTIONS.md, REPORT.md and
LOG.md "M2, session 2"; this file is only the practical part.*

## State

- Branch `experiment/fable-layout-01a`, PR #31 (draft, never merge), base `experiment/fable-layout-01`. Board md5
  **de2e14fbc50999fffc3058edefb7c374**.
- M2 at its bar (REPORT.md §5–§8): DRC 111 errors all Sofar's with reasons, 1 unconnected (J1's no-connect pair), 0
  dangling, rules clean, pairs 9.46 / 8.80 / 17.98 / 18.62 mm. Declared: the bottom GND island near (37.1, 13.9), Q7 as
  a table, M3 not started.
- Nick (2026-10-08): after QE approval, a design review with mote-vs-board images per fixed area, then his own review
  before M3 (`tools/review_views.py` → `out/review/`).

## How to run

- Full rebuild `HEIGHTS=heights.json tools/build_all.sh m4` (≈ 9 min). `START=m4 …` reruns the routing from
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

## Next

1. QE round 2 verdict → fix / resend; then the design review for Nick (region views in `out/review/`, mote beside ours).
2. M3 per BRIEF §6 (DFM: fetch JLCPCB's limits, cite them in `DFM.md`, encode in the design rules, silk clean-up, the
   stackup). 3. The GND island (REPORT §6 #1). 4. Q7.
