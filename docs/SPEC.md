# SPEC.md — nereus_Pi_shield_ADIN2111

*What Nick wants. Stable reference — agents skim this; changes require Nick's approval.*
*Last updated: 2026-10-04*

## Goal

A Raspberry Pi Zero 2W shield made from a copy of the Sofar Bristlemouth mote
(000639-AB): ADIN2111 two-port 10BASE-T1L with PoDL, powered from the bus,
5 V for the Pi, a 24 V payload port, and a **~50 W power path (absolute max at
24 V, defined like Sofar's 20 W mote rating)**, fully potted.
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
| Live KiCad project | `nereus_Pi_shield_ADIN2111/` (renamed from `_002` in S0.1) | The design. The only thing agents edit. |
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
- SRF1260-101M in series mode: 400 µH, Irms 0.892 A (40 °C rise), Isat 1.1 A
  (30 % drop), DCR 0.656 Ω max. That's where the mote's 20 W comes from.
  *(Bourns SRF1260 datasheet)*
- C22 and C23 are EEEFT1H470AP 47 µF/50 V aluminium electrolytics in the PoDL
  damping network. *(`BM_Mote_1_PoDL.kicad_sch`)*
- There is no fuse, PTC or e-fuse anywhere in the schematic.
  *(live schematic sheets, 2026-10-04)*
- kicad-cli ERC output isn't deterministic: two runs on the same file can name
  different example labels for the same violation. Compare ERC by counts and
  types, and do net checks on the exported netlist. *(measured 2026-10-04)*

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
7. No power-path part is chosen until it has been checked against the ~50 W
   absolute-max rating (2.083 A at 24 V) defined in `docs/POWER_PATH.md` §1.
8. **The electronics are potted.** Parts kept from the Sofar mote design are
   vetted and stay as they are, unchanged (e.g. C22/C23). These rules apply
   only to **newly sourced** parts *(Nick, 2026-10-04)*:
   - **No aluminium electrolytic capacitors.** *(Nick, 2026-10-04)*
   - **No PPTC resettable fuses**; their trip behaviour changes when
     encapsulated. *(Sofar 50W/100W guide)*
   - Flag for Nick: any part with internal voids, vents or moving parts
     (trimmers, switches, relays); large MLCCs (1210 and up; prefer
     flexible-termination parts); ferrite magnetics (check vendor potting
     guidance).
   - Thermal ratings assume free air; potted parts need derating.
     *(Sofar 50W/100W guide)*

## Success criteria by sprint

See TRACKER.md — every sprint ends with a demo Nick can run.

## Non-goals (this project)

- Board outline, placement, routing, fabrication outputs (Nick)
- Firmware or Pi software, beyond documenting the ADIN power-up order
- A 100 W variant; a Bristlemouth power-delivery protocol
- HAT ID EEPROM
- The shared nereus-lib (icebox)

## Open questions (flag, don't guess)

- Questions for Sofar (R11, R34/U9, mezzanine control, e-fuse, …) live in
  `docs/SOFAR_QUESTIONS.md`.
- Do two MSD1514-class inductors (15.5 × 15.5 × 14.2 mm each) fit a Pi
  Zero-sized board? — Nick, SolidWorks check 2026-10-05
- What is the FPF2700's current-limit range? (The onsemi datasheet link was
  dead on 2026-10-04.) — S3
- Which inductor does the 5 V converter need at 24 V in? (The 3.3 V U5 uses
  PA5432.822NLT as L3.) — S4
- Bus power budget: shield + Pi + payload against the 50 W path — S4/S5
