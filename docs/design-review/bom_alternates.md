# BOM alternates plan (S5.h) — ready to execute

*Plan approved by Nick 2026-10-06 (DESIGN D26). Alternates below were checked by the design agent against their
lcsc.com product pages on 2026-10-06. Recheck stock before ordering. Nothing here changes a connection: the specified
parts stay; only hidden fields are added.*

**Executed in S5.h (2026-10-06, branch `sprint/5h-bom-fields`)** as below, with one change to the export: a `${DNP}`
column and `--group-by 'Value,${DNP}'`, because grouping by Value alone merged R11 (DNP) into the row of the fitted
R12/R13/R17/R19 and marked all five DNP. Result: `docs/design-review/bom.csv`; changes in `changelog.md`.

**Cap (Nick, 2026-10-06; D26):** at most 3 alternates per part, the best by match and availability. This plan uses at most 2. Sofar's own
listed alternates (R8's `MANUFACTURERPARTNUMBER1–7`, D1's second sources) stay in their original fields, outside `bom.csv`.

## Planned parts (S5.i, D27)

The part we intend to build with, per BOM line, in hidden `PLANNED MPN/MFR/LCSC` + `PLANNED NOTE` fields. Unchanged
lines are planned as specified with their LCSC number (from `bom_lifecycle.md`); J1 is TBD. Changed lines:

| Refs | Your part | Planned part (LCSC) | Why |
|---|---|---|---|
| R34 | RC0402FR-079K09L | YAGEO AC0402FR-079K09L (C227284) | same YAGEO thick-film family; ours (D18) |
| R20, R39 | CRCW04021M82FKED | RALEC RTT021824FTH (C166520) | only stocked 1.82 MΩ ±1 % match |
| R21, R35, R37, R43 | RMCF0402FT100K | UNI-ROYAL 0402WGF1003TCE (C25741) | JLC Basic; AEC-Q200 not stated |
| C31 | C1608X5R0J226M080AC | Samsung CL10A226MQ8NRNC (C59461) | same spec; yours out of stock |
| C17, C26 | C2012X7S2A105K125AB | TDK C2012X7S2A105KT000N (C342785) | TDK C2012 series, same spec per LCSC (thickness not confirmed) |
| C21 | CL32B106KBJNNNE | Taiyo Yuden UMK325AB7106KM-T (C386167) | same spec, Taiyo Yuden; FH (more stock) kept as backup |
| C16, C18, C24, C25 | 08051C474KAT2A | YAGEO CC0805KKX7R0BB474 (C596323) | same spec, stock for 80 |
| C19, C27 | C0805C102MDRACTU | KEMET C0805C102KDRACTU (C2167549) | same series, ±10 % (tighter) |
| R14, R18 | RR0510P-101-D | YAGEO RT0402BRD07100RL (C705627) | ±0.1 % ±25 ppm thin film (tighter) |
| D1 | SMA6F33A (ST, obsolete) | Vishay SMA6F33A-M3/H (global sourcing) | your listed second source (Q7) |

Kept as specified (Sofar review): **R8** — ROHM PMR03EZPFU10L0 (ALT1) electrodes b = 0.35 ± 0.15 mm (ROHM datasheet
Rev.PMR03-IA-012E) sit inside R8's pads (1.1 × 1.1 mm at ±0.65 mm), which were drawn for the UR73D1J 10 mΩ's
0.55 ± 0.1 mm electrodes (KOA UR73 catalog, 11/17/24); ROHM gives no land pattern. Sources:
https://fscdn.rohm.com/en/products/databook/datasheet/passive/resistor/chip_resistor/pmr03-e.pdf and
https://www.koaspeer.com/pdfs/UR73.pdf (both read 2026-10-06), and the pads reach 0.35 mm under its body, so
not adopted. **C22/C23** no potting-safe like-for-like part; **R15/R16** no alternate with a stated pulse rating.

## What to do

1. **On each flagged passive**, add these hidden symbol fields with `schedit.set_properties` (it adds missing fields
   hidden at the symbol origin):
   - `ALT1 MPN`, `ALT1 MFR`, `ALT1 LCSC`
   - `ALT2 MPN`, `ALT2 MFR`, `ALT2 LCSC`
   - `ALT NOTE`
   - `SOURCING`: "JLC global sourcing (first build) until an ALT is approved (D26)"
2. **On each critical part**, add `SOURCING` only (values below).
3. **BOM export.** Add to `tools/check.sh` a tracked export `docs/design-review/bom.csv`:
   ```
   kicad-cli sch export bom \
     --fields 'Reference,Value,Footprint,${QUANTITY},MANUFACTURER,LCSC,SOURCING,ALT1 MPN,ALT1 MFR,ALT1 LCSC,ALT2 MPN,ALT2 MFR,ALT2 LCSC,ALT NOTE' \
     --labels 'Refs,Value (MPN),Footprint,Qty,Mfr,LCSC,Sourcing,Alt1 MPN,Alt1 Mfr,Alt1 LCSC,Alt2 MPN,Alt2 Mfr,Alt2 LCSC,Alt note' \
     --group-by Value
   ```
4. **Checks.** ERC 27/504 and netcheck 51/51 must be unchanged. The netlist diff must show fields only: identical nets,
   values and footprints.
5. **Docs.** Point `bom_lifecycle.md` at the fields and `bom.csv`. Add a note to the Sofar brief that the alternates are
   proposals for their review. Update TRACKER, the viewer, the changelog and DEV_LOG.
6. **Review.** QE, then Nick's look (Tools → Edit Symbol Fields shows the columns).

Part locations: R34/R35/D3 Load; R20/R21/R37/R39/C31/L3/L6 Power; R8 PowerMon; C16–C27/R14–R18/D1/D2 PoDL;
U1/U2/U3/Y1 ADIN2111; R43/MP1–MP4/J5/J1 Master.

## Flagged passives — alternates (verified 2026-10-06)

Group key: **A** ordinary passives, **B** power path (constraint 7), **C** PoDL front end. Adopting an alternate for a
Sofar part needs a constraint amendment after Sofar's review (D26). R34, R39, R43 and R35's group copies are our own
parts.

| Refs | Specified | ALT1 (LCSC, stock) | ALT2 (LCSC, stock) | ALT NOTE |
|---|---|---|---|---|
| R34 (A) | RC0402FR-079K09L 9.09 kΩ 1 % 0402 | YAGEO AC0402FR-079K09L (C227284, 7,700) | UNI-ROYAL 0402WGF9091TCE (C11549, 4,100) | 9.09 kΩ ±1 % 62.5 mW 50 V ±100 ppm thick film; our part (D18), no amendment |
| R20, R39 (A) | CRCW04021M82FKED 1.82 MΩ 1 % 0402 | RALEC RTT021824FTH (C166520, 7,500) | — (UNI-ROYAL/YAGEO equivalents out of stock) | 1.82 MΩ ±1 % 62.5 mW 50 V ±100 ppm |
| R21, R35, R37, R43 (A) | RMCF0402FT100K 100 kΩ 1 % 0402 | UNI-ROYAL 0402WGF1003TCE (C25741, 2.4 M; **JLC Basic**) | YAGEO RC0402FR-07100KL (C60491, 8.4 M) | 100 kΩ ±1 % 62.5 mW 50 V ±100 ppm; AEC-Q200 not stated (Stackpole is) |
| C31 (A) | C1608X5R0J226M080AC 22 µF 6.3 V X5R 0603 | Samsung CL10A226MQ8NRNC (C59461, 5.3 M) | Murata GRM188R60J226MEA0D (C77042, 77 k) | 22 µF ±20 % 6.3 V X5R 0603 |
| R8 (B) | UR73D1JTTD10L0F 10 mΩ 1 % 0603 | ROHM PMR03EZPFU10L0 (C308571, 1,390) | Vishay WSLP0603R0100FEA (C5334451, 4,990) | **Sofar review**: power-path current sense. Sofar's own 7 listed alternates (fields MANUFACTURERPARTNUMBER1–7) not found at LCSC; check land pattern |
| C17, C26 (B) | C2012X7S2A105K125AB 1 µF 100 V X7S 0805 | TDK C2012X7S2A105KT000N (C342785, 10,140) | Murata GCM21BC72A105KE36L (C126585, 23,540) | 1 µF ±10 % 100 V X7S 0805; power path: Sofar review |
| C21 (B) | CL32B106KBJNNNE 10 µF 50 V X7R 1210 | FH 1210B106K500NT (C116808, 17,644) | Taiyo Yuden UMK325AB7106KM-T (C386167, 5,670) | 10 µF ±10 % 50 V X7R 1210; power path: Sofar review |
| C22, C23 (B) | EEEFT1H470AP 47 µF 50 V Al electrolytic | — | — | **Sofar review**: bus damping; a newly sourced replacement must be potting-safe (constraint 8), so no like-for-like alternate; JLC global sourcing (DK 78,606) |
| R15, R16 (B) | CRCW08057R50FKEAHP 7.5 Ω 0.5 W pulse-proof 0805 | YAGEO SR0805FR-477R5L (C873769, 8,340) | — | **Sofar review**: 7.5 Ω ±1 % 0.5 W, ±200 vs ±100 ppm/°C, pulse rating not stated |
| C16, C18, C24, C25 (C) | 08051C474KAT2A 470 nF 100 V X7R 0805 | YAGEO CC0805KKX7R0BB474 (C596323, 250,730) | KYOCERA AVX 08051C474K4Z2A (C597303, 750) | 470 nF ±10 % 100 V X7R 0805; PoDL front end: Sofar review |
| C19, C27 (C) | C0805C102MDRACTU 1 nF 1 kV X7R ±20 % 0805 | KEMET C0805C102KDRACTU (C2167549, 3,715) | Walsin 0805B102K102CT (C303890, 182,650) | 1 nF 1 kV X7R 0805, ±10 % (tighter); PoDL front end: Sofar review |
| R14, R18 (C) | RR0510P-101-D 100 Ω 0.5 % 25 ppm thin film 0402 | YAGEO RT0402BRD07100RL (C705627, 326,300) | Panasonic ERA2AEB101X (C445575, 3,280; AEC-Q200) | 100 Ω ±0.1 % ±25 ppm thin film 0402 (tighter); PoDL front end: Sofar review |

## Critical parts — `SOURCING` only

| Refs | `SOURCING` value |
|---|---|
| U1 ADIN2111BCPZ | JLC global sourcing (D26); no LCSC listing, DK 120 |
| U2, U3 AP22913CN4-7 | JLC global sourcing, all 40 (LCSC has 30) (D26) |
| L3, L6 PA5432.822NLT | JLC global sourcing (D26); no LCSC listing |
| Y1 ABM11W-25.0000MHZ-6-K1Z-T3 | JLC global sourcing (D26); no LCSC listing, DK 87 |
| D1 SMA6F33A | JLC global sourcing of Sofar's second source Vishay SMA6F33A-M3/H (ST part obsolete; Sofar Q7) (D26) |
| D2, D3 RB058LAM-60TFTR | JLC global sourcing (D26); no LCSC listing |
| MP1–MP4 Würth 78614015360 | JLC global sourcing (D26); no LCSC listing, DK 7,835 |
| J5 SM02B-GHS-TB | JLC global sourcing (D26); LCSC C189893 out of stock, DK 10,839 |
| J1 (no MPN yet) | Part not chosen: 2×20 2.54 mm female TH socket, height open (Nick). Candidates ZHOURI 2.54-2*20 C2977589, Megastar ZX-PM2.54-2-20PY C7499354 (both 8.5 mm) |
