# New routing vs BRIEF §6 (M5)

Copied copper (blockcheck-matched): 922 items; new: 1331 tracks/vias (board total 2253).

## Widths of new tracks
| class | width | segments |
|---|---|---|
| bus | 1.5 | 8 |
| data | 0.15 | 252 |
| payload | 0.3 | 4 |
| payload | 0.6 | 48 |
| pi5v | 0.3 | 1 |
| pi5v | 0.5 | 5 |
| pi5v | 1.0 | 2 |
| power | 0.15 | 1 |
| power | 0.3 | 17 |
| power | 0.5 | 37 |
| rail | 0.15 | 2 |
| rail | 0.3 | 202 |
| signal | 0.15 | 235 |
| signal | 0.2 | 388 |

Below the class minimum (not the 0.15 fan-out allowance): 28 — pi5v 5V_PI 0.5; pi5v 5V_PI 0.5; pi5v 5V_PI 0.5; pi5v 5V_PI 0.5; pi5v 5V_PI 0.5; pi5v 5V_PI 0.3; power VBUS 0.3; power VBUS 0.3; power VBUS 0.15; power VBUS 0.3; power VBUS 0.3; power VBUS 0.3; power VBUS 0.3; power VBUS 0.3; power VBUS 0.3; power VBUS 0.3; power VBUS 0.3; power VBUS 0.3; power VBUS 0.3; power VBUS 0.3

## Brief clearances on new bus / power / payload / 5 V copper
Violations of the class clearance (bus 0.35, power/payload/5 V 0.25): 3
- bus BM2_N vs GND on Top Layer at (4.00, 21.40)
- power VBUS vs ~{PAYLOAD_FAULT} on Internal 1 at (31.10, 52.55)
- power VBUS vs 3V3 on Internal 1 at (37.00, 21.20)

## ADIN data pairs (BRIEF §6: ≤ the mote's length, Top + Internal 1, two vias)
| net | length mm | limit | vias | layers | ok |
|---|---|---|---|---|---|
| BM1_DATA_P | 9.4 | 9.5 | 2 | Internal 1, Top Layer | yes |
| BM1_DATA_N | 7.9 | 9.5 | 0 | Top Layer | yes |
| BM2_DATA_P | 21.3 | 21.3 | 0 | Top Layer | yes |
| BM2_DATA_N | 23.8 | 21.3 | 2 | Internal 1, Top Layer | NO |
