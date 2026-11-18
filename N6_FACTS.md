# OpenMV N6: facts sheet for the shield

Board: **OpenMV N6** (Nick, this session's chat, 2026-11-17). Every value below was read on 2026-11-17 from the
source named beside it. The full research notes with every pin and every "not found" are outside git:
`~/NereusData/nereus_Pi_shield_ADIN2111/n6_shield/n6_research_raw.md`, with local copies of the sources in
`n6_shield/sources/`. How it was read: a research agent fetched the documents; I re-read the docs page (S2) and the
model's bounding boxes (S5) myself for the values marked ✔. Values without ✔ rest on the agent's reading.

## Sources

| ID | Document | URL |
|---|---|---|
| S1 | N6 schematic PDF, file name "Rev4", sheets dated 10/06/2025 | https://cdn.shopify.com/s/files/1/0803/9211/files/OpenMV-N6-Schematic-Rev4.PDF?v=1773503475 |
| S2 | OpenMV docs, N6 quick reference | https://docs.openmv.io/dev/_sources/openmvcam/quickref/openmv-n6.rst.txt |
| S3 | OpenMV pinout image | https://docs.openmv.io/dev/_images/pinout-openmv-n6-pag7936.png |
| S4 | openmv-boards pinout JSON | https://raw.githubusercontent.com/openmv/openmv-boards/main/pinouts/OPENMV_N6.json |
| S5 | openmv-boards 3D model, top node "N6 r3 IDE" | https://raw.githubusercontent.com/openmv/openmv-boards/main/models/OPENMV_N6.glb |
| S6 | MicroPython board definition (pins.csv, mpconfigboard.h) | https://raw.githubusercontent.com/micropython/micropython/master/ports/stm32/boards/OPENMV_N6/pins.csv |
| S7 | MicroPython STM32N657 alternate-function table | https://raw.githubusercontent.com/micropython/micropython/master/ports/stm32/boards/stm32n657_af.csv |
| S8 | OpenMV firmware board config | https://raw.githubusercontent.com/openmv/openmv/master/boards/OPENMV_N6/board_config.h |
| S9 | OpenMV battery life estimator script | https://docs.openmv.io/dev/_static/battery_life/app.js |
| S10 | Gigabit PoE shield docs | https://docs.openmv.io/dev/_sources/openmvcam/shields/gigabit-poe-shield.rst.txt |
| S11 | PoE shield docs | https://docs.openmv.io/dev/_sources/openmvcam/shields/poe-shield.rst.txt |
| S12 | Pinout image from the product page, posted by Nick in the first-pass session's chat on 2026-11-18 ("this is from the front view") | https://openmv.io/products/openmv-n6 |

Not reachable: OpenMV's store page (HTTP 429) and ST's STM32N657 datasheet (timeout).

## Revision

The schematic is "Rev4" (S1); the 3D model is "r3" (S5). What changed between them: not found. **All geometry below
is from the r3 model, not from a dimension drawing** (none was found), so confirm it on a real board or a STEP file.

## Outline, headers, mounting

Frame: x across the board, y from the USB-end edge towards the camera end, as in the model (S5).

| Item | Value | Source |
|---|---|---|
| PCB outline | 35.56 x 44.45 mm (1.40 x 1.75 in), 1.3 mm thick ✔ | S5 |
| Headers | two 2x8, J2 left and J3 right, part FHFS85-208G0AYA4; 2.54 mm pitch | S1, S5 |
| Pin columns, x | 1.56 and 4.10 (left), 31.42 and 33.96 (right); inner to inner 27.32 mm, outer to outer 32.40 mm | S5 |
| Pin rows, y | 19.37 (row 1, camera end) down to 1.59 (row 8, USB end); header bodies y 0.32 to 20.64 ✔ | S5 |
| Header build | socket bodies on the camera side, 8.5 mm tall ✔; pins stick 9.19 mm out of the back | S5 |
| Mounting | no free mounting holes found. Two SMT spacers (9774030243R) at (2.54, 36.20) and (33.02, 36.20) on the camera side hold the camera module ✔ | S5, S1 |
| Back of the N6 | parts over the whole back; tallest: LiPo connector leads 2.09 mm, microSD socket 1.46 mm (x 23.6 to 35.0, y 21.2 to 33.1) | S5 |
| USB-C | on the y = 0 edge, camera side | S1, S5 |
| OpenMV's own shields | same two 2x8 headers; the PoE shield "stacks with dual-header shields" | S10 |

## Header pins (row 1 = camera end, row 8 = USB end)

| Row | Left outer (x 1.56) | Left inner (x 4.10) | Right inner (x 31.42) | Right outer (x 33.96) |
|---|---|---|---|---|
| 1 | P0, PD7: SPI2 MOSI | Ethernet LED | Ethernet pair C+ | P12 = RESET (not a GPIO) |
| 2 | P1, PD11: SPI2 MISO | Ethernet pair B- | Ethernet pair C- | P11, PC13: wake input, pulled to RAW |
| 3 | P2, PA12: SPI2 SCK, UART4 TX, CAN1 TX | Ethernet pair B+ | Ethernet pair D+ | P10, PD6: TIM15 CH2, shared with the camera's frame sync |
| 4 | P3, PA11: SPI2 CS, UART4 RX, CAN1 RX | Ethernet pair A- | Ethernet pair D- | P9, PG12: TIM17 CH1 |
| 5 | P4, PB10: I2C2 SCL, UART3 TX, TIM2 CH3 | Ethernet pair A+ | P14, PE8: UART7 TX | P8, PD13: TIM4 CH2 |
| 6 | P5, PB11: I2C2 SDA, UART3 RX, TIM2 CH4 | PWR WKUP, pulled to RAW | P13, PE7: UART7 RX | P7, PG13: TIM4 CH1 |
| 7 | P6, PG0: TIM12 CH1, and the ADC input | RAW | BOOT0 | VIN |
| 8 | 3V3 | GND | 3V3 | GND |

Sources: labels and functions S2 ✔ and S3; MCU pins S6 and S1; positions S4 and S5. The pinout JSON (S4) is wrong in
two places against the schematic: it calls the RAW position GND and labels the Ethernet C / D positions P18 to P15.

**Free for a shield: P0 to P9 (ten pins), P13, P14: twelve in all.** P10 is shared with the camera sensor, P11 is a
wake input on the always-on RAW rail, P12 is reset. P15 to P18 (SPI4) reach the header only after moving 0-ohm links
on the back of the N6, which "only disables gigabit Ethernet" (S2). The Ethernet pairs on the inner columns are live
PHY lines without magnetics (S1, S2): the shield must leave those eight pads and the Ethernet LED pad unconnected.

## Electrical

| Item | Value | Source |
|---|---|---|
| Logic level | 3.3 V; "The N6's I/O pins are **not 5 V tolerant**" ✔ | S2 |
| Per pin | 20 mA sink or source ✔ | S2, S3 |
| VIN | "5 V input" (S2 ✔); schematic net label "4.7V-5.7V" (S1, S4); the product page's pinout image says "VIN (4.7V – 5.7V)" (S12 ✔). The docs copy of the image still says "VIN (3.6V - 5V)" (S3 ✔, re-read 2026-11-18): two versions of the same image. The shield feeds 5.11 V nominal, inside the 4.7 to 5.7 V range | S1 to S4, S12 |
| VIN and USB together | a dual ideal diode (LM66200) picks the higher of VIN and USB; P-FET reverse protection on VIN | S1, S2 ✔ |
| 3V3 pins | output only, "Up to 1 A available for shields" ✔; "3.3V Rail (1A supply Max)" on the pinout image (S12 ✔). A retailer's copy of the store text says under 250 mA: conflict | S2, S12 |
| RAW | always-on 3.6 to 5 V, in or out; "You must drive RAW through a series diode" ✔ | S2 |
| Board power | 750 mW active; deep sleep 3.7 mW on LiPo, 12.5 mW on VIN or USB | S9 |
| OpenMV's PoE shields | feed 5.4 V and 5.6 V into VIN, up to about 1 A | S10, S11 |
| ADC | one header input: P6, "dedicated 12-bit ADC input", full scale about 3.3 V, through a 470 k / 560 k divider and a buffer ✔ | S2, S1 |
| DAC | none | S6 |
| PWM | P4, P5 (TIM2 CH3 / CH4), P6 (TIM12 CH1), P7, P8 (TIM4 CH1 / CH2), P9 (TIM17 CH1), P10 (TIM15 CH2) ✔ | S2 |
| SPI | SPI2 on P0 MOSI, P1 MISO, P2 SCK, P3 CS ✔; the docs example runs 10 MHz and drives CS as a plain pin ✔ | S2 |
| I2C | I2C2 on P4 SCL, P5 SDA ✔; no pull-ups found on the N6's schematic | S2, S1 |
| UART | UART3 on P4 / P5, UART4 on P2 / P3, UART7 on P14 / P13 | S2 |

## Not found

- A dimension drawing, STEP or board file from OpenMV; the header part's datasheet (socket height, pin length).
- Mounting hole sizes; the weight; the maker's own shield outline.
- ST's limits for the STM32N657 pins (absolute maximum, total I/O current, ADC electrical limits).
- OpenMV's stated maximum SPI and I2C speeds.
- The LM66200's datasheet was not read: the VIN / USB behaviour above is from the schematic and the docs text.
- The ADC reference (the schematic shows VREF+ on a 1.8 V rail, read at low zoom): recheck before relying on it.

## Left / right sense of the headers: settled by the maker's image, 2026-11-18

The pinout image (S12, and the docs copy S3) is a view of the camera side: the lens is in it, and Nick confirmed
"this is from the front view". Seen from the front, P0 to P6 and one 3V3 pin are the left outer column; Reset, P11,
P10, P9, P8, P7, VIN and GND are the right outer column. Seen from the back they are mirrored, which is what the
mocks and the board assume. `scripts/n6_header_check.py` compares every pad of J21 / J22 on the board with the
image's four columns and eight rows: **0 of 32 pads disagree** (run on the stage C part 1 board).
Still not measured on a real board: the header spacing. The r3 model gives 32.40 mm outer to outer. The shield had
32.44 mm (J21 sat 0.04 mm west of the model's position, because the mock used the un-mirrored column value); J21 was
moved 0.04 mm east on 2026-11-18 on Nick's word, and the check now shows 32.40 mm and no pad offset.
