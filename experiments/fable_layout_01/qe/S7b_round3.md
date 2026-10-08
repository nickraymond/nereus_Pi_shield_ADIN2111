# QE review — PR #30 (S7.b) — Round 3 — 2026-10-08

*Received from the S7 QE session; saved verbatim beside rounds 1 and 2.*

**Verdict:** CHANGES REQUESTED (report fix only; the board fixes verify)
**Reviewed:** 7582d3c + 57cc4d4 (board md5 df69788… confirmed), from a `git archive` copy in my scratchpad. Fresh kicad-cli DRC, two probe copies with the .kicad_dru edited (scratch only), my own pcbnew checks, and your blockcheck/check_fixed/check_rules re-run on the copy.

## Claims checked
| Claim | Result | Evidence |
|---|---|---|
| Scope | ✓ | `git diff --name-only a5f812c...57cc4d4`: nothing outside experiments/fable_layout_01/ |
| R2-F1 Kelvin restored | ✓ | My track-only search R8 ↔ U4: VBUS 6.821 mm and P_IN 6.445 mm, 9 items each, identical to the mote. Flood from U4.1 reaches only R8.2 (6.59 mm, no via); from U4.2 only R8.1 (6.96 mm, no via), as on the mote. rules.md Kelvin table: both "yes". blockcheck SENSE 65/77 tracks, 12 trimmed, 0 missing |
| R2-F2 bus rule live | ✓ | .kicad_dru: `A.NetClass == 'bus' && B.NetClass != 'bus'` → 0.35. Probe at 0.45: 54 bus-rule violations (39 via↔zone, 15 track↔via), so the rule applies to planes and both item orders. At 0.35 the committed board has exactly 1 (the declared 1V8 item). bus class priority 0 / clearance 0.15; the 4 BM nets assigned |
| DRC 111 / 1 unconnected / 4 parity / 258 warnings / 0 copper-defect warnings | ✓ | Fresh JSON: clearance 7 (6 T1/T2 + 1V8 ↔ BM1_P via (11.94, 43.88) on Internal 2), courtyards 12, hole_clearance 36, padstack_invalid 4, shorting 34, mask_bridge 18; unconnected = J1 pins 1/17; no dangling, hole_to_hole or co-located items |
| blockcheck 0 missing / 130 trimmed / 342 extra | ✓ | Fresh run byte-identical to out/m3/blockcheck.md; totals pads 242/242, tracks 638/744, vias 152/176 |
| check_fixed 0 failures, inserts clear (copper) | ✓ | Re-run: MP1–4 "copper pull-back r 4.8 … clear" |
| rules.md (1 class-clearance item, 10 narrow segments, 13 thin links, pairs 9.4 / 7.9 / 21.3 / 23.4) | ✓ | Re-run identical |

## Findings
| # | Severity | Finding | Evidence | Suggested fix |
|---|---|---|---|---|
| R3-F1 | **MAJOR** (report integrity) | REPORT.md at 57cc4d4 lost the `## 6. Deviations` heading, deviations #1–#9 and the tail of the §5 exclusion table. The headings jump from §5 (line 121) to §7 (line 152). After the "courtyards_overlap \| 2" row, the "courtyards_overlap \| 10" row now carries deviation #10's text. The exclusion rows for hole_clearance 36, padstack_invalid 4, shorting_items 28/6 and solder_mask_bridge 8/10, and the "kicad-cli DRC: 111 errors…" line, are gone. Then rows #11, #14, #12, #13, #15–#17 follow with no header. Missing deviations include #2 (bottom parts under the envelopes) and #3 (U1 0.3 mm allowance), which §9 #3 and §10 Q1/Q2 refer to, plus #4 J5 JST, #5 JP1 bottom, #6 fresh placements, #7 LEDs, #8 BM2_DATA_N over length, #9 pair widths/layers. BRIEF §9 requires "every deviation from the mote and why" | `grep -n "^## " REPORT.md` → 1, 2, 3, 4, 5, 7, 8, 9, 10; lines 135–150. 0903d87's REPORT had "## 6." at line 142. out/m5/drc_exclusions.md itself is intact (all 11 rows + the 111 line) | Restore §5's exclusion table from out/m5/drc_exclusions.md and §6 #1–#10 (with the round-2 wording), then re-check the headings |
| R3-F2 | MINOR | The bus-vs-bus exemption (§4, §6 #17) is justified as "Sofar's P/N legs and T1/T2 pads 6/7 keep Sofar's spacing", but it also exempts **new** bus copper. Of the 20 bus↔bus spacings below 0.35 mm (DRC with a probe rule `A.NetClass=='bus' && B.NetClass=='bus'` at 0.35), about 9 involve new routing: new BM1_N via (7.6, 39.9) 0.273 from TP3's BM1_P pad and 0.339 from the BM1_P feed; new BM2_P Top track (17.0, 30.4) 0.275/0.311 from a new BM2_N via (17.6, 30.7) and 0.29 from T2 pad 7; new BM2_N track (18.016…18.501, 30.976) 0.318 from T2 pad 6; new BM1_P Internal 2 tracks (11.7, 27.9)/(11.955, 27.576) 0.24–0.33 from Sofar's BM1_N leg via (11.8, 26.9). The rest (0.15 via pair, 0.24 pad pairs, P1T/P2T tracks) are Sofar's copied geometry. P and N carry the full bus voltage between them, which is why the brief has a bus class | Matched each item against the mote through the block transforms (P1T/P2T copied vs NEW) | Either apply 0.35 to new bus↔bus copper (router: treat the opposite leg as "other" outside copied regions) or declare these items with their spacings in §6 #17 |
| R3-N1 | NIT | §5's 1V8 row cites "(REPORT §6; the legs, not the feeds)", but §6 is the section that is missing (R3-F1) | — | Fixed with R3-F1 |

## Could not verify
- A fresh full rebuild this round (round 2's rebuild showed DRC-equivalence; §8 states the method).

## Repo untouched
My worktree: git status clean before and after. Your worktree untouched. All runs, including the .kicad_dru probes, used copies in my scratchpad.
