# QE review — PR #39 round 3 — 2026-11-18
**Verdict:** APPROVED WITH NITS on `d1c9f42b1911496d89e5f4f8e1ade7957684e89f`. 0 BLOCKER, 0 MAJOR; 3 MINOR (2 new, 1 carried), 4 NIT.
**Reviewed:** exactly `d1c9f42` (PR head at start and end), delta from round 2's `edfa070`: stages F (`692fc4e`, `c23fbce`,
`4dc6f74`) and G (`b083f7f`, `0c7c3f6`, `986339c`, `197115e`), repair `d39a491`, `4a378ee`, `2db5cd7`, docs/scripts commits.
Read-only; KiCad closed; copies under `/var/folders/wn/sxhv72591ml9f01mdxwfkmj40000gn/T/tmp.anVnn00R6N` (`h3/`, `r3/`,
scripts `py/`). Schematic, `.kicad_pro`, `.kicad_dru` unchanged since `edfa070` (not in `git diff --stat`), so ERC and net
diff of round 1 stand. Finished 5:16 PM PST.

## Claims checked

| Claim | Result | Evidence |
|---|---|---|
| DRC 3 skew + 16 items_not_allowed, parity 0, 0 unconnected; isolated_copper 3 → 2 | **Confirmed** | `pcb drc --schematic-parity --severity-all --refill-zones` on `d1c9f42`; via_dangling 2 → 0 |
| Every step reproduces | **Confirmed** | F1, F2, F3, G1, G0, G2, G3, G4, C3, C4 each run on its parent's board + kicad-cli refill: tracks, vias, zones, footprints identical multisets, all 26/27 zone fills identical to the commit (`r3/<sha>/rep.txt`) |
| Lock | **Confirmed** | own `cmp.py` base → `d1c9f42`, one transform: 870 tracks, 185 vias, 169 zones/rule areas of Sofar unchanged; the only Sofar change is zone `832abe7e` (net only). `edfa070` → `d1c9f42`: changed = R2 and that zone's net; one zone gone (our "N6 5V U12", redrawn), 144 tracks + 23 vias + 2 zones new |
| Pour pieces tied | **Confirmed** | own `islands.py`: no GND pour island without via/PTH pad (only the inherited 0.15 mm² Y1.2 bottom piece, which sits on that SMD pad, same as `edfa070`) |
| New track ends | **Confirmed** but 1 nit | `ends.py`: 144 new tracks, all on same-net copper except ADIN_VDDIO bottom end (-5.450, 9.600): 0.037 mm outside JP3.1, overlap 0.113 mm (N-2) |
| Clearances of new copper | **Confirmed** | own `clr.py` on all 167 new items: min 0.175 mm (P2_LED1 to D9.2; SCL top track to SDA via), 0.176/0.177 (I2C to VBUS / UVLO vias), 0.185, 0.186, then ≥ 0.196; all above 0.127 mm rule; HANDOVER lists them ("all 0.15 mm or more") |
| Class pairs | **Confirmed** | `pairsN.py`: I2C to motor out 1.22 mm, to motor logic 1.43 mm (plan 0.5); motor/ISET/VISEN numbers same as round 2 |
| G4: straps off the crystal | **Confirmed** | own `xtal.py` (keep-clear box Y1 body + Y1/C7/C8 pads, X' 8.02..12.69, y 13.58..16.51, any layer): straps/R2 now ≥ 1.32 mm (CFG1 / pin 19 top at X' 6.6), CFG0 In2 ≥ 1.87 mm; CFG0 0.213 mm to ~ADIN_INT via as stated |
| `d39a491` repair | **Confirmed** | new BM1_P top track (20.057, 7.458)–(20.057, 5.578) 0.2 mm matches base `af83088` track `3b6aac02` within 0.5 µm under the transform |
| `4a378ee` 5 V feed | **Confirmed** | fills 37.60 (PWR) / 41.68 mm² (In1, priority 1), one piece each; band y 44.30..47.80 = 3.50 mm on both layers; tab neck at y 43.6 X' 1.46..3.00 = 1.54 mm on both, as disclosed |
| `2db5cd7` switch-node net | **Confirmed** | same uuid on mote `ref.kicad_pcb`: net 3V3_Buck_SW, 21.29 mm²; now 21.35 mm², touches L3.1 |
| QE round-2 follow-ups | **Done** | `uncdiff.py` in `run_C.sh` (per-net unconnected diff, GND/supply marked); class departures, slot crossings (incl. N6 3V3 trunk), J21 inner-pad trap all in HANDOVER |

## Findings

| # | Severity | Finding | Evidence | Ask |
|---|---|---|---|---|
| R3-1 | MINOR (new) | ~ADIN_RST: this PR's Internal 1 track (10.007, 15.633)→(7.394, 13.020) (stage D part 2, not in base) runs ~2.8 mm diagonally under Y1's XTAL_I pad and C8. HANDOVER says the reset "still passes under the crystal at Sofar's own corner"; true for the tap point and Sofar's own segments, but the diagonal is ours. Nick asked to keep the crystal clean "even if there are planes between" | `xtal.py` −0.10 mm (overlaps the box); uuid not in base | Put to Nick: tap at Sofar's corner (9.507, 17.404) north of the box and route round C8's west side (watch the pin 19 net on In1 at X' 6.6..8.6), or accept |
| R1-6 | MINOR (reduced) | U12's 5 V: band now 3.5 mm on two layers (≈1.6 A each by IPC-2221 inner, 10 °C); tab still 1.54 mm per layer, and the 0.5 / 0.3 / 0.2 mm bottom escape into pin 9 is the limit (1.24 A current limit) | probe above; HANDOVER section | Nick decides on the pin 9 escape before fab (disclosed as open) |
| R3-2 | MINOR (new) | Plan's strap constraint "R9 and R2 / R47 within 2 mm of their U1 pins" is not met and not listed: R2 pad 1 now 5.99 mm straight from U1 pin 19 (was 3.81), R47 5.25 mm, R9 11.31 mm (R9/R47 since mock P) | own `r2.py` | List as a deviation (DC straps; pin 19 also drives LED0: acceptable) |
| R1-7 | NIT (trap recorded) | J21 inner-pad reliance | HANDOVER Traps | none |
| R3-3 | NIT | HANDOVER line 5–6: "Commits after `edfa070` … are local until Nick says push": now pushed (PR head `d1c9f42`). Finding 6 paragraph in the QE section still says "Not changed. Nick decides …", contradicting the `4a378ee` section | `git show d1c9f42:HANDOVER.md` | Correct |
| R3-4 | NIT | `d39a491` commit message calls the track Sofar's; corrected in HANDOVER and PR text only | commit message | none (history) |
| N-2 | NIT | ADIN_VDDIO bottom track end 0.037 mm outside JP3.1 (overlap 0.113 mm) | `ends.py` | End inside the pad in stage H |

Closed since round 2: R1-2 (per-net gate in place; pourcheck scope noted in HANDOVER), R1-4 and R1-5 (listed), R2-1 numbers.

## Could not verify
MP6550 datasheet (pin 9 current per pad, nSLEEP, θJA); the N6's 1 M on P6; `motediff.py`'s full 870/185/154/16 count (I checked the one zone it changes and the lock against base by my own method). Fab rules not read.

## Repo untouched
`git status --short` before and after: empty. No GitHub post, no message to Nick.
