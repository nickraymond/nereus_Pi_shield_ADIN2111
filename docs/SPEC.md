# SPEC.md — nereus_Pi_shield_ADIN2111

*What Nick wants. Stable reference — agents skim this; changes require Nick's approval.*
*Last updated: 2026-10-04*

## Goal

A Raspberry Pi Zero 2W shield made from a copy of the Sofar Bristlemouth mote
(000639-AB): ADIN2111 two-port 10BASE-T1L with PoDL, powered from the bus,
5 V for the Pi, a 24 V payload port, and a **50 W nominal power path at 24 V**.
Done = a design-review package in `docs/design-review/` that Nick can review
with colleagues: ERC clean (or every item justified), kept nets matching the
mote's copper, every new net listed, schematic PDF, change log, BOM changes,
and open questions with datasheet citations. Nick owns layout from there.

## Background

The mote design was imported from Altium. The import left pins touching wire
midpoints unconnected; a 33-junction fix (`Archive/shield_junction_fix.zip`)
is applied. The STM32 processor and USB go away; the Pi drives the ADIN2111
over SPI. The commercial mote's PoDL magnetics limit it to ~20 W, so reaching
50 W means re-selecting the inductors and re-rating the whole power path
(see `docs/POWER_PATH.md`).

## Inventory / environment

| Item | Location | Role |
|---|---|---|
| Live KiCad project | `nereus_Pi_shield_ADIN2111/` (S0.1 renames it from `nereus_Pi_shield_ADIN2111_002/`) | The design. The only thing agents edit. |
| Mote reference | `KiCAD_reference_designs/20250409_BM_Mote_000639-AB/` | Its `.kicad_pcb` copper is the truth for kept nets. Read-only. |
| UrchinCam | `KiCAD_reference_designs/UrchinCam-main/` | Prior art for a Pi shield. Read-only. |
| Archive | `Archive/` | Earlier iterations and the junction fix. Read-only. |
| KiCad 9.0.6 + kicad-cli | `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli` | ERC, netlist export, PDF export |
| Checklist | `pi-shield-checklist.html` | Nick's visual walkthrough. Reference only; TRACKER.md holds progress. |
| Sofar 50 W/100 W guide | [Component Selection & Circuit Design Guide](https://manual.sofarocean.com/50W-100W-Bristlemouth-Mote-Component-Selection-Circuit-Design-Guide-f78b6124579340ba88ac8631a784dd88) | Inductor and power-path selection (from Evan) |
| Sofar BM power roadmap | [Bristlemouth Evolution — More Power Delivery](https://manual.sofarocean.com/bristlemouth-evolution-more-power-delivery) | Context, Jetpack and Dev Kit precedents (from Evan) |

## Confirmed facts (verified, with sources)

- kicad-cli 9.0.6 is installed at the path above. *(measured 2026-10-04)*
- PoDL magnetics today are L1 and L2, both Bourns SRF1260-101M.
  *(`BM_Mote_1_PoDL.kicad_sch`)*
- The 3.3 V buck is U5, an LMR51430YDDCR; the load switch is U9, an FPF2700MX;
  R34 is 374 kΩ (RC0402FR-07374KL); R11 is a 0 Ω 1210 jumper; the R8 shunt is
  a UR73D1JTTD10L0F. *(live schematic sheets)*
- The commercial mote's absolute maximum BM current is 890 mA (~20 W),
  limited by its PoDL inductors, and it has no through-current protection.
  *(Sofar, More Power Delivery)*
- Bristlemouth v1 spec: a module draws ≤ 12 W from a nominal 24 V bus and must
  run from 16 V to 32 V. *(Sofar, More Power Delivery)*
- 50 W is 2.083 A at 24 V and 3.125 A at 16 V. *(arithmetic; matches the Sofar guide)*

## Safety / hard constraints (non-negotiable)

1. Agents never write any `.kicad_pcb`. Reading it is fine (for net checks
   and footprint extraction). Board, layout and routing belong to Nick.
2. KiCad stays closed while an agent edits project files. The agent confirms
   this with Nick before its first edit of each session.
3. Every net the design keeps must match the mote's copper, proven by a
   netlist diff, not by eye.
4. Never connect the Pi's 3.3 V pins (1, 17) to the shield's 3.3 V.
5. Every part value, pin number and rating carries a datasheet citation. No
   citation, no part: it goes in Open questions instead.
6. `KiCAD_reference_designs/` and `Archive/` are read-only.
7. No power-path part is chosen until it has been checked against the 50 W
   rating defined in `docs/POWER_PATH.md` §1.

## Success criteria by sprint

See TRACKER.md — every sprint ends with a demo Nick can run.

## Non-goals (this project)

- Board outline, placement, routing, fabrication outputs (Nick)
- Firmware or Pi software, beyond documenting the ADIN power-up order
- A 100 W variant; a Bristlemouth power-delivery protocol
- HAT ID EEPROM
- The shared nereus-lib (icebox)

## Open questions (flag, don't guess)

- Is R11 fitted? (0 Ω across the load switch; fitted means always on.) — Nick to ask
- Why does the mezzanine side control the load switch? — Nick to ask
- What current limit does R34 set on U9? — Nick to ask, and the agent checks the FPF2700 datasheet
- What exactly does "50 W" cover: port-to-port pass-through, the payload port, or
  both? At what minimum local voltage? — Nick (POWER_PATH.md §1)
- Do two MSD1514-class inductors (15.5 × 15.5 × 14.2 mm each) fit a Pi
  Zero-sized board? — Nick (layout)
- Which inductor does the 5 V converter need at 24 V in? (The 3.3 V U5 uses
  PA5432.822NLT as L3.) — S4
- Bus power budget: shield + Pi + payload against the 50 W path — S4/S5
