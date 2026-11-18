# N6 shield: pin map proposal and answers to the explore questions

Proposal only, 2026-11-17. Nothing in `N6_Shield_ADIN2111/` has changed. N6 facts: `N6_FACTS.md` (its source IDs
S1 ... are used here). Shield signals: read from the starting board's header J1 and part pads with
`scripts/n6_read_board.py` and `scripts/n6_groups.py`.

Datasheets used here (read 2026-11-17 by a research agent from the PDFs; I checked the ADIN2111 register values in
the PDF text myself, the others I could not open in this session):
- [MP] MPS MP6550 datasheet Rev. 1.0, https://docs.rs-online.com/67b6/A700000013717563.pdf
- [AD] ADIN2111 datasheet **Rev. 0** (mirror https://cdn.components.ru/media/PDF/8017716.pdf; analog.com timed out).
  The project's own facts in `docs/SPEC.md` are from Rev. B; re-check the LED registers against Rev. B before use.

## What the starting design uses on the Pi header (J1)

| Group | Signals | Pins today |
|---|---|---|
| ADIN2111 SPI | ADIN_SCK, ADIN_MOSI, ADIN_MISO, ~ADIN_CS | 4 |
| ADIN2111 control | ~ADIN_INT, ~ADIN_RST, ADIN_PWR (enables the ADIN's two supply switches U2 / U3), ADIN_TIMER | 4 |
| I2C0 | SDA, SCL: power monitor U4 (INA232) and ADC U13 (ADS1115) | 2 |
| ADC | ~ADC_ALERT | 1 |
| Motor driver | MOTOR_IN1, MOTOR_IN2, MOTOR_nSLEEP | 3 |
| Payload switch | PAYLOAD_EN, ~PAYLOAD_FAULT | 2 |
| Qwiic | I2C3 SDA, SCL | 2 |
| Spare pad rows | GPIO 7, 12, 14, 15, 17, 19, 20, 21 | 8 |
| Power | PI_5V (pins 2, 4), PI_3V3 (pins 1, 17: pull-ups and Qwiic only), GND | |

That is 18 signals plus 8 spares. The N6 offers 12 free pins.

## Proposed map

| Shield signal | N6 pin | Why this pin |
|---|---|---|
| ADIN_MOSI | P0 | SPI2 MOSI (S2) |
| ADIN_MISO | P1 | SPI2 MISO |
| ADIN_SCK | P2 | SPI2 SCK |
| ~ADIN_CS | P3 | SPI2 CS; the docs drive CS as a plain pin |
| I2C SCL (U4, U13, Qwiic) | P4 | I2C2 SCL; the only I2C bus on the header |
| I2C SDA | P5 | I2C2 SDA |
| MOTOR_IN1 | P7 | TIM4 CH1 |
| MOTOR_IN2 | P8 | TIM4 CH2: both PWM inputs on one timer |
| ~ADIN_INT | P6 | plain input with interrupt; Sofar's INT stub ends on the block's east side, 6.6 to 10 mm from P6 (reviews of mocks L and P). Decided by Nick, 2026-11-17: "Yes, swap them" |
| ADIN_PWR | P13 | plain output |
| MOTOR_nSLEEP | P14 | plain output |
| ~ADIN_RST | P9 | plain output; 8.7 mm in the mock P trial. Decided with the INT swap, 2026-11-17 |
| 5 V from U10 | VIN | accepts 4.7 to 5.7 V (S1) |
| Pull-up and Qwiic supply | 3V3 (both pins) | the N6's 3.3 V output; kept apart from the mote's own 3.3 V, as on the Pi boards (SPEC constraint 4) |
| GND | both GND pins | |
| Not connected, pads isolated | RAW, BOOT0, PWR WKUP, P10, P11, RESET, the nine Ethernet positions | live or special-purpose lines on the N6 (S1, S2) |

All twelve free pins are used. P6 has about 1 M to ground inside the N6 (S1); against the 1.5 k pull-up R1 on INT that
does not move the level. P13 / P14 are the N6's only UART that does not overlap SPI2 or I2C2, so this map
leaves no serial port on the header.

## Answers to the explore questions

**Can the N6's own ADC replace the ADS1115?** Not fully. The header has one documented ADC input, P6 (12-bit, about
3.3 V full scale, behind a 470 k / 560 k divider and a buffer; S2, S1). The shield has two analog signals: motor
current (MP6550 VISEN) and the pot wiper. One of them could go to P6 and U13 could then be dropped only if the other
is given up. The MP6550's sense output is 100 uA per amp into R48 (4.02 k), so 0.40 V per amp and 0.5 V at the
current-limit trip [MP]; on a 12-bit, 3.3 V scale that is about 2 mA per count, coarse but usable. P2 to P5 are
ADC-capable in ST's pin table (S7) but OpenMV does not offer them as ADC and the map needs them for SPI and I2C.
*Recommendation: keep U13 for both signals (it costs no pins on I2C), drop its ALERT line.*

**Can the N6's PWM drive the MP6550?** Yes. P7 and P8 are TIM4 CH1 and CH2 (S2). The MP6550's IN1 / IN2 take PWM
directly, up to 100 kHz, with V_IH 1.6 V and V_IL 0.4 V, so 3.3 V logic is fine; recommended drive is one input held
high and PWM on the other (slow decay) [MP]. The inputs have 520 k pull-downs [MP], so the bridge coasts while the
N6's pins float.

**A clear and safe SPI route.** SPI2 is on P0 to P3, the outer left column, rows 1 to 4. With the mote block turned
a quarter turn and its L1 end at the USB end, the ADIN2111 lands between rows 1 to 4, and its SPI pads (U1 pins 42
to 45, on the chip's north side: `scripts/n6_adin_pads.py`) face that column. The run is about 16 mm, on one layer
over the ground plane, past the unconnected inner-column pads. The crystal Y1 is on the chip's other side, and the
motor PWM pins P7 / P8 are in the opposite header, 27 mm away, which keeps the Pi Zero lesson (switching lines away
from the crystal). This depends on which way round the header is seen from the back (`N6_FACTS.md`, last item): if
it is the other way, the block turns the other way and the same holds with L2 at the USB end, to be re-checked.
SPI speed: the ADIN2111 allows 25 MHz [AD]; the OpenMV example uses 10 MHz (S2). Series resistors at the N6 end are
an option to decide at schematic time.

**ADIN LEDs under firmware control.** No N6 pin is needed for the two port LEDs. The ADIN2111 has an LED control
register per port (LED_CNTRL, device 0x1E, address 0x8C82): bits LED0_EN / LED1_EN switch each LED off, and the
function field can force "on", "off" or "blink" [AD, Table 225]. Firmware already talks to the chip over SPI, so D9
and D10 can be switched there. The red power LED D8 is not on an ADIN pin: it is lit whenever ADIN_LED_VDD is
present (DESIGN D25). Options for D8: leave it behind the cut-able jumper JP2 as today, drop it, or feed
ADIN_LED_VDD from an N6 pin instead of JP2 (three LEDs at about 1 mA each, far below the 20 mA per pin; S2), which
costs the last spare pin P6.
*Recommendation: port LEDs by register, D8 stays behind JP2, no pin spent.*

## What cannot be supported with the N6's twelve pins

| Signal today | Proposal |
|---|---|
| PAYLOAD_EN, ~PAYLOAD_FAULT | gone with the VBUS-out circuit (Nick's request) |
| Spare GPIO pad rows (8 pins) | gone: no spare pins exist |
| ~ADC_ALERT | not connected; firmware polls U13 over I2C |
| ADIN_TIMER (timestamp output) | not connected, to a test pad. It is only needed for hardware time-stamping |
| Second and third I2C buses | one bus: U4, U13 and the Qwiic connector share I2C2. The separate bus for the LiFePO4+ board is gone |
| ~ADIN_RST | on P9 since 2026-11-17 (was P6). The chip's own power-on reset still works if the line is left floating (SPEC confirmed facts) |
| A UART on the header | none left, because P13 / P14 carry ADIN_PWR and MOTOR_nSLEEP |

If one more pin is needed later, the choices are: tie MOTOR_nSLEEP high through a resistor (the driver then never
sleeps: its sleep current is 10 nA, its awake current was not read), or rework the N6 for P15 to P18 and lose
gigabit Ethernet.

## Open electrical points for the schematic stage

- The ADIN2111 runs from bus power while the N6 may be asleep with its 3.3 V rail gated off: MISO and INT would then
  drive unpowered N6 pins. The Pi boards had the same situation. ST's pin limits were not read (`N6_FACTS.md`).
- I2C pull-ups: none on the N6 (S1), so R26 / R27 stay, fed from the N6's 3V3 pin.
- VIN range conflict (4.7 to 5.7 V in the schematic, 3.6 to 5 V on the pinout image): U10 is set to 5.11 V nominal,
  4.95 to 5.28 V worst case (`power_budget.md` section 5), inside the schematic's range.

## Changes proposed by the mock L review (2026-11-17), for Nick to decide

Source: `~/NereusData/nereus_Pi_shield_ADIN2111/n6_shield/review_L/REVIEW_L.md` (independent review agent; trial
routes on a copy of the mock L board; ADIN2111 datasheet Rev. 0 for the pin facts). The INT / reset swap is applied to the table above; the other rows are still open proposals.

| Item | Today's proposal | Review's proposal | Why |
|---|---|---|---|
| ~ADIN_INT | P9 (west header) | **P6 (east header): DECIDED by Nick 2026-11-17, applied in the table above** | Sofar's stub for INT ends on the block's east side: 6.6 mm to P6 in the trial, against 19.9 mm to P9 under U1 and past the crystal. P6 carries about 1 M to ground inside the N6 (S1) against the 1.5 k pull-up R1: no effect on the level |
| ~ADIN_RST | P6 | P9: decided with the INT swap | reset is rarely driven; the chip has its own power-on reset (SPEC) |
| ADIN_PWR | P13 (west header) | open: 19.2 mm through T1's footprint in the trial | look for a shorter path at layout time, or swap with a west-side signal |
| ~ADIN_CS | plain pin P3 | add 10 k pull-up to ADIN_VDDIO | the ADIN's CS, SCLK and SDI have internal pull-downs, so CS reads "selected" while the N6's pins float |
| SCK, MOSI, MISO, CS | direct | 22 to 47 ohm series resistors at the driving ends (33 ohm to start) | edge control and current limiting if one side is unpowered; there is 2.45 mm of room in the east channel |
| Firmware | - | do not drive SPI pins high before ADIN_PWR is on and VDDIO is up | ADIN pins are rated to VDDIO + 0.3 V |
| U13 / pot supply | mote 3V3 | N6 3V3 pin | about 11 mm against 21 mm; decide at schematic time (it changes what the pot reads against) |
