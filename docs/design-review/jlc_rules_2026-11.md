# JLC rule values and stackup for `nick_raw_routing` (2026-11-10)

*Decision D of the S9 routing run (Nick, 2026-11-10). Everything here is in **one commit**, titled
"nick_raw_routing: JLC rule values and stackup", so it can be rolled back on its own if Sofar's answers
(Q11 stackup, Q13 data-pair skew) change the picture.*

**Roll back:** `git log --oneline --grep="JLC rule values and stackup"` gives the commit; `git revert <that sha>`
restores every value in the "Before" column. No copper, footprint or zone is part of that commit.

**Sources**, read 2026-11-10 at 10:36 AM PT:
- limits: https://jlcpcb.com/capabilities/pcb-capabilities
- stackup: https://jlcpcb.com/impedance (6-layer, 1.6 mm, 1 oz outer, 0.5 oz inner, "JLC06161H-3313")

## Board setup constraints (`nick_raw_routing.kicad_pro`)

| Setting | Before | After | JLC, multilayer |
|---|---|---|---|
| `min_clearance` | 0 (not set) | 0.10 mm | 0.09 mm track spacing, 1 oz |
| `min_track_width` | 0 (not set) | 0.10 mm | 0.09 mm, 1 oz |
| `min_via_diameter` | 0.5 mm | 0.45 mm | min 0.25 mm; a 0.2 or 0.25 mm hole costs more only with a via under 0.45 mm |
| `min_through_hole_diameter` | 0.3 mm | 0.2 mm | min 0.15 mm, preferred min 0.2 mm |
| `min_hole_to_hole` | 0.25 mm | 0.2 mm | via hole to hole 0.2 mm |
| `min_silk_clearance` | 0 (not set) | 0.15 mm | pad to silkscreen 0.15 mm |
| `min_text_height` | 0.8 mm | 1.0 mm | 1.0 mm |
| `min_text_thickness` | 0.08 mm | 0.15 mm | line width 0.15 mm |
| `min_hole_clearance` | 0.25 mm | unchanged | via hole to track 0.2 mm |
| `min_copper_edge_clearance` | 0.5 mm | unchanged | 0.2 mm from routed edges |
| `min_via_annular_width` | 0.1 mm | unchanged | via diameter ≥ hole + 0.1 mm (ring 0.05 mm) |

The net class is unchanged: tracks 0.2 mm, clearance 0.127 mm, new vias 0.6 mm with a 0.3 mm hole.
Sofar's 81 vias of 0.45 mm / 0.2 mm hole and 28 of 0.6 mm / 0.254 mm hole stay as drawn (Nick: the 0.2 mm
vias near the ADIN are acceptable, larger vias elsewhere).

## Custom rules (`nick_raw_routing.kicad_dru`)

| Rule | Before | After | JLC |
|---|---|---|---|
| "JLC through-hole pad: hole to copper" (`hole_clearance`) | none | 0.3 mm | plated pad hole to track 0.28 mm (0.35 mm recommended); inner layers 0.3 mm |
| "JLC pad hole to pad hole" (`hole_to_hole`) | none | 0.45 mm | 0.45 mm |
| "BM data pairs matched" (skew ≤ 0.5 mm) | present | **unchanged** | not a JLC rule; fails on Sofar's own copper, see Sofar Q13 |

Both new rules were checked to bind: with exaggerated values on a scratch copy they raised 131 and 100 violations.

## Board file (`nick_raw_routing.kicad_pcb`, setup block only)

| Setting | Before | After | Source |
|---|---|---|---|
| Stackup | none in the file | JLC06161H-3313, below | JLC stackup page |
| Copper finish | not set | ENIG | JLC: HASL is not offered from 6 layers up |
| `solder_mask_min_width` | not set | 0.1 mm | JLC solder mask bridge 0.10 mm (0.13 mm for black or white) |

| Layer (board name) | Material | Thickness | εr |
|---|---|---|---|
| Top solder mask | | 0.01524 mm (0.6 mil over traces) | 3.8 |
| F.Cu (Top Layer) | copper, 1 oz | 0.035 mm | |
| dielectric 1 | prepreg 3313 | 0.0994 mm | 4.1 |
| In1.Cu (Internal 1) | copper, 0.5 oz | 0.0152 mm | |
| dielectric 2 | core | 0.55 mm | 4.6 |
| In2.Cu (GND Plane) | copper, 0.5 oz | 0.0152 mm | |
| dielectric 3 | prepreg 2116 | 0.1088 mm | 4.16 |
| In3.Cu (Internal 2) | copper, 0.5 oz | 0.0152 mm | |
| dielectric 4 | core | 0.55 mm | 4.6 |
| In4.Cu (PWR Plane) | copper, 0.5 oz | 0.0152 mm | |
| dielectric 5 | prepreg 3313 | 0.0994 mm | 4.1 |
| B.Cu (6 Bottom Layer) | copper, 1 oz | 0.035 mm | |
| Bottom solder mask | | 0.01524 mm | 3.8 |

Copper and dielectric add up to 1.538 mm; the board thickness setting stays at the nominal 1.6 mm.
The loss tangent in the file (0.02) is KiCad's default, not a JLC figure.

**Not known:** Sofar's own stackup (Q11 is unanswered). On this stackup Internal 1 is 0.55 mm from the GND plane
and 0.10 mm under the top copper; Internal 2 is 0.11 mm from the GND plane.

## Effect on DRC (zones refilled, `--severity-all`, same board)

| | Before (board's own rules) | After |
|---|---|---|
| Errors | 324 | 134 |
| Open connections | 63 | 63 |
| Schematic parity issues | 0 | 0 |

What is left: 110 at the four inserts (68 hole clearance, 38 solder mask bridge, 4 pad stack), 16 GND vias in the
keepout under U1 (the same 16 as on the mote; kept, Nick 2026-11-10), 3 skew (Q13), 3 courtyard overlaps,
2 shorts that later routing steps remove. Warnings went from 377 to 466, almost all silkscreen text now
measured against JLC's 1.0 mm / 0.15 mm.
