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
    └── BM_Mote_1_Load                  U9 24 V payload switch

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
| 36 | 16 | SW_EN (low = payload on) |
| 38 / 40 | 20 / 21 | SW_FLAGB / SW_PGOOD |
| 2 / 4 | — | 5V_PI via solder jumper |
| 6, 9, 14, 20, 25, 30, 34, 39 | — | GND |
| 1, 17 | — | **unconnected** (Pi 3.3 V) |

Reserved: 26 (CE1), 29, 32, 33 (motor). Avoid: 27, 28 (HAT EEPROM), 8, 10 (console).

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
| D5 | 2026-10-04 | 5V_PI reaches Pi pins 2/4 through an open solder jumper | Must stay open whenever the Pi has its own USB power |
| D6 | 2026-10-04 | Plain 2×20 female socket header, no stacking header | Shield plugs onto the Pi's male pins |
| D7 | 2026-10-04 | Target ~50 W with two-winding PoDL inductors, one per port; selection in POWER_PATH.md | Commercial mote magnetics limit it to ~20 W |
| D8 | 2026-10-04 | Rating (P1): ~50 W **absolute max** = 2.083 A per port inductor at 24 V, defined like Sofar's 20 W. Margin comes from choosing larger magnetics (MSD1514-class, fit pending) | Same basis as the mote's rating; potting removes thermal headroom |
| D10 | 2026-10-05 | Every PR gets an independent, read-only Quality Engineer review in a separate Code session (never a sub-agent; `.claude/agents/quality-engineer.md`, Opus 5.5, high effort) before Nick's KiCad review; merge needs both | A second pair of eyes on every claim; QE never edits, so it can't collide with Nick or the design agent |
| D11 | 2026-10-05 | The shield provides I2C pull-ups on I2C1_SDA/SCL (S5), reusing the mote's R26/R27: 4.7 kΩ ERJ-2RKF4701X to 3V3 | Nick: the Pi needs them; the mote's pull-ups were on the removed STM32 sheet |
| D9 | 2026-10-04 | Electronics are potted. Sofar-vetted parts are kept as-is (including the C22/C23 electrolytics). Newly sourced parts: no aluminium electrolytics, no PPTCs, other risky parts flagged (SPEC constraint 8) | Vetted design is trusted; electrolytics vent or deform under pressure; PPTC trip behaviour changes when encapsulated |

## ERC / net-check results

| Date | Sprint | ERC errors / warnings | Net diff vs copper | Notes |
|---|---|---|---|---|
| 2026-10-04 | S0.1 | 90 / 578 before and after the rename | Netlist identical apart from the library path | Rename confirmed safe; not the S0.4 baseline |
| 2026-10-05 | S0.4 | 90 / 578 | 42/68 matched; **26 opens**, 0 shorts, 0 unpaired; 43 parts removed, 4 new | **Baseline.** Details in `docs/design-review/netcheck.md`. S1 target: 0 opens |
| 2026-10-05 | S1 | 65 / 590 | **53/53 matched, 0 opens, 0 shorts** (14 S2-deletion parts excluded); midwire 0 | Import fixed. Edits in `docs/design-review/changelog.md` |
| 2026-10-05 | S2 | 76 / 562 | 53/53, 0 opens, 0 shorts, **0 excluded**; J1 GND 8/8 on GND | Mezzanine gone, J1 placed. +29 errors are J1 pins awaiting S4/S5 |

**Remaining ERC errors after S2 (76), and who resolves each:**

| Type | # | What | Resolved by |
|---|---|---|---|
| pin_not_connected | 33 | J1: 28 GPIO pins + pin 4 (5V); MTG1–4 mounting holes | S4 (5V), S5 (GPIO); MTG1–4 Nick (board) |
| label_dangling | 18 | ADIN_MISO/MOSI/NSS/RST/SCK and the ADIN sheet's CS/MISO/MOSI/SCK/RST; I2C1_SCL/SDA and the Power Monitor sheet's SCL/SDA: each net has one pin until the Pi header is wired | S5 |
| power_pin_not_driven | 8 | J1.2 (5V); U9.8 VOUT; U5 CB/SW; U6 VIN/SW/VOS (switch nodes / regulator-fed rails with no power-output pin) | S4 (J1.2); remainder justified or flagged in S6 |
| unresolved_variable | 9 | Title block `${PCBPARTNAME}` ×1, `${PCBPARTNUMBER}` ×8 | Needs a name/part number from Nick (S6) |

S2's PWR_FLAGs cleared U5 VIN (VBUS) and U6 GND.

Warnings (590) are cosmetic import leftovers: 426 off-grid endpoints (Altium
coordinates such as `…0.0022`), 126 footprint-library links, 26 dangling wire
ends, 12 duplicate net names (e.g. `PHY1_P`/`BM1_P` on the same wire).
