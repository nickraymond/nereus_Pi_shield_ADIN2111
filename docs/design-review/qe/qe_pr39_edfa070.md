# QE review — PR #39 round 2 — 2026-11-18
**Verdict:** APPROVED WITH NITS on `edfa0705b056c01de94eb6000a884dd69c19c6eb`. 0 BLOCKER, 0 MAJOR; 5 MINOR open (fix or ticket), 2 NIT.
**Reviewed:** exactly `edfa070` (PR head at start and end), delta from round 1's `602830d`: `e3c8688` (board, `stepR1_fixes.py`,
`pourcheck.py`, `run_C.sh`) and `edfa070` (HANDOVER). Read-only; KiCad closed; copies under
`/var/folders/wn/sxhv72591ml9f01mdxwfkmj40000gn/T/tmp.anVnn00R6N` (`h2d/`, `rep_R1/`). Round 1: `qe_pr39_602830d.md` beside this file.
Finished 12:45 PM PST.

## Claims checked

| Claim | Result | Evidence |
|---|---|---|
| Schematic, .kicad_pro, .kicad_dru unchanged since 602830d | **Confirmed** | `git diff --quiet 602830d edfa070 -- *.kicad_sch *.kicad_pro *.kicad_dru` → no change, so ERC / net diff of round 1 stand |
| DRC 3 skew + 16 items_not_allowed, parity 0, 33 unconnected | **Confirmed** | `pcb drc --schematic-parity --severity-all --refill-zones`; warnings identical to round 1 |
| 36 → 33 | **Confirmed** | unconnected item diff: both GND zone-to-zone items and R26.2–R27.2 gone; the other changes re-pair the same ADC_ALERT / N6_3V3 pads |
| Lock | **Confirmed** | own `cmp.py`: base → edfa070 under one transform: Sofar's 81 footprints (5 removed as decided), 1055 tracks/vias, 170 zones 0 changed; d9f7e32 → edfa070 only J21 (+0.040 mm); 602830d → edfa070: 0 changed, 4 tracks gone, 13 tracks + 3 vias new. The 4 removed uuids were added in d818176 (none present at d9f7e32). `lockcheck_all.py` with them allowed: PASS |
| R1 reproduces | **Confirmed** | `stepR1_fixes.py` on a copy of 602830d's board + kicad-cli refill: tracks, vias, zones, footprints and 26 fills identical to edfa070; the `.removed` file lists the same 4 uuids |
| Pour pieces tied (round 1 F1) | **Fixed** | own `islands.py`: no GND pour island without a via; GND vias (3.5, 38.17), (4.6, 38.87), (11.45, 47.51) 0.45/0.20; `pourcheck.py`: 2 untied at 602830d, 0 at edfa070 |
| ADIN_PWR into TP8 (round 1 F3) | **Fixed** | `ends.py`: every new track end lies on same-net copper; end (25.457, 11.357) |
| R26.2 / R27.2 joined, SDA at X' 27.9 | **Confirmed** | new N6_3V3 bottom track X' 28.4; clearances 0.275 (R26.1), 0.300 (SDA); new GND via 0.209 from TP40 (bottom), 0.262 from MOTOR_nSLEEP (In2): above the 0.2 mm the session aimed at |

## Findings

| # | Severity | Finding | Evidence | Ask |
|---|---|---|---|---|
| R1-2 | MINOR (open) | `pourcheck.py` covers only zones named "N6 GND"; it counts a piece tied when a GND via lies within 0.31 mm or a through-hole GND pad within 1.0 mm of it, without checking the via or pad reaches the main ground; it ignores other nets' zones and Sofar's. The count-based gate stays | script text; my island check found no case it misses at this sha | Add an unconnected-item diff by net to the gate (any new item on GND or a power net fails) |
| R1-4 | MINOR (open) | Undisclosed class departures of round 1 (logic 0.21–0.25 mm to motor outputs, ISET 0.25, VBUS 0.5–0.6 mm, 3/3/2 vias on 5 V, OUT2 0.3 mm) | round 1 | List as deviations or fix |
| R1-5 | MINOR (open) | SDA at X' 27.9 still crosses the south GND-plane slot (void y 6.70–7.04), as do INT and ADIN_PWR | `block.py` on edfa070 | Record with deviation 4 / Sofar question |
| R1-6 | MINOR (open) | U12's 5 V through the 2.0 / 1.75 mm PWR-plane band: up to 1.24 A against the plan's 1.08 A at 10 °C | unchanged | Decide before fabrication |
| R1-7 | MINOR (open) | In2 logic lines rely on J21's removed inner pads | unchanged | Trap in HANDOVER |
| R2-1 | NIT | HANDOVER line 6: "Commits after 602830d are local … The QE review has not run yet" (both pushed and reviewed now); lines 118–121 keep 1.1 mm (measured 1.03 edge to edge), "no outer-layer logic between y 22 and 37.5" (MOTOR_IN1 bottom at y 37.30), 0.35 mm to TP41 (measured 0.44) | `git show edfa070:HANDOVER.md` | Correct |
| R1-9 | NIT (open) | Sofar's 22 mm open stub on ~ADIN_RST; MISO resistor at the receiving end | round 1 | Note |

## Could not verify
As round 1: MP6550 datasheet claims (maker's site blocked the fetch, no local copy); the N6's 1 M on P6. The sub-agent review record in `~/NereusData/.../stageR1/` was not read (not needed: I checked the board).

## Repo untouched
`git status --short` before and after: empty. No GitHub post, no message to Nick.
