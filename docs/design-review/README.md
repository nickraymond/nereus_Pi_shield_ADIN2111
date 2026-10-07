# Design-review package — nereus Pi shield (ADIN2111)

**Board:** nereus_Pi_shield_ADIN2111 · **Part number:** PCB-000001-AA · **Rev:** AA
**Based on:** Sofar Bristlemouth mote 000639-AB (KiCad copy of the Altium design), PoDL / ADIN2111 front end and power
path kept as Sofar designed them (DESIGN D12). **Package assembled:** 2026-10-06 (Sprint S6).

## Status at a glance

| Check | Result | Where |
|---|---|---|
| ERC | **0 errors**, 495 warnings (cosmetic import leftovers: 481 off-grid, 12 duplicate net names, 2 dangling wire ends on Sofar's PoDL sheet). 18 errors excluded, each with its reason | `erc_justifications.csv`, DESIGN "ERC / net-check results" |
| Connectivity vs the mote's copper | **51/51** copper nets match; 0 opens, 0 shorts. Every net touching a new part is listed | `netcheck.md` |
| BOM | 51 lines; Sofar's part, our planned part (with the reason) and backups side by side | `bom.csv` |
| Footprints | all 43 `Vault` footprints have a type and a courtyard; pads identical to the mote board | `footprints.md` |
| Schematic | rev AA, all 7 sheets; the tidy (S6.d) changed positions and text only, no connection | `schematic.pdf` |
| Independent review | every change reviewed by a separate read-only QE session before merging | `qe/` |

## Read in this order

| # | What | File |
|---|---|---|
| 1 | **What changed from Sofar's mote, and why** (one row per change) | `sofar_brief.md` |
| 2 | The schematic, all sheets (rev AA) | `schematic.pdf` |
| 3 | Every schematic edit, sprint by sprint | `changelog.md` |
| 4 | Connectivity check: kept nets vs the mote's copper, and every new net with its pins | `netcheck.md` |
| 5 | Pi header pin map; ADIN power-up order and back-power cases | `../DESIGN.md` → "Pi header pin map", "ADIN power and boot" |
| 6 | Power budget: bus power, 5 V converter, Pi supply, payload port | `power_budget.md` |
| 7 | BOM: `bom.csv` (Value = Sofar's part, Planned = what we'd build with, Planned note = why; Alt = backups); lifecycle and stock check; alternates and the planned-part table | `bom.csv`, `bom_lifecycle.md`, `bom_alternates.md` |
| 8 | Footprint types and courtyards (source of each) | `footprints.md` |
| 9 | ERC exclusions and their reasons | `erc_justifications.csv` |
| 10 | Decision log (D1–D29) | `../DESIGN.md` → "Decision log" |
| 11 | Open questions and proposed values (below) | `../SOFAR_QUESTIONS.md`, `../SPEC.md` → "Open questions" |
| 12 | QE review reports, sprint by sprint | `qe/S2.md` … `qe/S6.md` |

Note on the BOM's Mfr column: it mixes Sofar's spellings (e.g. "Yageo / Phycomp", "Wurth Elektronik") with the names in
our lifecycle table ("Yageo", "Würth Elektronik"), because Sofar's fields were left untouched (QE S6.a N1).

## Open questions and proposed values

**For Sofar** (`../SOFAR_QUESTIONS.md`, to send — Nick):
- **Q6** How the PoDL bus should connect to the threaded inserts MP1–MP4 (the front-side copper arc on 000639-AB).
- **Q7** D1's source: ST SMA6F33A is obsolete; is the Vishay SMA6F33A-M3/H your preferred replacement? (Planned in the BOM.)
- **Q2** Is R11 fitted on production motes? (Context only: R11 is DNP on the shield, D17.)
- **The planned parts** (10 BOM lines, `bom.csv` Planned columns): LCSC-stocked equivalents of parts LCSC doesn't stock.
  Nothing is adopted without your review (D26/D27).

**For the design review** (`../SPEC.md` → "Open questions"):
- Effective capacitance of C56/C57 (GRM21BR61C226ME44, 22 µF 16 V 0805) at 5 V DC bias: unmeasured; TI SLUSEF4A Eq. 14
  wants ≥ 22 µF effective.
- U10's input capacitance copies U5's (2.2 µF + 100 nF); TI SLUSEF4A §9.2.2.6 suggests ≥ 4.7 µF, its own Figure 9-1 uses
  2.2 µF. Field-proven on U5; U10 draws more input current.

**For Nick (layout and release):**
- J1's socket part number (height, once the board spacing is known).
- The title blocks still show the Altium placeholder "=ProjectAuthor" (text variable `AUTHOR`): needs a name.
- pcbnew → Tools → Update Footprints from Library, to pick up the S6.c types and courtyards (check its keep-text options).
- Grounding of the mounting holes MTG1–4 (no net, as on the mote).
- Not done in the tidy (more than minor): moving J1 so every interconnect sits on the right of the Top-Level sheet.
- Optional layout notes from the S6.d QE review: the two 3V3 symbols beside R26/R27 (2.54 mm apart) draw as one bar;
  the ADIN_VDDIO symbols under R3/R5 point down; MP1–MP4 reference text overlaps their bodies; TP5/TP7 labels crowd.
  U2/U3's courtyard is tight (0.05 mm past the 0.9 mm body; Sofar's outline).

## Regenerate

```bash
tools/check.sh
```

ERC, netlist, PDF (`out/`), BOM (`bom.csv`), ERC exclusions check, mid-wire check and the net check (`netcheck.md`).
Expected: `ERC messages: 495  Errors 0  Warnings 495`, `ercexclude: 18 errors justified, 0 unjustified, 0 stale / 0
missing exclusions`, `midwire: 0`, `netcheck: 51/51 … 0 opens, 0 shorts`, exit 0.

`schematic.pdf` here is the reviewed snapshot:

```bash
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli sch export pdf -o docs/design-review/schematic.pdf nereus_Pi_shield_ADIN2111/nereus_Pi_shield_ADIN2111.kicad_sch
```
