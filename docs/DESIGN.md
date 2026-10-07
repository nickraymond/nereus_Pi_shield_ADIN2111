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

**Pi header pin map** *(as built, S5.b: each signal pin has a short stub and a same-name label on the Top-Level sheet; every other GPIO pin has a no-connect flag)*

| Pi pin | GPIO | Signal |
|---|---|---|
| 19 / 21 / 23 / 24 | 10 / 9 / 11 / 8 | ADIN_MOSI / ADIN_MISO / ADIN_SCK / ADIN_NSS |
| 22 | 25 | ADIN_INT |
| 18 | 24 | ADIN_RST (no external pull: ADIN internal pull-up; the Pi must drive GPIO24 low to hold reset, see boot order) |
| 16 | 23 | ADIN_PWR (**R43 100 kΩ pull-down**: ADIN off unless the Pi drives it high, D21) |
| 3 / 5 | 2 / 3 | I2C1_SDA / I2C1_SCL (**R27/R26 4.7 kΩ to shield 3V3**, plus the Pi's own 1.8 kΩ to Pi 3V3, D20) |
| 36 | 16 | SW_EN (**high = payload on**; R42 pull-down keeps it off, D18); TP19 test pad on this net (R10 removed, D22) |
| 38 | 20 | SW_FLAGB (U11 FLT, open drain, R35 pull-up) |
| 2 / 4 | — | `PI_5V`, joined to `5V_PI` by JP1 (bridged link; cut to isolate, D14) |
| 6, 9, 14, 20, 25, 30, 34, 39 | — | GND |
| 1, 17 | — | **unconnected** (Pi 3.3 V) |

Reserved: 26 (CE1), 29, 32, 33 (motor). Free: 40 (SW_PGOOD dropped, D18). Avoid: 27, 28 (HAT EEPROM), 8, 10 (console).
All 17 unused GPIO pins (7, 8, 10–13, 15, 26–29, 31–33, 35, 37, 40) carry no-connect flags; remove the flag when a pin is used.
Pull resistors on these nets: S5.c (D20, D21). None on MISO (SDO is the SPI_CFG0 strap, see below) or on RST.

**ADIN power and boot** *(S5.c; Sofar's circuit, unchanged)*

U2 (1V8 → ADIN_AVDD) and U3 (3V3 → ADIN_VDDIO), both AP22913, share one ON net, ADIN_PWR (TP8). Sofar's sheet note:
the load switches cut ADIN power for "<10mW mote operation". ADIN_VDDIO ≈ 3.32 V when on (U5: 0.6 V × (1 + 100/22.1);
U3 ≈ 56 mΩ), 0 V when off (U3 output discharge). The ADIN needs no supply order and holds itself in reset until its
supplies are good (ADIN2111 Rev. B Table 3 note, "Power-On Reset").

Hardware configuration straps, read at power-up / reset release (Table 8, Tables 18–22; all on ADIN_VDDIO or GND, so
only valid with the ADIN powered):

| ADIN pin | Chip default (internal pull) | Sofar's resistor (overrides) | Reads | Result |
|---|---|---|---|---|
| 19 P1_LED_0 / SPI_CFG1 | pull-up → 1 | R2 4.7 kΩ to GND | 0 | with SPI_CFG0 = 0: OPEN Alliance SPI with protection (Table 22) |
| 43 SDO / SPI_CFG0 | pull-down → 0 | none | 0 | (Pi GPIO9's default pull-down agrees) |
| 41 TEST_0 / P1_SWPD_EN | pull-down → 0 (port 1 asleep) | R6 4.7 kΩ to ADIN_VDDIO | 1 | port 1 active after reset, links up |
| 47 P2_LED_0 / P2_SWPD_EN | pull-up → 1 (port 2 active) | R4 4.7 kΩ to GND | 0 | port 2 in software power-down |
| 21 / 48 Px_LED_1 / Px_TX2P4_EN | pull-down → 0 (2.4 V p-p allowed) | R3 / R5 4.7 kΩ to ADIN_VDDIO | 1 | 1.0 V p-p only, locked (pins 21 / 48 also drive D9 / D10, D25). **Required**: AVDD is 1.8 V, and 2.4 V p-p needs 3.3 V AVDD_H "otherwise, the device cannot start up" |
| 39 INT | pull-up | R1 1.5 kΩ to ADIN_VDDIO | — | the datasheet requires 1.5 kΩ to VDDIO |
| 20 RESET | pull-up | none | — | may float; hold low > 10 µs to reset; < 1 µs pulses ignored |

**Boot order (Pi software, D21):**
1. Firmware, before the kernel: `config.txt` lines `gpio=24=op,dl` (drive ADIN_RST low) and `gpio=23=op,dh` (drive
   ADIN_PWR high). Firmware applies these a few seconds after power-up (the ADIN is held off by R43 until then), and the
   kernel or user space can still change the pins later
   (Raspberry Pi documentation, config.txt "GPIO control"). GPIO24 must be **driven** low: once ADIN_VDDIO is up, the
   ADIN's internal RESET pull-up fights the Pi's weak default pull-down (neither value is published), so the default
   alone doesn't hold reset (QE S5.c F1).
2. Wait ≥ 40 ms (supply ramp, Table 3).
3. Release ADIN_RST (drive GPIO24 high, or a > 10 µs low pulse later for a deliberate reset).
4. Wait for INT to go low. It asserts after any reset; SPI is accessible ≤ 90 ms after RESET is released ("Hardware Reset").
5. Configure over SPI.

Even if step 1 is missed, the ADIN's power-on reset resets it when ADIN_PWR comes up, and the straps read correctly
(Pi GPIO9's default pull-down agrees with SDO's). The software then issues a deliberate RST pulse after the SPI driver
loads.

**Rule:** never leave CS, RST, SCK or MOSI high while ADIN_PWR is off. The ADIN's SPI/RESET/LED pins are rated −0.3 V to
VDDIO + 0.3 V (Table 5), so a high pin back-powers the unpowered chip through its clamps. U3's reverse blocking keeps
this off the shield's 3V3, but not off ADIN_VDDIO. Power the ADIN early in boot, before the SPI driver loads (CS idles
high), with the `config.txt` lines in step 1, and keep it on while SPI0 is enabled (Option 1, Nick 2026-10-05; no series
resistors). If the ADIN is ever switched off at runtime, drive CS, RST, SCK and MOSI low first.

**Back-power cases** (Pi 3V3 and shield 3V3 are separate rails; they only differ when JP1 is cut):

| Case | Path | Size | Handling |
|---|---|---|---|
| Pi booting, ADIN off | GPIO8 (CE0) defaults to pull-up (BCM2835 §6.2) → ADIN CS clamp | weak internal pull (value not given in the BCM2835 manual): small | power the ADIN early (rule above) |
| Pi running, ADIN off | spidev idles CS high, driven | mA-level through the clamp | not allowed by the rule |
| Pi off, shield on | INT: R1 1.5 kΩ from ADIN_VDDIO into GPIO25 | ≈ 1.8 mA if the ADIN were on | R43 keeps the ADIN off when the Pi doesn't drive GPIO23 |
| Pi off, shield on | R26/R27 4.7 kΩ into GPIO2/3; R35 100 kΩ into GPIO20 | ≈ 0.6 mA / line; ≈ 33 µA | accepted (small); only with JP1 cut |
| Pi on, shield off | the Pi's 1.8 kΩ I²C pull-ups into U4 (INA232) | — | exists without R26/R27; only with JP1 cut |

**Sheet layout rule (Nick, 2026-10-06):** all board interconnects (PoDL inserts MP1–MP4, payload connector J5, any
future connector) live on the right side of the Top-Level sheet.

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
| D19 | 2026-10-05 | Footprints from the mote come from a project library `mote.pretty`, nickname **`Vault`** (matching the board's `Vault:` IDs): the 43 footprints the schematic uses, extracted read-only from the reference board with KiCad's own pcbnew 9.0.6 (`tools/fpextract.py`; back-side instances flipped to the front, position/rotation zeroed, nets cleared). Every bare footprint field is now `Vault:<name>`; new parts keep their stock/`nereus` libraries | With IDs identical to the board's, Nick's F8 re-links by reference without replacing any kept footprint. `fpextract --verify` checks every board instance: pad numbers, sizes, pad-to-pad distances and exact pad centres after placing the library footprint like the instance, flipped for back-side ones (0 problems; it catches a moved, resized or mirrored pad set). **Expect ≈ 58 graphics-only "footprint doesn't match library" DRC warnings** (QE S4.d F1): the Altium import varies Fab/User-layer graphics and text between instances of one footprint, and Hole_M3's keepouts serialise differently; pads are identical. Don't run "Update Footprints from Library" on kept parts unless graphics-only changes are acceptable. The import also left no SMD/THT attributes and no courtyards (pre-existing, for layout/S6) |
| D20 | 2026-10-05 | I²C pull-ups **fitted**: R26 (I2C1_SCL) and R27 (I2C1_SDA) = Sofar's 4.7 kΩ ERJ-2RKF4701X to the shield's 3V3, same refs, footprint (`Vault:RESC1005X40X25LL05T05`) and fields as on the mote's Processor sheet, so netcheck verifies them against the copper. With the Pi's own pull-ups (Pi Zero 2 W reduced schematic: R23/R24 1.8 kΩ 1 % to the Pi's 3V3 on GPIO2/3) the bus sees ≈ 1.30 kΩ: ≥ R_P(min) 967 Ω at 3.3 V (V_OL ≤ 0.4 V at 3 mA, standard/fast mode; TI SLVA689 Table 1 / Eq. 1), ≈ 2.2 mA at V_OL. Rise time at 1.30 kΩ allows ≤ 272 pF (fast mode, SLVA689 Eq. 2) | Nick: the shield should work with another MCU on the bench, not only the Pi. Back-power with JP1 cut: ≈ 0.6 mA per line into an unpowered Pi (accepted) |
| D21 | 2026-10-05 | **R43 100 kΩ pull-down on ADIN_PWR** (RMCF0402FT100K, R21's part). AP22913 ON has no internal pull-down: input leakage ≤ 1 µA, so R43 holds ≤ 0.1 V, below V_IL 0.4 V (V_IN 1.4–3.6 V); the Pi's 3.3 V high clears V_IH 1.1 V at 33 µA (Diodes DS41203 Rev. 6-2). No resistor on ADIN_RST (the ADIN has an internal pull-up; floating is allowed, Rev. B Table 8) or MISO (SPI_CFG0 strap). CS/RST back-power handled in Pi software, not hardware (Option 1): boot order and rule in "ADIN power and boot" | The mote relied on STM32 firmware to drive ADIN_PWR; R43 keeps the ADIN off whenever the Pi is booting, absent or off, so its straps are read only on a deliberate power-up and INT can't feed an unpowered Pi. Option 1 chosen by Nick 2026-10-05 (Option 2, 1 kΩ series on CS/RST, not taken) |
| D22 | 2026-10-05 | **R10 removed**; TP19 tied straight to SW_EN. On the mote R10 (0 Ω) linked STM32 pin 19 (and, via R9, the mezzanine) to SW_ON, choosing the load-switch controller; R9 went with the mezzanine in S2 | Nick: the Pi header is the only controller; fewer parts, simpler to build. TP19 kept as a bench pad to probe or force SW_EN. **Layout:** route TP19 to SW_EN where R10's footprint was; netcheck can't check this (QE S5.c N1) |
| D23 | 2026-10-05 | **Payload power out on J5, JST GH 2-pin** SM02B-GHS-TB (LCSC C189893), stock footprint `Connector_JST:JST_GH_SM02B-GHS-TB_1x02-1MP_P1.25mm_Horizontal`: pin 1 VBUS_OUT, pin 2 GND (the UrchinCam's J4/J6 order: pin 1 power, pin 2 GND). Rated 1.0 A per contact with AWG #26, 50 V, −40…+105 °C (JST GH datasheet): ≥ the 890 mA requirement (D12) and above U11's ≈ 0.73 A limit; 50 V > the 16–32 V bus. Symbol copied from the UrchinCam into `nereus.kicad_sym` (`nereus:SM02B-GHS`); placed on the **right side of the Top-Level sheet, under the PoDL inserts MP1–MP4**, with a note. **Stock:** LCSC showed C189893 out of stock on 2026-10-06 (QE S5.d F1); recheck in S5.e. **Layout:** silkscreen "VBUS 16–32 V" next to J5 — the same GH 2-pin carries 5 V on the UrchinCam (J6), so a 5 V payload's cable would fit (QE S5.d N2) | On the mote, VBUS_OUT left through mezzanine P1 pins 14/16/18 (removed in S2), so the payload had no exit. Nick: GH series, part and footprint from his UrchinCam design; the 2-pin variant for now (4-pin with paired contacts considered); on the Top-Level sheet for awareness. Mate the cable before potting |
| D24 | 2026-10-06 | **Vault footprint fixes, 3D only** (pads unchanged, so D19's exact-copy check still holds: `fpextract --verify` 0 problems). (1) PoDL threaded inserts MP1–MP4 (Würth 78614015360, WA-SMSI M3; schematic MP1 BM1_P, MP2 BM1_N, MP3 BM2_P, MP4 BM2_N): the embedded model `FST-000629.STEP` had `opacity 0` (invisible); now 1. Model geometry: M3 bore Ø3.0, body Ø6.0 × **1.5 mm** above the board, Ø4.2 × 1.4 mm locating spigot into the Ø4.4 hole. (2) KiCad stock 3D models on footprints that had none: CAPC1608X100X20ML10 (C31) → C_0603_1608Metric; CAPC2013X145X50LL20T25 (C19, C27) → C_0805_2012Metric; CRCW08057R50FKEAHP (R15, R16) → R_0805_2012Metric; RESC1005X40X25LL05T10 (R22, R34, R40), …ML05T10 (R1) and …NL05T10 (R10's, unused, kept for a refit) → R_0402_1005Metric; RESC1608X60X55ML20T10 (R8) → R_0603_1608Metric. All offset 0, rotation 0. **Orientation:** all non-polarised (MLCCs, chip resistors), pads at ±x about the origin, stock models centred with the long axis on x (STEP extents), so model and pads line up. **Heights are generic** (QE S5.g N1): C_0805 1.25 mm vs the footprint's 1.45 mm class, C_0603 0.8 mm vs 1.0 mm; use datasheet heights for potting-depth checks. U2/U3 (AP22913 X1-WLB0909-4, 0.9 mm, 0.5 mm pitch) get **no model**: KiCad has none; footprint and pin map match the datasheet top view (A1 VOUT pin-1 top-left, A2 VIN, B1 GND, B2 ON). **Insert contact (no change, Sofar Q6):** on the mote the inserts sit on B.Cu with unnumbered, net-less pads; the bus reaches each insert position through a **front F.Cu C-shaped arc** on the bus track (~290°, 1.2 mm wide, radius 3.03 mm around the Ø4.4 hole), presumably under the screwed lug (no hardware in the files). So schematic pin 1 of MP1–MP4 has no matching pad, as on Sofar's files. How the new layout should make this contact (copy the ring, net the insert pad, or a ring pad in the footprint) is asked of Sofar first | Nick (2026-10-06): fix the inserts' invisible model; keep R10's footprint; stock models for the others, orientation checked; don't change the insert contact yet, ask Sofar (Q6). An earlier draft numbered the insert pad "1" on the wrong premise that the bus feed went through it (QE S5.g F1); reverted. **Confirmed by Nick in KiCad's 3D viewer (2026-10-06):** the insert model sits body-up on its pad with the spigot in the hole, and the stock models check out (the model is drawn on its Y axis, rotated −90° about X) |
| D25 | 2026-10-06 | **ADIN status LEDs** (ADIN sheet). ADIN_VDDIO → **JP2** (bridged net tie, JP1's footprint `nereus:SolderJumper-2_R1210_Bridged_NetTie`, not in BOM; cut to disable both) → net ADIN_LED_VDD → R44 1.5 kΩ → **D8 red KT-0603R** (Hubei KENTO, LCSC C2286) → GND: lit whenever the ADIN is powered. ADIN_LED_VDD → R45 1.5 kΩ → **D9 yellow-green KT-0603YG** (KENTO, C2289) → ADIN pin 21 (P1_LED_1), active low per ADIN2111 Rev. B Fig. 24, with R3 (4.7 kΩ to ADIN_VDDIO) as the recommended pull-up, so the P1_TX2P4_EN strap still reads high (1.0 V p-p, required with AVDD at 1.8 V). **Port 2 twin (Nick, 2026-10-06):** ADIN_LED_VDD → R46 1.5 kΩ → **D10 KT-0603YG** → ADIN pin 48 (P2_LED_1), with Sofar's R5 as its pull-up (P2_TX2P4_EN strap unchanged); port 2 is in software power-down after reset (R4 strap), so D10 stays dark until the Pi wakes port 2 and enables its LED_1. In a daisy chain D9 and D10 both blink (the internal switch forwards pass-through frames); as a leaf only the cabled port's LED does. Resistors reuse R1's RC0402FR-071K5L. Currents ≈ (3.3 − ~1.9) / 1.5 k ≈ 0.9 mA red, (3.3 − ~2.0 − ~0.1) / 1.5 k ≈ 0.8 mA green (pin sinks up to 8 mA, Table 1): ≈ 6 mW for D8 + D9; while D9 (or D10) is lit its pin also sinks R3's (R5's) ≈ 0.7 mA, so ≈ 1.5 mA at the pin (inside Table 1's 2 mA V_OL test point): ≈ 8 mW with port 1 activity, ≈ 13 mW with both ports active. The green is ≈ 10× dimmer (30–42 mcd vs 300 mcd at 20 mA, scaled linearly; indicative). The feed is ADIN_VDDIO, never the always-on 3V3 (an LED from 3V3 would back-power pins 21 / 48 with the ADIN off); cutting JP2 doesn't touch the straps. LED_1 is disabled by default: the Pi enables it over SPI (DIGIO_LED1_PINMUX, LED1_EN; polarity autosense sees R3 → active low; default function TXRX_ACTIVITY, Table 15). Symbols `Device:LED` (pin 1 K, pin 2 A), footprint `LED_SMD:LED_0603_1608Metric` (pad 1 = cathode); KENTO marks the cathode green (KT-0603R spec sheet). R3 and R5 were redrawn in the LED group (connections unchanged) and U1 pins 21 / 48 got stubs + labels `ADIN_P1_LED1` / `ADIN_P2_LED1` | Nick (2026-10-05/06): red "ADIN powered" + green link/activity, one shared cut jumper to save power, option (a) both 1.5 kΩ. Not pin 19 (P1_LED_0/SPI_CFG1: "use without LED" in OPEN Alliance mode). Not KT-0603G (3.1 V emerald green: too little headroom from 3.3 V). Open: visible after potting? (if not, cut JP2 before potting) |
| D26 | 2026-10-06 | **Sourcing policy for the first build (20 boards).** Critical parts are bought as specified through **JLC global sourcing**: U1, U2/U3, L3/L6, Y1, D1–D3, MP1–MP4, J5 (D1 via Sofar's listed second source Vishay SMA6F33A-M3/H, pending Sofar Q7). Passives keep the specified part on the schematic; generic, pin-compatible, LCSC-stocked alternates are recorded as hidden `ALT…` fields beside it (S5.h) as proposals for Sofar's design review, **at most 3 per part, the best by match and availability** (Nick, 2026-10-06: don't bog reviewers down; Sofar's own listed alternates, e.g. R8's 7, stay in their original fields, outside the BOM). Adopting an alternate for a Sofar part needs constraint 8 (and 7 for power-path parts) amended; bespoke PoDL/power-path parts (R8, R15/R16, C22/C23) are marked "Sofar review". **For the first build every flagged passive is also bought exact via JLC global sourcing** (or consigned) until an alternate is approved, so the order can be placed (**amended by D27**: the first build buys the planned parts after Sofar's review) | Nick: treat it as a design review so Sofar's engineers can weigh in; JLC buys the critical parts, we do the legwork on resistors and capacitors. QE S5.e F1: substitutions of Sofar parts are not allowed under constraints 7/8 without an amendment |
| D27 | 2026-10-06 | **Planned part per BOM line** (S5.i). Every purchased part carries hidden `PLANNED MPN/MFR/LCSC` + `PLANNED NOTE` (why): the part we intend to build with at JLC, beside Sofar's specified part (`Value`, unchanged), so Sofar reviews one diff column. 10 lines change (R34, R20/R39, R21/R35/R37/R43, C31, C17/C26, C21, C16/C18/C24/C25, C19/C27, R14/R18 to LCSC-stocked equivalents; D1 to Sofar's listed Vishay second source); J1 TBD; everything else planned as specified, with its LCSC number. R8 stays as specified: ROHM PMR03's 0.35 mm electrodes fit the UR73D1J pads (0.55 mm electrodes) but ROHM gives no land pattern and the pads reach 0.35 mm under its body. The **first build buys the planned parts after Sofar's review** (amends D26's "exact until approved"); ALT1/ALT2 stay as backups. View "Sofar review (planned parts)" = `bom.csv` | Nick: a single column for Sofar to check the diff, with the why; "your chance to replace the part with what we should use" |
| D28 | 2026-10-06 | **ERC clean by fix or justified exclusion** (S6.b). Title block: name = file name, rev AA, part number PCB-000001-AA (text variables + title-block rev). The 18 remaining errors (FID/MTG pins with no net on the mote board; regulator switch/bootstrap pins and inductor-fed rails the imported symbols type as power input; ADIN_VDDIO driven by U3's passive-typed VOUT) are KiCad ERC exclusions whose comment is the reason. Exclusion keys include the item's position, so `tools/ercexclude.py` regenerates them from `erc_justifications.csv` and `check.sh` fails if they go stale | Nick: S6 "ERC clean, or every remaining item justified"; Sofar's symbols and sheets left as they are (no PWR_FLAGs or pin-type edits) |
| D29 | 2026-10-06 | **Footprint type + courtyard for fab** (S6.c). All 43 `Vault` footprints get a type (KiCad stock conventions: `smd`; fiducial `smd exclude_from_bom`; test pad / mounting hole `exclude_from_pos_files exclude_from_bom`) and an F.CrtYd rectangle taken from Sofar's own outline where one exists (8 courtyard rectangles, 31 outer outlines on the Altium mechanical/User layers), else pads ∪ silk ∪ fab + 0.25 mm (4). Text inserts only; pads verified against the mote board. Board pick-up is Nick's (Update Footprints from Library). Record: `docs/design-review/footprints.md` | QE S4.d N3: JLC's SMD-only position file would drop untyped parts; no courtyard = no overlap DRC. Reuse Sofar's outlines before computing |

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
| 2026-10-05 | S4.d | 74 / 508 | 50/50, 0 opens, 0 shorts; netlist identical except 117 footprint fields (bare → `Vault:`) | Footprint library `Vault` (D19): −118 footprint-link warnings |
| 2026-10-05 | S5.b | 27 / 508 | 50/50, 0 opens, 0 shorts, 0 excluded; 11 nets each gain exactly one J1 pin, nothing else changes | Pi header wired: −29 pin_not_connected (28 J1 GPIO, SW_FLAGB sheet pin), −18 label_dangling (every one-pin I2C1/ADIN net now has the Pi pin). Net names: `Load Switch/SW_ON` → `SW_EN`, `Load Switch/SW_FLAGB` → `SW_FLAGB` (new top-level labels) |
| 2026-10-05 | S5.c | 27 / 508 | **51/51**, 0 opens, 0 shorts, 0 excluded; kept parts' connections identical except TP19 (D22). netcheck can't see TP19's move: its copper net is now TP19 alone, and copper SW_ON has no shared parts left | R26/R27 → I2C1_SCL/SDA + 3V3 (restoring their copper connections: copper nets 50 → 51), R43 ADIN_PWR → GND, R10 removed and TP19 moved onto SW_EN; nothing else changed. ERC counts and types unchanged |
| 2026-10-05 | S5.d | 27 / 508 | 51/51, 0 opens, 0 shorts, 0 excluded; J5 new | J5 added: VBUS_OUT + J5.1, GND + J5.2, nothing else. ERC counts and types unchanged |
| 2026-10-06 | S5.g | 27 / 508 | 51/51 (unchanged; library only) | 8 Vault footprints: 3D models only (D24), pads unchanged; `fpextract --verify` 0 problems |
| 2026-10-06 | S5.f | 27 / 504 | 51/51, 0 opens, 0 shorts, 0 excluded; R3 and R5 keep their connections | LEDs added (D25): new nets ADIN_LED_VDD, Net-(D8-A), Net-(D9-A), Net-(D10-A); the pin-21 / pin-48 nets are now named ADIN_P1_LED1 / ADIN_P2_LED1 and gain D9.K / D10.K; ADIN_VDDIO + JP2.1, GND + D8.K. ERC errors unchanged; warnings −4 (−3 each for the R3 and R5 groups now on grid, +1 each for the pin-21 / pin-48 stubs on U1's off-grid y) |
| 2026-10-06 | S5.e | 27 / 504 | unchanged (docs only) | Lifecycle + stock check of all 50 BOM parts (20 boards) → `docs/design-review/bom_lifecycle.md`; sourcing decisions open |
| 2026-10-06 | S5.h | 27 / 504 | 51/51, 0 opens, 0 shorts; netlist identical except 208 new hidden fields | BOM alternates (D26): `ALT…` + `SOURCING` fields on 24 flagged passives, `SOURCING` on the critical parts; tracked `bom.csv` from `tools/check.sh`. ERC items identical (only `multiple_net_names` cites a different copy of a repeated label; KiCad varies it run to run) |
| 2026-10-06 | S5.i | 27 / 504 | 51/51, 0 opens, 0 shorts; netlist identical except 428 new PLANNED fields and 19 SOURCING values | Planned parts (D27). ERC items identical with locations stripped |
| 2026-10-06 | S6.a | 27 / 504 | 51/51; netlist + 26 exclude_from_bom markers + MANUFACTURER fields only | BOM hygiene: TP/FID/MTG out of the BOM; Mfr filled; bom.csv 51 rows |
| 2026-10-06 | S6.b | **0** / 504 | 51/51; netlist: title-block revs + 3 text variables only | ERC clean (D28): 9 title-block errors fixed, 18 excluded with reasons; warnings item-for-item unchanged |
| 2026-10-06 | S6.c | 0 / 504 | 51/51 (unchanged; library only) | 43 Vault footprints: type + F.CrtYd added (D29); `fpextract --verify` 0 problems |
| 2026-10-06 | S6.d | 0 / 495 | 51/51; netlist identical (nets and pins) | Minor tidy: positions, text, notes, 9 dangling wire ends removed (warnings −9, no new items); #PWR34's exclusion key regenerated (reason unchanged) |
| 2026-10-06 | S6.e | 0 / 495 | 51/51; netlist identical except 5 Description values | Review package: README, schematic.pdf, new-nets table in netcheck.md; jumper descriptions fixed |

**ERC errors after S6.b: 0** (D28). The 9 title-block `unresolved_variable` errors are fixed (text variables
`PCBPARTNAME` = nereus_Pi_shield_ADIN2111, `PCBPARTNUMBER` = PCB-000001-AA, `PROJECTREVISION` = AA; title-block rev AA on
all 7 sheets; Nick, 2026-10-06). The other 18 are KiCad ERC exclusions, each with its reason as the exclusion comment
(visible in KiCad's ERC dialog), generated from `docs/design-review/erc_justifications.csv` by `tools/ercexclude.py`:

| Type | # | What | Reason |
|---|---|---|---|
| pin_not_connected | 6 | FID1–6 hidden NC pin | fiducial copper mark, no net on the mote board |
| pin_not_connected | 4 | MTG1–4 pin | M3 plated hole, no net on the mote board |
| power_pin_not_driven | 1 | #PWR34 ADIN_VDDIO | driven by U3 VOUT, typed passive in the imported symbol |
| power_pin_not_driven | 5 | U5/U10 SW + CB, U6 SW | switch node / bootstrap, driven by the regulator itself |
| power_pin_not_driven | 2 | U6 VIN (3V3), VOS (1V8) | rails fed through inductors L3/L4 (passive pins) |

History: 27 errors after S5.b (pin_not_connected 10, power_pin_not_driven 8, unresolved_variable 9).
S2's PWR_FLAGs cleared U5 VIN (VBUS) and U6 GND.

Warnings (508) are cosmetic import leftovers: 485 off-grid endpoints (Altium
coordinates such as `…0.0022`; +2 in S2 where the trimmed I2C1 wires end on
off-grid label anchors; +57 in S4.a, the U10 copy keeps U5's off-grid offset),
0 footprint-library links (all 118 cleared in S4.d: every footprint field now
names a real library), 11 dangling wire ends
(all pre-existing), 12 duplicate net names (e.g. `PHY1_P`/`BM1_P` on the same wire).
