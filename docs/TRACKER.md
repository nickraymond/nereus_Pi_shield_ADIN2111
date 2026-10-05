# TRACKER.md — Sprint Ladder & Rules

*The agent entry point and the single source of truth for progress.*
*Last updated: 2026-10-05 · Owner/gate: **Nick***

---

## Rules for Agents (READ FIRST, EVERY SESSION)

1. **Read this whole document cover-to-cover first, every session.** Then skim
   `docs/SPEC.md` and `docs/DESIGN.md` (`docs/POWER_PATH.md` only for the deferred 50 W revision).
   Read the top ~3 entries of `docs/DEV_LOG.md`.
2. **Take small bites.** One TODO, or one tight group within a sprint, at a
   time. If SPEC.md is too thin to inform the bite, stop and ask Nick.
3. **Nibbles per bite:**
   1. **Plan** — list the exact edits (sheet, refs, labels, values) with a
      citation for each. Change no files. *Gate: Nick approves.*
   2. **Edit + check** — confirm KiCad is closed, edit, then run ERC and export
      the netlist (commands below). Diff the nets against the last baseline.
      Flag Nick on any substantial plan change.
   3. **Open the PR, unmerged.**
   4. **QE review** — in a **separate Code session, never a sub-agent**, following
      `.claude/agents/quality-engineer.md` (Opus 5.5, high effort). **One standing QE
      session per sprint:** the first review of a sprint is spawned as a task chip Nick
      starts; later rounds in that sprint are sent to the same session (session message);
      a new sprint gets a fresh QE session. The QE is read-only; its report stays in its
      own transcript. The design agent fetches it, saves it to
      `docs/design-review/qe/<sprint>.md` and posts it on the PR. CHANGES REQUESTED →
      fix, push, new QE review until APPROVED. Don't edit files while the QE runs.
   5. **Nick's KiCad review** — only after QE APPROVED. Give copy-pastable
      commands and say exactly what to look at.
   6. **Merge** — only after both approvals.
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
`python3 tools/test_netcheck.py` and `python3 tools/test_midwire.py`, `python3 tools/test_schedit.py` and `python3 tools/test_ercsum.py`. ERC tables: `python3 tools/ercsum.py --items`.

### Project layout

```
docs/                         SPEC TRACKER DESIGN POWER_PATH SOFAR_QUESTIONS DEV_LOG PROMPTS
docs/design-review/           netcheck.md, out/ (check outputs), final review package
nereus_Pi_shield_ADIN2111/    live KiCad project (the only design agents edit)
tools/                        check.sh, netcheck.py, midwire.py, schedit.py, ercsum.py (+ tests)
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

### S2 — Mezzanine (P1) → Pi header; grounds  `[x]`
- [x] Delete P1, R9 and test points TP4, 6, 9, 10, 11, 12, 14, 15, 16, 17, 18, 33
      (keep R10 and TP19); exclusion list now empty
- [x] Delete leftover STM32/mezzanine labels and wires (14 labels, 5 orphan power
      symbols, 69 wires); `ADIN_*`, `I2C1_*` kept. Kept-pin connectivity verified identical
- [x] Place J1 `Connector:Raspberry_Pi_2_3` on Top-Level, footprint
      `Connector_PinSocket_2.54mm:PinSocket_2x20_P2.54mm_Vertical`
- [x] All Pi GND pins (6, 9, 14, 20, 25, 30, 34, 39) → GND; pins 1 and 17 no-connect flag
- [x] PWR_FLAG on VBUS and GND
- [x] QE review: **APPROVED** in round 3 (round 1 changes requested, round 2 nits; all fixed) — `docs/design-review/qe/S2.md`
- [x] Checkpoint: Nick looks at the Top-Level sheet in KiCad (also confirmed S1's R8 junctions)
**Demo (Nick):** `tools/check.sh` exits 0 → `netcheck: 53/53 … 0 opens, 0 shorts; 0 parts
excluded`, ERC `Errors 76  Warnings 562` (−27/+38 vs S1; 30 are J1 pins for S4/S5).
In KiCad: P1 gone, J1 in clear space with GND + PWR_FLAG below, an X on pin 1 (3V3).
ERC detail: `python3 tools/ercsum.py --items` (every error has an owner in DESIGN.md).
**Result:** QE APPROVED (round 3); demo passed and KiCad look OK (Nick, 2026-10-05).

### S3 — Power path: keep Sofar's  `[~]`
**Goal:** settle the power path for this board. Decided: keep the mote's power path
unchanged, ~20 W absolute max = 890 mA per port inductor at 24 V (DESIGN D12, Nick
2026-10-05). The 50 W work moved to the Icebox, kept in `docs/POWER_PATH.md`.
- [x] Nick defines the rating — first ~50 W (D8), then the mote's ~20 W for this board (D12)
- [x] Record D12 in SPEC, DESIGN, POWER_PATH, SOFAR_QUESTIONS (Q5 deferred), TRACKER and the viewer;
      no schematic change
- [ ] QE review (fresh S3 session), then Nick reviews the docs diff (nothing to see in KiCad)
**Demo (Nick):** `tools/check.sh` → unchanged from S2: ERC `Errors 76  Warnings 562`,
`netcheck: 53/53 … 0 opens, 0 shorts`; `git diff main --stat` touches docs only.

### S4 — 5 V converter for the Pi (copy of U5)  `[ ]`
*Feeds from VBUS on the mote's unchanged power path (D12).*
- [ ] Copy U5 block with new refs (U5, L3, C28–C31, C33, R20–R23)
- [ ] Rename copied local labels `3V3_*` → `5V_*`
- [ ] Set 5 V: R23 copy → 13.7 kΩ (confirm the 0.6 V reference in the LMR51430 datasheet)
- [ ] Inductor for 5 V out at 24 V in, with citation
- [ ] Output caps rated 10 V or 16 V, with real part numbers
- [ ] Footprints for new parts extracted to `mote.pretty` (read board, never write it)
- [ ] `5V_PI` to Top-Level; SolderJumper_2_Open to Pi pins 2 and 4
- [ ] Bus power budget estimate (shield + Pi + payload vs the 890 mA / ~20 W rating, D12)
**Demo (Nick):** ERC + net diff; `5V_PI` net contains exactly the intended pins.

### S5 — Pi header wiring, ADIN details, load switch  `[ ]`
- [ ] Wire the pin map in DESIGN.md; leave reserved (26, 29, 32, 33) and
      avoided (8, 10, 27, 28) pins free
- [ ] ADIN_PWR 100 kΩ pull-down (unless AP22913 has one internally); ADIN_RST
      pull-up only if needed; no pull-up on MISO — each with a citation
- [ ] Document the ADIN power-up order
- [ ] SW_EN/SW_FLAGB/SW_PGOOD → pins 36/38/40 (keep R32 pull-up). SW_FLAGB/SW_PGOOD sheet pins are
      unconnected on the Top-Level sheet since import; reuse their R33/R35 pull-ups and TP34/TP35
- [ ] VBUS_OUT + GND → 2-pin connector rated for at least 890 mA (D12)
- [ ] Add I2C pull-ups on I2C1_SDA/SCL to the shield's 3V3 (Nick, 2026-10-05: the Pi
      needs them). Reuse the mote's vetted parts: R26/R27 = 4.7 kΩ ERJ-2RKF4701X, 0402
      (reference Processor sheet). Note the combined value if the Pi also has pull-ups
      (QE: the Pi documents 1.8 kΩ on GPIO2/3 → ≈1.3 kΩ combined; cite a primary source)
- [ ] Choose the pull-up rail and document power sequencing: shield 3V3 and Pi 3V3 are
      separate rails, so one powered while the other is off can back-power through pull-ups /
      IO clamp diodes (applies to the ADIN SPI/control lines too) — QE S2 risk
- [ ] Every new net verified from the exported netlist
**Demo (Nick):** net diff lists every new net with exactly its intended pins.

### S6 — Design review package  `[ ]`
- [ ] ERC clean, or every remaining item justified (incl. FID1–6 hidden NC pins, the
      regulator switch-node/rail power pins, #PWR34 ADIN_VDDIO)
- [ ] Remove/update stale sheet notes (e.g. "Processor + onboard logic runs off 3V3…" on Top-Level)
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
- **50 W revision** (after production; scoped with the future motor load). Deferred S3 work,
  evidence in `docs/POWER_PATH.md` (DESIGN D7/D8 superseded by D12 for this board):
  MSD1514 fit check (SolidWorks); sort Evan's references; confirm Coilcraft figures on one
  basis; audit every path part vs the rating and potting rules; damping retune (SOFAR Q5);
  potting-safe bidirectional e-fuse (SOFAR Q1); P2–P4 decisions; L1/L2 swap and re-rated parts
- 100 W variant (see POWER_PATH sources [G])
