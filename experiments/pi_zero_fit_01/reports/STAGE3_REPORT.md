# Stage 3 (routing), experiment pi_zero_fit_01: report

Written 2026-11-15, 10:30 PM Pacific. Branch `experiment/pi-zero-fit-01`, nothing pushed. **Partial result: phases A, B and C
(west end) are done and checked; phase D is done for eight ADIN header nets only; 96 connections are still open.**
I stopped here because my working context ran out, not because a net was blocked. Every number below was read from a
run of this session; files are under `~/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/stage3_routing/` ("NereusData" below).

## Gates (last run, `drc_final_recheck.json`)

| | Input (commit d30920b, my run) | Now (commit 91eebf9) |
|---|---|---|
| DRC errors | 3 skew_out_of_range + 16 items_not_allowed | **the same 3 + 16, nothing else** |
| Unconnected | 137 | **96** |
| Schematic parity | 0 | **0** |
| Warnings | 550 | 533 (track_dangling 14 -> 8, via_dangling 19 -> 8, isolated_copper 3 -> 3; silkscreen items unchanged) |
| Lock check | | **PASS**: 154 footprints, 1156 tracks + vias, 171 zones, 17 copper graphics of the input all present and identical; added 116 track segments + vias and 7 zones, no footprint |
| Project files | | `.kicad_pro`, `.kicad_dru`, schematic: identical to d30920b (`git diff`, checked by `run.sh` after every run) |

ERC was not re-run (the schematic is byte-identical to the input). The lock check covers all 154 footprints, which includes the 81 mote ones.
Pair skew (the three carried errors), before and after, identical: BM1_DATA_N -13.1105 mm, BM1_DATA_P -11.7761 mm,
BM2_DATA_P -3.1088 mm. They are on Sofar's Internal 1 data tracks; no trunk is part of those nets.

## Commits

| Commit | Phase |
|---|---|
| ff2f5db | A: bus trunks |
| 27ff643, b1e7816 (scripts), 2a4a185 (board) | B: planes; revised once (PWR-plane lanes) |
| 2abb9bc | C: power, west end |
| 91eebf9 | D (part): ADIN header signals |

Rebuild any phase: `sh scripts/stage3_routing/run.sh <A|B|C|D>` (takes the previous phase's committed board, runs the phase script,
DRC, lock check, project-file check). Phase E has no script: nothing was removed or added in clean-up.

## Phase A: bus trunks (top layer, no vias)

| Net | Width, length | Path (new frame) |
|---|---|---|
| BM2_P | 2.0 mm, 13.4 mm | from the end of Sofar's stub (18.181, 22.339): the frozen board's diagonal to x 15.63, south to y 27.455, 45 deg to x 17.475, south onto J9 pads 3-4 |
| BM2_N | 2.0 mm, 22.2 mm | L2 pad 2 -> (11.471, 17.224) -> (9.531, 19.164) -> south (the frozen board's path, 1:1) to y 24.891, 45 deg parallel to BM2_P's at 2.5 mm pitch, south onto J9 pads 1-2 |
| BM1_N | 1.2 mm for 14.3 mm, then 2.0 mm for 5.4 mm | L1 pad 2 -> 45 deg between L1's pads -> x 51.65 south to y 24.62 -> 45 deg to x 54.125 -> J10 pads 1-2 |
| BM1_P | 1.2 mm for 14.1 mm, then 2.0 mm for 5.4 mm; 0.2 mm tap link 1.9 mm | L1 pad 3 -> 45 deg -> x 53.2 south to y 23.95 -> 45 deg to x 56.625 -> J10 pads 3-4; Sofar's data-tap via (52.406, 18.614) joined to the trunk (the frozen board's link, shortened) |

DRC after A: 3 + 16 errors, 128 unconnected.

**Deviation from the brief: BM1_P does not go round the east of L1.** J5's pads (placed after the routing review) leave 1.27 mm
between L1 pad 4 and J5 pad 2 (both GND), on top of the 1.65 mm at the screw keep-out, so that path would be about 0.9 mm wide
for some 10 mm, beside the payload pads, and 10 mm longer than BM1_N. Instead both BM1 trunks pass between L1's pads
(4.01 mm apart; the review's third option for F3, which it had not trialled): **neck 1.2 mm for 14 mm on each**, 0.35 mm between
the two trunks, 0.2 mm or more to L1's pads and to Sofar's GND via at (50.53, 23.54); P and N are the same shape and length within 0.2 mm.
1.2 mm of 1 oz outer copper is above the 1.0 mm / 2.4 A figure of `power_budget.md` section 4 (0.89 A needed, D12).
BM1_N no longer follows the frozen board's 2.0 mm path under L1. Nick's call whether this stands.
Port 2 is not a mirror of port 1 (2.0 mm throughout, N west of L2 past the converter).
Trunks end 0.2 mm short of the pad centres (y 33.9) over both ganged pads; the two trunks of a port are 0.5 mm apart there.

## Phase B: planes

New zones, all named "S3 ...", settings copied from the frozen board's own added zones (clearance 0.3, min width 0.25, thermal spokes 0.5 / 0.3, priority 1):

| Zone | Layer | Filled |
|---|---|---|
| GND west / south / east | GND Plane | 927 mm2 after phase C; one U-shaped outline: west end, south strip, east end, SW / SE notches, NW / NE corners (J1 pins 6 and 39 now on the plane, thermal spokes; J4 pad 2, J5 pad 2 too) |
| 5V_PI west strip | PWR Plane | 152 mm2 (the fill under the converter that D47 had and the move lost) |
| PI_5V lane | PWR Plane | 69 mm2, J1 pins 2 / 4 to JP1 |
| H1..H4 screw keep-out | all six copper layers | r 3.0 mm; tracks, vias, pour not allowed (as on the frozen board) |

- The GND zone stays west of Sofar's west slot and east of the east slot; it does not bridge them.
- How it joins Sofar's plane: the outline reaches 0.3..0.8 mm into Sofar's GND zone; KiCad cuts Sofar's fill back to the new outline and the
  two fills abut. Measured by `zone_touch.py`: they meet when one is grown by 1 um. No stitching vias were added for this. **Sofar's zone
  outline is untouched, but its fill is 0.3..0.8 mm smaller along that edge** (the new zone's copper is there instead).
- Not done: 3V3 / VBUS pours; outer-layer ground pours; any pour in the channel (J1 already stands in Sofar's planes).
DRC after B: 3 + 16 errors, 120 unconnected.

## Phase C: power, west end

| Net | Layer, width, length | Vias | Current basis |
|---|---|---|---|
| 5V_PI | top 1.0 mm 2.1 mm; bottom 1.0 mm 11.3 mm, 0.6 mm 1.4 mm, 0.5 mm 2.9 mm, 0.3 mm 5.9 mm, 0.2 mm 1.4 mm; plus the PWR-plane strip | 6 new + the group's own | Pi <= 1 A (D15) + motor 0.5 A, 1.24 A limit. 1.0 mm outer = 2.4 A at 10 degC (`power_budget.md` s.4), the frozen board's width |
| PI_5V | bottom 0.6 mm 1.6 mm, then the PWR-plane lane | 2 | <= 1 A |
| VBUS (converter input) | Internal 2, 1.0 mm, 27.1 mm, y 7.1 | 0 (group's own via to Sofar's via at (29.981, 12.764)) | 0.56 A at 16 V for 1.5 A out (review S3). 0.5 oz inner: about 0.65 A at 10 degC (IPC-2221 inner formula, my arithmetic) |
| Net-(J4-Pin_1) | bottom 1.0 mm, 9.8 mm | 0 | frozen board's width |
| 5V_LIFEPO4 | Internal 2 0.8 mm 11.3 mm, bottom 0.8 mm 2.4 mm | 1 | 0.57 A (F1's part note). Frozen board: 1.0 mm top; here inner because F1's two pads face the wrong way round for a bottom route |
| GND (capacitor bank) | bottom 0.5 / 0.3 / 0.25 mm, 6.7 mm | 2 | one via per 22 uF; C61 and C60 return through C62's pad |

- The 5V_PI plane strip necks to 1.1 mm beside the H4 keep-out; the 1.0 mm bottom track (x 7.15, y 20.2..29.6) runs in parallel, two vias at each end. JP1 pad 2 and TP38 join it.
- The feed to the capacitor bank is 0.5 mm for 2.6 mm between the two 0805 columns (1.65 mm gap, shared with C61's ground return).
- U12 pin 9 (VIN) is fed by a 0.2 mm link from C61 (the pad is 0.2 mm wide).
DRC after C: 3 + 16 errors, 104 unconnected.

## Phase D (part): header signals

Eight nets, 0.2 mm, each one horizontal run in the channel (y 6.9..8.7, 0.4 mm pitch) with 45 deg corners, split over layers so none cross:

| Net (J1 pin) | Layer, length | Vias |
|---|---|---|
| ADIN_MISO (21), I2C0_SCL (28), I2C0_SDA (27) | top, 15.4 / 13.1 / 9.2 mm, onto Sofar's stubs at y 10.289 | 0 |
| ADIN_MOSI (19) | Internal 1, 20.3 mm | 0 |
| ~ADIN_INT (22) | Internal 1 19.1 mm + top 0.6 mm | 1 at (47.281, 9.7) |
| ADIN_SCK (23), ~ADIN_CS (24) | Internal 2, 14.1 / 18.4 mm, into Sofar's vias | 0 |
| ~ADIN_RST (18) | bottom, 29.3 mm | 1 at (52.706, 10.406), on Sofar's remaining Internal 1 track |

DRC after D: 3 + 16 errors, 96 unconnected.

## Not routed: 96 connections (`drc_final_recheck.json`), by net

- **Payload switch group, none of it**: VBUS (3: to U11, C49, R41), VBUS_OUT (3: D3, U11, J5, and Sofar's stub at R11 / C50 in the north),
  U11_RTN (6), PAYLOAD_EN (3), ~PAYLOAD_FAULT (2), Net-(U11-UVLO) (2), ISET (1), Net-(U11-dVdT) (1). Not started; no finding that it has no safe path.
- **Motor driver U12 except VIN**: MOTOR_OUT1 (2), MOTOR_OUT2 (2), MOTOR_IN1, MOTOR_IN2, MOTOR_nSLEEP, MOTOR_VISEN, Net-(U12-ISET), Net-(U12-V3P3), Net-(U12-VCC).
  The outputs need 1.24 A out of 0.2 mm wide pads and vias to J7; vias only fit north of y 32.9 or south of y 35.3 (J7's pads are above the capacitor row). Not designed.
- **ADC group**: 3V3 (4), POT_WIPER (3), I2C0_SDA / SCL south branch to U13, R26, R27 (2 + 2), ~ADC_ALERT (2), Net-(U13-ADDR).
- **Qwiic**: PI_3V3 (6, incl. J1 pin 1 to pin 17), I2C3_SDA (2), I2C3_SCL (2).
- **LEDs and straps**: ~ADIN_P1_LED1, ~ADIN_P2_LED1, Net-(D8-A), Net-(D9-A), Net-(D10-A), ADIN_LED_VDD (3), ADIN_VDDIO (3), CFG0_STRAP, CFG1_STRAP,
  Net-(U1A-P1_LED_0/SPI_CFG1) (2), ADIN_MISO to R9 (1), ADIN_TIMER (1).
- ADIN_PWR (2): J1 pin 16 to R43 and Sofar's via at (51.656, 7.164). The clear lanes in the channel on Internal 2 (y 7.65..7.8) and the bottom (y 8.5..8.95) are now used by ADIN_SCK and ~ADIN_RST.
- GND (21): pads of all the groups above, plus J1 pin 14's Sofar stub at (24.27, 6.73), R43, D8, J3, D3, TP24.

## Deviations and things to know

1. BM1 trunks under L1 at 1.2 mm (phase A, above).
2. PI_5V has no outer-layer copper in parallel with its PWR-plane lane. The lane is 1.7 mm wide with three 1.0..1.1 mm necks (at J1 pin 1 and past two
   of the converter's vias). By the IPC-2221 inner formula 1.1 mm of 0.5 oz carries about 0.95 A at 20 degC rise (my arithmetic, not measured). **This is the weakest power path on the board.**
3. Sofar's GND fill shrinks slightly where the new zone overlaps it (phase B).
4. VBUS to the converter uses 1.3 mm of the channel on Internal 2 from x 11.7 to 28.6.
5. Left as they were, still dangling: the converter group's own 0.7 mm VBUS stub on the bottom at (11.22, 10.19), and the north 4.2 mm of Sofar's ~ADIN_RST Internal 1 track above the new via.
6. The pre-check in `s3lib.py` treats Sofar's fills as obstacles; no new track or via cuts into one.
7. Layers: no signal on the GND or PWR plane layers. Vias are all 0.6 / 0.3 mm.

## Not checked

- Renders `final_top.png`, `final_bottom.png` and the six plots in `plots_final/` were written but not looked at. I looked at crops of: the BM trunks (top),
  the GND plane, the PWR plane west strip, the channel with the eight header nets.
- No ERC run, no QE review, no impedance or return-path check of the header nets, no thermal check beyond the arithmetic quoted.
- `view.sh` uses a measured scale factor for its crops; good for looking, not for measuring.

## Next session, first steps

1. Nick: accept or reject the BM1 route under L1, and say whether PI_5V needs a second path (item 2).
2. U12 fan-out (outputs first: they set where the vias go), then the three MOTOR control nets and MOTOR_VISEN from the header (Internal 2, per review S5).
3. Payload switch group in the south-east; then ADC group, Qwiic, LEDs and straps, ADIN_PWR; then the GND vias of each group.
4. Continue as `phaseD2.py` from commit 91eebf9 (add it to the `case` in `run.sh`); `probe.py` finds free straight runs.
