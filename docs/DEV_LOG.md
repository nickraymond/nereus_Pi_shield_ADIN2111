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
**Next:** QE review (same S4 session), Nick's KiCad look, merge; then S4.c (power budget, bridge current,
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
