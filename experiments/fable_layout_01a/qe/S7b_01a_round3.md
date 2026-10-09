# QE review — PR #31 (S7, experiment 1.a, do not merge) — Round 3 — 2026-10-08

*Received from the standing S7 QE session (session message to "Fable layout 01b [e3972d]"). Saved here because this branch
writes only `experiments/fable_layout_01a/` (BRIEF rule 1). F1 / F2 / N1–N4 are fixed in the commit after this file (LOG.md
"Session 2.b, QE round 3 fixes").*

**Verdict:** CHANGES REQUESTED (M3's DFM table; M2 verifies)
**Reviewed:** 03b2adb (board md5 f33491bc… confirmed), from a `git archive` copy in my scratchpad, plus a full rebuild from m0 on a second copy (`VARIANT=pocket HEIGHTS=heights.json tools/build_all.sh m4`, 4 m 30 s). Fresh kicad-cli DRC classified by items; your check_fixed/blockcheck/check_rules re-run; my own pcbnew checks; JLCPCB's capabilities and impedance pages fetched myself.

## Claims checked
| Claim | Result | Evidence |
|---|---|---|
| Scope | ✓ | `git diff --name-only e2eb9dc...03b2adb`: experiments/fable_layout_01a/ only |
| 49 × 68 outline | ✓ recorded | Nick's decision in LESSONS.md §3 and the 2.b KICKOFF ("supersedes the brief's 2 mm south allowance"); edge bbox −10.55…38.55 × −0.05…68.05 (0.1 line). BRIEF.md §2 itself not amended (N1) |
| Frame / fixed items | ✓ | J1.1 (25.23, 8.37); H1–H4 unchanged; MP3/MP4/MP1/MP2 at x −6.31, y 12.0 / 21.4 / 46.1 / 55.5 (ring 3.69 → 0.5 from x −10.5); MTG at the corners; L1 (12.74, 47.25) |
| DRC 109 / 70 warnings / 1 unconnected / 4 parity | ✓ | Fresh JSON: 76 insert contact + 22 involving T1/T2's `[<no net>]` pads + 10 intra-block courtyards + 1 bus-rule item (BM1_N track vs GND via (7.39, 48.30), which inverse-transforms exactly onto Sofar's via in P1L); unconnected J1 1/17; warnings 28 lib_footprint_mismatch, 38 padstack, 2 nonmirrored, 2 silk_overlap (U1, C33/U6) |
| Rebuild reproduces | ✓ | From-m0 rebuild: DRC identical type for type, unconnected 1; check_rules identical (pairs 9.39 / 8.77 / 19.93 / 20.61, 0 below class / 0 thin / 0 clearance, Kelvin yes/yes) |
| check_fixed 0 failures, no allowance | ✓ | Re-run; `ALLOWANCES = {}` |
| blockcheck 0 missing / 127 trimmed | ✓ | Fresh = committed |
| Kelvin, rigidity, mote pad-to-pad paths | ✓ | R8↔U4 6.821 / 6.445 mm, as the mote; 87 block parts, 0 side or rotation anomalies; the same 3 GND groups by the pours as round 2 (carried in REPORT §9) |
| JLCPCB limits quoted in DFM.md | ✓ | jlcpcb.com/capabilities/pcb-capabilities (fetched today): 0.09/0.09 mm, via 0.15/0.25, via hole-to-hole 0.2, pad hole-to-hole 0.45, PTH-to-track 0.28, NPTH-to-track 0.2, inner PTH-to-copper 0.3, edge ≥ 0.2, mask dam 0.10, silk 0.15 / 1.0 mm text / 0.15 to pad, NPTH ≥ 0.5, min SMD pad 0.25 × 0.25, same-net 0.25 all match |
| Stackup JLC06161H-3313 in the board | ✓ | jlcpcb.com/impedance: 0.035 / 3313 0.0994 (εr 4.1) / 0.0152 / core 0.55 (4.6) / 0.0152 / 2116 0.1088 (4.16) / 0.0152 / core 0.55 / 0.0152 / 3313 0.0994 / 0.035; the board's (stackup) section has exactly these |

## Findings
| # | Severity | Finding | Evidence | Suggested fix |
|---|---|---|---|---|
| F1 | **MAJOR** (DFM claim false; undeclared) | **DFM row 30 "Via in pad" passes on a false premise.** The row says "none added; Sofar's thermal-pad vias under U1 (16) and the others are the mote's". I matched every via whose centre lies in an SMD pad against the mote through the block transforms: **44 are Sofar's, 64 are new.** Many are in pads of parts that don't exist on the mote. **U11 pads 4/5/6 (0.6 × 0.24 mm)** and 11 each carry a 0.45 mm via, wider than the pad. Others: **R26.2 (2 vias) and R27.2 in 0.45 × 0.45 mm 0402 pads**; D8.1, D9.1, D10.1 (LEDs); JP2.1/.2; R44.1, R45.1, R46.1, R41.2, R42.2, R43.1, R34.1, R35.2; C31.1/.2 (3); D3.1 (3); J5.1/.2; D1.1; R11.1/.2; R15.2; R16.1; TP8/TP20/TP24/TP36. New stitch/escape vias also sit in block parts' pads (L1.1/.3/.4, L2.1/.2/.4, D5.1/.2, R7.1/.2, R8.1, R3.2, T2.7, C20/C21/C23/C33). The row's own JLC text says plain vias in pads "wick solder", and the board isn't specified with JLC's filled-and-capped option. The row can't fail anyway: tools/dfm.py line 416 builds `R["via_in_pad"] = (…, True)`. Board copy count: DFM.md lists 80; my centre-in-pad test on the pad's own layer finds 108 | My vip check (pcbnew, scratch); `sed -n 405,416p tools/dfm.py` | Make row 30 measured (pass only if every via-in-pad is Sofar's or on a thermal pad/test point), move the fresh-part vias off the pads (escape then via, as the router does elsewhere), or declare via-in-pad filled-and-capped with its cost. Re-run DFM |
| F2 | MINOR | **DFM row 29 understates the small-pad failure.** Besides U6 (FP-YBG0006, 6 pads 0.23 mm, Sofar's), **U2 and U3** (AP22913 WLCSP, 8 pads 0.235 mm, Sofar's footprint) and **U11** (Package_SON:Texas_DRC0010J, KiCad stock, a part this design added: 10 pads 0.24 mm wide) are below JLC's 0.25 × 0.25. The row reports only the minimum and declares only U6 | My netted-SMD-pad scan | List every footprint under 0.25 in the row and in REPORT §9 (Nick's call per part; U11's footprint isn't Sofar's) |
| N1 | NIT | BRIEF.md §2 still reads 46 × 65 with 2 mm growth; the 49 × 68 decision lives in LESSONS/KICKOFF | — | Add a dated note in BRIEF §2 pointing to LESSONS §3 |
| N2 | NIT | The exclusion reason for the BM1_N stub says "0.31 mm apart"; DRC measures **0.250 mm** (also in round 2, which I missed) | DRC JSON | Correct the number |
| N3 | NIT | DFM row 4 says "0 gaps" and also "Sofar's bus leg at T1 pad 6 is the one item, declared" | DFM.md | Make the text match the measurement |
| N4 | NIT | 28 lib_footprint_mismatch warnings: dfm_fix's silk edits live only on the board copies, so a KiCad "Update Footprints from Library" would undo them | DRC warnings | Note it for Nick's KiCad session, or move the silk fixes into the libraries of the experiment copy |

## Could not verify
- The scratch trials behind OPTIONS A3 (U1 centre vs pocket): not re-run, only read.
- The before/after and review HTML pages: not opened.

## Repo untouched
My worktree: git status clean before and after. Your worktree untouched; all runs used git-archive copies in my scratchpad.
