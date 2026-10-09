# QE review — PR #31 (S7, experiment 1.a, do not merge) — Round 4 — 2026-10-08

*Received from the standing S7 QE session (session message to "Fable layout 01b [e3972d]"). Saved here because this branch
writes only `experiments/fable_layout_01a/` (BRIEF rule 1). N1–N3 are fixed in the commit after this file; N4 is for Nick
(DESIGN D31, outside this folder).*

**Verdict:** APPROVED WITH NITS
**Reviewed:** b34293d (board md5 3a4dbf32… confirmed), from a `git archive` copy in my scratchpad, plus a from-m0 rebuild on a second copy (`VARIANT=pocket HEIGHTS=heights.json tools/build_all.sh m4`, 5 m 0 s). Fresh kicad-cli DRC classified by items; your check_fixed/blockcheck/check_rules re-run; my via-in-pad and small-pad scans.

## Claims checked
| Claim | Result | Evidence |
|---|---|---|
| Scope; schematic copy | ✓ | `git diff --name-only e2eb9dc...b34293d`: experiments/fable_layout_01a/ only; board/ sheets and libraries identical to a5f812c |
| Nick's A6 decisions recorded | ✓ | OPTIONS A6 (20 W SRF1260 courtyard + 2 mm as the keep-out; U1 group 3 mm east), BRIEF §3 marked superseded (see N4) |
| DRC 109 errors, all Sofar's; 1 unconnected; 4 parity | ✓ | Fresh JSON: 76 insert contact + 22 T1/T2 no-net pads + 10 intra-block courtyards + the BM1_N stub vs Sofar's GND via (0.2502 mm, reason now says 0.25) |
| DRC warnings 68 | ✗ (70) | N1 |
| F1: no new via in a solder pad; row 30 measured | ✓ | My scan: 44 vias-in-SMD-pad are Sofar's copied ones, 18 are new. All 18 are in test pads (TP7, TP8 ×2, TP13, TP20 ×2, TP22, TP24, TP36 ×2), the U11 exposed pad (U11.11), or large pads (L1.1/.3/.4, L2.1/.2/.4, C23.1). None in U11's signal pads, 0402s, LEDs, JP2, J5 or R4x any more. Row 30's figures (Sofar's 16, test pads 10, thermal 8, new in solder pads 0) agree with that classification. The row now fails on any NEW (dfm.py) |
| F2: row 29 lists every pad under 0.25 | ✓ | U11 0.240 (KiCad stock, this design's part), U2/U3 0.235, U6 0.230, as my scan |
| check_fixed 0 failures, no allowance; blockcheck 0 missing / 128 trimmed | ✓ | Re-run; fresh blockcheck = committed |
| check_rules: 0 below class / 0 thin / 0 clearance; 6 small-pad stubs; pairs 9.39 / 8.77 / 20.19 / 20.87; Kelvin yes/yes | ✓ | Re-run identical to out/m4/rules.md; stubs: VBUS at C20.1, C49.1, R15.2, R16.2 0.4 mm, R41.1 0.9 mm, U11.1 0.3 mm |
| Rebuild reproduces | ✓ | From-m0 rebuild: DRC 109 / 70 / 1 / 4, same as the committed file; pairs and rules identical; check_fixed 0 failures |

## Findings
| # | Severity | Finding | Suggested fix |
|---|---|---|---|
| N1 | NIT | REPORT §1/§5/§7 and DFM.md say **68 warnings**. kicad-cli on the committed file, and on the rebuilt one, gives **70**: the 2 extra are `nonmirrored_text_on_back_layer` for U5's and U10's `*` texts at (31.57, 33.63) / (31.57, 20.43). The pipeline's own out/m4/drc_summary.txt also says 68, so that summary runs on a board state that differs from the saved file (a later step changes it, or the summary runs before the final save). Round 3's file did list "2 nonmirrored" | Run drc_summary.py (and dfm.py check) last, on the saved file; quote 70, or fix the two texts |
| N2 | NIT | Row 30's "thermal pads" class (SMD pad > 4 mm²) also covers the **solder pads of L1/L2 (6 new vias) and C23.1**, which aren't thermal pads. Vias in large pads wick less, but they are new router/stitch vias, not Sofar's | Call them "large power pads", and consider JLC's via plugging/tenting for them, or move them off the pads |
| N3 | NIT | The "small decoupling stub" at **U11.1** is U11's IN pin (TPS26621 pin 1 = IN, VBUS), so it carries the payload current (≤ ≈ 0.73 A, U11's limit). 0.3 mm long, so harmless, but it isn't a decoupling stub | Say so in REPORT §9 #3b |
| N4 | NIT (for Nick) | A6 #1 replaces the 50 W MSD1514 envelope with the 20 W part's courtyard in this experiment. DESIGN D31 still sets the 50 W envelope as the proposed target for the real layout | If the 20 W keep-out should carry over, D31 needs Nick's decision (outside this experiment's folder) |

## Could not verify
- The OPTIONS A3 trials (centre vs pocket): read, not re-run.
- The review and before/after pages: not opened.

## Repo untouched
My worktree: git status clean before and after. Your worktree untouched; every run used git-archive copies in my scratchpad.
