# SPEC.md — nereus_Pi_shield_ADIN2111

*What Nick wants. Stable reference — agents skim this; changes require Nick's approval.*
*Last updated: 2026-10-05*

## Goal

A Raspberry Pi Zero 2W shield made from a copy of the Sofar Bristlemouth mote
(000639-AB): ADIN2111 two-port 10BASE-T1L with PoDL, powered from the bus,
5 V for the Pi, a 24 V payload port, and **the mote's power path kept exactly
as Sofar built it: ~20 W absolute max (890 mA per port inductor at 24 V)**,
fully potted. This first board is a new layout of Sofar's vetted hardware; 50 W
waits for a later revision (DESIGN D12).
Done = a design-review package in `docs/design-review/` that Nick can review
with colleagues: ERC clean (or every item justified), kept nets matching the
mote's copper, every new net listed, schematic PDF, change log, BOM changes,
and open questions with datasheet citations. Nick owns layout from there.

## Background

The mote design was imported from Altium. The import left pins touching wire
midpoints unconnected; a 33-junction fix (`Archive/shield_junction_fix.zip`)
is applied. The STM32 processor and USB go away; the Pi drives the ADIN2111
over SPI. The commercial mote's PoDL magnetics limit it to ~20 W. Reaching
50 W means re-selecting the inductors and re-rating the whole power path; that
trade study is in `docs/POWER_PATH.md`, deferred until after this board is in
production (DESIGN D12).

## Inventory / environment

| Item | Location | Role |
|---|---|---|
| Live KiCad project | `nereus_Pi_shield_ADIN2111/` (renamed from `_002` in S0.1) | The design. The only thing agents edit. |
| Mote reference | `KiCAD_reference_designs/20250409_BM_Mote_000639-AB/` | Its `.kicad_pcb` copper is the truth for kept nets. Read-only. |
| UrchinCam | `KiCAD_reference_designs/UrchinCam-main/` | Prior art for a Pi shield. Read-only. |
| Archive | `Archive/` | Earlier iterations and the junction fix. Read-only. |
| KiCad 9.0.6 + kicad-cli | `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli` | ERC, netlist export, PDF export |
| Checklist | `pi-shield-checklist.html` | Shared visual view of TRACKER.md; agents keep it in sync. |
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
- LMR51430YDDCR (U5, U10) is the 1.1 MHz PFM variant; VIN 4.5–36 V, absolute
  max 38 V; VREF 0.591 / 0.6 / 0.609 V; 70 ns minimum on-time; 5 V example uses
  RFBT 100 kΩ / RFBB 13.7 kΩ. *(TI LMR51430 datasheet SLUSEF4A, §1, §5, §7.1,
  §7.5, §9.2.2.2)*
- PA5432.822NLT (L3, L6): 8.2 µH ±20 %, Isat 8.4 A (~30 % drop), heating current
  8 A (ΔT ≈ 40 °C), DCR 24.0 / 26.4 mΩ typ/max, composite, −55 to +155 °C.
  *(Pulse P890.B, 01/22)*
- GRM21BR61C226ME44 (C56, C57): 22 µF ±20 %, 16 V, X5R, 0805; GRM155R61A475MEAA
  (C58): 4.7 µF ±20 %, 10 V, X5R, 0402; both in production. *(Murata product
  pages, read 2026-10-05)*
- RC0402FR-0713K7L (R38): Yageo 13.7 kΩ ±1 %, 1/16 W, 0402, thick film.
  *(Digi-Key product listing 311-13.7KLRCT-ND, 2026-10-05)*
- TI's own LMR51430 application circuit uses C_IN = 2.2 µF and, at 1.1 MHz,
  suggests L = 3.3 µH (5 V) / 2.2 µH (3.3 V) with 2 × 10 µF / 25 V output caps.
  *(SLUSEF4A Figure 9-1, Table 9-2)*
- There is no fuse, PTC or e-fuse anywhere in the schematic.
  *(live schematic sheets, 2026-10-04)*
- The Altium import breaks connectivity: the untouched reference mote
  schematic shows 38 opens against its own copper. Our project, with the
  junction fix, still shows 26. *(tools/netcheck.py, 2026-10-05)*
- In KiCad 9.0.6, a pin whose end sits mid-wire is unconnected, and a junction
  loaded from file at that point connects the pin but can disconnect a
  neighbouring pin on the same wire. Splitting the wire at the pin works.
  *(measured one junction at a time, 2026-10-05)*
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
7. The power path stays exactly as in the Sofar mote: no part in it (L1/L2,
   D1–D3, U9/R34/R11, R8, C22/C23/R15/R16, …) changes value or part number.
   The rating is the mote's: ~20 W absolute max = 890 mA per port inductor at
   24 V *(Sofar, More Power Delivery)*; anything new on the bus (the S4 5 V
   converter, the payload connector) is checked against it. *(Nick, 2026-10-05; DESIGN D12)*
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
- A 50 W power path on this board (deferred to a later revision, DESIGN D12)
- A 100 W variant; a Bristlemouth power-delivery protocol
- HAT ID EEPROM
- The shared nereus-lib (icebox)

## Open questions (flag, don't guess)

- Questions for Sofar (R11, R34/U9, mezzanine control, e-fuse, …) live in
  `docs/SOFAR_QUESTIONS.md`.
- What is the FPF2700's current-limit range? (The onsemi datasheet link was
  dead on 2026-10-04.) — S4/S5 power budget; SOFAR_QUESTIONS Q3
- Effective capacitance of C56/C57 (GRM21BR61C226ME44) at 5 V DC bias. Murata's
  SimSurfing tool needs its licence accepted first, so it's unmeasured; TI's
  Eq. 14 wants ≥ 22 µF effective (≈ 1.5 A step, 5 %). — S4.c / S6 (Nick or a
  datasheet curve)
- U10's input caps copy U5's 2.2 µF (C55) + 100 nF. TI's text suggests ≥ 4.7 µF
  (SLUSEF4A §9.2.2.6), though its own Figure 9-1 uses 2.2 µF; field-proven on
  U5, but U10 draws more input current. — S6 review
- Does JP1's 1.0 mm copper bridge (1 oz assumed; Nick's stack-up decides) carry the
  Pi's maximum 5 V current with margin? Check against IPC-2221 trace-current data,
  with the Pi's current from Raspberry Pi's documentation. — S4.c
- The Pi Zero 2 W's undervoltage threshold, from a primary Raspberry Pi source
  (the bench check and the 4.82 V worst-case setpoint depend on it). — S4.c
- With JP1 bridged, the Pi must never also have a USB cable plugged in. Its power
  micro-USB feeds the 5 V rail directly (Raspberry Pi Zero 2 W reduced schematic,
  J1 → 5V); whether the data port's VBUS does too is unconfirmed (not shown in the
  reduced schematic). Failure modes: shield unpowered → USB 5 V back-feeds through L6
  and U10's high-side body diode onto VBUS (bus side via L1, payload port via R11);
  shield powered → two supplies fight. **Decided (Nick, 2026-10-05, D14): bench rule
  only** — never connect a USB 5 V source (charger, PC host, self-powered hub that
  back-feeds) to a bridged board's Pi, shield powered or not; Pi-powered USB
  peripherals are fine and count toward the S4.c budget. Open part: the data port's
  VBUS wiring (primary source).
- U10/L6 losses and temperature rise at the Pi's maximum load, potted: U10's
  RθJA is 107.8 °C/W (SLUSEF4A §7.4, JEDEC board), so ~0.4–0.6 W of IC loss is
  ~45–65 °C before any potting derating (SPEC constraint 8). — S4.c (QE S4 F2)
- Murata's product pages list "undersea equipment" among applications they
  don't warrant for these consumer/industrial MLCCs. Applies equally to the
  mote's existing Murata parts (C29, C32, C33, …). — note for S6 review
- Bus power budget: shield + Pi (incl. USB peripherals the Pi powers) + payload against the ~20 W (890 mA) path — S4/S5
