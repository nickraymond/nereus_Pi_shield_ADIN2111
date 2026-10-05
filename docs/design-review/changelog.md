# Schematic change log

*Every edit to the live schematic, newest sprint first. Part of the S6 design-review package.*

## S5.a — Payload load switch: U9 → U11 TPS26621, R11 DNP (2026-10-05, branch `sprint/5a-u9-replacement`)

Load Switch sheet (`BM_Mote_1_Load.kicad_sch`), D18:

| Change | Detail |
|---|---|
| U9 FPF2700MX removed | Obsolete (Digi-Key) |
| **U11 TPS26621DRCR** added at (226.06, 149.68) | New project symbol `nereus:TPS26621DRCR` (new `nereus.kicad_sym` + sym-lib-table entry); stock footprint `Package_SON:Texas_DRC0010J`; LCSC C1848341. Pins placed on U9's old wire ends: IN/ILIM/SHDN/RTN left, OUT/dVdT/FLT/OVP right, GND/EP down to the GND rail |
| R34 | 374 kΩ → **9.09 kΩ RC0402FR-079K09L** (0.73 A) |
| **R41** 1 MΩ (stock `Device:R`, 0402, RC0402FR-071ML) | IN → UVLO, tapping the VIN riser (split + junction) |
| dVdT | no-connect flag (floating = internal ramp) |
| R32 → **R42**, its 3V3 symbol → GND (#PWR76) | Pull-down instead of pull-up (SHDN active low) |
| R33, TP34, label + hierarchical label SW_PGOOD, #PWR65, 4 wires, 1 junction removed | No PGOOD on TPS26621 |
| Note text | "Ilim (R34 9.09k): typ 0.73A, −6/+4 %, TPS26621 D18" |

Top-Level sheet: **R11 DNP**; SW_PGOOD pin removed from the Load Switch sheet symbol.
**Verified:** kept parts' connections identical; new nets only `Net-(U11-UVLO)` and the
floating dVdT; VBUS + R41.1, U11.1; VBUS_OUT + U11.10; GND + R42.2, U11.3/5/6/11;
SW_ON + R42.1, U11.4; SW_FLAGB + U11.9; ISET + U11.7. ERC 76/629 → 74/626; netcheck
50/50, 0 opens, 0 shorts.

## S4.c — Power budget (2026-10-05, branch `sprint/4c-power-budget`)

No schematic edit. New `docs/design-review/power_budget.md`. `tools/check.sh`: ERC 76/629,
netcheck 53/53, same as S4.b.

## S4.b — Shield powers the Pi through JP1 (2026-10-05, branch `sprint/4b-pi-5v-jumper`)

Top-Level sheet (`BM_Mote_1_Master.kicad_sch`), above J1 (DESIGN D14):

| Added | Detail |
|---|---|
| JP1 `Jumper:SolderJumper_2_Bridged` (KiCad 9.0.6 stock) at (120.65, 40.64) | Not in BOM. Pin 2 → `5V_PI` label; pin 1 → J1 pin 2 (5V, pin 4 stacked) |
| Net `PI_5V` | label on the tap to #FLG03 (PWR_FLAG); J1.2, J1.4, JP1.1 |
| Text note | "JP1 bridged as built … cut … refit a 0R 1210 (CRCW12100000Z0EA)" |
| Footprint `nereus:SolderJumper-2_R1210_Bridged_NetTie` (new `nereus.pretty` + project `fp-lib-table`) | Pads from the mote's R11 (1.2049 × 2.7062 mm at ±1.45065 mm, read from the reference board), 1.0 mm F.Cu bridge, net tie "1, 2", mask opened over the bridge, no paste, excluded from BOM and position files. Loads in kicad-cli (`fp export svg`) |

Tool: `midwire.lib_pins` skipped any library symbol whose name ends in `_<n>_<n>`
(`Raspberry_Pi_2_3`), so J1's pins were invisible to midwire, the island graph and
`bbox_clear`. Fixed and tested; midwire still 0 with J1's 40 pins included.
**Verified:** existing connections identical; `PI_5V` = J1.2, J1.4, JP1.1; `5V_PI`
gains JP1.2; ERC −2 errors (J1 pin 2), warnings unchanged. netcheck 53/53.

## S4.a — 5 V converter for the Pi (2026-10-05, branch `sprint/4-5v-converter`)

Power sheet (`BM_Mote_1_Power.kicad_sch`): the U5 block copied 76.2 mm down with
`tools/schedit.py copy_block` (new refs, renamed labels, fresh uuids), then values
set (DESIGN D13). Top-Level sheet: new sheet pin and test point.

| Added | Copy of | Value / change |
|---|---|---|
| U10 | U5 | LMR51430YDDCR (same) |
| L6 | L3 | PA5432.822NLT 8.2 µH (same) |
| R37, **R38** | R21, R23 | 100 kΩ (same); **13.7 kΩ RC0402FR-0713K7L** (was 22.1 kΩ) → 4.98 V |
| R39, R40 | R20, R22 | 1.82 MΩ / 200 kΩ enable divider (same) |
| C53, C54, C55 | C28, C29, C30 | bootstrap 100 nF 25 V; input 100 nF 100 V, 2.2 µF 50 V (same) |
| **C56, C57** | C31 | **22 µF 16 V X5R 0805 GRM21BR61C226ME44L** (was 22 µF 6.3 V 0603); C57 is an extra one; stock KiCad footprint `C_0805_2012Metric` |
| **C58** | C33 | **4.7 µF 10 V X5R 0402 GRM155R61A475MEAAD** (was 6.3 V); `C_0402_1005Metric` |
| #PWR68–#PWR75 | GND symbols | for the copied parts |
| Labels | `3V3_Buck_Input/SW/UVLO/FB` | → `5V_*`; VBUS hierarchical label reused |
| Hierarchical label `5V_PI` + sheet pin | `3V3` | Power Regulators sheet pin at (353.06, 198.12) on the Top-Level sheet |
| TP38 | TP20 | test point on `5V_PI`, with a `5V_PI` label for S4.b |

After QE round 1: C58 and its GND symbol sit one grid (2.54 mm) right of the first
placement, at x = 254, with its 10 V rating shown; stale hidden 0603 size fields
removed from C56/C57 (`set_properties` had skipped values containing `\"`).

Also: TP23/TP24 and their GND symbols (#PWR01, #PWR03) moved 7.62 mm down on the
Top-Level sheet to clear the new wire (placement only, same connections); sheet
title now "Buck Converters - 3V3, 1V8, 5V". **Verified:** every existing part's
pin-to-net grouping identical; new nets exactly `5V_PI` (C56.2, C57.2, C58.1,
L6.2, R37.1, TP38.1), `5V_Buck_SW`, `5V_FB`, `5V_UVLO`, `Net-(U10-CB)`; VBUS and
GND gain only the new parts. netcheck 53/53.

## S3 — Power path kept as Sofar's (2026-10-05, branch `sprint/3-power-path`)

No schematic edit. Nick decided this board keeps the mote's power path unchanged
(DESIGN D12), so L1/L2 (SRF1260-101M) and every other power-path part stay as
imported. `tools/check.sh`: ERC 76/562, netcheck 53/53, same as S2.

## S2 — Mezzanine (P1) → Pi header (2026-10-05, branch `sprint/2-pi-header`)

All edits on the Top-Level sheet (`BM_Mote_1_Master.kicad_sch`), made with `tools/schedit.py`.

### S2.1 Mezzanine deleted

| Removed | Items |
|---|---|
| Parts | P1 (DF17 30-pin mezzanine, 2 units), R9 (0 Ω, MZ_ADC_EXTRA → R10), TP4, 6, 9, 10, 11, 12, 14, 15, 16, 17, 18, 33 |
| Labels | BM_INT, BOOT, I2C_MUX_RST, IOEXP_INT, LPUART1_RX, LPUART1_TX, MCU_RESET, MZ_ADC_EXTRA, MZ_BM_CS, MZ_BM_MISO, MZ_BM_MOSI-TX3, MZ_BM_SCK-RX3, PAYLOAD_DE_CTS, PAYLOAD_RE_RTS |
| Power symbols that fed only P1 | #PWR04, #PWR07, #PWR11, #PWR13 (GND); #PWR12 (3V3 to the mezzanine) |
| Other | 2 no-connect flags on P1; 69 wires; 12 junctions left with < 3 connections |

Kept: R10 and TP19 (still on SW_ON), the I2C1_* and ADIN_* labels, the VBUS_OUT
wiring to R11/TP36. Wire stubs that ran to P1 were trimmed back to the label
or junction on them. **Verified:** all 277 kept pins have exactly the same
connections before and after; the only nets that disappeared are the 14
mezzanine nets. The netcheck exclusion list is now empty.

### S2.2 Pi header placed

| Added | Detail |
|---|---|
| J1 `Connector:Raspberry_Pi_2_3` at (121.92, 88.9) | Footprint `Connector_PinSocket_2.54mm:PinSocket_2x20_P2.54mm_Vertical`; symbol copied from KiCad 9.0.6's library |
| #PWR66 GND (+ junction) | At J1's stacked GND pins: 6, 9, 14, 20, 25, 30, 34, 39 → GND |
| No-connect flag at (127, 55.88) | J1 pins 1 and 17 (Pi 3V3) stay unconnected, never tied to the shield's 3V3 |
| #FLG01 PWR_FLAG on GND, #PWR67 VBUS + #FLG02 PWR_FLAG | Tells ERC these nets have a source |

J1 pins 2/4 (5V) are left for S4; the 28 GPIO pins for S5.

### S2.3 QE round 1 fixes

- Deleted the stale `MEZZANINE` text box (section header of the old mezzanine area, (115.57–181.61, 175.26)). Netlist and ERC unchanged.
- ERC accounting corrected (see DESIGN.md); new `tools/ercsum.py` builds those tables.

### S2 result

| Check | Before S2 | After S2 |
|---|---|---|
| netcheck | 53/53, 14 parts excluded | **53/53, 0 opens, 0 shorts, 0 excluded** |
| ERC errors / warnings | 65 / 590 | 76 / 562: −27 (12 TPs, 13 mezzanine labels, U5 VIN, U6 GND) / +38 (29 J1 pins, 8 I2C1/SCL/SDA labels now one-pin, J1.2) |
| J1 GND pins on GND | — | 8/8 (netlist) |

## S1 — Fix the Altium import (2026-10-05, branch `sprint/1-import-fix`)

### S1.1 Pins that sat mid-wire, now connected (21 locations)

Altium connects a pin that touches a wire anywhere along it; KiCad only
connects at wire ends, so the import left these pins unconnected. At each
location the wire was split at the pin end and a junction added
(`tools/midwire.py --fix`). Result: netcheck went from 39/53 matched with
14 opens to 53/53 matched with 0 opens and 0 shorts.

| Sheet | Location (mm) | Pins now connected |
|---|---|---|
| ADIN2111 | (124.46, 73.4822) | R1.1 |
| ADIN2111 | (215.9, 228.4222) | C13.1 |
| ADIN2111 | (226.06, 228.4222) | C14.1 |
| Load | (152.4, 134.4422) | C49.1 |
| Load | (261.62, 164.9222) | R33.1, TP34.1 |
| Load | (271.78, 134.4422) | C50.1 |
| Load | (279.4, 172.5422) | TP35.1, R35.1 |
| Load | (292.1, 134.4422) | D3.1 |
| Master | (124.46, 205.74) | TP36.1 |
| Master | (292.1, 119.38) | TP8.1 |
| Master | (304.8, 187.96) | TP22.1 |
| Master | (368.3, 185.42) | TP20.1 |
| Master | (378.46, 190.5) | TP21.1 |
| Master | (472.44, 104.14) | TP3.1 |
| Master | (472.44, 106.68) | TP5.1 |
| Master | (472.44, 121.92) | TP7.1 |
| Master | (472.44, 124.46) | TP13.1 |
| PoDL | (43.18, 63.3222) | D4.1 |
| PoDL | (43.18, 175.0822) | D5.1 |
| PowerMon | (177.8, 149.6822) | R8.2 |
| PowerMon | (177.8, 159.8422) | R8.1 |

**Why not the original junction fix?** `Archive/shield_junction_fix.zip`
marks the same 33 locations (these 21 plus 12 on parts S2 deletes) with
junctions only. It had never been applied to the live project. Tested one
junction at a time in KiCad 9.0.6, each one connects its pin but most also
disconnect a neighbouring pin on the same wire (e.g. the C49.1 junction drops
U9.1 off VBUS). Splitting the wire at the pin connects it with no side effects.

### S1.2 Orphan sheet files deleted

`BM_Mote_1_Processor.kicad_sch` and `BM_Mote_1_USB.kicad_sch` were not
referenced by any sheet or by the project file. Deleting them changed neither
the ERC counts nor the netlist.

### S1.3 Power symbols numbered

All 65 power symbols had the same reference, `#PWR?`, in both the
property and the instance record (the checklist's "65 duplicate references").
They are now `#PWR01`–`#PWR65` in hierarchy order (Master 01–17, Power 18–27,
ADIN2111 28–50, PoDL 51–57, PowerMon 58, Load 59–65). ERC counts and the
netlist are unchanged.

### S1.4 ADIN_VDDIO label — verified, not changed

The plain label `ADIN_VDDIO` on the ADIN2111 sheet sits on the C13/C14 wire,
and the netlist has one `ADIN_VDDIO` net holding U3.A1 (switch output),
U1.18/U1.46, the R1/R3/R5/R6 pull-ups, TP2, C13 and C14, matching the copper.
The checklist's goal (pull-ups powered from ADIN_VDDIO) is met, so the label
was left as it is.

### S1 result

| Check | Before S1 | After S1 |
|---|---|---|
| netcheck (excl. S2 deletions) | 39/53 matched, 14 opens | **53/53, 0 opens, 0 shorts** |
| Pins mid-wire (kept parts) | 21 | **0** |
| ERC errors / warnings | 90 / 578 | 65 / 590 |
| Unnumbered power symbols | 65 | 0 |
