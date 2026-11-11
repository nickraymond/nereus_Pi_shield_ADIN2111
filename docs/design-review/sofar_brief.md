# Design-review brief for Sofar — nereus Pi shield vs Bristlemouth mote 000639-AB

*Shipped with the board files. Lists every deliberate change from your mote design
and why. Anything not listed is your circuit, copied as-is. Decision IDs (Dn) refer
to `docs/DESIGN.md`.* *Updated 2026-10-05 (S5.c).*

**Baseline:** Sofar Bristlemouth mote 000639-AB (KiCad copy of the Altium design).
The ADIN2111 / PoDL front end, 3.3 V and 1.8 V regulation and the ~20 W power path
(L1/L2 SRF1260-101M, D1–D3, R8, C22/C23/R15/R16) are **unchanged** (D12).

| # | Area | Mote 000639-AB | This shield | Why |
|---|---|---|---|---|
| 1 | Host processor | STM32 + DF17 mezzanine (P1) | Removed. Raspberry Pi Zero 2 W on a 2×20 socket header (J1); the Pi drives the ADIN2111 over SPI | The Pi runs the application (cameras) |
| 2 | I²C pull-ups | R26/R27 4.7 kΩ on the STM32 sheet | Re-added on the shield: same refs, part (ERJ-2RKF4701X) and footprint, to the shield's 3V3 (D11, D20). With the Pi's own 1.8 kΩ the bus sees ≈ 1.3 kΩ | Removed with the STM32; the Pi needs them, and they keep the bus usable with a bench MCU |
| 3 | 5 V rail | None | U10 LMR51430YDDCR, a copy of your U5 block: R38 13.7 kΩ (4.98 V), output caps 2 × 22 µF 16 V + 4.7 µF 10 V, same 8.2 µH inductor (D13, D16). Layout as at your U5 and L3: a top-layer ground fill under U10 with five ground vias, and the inductor's output vias under its body on a 5 V fill on the PWR plane (D47) | Powers the Pi from the bus |
| 4 | 5 V to the Pi | — | JP1: bridged copper link on 1210 pads (connected as built; cut for a battery/USB-powered Pi; refit a 0 Ω) (D14) | Shield is normally the Pi's only supply |
| 5 | Payload load switch | U9 FPF2700MX with R11 (0 Ω) **fitted across it** in the files we received, so the switch was bypassed (Q2 asks about production) | **R11 DNP.** U9 replaced by **TI TPS26621DRCR** (U11): R34 374 kΩ → **9.09 kΩ** (≈ 0.73 A limit), new R41 1 MΩ (UVLO tie), dVdT open, OVP to GND. Enable pull-up R32 → **10 kΩ pull-down R42** (TPS26621 SHDN is active low; payload off by default). PGOOD dropped (R33/TP34 removed); FLT kept. RTN = GND (reverse-input protection not used). R_ON 478 mΩ vs 88 mΩ: ≈ 0.35 V drop at 0.73 A (D17, D18) | FPF2700MX is no longer manufactured (Digi-Key, 2026-10); we want the payload switched by the Pi and current-limited. TPS26621 is active at TI and stocked by JLC (C1848341) |
| 6 | ADIN power enable (ADIN_PWR → U2/U3 ON) | Driven by the STM32, no pull resistor | Driven by Pi GPIO23 with a new **R43 100 kΩ pull-down** (your R21 part). The AP22913 ON pin has no internal pull-down | Keeps the ADIN off while the Pi boots, is absent or is off, so the straps are only read on a deliberate power-up and INT can't feed an unpowered Pi. CS/RST back-power is handled by a boot order in Pi software (D21) |
| 7 | Load-switch control links | R10 0 Ω (STM32 pin 19 → SW_ON) and R9 0 Ω (mezzanine → same net), TP19 | R9 and R10 removed; TP19 kept, tied to SW_EN; Pi GPIO16 is the only controller (D22) | One controller; fewer parts to place |
| 8 | Payload power out | VBUS_OUT through mezzanine P1 pins 14/16/18 | **J5: two through-hole wire pads** (oval 4.2 × 2.6 mm, 1.3 mm hole, 3.81 mm pitch), leads soldered directly: pad 1 VBUS_OUT, pad 2 GND (D34; was a JST GH 2-pin connector, D23) | The mezzanine is gone; pads save a part and board space and are easy to wire by hand |
| 9 | ADIN status LEDs | None | **D8 red** (ADIN powered), **D9 / D10 yellow-green** (port 1 / port 2 link/activity on ADIN pins 21 / 48, active low; your R3 / R5 stay as their pull-ups, so the 1.0 V p-p straps are unchanged), each via 1.5 kΩ from ADIN_VDDIO through **JP2**, a bridged link that is cut to disable them (D25). On the board the three LEDs sit in one line on the south edge, each port LED beside its own port's inserts (port 2 west by BM2, power in the middle, port 1 east by BM1; D40), with their resistors underneath and JP2 just north of them; the two link lines reach them on Internal 2 from your vias beside U1 (D36) | Bench visibility of PHY power and per-port link; a few mW, off with the ADIN |
| 10 | BOM: planned parts | Your specified parts | 10 lines planned as LCSC-stocked equivalents for JLC assembly; the rest unchanged (D27): R34, R20/R39, R21 group, C31, C17/C26, C21, C16 group, C19/C27, R14/R18, D1 → your Vishay second source. Table and reasons: `bom.csv` (Planned note), `bom_alternates.md` | Your exact parts aren't stocked at LCSC; for your review, not yet adopted |
| 11 | SPI configuration straps | **R2** 4.7 kΩ from U1 pin 19 (P1_LED_0 / SPI_CFG1) to GND, on the bottom under U1 at (154.70, 116.00). **R9** was a 0 Ω link on another net | R2 now goes to net CFG1_STRAP and solder jumper **JP3** selects ADIN_VDDIO (bridged as built) or GND. R2 sits with R47 (1 kΩ to the Pi, ADIN_TIMER) on the top side south of U1; pin 19 reaches them from its existing via on Internal 2 (10.6 mm more). JP3 sits beside JP4 in the north-east corner; the jumper side of R2 runs there on Internal 1 (61 mm, a DC level) (D38). **R9** is reused as a 4.7 kΩ strap resistor from SDO / SPI_CFG0 (the MISO stub) to net CFG0_STRAP, and **JP4** selects GND (bridged as built) or ADIN_VDDIO (S9 step 2) | The Pi can run either SPI mode without a board change. R2 had to move: its strap pad was boxed in under U1 with no room for a via |
| 12 | Planes outside the mote's outline | GND plane and PWR plane stop at the mote's board edge (x 123.5..173.5, y 87..123, with a notch in the north-west corner). The insert's unplated hole carries a net-less 5.5 mm copper disc on the bottom in the files we received | The shield is 65 × 56 mm. Added on the **GND plane**: a strip under the Pi header (y 76.6..88) and a fill of the north-west notch (to y 103.2) under the 5 V converter and the 5 V input. Added on the **PWR plane**: PI_5V and PI_3V3 areas under the Pi header. Your planes are unchanged inside the mote's outline; no plane was added under the bus trunks or east of x 173.5. The insert hole is a plain unplated hole; the seven ring vias and the ring pad carry the bus net as on the mote (S9 steps 3–4) | The Pi header, the 5 V converter and the 5 V input sit outside the mote's outline and need a return plane |
| 13 | Silkscreen | Reference designators 0.6 / 0.64 mm; part number and "BM Mote" on the bottom | No copper change. Font Menlo Bold (slashed zero). Designators all 0.8 mm, horizontal, re-placed beside their parts. Function names for the straps, connectors and LEDs; J4 (+5V AUX OUT) and J5 (VBUS OUT) boxed. Board name "Pi Shield / ADIN2111 Rev0" with the Bristlemouth logo on top; pin names, ratings, screw sizes and a table of the four SPI strap modes on the bottom; your name frame there is removed (D39, D42, D46) | The board is hand-wired and strapped by developers: the function of each strap and connector should read at a glance |

**Notes for your review**

- Rating, budget and thermal analysis: `docs/design-review/power_budget.md`. The Pi
  is limited to ≤ 1 A continuous by U10's temperature (D15).
- Open questions for you: `docs/SOFAR_QUESTIONS.md` (Q2 R11 on production motes,
  Q4 mezzanine-side load-switch control).
- **Planned parts: the one column to review** (D27). Each BOM line now has a `Planned MPN/Mfr/LCSC` and a
  `Planned note` (why) right after your part in `docs/design-review/bom.csv` and in KiCad's Symbol Fields view
  "Sofar review (planned parts)". Where Planned equals your part, nothing changes. Ten lines differ (row 10 above).
  The first build uses the planned parts only after your review. Your part stays the schematic `Value` until then.
- **BOM alternates are proposals for your review, not substitutions** (D26). Every part you specified is still the
  part on the schematic (`Value`) and in the BOM's first column. Where LCSC doesn't stock it, we recorded up to two
  LCSC alternates as hidden `ALT…` fields with a note, and a `SOURCING` field saying how the first build buys it (your
  exact part, through JLC global sourcing). Side by side in `docs/design-review/bom.csv`; reasoning and stock in
  `bom_alternates.md` and `bom_lifecycle.md`. The PoDL/power-path ones (R8, R15/R16, C22/C23, C17/C21/C26, PoDL
  front end) are marked "Sofar review": we won't adopt any of them without you.
- **Signal names** (D30): active-low labels carry an overbar (~{ADIN_RST}, ~{ADIN_INT}, ~{ADIN_CS}); the payload
  switch's control and fault lines are PAYLOAD_EN and ~{PAYLOAD_FAULT} (your SW_ON / SW_FLAGB). Connections unchanged.
- **Cover page:** your mote renders, sheet index image and revision row are replaced (renders TBD after our layout); your
  licence notice and CC BY-ND logo stay.
- Import housekeeping, not design changes: the five 0 Ω CRCW1210 jumpers (R11, R12, R13, R17, R19) carried the
  Description "RES SMD 205K OHM 1% 1/2W 1992" from the import; it now reads "RES SMD 0 OHM JUMPER 1210" (same part).
- Import housekeeping, not design changes: Altium-import connectivity repairs (21
  mid-wire pins split and joined), new reference numbers start above the mote
  board's highest (U10+, C53+, R37+).
