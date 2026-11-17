# Top-entry connector variant: INCOMPLETE, do not build

Branch `design/pi-zero-top-entry`. Status on 2026-11-17: **stopped by Nick** ("stop here, side mount is fine for this
version. We need to ship."). The design that went to M for review is the side-entry board on `design/pi-zero`.

**This branch is a work in progress and is not a buildable variant.** One of the five south-wall connectors is
top-entry here (J9, BM2); the other four are still side-entry. Do not order boards from this branch.

## What was asked

A copy of the Pi Zero shield in which the only difference is that the five JST connectors on the south wall
(J7 MOTOR, J9 BM2, J8 POT, J3 QWIIC, J10 BM1) are top-entry (vertical) parts, pin 1 west as on the side-entry board.

## What is on this branch

- Base: Nick's commit `4676018` on `design/pi-zero` (side-entry, DRC 3 skew + 16 keep-out errors inherited,
  0 unconnected, parity 0, ERC 0 errors).
- Commit `28539b4`: **J9 only** changed to `JST_GH_BM04B-GHS-TBT_1x04-1MP_P1.25mm_Vertical` at (16.375, 36.15) in the
  board frame minus (113.47, 89.34), 0.15 mm east of the old place to clear the CFG0_STRAP via. BM2_N / BM2_P re-routed
  on the top layer (2.0 mm, BM2_N necked to 1.4 mm for about 4.5 mm). Checks at that commit: DRC and ERC as the base,
  every other footprint, track and zone identical (`scripts/stage21_top_entry/lock21.py`).
- Scripts and the fit search: `scripts/stage21_top_entry/` (`fit21.py` prints why each connector does not fit).
- Blocker plots (outside git): `~/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/stage21_top_entry/`
  (`blockers_J7.png`, `blockers_J8.png`, `blockers_J3_J10.png`, `blockers_J10_zoom.png`).

## Why it stopped

The south strip was laid out around side-entry connectors. Their signal pads sit north of the body and the board
under the body is free, so the routing put vias there. The stock top-entry footprints (rotation 0, pin 1 west) put
the signal pads south of the body, on that same area.

| Connector | Result | What blocks it |
|---|---|---|
| J9 BM2 | done | - |
| J8 POT | feasible, not built | shift +0.25 mm in x; move C65's GND via (28.6, 33.3) to (28.6, 32.9); short jogs |
| J3 QWIIC | feasible, not built | shift -0.05 mm; move the VBUS via (44.5, 37.45) with its Internal 1 run and the I2C3_SCL via (43.7, 36.38); reorder the GND / PI_3V3 lanes |
| J7 MOTOR | does not fit | the motor driver U12 is under it on the bottom; its vias MOTOR_nSLEEP (4.4, 38.62), MOTOR_IN2 (7.0, 38.0), 5V_PI (8.05, 37.9) land on the new pad row, MOTOR_IN1 (3.7, 38.2) is 0.275 mm from pad 1, both MOTOR_OUT1 vias and SPI_CFG1 (10.85, 33.8) are on the mounting pads |
| J10 BM1 | does not fit | new pads and the two BM1 trunks land on the via column of R41 / R42 at x 55.5 (UVLO, VBUS, GND, PAYLOAD_EN) and on R36's UVLO via (53.6, 38.07); U11_RTN via (51.9, 35.4) is on the west mounting pad |

All blocking vias are the experiment's own (none is on the stage-2c board of commit d30920b), so none of Sofar's
copper is involved. A shift of up to 1.0 mm in x or 1.5 mm north does not clear J7 or J10.

## Parts (JLC, read 2026-11-17 on jlcpcb.com; quantity not read, the part pages show "In Stock")

| Connector | Part | LCSC |
|---|---|---|
| GH 4-pin vertical (J7, J9, J10) | BM04B-GHS-TBT(LF)(SN) | C161692 |
| GH 3-pin vertical (J8) | BM03B-GHS-TBT(LF)(SN) | C161691 |
| SH 4-pin vertical (J3) | BM04B-SRSS-TB(LF)(SN) | C160390 |

J9's `PLANNED LCSC` field is empty on this branch (it was cleared before these numbers were found): fill C161692
when the work resumes.

Height: JLC's listing gives 4.05 mm for the GH vertical header alone. The mated height with a plug was not
confirmed (JST's drawing could not be read); an early estimate in this project was about 7.3 mm, against about
6.0 mm for the port inductors L1 / L2. Confirm it against the enclosure before committing to top entry.

## Suggested next steps, if the variant is taken up again

1. Decide first whether top entry is needed (enclosure, cable routing) and confirm the mated height from JST's
   drawing.
2. Treat it as a re-layout of the south strip, not a part swap. Start from `design/pi-zero` as approved by M, not
   from this branch's state, unless nothing changed in between.
3. Re-plan U12's breakout so its control and supply vias come up north of J7's pad row (or move U12 about 2 mm
   north on the bottom), then fit J7.
4. Re-place the load switch's support parts R36, R41, R42 and their vias clear of J10's pads and the BM1 trunks;
   accept a BM1 neck of about 1.2 to 1.4 mm for about 4 mm, or move J10 west and re-space the LED group.
5. Build J8 and J3 as described in the table.
6. Alternative worth checking before any of the above: a top-entry footprint whose signal pads are north of the
   body with pin 1 still west (a mirrored land pattern does not exist for these parts, so this means rotating the
   connector 180 degrees and reversing the pin order in the cable, which changes the cable pinout). Only if a
   different cable is acceptable.
7. After the layout: fill the three LCSC numbers above, re-run DRC with parity and ERC, re-place the connector
   labels, and have the south strip reviewed (BM1 / BM2 trunk widths, the motor driver's vias, the payload switch).

## Sources

The fit results and via positions are from the stage-21 pass's own checks on commit `4676018`
(`scripts/stage21_top_entry/fit21.py`, `LOG.md` stage 21). The part numbers are from JLC's part pages read on
2026-11-17. The J8 / J3 fixes and the J7 / J10 remedies are proposals: none was built or checked.
