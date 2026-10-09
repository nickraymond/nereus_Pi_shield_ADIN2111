# New routing vs BRIEF §6 (M5)

Copied copper (blockcheck-matched): 805 items; new: 665 tracks/vias (board total 1470).

## Widths of new tracks
| class | width | segments |
|---|---|---|
| bus | 1.5 | 8 |
| data | 0.2 | 78 |
| payload | 0.15 | 1 |
| payload | 0.6 | 16 |
| pi5v | 1.0 | 33 |
| power | 0.15 | 1 |
| power | 0.2 | 7 |
| power | 0.5 | 4 |
| rail | 0.15 | 4 |
| rail | 0.2 | 108 |
| signal | 0.15 | 6 |
| signal | 0.2 | 295 |

Below the class minimum (not the 0.15 fan-out allowance): 0

Small-pad stubs of power-class nets at 0.2 mm (BRIEF §6 'small decoupling stubs keep the mote's 0.2 mm'; ≤ 2 mm per pad, 0.15 clearance as DRC checks it): 6 — VBUS stub at C20.1 0.4 mm; VBUS stub at C49.1 0.4 mm; VBUS stub at R15.2 0.4 mm; VBUS stub at R16.2 0.4 mm; VBUS stub at R41.1 0.9 mm; VBUS stub at U11.1 0.3 mm

Links routed at 0.15 mm beyond a fan-out (> 2 mm of 0.15 mm track on the net; below the 0.2 mm class width, BRIEF §6): 0

## Brief clearances on new bus / power / payload / 5 V copper
Violations of the class clearance (bus 0.35, power/payload/5 V 0.25): 0

## ADIN data pairs (BRIEF §6: ≤ the mote's length, Top + Internal 1, two vias)
| net | length mm | limit | vias | layers | length ok | as the mote (2 vias, Top + Internal 1) |
|---|---|---|---|---|---|---|
| BM1_DATA_P | 9.39 | 9.5 | 2 | Internal 1, Top Layer | yes | yes |
| BM1_DATA_N | 8.77 | 9.5 | 2 | Internal 1, Top Layer | yes | yes |
| BM2_DATA_P | 20.19 | 21.3 | 2 | Internal 1, Top Layer | yes | yes |
| BM2_DATA_N | 20.87 | 21.3 | 2 | Internal 1, Top Layer | yes | yes |

## Kelvin sense (R8 shunt ↔ U4 INA232): pad-to-pad by tracks only (no via, no plane), as the mote
| link | track path | tracks in that cluster mm |
|---|---|---|
| U4.1 ↔ R8.2 (P_IN) | yes | 18.17 |
| U4.2 ↔ R8.1 (VBUS) | yes | 9.67 |
