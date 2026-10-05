# TRACKER.md — Sprint Ladder & Rules

*The agent entry point and the single source of truth for progress.*
*Last updated: 2026-10-04 · Owner/gate: **Nick***

---

## Rules for Agents (READ FIRST, EVERY SESSION)

1. **Read this whole document cover-to-cover first, every session.** Then skim
   `docs/SPEC.md` and `docs/DESIGN.md` (plus `docs/POWER_PATH.md` in S3).
   Read the top ~3 entries of `docs/DEV_LOG.md`.
2. **Take small bites.** One TODO, or one tight group within a sprint, at a
   time. If SPEC.md is too thin to inform the bite, stop and ask Nick.
3. **Four nibbles per bite:**
   1. **Plan** — list the exact edits (sheet, refs, labels, values) with a
      citation for each. Change no files. *Gate: Nick approves.*
   2. **Edit + check** — confirm KiCad is closed, edit, then run ERC and export
      the netlist (commands below). Diff the nets against the last baseline.
      Flag Nick on any substantial plan change.
   3. **Nick looks** — Nick opens the project in KiCad. Give copy-pastable
      kicad-cli commands and say exactly what to look at.
   4. **Open PR.**
4. **Feature branch for all new work** — `sprint/<n>-<slug>`. Never commit to main.
5. **Every sprint ends with a demo Nick can run** — kicad-cli commands that
   produce the ERC report, net diff and PDF, with the expected result.
   Commands go in the sprint's Demo line and the PR description.
6. **End of every session:** DEV_LOG.md entry (newest on top); DESIGN.md updated
   on any design or decision change; **`pi-shield-checklist.html` synced to
   this tracker** (items, `done` flags, the status panel's "Updated / Now" line)
   in the same PR.
7. **Facts carry sources; unknowns get flagged, not guessed.**
8. **KiCad files:** never write a `.kicad_pcb`. Reference designs and
   `Archive/` are read-only. After every `.kicad_sch` text edit, kicad-cli must
   load the schematic and ERC must run, or the edit is not done.
9. **The board is Nick's.** Answer layout and routing questions; don't act on them.

### Check command

```bash
tools/check.sh
```

This runs ERC, netlist export, PDF export and `tools/netcheck.py`. Raw outputs
go to `docs/design-review/out/` (git-ignored); `docs/design-review/netcheck.md`
is tracked. The exit code is netcheck's (0 = matches the copper). Tool tests:
`python3 tools/test_netcheck.py` and `python3 tools/test_midwire.py`.

### Project layout

```
docs/                         SPEC TRACKER DESIGN POWER_PATH SOFAR_QUESTIONS DEV_LOG PROMPTS
docs/design-review/           netcheck.md, out/ (check outputs), final review package
nereus_Pi_shield_ADIN2111/    live KiCad project (the only design agents edit)
tools/                        check.sh, netcheck.py, midwire.py (+ tests)
KiCAD_reference_designs/      mote + UrchinCam (read-only)
Archive/                      earlier iterations, junction fix (read-only)
pi-shield-checklist.html      shared visual view of this tracker (agents keep it in sync)
.claude/skills/               /agent-entry, /capture-task
```

---

## Sprint ladder

State key: `[ ]` pending · `[~]` in progress · `[x]` done · `[!]` blocked

### S0 — Repo & baseline  `[x]`
**Goal:** one live project and a repeatable check.
- [x] S0.1 Rename `nereus_Pi_shield_ADIN2111_002/` → `nereus_Pi_shield_ADIN2111/`
      (stray `.kicad_pro` was byte-identical; removed. ERC 90/578 unchanged)
- [x] S0.2 Untrack files now covered by `.gitignore` (58 files; still on disk)
- [x] S0.3 Net-check method: `tools/netcheck.py` + `tools/check.sh`; method in DESIGN.md
- [x] S0.4 First baseline in DESIGN.md: ERC 90/578; netcheck 42/68 matched, 26 opens, 0 shorts
**Demo (Nick):** `tools/check.sh` → `ERC messages: 668  Errors 90  Warnings 578`
and `netcheck: 42/68 copper nets matched; 26 opens, 0 shorts`; open
`docs/design-review/netcheck.md` to see every open. Exit code 1 is expected
until S1 fixes the opens.
**Result:** demo passed 2026-10-05 (Nick).

### S1 — Fix the Altium import  `[x]`
- [x] Fix the opens: 12 are mezzanine nets → `docs/design-review/excluded_parts.txt`
      (S2 deletions); 21 pins sat mid-wire → wire split + junction (`tools/midwire.py`).
      The 33-junction zip had never been applied, and tested alone it breaks
      neighbouring connections in KiCad 9, so it was not used
- [x] ADIN_VDDIO label: verified already on the ADIN_VDDIO net with the pull-ups; left as is
- [x] Remove the unused Processor and USB sheet files
- [x] Number all `#PWR` symbols uniquely (65 → `#PWR01`–`#PWR65`)
- [x] Baseline report: netcheck 53/53, 0 opens; ERC 65/590, every error assigned (DESIGN.md)
- [x] Checkpoint: Nick opens it in KiCad (30-second look)
**Demo (Nick):** `tools/check.sh` exits 0 → `midwire: 0`, `netcheck: 53/53 …
0 opens, 0 shorts; 14 parts excluded`, ERC `Errors 65  Warnings 590`. Then open
the project in KiCad: the 21 fixed points are listed in
`docs/design-review/changelog.md` (e.g. R8 on the PowerMon sheet now shows
junctions at both ends).
**Result:** demo passed and KiCad look OK (Nick, 2026-10-05).

### S2 — Mezzanine (P1) → Pi header; grounds  `[ ]`
- [ ] Delete P1, R9 and test points TP4, 6, 9, 10, 11, 12, 14, 15, 16, 17, 18, 33
      (keep R10 and TP19); remove each from `docs/design-review/excluded_parts.txt`
- [ ] Delete leftover STM32/mezzanine labels and wires (keep `ADIN_*`, `I2C1_*`)
- [ ] Place `Connector:Raspberry_Pi_2_3` on Top-Level, footprint
      `Connector_PinSocket_2.54mm:PinSocket_2x20_P2.54mm_Vertical`
- [ ] All Pi GND pins (6, 9, 14, 20, 25, 30, 34, 39) → GND; pins 1 and 17 unconnected
- [ ] PWR_FLAG on VBUS and GND
**Demo (Nick):** ERC + net diff → only the intended nets changed.

### S3 — 50 W power path: inductors & design decisions  `[ ]`
**Goal:** a ~50 W absolute-max (2.083 A at 24 V), potting-safe PoDL path with
two-winding magnetics, decided by Nick on cited evidence. Working file:
`docs/POWER_PATH.md`.
- [x] Nick defines the rating (POWER_PATH §1) — *gate* (DESIGN D8)
- [ ] Nick confirms MSD1514 (15.5 × 15.5 × 14.2 mm) fit in SolidWorks
- [ ] Sort Evan's references; record facts with citations ([G], [E], [J], [DS])
- [ ] Confirm candidate figures against Coilcraft datasheets, normalised to one basis (§2–3)
- [ ] Audit every part in the path against the rating and potting rules (§4)
- [ ] Damping: keep C22/C23/R15/R16; retune only if the new magnetics need it (SOFAR_QUESTIONS Q5)
- [ ] Propose through-path protection (e-fuse) that works in both directions and is safe to pot (SOFAR_QUESTIONS Q1)
- [ ] Nick decides P1–P4 → DESIGN.md decision log
- [ ] Schematic edits: L1/L2 swap, re-rated path parts, damping/bulk provisions,
      footprints findable (`mote.pretty`)
**Demo (Nick):** POWER_PATH §4 has no open rows; ERC + net diff show only the
agreed changes.
**Needs:** Nick's rating definition; any further references from Evan.

### S4 — 5 V converter for the Pi (copy of U5)  `[ ]`
*Input side depends on S3 decisions.*
- [ ] Copy U5 block with new refs (U5, L3, C28–C31, C33, R20–R23)
- [ ] Rename copied local labels `3V3_*` → `5V_*`
- [ ] Set 5 V: R23 copy → 13.7 kΩ (confirm the 0.6 V reference in the LMR51430 datasheet)
- [ ] Inductor for 5 V out at 24 V in, with citation
- [ ] Output caps rated 10 V or 16 V, with real part numbers
- [ ] Footprints for new parts extracted to `mote.pretty` (read board, never write it)
- [ ] `5V_PI` to Top-Level; SolderJumper_2_Open to Pi pins 2 and 4
- [ ] Bus power budget estimate (shield + Pi + payload vs S3 rating)
**Demo (Nick):** ERC + net diff; `5V_PI` net contains exactly the intended pins.

### S5 — Pi header wiring, ADIN details, load switch  `[ ]`
- [ ] Wire the pin map in DESIGN.md; leave reserved (26, 29, 32, 33) and
      avoided (8, 10, 27, 28) pins free
- [ ] ADIN_PWR 100 kΩ pull-down (unless AP22913 has one internally); ADIN_RST
      pull-up only if needed; no pull-up on MISO — each with a citation
- [ ] Document the ADIN power-up order
- [ ] SW_EN/SW_FLAGB/SW_PGOOD → pins 36/38/40 (keep R32 pull-up)
- [ ] VBUS_OUT + GND → 2-pin connector rated for the S3 rating
- [ ] Every new net verified from the exported netlist
**Demo (Nick):** net diff lists every new net with exactly its intended pins.

### S6 — Design review package  `[ ]`
- [ ] ERC clean, or every remaining item justified
- [ ] Net check: kept nets match the copper; every new net listed
- [ ] Schematic PDF (all sheets)
- [ ] Change log of every edit
- [ ] Open questions and proposed values, with datasheet citations
- [ ] Pin map, power budget, BOM changes
**Demo (Nick):** open `docs/design-review/` → a complete package, ready to review.

---

## Nick-owned (not agent work — listed so the boundary is clear)

Review & decide (independent net check, colleague review, freeze with a git
tag) → board outline → update board & place parts → route & DRC → bench
power-up. Agents answer questions here; they don't edit.

---

## Icebox (captured, not scheduled)

- Hardware watchdog switching the 5 V converter's enable (e.g. TI TPL5010)
- Shared nereus-lib from the UrchinCam parts
- 100 W variant (see POWER_PATH sources [G])
