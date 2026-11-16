# Pi Zero fit "G" (65 x 39.5 mm): routing-feasibility and power review

**Verdict: ROUTABLE WITH CHANGES.** As drawn, BM2_N has no top-layer path at any width and four Sofar copper items touch J1 pads.
With the changes in "Smallest set of changes": about **80 %** that every net routes DRC-clean, about **65 %** that it does so with no second placement pass. Space is not the limit; the unknowns are the parts that are still boxes.

Frame: G's (x_old - 113.47, y_old - 89.34), mm. "Scratch" = derived from `review_G_scratch_routing/scratch_G_core_only.kicad_pcb` (source board, 543 non-Sofar tracks and 57 non-core parts removed, J1 and holes moved, new outline, zones refilled) rasterised at 0.05 mm. "Trial" = my grid router on that raster (0.2 mm track, 0.127 mm clearance, 0.6/0.3 vias, 0.5 mm edge, r 3.0 hole keep-outs). A trial path is an existence proof, not a layout. "Frozen board" = `Nereus_Pi_Shield_Adin2111.kicad_pcb`.

## BM connector position (the owner's question)

**Move both. BM2 to block x = 10.5 (centre 15.3, 8.7 mm west), swapping with POT (POT to x 20.3). BM1 to block x = 50.6 (centre 55.4, 7.5 mm east), swapping with QWIIC (QWIIC to x 42.5). MOTOR and the LEDs stay. On both connectors N takes the west pad pair, P the east pair (one cable pinout for both ports).**

Why: the bus enters L1/L2 at their *north* pads (y 16.1..18.8); pads 1/4 (P_IN/VBUS, GND) are south. A trunk from the south must pass under the inductor body or around its outside. Only three such paths exist, and the frozen board already uses them:

| Net | Copper that can be copied 1:1 | Where it arrives | Trial, G as drawn | Trial, connectors moved |
|---|---|---|---|---|
| BM2_P | Sofar stub pad 3 -> (18.18, 22.34), 8.3 mm, 2.0 mm top (the only Sofar bus copper south of an inductor); frozen (18.18, 22.34) -> (15.63, 24.89) -> (15.63, 30.78), 9.5 mm | x 15.6, y 30.8 | 1.0 mm only, 32.5 mm, loops round POT | **2.0 mm, 18.1 mm** |
| BM2_N | frozen pad 2 -> (11.47, 17.22) -> (9.53, 19.16) -> (9.53, 30.76), 16.8 mm, west of the core | x 9.5, y 30.8 | **no path at 2.0 / 1.5 / 1.0** | **2.0 mm, 18.0 mm** (converter block trimmed, F2) |
| BM1_N | frozen pad 2 -> (52.23, 20.56) -> (54.23, 24.96) -> (54.23, 29.71), 15.6 mm, under L1 | x 54.2, y 29.7 | 1.5 mm, 18.8 mm | 1.5 mm, 17.0 mm (2.0 on the frozen board; my raster is conservative on diagonals) |
| BM1_P | none: the frozen east trunk (x 59.8..61.8, y 19.7..31.4) runs through the Pi Zero hole at (61.5, 26.5) | - | 1.0 mm only, 31.6 mm | **1.0 mm, 16.3 mm** (1.5 fails, F3) |

All four are top layer, no vias, no crossings (N is west of P at both ports once the connectors sit under the trunk ends). The moved positions are the frozen board's MP4 (x 15.23) and MP1 (x 55.43) insert sites.

10BASE-T1L: Sofar's 0.2 mm Internal 2 branches to T1/T2 and their tap vias are untouched, so Q13's 1.46 / 3.05 mm stays. BM1_P's tap via (52.41, 18.61) reaches pad 3 only through the frozen board's own 4.25 mm, 0.2 mm top link; copy it 1:1. Connector-to-tap length falls from 33..42 mm (frozen) to 16..21 mm; P/N differ by under 1 mm per port in the trial. Ports are not mirror images (BM1_P has the neck of F3, BM2_N passes the converter).

## Blockers

**F1. Sofar copper touches J1 pads (scratch, `a3.py`).** The lock cannot hold literally in the J1 band:
- ~ADIN_RST via (51.66, 5.16) and its Internal 1 segment overlap pin 35's pad by 0.67 / 0.54 mm.
- 3V3 via (51.13, 5.66) and a bottom 3V3 stub overlap pin 35's pad by 0.08 / 0.01 mm (shield 3V3 onto Pi GPIO19).
- GND via (24.27, 5.87) is 0.14 mm from pin 13's pad (rule: 0.3 mm hole clearance).
- **Change:** delete these three vias and two segments (remnants of the mote's connector fan-out); re-land ~ADIN_RST on the remaining Internal 1 track at x 52.7, y 6.2..11.2. Needs Nick's word.

**F2. BM2_N as drawn.** The only route to L2 pad 2 (x 11.71..16.20, facing west) is the frozen one at x 8.5..10.5. The 5 V block (x 0.4..10.6, y 7..19.6) covers its bend, and L2 pad 1 (P_IN, y 19.57..21.73) closes the east side. **Change:** nothing of the converter east of x 7.4 below y 15.8 (trial used 10.2 x 8.8 plus 6.6 x 5.4, 125 mm2), and BM2 moved as above.

**F3. BM1_P neck.** With r 3.0 at (61.5, 26.5) the east strip is closed on every layer (capacity 0 at y 26.5, scratch). The trunk must pass between Sofar's GND polygon corner (58.43, 23.01) and the keep-out: 1.65 mm gap, so about 1.25..1.4 mm of copper for about 2 mm of length. Electrically adequate (1.0 mm, 1 oz: 2.4 A at 10 degC rise by `power_budget.md` section 4; 0.89 A needed). **Change, pick one:** accept the neck; or top keep-out r 2.5 at that hole (gap 2.15 mm); or run P and N both under L1 at 1.5 mm each (4.02 mm between pads; not trialled).

**F4. Payload pads under QWIIC.** The frozen board's J5 is through-hole (`WirePads_1x02_P3.81mm_Oval4.2x2.6mm_Drill1.3mm`); G puts a 6.5 x 4.5 pad block on the bottom at x 53..59.5 directly under a top-side connector. **Change:** surface pads, or move them (the east strip y 7..16 is free on both sides).

## Should fix

**S1. Header fan-out: space is ample; three nets need a named change.** J1 nets read from the frozen board (DESIGN's pin-map table differs on pins 3/5, 31, 36..38; TRACKER N12).

Measured capacity (scratch, `measure.py`, tracks at 0.327 mm pitch): north channel y 5.62..9.07, worst cut: Internal 1 = 5, Internal 2 = 5 (x 20..32), 7..8 elsewhere; top = 0 at x 20..32 (Sofar's GND zone at the old U9 site), bottom median 10. Between the pin rows 1 per layer, north of the header 2 per layer. West strip 34 per layer (16 at the hole). East strip 19, **0 at the hole**. Through the core north-south: 38..73 per inner layer. Trial use never exceeded 2 per layer in the channel and 5 through the core.

| Net (J1 pin, x) | Destination | Trial path (moved-connector run) | Class |
|---|---|---|---|
| ADIN_MOSI (19, 31.23) / MISO (21, 33.77) / SCK (23, 36.31) / ~CS (24, 36.31) / ~INT (22, 33.77) | Sofar stubs x 43.5..47.1, y 9.6..12.4 | 10.8..17.1 mm, one layer each, 0 vias | clear |
| I2C0_SDA / SCL (27 / 28, 41.39) | Sofar top stubs (46.4 / 45.6, 10.7) | 7.8 / 10.3 mm, 1 via | clear |
| ADIN_PWR (16, 26.15) | via (36.05, 19.8) | 22.0 mm Internal 1 | clear |
| ~ADIN_RST (18, 28.69) | Internal 1 at (45.25, 17.55) | 23.9 mm Internal 2, 1 via | clear after F1 |
| ADIN_TIMER (36, 51.55) | R47 beside the LEDs | 38.8 mm, top + Internal 2, 2 vias, through the core | clear; R47 / R2 have no place in the spec |
| PAYLOAD_EN (37, 54.09), ~PAYLOAD_FAULT (31, 46.47) | load switch, bottom SE | 35.3 / 32.9 mm, inner layers through the core, 2 / 1 vias | clear |
| MOTOR_nSLEEP / IN1 / IN2 (29, 32, 33; 43.93..49.01) | MP6550, bottom SW | 57.5 / 62.2 / 59.8 mm, 2..3 vias | clear, longest nets on the board (S5) |
| ~ADC_ALERT (7, 15.99) | ADC | 33.7 mm, 2 vias | clear |
| ADC I2C | ADC | 34.7 / 34.8 mm from pins 3 / 5 (Urchin's bus; my assumption) | bus not decided |
| I2C3_SCL / SDA (13 / 15, 23.61 / 26.15), PI_3V3 (17, 28.69) | QWIIC | 39.0..43.1 mm, 2 vias | clear |
| PI_3V3 (1, 8.37) | ADC, POT | 39.3 mm at 0.3 mm | clear |
| PI_5V (2 / 4, 8.37 / 10.91) | converter | **1.0 and 0.8 mm fail; 0.5 mm routes (5.9 mm)** | named change (S2) |
| VBUS -> U10 | converter VIN | 22.7 mm at 0.6 mm, inner, from the top VBUS zone at (29.65, 13.7) | named change (S2) |
| CFG0_STRAP (R9, stays at 44.78, 9.49) | JP4 in the south block | 42.1 mm when routed first; boxed in when routed last | named change (S4) |
| LED nets, U1.19 strap, ADIN_VDDIO, ADIN_LED_VDD, CFG1_STRAP, VISEN, POT wiper | south strip | 7..25 mm, 0..2 vias | clear |

Result: 35 of 36 nets routed in one pass with at most 3 vias (CFG0 routes in a different order). The same header nets routed in the as-drawn run. No net is without a path.

**S2. 5 V converter at the west end.**
- *PI_5V into pins 2 / 4:* the gap between pads 1 and 3 is 0.84 mm (0.58 mm of copper), and west of pin 1 the hole keep-out leaves about 0.9 mm. Feed through necks on several layers plus an L5 pour between the rows. JP1 belongs here, not in the south jumper block.
- *VBUS feed:* no VBUS at the west edge. L5 there is Sofar's NoConnect_Left island (x 10.5..24.7, y 4.1..16.6) and P_IN (y > 17); the VBUS plane starts at x 25.1. At 0.6 mm on 0.5 oz, 20 mm is 38 mohm and about 16 degC rise at 0.56 A (IPC-2221 internal, k 0.024; my arithmetic). Use 1.0 mm or more.
- *Next to the bus:* L2 pad 2 and the BM2_N trunk are the unfiltered 10BASE-T1L side, 1..3 mm from the block; on the frozen board the converter was about 18 mm away. Put SW, CB and L6 pad 1 in the north-west corner, input and output capacitors toward the trunk, and a GND pour on L3 under the whole strip. Not quantified.
- *Heat copper (D47):* the strip has no Sofar plane, so a GND pour on L3 and a 5V_PI pour on L5 (about 150 mm2 each) are available if the block keeps its vias.

**S3. 5 V rail with the motor** (`power_budget.md` method: loss = Pout (1/eta - 1), L6 = I2 x 26.4 mohm, rest in U10, x 107.8 / 80 degC/W).

| Load | eta | Loss | L6 | U10 | dTj | Bus at 16 V |
|---|---|---|---|---|---|---|
| 1.15 A (Pi 0.65 + motor 0.5) | 90 % | 0.64 W | 35 mW | 0.60 W | 65 / 48 degC | - |
| 1.5 A (Pi 1.0 + motor 0.5) | 89.5 % (interpolated) | 0.88 W | 59 mW | 0.82 W | 88 / 66 degC | 555 mA, 335 mA left of 890 |
| 2.0 A (Pi 1.0 + 1 A spike) | 89 % | 1.23 W | 106 mW | 1.13 W | 121 / 90 degC | 741 mA |

- Fine for a motor that runs rarely; continuous 1.5 A is the regime D15 was written to avoid. At 1.5 A the shield takes 8.7 W of the 12 W module limit.
- U10 peak limit 3.67 A min, valley 2.75 A min (TI SLUSEF4A, search summary). Urchin's ISET resistor is 2 kohm (read from `UrchinCam_01.kicad_pcb`), which is about 2.5 A at 100 uA/A and a 0.5 V trip (MPS data via distributor copies, search summary). A stall then takes U10 into current limit with the Pi on the same rail. **Change:** 5 kohm (about 1 A, 0.5 V/A).
- Bulk: C56 / C57 / C58 are at the converter, 19 mm from the driver. A 1 A step into about 30 uF effective is roughly 0.1 V (estimate; loop bandwidth not known), against D16's 4.82 V low corner and no brown-out detector on the Zero. **Change:** 47 uF or more at MP6550 VIN, besides Urchin's 10 uF + 100 nF.
- Return path: Sofar's GND plane has a notch at x < 18, y > 26.7 (and x > 52 in the south-east), exactly under MOTOR / POT / BM2. Without a new L3 pour the driver's return and VISEN's reference run on tracks (0.3 mm x 10 mm is 16 mohm, 16 mV at 1 A, 3 % of a 0.5 V full scale). With the pour it is 1..2 mV.

**S4. Jumpers and the load-switch leftovers.**
- JP1..JP4 as a 2 x 2 block on the bottom at x 21..30.5 sends CFG0_STRAP 42 mm through the core and PI_5V away from pins 2 / 4. Put JP4 by R9 (top, in the channel), JP2 / JP3 by the LEDs, JP1 at the converter.
- The block as drawn overlaps Sofar's C24 (bottom, to y 31.71) and the load switch overlaps TP23 (to y 31.49); start both at y 31.9.
- About 14 small parts still have no place: R2, R47, R10, R24, R26, R27, R44..R46, R42, TP36, TP38 (R9, R43 can stay where they are).

**S5. Long logic nets.** The trial put 2..7 mm of MOTOR and ADC nets on Internal 1 directly under top-side bus copper (0.099 mm prepreg). Route the long nets on Internal 2 (0.109 mm above the GND plane) through the channel and the west strip.

## Notes

- **N1. Planes.** Inside the core Sofar's L3 GND and L5 (3V3 north, VBUS centre and south-east, P_IN south-west) are intact after refill. Sofar's zone outlines follow the mote's shape and stop at x 10.1 / 60.0 and y 32.2..33.7. New GND zones are needed on L3 for the west end, east end, the south strip and both notches; they join Sofar's plane where they overlap. Sofar's GND slots (west: x 17.8..18.2 to y 12.5, then east and south to y 23.9; east: x 52.8..53.2, diagonal to (44.5, 18.9)) reach the north edge. The west strip and pin 6 sit on the west island, which joins the main plane over about 14 mm south of y 24. Pin 9's pad straddles the west slot, and the Pi's own ground joins all eight GND pins.
- **N2. Load switch (item 5): a safe path exists; no need to drop it.** VBUS: 4.5 mm on the bottom from Sofar's VBUS vias at x 34.4..36.4, y 31.2..31.9 (the L5 VBUS plane reaches y 33.5). VBUS_OUT 4.4 mm to the pads, RTN = GND, control lines as in S1. Cost of the move: C50 (output capacitor), R35 (pull-up), TP19, R11 and Sofar's 11.9 mm VBUS_OUT stub stay at x 20..33, y 9..12, so U11 needs its own output capacitor and pull-up. Lower-risk option: leave the group at its frozen site (top, x 24..32, y 6..10.8). J1's body is on the bottom and its top pads end at y 5.62; only R42 (bottom, y 6.76) and the "U11 RTN island" zone (from y 6.0) need a 0.3..0.5 mm nudge. Not trialled.
- **N3. Connector pads against Sofar copper** (KiCad's stock GH footprint, signal pads y 31.14..32.84): the nearest Sofar item is GND via (45.23, 31.07), 0.19 mm from a BM1 pad as drawn. No short. Sofar copper extends to y 32.34, not 32.05.
- **N4.** The frozen board's J1 solder side is the top, 3.4 mm from the nearest core part; assembly method not checked.

## Smallest set of changes

1. Swap BM2 with POT and BM1 with QWIIC (x above); N west pair, P east pair.
2. Converter block: clear x > 7.4 below y 15.8; SW node north-west; JP1 beside it; PI_5V through necks.
3. Delete the three Sofar vias and two segments of F1.
4. Decide the BM1_P neck (F3).
5. Jumpers by their nets; blocks start at y 31.9; payload pads surface-mount or moved.
6. New L3 GND pours (west, south, notches); L5 5V_PI pour in the west strip; long logic on Internal 2.

Top three remaining risks: (1) BM1_P at the hole and the converter beside BM2_N; (2) the 5 V rail's behaviour with a stalled motor; (3) the unplaced parts and the real MP6550 / ADS1115 / U11 footprints.
Nets to trial-route on a real board before committing: BM1_P, BM2_N, PI_5V to pins 2 / 4, VBUS to U10, the three MOTOR nets, then DRC.

## Not checked

- No DRC run; no real footprints for the MP6550, ADS1115, re-laid U11 group, jumpers or LEDs (blocks treated as opaque on their side).
- GH / SH pad geometry is KiCad's stock library footprint, not checked against JST drawings; connector heights; L6 height against the Pi.
- MP6550 and LMR51430 figures come from search summaries, not the PDFs. ADS1115 noise and PSRR not looked up. SPEC.md not re-read; constraint 4 is quoted from DESIGN.
- Coupling from the converter or the motor into the bus is not quantified. Potting, thermal and EMC effects.
- Which I2C bus the ADC uses; whether the pot goes to the ADC.
- My raster uses a square clearance kernel (pessimistic by up to 41 % on diagonals) and J1 pads as drawn in the frozen footprint.
- The U11-stays-in-place option, the two-trunks-under-L1 option and JP4 in the channel are geometry arguments, not trialled.

## Sources

- Repo: frozen board, mote board, `UrchinCam_01.kicad_pcb`, `.kicad_pro`, `.kicad_dru`, `docs/DESIGN.md` (pin map, D12, D15, D18, D34, D47, D56), `docs/design-review/power_budget.md`, `docs/design-review/jlc_rules_2026-11.md`, `docs/SOFAR_QUESTIONS.md`.
- Scratch folder `review_G_scratch_routing/`: `build.py`, `dump.py`, `ras.py`, `router.py`, `scen.py`, `measure.py`, `a1.py`..`a8.py`; results `routes_G.json`, `routes_B.json`, `trunks_*.json`, `runB.log`; pictures `r_full_*.png` (Sofar copper per layer), `v_trunks_G.png`, `v_trunks_B.png`, `v_B_*.png`.
- KiCad library footprints `JST_GH_BM04B-GHS-TBT_1x04-1MP_P1.25mm_Vertical`, `JST_GH_BM03B-GHS-TBT_1x03-1MP_P1.25mm_Vertical`, `JST_SH_BM04B-SRSS-TB_1x04-1MP_P1.00mm_Vertical`.
- MP6550: https://docs.rs-online.com/67b6/A700000013717563.pdf , https://components101.com/ics/mp6550-bi-directional-dc-motor-driver-pinout-datasheet (search summaries).
- LMR51430: https://ti.com/document-viewer/LMR51430/datasheet/GUID-55E2EEA8-9726-40D9-A528-B216074861B1 (search summary).
