# Experiment pi_zero_fit_01: the shield on a Pi Zero sized board

*Layout experiment under DESIGN D31: its own board in this folder, on branch `experiment/pi-zero-fit-01`, never merged.
The JLC board in `Nereus_Pi_Shield_Adin2111/` is frozen and is not touched. Owner and gate: Nick.*

## Goal (Nick, design session's chat, 2026-11-15)
Fit the latest board onto a Pi Zero footprint while Sofar's mote block stays as it is; show with high confidence what
can be achieved; rip up our own header / breakout routing and start again once the mote is in place.

## Decisions so far (all Nick, design session's chat, 2026-11-15, unless marked)
- Outline **65 x 39.5 mm**, 3 mm corners ("Sizes work"); it overhangs the Pi by 9.5 mm on the south. Pi Zero holes.
- Mote core: 81 footprints at Sofar's exact coordinates, with Sofar's copper. The outline is drawn around it:
  new frame = old board coordinates - (113.47, 89.34) mm.
- Threaded inserts MP1-MP4 go; each bus port gets a **JST GH 4-pin, 2 pins ganged per polarity**.
- All connectors on the **south wall, side entry** (a mated top-entry GH is 7.3 mm, the inductors 6.0 mm; reviewer's
  figures from JST drawings), west to east: MOTOR (GH 4), BM2 (GH 4, under L2), POT (GH 3), LEDs BM2 | ADIN | BM1,
  QWIIC (SH 4, the board's J3), BM1 (GH 4, under L1). Names on the silkscreen north of each connector.
- 5 V converter at the west end, **L6 on top** ("skyline"). Motor driver (MP6550, from the Urchin board) on the bottom,
  west; **runs from the 5 V rail**, 0.5 A steady, under 1 A spikes, rarely (Nick's bench figures). ADC (ADS1115, Urchin)
  near the pot connector. Payload load switch and its pads on the bottom; first thing to drop if it has no safe path.
- "Removing the conflict with the header is approved, as are updates to the schematic": five Sofar items at J1 pins 13
  and 35 are removed (listed by `scripts/build_stage1.py` when it runs).
- JLC's rules for the 6-layer board apply (project rule set and stackup JLC06161H-3313, DESIGN D34).
- Not placed (my reading of the approved mocks, not a typed decision): J2 breakout, J6, TP36. JP1-JP4 stay.

## Decisions after the first placed board (Nick, design session's chat, 2026-11-15, evening)
- 5 V converter: "keep it as close to how it is ... similar to how Sofar did their layout": it moves as one rigid group
  with its own copper (`build_stage1.py` section 5).
- "keep the connectors and LEDs as they are"; AUX 5 V on the west side, "large copper pads on the bottom unless a pair of
  smaller thru holes oblong pads will fit": a smaller through-hole pair fits (J4: 2.2 x 3.3 mm, 1.1 mm drill, 3.2 mm pitch,
  +5 V at the west edge, GND inboard). Payload pads J5 in the east with the load switch. J4, F1 and JP1 stay in the schematic.
- Motor current limit: "4.02 k, so we don't clip - it's transient" (R48 = 4.02 kOhm, about 1.24 A by the MP6550 formula
  the schematic stage cited).
- I2C, settled: "ADC and power monitor on I2C0, how I have the load monitor in the frozen board. Then I2C1 is for the
  LiFepo4+ board". U13 (ADS1115) shares I2C0 (J1 pins 27 / 28) with U4 (INA232) and R26 / R27; J1 pins 3 / 5 (I2C1)
  stay unconnected for the LiFePO4+ board; I2C3 is for the Qwiic connector only. No schematic change from stage 2.
- Pot: a 100 kOhm pull-down from the wiper to GND, plus an unfitted 0.1 uF footprint. Source: the session "Builder:
  urchin board bring-up" (its reply of 2026-11-15: the pot has a dead zone of about 30 degrees where the wiper is open and
  the input floats 0.08 to 1.22 V; cam02 bench, UrchinCam PR 1 `bringup/WIPER_BENCH.md`). Untested; Nick tests it.
- "When possible please reuse vetted part footprints": new passives take footprints and parts already on this board
  or the Urchin.
- JLC's rules for the 6-layer board apply to everything.
- Routing style: "keep the trace routing like a human would do, not organic zig zags but more straight lines when
  possible": few long segments on 0 / 45 / 90 degrees, related nets parallel; a path-finder's raw output never goes
  on the board as it is.

## Evidence (outside git): `~/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/`
Mocks v1-v9, `PLACEMENT_SPEC_G.md`, reviews `review_G_placement.md` (FITS WITH CHANGES) and `review_G_routing.md`
(ROUTABLE WITH CHANGES, about 80 % after changes; trial router on a scratch board, no DRC), `stage1_scratch/`.

## Stages
1. **Geometry and placement** - `scripts/build_stage1.py` (done on a scratch copy outside the repo, 2026-11-15, because
   KiCad was open): outline, core kept, our copper removed, kept parts placed, connectors as library footprints with no
   nets. DRC under the project's JLC rules: errors = the 3 skew + 16 keep-out vias the frozen board also carries; no
   courtyard, edge or short error. 103 unconnected (expected, nothing routed).
2. **Schematic** - add MP6550, ADS1115, the four connectors; remove inserts, J2, J4, F1, J6; then board parity.
3. **Routing** - bus trunks first (BM2_N path past the 5 V converter; BM1_P neck of about 1.25 mm at the south-east
   hole), then the header fan-out through the 2.5 mm channel, then power.
4. Two independent reviews of the routed board (issues, errors, JLC rule compliance), fixes, then the design is posted
   for Nick's inspection (Nick, design session's chat, 2026-11-15: "pass the final design through two reviewers and
   check for issues, errors, and alignment with the JLC DRC before posting the final designs").

## Open
- 5 V rail at 1.5 A: U10 about 0.82 W (reviewer's figure with `power_budget.md`'s method); MP6550 current-limit resistor.
- Motor driver and ADC part sizes are estimates until their footprints are on the board.
- Heights under the board against the Pi were not checked.
