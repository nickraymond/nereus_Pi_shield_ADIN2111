# Pi Shield ADIN2111, Pi Zero variant (pi_zero_fit_01): hand-over for review

Prepared 2026-11-16, 12:50 PM Pacific, from commit **793c97c** (branch `experiment/pi-zero-fit-01`), read-only. KiCad 10.0.7.

## What it is and how to open it

A 6-layer, 65 x 39.5 mm Raspberry Pi Zero shield: Sofar's Bristlemouth mote core (ADIN2111 two-port 10BASE-T1L, power, PoDL) carried
over from the parent board `Nereus_Pi_Shield_Adin2111/`, plus an MP6550 motor driver (U12), an ADS1115 ADC (U13), four JST GH connectors
(J7-J10) in place of the threaded bus inserts, and a bare pad row (J15-J19) for spare Pi pins. JLC fabricates and assembles it.

Open `experiments/pi_zero_fit_01/board/Nereus_Pi_Shield_Adin2111.kicad_pro`. **Keep the `.kicad_pro` and `.kicad_dru` beside the
`.kicad_pcb`**: without them KiCad falls back to default rules and shows several hundred false errors (the audit counted 424 clearance,
68 drill, 68 via, 40 track width, 14 hole-in-courtyard and 16 un-excluded keep-out items).

## DRC / ERC (fresh: `reports/drc.json`, `drc.rpt`, `erc.json`, `erc.rpt`)

DRC with zone refill and schematic parity: **3 errors, 16 excluded errors, 0 unconnected, 0 parity, 641 warnings.**

- Inherited from the Altium-imported mote block:
  - 16 `items_not_allowed` (excluded with comments): the 16 GND vias under U1 sit in rule area `NoConnect_Pwr_MCU` on the PWR plane, an
    imported plane cut-out that became a "no vias" area. Same 16 vias on the parent and on Sofar's board.
  - 3 `skew_out_of_range`: the project's own rule "BM data pairs matched" (0.5 mm) applied to Sofar's imported data-pair copper
    (BM1_DATA_N 8.41, BM1_DATA_P 9.75, BM2_DATA_P 18.42 against BM2_DATA_N 21.53 mm). Left as is pending Sofar (Q13).
  - Inherited warnings (objects from Sofar's file): lib_footprint_mismatch 92, text_thickness 78, text_height 84, padstack 32,
    silk_over_copper 50, silk_overlap 6, isolated_copper 3 (no-net fills), via_dangling 4 and track_dangling 6 (Sofar's copper; 3 vias and
    the 6 stubs lost their second connection through our edits), nonmirrored text 1.
- Ours: **warnings only**: lib_footprint_mismatch 18, text_thickness 121, text_height 73, silk_over_copper 60, silk_overlap 7, padstack 5,
  nonmirrored text 1. All cosmetic or library bookkeeping: TrueType text KiCad cannot measure, texts of 0.7-0.8 mm under JLC's 1.0 mm,
  outlines clipped by pad openings (JLC removes silk from pads), no paste on test points (intended).
  The inherited / ours split is the rule audit's per-object triage (stage 13, commit 16dbac5); today's counts per type equal that triage
  plus the 102 silk-over-pad lines of the pad-to-silkscreen rule added since. Not re-triaged item by item at 793c97c.

ERC: 39 items (12 pin_not_connected, 5 power_pin_not_driven, 11 multiple_net_names, 7 unconnected_wire_endpoint, 2 lib_symbol_mismatch,
1 same_local_global_label, 1 endpoint_off_grid); item for item the parent's 39 (re-review A).

## JLC rule audit (stage 13, 2026-11-16)

1. Verified against JLC's capability pages today: track / spacing, pad-to-track, via size and ring, hole-to-hole, PTH / NPTH hole to copper,
   edge clearance, text size, thickness, copper weights, ENIG, the JLC06161H-3313 stackup.
2. Added 2026-11-16 (in the frozen files): PTH annular ring 0.2, NPTH and plated pad hole size 0.5-6.3, SMD pad to SMD pad 0.15, pad to
   silkscreen 0.15, mask to copper 0.09, hole_to_hole raised to error.
3. KiCad cannot check: minimum SMD pad size (U12's pads are 0.204 mm wide against JLC's stated 0.25 mm; the footprint's pads equal the
   Urchin board's U1 (`stage4_review/electrical/REVIEW_ELECTRICAL.md`), and the owner states JLC built the Urchin board: his statement,
   not verified here), silkscreen graphic line widths, same-net spacing.
4. No spacing, width, ring or hole violation exists in the project's own copper, before or after the new rules.

## Open items for the reviewer (each checked on 793c97c today; figures in `work/open_items_raw.txt`)

Coordinates in the board frame minus (113.47, 89.34).

| Item | State at 793c97c |
|---|---|
| Vias in / at pads, and the via-fill order option | Board file: all vias tented, filling and capping "no". Holes inside pads: F1 pad 1 (5V_LIFEPO4, 4.267, 15.887; the second F1 via now 0.375 mm off the pad, stage 12), U11 pad 11 (47.3, 35.3), 16 GND vias in U1's exposed pad (Sofar's). Within 0.1 mm of a pad: C61 pad 2 0.017 mm, C57 pad 1 0.078 / 0.092 mm. Fill / cap choice on the order form: not recorded |
| Single vias on U12 supply and ground | Open: 5V_PI one via (8.05, 37.9), GND two near U12 (5.15, 36.75) and C61's (8.0, 36.25) |
| PWM pair over a GND-plane slot | Open: MOTOR_IN1 / IN2 run on Internal 2 along the north edge across the west GND-plane slot (no GND copper at x 17.3..18.2, y 0..3) |
| 1.0 mm neck in the VBUS feed | Open: Internal 2, 1.5 mm for 18.8 mm then 1.0 mm for 7.0 mm (x 19.7..25.6); re-review: 0.65 A at 10 degC rise, need 0.53-0.79 A |
| Converter heat | Bench check still open (no file change can close it) |
| Pad row next to the Pi header | 0.438 mm copper from J15-J19 pads to J1 pads, top and bottom (J15.1 PI_5V next to J1 pin 3); J1's body over the row's bottom rings: pins soldered from the top only |
| Dangling stubs on imported copper | Open: 6 track stubs, 4 vias (DRC list in `reports/drc.rpt`); owner's word needed to remove Sofar's copper |
| No-net fill tip on the PWR plane | Present: `NoConnect_Right` piece of 0.171 mm2 at (53.22..53.67, 5.75..6.28), in the gerbers (fresh refill equals stored fill) |

## Package (outside git, on the owner's machine: folder `stage15_fab_package/`)

- `Nereus_Pi_Shield_Adin2111_pi_zero_fit_01_793c97c_gerbers_drill.zip` (13 gerbers, job file, PTH + NPTH drill)
- `gerbers/`, `drill/` (with PDF drill maps)
- `assembly/..._bom.csv`, `..._positions.csv` (KiCad format, fitted parts), `..._cpl_jlc_columns.csv`
- `reports/drc.json`, `drc.rpt`, `erc.json`, `erc.rpt`, `schematic.pdf`
- `BOM_CHECK.md`, `FAB_CHECK.md`, this file; `src/` (the design at 793c97c); `work/` (raw script output, parent copy)
