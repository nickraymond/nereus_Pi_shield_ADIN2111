# DESIGN.md — Architecture & Decisions (as-built)

*What the schematic is and why. Agents append; never silently rewrite history.*
*Last updated: 2026-10-04*

## Sheet hierarchy

```
nereus_Pi_shield_ADIN2111.kicad_sch     root
└── BM_Mote_1_Master                    Top-Level
    ├── BM_Mote_1_Power                 U5 3.3 V buck, U6 1.8 V
    ├── BM_Mote_1_ADIN2111              ADIN2111 + AP22913 switches
    ├── BM_Mote_1_PoDL                  L1/L2 PoDL magnetics, D1/D2 protection
    │   └── BM_Mote_1_PowerMon          INA232 + R8 shunt
    └── BM_Mote_1_Load                  U11 24 V payload switch (TPS26621, D18)

Not referenced by any sheet (files deleted in S1): BM_Mote_1_Processor, BM_Mote_1_USB
```

## Key designs

**Pi header pin map** *(planned; becomes as-built in S5)*

| Pi pin | GPIO | Signal |
|---|---|---|
| 19 / 21 / 23 / 24 | 10 / 9 / 11 / 8 | ADIN_MOSI / ADIN_MISO / ADIN_SCK / ADIN_NSS |
| 22 | 25 | ADIN_INT |
| 18 | 24 | ADIN_RST |
| 16 | 23 | ADIN_PWR |
| 3 / 5 | 2 / 3 | I2C1_SDA / I2C1_SCL |
| 36 | 16 | SW_EN (**high = payload on**; R42 pull-down keeps it off, D18) |
| 38 | 20 | SW_FLAGB (U11 FLT, open drain, R35 pull-up) |
| 2 / 4 | — | `PI_5V`, joined to `5V_PI` by JP1 (bridged link; cut to isolate, D14) |
| 6, 9, 14, 20, 25, 30, 34, 39 | — | GND |
| 1, 17 | — | **unconnected** (Pi 3.3 V) |

Reserved: 26 (CE1), 29, 32, 33 (motor). Free: 40 (SW_PGOOD dropped, D18). Avoid: 27, 28 (HAT EEPROM), 8, 10 (console).

**Label rules:** labels copied with a block get a new prefix (`3V3_*` → `5V_*`);
two local labels with the same name silently join their nets.

**Net-check method** (`tools/netcheck.py`, run by `tools/check.sh`):
- **Truth:** pad-to-net assignments in the mote board
  `KiCAD_reference_designs/20250409_BM_Mote_000639-AB/BM_Mote_000639-AB.kicad_pcb`
  (read-only).
- **Candidate:** the kicadsexpr netlist exported from our schematic.
- **Compare connectivity, not names** (the import renamed nets). Only parts
  present in both are compared; nodes are `REF.PIN` = `REF.PAD`.
- **Reports:** opens (a copper net split across schematic nets), shorts (a
  schematic net joining copper nets), unpaired pins/pads on shared parts,
  removed and new parts. Exit 0 only if there are no opens, shorts or unpaired pins.
- **Validated:** unit tests on fixtures; the TP22→VBUS open was confirmed by hand
  in both files; the untouched reference schematic shows 38 opens against its
  own copper, so the opens come from the import, not the tool.
- ERC reports aren't deterministic run to run (same violations, different
  example labels), so compare ERC by counts and types.
- Parts scheduled for deletion are listed in `docs/design-review/excluded_parts.txt`
  and treated as already removed.
- `tools/midwire.py` (also run by check.sh) flags any pin whose end sits mid-wire;
  KiCad needs the wire split there, a junction alone isn't enough (measured).
- Copper can't verify nets whose other end was a removed part: e.g. the ADIN SPI
  went to the STM32. Those are checked from the netlist: `ADIN_MISO/MOSI/SCK/NSS/RST/INT`
  each reach the Top-Level sheet from U1 (verified 2026-10-05), ready for S5.

## Decision log

| # | Date | Decision | Rationale |
|---|---|---|---|
| D1 | 2026-10-04 | Agents own schematic capture up to the design-review package; Nick owns review, board and bring-up | Clear boundary; the board is Nick's |
| D2 | 2026-10-04 | TRACKER.md is the single source of truth. `pi-shield-checklist.html` is the shared visual view of it: agents keep it in sync every PR, and finished work is marked in its data (`done`), not only in the browser (revised same day at Nick's request) | Nick and colleagues use the HTML; ticks stored only in a browser are invisible to agents and other viewers |
| D3 | 2026-10-04 | Live project folder is `nereus_Pi_shield_ADIN2111/` (renamed from `_002` in S0.1) | One stable name; git keeps the history |
| D4 | 2026-10-04 | 5 V for the Pi: copy of the LMR51430 (U5) set to 5 V, fed from VBUS | Reuses a proven block (checklist Option A) |
| D5 | 2026-10-04 | **Superseded by D14.** 5V_PI reaches Pi pins 2/4 through an open solder jumper | Must stay open whenever the Pi has its own USB power |
| D6 | 2026-10-04 | Plain 2×20 female socket header, no stacking header | Shield plugs onto the Pi's male pins |
| D7 | 2026-10-04 | **Superseded by D12 for this board.** Target ~50 W with two-winding PoDL inductors, one per port; selection in POWER_PATH.md | Commercial mote magnetics limit it to ~20 W |
| D8 | 2026-10-04 | **Superseded by D12 for this board.** Rating (P1): ~50 W **absolute max** = 2.083 A per port inductor at 24 V, defined like Sofar's 20 W. Margin comes from choosing larger magnetics (MSD1514-class, fit pending) | Same basis as the mote's rating; potting removes thermal headroom |
| D9 | 2026-10-04 | Electronics are potted. Sofar-vetted parts are kept as-is (including the C22/C23 electrolytics). Newly sourced parts: no aluminium electrolytics, no PPTCs, other risky parts flagged (SPEC constraint 8) | Vetted design is trusted; electrolytics vent or deform under pressure; PPTC trip behaviour changes when encapsulated |
| D10 | 2026-10-05 | Every PR gets an independent, read-only Quality Engineer review in a separate Code session, one standing session per sprint (never a sub-agent; `.claude/agents/quality-engineer.md`, Opus 5.5, high effort) before Nick's KiCad review; merge needs both | A second pair of eyes on every claim; QE never edits, so it can't collide with Nick or the design agent |
| D11 | 2026-10-05 | The shield provides I2C pull-ups on I2C1_SDA/SCL (S5), reusing the mote's R26/R27: 4.7 kΩ ERJ-2RKF4701X to 3V3 | Nick: the Pi needs them; the mote's pull-ups were on the removed STM32 sheet |
| D12 | 2026-10-05 | This first board keeps the Sofar mote's power path unchanged (exception: the payload load switch, D17): L1/L2 stay SRF1260-101M and every other path part stays as vetted. Rating = the mote's ~20 W absolute max, 890 mA per port inductor at 24 V (Sofar, More Power Delivery). 50 W (D7/D8, POWER_PATH.md) is deferred until after this board is in production | Nick: reduce technical risk on the first board and reuse Sofar's work, so the board is a new layout of proven hardware. The design has been in the field for years, and Nick already powers his cameras from the mote's power electronics, so it's known to work; no derating question goes to Sofar. The 50 W revision gets scoped with the future motor load |
| D13 | 2026-10-05 | 5 V for the Pi (S4.a): U10 LMR51430YDDCR, a copy of U5 with new refs above the mote board's highest. Changed from U5: R38 = 13.7 kΩ (5 V, TI's own example), output caps C56/C57 22 µF 16 V 0805 + C58 4.7 µF 10 V 0402 (U5's are 6.3 V). Kept: L6 = PA5432.822NLT 8.2 µH (same as L3), input caps, bootstrap cap, its own 1.82 MΩ/200 kΩ enable divider | Reuse the proven block (D4, D12). Ripple (16–32 V in, nominal L): 8.2 µH gives 12.7–15.6 % of 3 A at 5 V, below TI's 20–60 % guideline (§9.2.2.4) but above the 9.7–10.9 % the field-proven 3.3 V converter runs at; Nick chose it over 4.7 µH. TI Table 9-2 (1.1 MHz) suggests 3.3 µH for 5 V and 2.2 µH for 3.3 V, so L6 is 2.5× and U5's L3 3.7× TI's value; low ripple weakens the peak-current comparator's signal-to-noise (§9.2.2.4), so bring-up checks the SW node for jitter at full and light load. Output capacitance from TI Eq. 14 (≥ 22 µF effective at 1.1 MHz, 1.5 A step, 5 %). Vout 4.98 V nominal, 4.82–5.14 V worst case (VREF ±1.5 %, 1 % resistors). Own enable divider keeps the 5 V watchdog idea open |
| D14 | 2026-10-05 | The shield powers the Pi by default. JP1, a bridged link (project footprint `nereus:SolderJumper-2_R1210_Bridged_NetTie`: Sofar R11's 1210 pads joined by a 1.0 mm copper net tie, no BOM part), joins `5V_PI` to `PI_5V` (Pi pins 2/4). Battery- or USB-powered Pi: cut the bridge before potting; reconnect by fitting a 0 Ω 1210 (CRCW12100000Z0EA, as R11). Revises D5 | Nick: the usual case is the shield as the Pi's only supply; no DNP part wanted. Copper is repeatable at fab with no assembly step; a 0 Ω resistor fits the pads if a cut ever needs undoing. Bridge current rating checked in S4.c. **Known risk, accepted with a bench rule (QE S4.b F1; Nick re-confirmed 2026-10-05):** with JP1 bridged, any other 5 V on the Pi's rail is tied to 5V_PI. The Pi Zero 2 W's power micro-USB feeds its 5 V rail directly, as do header pins 2/4 (Raspberry Pi Zero 2 W reduced schematic, J1/J8); the data port isn't shown there (unconfirmed). With the shield unpowered, that 5 V back-feeds through L6 and U10's high-side MOSFET body diode onto VBUS (≈ 4.4 V on the bus side via L1, and on the payload port via R11 as captured, or through U9 when SW_EN has it on once R11 is DNP per D17); with the shield powered, the two supplies fight. Mitigation (Nick): procedure only — on a bridged board never connect a USB 5 V *source* to the Pi (charger, PC/laptop host, self-powered hub that back-feeds), shield powered or not; USB peripherals the Pi powers are fine (they count toward the S4.c budget). Hardware guard left for a later revision |
| D15 | 2026-10-05 | Continuous Pi load target ≤ 1 A at 5V_PI (Pi + its USB devices), short peaks above; generous copper at U10; measure U10's case temperature at bring-up (P-S4c-1) | U10's temperature is the binding limit: ≈ 42–57 °C junction rise at 1 A vs 90–121 °C at 2 A (indicative, `docs/design-review/power_budget.md` §3). Typical Pi + camera + GPIO ≈ 650 mA (RPi docs) |
| D16 | 2026-10-05 | R38 stays 13.7 kΩ: U10 at 4.98 V nominal, 4.82–5.14 V worst case (P-S4c-2) | Every corner inside USB's 4.75–5.25 V for the Pi's peripherals; no cable/fuse drop to the Pi's rail; the Zero range has no undervoltage detector (RPi docs). 13.5 kΩ (5.04 V) is the drop-in fix if bring-up shows 5V_PI < 4.75 V at J1 |
| D17 | 2026-10-05 | Payload port: switched by the Pi (SW_EN) and current-limited by the load switch (R34 → ≈ 0.74 A typical, FPF2700 datasheet), with **R11 DNP** (S5). As captured from Sofar, R11 (0 Ω across U9) was fitted, which bypassed U9 entirely. U9 FPF2700MX is obsolete, so S5 replaces it with a part JLC can source, matching the function (36 V class, ≈ 0.74 A limit, active-low ON, FLAGB/PGOOD) | Amends SPEC constraint 7 (Nick, 2026-10-05). Nick: payloads are small devices (e.g. another sensor to switch on), none runs near the limit; he wants the switch and limit active (QE S4.c F4 found R11 fitted). Digi-Key lists FPF2700MX as no longer manufactured (2026-10-05) |
| D18 | 2026-10-05 | U9 FPF2700MX → **U11 TI TPS26621DRCR** (JLC C1848341; TI status ACTIVE). R34 → 9.09 kΩ (I_LIM = 6.636/R = 0.73 A, SLVSDT4F Eq. 3; ≈ −6/+4 %); new R41 1 MΩ IN→UVLO and OVP→GND (UV/OV cut-off unused, Fig. 10-14); dVdT open (internal 24 V/660 µs ramp). SHDN is active low, so the SW_ON pull-up R32 becomes a **10 kΩ pull-down R42** (RMCF0402FT10K0): worst-case SHDN source current 10 µA → 0.1 V, below V(SHUTF) min 0.9 V; the Pi's 3.3 V high is above V(SHUTR) max 1.8 V (SLVSDT4F §7.5; 100 kΩ had no worst-case margin, QE S5.a F2). Payload off by default, Pi drives SW_EN high. No PGOOD: SW_PGOOD, R33, TP34 and the sheet pin removed (Pi pin 40 freed); FLT keeps SW_FLAGB. R11 DNP (D17). **RTN = GND** (with GND and the PowerPAD): reverse-input protection isn't used — VBUS is internal behind D1, and the FPF2700 had none (§12.1 allows it; §10.4's "don't" applies only when reverse protection is wanted). R_ON 478 mΩ vs FPF2700's 88 mΩ: ≈ 0.35 V drop and ≈ 0.25 W at 0.73 A. Hard short / output caps (closes QE S4.c N6): C_OUT ≥ 0.01 µF (ROC), start-up into a short is current-limited (Fig. 9-12), fast-trip 1.6 A typ / 220 ns, thermal shutdown 155 °C with 512 ms auto-retry, D3 is TI's recommended output Schottky (§11). Floating dVdT ramps at ≈ 36 V/ms, so a payload input capacitance above ≈ 20 µF charges in current limit (≈ C·V/0.73 A, e.g. 4.4 ms for 100 µF at 32 V, well inside tCL(dly) 512 ms); auto-retry only if thermal shutdown trips. New project symbol `nereus:TPS26621DRCR`; footprint `Package_SON:Texas_DRC0010J` (stock) | Nick: JLC-sourceable replacement for the obsolete part, payload switched and limited; the three sub-choices (part, pull-down, drop PGOOD) approved 2026-10-05. Tracked for Sofar in `docs/design-review/sofar_brief.md` |

## ERC / net-check results

| Date | Sprint | ERC errors / warnings | Net diff vs copper | Notes |
|---|---|---|---|---|
| 2026-10-04 | S0.1 | 90 / 578 before and after the rename | Netlist identical apart from the library path | Rename confirmed safe; not the S0.4 baseline |
| 2026-10-05 | S0.4 | 90 / 578 | 42/68 matched; **26 opens**, 0 shorts, 0 unpaired; 43 parts removed, 4 new | **Baseline.** Details in `docs/design-review/netcheck.md`. S1 target: 0 opens |
| 2026-10-05 | S1 | 65 / 590 | **53/53 matched, 0 opens, 0 shorts** (14 S2-deletion parts excluded); midwire 0 | Import fixed. Edits in `docs/design-review/changelog.md` |
| 2026-10-05 | S2 | 76 / 562 | 53/53, 0 opens, 0 shorts, **0 excluded**; J1 GND 8/8 on GND | Mezzanine gone, J1 placed. Errors −27 (12 TPs, 13 mezzanine labels, U5 VIN, U6 GND) / +38 (29 J1 pins, 8 I2C1/SCL/SDA labels now one-pin, J1.2) |
| 2026-10-05 | S3 | 76 / 562 | 53/53, 0 opens, 0 shorts, 0 excluded | No schematic change: power path kept as Sofar's (D12) |
| 2026-10-05 | S4.a | 78 / 629 | 53/53, 0 opens, 0 shorts, 0 excluded; 13 new parts; existing parts' connections identical | 5 V converter U10 (copy of U5): +2 errors (U10 CB/SW, like U5), +57 off-grid, +10 footprint links. New nets 5V_PI, 5V_Buck_SW, 5V_FB, 5V_UVLO, U10 CB; VBUS and GND gain only the new parts |
| 2026-10-05 | S4.b | 76 / 629 | 53/53, 0 opens, 0 shorts, 0 excluded; 1 new part (JP1); existing connections identical | JP1 bridged link 5V_PI → PI_5V (J1.2/J1.4), #FLG03 on PI_5V: −2 errors (J1 pin 2 not connected / not driven). midwire now sees J1's 40 pins (tool fix); still 0 |
| 2026-10-05 | S4.c | 76 / 629 | unchanged (docs only) | Power budget in `docs/design-review/power_budget.md`; D15 (Pi ≤ 1 A), D16 (R38 13.7 kΩ), D17 (payload switched/limited by U9, R11 DNP and U9 replacement in S5) |
| 2026-10-05 | S5.a | 74 / 626 | 50/50, 0 opens, 0 shorts, 0 excluded; kept parts' connections identical; U9/R32/R33/TP34 removed, U11/R41/R42 new | Load switch replaced (D18), R11 DNP: −2 errors (SW_PGOOD sheet pin, U9.8), −3 footprint-link warnings. Copper nets 53 → 50: three nets now hold only removed parts |

**Remaining ERC errors after S5.a (74), and who resolves each** (counted with
`python3 tools/ercsum.py --items`; the S1 version of this table undercounted
pin_not_connected, 16 vs 24, by missing FID and sheet-pin items — QE S2 F1):

| Type | # | What | Resolved by |
|---|---|---|---|
| pin_not_connected | 39 | J1: 28 GPIO pins (pin 2 cleared in S4.b); Load Switch sheet pin SW_FLAGB = 1 (unconnected on the Top-Level sheet since import; SW_PGOOD removed in S5.a); FID1–6 fiducials' hidden NC pin = 6; MTG1–4 mounting holes = 4 | S5 (GPIO, SW_FLAGB → Pi 38); FID1–6 S6 (justify/exclude); MTG1–4 Nick (board) |
| label_dangling | 18 | ADIN_MISO/MOSI/NSS/RST/SCK and the ADIN sheet's CS/MISO/MOSI/SCK/RST; I2C1_SCL/SDA and the PoDL and Power Monitor sheets' SCL/SDA: each net has one pin until the Pi header is wired | S5 |
| power_pin_not_driven | 8 | #PWR34 ADIN_VDDIO (switched rail from U3); U5 CB/SW; U10 CB/SW (S4.a copy of U5); U6 VIN/SW/VOS (switch nodes / regulator-fed rails with no power-output pin) | justified or flagged in S6 (J1.2 cleared in S4.b by #FLG03) |
| unresolved_variable | 9 | Title block `${PCBPARTNAME}` ×1, `${PCBPARTNUMBER}` ×8 | Needs a name/part number from Nick (S6) |

S2's PWR_FLAGs cleared U5 VIN (VBUS) and U6 GND.

Warnings (626) are cosmetic import leftovers: 485 off-grid endpoints (Altium
coordinates such as `…0.0022`; +2 in S2 where the trimmed I2C1 wires end on
off-grid label anchors; +57 in S4.a, the U10 copy keeps U5's off-grid offset),
118 footprint-library links (+10 in S4.a: the copied parts keep the mote's
library-less footprint names; S5.a: −4 for U9/R32/R33/TP34, +1 for R42, which keeps
R32's library-less footprint; S4.d), 11 dangling wire ends
(all pre-existing), 12 duplicate net names (e.g. `PHY1_P`/`BM1_P` on the same wire).
