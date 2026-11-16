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
- Not placed (my reading of the approved mocks, not a typed decision): J2 breakout, J4 / F1 AUX 5 V, J6, TP36. JP1-JP4 stay.

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
4. Report, QE review, Nick's KiCad look.

## Open
- 5 V rail at 1.5 A: U10 about 0.82 W (reviewer's figure with `power_budget.md`'s method); MP6550 current-limit resistor.
- Motor driver and ADC part sizes are estimates until their footprints are on the board.
- Heights under the board against the Pi were not checked.
