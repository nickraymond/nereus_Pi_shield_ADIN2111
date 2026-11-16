# Review of placement "G" (Pi Zero fit study, 65 x 39.5 mm)

Reviewer: independent placement / mechanical review, 2026-11-15 8:35 PM Pacific. Read-only; nothing in the repo was changed.
Inputs: `PLACEMENT_SPEC_G.md`, `mock8.py`, `locked.json`, `review_placement.md` (+ `review_scratch/core.json`), the three `.kicad_pcb` files, KiCad's JST footprints and STEP models, the STEP models embedded in the source board, datasheets (URLs below).
Scripts and dumps: `review_G_scratch_placement/` (`geo.py`, `g_dump.py`, `g_conn.py`, `g_core.py`, `g_j1.py`, `g_row.py`, `g_bot.py`, `g_scan.py`, `g_scan2.py`, `g_grp.py`, `g_silk.py`, `g_silk3.py`, `embed.py`, `pdfrender.js`; datasheet pages rendered in `pdf/`).
Frame: the spec's (origin NW corner, x east, y south, mm), x_new = x_old - 113.47, y_new = y_old - 89.34. GH top-entry connectors taken at 180 deg (signal pads north, as the spec says for BM2), Qwiic at 0 deg.

## Verdict: FITS WITH CHANGES

The top-side row fits as drawn (no overlap; smallest courtyard gap 0.23 mm). Four things do not hold as written: Sofar copper runs into J1 pin 35, two bottom blocks sit on Sofar parts and copper, the mated top-entry plugs are the tallest thing on the board, and the payload pads are through-hole on the source board.

## A. Skyline

| Part | Height above board (mm) | Source |
|---|---|---|
| JST GH top entry BM04B / BM03B-GHS-TBT, bare | 4.20 (4.05 body + 0.15 stand-off) | JST eGH.pdf p.3 header drawing (https://www.jst-mfg.com/product/pdf/eng/eGH.pdf); KiCad STEP z 0..4.20 |
| same, GHR plug mated | 7.3 (reference), wires leave upward from there | eGH.pdf p.2 assembly layout "(7.3)" |
| JST SH top entry BM04B-SRSS-TB, bare | 4.30 (4.25 + 0.05) | JST eSH.pdf p.3 (https://www.jst-mfg.com/product/pdf/eng/eSH.pdf); KiCad STEP z 0..4.32 |
| same, SHR plug mated | 6.3 (reference), wires upward | eSH.pdf p.1 "(6.3)" |
| L1 / L2 Bourns SRF1260-101M | 6.0 +/- 0.2 (6.2 max) | Bourns SRF1260 datasheet p.1 "6.00 +/- 0.2" (https://www.bourns.com/docs/Product-Datasheets/SRF1260.pdf); embedded STEP top at 6.17 |
| L3 / L6 Pulse PA5432.822NLT | 6.0 max | series text "Height: 6.0mm Max" (https://pdf.jiepei.com/pm5432.472nlt-34949312.html, secondary; Pulse PDF not opened); embedded STEP 5.99 |
| C22 / C23 Panasonic EEEFT1H470AP | 5.8 +/- 0.3 (6.1 max), size code D, dia 6.3 | Panasonic FT series list p.4, row 50 V 47 uF (https://industrial.panasonic.com/cdbs/www-data/pdf/RDE0000/ABA0000C1240.pdf); +/-0.3 from the FK-series dimension table for the same case, FT table not read |
| T1 / T2 Wurth 74930000 | 2.9 | embedded STEP only |
| U1 ADIN2111 (LFCSP-48) | 0.8 | embedded STEP `CP_48_13_ADI.step` only |
| GH side entry SM04B / SM03B-GHS-TB, bare and mated | 4.35 (4.25 + 0.1); mated "(4.35)" | eGH.pdf p.3 and p.2 |
| SH side entry SM04B-SRSS-TB, bare and mated | 2.95 (2.9 + 0.05); mated "(2.95)" | eSH.pdf p.3 and p.1 |

**Answer.** Bare, the top-entry connectors (4.2 / 4.3 mm) are 1.7 to 1.8 mm lower than the inductors (6.0 mm) and lower than C22 / C23. **Mated, they are taller: GH 7.3 mm is 1.3 mm above L1 / L2 nominal (1.1 mm above their 6.2 max) and SH 6.3 mm is 0.3 mm above nominal, and the wires leave straight up, so the real stack is 7.3 mm plus the wire bend.** By Nick's rule this means side entry.

**Side entry on the same line (y 30.55), cable to the south** (KiCad `JST_GH_SM0xB-GHS-TB` / `JST_SH_SM04B-SRSS-TB` at 0 deg: signal pads north, mating face south):

| | GH 4-pin | GH 3-pin | SH 4-pin |
|---|---|---|---|
| Courtyard w x depth | 9.55 x 6.49 | 8.29 x 6.49 | 7.89 x 6.65 (top entry: 5.29) |
| Body depth (datasheet) | 4.05 + 0.8 lead | same | 4.25 + 0.7 lead |
| Courtyard south edge | 37.04 | 37.04 | 37.20 |
| Mating face (fab line) | y 36.30, 3.2 mm inside the edge | same | y 36.50, 3.0 mm inside |
| Mated plug end | about y 39.4 (plug stands 3.1 mm out of the header: 7.15 - 4.05) | same | about y 38.5 (6.25 - 4.25) |

- The row fits: widths are identical, GH signal pads land on the same copper positions as top entry at 180 deg (y 31.10..32.80), so findings C1 / C2 carry over unchanged. Mounting pads y 33.80..36.50.
- **The label strip (y 37.45..38.95) is then under the mated plugs** (GH plug covers y 36.3..39.4). Labels are readable only with the cables out.
- Options: (a) keep the line and put the names between / beside the housings or accept hidden labels; (b) move the side-entry row south so the mounting pads end 0.5 mm from the edge (courtyard top y 33.05, signal pads y 33.6..35.3, face 0.7 mm inside the edge, plug 2.4 mm past the edge) and put the names north of the row at y 31.2..32.9. (b) also removes C1 (pads leave the GND vias). In (b) MOTOR must move east about 1.8 mm: at x 0.80 its west mounting pad corner (1.35, 39.0) lies on the 3 mm corner arc (0.00 mm). The west half has 2.0 mm of slack before the LED block.
- The 7.15 / 6.25 mated lengths are reference dimensions and I read the 7.15 as measured from the header's back wall, not the lead tip; if from the lead tip the plugs stand 0.8 mm less far out.
- The Urchin board already uses SM04B-GHS-TB side entry (J2, J3, J5; body face 2.00 mm inside the board edge).

## Blockers

### B1. Sofar copper collides with J1 pin 35 (and the "2.5 mm channel" is not empty)
- 11 Sofar copper items lie north of J1's courtyard line (y 6.57), reaching y 4.94 (`g_row.py`). Against J1's pads (1.7 mm pad, 1.0 mm drill, on every layer; `g_j1.py`):
  - `~{ADIN_RST}` via (51.66, 5.16), 0.45 mm: **0.32 mm inside the drill** of pin 35 (51.55, 4.77; SPI1_MISO on the source board).
  - `~{ADIN_RST}` In1 track (51.66, 5.16)-(52.71, 6.21): 0.54 mm inside the pad.
  - 3V3 via (51.13, 5.66): 0.09 mm inside the pad; its 0.05 mm B.Cu stub 0.01 mm inside.
  - GND via (24.27, 5.88): 0.14 mm from pin 13's pad (passes 0.127 by 0.01).
- So "Sofar's copper stays exactly as it is" cannot hold at this position. Change: cut back these north ends (the `~{ADIN_RST}` via and In1 track, the 3V3 via and stub, and the GND via at pin 13) and say so in the spec; they are the ends that ran to parts no longer there or to J1. Moving the core does not help: it cannot go south (row) and J1 is fixed by the Pi.
- Also: Sofar copper reaches y 32.34 in the south (VBUS F.Cu at x 34.7..36.4), not "~32.05"; inner-layer fills (In2 GND, In4 P_IN / VBUS) reach y 33.65. All inside the board; no pad of the row touches them.

### B2. Jumper block sits on a Sofar part and on Sofar P_IN copper (bottom)
- JP block (21.0..30.5, 31.0..37.0) overlaps C24 (bottom, 22.43..25.43 x 29.51..31.71) by 3.00 x 0.71 mm, and contains Sofar B.Cu P_IN track (1.0 mm, y 31.41, x 27.73..29.98, south edge y 31.91) and three P_IN vias at (27.73 / 28.86 / 29.98, 31.41) (`g_bot.py`).
- Size: the four jumpers are 4.69 x 2.59 (JP1, JP3, JP4) and 4.70 x 3.30 (JP2), not 4.65 x 2.83; 2 x 2 with 0.2 mm gaps needs 9.6 x 6.1, block is 9.5 x 6.0.
- Change: block y 32.25..38.35, 9.6 wide (edge clearance 1.15 mm), or x 18.9..28.5 and south of y 32.0.

### B3. Payload pads: through-hole and larger than the block
- On the source board J5 is `WirePads_1x02_P3.81mm_Oval4.2x2.6mm_Drill1.3`: two 1.3 mm plated holes, 4.79 x 7.00 mm. The block is 6.5 x 4.5 directly under the Qwiic connector's six SMD pads (x 53.5..60.3). Through-hole pads there go through the Qwiic footprint.
- Change: state the pad type. If through-hole wire pads stay, they need their own spot clear of the top-side row (free: x 61.2..64.5 south of the SE keep-out is too narrow for 4.79; the LED gap x 29.0..43.0 at y 33..39 is free on the bottom if the load switch is dropped or shortened). If SMD-only pads, 6.5 x 4.5 is fine.

## Should fix

### S1. Top-entry plugs set the skyline (see A)
Switch the row to side entry; decide label option (a) or (b).

### C1. BM1 signal pad is 0.19 mm from a Sofar GND via, not ~0.3 (refuted)
- BM1 at x 43.12, 180 deg: pad 4 (45.72..46.32, 31.10..32.80) to GND via (45.23, 31.06; 0.6 mm, 0.3 drill): **0.190 mm**. Pads 3 and 2 to GND via (47.93, 30.46): 0.427 / 0.394 mm. Pad 1: 1.36 mm. Mounting pads: 2.25 / 4.34 mm. Passes 0.127, but pad 4 carries bus voltage if two pins are ganged per polarity, 0.19 mm from an (untented?) GND via; solder bridging risk.
- BM1's position is also 0.02 mm from the west limit of where a GH 4-pin can stand at all (x 43.10; west of that C21 and the vias block it).
- Change: move BM1 east. x 43.25..45.5 gives 0.32..0.35 mm; x 46.0 gives 0.62 mm; x >= 47.0 gives >= 1.48 mm (`g_scan2.py`).

### C2. BM2 mounting pads clear the P_IN vias (confirmed)
- BM2 at x 19.25: mounting pad (27.25..28.25, 33.90..36.70) to P_IN via (27.73, 31.41): 2.18 mm; signal pads to the nearest vias (Net-(C24-Pad1/2) at (25.03 / 22.98, 29.61)): 1.18..1.27 mm. No Sofar F.Cu track, via or F.Cu fill under any pad of MOTOR, POT, BM2, QWIIC or the LED block (LED block: 0.36 mm to VBUS F.Cu at y 32.34, 0.44 mm to a VBUS via). The one Sofar F.Cu fill near the row (GND, x 24.9..31.0) ends at y 29.46.

### C3. Where BM1 / BM2 can physically stand on this line
- A GH 4-pin (9.55 wide, signal pads north, pads >= 0.3 mm from Sofar copper, courtyard clear of core top parts): courtyard west edge **x 0.45..19.45** or **x 43.25..55.0**. Nothing between: C23, R16, C21 and the VBUS / GND vias occupy x 29..43.
- L2's centre is x 18.21 (BM2_N pad 13.95, BM2_P 22.46); BM2 is drawn centred at 24.03, 5.8 mm east of it and at the east end of its interval (0.2 mm left). Centred under L2 it would stand at x 13.44, which is where POT is: swapping POT and BM2 (MOTOR 0.8, BM2 10.65..20.2, POT 20.5..28.8) puts BM2 centred at 15.4.
- L1's centre is x 52.03 (BM1_N 47.78, BM1_P 56.29); BM1 is drawn centred at 47.90. BM1 at x 46.9 (centre 51.7) with QWIIC moved to x 56.75 (courtyard 0.36 mm from the east edge, 4.05 mm from the SE hole centre) fits; or BM1 x 46.0 / QWIIC x 55.85 (edge 1.26 mm). Either also fixes C1.

### S2. Load-switch block touches Sofar parts and vias (bottom)
- Block (37.5..51.7, 31.3..38.0) overlaps TP23 (41.21..42.71 x 29.99..31.49) by 1.50 x 0.19 mm, is 0.11 mm from C20, and contains GND vias (43.08, 31.41) and (45.23, 31.06) with their B.Cu GND tracks. Change: y 31.95..38.65 (edge 0.85 mm) or shorten.
- Realistic single-sided size: top members today 10.96 x 3.99, D3 2.90 x 6.40, C50 2.41 x 0.91, R42 0.84 x 1.60; D3 standing at one end gives about 14.1 x 6.4, so 14.2 x 6.7 is enough but with nothing to spare for routing.
- R35 and C50 are still counted twice (earlier review B3): both are in the 81-part core (R35 top at 22.1..23.4 x 9.3..10.0; C50 bottom at 18.9..21.3 x 10.7..11.6) and in the spec's load-switch list, 20 to 30 mm from the block.

### S3. MP6550 and ADS1115 blocks are undersized (unchanged from the earlier review)
- MP6550, Urchin as built: U1 3.51 x 3.51 with C7, C31 (4.06 x 5.76 on one side) plus C5, C6, R3 on the other side (2.31 x 3.82). Single-sided that is about 6.5 x 5.8; the block is 5 x 5 (part area 21.0..23.9 of 25 mm2). Room exists: x 2.6..12.1 is free on the bottom.
- ADS1115, as built one side: 7.50 x 4.86 plus R4; block is 6.0 x 4.5. Room exists to x 20.7.
- No through-hole conflict with the SMD connectors above: the core has no through-hole pad, the connectors are SMD, all vias on the board are through vias (F.Cu to B.Cu), so each top-pad via must be placed clear of the bottom parts.

### S4. Clearances under 0.3 mm (no overlaps)
- BM2 courtyard to C23's outline: 0.23 mm (body to body 0.94).
- Label strip to connector courtyards: 0.21 mm (to the housings' silk 0.9); strip SW corner (1.6, 38.95) is 0.18 mm from the corner arc: start the MOTOR name at x >= 2.3.
- For the record, at 0.30 / 0.31: MOTOR-POT 0.30, POT-BM2 0.31, BM1-QWIIC 0.30 (courtyard to courtyard; bodies 1.5..1.8 apart). The west half holds.

### S5. 5 V group at the west end
- Real turned size 10.25 x 12.61 (block 10.2 x 12.6): x 0.40..10.65, y 7.00..19.61. C53, R37, R38 stay under U10 inside the outline.
- Clearances: L2 pads 1.06 mm (L2 body 1.31), MOTOR courtyard 10.9 mm, west edge 0.40, NW keep-out clear by 0.50, J1 courtyard 0.43, J1 pad copper 1.38, nearest Sofar via 0.81.
- The turn direction matters and is not in the spec. Turned clockwise, L6 (6 mm tall) stands at y 7.00..14.09, 1.38 mm from J1's solder joints and 0.50 mm from the NW screw keep-out; turned counter-clockwise L6 is at x 0.47..7.36, y 12.52..19.61 and U10 is the part next to J1 (R38 on the bottom 1.04 mm from the socket body). Change: state counter-clockwise.

## Notes

- N1. MOTOR at the SW corner: courtyard corner 0.68 mm inside the arc, body 1.40, pads 1.34 (rule 0.5). SW hole 4.05 mm from the courtyard.
- N2. L1 against the SE keep-out: 12.5 mm max body corner (58.28, 25.66) is 3.33 mm from the hole centre, 0.33 mm outside the 3.0 keep-out; its 12.9 mm silk box 0.08 mm outside; pads 5.22 mm. No Sofar copper inside any of the four keep-outs.
- N3. Core extents measured: top parts x 11.71..58.53, y 9.26..31.76 (N R35, S R16); bottom x 14.46..58.03, y 9.07..31.71 (N R15, S C24). Matches the spec.
- N4. Under the south overhang: no Pi board, but the Pi's mini-HDMI (centre x 12.4), USB (41.4) and PWR IN (54.0) connectors are on that edge (Raspberry Pi Zero 2 W mechanical drawing, https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf), so their plugs and cables run under the MP6550 / ADC, load-switch and payload-pad areas. Bottom parts there are about 1.0..1.3 mm tall (MP6550 STEP 0.99, D3 STEP 1.3; ADS1115 and TPS26621 not measured). With the 8.5 mm socket the gap should be ample, but the stack height and plug sizes were not verified. Jumpers and pads in the overhang are reachable from below with the Pi fitted, unless a cable is in the way.
- N5. Label strip, F: Menlo Bold draws about 1.06 x the set height on this board (set 1.0 -> 1.06 mm, 1.3 -> 1.38, 1.5 -> 1.59; read from the board file's text outlines). In a 1.5 mm strip, size 1.2 (1.27 mm drawn, 0.11 mm margins) is the largest sensible; D39's function-name range starts at 1.3 (0.06 mm margins) and its 1.5 does not fit. The Urchin board labels its edge connectors with 1.0 mm KiCad stroke text, 0.2 mm line (a second set at 0.7 / 0.15), i.e. smaller than this. Legible; if D39's 1.3..1.5 is wanted the strip needs 1.8..2.0 mm, and there is 0.55 mm between it and the edge.
- N6. Qwiic bare is 4.3 mm; its 180 deg rotation was not checked against copper (nothing of Sofar's lies east of x 51.1 at that height).

## Not checked
- Routing of any kind; current capacity; the motor supply; thermal.
- JST drawings beyond the catalogue sheets (tolerances; latch clearance; wire bend height above a mated top-entry plug).
- Pi-to-shield stack height, Pi part heights, USB / HDMI plug sizes; any enclosure above or beside the board.
- Via tenting on Sofar's vias (decides how serious C1 is); JLC assembly rules for edge rails, fiducials, connectors overhanging pads near the edge.
- ADS1115, TPS26621, LED heights (datasheets not opened); Pulse's own PA5432 datasheet; Panasonic FT dimension table (tolerance taken from the FK table for the same case code).
- Screw-head and standoff diameters against the 3.0 mm keep-out.
- LED cluster internals (three 0603 plus resistors inside 10.3 x 4.5) and the SVG picture against the spec.
