# Pi Full Shield ADIN2111 (full-size Raspberry Pi form factor)

Branch `pi-full`. The 65 x 56 mm, 6-layer Raspberry Pi shield with Sofar's Bristlemouth mote core (ADIN2111, PoDL
power) and a 5 V converter for the Pi. This is the board that was frozen on 2026-11-11 and ordered at JLC
(decision D57 in `docs/DESIGN.md` on the `development` branch). The files are unchanged from that state; only the
folder was renamed.

## Open it

Open `Pi_Full_Shield_ADIN2111/Nereus_Pi_Shield_Adin2111.kicad_pro` in KiCad 10. Keep the `.kicad_pro` and
`.kicad_dru` beside the board file: they carry the JLC rules.

## What is in this branch

Only the files this board needs: the KiCad project, its libraries (`*.pretty`, `*.kicad_sym`, the lib tables) and
the two outline DXFs. The decision log, power budget, BOM and purchase records, reviews, scripts and reference
designs are on the `development` branch.

## Other branches

- `pi-zero-side-entry`: the Pi Zero-size shield with motor driver and ADC (in review).
- `pi-zero-top-entry-incomplete`: a stopped top-entry connector variant. Do not build.
- `development`: references, docs, tools and the history of how these boards were made.
