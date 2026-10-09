# New routing vs BRIEF §6 (M5)

Copied copper (blockcheck-matched): 827 items; new: 1587 tracks/vias (board total 2414).

## Widths of new tracks
| class | width | segments |
|---|---|---|
| bus | 1.5 | 8 |
| data | 0.15 | 132 |
| payload | 0.5 | 3 |
| payload | 0.6 | 56 |
| pi5v | 0.3 | 1 |
| pi5v | 0.5 | 5 |
| pi5v | 1.0 | 2 |
| power | 0.15 | 1 |
| power | 0.5 | 22 |
| rail | 0.15 | 16 |
| rail | 0.3 | 412 |
| signal | 0.15 | 300 |
| signal | 0.2 | 509 |

Below the class minimum (not the 0.15 fan-out allowance): 10 — pi5v 5V_PI 0.5; pi5v 5V_PI 0.5; pi5v 5V_PI 0.5; pi5v 5V_PI 0.3; pi5v 5V_PI 0.5; pi5v 5V_PI 0.5; power VBUS 0.15; payload VBUS_OUT 0.5; payload VBUS_OUT 0.5; payload VBUS_OUT 0.5

Links routed at 0.15 mm beyond a fan-out (> 2 mm of 0.15 mm track on the net; below the 0.2 mm class width, BRIEF §6): 13 — 3V3 9.2 mm; ADIN_MOSI 35.1 mm; ADIN_PWR 4.3 mm; BM1_DATA_N 7.9 mm; BM1_DATA_P 9.4 mm; BM2_DATA_N 23.4 mm; BM2_DATA_P 21.3 mm; ISET 2.8 mm; Net-(U11-UVLO) 5.1 mm; PAYLOAD_EN 4.9 mm; ~{ADIN_CS} 39.8 mm; ~{ADIN_P2_LED1} 34.9 mm; ~{PAYLOAD_FAULT} 16.0 mm

## Brief clearances on new bus / power / payload / 5 V copper
Violations of the class clearance (bus 0.35, power/payload/5 V 0.25): 1
- payload VBUS_OUT vs ~{PAYLOAD_FAULT} on Top Layer at (34.10, 53.00)

## ADIN data pairs (BRIEF §6: ≤ the mote's length, Top + Internal 1, two vias)
| net | length mm | limit | vias | layers | length ok | as the mote (2 vias, Top + Internal 1) |
|---|---|---|---|---|---|---|
| BM1_DATA_P | 9.4 | 9.5 | 2 | Internal 1, Top Layer | yes | yes |
| BM1_DATA_N | 7.9 | 9.5 | 0 | Top Layer | yes | no (declared: fewer vias / one layer is no electrical loss) |
| BM2_DATA_P | 21.3 | 21.3 | 0 | Top Layer | yes | no (declared: fewer vias / one layer is no electrical loss) |
| BM2_DATA_N | 23.4 | 21.3 | 2 | Internal 1, Top Layer | NO | yes |

## Kelvin sense (R8 shunt ↔ U4 INA232): pad-to-pad by tracks only (no via, no plane), as the mote
| link | track path | tracks in that cluster mm |
|---|---|---|
| U4.1 ↔ R8.2 (P_IN) | yes | 18.95 |
| U4.2 ↔ R8.1 (VBUS) | yes | 9.67 |
