# New routing vs BRIEF §6 (M5)

Copied copper (blockcheck-matched): 801 items; new: 1614 tracks/vias (board total 2415).

## Widths of new tracks
| class | width | segments |
|---|---|---|
| bus | 1.5 | 8 |
| data | 0.2 | 130 |
| payload | 0.15 | 1 |
| payload | 0.6 | 22 |
| pi5v | 1.0 | 6 |
| power | 0.15 | 1 |
| power | 0.5 | 11 |
| rail | 0.15 | 3 |
| rail | 0.2 | 249 |
| signal | 0.15 | 6 |
| signal | 0.2 | 1060 |

Below the class minimum (not the 0.15 fan-out allowance): 0

Links routed at 0.15 mm beyond a fan-out (> 2 mm of 0.15 mm track on the net; below the 0.2 mm class width, BRIEF §6): 0

## Brief clearances on new bus / power / payload / 5 V copper
Violations of the class clearance (bus 0.35, power/payload/5 V 0.25): 0

## ADIN data pairs (BRIEF §6: ≤ the mote's length, Top + Internal 1, two vias)
| net | length mm | limit | vias | layers | length ok | as the mote (2 vias, Top + Internal 1) |
|---|---|---|---|---|---|---|
| BM1_DATA_P | 9.46 | 9.5 | 2 | Internal 1, Top Layer | yes | yes |
| BM1_DATA_N | 8.8 | 9.5 | 2 | Internal 1, Top Layer | yes | yes |
| BM2_DATA_P | 17.98 | 21.3 | 2 | Internal 1, Top Layer | yes | yes |
| BM2_DATA_N | 18.62 | 21.3 | 2 | Internal 1, Top Layer | yes | yes |

## Kelvin sense (R8 shunt ↔ U4 INA232): pad-to-pad by tracks only (no via, no plane), as the mote
| link | track path | tracks in that cluster mm |
|---|---|---|
| U4.1 ↔ R8.2 (P_IN) | yes | 18.17 |
| U4.2 ↔ R8.1 (VBUS) | yes | 9.67 |
