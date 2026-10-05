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

**Net-check method:** *(S0.3)* Note: ERC reports aren't deterministic run to
run (same violations, different example labels), so compare ERC by counts and
types; nets are compared from the exported netlist only.

## Decision log

| # | Date | Decision | Rationale |
|---|---|---|---|
| D1 | 2026-10-04 | Agents own schematic capture up to the design-review package; Nick owns review, board and bring-up | Clear boundary; the board is Nick's |
| D2 | 2026-10-04 | TRACKER.md is the single source of truth; the checklist HTML is reference only | The HTML saves progress in a browser, which agents can't see |
| D3 | 2026-10-04 | Live project folder is `nereus_Pi_shield_ADIN2111/` (renamed from `_002` in S0.1) | One stable name; git keeps the history |
| D4 | 2026-10-04 | 5 V for the Pi: copy of the LMR51430 (U5) set to 5 V, fed from VBUS | Reuses a proven block (checklist Option A) |
| D5 | 2026-10-04 | 5V_PI reaches Pi pins 2/4 through an open solder jumper | Must stay open whenever the Pi has its own USB power |
| D6 | 2026-10-04 | Plain 2×20 female socket header, no stacking header | Shield plugs onto the Pi's male pins |
| D7 | 2026-10-04 | Target ~50 W with two-winding PoDL inductors, one per port; selection in POWER_PATH.md | Commercial mote magnetics limit it to ~20 W |
| D8 | 2026-10-04 | Rating (P1): ~50 W **absolute max** = 2.083 A per port inductor at 24 V, defined like Sofar's 20 W. Margin comes from choosing larger magnetics (MSD1514-class, fit pending) | Same basis as the mote's rating; potting removes thermal headroom |
| D9 | 2026-10-04 | Electronics are potted. Sofar-vetted parts are kept as-is (including the C22/C23 electrolytics). Newly sourced parts: no aluminium electrolytics, no PPTCs, other risky parts flagged (SPEC constraint 8) | Vetted design is trusted; electrolytics vent or deform under pressure; PPTC trip behaviour changes when encapsulated |

## ERC / net-check results

| Date | Sprint | ERC errors / warnings | Net diff vs copper | Notes |
|---|---|---|---|---|
| 2026-10-04 | S0.1 | 90 / 578 before and after the rename | Netlist identical apart from the library path | Rename confirmed safe; not the S0.4 baseline |
