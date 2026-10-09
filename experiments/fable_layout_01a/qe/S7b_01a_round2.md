# QE review — PR #31 (S7, experiment 1.a, do not merge) — Round 2 — 2026-10-08

*Received from the standing S7 QE session (session message to "Layout experiment 1.a session 2"). Saved here because
this branch writes only `experiments/fable_layout_01a/` (BRIEF rule 1). N1 and N2 are folded into REPORT.md §1 / §6 in
the commit that adds this file; N3 is left for M3.*

**Verdict:** APPROVED WITH NITS
**Reviewed:** 206607d (board md5 de2e14fb… confirmed; PR base now experiment/fable-layout-01), from a `git archive` copy in my scratchpad. Fresh kicad-cli DRC with every error classified by its items (not by drcexclude), your check_fixed/blockcheck/check_rules/test_pair re-run in the copy, and my own pcbnew checks.

## Claims checked
| Claim | Result | Evidence |
|---|---|---|
| Scope | ✓ | `git diff --name-only e2eb9dc...206607d`: experiments/fable_layout_01a/ only; board/ schematic + libraries identical to a5f812c (cmp) |
| F1: no pair shorts; T-pad patterns need the no-net pad | ✓ | Fresh DRC: 111 errors = 76 insert contact + 22 involving T1/T2's `[<no net>]` pads (my own classification) + 12 courtyards (the same 10 intra-block pairs + MTG1/H1, MTG3/H3) + 1 bus-rule item (BM1_N track vs GND via (7.39, 45.30), the declared Sofar stub). shorting_items 34 / mask 18, the same as the mote's transformer/insert set; no DATA net in any error. drcexclude T patterns require `Pad [<no net>] of T[12]` |
| F2: ~{ADIN_INT} hand via; mote pad-to-pad paths protected | ✓ | Via (−6.75, 30.25) ~{ADIN_INT}, 0.45/0.2, 0.525 mm from the west edge, nearest other-net copper 0.207 (ADIN_VDDIO via). My per-block check (pad groups track-connected on the mote) now finds U1.39–R1.1 connected; the only remaining differences are 3 GND groups (N1) |
| DRC 111 / 0 unjustified / 1 unconnected / 4 parity / 254 warnings, 0 dangling | ✓ | Fresh JSON; unconnected = J1 1/17; warnings silk/text/padstack/lib only; exclusion table counts match type by type |
| check_fixed 0 failures, no allowance | ✓ | Re-run; `ALLOWANCES = {}` |
| blockcheck 0 missing / 127 trimmed | ✓ | Fresh run byte-identical to out/m4/blockcheck.md |
| check_rules 0 below class / 0 thin links / 0 clearance items; pairs 9.46 / 8.80 / 17.98 / 18.62 (2 vias, Top + In1); Kelvin yes/yes | ✓ | Re-run identical to out/m4/rules.md; my track-only R8↔U4 search: 6.821 / 6.445 mm, 9 items each, as the mote |
| test_pair.py | ✓ | Ran in the copy (no snapshot, so the stripped-board fallback): 18 blank-board cases OK; real board OK, pairs 9.46 / 8.80 / 17.98 / 18.62, min clearance to other nets 0.175 mm, "ALL OK" (72 s); board md5 unchanged afterwards |
| Blocks rigid | ✓ | 87 block parts vs the mote: 0 side mismatches, 0 rotation anomalies |
| Pair geometry | ✓ looked | Rendered port1/port2_pair_top_board: coupled pairs, straight approaches into the T pads, swap/via figures clear of the opposite pads |

## Findings
| # | Severity | Finding | Suggested fix |
|---|---|---|---|
| N1 | NIT | REPORT §1 "0 of the mote's pad-to-pad paths cut" holds for copied items only. Three of Sofar's GND links are not copied because the block regions leave them out: B33 and B5V C29.2–C30.2 (the mote's bottom lead-out at (138.95, 110.83) + via (138.88, 110.43); B33 rect 1 has no B.Cu) and DAMP1 C21.2 (via at mote (156.55, 120.75), just outside the region's x 156.5). On the board they are joined by the GND pours instead, which is electrically fine | Add "(three GND pad links are made by the pours instead of Sofar's tracks: …)" |
| N2 | NIT | BM1_DATA_P is 9.46 mm against a 9.5 mm limit, a 0.04 mm margin. §8 says a rebuild isn't byte-identical, so a rerun could land over | Note the margin in §6 or §7, or have the pair router keep a small margin |
| N3 | NIT | The pairs' 45° runs are 0.1 mm-grid staircases (port 1: 25 segments per leg, port 2: 40) | Optional: merge collinear steps before M3 |

## Could not verify
- A full rebuild this round.
- The bottom GND island near (37.1, 13.9) under a KiCad refill (declared §6 #1).

## Repo untouched
My worktree: git status clean before and after. Every run used a git-archive copy in my scratchpad.
