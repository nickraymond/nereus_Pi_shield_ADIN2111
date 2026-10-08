# DEV_LOG.md — Session Log

*Newest entries on top. One entry per working session. Short: what changed,
what broke, what's next.*

---

## Entry template

```
## YYYY-MM-DD — Sprint Sn — <one-line summary>
**Branch:** sprint/n-slug
**Files touched:** <sheets / docs>
**ERC:** <n errors / n warnings>  ·  **Net diff:** <clean | n changed — intended?>
**Done:**  <bullets>
**Broke/surprised us:** <bullets or "nothing">
**Next:** <the single next bite>
```

---

## 2026-10-07 — Sprint S7.a — Layout experiment brief (Fable port of the mote layout)

**Branch:** sprint/7a-layout-experiment-brief
**Files touched:** experiments/fable_layout_01/ (BRIEF, KICKOFF, tools/render_layers.py); CLAUDE.md, SPEC (constraint 1,
insert-contact fact, non-goals), TRACKER (rules 8/9, S6.g QE done, S7), DESIGN D31, SOFAR_QUESTIONS (Q6 reworded, Q9–Q12),
viewer
**ERC:** 0 / 494 (no schematic change)  ·  **Net diff:** none
**Done:**
- Read Sofar's board layer by layer (pcbnew, read only): stack, block placement, routing by net class; published a
  walkthrough page and a Sofar layout-questions page (one copper render per question; Notion text + PNGs for Nick)
- Nick's envelope for the shield, worked out with scale drawings: inserts on the west wall, 50 W inductor room, Micro-Fit
  payload facing south, M3 housing holes, 46 × 65 mm; OpenMV N6 overlay (later variant, staggered 4.2 mm east)
- Area check against Sofar's density: fits overall; U1's 9.12 mm courtyard doesn't fit the 8 mm band between the
  inductors, so the brief offers the west pocket or 2 mm of growth
**Broke/surprised us:**
- R12/R13/R17/R19 (fitted) sit across L1/L2's windings (Bourns pinout 1–3, 2–4): asked Sofar (Q9)
- SPEC said "no vias within 3.5 mm" of the inserts; there are seven at r 3.0 mm inside the ring pad. Corrected
- Four inserts in a row along the south edge don't fit a 31.5 mm board (copper Ø7.4 each); moved to the west wall
**Next:** QE review of S7.a; then Nick starts the Fable session

---

## 2026-10-07 — Sprint S6.g — Presentation clean-up (Nick's list)

**Branch:** sprint/6g-presentation
**Files touched:** all 7 sheets; .kicad_pro (exclusion keys); schematic.pdf; DESIGN (D30), changelog, README, sofar_brief,
TRACKER, viewer
**ERC:** 0 / 494 (was 0 / 495)  ·  **Net diff:** identical pin partition, 7 nets renamed — intended
**Done:**
- Nick's KiCad look (S6.f) produced an 8-item list; he discarded his own KiCad edits and asked for them fresh
- Asked: what ADIN_PWR/R43 do (Pi GPIO23 → U2/U3 ON; R43 keeps the ADIN off while the Pi boots or is absent, D21);
  active-high/low marking → KiCad overbar; names PAYLOAD_EN / ~{PAYLOAD_FAULT}, ~{ADIN_CS}; no signal table for now
- New helpers (scratch): move_block / move_where (shift items wholly in a region; stretch wires only along their axis,
  else refuse), label renames, title blocks, text/rect adders
**Broke/surprised us:**
- My label-rename pattern first matched nothing while the sheet-pin rename did: the pin-partition check caught the split
  nets at once. A text insert landed at the top of a sub-sheet (no sheet_instances block): KiCad loaded an empty sheet;
  inserts now go before the file's closing bracket
- KiCad JSON/SVG: the cover's 2 render images were ~8 MB of the file
- QE round 1 APPROVED WITH NITS (P2_LED1 overbar vs pin 47's wire; 1V8 header on its wire; licence note → Sofar Q8 drafted)
- Nick, after his KiCad look: J5 wired beside the Load Switch (connector with its switch beats "interconnects on the right");
  R11 note as an open / fitted summary; headers for J1 and the Load Switch; Power sheet title removed
- QE round 2 APPROVED WITH NITS: ~{PAYLOAD_FAULT}'s overbar touched the PAYLOAD_EN wire; jogged like ~{ADIN_P2_LED1}
**Next:** Nick's look in KiCad; merge #28; then S6 complete

---

## 2026-10-07 — Sprint S6.f — Author + BOM PDF

**Branch:** sprint/6f-author
**Files touched:** .kicad_pro (AUTHOR); bom.pdf + schematic.pdf; tools/bompdf.py, tools/html2pdf.js; README, TRACKER, viewer,
changelog
**ERC:** 0 / 495 (unchanged)  ·  **Net diff:** none
**Done:**
- Nick: author is Nick Buemond; he wants the KiCad project, the changes and a BOM PDF to review
- BOM PDF from bom.csv, one row per line, changed lines highlighted
**Broke/surprised us:**
- No HTML/RTF → PDF filter on macOS (cupsfilter); AppKit's print operation via JavaScript for Automation works, and
  needs absolute column widths (percentages are ignored)
**Next:** QE review; Nick's review of the package and the KiCad project; S6 complete

---

## 2026-10-06 — Sprint S6.e — Review package (overnight run, bite 5 of 5)

**Branch:** sprint/6e-review-package
**Files touched:** README.md + schematic.pdf (new, design-review); tools/netcheck.py (+ test), netcheck.md; R11–R13/R17/R19
Description; SPEC, DESIGN, changelog, TRACKER, viewer
**ERC:** 0 / 495 (unchanged)  ·  **Net diff:** 5 Description values — intended
**Done:**
- S6.d merged (PR #25) after QE (rendered base vs head; redundant junction removed)
- netcheck now lists every new net with its pins; package README ties the whole review together
- SPEC's S6 cleanup: the five CRCW1210 jumpers' wrong "205K" Description
**Broke/surprised us:**
- The S6 QE's sends arrive late or in bursts: its S6.b/S6.c reports landed after they were already acted on from its transcript
- QE APPROVED WITH NITS: 4 open SPEC items added to the README, MP1–MP4 wording, Description source, U11 note; merged
**Next:** Nick's demo of the package; then S6 is complete

---

## 2026-10-06 — Sprint S6.d — Minor schematic tidy (overnight run, bite 4 of 5)

**Branch:** sprint/6d-tidy
**Files touched:** BM_Mote_1_Master.kicad_sch, BM_Mote_1_ADIN2111.kicad_sch, .kicad_pro (one exclusion key); DESIGN,
changelog, TRACKER, viewer
**ERC:** 0 / 495 (was 0 / 504)  ·  **Net diff:** none (nets and pins identical)
**Done:**
- S6.c merged (PR #24) after QE (footprints.md "Used by" fixed)
- Rendered every sheet (SVG → region crops via Quick Look) and listed only clear readability issues
- I²C pull-ups onto J1's stubs; LED columns even with pull-ups under their LEDs; overlapping text/notes fixed; stale note
  updated; dead stub + dangling lead-ins removed
**Broke/surprised us:**
- kicad-cli JSON also scales wire lengths by 100: the "0.2 mm" dangling wires were 20–40 mm lead-ins on Top-Level
- Sofar's ADIN_VDDIO bar symbol points down at rotation 0 (opposite to KiCad's stock symbols); field angle 90 keeps text
  horizontal on a 270° symbol; Sofar's resistors show a RESISTANCE field (Value hidden)
- Moving #PWR34 made its exclusion stale exactly as designed: check.sh failed until `ercexclude.py --write`
- QE APPROVED WITH NITS after rendering base vs head; redundant TP8 junction removed
**Next:** S6.e (review package)

---

## 2026-10-06 — Sprint S6.c — Footprint types and courtyards (overnight run, bite 3 of 5)

**Branch:** sprint/6c-footprints
**Files touched:** mote.pretty (43 footprints, inserts only); tools/fpattrs.py (+ test); footprints.md (new); DESIGN (D29),
changelog, TRACKER, viewer
**ERC:** 0 / 504 (unchanged)  ·  **Net diff:** none (library only)
**Done:**
- S6.b merged (PR #23) after QE round 2
- Type + F.CrtYd on all 43 Vault footprints; courtyards from Sofar's outlines first (39), computed for 4
**Broke/surprised us:**
- A pads+fab courtyard came out smaller than the body (SRF1260 6.1 × 13.5 mm vs a 12.5 mm body): these Altium footprints
  draw the body on User layers, not Fab. Rule changed to use Sofar's User-layer outline first
- KiCad's writer (FootprintSave) regenerates every uuid and drops default-valued fields (the S5.g `opacity 1`), so the
  change is written as text inserts and re-read with pcbnew; BOX2I.Merge didn't behave through SWIG: plain min/max
- QE sends from the S6 session get queued, not delivered: read its verdicts from its transcript
- QE APPROVED WITH NITS: footprints.md "Used by" was wrong on 5 rows (regex ran across netlist components), regenerated
**Next:** S6.d (minor schematic tidy)

---

## 2026-10-06 — Sprint S6.b — ERC clean or justified (overnight run, bite 2 of 5)

**Branch:** sprint/6b-erc
**Files touched:** .kicad_pro (text variables, exclusions); 7 sheet title blocks; tools/ercexclude.py (+ test), check.sh;
erc_justifications.csv (new); DESIGN (D28), changelog, TRACKER, viewer
**ERC:** **0** / 504 (was 27 / 504)  ·  **Net diff:** title-block revs + text variables — intended
**Done:**
- S6.a QE APPROVED WITH NITS, merged (PR #22); report started `docs/design-review/qe/S6.md`
- Title block from Nick: rev AA, PCB-000001-AA, name = file name
- KiCad 9 exclusion key format taken from the 9.0 source (sch_marker.cpp SerializeToString) and confirmed empirically
  on a scratch copy: only the variant with the sheet path in both path slots is accepted
- Reasons sourced: FID/MTG have no net on the mote copper; U3 VOUT is passive-typed; switch/bootstrap and inductor nets
**Broke/surprised us:**
- kicad-cli JSON positions are in 100 mm units (229.87 mm prints 2.2987)
- `--severity-exclusions` still omits excluded items from the JSON in 9.0.6, so the tool runs ERC on a copy with the
  exclusions cleared
- Exclusion keys carry the item's position: S6.d moves must be followed by `ercexclude.py --write` (check.sh catches it)
- QE round 1 CHANGES REQUESTED (read from its transcript: its send was queued, never delivered): F1 the tool exited 0 on
  unjustified errors; F2 MTG grounding stays Nick's; N1 two-item errors. Fixed
**Next:** QE round 2; then S6.c (footprint attributes, library only)

---

## 2026-10-06 — Sprint S6.a — BOM hygiene (overnight run, bite 1 of 5)

**Branch:** sprint/6a-bom-hygiene
**Files touched:** six sheet files (flags + MANUFACTURER); bom.csv; bom_lifecycle, changelog, DESIGN, TRACKER, viewer
**ERC:** 27 / 504 (unchanged)  ·  **Net diff:** 26 exclude_from_bom markers + MANUFACTURER fields — intended
**Done:**
- S5.i merged (PR #21) on Nick's instruction; S5 complete except J1's part number
- Nick: run S6.a–e overnight, QE-approved before each next bite; fresh S6 QE session started from a task chip
- Title block values from Nick: name = file name, rev AA, part number PCB-000001-AA (for S6.b)
- TP/FID/MTG out of the BOM; MANUFACTURER filled from the lifecycle table on the 75 parts without one
**Broke/surprised us:**
- First pass treated Sofar's MANUFACTURER1 as D1's maker; it belongs to their *second source* (Vishay). Redone with
  MANUFACTURER as the only BOM field: D1 = STMicroelectronics, U5/U10 = Texas Instruments (Sofar's MFR_NAME agrees)
**Next:** QE review; then S6.b (ERC)

---

## 2026-10-06 — Sprint S5.i — Planned part per BOM line (D27)

**Branch:** sprint/5i-planned-parts
**Files touched:** six sheet files (fields only); .kicad_pro (view); tools/check.sh; bom.csv; DESIGN (D27), bom_alternates,
bom_lifecycle, sofar_brief, changelog, TRACKER, viewer
**ERC:** 27 / 504 (unchanged)  ·  **Net diff:** 428 new PLANNED fields + 19 SOURCING values — intended
**Done:**
- S5.h merged (PR #20, `1acef25`) after Nick's look; KiCad's close-time .kicad_pro rewrite discarded first
- Nick: one "planned part" column, with the why, as the single diff for Sofar. Decisions: Value stays Sofar's; first build
  buys planned parts after Sofar's review; ALT1/ALT2 stay as backups
- 10 changed lines from the S5.h alternates; every other part planned as specified with its S5.e LCSC number
- R8: compared ROHM PMR03 (b 0.35 mm) and KOA UR73D1J (b 0.55 mm) against R8's pads; no ROHM land pattern → kept
- check.sh now exports bom.csv from the KiCad preset (one definition); unknown preset fails loudly with a restore hint
**Broke/surprised us:**
- Five more parts (U11, R41, C56–C58) had the 4-tab Footprint line; the guard stopped after one sheet, restored, re-run
  with the same whitespace normalisation as J1
- No LCSC listing for D1's Vishay second source; TDK KT000N vs K125AB: same spec per LCSC, thickness not confirmed
- QE round 1: **APPROVED WITH NITS** (F1 two notes overstated stock; N1 TDK claim; N2 D26 → D27; N3 "tier-1"), fixed
**Next:** merged on Nick's instruction; S6.a plan (BOM hygiene), with a fresh S6 QE session

---

## 2026-10-06 — Sprint S5.h — BOM alternates as hidden fields + tracked BOM

**Branch:** sprint/5h-bom-fields
**Files touched:** six sheet files (fields only); tools/check.sh; docs/design-review/bom.csv (new); bom_alternates,
bom_lifecycle, sofar_brief, changelog, DESIGN, TRACKER, viewer
**ERC:** 27 / 504 (unchanged)  ·  **Net diff:** 208 new hidden fields, nothing else — intended
**Done:**
- Executed `bom_alternates.md` as planned: 8 fields on each of the 24 flagged passives, `SOURCING` on 15 critical refs
  (U1 on both units). Nick: Sofar's listed parts stay the primary column, alternates beside them; that is the layout
- Structural compare against HEAD: every existing property unchanged and in order, every new field hidden
**Broke/surprised us:**
- `--group-by Value` alone merged R11 (DNP) with the fitted R12/R13/R17/R19 and marked all five DNP; caught in a
  scratch export before editing, now grouped by Value + `${DNP}`
- J1's Footprint property was indented 4 tabs (import leftover, like JP1) and tripped `set_properties`' guard; the
  first run had already written two sheets, so I restored them and reran with that line re-indented
- ERC reports differ between runs on the *same* file: `multiple_net_names` cites whichever copy of a repeated label
  KiCad picks. Compare ERC with coordinates stripped
- `Mfr`/`LCSC` columns are mostly blank: only 30 of 291 symbols have `MANUFACTURER`, 5 have `LCSC` (S6 harmonisation)
- QE round 1: **APPROVED WITH NITS** (undeclared note-text tweaks, TP/FID/MTG rows in bom.csv → S6, viewer label), fixed
- Nick: at most 3 alternates per part (ours ≤ 2); R8's 7 Sofar fields stay as Sofar's data, its ALT NOTE no longer cites them
- Nick's first look: the fields existed but KiCad shows new fields only once their columns are enabled, and his enabled
  columns landed after Footprint/Datasheet. Added the view "Sofar review (alternates)" to the `.kicad_pro` (preset + the
  dialog's opening view); `kicad-cli --preset` export = bom.csv cell for cell. Closing KiCad had rewritten the `.kicad_pro`
  with all 186 imported field names; discarded, the preset written on the committed file
- Nick's look: fields present; KiCad 9 (macOS) draws the fields-table header blank with these columns, though its Export
  has the headers and equals bom.csv cell for cell, so bom.csv is the review table. KiCad's close-time .kicad_pro rewrite discarded
- Nick asked for a **Planned part** column (+ a why note) as the single diff for Sofar → S5.i, decisions recorded in TRACKER
**Next:** merge #20; S5.i (planned parts); then S6

---

## 2026-10-06 — Session handoff — S5.h planned, ready for a new session

**Branch:** sprint/5h-bom-alternates (handoff docs only)
**Files touched:** docs/design-review/bom_alternates.md (new); TRACKER, viewer, DEV_LOG
**ERC:** 27 / 504 (unchanged)  ·  **Net diff:** none
**Done:**
- S5.e closed: QE approved (round 2), Nick approved, PR #18 merged (`f5b2279`)
- S5.h fully specified for the next session: field names, every alternate's MPN/LCSC/stock (checked on lcsc.com
  today), `SOURCING` values for the critical parts, the BOM export command, and the expected checks
- Nick asked to wind this session down; the handoff PR merged at his instruction without a QE round (plan only,
  no design change)
**State for the next agent:**
- main is green (ERC 27/504, netcheck 51/51, midwire 0)
- S5 standing QE session `local_fad7e722-e717-4a71-88c9-020652d9d441`: its sends to the design session get paused after
  ~10 messages; read its transcript if no report arrives
- Sofar questions still to send (Nick): Q2, Q6 (PoDL insert contact), Q7 (D1 source)
- J1's part number waits on the board spacing (Nick)
**Next:** S5.h, then S6

---

## 2026-10-06 — Sprint S5.e — BOM lifecycle + stock check (all parts, 20 boards)

**Branch:** sprint/5e-bom-lifecycle
**Files touched:** docs/design-review/bom_lifecycle.md (new); DESIGN, SPEC, SOFAR_QUESTIONS (Q7), TRACKER, viewer
**ERC:** 27 / 504 (unchanged)  ·  **Net diff:** none (docs only)
**Done:**
- S5.f closed: Nick's look OK, PR #17 merged (`e62d974`); S5.e run last with every part on the schematic (Nick)
- 50 unique parts / 105 placements; four read-only research agents in parallel; Nick set the build to 20 boards mid-run
- Spot-checks: SMA6F33A obsolete (Digi-Key), LMR51430YDDCR stock (LCSC), second-source fields in the netlist
- Found Sofar's own second sources in the part fields: D1 (Vishay SMA6F33A-M3/H, ST SMA6F33AY), R8 (7 alternates)
**Broke/surprised us:**
- 21 of 50 flagged, but only D1 for lifecycle: the rest is LCSC not stocking Sofar's exact parts (all Active at DK)
- UrchinCam's 2×20 header (Amphenol 95157-440LF) is a male SMD header, not a usable socket for J1
- LCSC search can't be read automatically: "no listing found" is not proof; Nick to confirm the key ones in a browser
**Next:** QE review; Nick's review + sourcing decisions; then S6

---

## 2026-10-06 — Sprint S5.f — ADIN status LEDs

**Branch:** sprint/5f-adin-leds
**Files touched:** BM_Mote_1_ADIN2111.kicad_sch; DESIGN (D25), SPEC, sofar_brief, TRACKER, viewer, changelog
**ERC:** 27 / 506 (was 27/508)  ·  **Net diff:** LED nets + pin-21 net renamed — intended
**Done:**
- S5.d and S5.g closed: Nick's look OK (J5 moved right, 3D models checked), PRs #15/#16 merged (`c9aa575`, `94bc4b8`)
- Nick: lifecycle check only once every part is on the schematic → S5.f before S5.e
- D8 red (ADIN powered) + D9 yellow-green (pin 21 link/activity), R44/R45 1.5 kΩ, JP2 cut-to-disable (option a)
- Parts from LCSC with stock; KENTO's spec sheet gives the cathode mark (green), matching pad 1 / pin K
**Broke/surprised us:**
- R3 touched U1 pin 21 directly, leaving nowhere clean to tap: moved R3 into the LED group, stub + label on pin 21
- The mid-wire junction quirk again: R45 came up unconnected until the wire was split at the junction
- JP1's Footprint property is indented 4 tabs (S4.b leftover; KiCad doesn't care) and tripped set_properties' guard;
  normalised on the JP2 copy only
- Rotated LED field text collided with the label: fields set horizontal
**Next:** Nick's KiCad look; then S5.e (lifecycle + stock, all parts)
- QE round 1: **APPROVED WITH NITS** (off-grid accounting −3/+1; ≈ 8 mW with R3's current while D9 is lit), fixed
- Nick: add the port-2 twin → D10 + R46 on ADIN pin 48 (R5 moved like R3, stub + label); D10 joins the ADIN_LED_VDD
  wire directly; note reflowed to stay inside the sheet

---

## 2026-10-06 — Sprint S5.g — Footprint library 3D fixes (PoDL insert model, stock models)

**Branch:** sprint/5g-footprint-fixes (stacked on S5.d)
**Files touched:** mote.pretty (8 footprints, 3D only); DESIGN (D24), SPEC, SOFAR_QUESTIONS (Q6), TRACKER, viewer, changelog
**ERC:** 27 / 508 (unchanged)  ·  **Net diff:** none (library only)
**Done:**
- Nick: the mote's bus attaches with threaded inserts; found them as MP1–MP4 (Würth 78614015360) on BM1±/BM2±
- Insert model was present but opacity 0 → now visible; geometry settles the "1.5 mm": M3, 6 mm × 1.5 mm body
- Stock 3D models on 7 footprints (+ R10's spare); orientation checked numerically (non-polarised, pads and model on x)
**Broke/surprised us:**
- I numbered the insert pad "1" thinking the bus fed through it. QE round 1 (CHANGES REQUESTED) found the real contact:
  a front-side C-shaped copper arc on the bus track (presumably under the screwed lug); the back insert pads are net-less. Nick: don't jump
  to layout details; ask Sofar (Q6). Pad change and the fpextract exception reverted
- KiCad has no 0.9 mm, 0.5 mm-pitch 4-ball model, so U2/U3 stay without one
- The insert model's up/down depends on KiCad's rotation sign, not confirmable offline → Nick checked in the 3D viewer:
  body-up, models check out
**Next:** QE round 2; Nick's KiCad look (incl. the 3D check)
---

## 2026-10-06 — Sprint S5.d — Payload connector J5 (JST GH 2-pin)

**Branch:** sprint/5d-payload-connector
**Files touched:** BM_Mote_1_Master.kicad_sch; nereus.kicad_sym (SM02B-GHS); DESIGN (D23), SPEC, sofar_brief, TRACKER, viewer, changelog
**ERC:** 27 / 508 (unchanged)  ·  **Net diff:** J5 on VBUS_OUT / GND — intended
**Done:**
- S5.c closed: Nick's KiCad look OK, PR #14 merged (`d5bc13b`)
- Traced VBUS_OUT on the mote copper: it left through mezzanine P1 pins 14/16/18, gone since S2
- Nick: JST GH, the 2-pin variant, part and footprint from his UrchinCam (J4/J6), shown on the Top-Level sheet
- Found while answering the bus question: the PoDL threaded inserts MP1–MP4 (Würth 78614015360, M3) have an
  invisible 3D model (opacity 0) and an unnumbered copper pad, so a new layout wouldn't put the bus nets on them —
  fixed next in S5.g
**Broke/surprised us:**
- First placement: the note crossed the VBUS_OUT wire and the value touched GND; re-placed after the render
- Nick's look: move J5 to the right with the inserts (interconnects live there), drop the UrchinCam reference from the
  note, update the stale "Molex 2-pin" bus note. My first move broke the sheet: re.sub turned the note's `\n` escapes
  into real newlines inside a quoted string, KiCad couldn't parse it (ERC 4, empty netlist). Caught by check.sh, fixed;
  netlist identical after the move
**Next:** Nick's KiCad look; S5.g footprint fixes
- QE round 1: **APPROVED WITH NITS** — C189893 out of stock on LCSC today (recorded, recheck in S5.e); MP pad wording;
  layout silkscreen "VBUS 16–32 V" next to J5 so a 5 V GH cable isn't plugged in

---

## 2026-10-05 — Sprint S5.c — I²C pull-ups, ADIN_PWR pull-down, R10 removed, ADIN boot order

**Branch:** sprint/5c-pullups
**Files touched:** BM_Mote_1_Master.kicad_sch; tools/schedit.py (clone_symbol) + test; DESIGN (D20–D22, "ADIN power and boot"), SPEC, SOFAR_QUESTIONS, sofar_brief, TRACKER, viewer, changelog
**ERC:** 27 / 508 (unchanged)  ·  **Net diff:** R26/R27/R43 added, R10 removed, TP19 → SW_EN — intended
**Done:**
- S5.b closed: Nick's KiCad look OK, PR #13 merged (`31bc0f3`)
- Read Sofar's reference sheets (Nick: answer from the mote design first): the ADIN load switches exist for
  "<10mW mote operation"; every strap checked against the ADIN2111 Rev. B datasheet Nick supplied
- Citations: Pi Zero 2 W schematic (1.8 kΩ I²C pull-ups to Pi 3V3), BCM2835 §6.2 (GPIO reset pulls; Zero 2 W =
  BCM2710A1 per product brief), AP22913 DS41203 (no ON pull-down), TI SLVA689 (I²C R_P(min) 967 Ω)
- Nick chose Option 1 (software boot order, no CS/RST series resistors); R10 removed (Pi is the only controller)
**Broke/surprised us:**
- git's default diff showed ~7,500 changed lines for ~1,450 added; `--diff-algorithm=patience` shows the real
  +1665/−214 (two Altium symbols with ~35 fields each)
- NXP's I²C spec download returns 404 to scripts; cited TI SLVA689's table of the spec values instead
**Next:** Nick's KiCad look; then S5.d payload connector
- QE round 1: **APPROVED WITH NITS**. F1 (minor): the Pi's default pull-down doesn't hold ADIN RESET once the
  ADIN is powered (it fights the internal pull-up) → boot order now drives GPIO24 low / GPIO23 high from config.txt;
  nits: TP19's move isn't visible to netcheck (layout note added), Q4 state key, duplicate import

---

## 2026-10-05 — Sprint S5.b — Pi header wired

**Branch:** sprint/5b-pi-header-wiring
**Files touched:** BM_Mote_1_Master.kicad_sch; tools/schedit.py (180° labels) + test; DESIGN, TRACKER, viewer, changelog
**ERC:** 27 / 508 (was 74/508)  ·  **Net diff:** 11 nets each + one J1 pin — intended
**Done:**
- S4 closed: Nick's KiCad look OK, PR #12 merged (`9949b37`); S4 QE session archived (Nick)
- J1: 11 signal pins stubbed and labelled per the pin map, 17 unused GPIO pins no-connect flagged
- SW_EN label on the R10.1 / sheet-pin wire; SW_FLAGB sheet pin stubbed and labelled
**Broke/surprised us:**
- All 18 label_dangling errors cleared, including the sub-sheet hierarchical labels: KiCad reported each as
  "not connected" because its net held one pin, not because it was unwired
- One multiple_net_names line cites a different example label; count and type unchanged (ERC text varies run to run, QE N2)
**Next:** QE review (standing S5 session), then Nick's KiCad look; then S5.c pull-ups + sequencing
- QE round 1: **APPROVED WITH NITS** (DEV_LOG separator and wording, fixed); carry-over risk for S5.c: CE0
  (GPIO8) defaults high and can back-power the ADIN through its IO clamps while ADIN_VDDIO is off

---

## 2026-10-05 — Sprint S4.d — Footprints findable (library `Vault`); S5.a closed

**Branch:** sprint/4d-footprints
**Files touched:** new mote.pretty (43 footprints) + fp-lib-table entry; footprint fields on all sheets; tools/fpextract.py (+ test_fpextract.py); docs/design-review/vault_footprints.txt; DESIGN (D19), TRACKER, viewer, changelog
**ERC:** 74 / 508 (was 74/626)  ·  **Net diff:** identical except 117 footprint fields
**Done:**
- S5.a closed: Nick's KiCad look OK (asked the QE about the R11 cross / page contents), PR #11 merged (`10d64d0`)
- Extracted only the footprints the schematic uses (Nick: keep only what we use) with KiCad's own pcbnew
  (bundled Python 3.9), library nickname `Vault` = the board's prefix, so F8 re-links without replacing
- Verifier compares every board instance; negative test (moved pad, widened pad) is caught
**Broke/surprised us:**
- My first verifier rotated the wrong way (KiCad's y axis points down) and compared front-layer pad sizes
  on flipped parts (the mezzanine standoff has different front/back pads): 22 false alarms, fixed and proven
  with a deliberate-corruption test
- `pcbnew.FootprintSave` can't guess the library type of an empty folder; used PCB_IO_KICAD_SEXPR directly
- QE round 1: APPROVED WITH NITS (placed-pad check on all 150 instances, 10 nm). Expect ≈ 58 graphics-only
  library-mismatch DRC warnings (Altium import); verifier now catches a mirrored library; Value = footprint name;
  SMD/THT attributes + courtyards missing since import → S6/layout item
- QE round 2: **APPROVED**, no findings. Its report didn't arrive: the session-message tool pauses a session's
  sends after 10 messages without user input; Nick noticed nothing was running and I read it from the transcript
**Next:** Nick's KiCad look, merge; S4 then done.

---

## 2026-10-05 — Sprint S5.a — Payload load switch: U9 → TPS26621, R11 DNP; S4.c closed

**Branch:** sprint/5a-u9-replacement
**Files touched:** BM_Mote_1_Load.kicad_sch, BM_Mote_1_Master.kicad_sch; new nereus.kicad_sym + sym-lib-table entry; SPEC, DESIGN (D18), TRACKER (+rule: Sofar brief), viewer, changelog, CLAUDE.md; new docs/design-review/sofar_brief.md
**ERC:** 74 / 626 (was 76/629)  ·  **Net diff:** 50/50; kept parts identical; U9/R32/R33/TP34 out, U11/R41/R42 in
**Done:**
- S4.c closed: Nick approved PR #10, merged (`1f906bc`)
- Part search: TI TPS26621DRCR (JLC C1848341 via LCSC listing; TI ACTIVE; SLVSDT4F Rev. F read). Nick approved
  it plus the R42 pull-down (SHDN active low) and dropping PGOOD
- Symbol drawn from TI's pin table with pins on U9's old wire ends, so most wiring stayed; R11 DNP
- Started `docs/design-review/sofar_brief.md` (Nick: a tight mote-vs-shield table for Sofar, ships with the
  board); TRACKER rule 6 now requires a row for every deviation
**Broke/surprised us:**
- TI's product summary claimed PGOOD variants; the datasheet pinout has none (FLT only)
- JLC's parts page renders only with the browser pane visible; found the part via LCSC search results
- Quick Look (qlmanage) hung; rendered the schematic PDF page via PDFKit instead
- R11's description field says "205K OHM" (Altium import junk) — S6 cleanup
- QE round 1 (fresh S5 session): CHANGES REQUESTED. F1 MAJOR: R34's PART NUMBER field still said 374 kΩ
  (set_properties only changed what I named). F2 MAJOR: R42 100 kΩ had no worst-case SHDN margin (I used the
  typical 2 µA; max is 10 µA) → 10 kΩ. Also RTN = GND recorded (§12.1), QE N6 closed, stale SPEC/DESIGN U9
  lines, footprint-link accounting, R41 fields harmonised, sofar_brief row 5 detail
- QE round 2: **APPROVED WITH NITS**; N5 (current-limit start wording) fixed
**Next:** Nick's KiCad look, merge; then S4.d (footprints).

---

## 2026-10-05 — Sprint S4.c — Power budget (docs only); S4.b closed

**Branch:** sprint/4c-power-budget
**Files touched:** docs/design-review/power_budget.md (new); SPEC open questions, TRACKER, DESIGN results row, viewer, changelog
**ERC:** 76 / 629 (unchanged)  ·  **Net diff:** none (docs only)
**Done:**
- S4.b closed: Nick's KiCad look OK, PR #9 merged (`11914fb`)
- Budget from primary sources: RPi docs (Zero 2 W: 2 A PSU, 350 mA typical; **no undervoltage
  detector on the Zero range**; all models want 5.1 V), RPi product brief (5 V 2.5 A), TI SLUSEF4A
  Fig 7-2 efficiency, Pulse P890.B, ADI product page (ADIN2111 77 mW typ), IPC-2221
- Findings: U10's temperature is the binding limit (≈ 42–57 °C rise at 1 A, 90–121 °C at 2 A), not the
  bus; JP1 bridge fine (2.4 A at 10 °C rise). Proposals for Nick: P-S4c-1 Pi load ≤ 1 A continuous;
  P-S4c-2 keep R38 13.7 kΩ (USB-range corners)
- Split S4: footprints become S4.d (library named `Vault` to match the board's IDs)
**Broke/surprised us:** analog.com and onsemi datasheets wouldn't download (timeouts / landing page);
ADIN2111 2.4 V p-p power and the FPF2700 limit stay open (0.30 W allowance used for the 3.3 V domain)
- Nick decided D15 (Pi ≤ 1 A) and D16 (R38 13.7 kΩ); Nick found the FPF2700 datasheet (Fairchild
  Rev. 1.0.3): R34 sets ≈ 0.74 A typical, so Sofar Q3 is answered
- QE round 1: CHANGES REQUESTED. F1 MAJOR: I'd missed Bristlemouth v1's 12 W per-module limit (already
  in SPEC) — with a 1 A Pi the payload gets ≈ 6.2 W, and U9's 0.74 A limit doesn't enforce that →
  P-S4c-3 for Nick. Also L1's 0.656 Ω drop/heat, thermal caveats + ψJT bench check, camera figures,
  13.5 kΩ option, footprint count wording, Fig 7-2 legend note
- Nick asked for a lifecycle check: **FPF2700MX (U9) is obsolete** (Digi-Key). Captured in S5 (replace with a
  JLC-sourceable part) plus a whole-BOM lifecycle check before S6
- Nick: payloads are small devices, keep Sofar's payload port (D17); U9 needs a JLC-sourceable replacement (S5)
- QE round 2: CHANGES REQUESTED. F4 MAJOR: R11 (0 Ω across U9) is fitted in our files (and on the mote board),
  so U9 was bypassed — D17's premise was wrong. Nick: R11 DNP so the switch and limit work (S5). N6: U9
  replacement must handle output caps / hard shorts up to 32 V
- QE round 3: CHANGES REQUESTED. F5 MAJOR: D17 contradicted SPEC hard constraint 7 (no power-path part
  changes, naming U9/R34/R11). Nick explicitly amended constraint 7: payload load switch excepted (R11 DNP,
  U9 replaced, R34/R33/R35 re-derived); everything else stays Sofar's. N7 D14 wording, N8 viewer line
- QE round 4: **APPROVED WITH NITS**; N9 (three summary lines missing the D17 exception) fixed
**Next:** Nick's review, merge; then the U9 replacement + R11 DNP, and S4.d (footprints).

---

## 2026-10-05 — Sprint S4.b — Shield powers the Pi through bridged link JP1; S4.a closed

**Branch:** sprint/4b-pi-5v-jumper
**Files touched:** BM_Mote_1_Master.kicad_sch; new nereus.pretty (SolderJumper-2_R1210_Bridged_NetTie) + fp-lib-table; tools/midwire.py (+ test); SPEC, DESIGN (D14, D5 superseded), TRACKER, viewer, changelog
**ERC:** 76 errors / 629 warnings (was 78/629)  ·  **Net diff:** 53/53; existing connections identical; new net PI_5V
**Done:**
- S4.a closed: Nick's KiCad look OK, PR #8 merged (`b394edb`)
- Design discussion with Nick: solder jumper vs 0 Ω resistor vs bridged link. Nick's call: the shield
  powers the Pi by default, no DNP part; pads that fit a 0 Ω resistor. → JP1 bridged net tie on R11's
  1210 pads (D14, revises D5's "open by default")
- Found and fixed a tool bug: J1's pins were invisible to midwire/bbox_clear (symbol name ends in `_2_3`)
**Broke/surprised us:**
- First JP1 layout (vertical, close to J1) put rotated text on top of J1's value and the PWR_FLAG;
  caught in the render, re-laid out horizontally higher up. A label part-way along a wire left the
  wire's end dangling (+1 ERC warning); moved the label to the end
- QE round 1 (same S4 session): CHANGES REQUESTED. F1 MAJOR: D14 missed the USB back-feed path
  (Pi USB 5 V → L6 → U10 high-side body diode → VBUS/bus/payload). Checked the Pi Zero 2 W reduced
  schematic (power USB feeds 5V directly; data port not shown). Nick chose a bench rule over a hardware
  guard: no USB 5 V source on a bridged board, shield powered or not. F2–F6 fixed (note cites D14,
  demo line, footprint renamed SolderJumper-2_R1210_Bridged_NetTie, dead code, cut guidance)
- QE round 2 (same session): **APPROVED**, no findings
**Next:** Nick's KiCad look, merge; then S4.c (power budget incl. USB peripherals, bridge current,
footprints, U10 thermal).

---

## 2026-10-05 — Sprint S4.a — 5 V converter for the Pi (copy of U5); S3 closed

**Branch:** sprint/4-5v-converter
**Files touched:** BM_Mote_1_Power.kicad_sch, BM_Mote_1_Master.kicad_sch; tools/schedit.py (copy_block, set_properties; 12 tests); SPEC, DESIGN (D13), TRACKER, viewer, changelog, qe/S4.md
**ERC:** 78 errors / 629 warnings (was 76/562)  ·  **Net diff:** 53/53, 0 opens, 0 shorts; existing parts identical; 5 new nets
**Done:**
- S3 closed: Nick approved PR #7, merged (`09af9d8`); S3 QE session archived
- U10 block copied from U5 with `copy_block`; R38 13.7 kΩ, C56/C57 22 µF 16 V, C58 4.7 µF 10 V;
  L6 = same 8.2 µH as L3 (Nick). Values from TI SLUSEF4A and Pulse P890.B (read, cited in SPEC)
- 5V_PI to the Top-Level sheet via a new sheet pin + TP38
- Visual check of both sheets (SVG render)
**Broke/surprised us:**
- First placement of the 5V_PI wire ran across TP23/TP24's graphics on the Top-Level sheet
  (bbox_clear only checks pins, wire ends, labels and symbol origins, not bodies or text).
  Caught in the render; moved TP23/TP24 + their GND symbols 7.62 mm down (same connections)
- Murata's DC-bias tool needs a licence accepted, so the 22 µF parts' effective capacitance at
  5 V is an open question rather than a number; the Yageo datasheet link triggered a download
  prompt in Nick's browser pane (read via fetch instead)
- QE round 1 (fresh S4 session, report sent to me directly): CHANGES REQUESTED. F1 MAJOR: my
  `set_properties` silently skipped values containing `\"`, leaving stale 0603 size fields on
  C56/C57. Fixed the regex, made it refuse partial parses, added a test. Also F2 thermal item
  scheduled (S4.c), demo line, D13 ripple basis/Vout band/TI Table 9-2, R38 citation, C58 nudged.
  Report: `qe/S4.md`
- QE round 2 (same session): **APPROVED WITH NITS**; N1–N3 fixed (report typo, C58 10V text, bench item)
**Next:** Nick's KiCad look, merge; then S4.b (jumper to Pi pins 2/4).

---

## 2026-10-05 — Sprint S3 — Keep Sofar's power path for this board (D12)

**Branch:** sprint/3-power-path
**Files touched:** SPEC, DESIGN (D12; D7/D8 superseded), POWER_PATH (deferred banner), SOFAR_QUESTIONS (Q1, Q5 deferred), TRACKER, checklist viewer, README, CLAUDE.md, /agent-entry, PROMPTS §5, quality-engineer.md, qe/S3.md; no schematic change
**ERC:** 76 errors / 562 warnings (unchanged)  ·  **Net diff:** 53/53, 0 opens, 0 shorts (unchanged)
**Done:**
- Nick chose S3 next, then decided to cut risk on the first board: keep the mote's power path
  exactly as Sofar built it, rated ~20 W absolute max (890 mA per port inductor at 24 V). The
  design has years in the field and already powers Nick's cameras
- 50 W deferred to a later spin, scoped with the future motor load; the S3 inductor/e-fuse
  work moved to the TRACKER Icebox with its evidence kept in POWER_PATH.md
- S4 power budget and the S5 payload connector now check against 890 mA
- QE round 1 (fresh S3 session): CHANGES REQUESTED, schematic side all clean. I'd missed the
  README headline (still ~50 W) and left Sofar Q1 (e-fuse, worded for 50 W) as "send now"
  while its work moved to the Icebox. Fixed: README matches SPEC; Q1 deferred like Q5; Q3
  wording, POWER_PATH S3 references and the TRACKER demo line fixed. Report: `qe/S3.md`
- Process (Nick): the QE sends its report straight to the design session when done; Nick
  doesn't relay. Written into TRACKER rule 3.4, `quality-engineer.md` and PROMPTS §5
- QE round 2 (same session, report sent to me directly): **APPROVED WITH NITS**; all 5 fixed
  (PR body, process wiring, DEV_LOG layout, TRACKER demo line, qe/S3.md wording)
**Broke/surprised us:** nothing in the design. I proposed asking Sofar whether 20 W holds
when potted; Nick declined (field-proven), so no Q6
**Next:** Nick's docs review, merge; then S4 (5 V converter).

---

## 2026-10-05 — Sprint S2 — Mezzanine removed, Pi header J1 placed

**Branch:** sprint/2-pi-header
**Files touched:** BM_Mote_1_Master.kicad_sch; tools/schedit.py (new, 7 tests); exclusion list emptied; docs
**ERC:** 76 errors / 562 warnings (was 65/590)  ·  **Net diff:** 53/53, 0 opens, 0 shorts, 0 excluded
**Done:**
- Deleted P1, R9, 12 TPs, 14 mezzanine labels, 5 orphan power symbols, 2 NCs, 69 wires, 12 junctions
- Placed J1 (stock KiCad Pi header + 2×20 socket footprint), GND + PWR_FLAG, NC on 3V3, VBUS PWR_FLAG
- Verified: all 277 kept pins keep identical connections; J1's 8 GND pins on GND; visual check of the sheet (SVG render)
**Broke/surprised us:**
- First deletion pass trimmed the wire under the I2C1 labels (they sat part-way along a stub
  to P1), leaving them unnamed. Caught by the before/after net-name diff; schedit now shortens
  such wires instead of deleting them (test added)
- The mote's I2C pull-ups (R26/R27) were on the STM32 sheet, so the shield now has none.
  Nick decided the shield adds them (D11, S5 task)
- ERC errors rose, not fell: −27 (12 TPs, 13 mezzanine labels, U5 VIN, U6 GND) / +38 (29 J1 pins,
  8 I2C1/SCL/SDA labels now one-pin, J1.2)
- QE round 1 (separate session): CHANGES REQUESTED — my ERC owner table was hand-filtered and
  missed FID1–6, the SW_FLAGB/SW_PGOOD sheet pins and #PWR34 (also undercounted in S1). Fixed
  with `tools/ercsum.py`; also deleted a stale MEZZANINE text box. Report: `docs/design-review/qe/S2.md`
- QE round 2 (fresh session): APPROVED WITH NITS. N1: my F1 fix claimed SW_FLAGB/SW_PGOOD
  "lost P1" — false (copper: they never reached P1). Lesson: a fix to the docs is still a claim;
  check it against copper/netlist before writing it. All N1–N7 fixed; ercsum hardened
- Process: one standing QE session per sprint (Nick)
- QE round 3 (same standing session): **APPROVED**; 2 nits (R1 log wording, R2 TRACKER date) fixed
- Nick's KiCad look OK, via the worktree `open` command (his earlier S0/S1 looks had opened the
  stale main checkout; this look also confirmed S1's R8 junctions). PR #5 merged (`5885820`)
- Close-out slip: my close-out script failed on one HTML text match, but the chained git commands
  still committed and merged TRACKER alone. This follow-up PR syncs the viewer and DEV_LOG
**Next:** S2 done. Choose S3 (50 W power path) or S4 (5 V converter); fresh QE session for it.

## 2026-10-05 — Sprint S1 — Altium import fixed: 53/53 nets match the copper

**Branch:** sprint/1-import-fix
**Files touched:** ADIN2111, Load, Master, PoDL, PowerMon sheets; Processor/USB sheets deleted; tools/midwire.py (new); netcheck exclusions; docs
**ERC:** 65 errors / 590 warnings (was 90/578)  ·  **Net diff:** 53/53 matched, 0 opens, 0 shorts (14 S2 parts excluded)
**Done (Nick away; worked through the S1 checklist unattended, as Nick asked):**
- Exclusion list for S2 deletions (P1, R9, 12 TPs), approved by Nick
- 21 pins sat mid-wire (Altium connects them, KiCad doesn't): wire split + junction at each, via `tools/midwire.py --fix`
- Orphan Processor/USB sheets deleted; 65 `#PWR?` numbered `#PWR01`–`#PWR65`
- ADIN_VDDIO label verified correct, not changed; ADIN SPI/INT/RST verified to reach the Top-Level sheet
- Every remaining ERC error assigned to a sprint (DESIGN.md); edit log in `docs/design-review/changelog.md`
**Broke/surprised us:**
- The 33-junction zip had never been applied to the live project. Applied wholesale it
  fixed 4 nets but broke others (U9.1, U4.1/2, U1.39, U1.18/46, T1.6). Tested one junction
  at a time: each connects its pin but knocks a neighbour off the same wire. Splitting the
  wire is clean. The zip's 33 locations were right; the method wasn't
- The "65 duplicate references" never showed in kicad-cli ERC, because the CLI numbers `#PWR?` in its own report
- kicad-cli PDF size: `du` reported disk blocks; check.sh now prints real bytes
**Next:** S1 demo passed and KiCad look OK (Nick, 2026-10-05) → S1 done. Next: S2, mezzanine → Pi header (plan nibble).

## 2026-10-05 — Sprint S0 — Net check built; baseline recorded

**Branch:** sprint/0-net-check
**Files touched:** tools/ (new), .gitignore, docs/design-review/netcheck.md, docs/*, checklist HTML
**ERC:** 90 errors / 578 warnings  ·  **Net diff:** 42/68 matched, 26 opens, 0 shorts
**Done:**
- `tools/netcheck.py` (stdlib, 5 unit tests) compares schematic connectivity
  with the mote copper; `tools/check.sh` runs ERC + netlist + PDF + netcheck
- Baseline in DESIGN.md; every open listed in `docs/design-review/netcheck.md`
**Broke/surprised us:**
- The junction fix isn't complete: 26 copper nets are still split, mostly
  single pins on wire midpoints (TP20/21/22, C13/C14, D4/D5 pin 1, R1 pin 1, …)
- The untouched reference schematic has 38 opens against its own copper, so
  this is import damage
- The probe's 48/74 became 42/68 in the tool: same opens, minus 6 trivially
  matched single-pin nets
**Next:** S0 demo passed (Nick, 2026-10-05) → S0 done. Next: S1, fixing the 26 opens (plan nibble).

## 2026-10-04 — Sprint S0 — Project renamed, junk untracked, rating defined

**Branch:** sprint/0-repo-baseline
**Files touched:** project folder (rename only), 58 files untracked, docs/*
**ERC:** 90 errors / 578 warnings, the same before and after  ·  **Net diff:** clean (library path only)
**Done:**
- S0.1: `_002` → `nereus_Pi_shield_ADIN2111/`; the stray `.kicad_pro` was byte-identical
- S0.2: `git rm --cached` for everything `.gitignore` covers
- Recorded Nick's decisions: ~50 W absolute max at 24 V (D8); potted, so newly
  sourced parts can't be electrolytics or PPTCs, while vetted Sofar parts stay
  as-is (D9, SPEC constraint 8)
- Bourns SRF1260 datasheet figures added to POWER_PATH; this explains the mote's 20 W
- New `docs/SOFAR_QUESTIONS.md` (Q1 e-fuse, Q2–Q4 moved from SPEC, Q5 MSD1514/damping)
- `pi-shield-checklist.html` rebuilt to mirror TRACKER: S0–S6, Sofar questions,
  status panel; finished work marked "✓ in repo" in the data (D2 revised;
  TRACKER rule 6 now requires syncing it every PR)
**Broke/surprised us:**
- kicad-cli ERC names different example labels from run to run; compare counts, not text
- No fuse or e-fuse anywhere on the through path (Nick remembered one; asked Sofar, Q1)
- The FPF2700 datasheet link on onsemi is dead
**Next:** S0.3, the net-check method.

## 2026-10-04 — Pre-work — Docs fitted to the KiCad project

**Branch:** claude/kicad-docs-setup-19be00
**Files touched:** CLAUDE.md, README.md, .gitignore, docs/*, .claude/skills/*, checklist banner
**ERC:** not run (no schematic edits)  ·  **Net diff:** n/a
**Done:**
- Templates filled for schematic capture; sprint ladder S0–S6 built from the
  checklist, plus the new S3 (50 W power path)
- `docs/POWER_PATH.md` seeded from Evan's two Sofar references
- `/agent-entry` and `/capture-task` skills added
**Broke/surprised us:**
- Live PoDL inductors are SRF1260-101M (~20 W), so 50 W touches the whole power path
- The Processor and USB sheets are orphan files, not part of the hierarchy
- MSD1514 (Sofar's 50 W pick) is 15.5 × 15.5 × 14.2 mm, which is tight on a Pi Zero board
**Next:** S0.1, plan nibble — Nick gate.
