# HANDOFF — layout experiment 1.a, for the session that continues it

*Written 2026-10-08 by the session that ran M0–M2 (stopped on Nick's instruction after ~2 h; QE round 1 of PR #31 was
requested from the standing S7 QE session, which sends its report to the design session named in the request — a fresh
session should ask Nick to point the QE at it, or read the report Nick relays). Start with CLAUDE.md, BRIEF.md,
OPTIONS.md, REPORT.md §6–§9 and LOG.md M2; this file is only the practical part.*

## State

- Branch `experiment/fable-layout-01a`, PR #31 (draft, never merge), last commit = M2. Board md5 f70595e5438bf4d6df0c6e6ee80deebd.
- M2's shortfall is REPORT.md §6 (3 open links, port-1 pair P 10.7 mm > 9.5, 12 DRC errors of new copper, 6
  class-clearance items, 1 dangling zone via). M3 (DFM) not started; Q7 not attempted.

## How to run

- Full rebuild `HEIGHTS=heights.json tools/build_all.sh m4` (≈ 6 min). `START=m4 …` reruns the routing from
  `out/m3/snapshot.kicad_pcb` (git-ignored: the first run on a fresh checkout must be from m0). `START=m2` restarts from
  `out/m1/snapshot.kicad_pcb`. **Never run a milestone script on the board as left by a later step** — the restarts exist
  because that doubled the copper once.
- Checks: `tools/check_fixed.py --heights heights.json`, `tools/blockcheck.py`, `tools/check_rules.py out/m4/rules.md`,
  `tools/drc_summary.py m4`, `tools/drcexclude.py` (writes `out/m5/drc_exclusions.md`), `tools/test_pair.py` (the pair
  emitter's unit test, 7 cases, all OK at this commit).
- Routing takes ≈ 5 min; the grid builds in 19 s. `out/m4/routing.json` has "failed" with the open links and their
  cluster pads, and "notes".

## Pitfalls met (cost real time)

- `geom.load()` / `geom.save()` bind their default path at import: a scratch harness that overrides `geom.BOARD` after
  importing still loads AND SAVES the live `board/…kicad_pcb`. Use `pcbnew.LoadBoard(path)` / `SaveBoard(path, …)`
  explicitly in any harness.
- A second `pcbnew.LoadBoard` in one process returns dead SWIG proxies (01's finding); one board per process.
- kicad-cli DRC's JSON gives item positions, not marker positions (Q7).
- The router's maps are net-coded; two nets near one cell read BLOCK. The pairs are routed with `Grid(merge=…)` so
  P and N are one net to the grid.

## Next fixes, in order (REPORT §6 / §9)

1. Port-1 pair: dump the real path (out/m4/routing.json "pair port 1" note has the swap cell and side; the path can be
   re-created by running `route_pairs` alone on the M3 snapshot in a harness) into `tools/test_pair.py`, find the case
   the emitter gets wrong (candidates: the entry run after a turn; the straight via pair at (0.23, 27.2) 0.9 mm before the
   swap at (1.1, 27.0) — GAP in `route_pair` counts cells after a macro's exit), fix, rerun `START=m4`.
2. ~{ADIN_INT}: hand via at (−6.75, 30.3) + a 0.2 mm Top track along Sofar's old path from pin 39's escape, before the
   pocket's nets (see the probe in LOG M2).
3. VBUS at U11.1: pre-stitch it (power class via within 1.5 mm) before U11's row signals.
4. 5V_PI: one via inside both the copied Top output pour and the bottom pour (zone_stitch skips islands that already hold
   a via of the net; add "and that via reaches another layer's copper").
5. `via_free_exact`: use the class's real via diameter (it derives one from the map radius; R21 pad 2 vs the 3V3 via).
6. The payload clearance (0.25) for power-class routes in the cross map (`xradii` applies it to signal routes only).
7. M3 per BRIEF §6.
