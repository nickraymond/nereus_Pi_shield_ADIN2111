# Pi Zero Shield ADIN2111, side-entry connectors

Branch `pi-zero-side-entry`. A 65 x 39.5 mm, 6-layer Raspberry Pi Zero shield: Sofar's Bristlemouth mote core
(ADIN2111, PoDL power), a 5 V converter for the Pi, an MP6550 motor driver, an ADS1115 ADC, JST GH side-entry
connectors on the south wall and a pad row for spare Pi pins.

**Status (2026-11-17):** sent to M for review. `main` becomes this board when the review is closed and Nick
releases it by pull request.

## Open it

Open `Pi_Zero_Shield_ADIN2111/Nereus_Pi_Shield_Adin2111.kicad_pro` in KiCad 10. The `.kicad_pro` and `.kicad_dru`
carry the JLC rules: keep them beside the board file. The developer spec (power, I/O, I2C addresses) is on the
schematic's cover page.

## What is in this branch

Only the files this board needs: the KiCad project, its libraries (`*.pretty`, `*.kicad_sym`, the lib tables) and
the STEP model. Everything else (decision log, power budget, JLC rule record, reviews, scripts, reference designs,
the other boards) is on the `development` branch.

## Other branches

- `pi-full`: the full-size Pi shield, frozen and ordered at JLC.
- `pi-zero-top-entry-incomplete`: a stopped top-entry connector variant. Do not build.
- `development`: references, docs, tools and the history of how these boards were made.
