# New routing vs BRIEF §6 (M5)

Copied copper (blockcheck-matched): 815 items; new: 1400 tracks/vias (board total 2215).

## Widths of new tracks
| class | width | segments |
|---|---|---|
| bus | 1.5 | 8 |
| data | 0.15 | 145 |
| payload | 0.3 | 4 |
| payload | 0.6 | 48 |
| pi5v | 0.3 | 1 |
| pi5v | 0.5 | 5 |
| pi5v | 1.0 | 2 |
| power | 0.15 | 1 |
| power | 0.3 | 14 |
| power | 0.5 | 25 |
| rail | 0.15 | 15 |
| rail | 0.3 | 319 |
| signal | 0.15 | 263 |
| signal | 0.2 | 427 |

Below the class minimum (not the 0.15 fan-out allowance): 25 — pi5v 5V_PI 0.5; pi5v 5V_PI 0.5; pi5v 5V_PI 0.5; pi5v 5V_PI 0.3; pi5v 5V_PI 0.5; pi5v 5V_PI 0.5; power VBUS 0.3; power VBUS 0.3; power VBUS 0.3; power VBUS 0.3; power VBUS 0.3; power VBUS 0.3; power VBUS 0.3; power VBUS 0.3; power VBUS 0.15; power VBUS 0.3; power VBUS 0.3; power VBUS 0.3; power VBUS 0.3; power VBUS 0.3

Links routed at 0.15 mm beyond a fan-out (> 2 mm of 0.15 mm track on the net; below the 0.2 mm class width, BRIEF §6): 12 — 3V3 9.0 mm; ADIN_MOSI 35.7 mm; BM1_DATA_N 7.9 mm; BM1_DATA_P 9.4 mm; BM2_DATA_N 23.4 mm; BM2_DATA_P 21.3 mm; ISET 2.8 mm; Net-(U11-UVLO) 4.9 mm; PAYLOAD_EN 4.9 mm; ~{ADIN_CS} 39.6 mm; ~{ADIN_P2_LED1} 34.9 mm; ~{PAYLOAD_FAULT} 5.1 mm

## Brief clearances on new bus / power / payload / 5 V copper
Violations of the class clearance (bus 0.35, power/payload/5 V 0.25): 6
- bus BM2_N vs GND on Top Layer at (4.00, 21.40)
- power VBUS vs Net-(U11-UVLO) on Top Layer at (30.00, 56.60)
- power VBUS vs Net-(U11-UVLO) on Top Layer at (30.00, 56.10)
- power VBUS vs Net-(U11-UVLO) on Top Layer at (31.00, 55.90)
- power VBUS vs ~{PAYLOAD_FAULT} on 6 Bottom Layer at (35.40, 55.30)
- power VBUS vs 3V3 on Internal 1 at (37.00, 21.20)

## ADIN data pairs (BRIEF §6: ≤ the mote's length, Top + Internal 1, two vias)
| net | length mm | limit | vias | layers | length ok | as the mote (2 vias, Top + Internal 1) |
|---|---|---|---|---|---|---|
| BM1_DATA_P | 9.4 | 9.5 | 2 | Internal 1, Top Layer | yes | yes |
| BM1_DATA_N | 7.9 | 9.5 | 0 | Top Layer | yes | no (declared: fewer vias / one layer is no electrical loss) |
| BM2_DATA_P | 21.3 | 21.3 | 0 | Top Layer | yes | no (declared: fewer vias / one layer is no electrical loss) |
| BM2_DATA_N | 23.4 | 21.3 | 2 | Internal 1, Top Layer | NO | yes |
