# SPEC.md — nereus_Pi_shield_ADIN2111

*What Nick wants. Stable reference — agents skim this; changes require Nick's approval.*
*Last updated: 2026-10-05*

## Goal

A Raspberry Pi Zero 2W shield made from a copy of the Sofar Bristlemouth mote
(000639-AB): ADIN2111 two-port 10BASE-T1L with PoDL, powered from the bus,
5 V for the Pi, a 24 V payload port, and **the mote's power path kept exactly
as Sofar built it (except the payload load switch, D17): ~20 W absolute max (890 mA
per port inductor at 24 V)**,
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
- The 3.3 V buck is U5, an LMR51430YDDCR; the load switch is U11, a TPS26621DRCR
  (was U9 FPF2700MX, replaced in S5.a, D18); R34 is 9.09 kΩ (RC0402FR-079K09L, was
  374 kΩ); R11 is a 0 Ω 1210 jumper, DNP (D17); the R8 shunt is a UR73D1JTTD10L0F.
  *(live schematic sheets)*
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
- *Historical (U9 removed in S5.a):* FPF2700: 2.8–36 V, 88 mΩ typical; R_SET (kΩ) = 277.5 / I_LIM(TYP) (A), ±20 %;
  short-circuit limit 0.75 × I_LIM; FPF2700 turns off after 0.5 ms blanking and
  retries after 127.5 ms; thermal shutdown 140 °C. With R34 = 374 kΩ, I_LIM ≈ 0.74 A
  typical. *(Fairchild FPF2700/1/2 datasheet Rev. 1.0.3, Eq. 1)*
- Pi Zero 2 W: recommended PSU 2 A, typical bare-board active 350 mA, Camera Module
  250 mA; all models require a 5.1 V supply; no low-voltage detector on the Zero range.
  *(Raspberry Pi documentation, "Power supply")* Input power 5 V DC 2.5 A; operating
  temperature −20 °C to +70 °C. *(Zero 2 W product brief, April 2024)*
- TPS26621DRCR (U11): 4.5–60 V (62 V abs max), 478 mΩ, current limit
  R_ILIM (kΩ) = 6.636 / I_LIM (A), I(OL) 0.757/0.80/0.827 A at 8.25 kΩ, auto-retry,
  FLT open drain, no PGOOD; SHDN low = shutdown (≈ 2 µA internal pull-up); dVdT may
  float (24 V/660 µs); UVLO to IN via ≥ 1 MΩ and OVP to RTN when unused; status ACTIVE.
  SHDN: I(SHDN) −2.4 µA typ / −10 µA max at 0.4 V, V(SHUTF) min 0.9 V, V(SHUTR) max 1.8 V;
  fast-trip 1.6 A typ / 220 ns; thermal shutdown 155 °C, retry 512 ms; §12.1 allows RTN,
  GND and PowerPAD together when reverse-input protection isn't needed (RTN = GND here).
  *(TI SLVSDT4F Rev. F; ti.com part page 2026-10-05)* JLC/LCSC C1848341.
- ADIN2111 (U1): no supply sequencing required; supply ramp ≤ 40 ms; internal power good 20–43 ms after the
  last supply; SPI active ≤ 50 ms (Table 3). Built-in power-on reset holds the chip in reset until supplies are
  good. RESET: active low, internal pull-up, may float, hold low > 10 µs, < 1 µs rejected; SPI accessible ≤ 90 ms
  after release. INT: open drain, active low, requires 1.5 kΩ to VDDIO; asserts after any reset. SPI, INT, LED and
  RESET pins rated −0.3 V to VDDIO + 0.3 V. Straps (internal pull): SPI_CFG1 pin 19 PU, SDO/SPI_CFG0 PD,
  P1_SWPD_EN pin 41 PD, P2_SWPD_EN pin 47 PU, Px_TX2P4_EN pins 21/48 PD; SPI_CFG1/0 = 0/0 → OPEN Alliance with
  protection (Table 22); 2.4 V p-p needs AVDD_H 3.3 V. VDDIO 1.71 V min (1.8/2.5/3.3 V typ); digital V_IL 0.8 V /
  V_IH 2.0 V at VDDIO 3.3 V; LED pins 8 mA at 3.3 V. *(ADIN2111 Rev. B datasheet, Tables 1, 3, 5, 8, 22,
  "Reset Operations"; PDF supplied by Nick, SHA-256 10b6521e7b7fabeaedf7afee6b15a058a923c72ed6e401ad4de53911201b2fba)*
- PoDL bus contact on the mote: threaded inserts MP1–MP4 (Würth 78614015360) sit on B.Cu with unnumbered,
  net-less pads (an SMD ring and the Ø4.4 NPTH); the bus nets reach each insert position through a front F.Cu arc
  on the bus track, C-shaped (~290°, not a closed ring), width 1.2 mm, radius 3.03 mm (copper ≈ 2.4–3.6 mm from centre): MP1 BM1_P, MP2 BM1_N, MP3 BM2_P
  (two arcs), MP4 BM2_N; no vias within 3.5 mm. *(reference .kicad_pcb, read 2026-10-06; QE S5.g F1)* Why, and how a
  new layout should copy it: Sofar Q6.
- AP22913 (U2, U3): ON active high, no internal pull-down; ON input leakage ≤ 1 µA; V_IH 1.1 V min; V_IL 0.4 V max
  (V_IN 1.4–3.6 V) / 0.6 V (3.6–5.5 V); output discharge when off; reverse-current blocking always active; R_ON
  56 mΩ typ at 3.3 V (X1-WLB0909-4 = "CN4": 0.9 × 0.9 mm, 0.5 mm ball pitch; top view A1 VOUT (pin-1 dot) and A2 VIN
  on the top row, B1 GND and B2 ON on the bottom row). *(Diodes DS41203 Rev. 6-2, p. 1 "Pin Assignments")*
- Pi Zero 2 W I²C1: R23/R24 1.8 kΩ 1 % pull-ups from GPIO2/GPIO3 to the Pi's 3V3. *(Raspberry Pi Zero 2 W reduced
  schematics, datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-reduced-schematics.pdf)*
- Pi GPIO reset-default pulls: GPIO0–8 pull up (incl. GPIO8 = CE0), GPIO9–27 pull down (incl. GPIO9 MISO,
  GPIO16, 20, 23, 24, 25). *(BCM2835 ARM Peripherals §6.2 p. 102; assumed to apply to the Zero 2 W's BCM2710A1 (in the RP3A0,
  product brief), not separately verified)*
- I²C standard/fast mode: V_OL ≤ 0.4 V at 3 mA sink, so R_P(min) = (3.3 − 0.4) / 3 mA = 967 Ω at 3.3 V; R_P(max) =
  t_r / (0.8473 · C_b) with t_r 1000 ns / 300 ns. *(TI SLVA689, Table 1 from the I²C specification; Eq. 1–2)*
- JST GH (1.25 mm): current rating 1.0 A AC/DC per contact (AWG #26), voltage rating 50 V AC/DC, −40 °C to +105 °C
  incl. temperature rise, contact resistance 30 mΩ max initial; wire AWG #30–#26. SM02B-GHS-TB is the 2-pin SMD
  right-angle header. *(JST GH connector datasheet, eGH.pdf)* JLC part C189893 for SM02B-GHS. *(Nick's UrchinCam BOM,
  UrchinCam_0v1_BOM_20260121.csv)* LCSC C189893 = SM02B-GHS-TB(LF)(SN), shown out of stock on 2026-10-06
  *(lcsc.com, QE S5.d)*; recheck in S5.e.
- Status LEDs (S5.f): Hubei KENTO KT-0603R, 0603 red, 615–630 nm, V_F 1.8–2.4 V at 20 mA, 300 mcd, LCSC C2286 (stock
  ≈ 2.6 M on 2026-10-06); KT-0603YG, 0603 yellow-green, 567–573 nm, V_F 2.0–2.2 V at 20 mA, 30–42 mcd, LCSC C2289
  (stock ≈ 24 k; JLC extended part). *(lcsc.com product pages, 2026-10-06; JLC part page for C2289)* KENTO marks the
  cathode with a green mark. *(KENTO KT-0603R specification, distributor copy rcscomponents.kiev.ua)* KiCad
  `Device:LED` pin 1 = K, pin 2 = A; `LED_SMD:LED_0603_1608Metric` pad 1 = cathode. *(KiCad 9.0.6 libraries)*
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
7. The power path stays exactly as in the Sofar mote, except the payload load
   switch: R11 is DNP and U9 (obsolete) is replaced by a function-equivalent part,
   with R34/R33/R35 re-derived as needed (D17). L1/L2, D1–D3, R8, C22/C23/R15/R16
   etc. stay unchanged. *(Amended by Nick, 2026-10-05, QE S4.c F5.)* The rating is the mote's: ~20 W absolute max = 890 mA per port inductor at
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
- ~~FPF2700 current limit~~ answered (Fairchild datasheet Rev. 1.0.3, supplied by Nick;
  power_budget §1): R34 = 374 kΩ → ≈ 0.74 A typical (0.59–0.89 A). As captured, R11 was
  fitted and bypassed U9; Nick: R11 DNP so the switch and limit work (D17, S5).
- ~~U9 (FPF2700MX) obsolete~~ done (S5.a, D18): replaced by TPS26621DRCR (U11). Still
  open: lifecycle-check every BOM part before S6.
- R11's description field (Altium import) reads "RES SMD 205K OHM 1% 1/2W 1992" for a
  0 Ω CRCW1210 jumper: stale import data to clean in S6.
- Effective capacitance of C56/C57 (GRM21BR61C226ME44) at 5 V DC bias. Murata's
  SimSurfing tool needs its licence accepted first, so it's unmeasured; TI's
  Eq. 14 wants ≥ 22 µF effective (≈ 1.5 A step, 5 %). — S4.c / S6 (Nick or a
  datasheet curve)
- U10's input caps copy U5's 2.2 µF (C55) + 100 nF. TI's text suggests ≥ 4.7 µF
  (SLUSEF4A §9.2.2.6), though its own Figure 9-1 uses 2.2 µF; field-proven on
  U5, but U10 draws more input current. — S6 review
- ~~JP1 bridge current~~ answered (S4.c, `docs/design-review/power_budget.md` §4):
  IPC-2221, 1 oz assumed, 2.4 A at ΔT 10 °C / 3.2 A at 20 °C; 2 mV drop at 2.5 A.
- ~~Pi undervoltage threshold~~ answered (power_budget §5): the Zero range has **no**
  low-voltage detector (Raspberry Pi documentation, "Power supply warnings"); the
  bench check is 5V_PI ≥ 4.75 V at J1 (USB 2.0 VBUS minimum). R38 stays 13.7 kΩ
  (D16); 13.5 kΩ is the drop-in fix if the bench check fails.
- With JP1 bridged, the Pi must never also have a USB cable plugged in. Its power
  micro-USB feeds the 5 V rail directly (Raspberry Pi Zero 2 W reduced schematic,
  J1 → 5V); whether the data port's VBUS does too is unconfirmed (not shown in the
  reduced schematic). Failure modes: shield unpowered → USB 5 V back-feeds through L6
  and U10's high-side body diode onto VBUS (bus side via L1, payload port through U11 when SW_EN has it on; R11 is DNP);
  shield powered → two supplies fight. **Decided (Nick, 2026-10-05, D14): bench rule
  only** — never connect a USB 5 V source (charger, PC host, self-powered hub that
  back-feeds) to a bridged board's Pi, shield powered or not; Pi-powered USB
  peripherals are fine and count toward the S4.c budget. Open part: the data port's
  VBUS wiring (primary source).
- U10/L6/L1 heat (power_budget §3): ΔTj ≈ 42–57 °C at the D15 target (1 A), indicative
  only (TI's RθJA is for comparison; 25 °C efficiency). Potted RθJA unknown; measure
  T_top at bring-up (Tj ≈ T_top + 9.3 °C/W · P_U10).
- ADIN2111 power at 2.4 V p-p and the other 3.3 V loads: the budget uses a 0.30 W
  allowance at U5's input (ADI: 77 mW typical at 1.0 V p-p, dual supply) until the
  full datasheet is read. — S6
- Murata's product pages list "undersea equipment" among applications they
  don't warrant for these consumer/industrial MLCCs. Applies equally to the
  mote's existing Murata parts (C29, C32, C33, …). — note for S6 review
- ~~Bus power budget~~ done (power_budget §2): against the 12 W v1 module limit a 1 A
  Pi leaves ≈ 6.2 W for the payload; against 890 mA it leaves 645 mA at 24 V for
  payload + pass-through (VBUS behind L1's 0.656 Ω included).
