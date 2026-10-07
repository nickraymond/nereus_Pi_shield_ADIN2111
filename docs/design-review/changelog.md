# Schematic change log

*Every edit to the live schematic, newest sprint first. Part of the S6 design-review package.*

## S6.e — Review package (2026-10-06, branch `sprint/6e-review-package`)

| Change | Where |
|---|---|
| Description "RES SMD 205K OHM 1% 1/2W 1992" (Altium import, wrong) → "RES SMD 0 OHM JUMPER 1210" | R11 (Top-Level), R12, R13, R17, R19 (PoDL): the CRCW12100000Z0EA 0 Ω jumpers |
| `netcheck.md` gains "Schematic nets with new parts": every net touching a part not on the mote board, with all its pins (unconnected single pins collapsed into one row) | `tools/netcheck.py` (+ test) |
| Package index `docs/design-review/README.md`; reviewed snapshot `docs/design-review/schematic.pdf` (rev AA) | docs |

**Verified:** netlist identical except the 5 Description values; ERC 495/0/495; ercexclude 18/0/0/0; netcheck 51/51;
midwire 0; tool tests OK.

## S6.d — Minor schematic tidy (2026-10-06, branch `sprint/6d-tidy`)

Nick: small readability fixes on Sofar's design, no overhaul. Positions, text and dead wires only.

| Sheet | Change |
|---|---|
| Top-Level | R27 / R26 moved onto J1's I2C1_SDA / I2C1_SCL stubs (wire from the stub label straight into each resistor, then 3V3); their floating copies' labels and wires removed; text on one line above (R27) / below (R26) |
| Top-Level | dead `3V3` stub removed (#PWR06, 3 wires, 1 junction: no pins on it) |
| Top-Level | ADIN_MISO/MOSI/SCK/NSS/RST/INT wires start at their labels (were 25 mm dangling lead-ins from x 269.24); dead ADIN_PWR lead-in left of TP8 removed, and the junction there (now redundant; QE N2) |
| Top-Level | note "Processor + onboard logic runs off 3V3, and ADIN AVDD off 1V8." → "Shield logic runs off 3V3; ADIN AVDD runs off 1V8." (box 12.7 → 7.62 mm tall) |
| Top-Level | bus note: Sofar's 3 lines at the J5 note's font size (2.286 → 1.27 mm), box 19.05 → 8.89 mm: no longer wraps to 5 lines |
| ADIN | D10 + R46 moved to an even 17.78 mm pitch (x 388.62 → 358.14); R3 / R5 rotated vertical under D9 / D10 (pin 1 on the cathode node), ADIN_VDDIO symbols (#PWR49 / #PWR34) below them; R5's separate ADIN_P2_LED1 label + wire removed (R5 now on the node) |
| ADIN | ADIN_LED_VDD label moved off the D9 junction (x 327.66 → 342.9; wire split moved with it) |
| ADIN | R4 / R6 text off their pins: R6 in R2's layout; R4 on one line above its wire (the ADIN_P2_LED1 stub label is below) |
| ADIN | "Set for 1Vp-p comms." note widened 27.94 → 33.02 mm (it wrapped into the SWPD note below) |
| .kicad_pro | #PWR34's ERC exclusion key regenerated (`ercexclude.py --write`): position 198.12 → 200.66 mm, reason unchanged |

**Verified:** nets identical (all 109, same pins) after every step; ERC 504/0/504 → **495/0/495**: the 9 removed items are
all `unconnected_wire_endpoint` (the dead stub and lead-ins), no item added; ercexclude 18/0/0/0 (only #PWR34's key
changed); netcheck 51/51; midwire 0. Each change checked in a rendered SVG. Not done (more than minor): J1 moved to the
right of the sheet; Sofar's 2 PoDL wire ends.

## S6.c — Footprint types and courtyards (2026-10-06, branch `sprint/6c-footprints`)

Library `mote.pretty` (`Vault`) only, D29; no schematic or pad change. 43 footprints: one `(attr …)` line and four F.CrtYd
`fp_line`s each, inserted as text (0 lines removed). Per-footprint type, courtyard size and source:
`docs/design-review/footprints.md`. New `tools/fpattrs.py` (+ `test_fpattrs.py`). `nereus.pretty`'s jumper already had both.

**Verified:** `fpextract --verify` 0 problems (pads identical to the mote board); every written file re-loaded with pcbnew
(type and 4 courtyard lines read back); a second run changes nothing; `check.sh` unchanged (504/0/504, 51/51, midwire 0).

## S6.b — ERC clean or justified (2026-10-06, branch `sprint/6b-erc`)

| Change | Where |
|---|---|
| Title block rev `=ProjectRevision` (Altium placeholder) → `AA` | all 7 sheets (`title_block`) |
| Text variables `PCBPARTNAME` = nereus_Pi_shield_ADIN2111, `PCBPARTNUMBER` = PCB-000001-AA, `PROJECTREVISION` = AA (Nick) | `.kicad_pro` `text_variables` |
| 18 ERC exclusions, comment = reason (FID1–6, MTG1–4, #PWR34, U5/U10 SW+CB, U6 SW/VIN/VOS) | `.kicad_pro` `erc.erc_exclusions`, from `docs/design-review/erc_justifications.csv` |
| New `tools/ercexclude.py` (+ `test_ercexclude.py`): regenerates / checks the exclusions; `check.sh` runs the check | tools |

**Verified:** ERC 531 / 27 / 504 → **504 / 0 / 504**; the 504 warnings item-for-item unchanged. Netlist: the 7 revs and 3
text variables only; nets identical. netcheck 51/51; midwire 0. A deliberately stale exclusion makes `check.sh` exit 1
with ERC 1 error. Title blocks render "Rev: AA" and PCB-000001-AA on every sheet (SVG export). Still showing:
"=ProjectAuthor" (needs a name from Nick).

## S6.a — BOM hygiene (2026-10-06, branch `sprint/6a-bom-hygiene`)

Six sheet files (root untouched); flags and one field only. No connection, value or footprint changed.

| Change | Refs |
|---|---|
| `(in_bom yes)` → `(in_bom no)`: bare copper pads and holes, not purchased | TP1–3, TP5, TP7, TP8, TP13, TP19–24, TP35, TP36, TP38; FID1–6; MTG1–4 (26) |
| + `MANUFACTURER` (hidden), from `bom_lifecycle.md`'s Mfr column (S5.e, Digi-Key-checked) | the 75 BOM parts (76 blocks, U1 ×2) with no `MANUFACTURER`; J1 has no part yet. Sofar's `MFR_NAME` (U5/U10), `MANUFACTURER1` (D1: its *second source*, Vishay) and `MANUFACTURER 1` (R15/R16) untouched; D1's `MANUFACTURER` = STMicroelectronics (its specified part) |

**Verified:** structural compare against `main`: 26 `in_bom` flips, 76 appended hidden `MANUFACTURER` fields, nothing else.
Netlist: + 26 `exclude_from_bom` markers and the new `MANUFACTURER` fields only. ERC 531 / 27 / 504, items identical
with locations stripped (one `multiple_net_names` item names VBUS or 5V_Buck_Input as the second label from run to run on
the unchanged base too). netcheck 51/51; midwire 0. `bom.csv` 51 rows (TP/FID/MTG rows gone), `Mfr` blank only on J1.

## S5.i — Planned part per BOM line (2026-10-06, branch `sprint/5i-planned-parts`)

Six sheet files (root sheet untouched); fields only (D27). No connection, value or footprint changed.

| Change | Refs |
|---|---|
| + `PLANNED MPN`, `PLANNED MFR`, `PLANNED LCSC`, `PLANNED NOTE` (hidden) | all 106 purchased parts (U1 on both units); not TP/FID/MTG or JP1/JP2 |
| `SOURCING` → "Planned part from LCSC once Sofar approves it (D27); until then the specified part via JLC global sourcing" | the 19 parts on the 9 changed passive lines |
| `Footprint` property line re-indented 4 → 2 tabs (whitespace only) | U11, R41, C56, C57, C58 (S4/S5 leftovers; `set_properties` refuses a symbol with an unparsed property) |
| `.kicad_pro`: view renamed "Sofar review (planned parts)": Refs, Qty, Value (MPN), Mfr, **Planned MPN/Mfr/LCSC, Planned note**, DNP, Sourcing, Alt1/Alt2, Alt note, Footprint (the specified part's LCSC column dropped: Planned LCSC replaces it) | `bom_presets` + `bom_settings` |
| `tools/check.sh` exports `bom.csv` with `--preset "Sofar review (planned parts)"` (one definition for the view and the file; fails with a restore hint if KiCad dropped the preset) | — |

**Verified:** 428 fields added (107 blocks × 4); a structural compare against `main` finds every other existing
property unchanged and in order, nothing outside symbol blocks changed, every new field hidden. Netlist: the only removed
lines are the 19 old `SOURCING` values; all other lines added are the new fields. ERC 531 / 27 / 504, items identical
with locations stripped; netcheck 51/51; midwire 0. `bom.csv` (54 rows) reproducible; 11 rows where Planned ≠ Value
(the 10 changes + J1 TBD).

## S5.h — BOM alternates as hidden fields (2026-10-06, branch `sprint/5h-bom-fields`)

Six sheet files (the root `nereus_Pi_shield_ADIN2111.kicad_sch` untouched); fields only (D26, `docs/design-review/bom_alternates.md`). No connection, value or
footprint changed. Every new field is hidden, at the symbol origin.

| Change | Refs |
|---|---|
| + `ALT1 MPN`, `ALT1 MFR`, `ALT1 LCSC`, `ALT2 MPN`, `ALT2 MFR`, `ALT2 LCSC`, `ALT NOTE`, `SOURCING` ("JLC global sourcing (first build) until an ALT is approved (D26)") | 24 flagged passives: R34 (Load); R20, R39, R21, R37, C31 (Power); R35 (Load); R43 (Master); R8 (PowerMon); C16–C19, C21–C27, R14–R16, R18 (PoDL) — values per `bom_alternates.md`; empty where it lists no alternate (R20/R39 and R15/R16 ALT2, C22/C23 both) |
| + `SOURCING` only | U1 (both units), U2, U3, Y1 (ADIN2111); L3, L6 (Power); D1, D2 (PoDL); D3 (Load); MP1–MP4, J5, J1 (Master) |
| J1 `Footprint` property line re-indented 4 → 2 tabs | whitespace only (import leftover, like JP1 in S5.f); `set_properties` refuses a symbol with an unparsed property |
| `tools/check.sh` exports `docs/design-review/bom.csv` (tracked) | `Value (MPN)` = the specified part, then Mfr, LCSC, Sourcing, Alt1/Alt2 MPN/Mfr/LCSC, Alt note; grouped by Value and DNP |

| `.kicad_pro`: Symbol Fields Table view **"Sofar review (alternates)"** (`bom_presets`), also the view the dialog opens with (`bom_settings`, was "Default Editing") | Refs, Qty, Value (MPN), Mfr, LCSC, DNP, Sourcing, Alt1/Alt2 MPN/Mfr/LCSC, Alt note, Footprint; grouped by Value + DNP; BOM-excluded parts (JP1/JP2) hidden. `kicad-cli sch export bom --preset "Sofar review (alternates)"` gives the same 54 groups as `bom.csv`, every cell equal. Added after Nick's look: new fields need their columns switched on, and the ones he enabled landed after the wide Footprint/Datasheet columns |

Field text follows `bom_alternates.md` except: C22/C23 `ALT NOTE` leaves out the plan's "(DK 78,606)" (stock figures drift; it stays in
the plan); R8 `ALT NOTE` is "Sofar review: power-path current sense; check land pattern" (Nick: at most 3 alternates per part; R8's
7 Sofar fields `MANUFACTURERPARTNUMBER1–7` stay untouched, outside bom.csv).

**Verified:** 208 fields added (24 × 8 + 16 SOURCING blocks); a structural compare against `HEAD` finds every existing
property of every symbol unchanged and in order, nothing outside symbol blocks changed, and every new field hidden.
Netlist diff: 0 lines removed; all 414 added lines are the new fields (component `property` + libpart `field`). ERC
531 / 27 / 504, item-for-item identical to the baseline apart from which copy of a repeated label `multiple_net_names`
cites (KiCad's choice varies between runs on the same file); netcheck 51/51; midwire 0.

## S5.f — ADIN status LEDs (2026-10-06, branch `sprint/5f-adin-leds`)

ADIN sheet (`BM_Mote_1_ADIN2111.kicad_sch`), D25:

| Change | Detail |
|---|---|
| **JP2** | clone of JP1 (`Jumper:SolderJumper_2_Bridged`, `nereus:SolderJumper-2_R1210_Bridged_NetTie`, not in BOM); ADIN_VDDIO (#PWR82) → JP2 → net ADIN_LED_VDD |
| **R44, R45** | clones of R1 (RC0402FR-071K5L 1.5 kΩ) |
| **D8** | `Device:LED`, KT-0603R red (C2286), `LED_SMD:LED_0603_1608Metric`; ADIN_LED_VDD → R44 → D8 → GND (#PWR83) |
| **D9** | `Device:LED`, KT-0603YG yellow-green (C2289); ADIN_LED_VDD → R45 → D9 → label ADIN_P1_LED1 |
| **R46, D10** (port 2, added at Nick's request) | R1 clone + KT-0603YG; ADIN_LED_VDD → R46 → D10 → label ADIN_P2_LED1 |
| **R5 moved** (with #PWR34 and their wire) | same shift as R3, into the LED group; connections unchanged |
| U1 pin 48 | 5.08 mm stub + label ADIN_P2_LED1 |
| **R3 moved** (with #PWR49 and their wire) | from beside U1 into the LED group, onto the grid; connections unchanged (pin 21 net and ADIN_VDDIO) |
| U1 pin 21 | 5.08 mm stub + label ADIN_P1_LED1 (R3 used to touch the pin directly) |
| Note | LED functions, Pi enable, strap, cut JP2 |

**Verified:** netlist diff = the pin-21 / pin-48 nets renamed ADIN_P1_LED1 / ADIN_P2_LED1 with + D9.1 / D10.1; ADIN_VDDIO
+ JP2.1; GND + D8.1; new nets ADIN_LED_VDD (JP2.2, R44.2, R45.2, R46.2), Net-(D8-A), Net-(D9-A), Net-(D10-A); nothing
else. ERC 27/508 → 27/504 (off-grid −3 each for the R3 and R5 groups on grid, +1 each for the two stubs on U1's off-grid y); netcheck 51/51; midwire 0. The mid-wire junction quirk (SPEC) bit once:
the ADIN_LED_VDD wire is split at the junction and at the label.

## S5.g — Footprint library 3D fixes (2026-10-06, branch `sprint/5g-footprint-fixes`)

Library `mote.pretty` (`Vault`) only, D24; no schematic change, no pad change:

| Footprint | Change |
|---|---|
| 78614015360-Footprint-2 (MP1–MP4, PoDL inserts) | model `FST-000629.STEP` opacity 0 → 1 (pads untouched: contact question → Sofar Q6) |
| CAPC1608X100X20ML10 (C31) | + `Capacitor_SMD.3dshapes/C_0603_1608Metric.step` |
| CAPC2013X145X50LL20T25 (C19, C27) | + `Capacitor_SMD.3dshapes/C_0805_2012Metric.step` |
| CRCW08057R50FKEAHP-Footprint-1 (R15, R16) | + `Resistor_SMD.3dshapes/R_0805_2012Metric.step` |
| RESC1005X40X25LL05T10 (R22, R34, R40), RESC1005X40X25ML05T10 (R1), RESC1005X40X25NL05T10 (R10's, unused) | + `Resistor_SMD.3dshapes/R_0402_1005Metric.step` |
| RESC1608X60X55ML20T10 (R8) | + `Resistor_SMD.3dshapes/R_0603_1608Metric.step` |

**Verified:** `fpextract --verify` 0 problems (pads identical to the board); all 8 footprints load in pcbnew with their
model at opacity 1; ERC/netcheck unchanged. A first draft also renumbered the insert pad and taught fpextract about it;
both reverted after QE S5.g F1 (the bus contact is a front copper ring) and Nick's call to ask Sofar first.

## S5.d — Payload connector J5 (2026-10-06, branch `sprint/5d-payload-connector`)

Top-Level sheet: **J5** JST GH SM02B-GHS-TB (LCSC C189893), footprint
`Connector_JST:JST_GH_SM02B-GHS-TB_1x02-1MP_P1.25mm_Horizontal`; pin 1 → VBUS_OUT symbol (#PWR80), pin 2 → GND
(#PWR81); note text below it. Placed on the right side under MP1–MP4, pins on the inserts' column (Nick: interconnects
live on the right; moved after his first look, netlist identical). Sofar's stale note "Bristlemouth Bus: Molex 2-pin"
now reads "Bristlemouth bus: M3 threaded inserts MP1-MP4" (the Molex was replaced by the inserts, Nick). Symbol `nereus:SM02B-GHS` copied from the UrchinCam schematic into `nereus.kicad_sym`
(name changed from `Connectors:SM02B-GHS`, otherwise verbatim). **Verified:** netlist diff = VBUS_OUT + J5.1, GND +
J5.2, nothing else; ERC 27/508 unchanged; netcheck 51/51; midwire 0; the footprint's pads are 1, 2 and two "MP" mounting
pads (no symbol pin, so no net, as on the UrchinCam).

## S5.c — Pull-ups, ADIN power-up, R10 removed (2026-10-05, branch `sprint/5c-pullups`)

Top-Level sheet (`BM_Mote_1_Master.kicad_sch`), D20–D22:

| Change | Detail |
|---|---|
| **R27** I2C1_SDA → 3V3, **R26** I2C1_SCL → 3V3 | 4.7 kΩ ERJ-2RKF4701X, `Vault:RESC1005X40X25LL05T05`; placed right of J1 (labels + 3V3 symbols #PWR77/#PWR78). Cloned from R3 (same part and symbol), fields set to the mote's R26/R27 (Processor sheet) except SHEET = Top-Level |
| **R43** ADIN_PWR → GND | 100 kΩ RMCF0402FT100K, cloned from R21 (all fields); left of J1 (ADIN_PWR label, GND #PWR79) |
| **R10 removed** | Symbol and its now-unused lib symbol deleted; a wire joins the SW_EN corner to TP19's wire. **Layout:** route TP19 to SW_EN where R10's footprint was; netcheck can't see this (TP19's copper net is now TP19 alone) |

**Verified:** netlist diff = R26/R27/R43 added on exactly those nets, R10 gone, TP19 moved from `Net-(R10-Pad2)` to
SW_EN, nothing else; netcheck 50/50 → **51/51** (R26/R27 restore copper connections), 0 opens/shorts; ERC 27/508,
counts and types unchanged; midwire 0. Tool: `schedit.clone_symbol` (place a copy of a part from another sheet, all
fields kept) + test.

## S5.b — Pi header wired (2026-10-05, branch `sprint/5b-pi-header-wiring`)

Top-Level sheet (`BM_Mote_1_Master.kicad_sch`), pin map in DESIGN.md:

| Change | Detail |
|---|---|
| 11 J1 signal pins | 2.54 mm stub + same-name local label: 3 I2C1_SDA, 5 I2C1_SCL, 19 ADIN_MOSI, 21 ADIN_MISO, 23 ADIN_SCK, 24 ADIN_NSS (right side); 16 ADIN_PWR, 18 ADIN_RST, 22 ADIN_INT, 36 SW_EN, 38 SW_FLAGB (left side, labels read leftward) |
| 17 unused J1 GPIO pins | no-connect flags: 7, 8, 10, 11, 12, 13, 15, 26, 27, 28, 29, 31, 32, 33, 35, 37, 40. Pins 1/17 (Pi 3V3) keep theirs; 5 V and GND unchanged |
| SW_EN | label at the corner of the existing wire from the Load Switch SW_EN sheet pin to R10.1 |
| SW_FLAGB | 2.54 mm stub + label on the Load Switch sheet pin (unconnected on this sheet since import) |

**Verified:** netlist diff = exactly one J1 pin added to each of the 11 nets (ADIN_INT/MISO/MOSI/NSS/PWR/RST/SCK,
I2C1_SDA/SCL, SW_EN, SW_FLAGB), the 11 one-pin `unconnected-(J1-…)` nets gone, nothing else; two nets renamed by the
new top-level labels (`Load Switch/SW_ON` → `SW_EN`, `Load Switch/SW_FLAGB` → `SW_FLAGB`). ERC 74/508 → 27/508
(−29 pin_not_connected, −18 label_dangling); netcheck 50/50; midwire 0. Tool: `schedit.add_label` writes 180° labels
right-justified, as KiCad does.

## S4.d — Footprints findable (2026-10-05, branch `sprint/4d-footprints`)

New project library `nereus_Pi_shield_ADIN2111/mote.pretty`, registered in the project
`fp-lib-table` as **`Vault`**: the 43 footprints the schematic uses
(`docs/design-review/vault_footprints.txt`), extracted from the reference mote board
with KiCad 9.0.6's pcbnew (`tools/fpextract.py`; the board is only read). 24 came from
a front-side instance, 19 were flipped from the back. All schematic footprint fields
without a library (117 parts, 118 fields counting U1's two units) now read `Vault:<name>`.
No other field, value or connection changed. **Verified:** `fpextract --verify` 0
problems over every board instance (pad centres compared after placing the library
footprint like each instance, flipped for back-side ones; a mirrored library is caught); netlist identical except the footprint fields;
ERC 74/626 → 74/508 (the 118 footprint-link warnings gone); netcheck 50/50; all 43
load in `kicad-cli fp export svg`.

## S5.a — Payload load switch: U9 → U11 TPS26621, R11 DNP (2026-10-05, branch `sprint/5a-u9-replacement`)

Load Switch sheet (`BM_Mote_1_Load.kicad_sch`), D18:

| Change | Detail |
|---|---|
| U9 FPF2700MX removed | Obsolete (Digi-Key) |
| **U11 TPS26621DRCR** added at (226.06, 149.68) | New project symbol `nereus:TPS26621DRCR` (new `nereus.kicad_sym` + sym-lib-table entry); stock footprint `Package_SON:Texas_DRC0010J`; LCSC C1848341. Pins placed on U9's old wire ends: IN/ILIM/SHDN/RTN left, OUT/dVdT/FLT/OVP right, GND/EP down to the GND rail |
| R34 | 374 kΩ → **9.09 kΩ RC0402FR-079K09L** (0.73 A); Value and PART NUMBER fields both updated |
| **R41** 1 MΩ (stock `Device:R`, 0402; Value/PART NUMBER RC0402FR-071ML, RESISTANCE 1MR shown) | IN → UVLO, tapping the VIN riser (split + junction) |
| dVdT | no-connect flag (floating = internal ramp) |
| R32 → **R42**, its 3V3 symbol → GND (#PWR76) | Pull-down instead of pull-up (SHDN active low); **10 kΩ RMCF0402FT10K0** (QE round 1: 100 kΩ had no worst-case margin) |
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
