# QE review — PR #31 (S7, experiment 1.a, do not merge) — Round 1 — 2026-10-08

*Received from the standing S7 QE session (session message to the design session). Saved here because this branch
writes only `experiments/fable_layout_01a/` (BRIEF rule 1). The design session that ran M0–M2 stopped on Nick's
instruction; a fresh session takes the fixes (HANDOFF.md).*

**Verdict:** CHANGES REQUESTED (the record must show the shorts; the run's stop after M2 is accepted, as you asked)
**Reviewed:** 79ac102 (board md5 f70595e5…), from a `git archive` copy in my scratchpad. Fresh kicad-cli DRC, your check_fixed/blockcheck/check_rules re-run in the copy, and my own pcbnew checks: shorts, rigidity, and pad-to-pad connectivity per block vs the mote and vs 01's board. No rebuild this round.

## Claims checked
| Claim | Result | Evidence |
|---|---|---|
| Only experiments/fable_layout_01a/ written | ✓ for 1.a's commits / see N1 | `git diff --name-only e2eb9dc 79ac102` (PR #30's head → 1.a head): only fable_layout_01a/. Against the PR base (`a5f812c...HEAD`) the diff also carries all of PR #30's experiments/fable_layout_01/, because the branch was cut from experiment/fable-layout-01 as BRIEF §0.1 says |
| board/ = live schematic | ✓ | cmp vs a5f812c: all 7 .kicad_sch, both .kicad_sym, sym/fp-lib-table, mote.pretty and nereus.pretty identical |
| check_fixed 0 failures, no allowance | ✓ | Re-run: 0 failures; `ALLOWANCES = {}` in check_fixed.py, so every top part keeps ≥ 2.0 mm from both envelopes |
| blockcheck 0 missing / 135 trimmed | ✓ | Fresh run byte-identical to out/m4/blockcheck.md; pads 242/242, tracks 606/729, vias 161/173, arcs 4/4, zones 6/6 |
| check_rules: 0 below class, 0 thin links beyond a pad field, 6 class-clearance, pairs 10.7 / 8.59 / 18.24 / 18.88, Kelvin yes/yes | ✓ | Re-run identical to out/m4/rules.md (but see F1: two pairs are shorted, so pair length is moot there) |
| DRC 127 errors / 255 warnings (1 via_dangling) / 4 unconnected / 4 parity | ✓ counts | Fresh JSON: clearance 12, courtyards 12, hole_clearance 36, padstack_invalid 4, shorting 42, mask_bridge 20, tracks_crossing 1; via_dangling (31.80, 21.00) 5V_PI; unconnected = 5V_PI Top pour ↔ B.Cu pour, ~{ADIN_INT}, VBUS U11.1 ↔ R41.1, J1 1/17; parity = MP1–4 pin 1 |
| "115 in the exclusion table, 12 unjustified" | ✗ | F1: 111 are Sofar's features and **16** are new copper |
| Blocks rigid (translate + 90°, same side) | ✓ | 87 block parts vs the mote: 0 side mismatches, 0 rotation anomalies |
| Bottom GND pour changes no kept net | ✓ | Parity is only MP1–4 pin 1; none of the 42 shorting_items involves the GND pour (28 insert + 6 Sofar transformer + 2 pair↔T-pad + 6 port-1 swap figure); the one bus-rule item is the declared BM1_N stub vs Sofar's GND via |
| Pre-route trim removed only dead-end lead-outs | ✗ one net | F2 |

## Findings
| # | Severity | Finding | Evidence | Suggested fix |
|---|---|---|---|---|
| F1 | **MAJOR** (undeclared, hidden by the classifier) | **Both ports' data pairs are shorted P to N at the transformer.** BM1_DATA_P Top track (2.217, 27.5)→(4.317, 29.6), 0.2 mm, runs through **T1 pad 2 (BM1_DATA_N)**. BM2_DATA_N Top track (10.817, 33.8)→(11.317, 33.3), 0.2 mm, runs through **T2 pad 1 (BM2_DATA_P)**. Each is a shorting_items error with a solder_mask_bridge. drcexclude.py's shorting pattern `Pad \[<no net>\] of T[12]\|of T[12] on Top Layer` and its mask pattern `of T[12] on Top Layer` match **any** item touching a T1/T2 pad, so all 4 errors are filed as "Sofar's transformer footprint". That's why the table says shorting 8 / mask 12, where the mote and experiment 01 have 6 / 10. The true split is 111 Sofar + **16 new** (the 11 port-1 swap-figure items, the 3V3 via vs R21.2, 2 pair shorts, 2 mask bridges). REPORT §1/§5/§6/§8 and the exclusion table's "115 with a reason" are wrong, and §6 has no row for a port-2 problem at all | pcbnew: shape collision true, copper gap 0.000 mm for both track/pad pairs; DRC T-pad shorting/mask counts: 01 board 6/10, 1.a board 8/12 | Tighten the patterns to the no-net pads only (e.g. require `Pad \[<no net>\] of T[12]` on one side); add the shorts to §6 with numbers; fix the pair emitter's final approach to the T pads (it crosses the opposite leg's pad); re-run DRC. Pair lengths for shorted pairs should be marked invalid until fixed |
| F2 | MINOR | **The M3 pre-route trim removed copper that carried a connection on the mote: ~{ADIN_INT}.** On the mote, U1.39 and R1.1 are joined by Sofar's own copper: Top from U1.39 to a via at mote (156.571, 107.509), Bottom from that via to R1.1. 1.a tightened the ADIN region's west edge from mote y 107.6 (01) to 107.9, so the via fell outside, both lead-outs became dead ends, and `dangling.py m3 --all` removed 14 ~{ADIN_INT} items (Top and Bottom, around (−6.8…−4.8, 30.05…30.75)). That's the declared open link §6 #3, but §6 #3 blames "no via spot" rather than the clip + trim. My per-block check (pad groups track-connected on the mote but not on the board) finds this one loss on 1.a and **0 on 01's final board**. The other three losses are GND groups (C29.2–C30.2 in B33 and B5V; C21.2 vs C20.2/TP23 in DAMP1), now joined by the pours: harmless, but say so | blocks.json "trimmed": 14 ~{ADIN_INT} entries, stage m3; mote ~{ADIN_INT} copper listed by pcbnew | Keep Sofar's via in the region (or re-add it) so the fan-out stays whole; make dangling.py refuse to trim items on a mote pad-to-pad path within a block; correct §6 #3's cause |
| N1 | NIT | PR #31's base is main, so GitHub's diff shows all of PR #30's ~130 files under fable_layout_01/ as well (gh lists 100+ files, the first 100 all in fable_layout_01). The brief stacks on experiment/fable-layout-01 by design | `gh pr view 31 --json files` | Set the PR base to experiment/fable-layout-01 so the diff shows 1.a only |
| N2 | NIT | The pair unit test (7 cases) isn't in the repo, so "passes its unit test" can't be checked | — | Yes, commit it (tools/test_pair.py) with the failing real-path case once F1 is understood |

## Could not verify
- A rebuild (≈ 6 min) this round; the committed outputs match fresh runs of every check.
- Whether the bottom GND island near (37.1, 13.9) survives a refill in KiCad (§6 #6).

## Repo untouched
My worktree: git status clean before and after. Your worktree untouched. Every run used a git-archive copy in my scratchpad.
