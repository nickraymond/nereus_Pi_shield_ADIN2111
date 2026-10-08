# QE review — PR #30 (S7.b) — Round 4 — 2026-10-08

*Received from the S7 QE session; saved verbatim beside rounds 1–3.*

**Verdict:** APPROVED WITH NITS (the experiment is reviewable by Nick; never merge)
**Reviewed:** 835f1a8 + 60e14d6 + 554d934 (board md5 e6938b5… confirmed), from a `git archive` copy in my scratchpad. Fresh kicad-cli DRC, a bus-vs-bus probe copy (scratch only), my own pcbnew checks, and your blockcheck/check_fixed/check_rules re-run on the copy.

## Claims checked
| Claim | Result | Evidence |
|---|---|---|
| Scope | ✓ | `git diff --name-only a5f812c...554d934`: nothing outside experiments/fable_layout_01/ |
| R3-F1 REPORT restored | ✓ | `grep -n "^## "`: §1–§10 once each, in order (§6 at line 153); deviation rows #1–#17 all present; the §5 exclusion table (header through the "kicad-cli DRC: 111 errors…" line) is identical to out/m5/drc_exclusions.md (diff empty); §9 #3 and §10 Q1/Q2 again point at existing #2/#3 |
| R3-F2 new bus copper keeps 0.35 from the opposite leg | ✓ | Probe rule `A.NetClass=='bus' && B.NetClass=='bus'` at 0.35 → 14 items (was 20). I traced each through the block transforms: all are Sofar's P1T/P2T geometry (T1/T2 pads 6↔7 at 0.24, P1T via pair at 0.15, P1T/P2T tracks vs the pads and vias). The two that weren't exact matches (BM1_P Internal 2 (11.955, 27.576)→(12.025, 27.506); BM2_N Top (18.501→18.016, 30.976)) are sub-segments of Sofar's own tracks, shortened by dangling.py. No new bus copper is under 0.35 from the other leg. router.py has the busleg class (0.2 / 0.35 / 0.45 / 0.2) |
| DRC 111 / 258 warnings / 0 copper-defect / 1 unconnected / 4 parity | ✓ | Fresh JSON identical by type to round 3. The only non-Sofar error is the declared 1V8 Internal 2 track (12.40, 43.20) ↔ BM1_P leg via (11.94, 43.88), actual 0.225 mm under the bus rule; unconnected = J1 pins 1/17 |
| Kelvin both yes | ✓ | My track-only path search: VBUS 6.821 mm / P_IN 6.445 mm, 9 items each, identical to the mote; rules.md Kelvin table: yes / yes |
| blockcheck 0 missing / 126 trimmed / 414 extra; 242/242, 641/744, 4/4, 153/176, 6/6 | ✓ | Fresh run byte-identical to out/m3/blockcheck.md; per-block columns sum to 126 trimmed and 414 extra |
| check_fixed 0 failures | ✓ | Re-run, inserts' copper pull-back included |
| rules.md: 1 class-clearance item (VBUS_OUT vs ~{PAYLOAD_FAULT} at U11 pad 9); pairs 9.4 / 7.9 / 21.3 / 23.4 | ✓ | Re-run identical; no busleg fallback note in routing.json; stitch 69 |

## Findings
| # | Severity | Finding | Suggested fix |
|---|---|---|---|
| R4-N1 | NIT | REPORT §1, §5 row "errors" and §6 #16 describe the 1V8 item as "at the Default 0.15 mm" or "0.15 mm on Internal 2". The measured gap is **0.225 mm** (DRC: "actual 0.2250 mm"); 0.15 is the rule it was routed under | "0.225 mm (routed under the Default 0.15 mm rule)" |
| R4-N2 | NIT | §1 still reads "copper items 930.;" (stray period, R2-N1) | Tidy |

## Could not verify
- A fresh full rebuild this round (round 2's showed DRC-equivalence; §8 states the method).

## For Nick (carried from earlier rounds, all declared in REPORT)
BM2_DATA_N +2.1 mm over the mote; the 1V8 lane past the BM1_P leg via (one DRC error with a reason); bottom-side parts under the inductor envelopes (#2); U1 at 1.79 mm from the L1 envelope (#3); 10 narrow fallback segments and 13 thin links; DRC exclusions to apply by hand in KiCad (kicad-cli can't store them).

## Repo untouched
My worktree: git status clean before and after. Your worktree untouched. All runs, including the probe, used copies in my scratchpad.
