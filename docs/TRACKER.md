# TRACKER.md — Sprint Ladder & Rules

*The agent entry point and the single source of truth for progress.*
*Last updated: 2026-11-10 · Owner/gate: **Nick***

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
      a new sprint gets a fresh QE session. The QE is read-only. Every review request
      names the design session; when done, the QE **sends its report to that session**
      (session message), so Nick never relays. The design agent saves it to
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
   **Every deliberate change from Sofar's mote goes in `docs/design-review/sofar_brief.md`**
   (one row: mote vs shield vs why), shipped with the board files.
7. **Facts carry sources; unknowns get flagged, not guessed.**
8. **KiCad files:** never write a `.kicad_pcb` (exception: a layout experiment's own board in `experiments/<name>/`, D31). Reference designs and
   `Archive/` are read-only. After every `.kicad_sch` text edit, kicad-cli must
   load the schematic and ERC must run, or the edit is not done.
9. **The board is Nick's.** Answer layout and routing questions; don't act on them, except inside an approved layout
   experiment (`experiments/`, D31), which is never merged.

### Check command

```bash
tools/check.sh
```

This runs ERC, netlist export, PDF export and `tools/netcheck.py`. Raw outputs
go to `docs/design-review/out/` (git-ignored); `docs/design-review/netcheck.md`
is tracked. The exit code is netcheck's (0 = matches the copper). Tool tests:
`python3 tools/test_netcheck.py` and `python3 tools/test_midwire.py`, `python3 tools/test_schedit.py`, `python3 tools/test_ercsum.py`, `python3 tools/test_fpextract.py`, `python3 tools/test_ercexclude.py`, `python3 tools/test_fpattrs.py` and `python3 tools/test_bompdf.py`. ERC tables: `python3 tools/ercsum.py --items`.
ERC exclusions: `python3 tools/ercexclude.py` (check) / `--write` (regenerate from `docs/design-review/erc_justifications.csv`).

### Project layout

```
docs/                         SPEC TRACKER DESIGN POWER_PATH SOFAR_QUESTIONS DEV_LOG PROMPTS
docs/design-review/           netcheck.md, out/ (check outputs), final review package
nereus_Pi_shield_ADIN2111/    live KiCad project (the only design agents edit)
tools/                        check.sh, netcheck.py, midwire.py, schedit.py, ercsum.py, fpextract.py, ercexclude.py, fpattrs.py, bompdf.py (+ tests)
experiments/                  layout experiments (D31): briefs on main; each run on its own branch, never merged
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

### S3 — Power path: keep Sofar's  `[x]`
**Goal:** settle the power path for this board. Decided: keep the mote's power path
unchanged, ~20 W absolute max = 890 mA per port inductor at 24 V (DESIGN D12, Nick
2026-10-05). The 50 W work moved to the Icebox, kept in `docs/POWER_PATH.md`.
- [x] Nick defines the rating — first ~50 W (D8), then the mote's ~20 W for this board (D12)
- [x] Record D12 in SPEC, DESIGN, POWER_PATH, SOFAR_QUESTIONS (Q5 deferred), TRACKER and the viewer;
      no schematic change
- [x] QE review (fresh S3 session): **APPROVED WITH NITS** in round 2, nits fixed — `docs/design-review/qe/S3.md`
- [x] Nick reviews the docs diff (nothing to see in KiCad)
**Demo (Nick):** `tools/check.sh` → unchanged from S2: ERC `Errors 76  Warnings 562`,
`netcheck: 53/53 … 0 opens, 0 shorts`; `git diff main --stat` touches only docs, the viewer, README, CLAUDE.md, the skill and the QE role file.
**Result:** QE APPROVED WITH NITS (round 2); Nick approved; PR #7 merged (`09af9d8`), 2026-10-05.

### S4 — 5 V converter for the Pi (copy of U5)  `[x]`
*Feeds from VBUS on the mote's unchanged power path (D12). Bites: S4.a converter (done),
S4.b link to the Pi, S4.c power budget (docs), S4.d footprints. Values: DESIGN D13, D14.*
- [x] Copy U5 block with new refs above the mote board's highest (U10, L6, C53–C58, R37–R40, TP38)
- [x] Rename copied local labels `3V3_*` → `5V_*`
- [x] Set 5 V: R38 (copy of R23) = 13.7 kΩ RC0402FR-0713K7L; VREF 0.6 V confirmed (TI SLUSEF4A §7.5, §9.2.2.2)
- [x] Inductor: L6 = PA5432.822NLT, same as L3 (Nick, 2026-10-05; Pulse P890.B)
- [x] Output caps: C56/C57 22 µF 16 V GRM21BR61C226ME44L (0805), C58 4.7 µF 10 V GRM155R61A475MEAAD (0402)
- [x] `5V_PI` reaches the Top-Level sheet (new sheet pin, TP38, `5V_PI` label)
- [x] QE review (fresh S4 session): **APPROVED WITH NITS** in round 2, nits fixed — `docs/design-review/qe/S4.md`
- [x] Nick's KiCad look — S4.a (PR #8 merged, `b394edb`)
- [x] S4.b: JP1 bridged link `5V_PI` → `PI_5V` (Pi pins 2/4), #FLG03; footprint `nereus:SolderJumper-2_R1210_Bridged_NetTie`
      in a new project library `nereus.pretty` (D14, revises D5); midwire now sees J1's pins (tool fix)
- [x] S4.b: QE review (same S4 session): **APPROVED** in round 2 — `docs/design-review/qe/S4.md`
- [x] S4.b: Nick's KiCad look (PR #9 merged, `11914fb`)
- [x] S4.c: bus power budget, U10/L6 losses, JP1 bridge current, Pi supply voltage → `docs/design-review/power_budget.md`
- [x] S4.c: Nick decided D15 (Pi load ≤ 1 A continuous) and D16 (keep R38 13.7 kΩ)
- [x] S4.c: payload port decided (D17): switched and limited by U9; R11 DNP and U9 replacement in S5
- [x] S4.c: QE review (same S4 session): **APPROVED WITH NITS** in round 4, nit fixed — `docs/design-review/qe/S4.md`
- [x] S4.c: Nick's review of power_budget.md (PR #10 merged, `1f906bc`)
- [x] S4.d: all footprints findable — the 43 footprints the schematic uses, extracted read-only from the mote board
      into `mote.pretty` (nickname `Vault`, matching the board IDs); every bare field → `Vault:<name>` (D19)
- [x] S4.d: QE review (standing S4 session): **APPROVED** in round 2 — `docs/design-review/qe/S4.md`
- [x] S4.d: Nick's KiCad look (PR #12 merged, `9949b37`)
**Demo (Nick):** `tools/check.sh` → `ERC messages: 582  Errors 74  Warnings 508` (S4.d; includes S5.a's load-switch
change), `netcheck: 50/50 … 0 opens, 0 shorts; 0 parts excluded`, midwire 0, exit 0; `python3 tools/ercsum.py` lists
no footprint_link_issues; netlist `PI_5V` = J1.2, J1.4, JP1.1 and `5V_PI` = C56.2, C57.2, C58.1, JP1.2, L6.2, R37.1,
TP38.1; KiCad-Python `tools/fpextract.py … --verify` → 0 problems.
**Result:** S4.a–d each QE-approved and reviewed by Nick; PRs #8, #9, #10, #12 merged (last `9949b37`), 2026-10-05.

### S5 — Pi header wiring, ADIN details, load switch  `[x]` *(J1 part number open: Nick, board spacing)*
*Bites: S5.a load switch, S5.b Pi header wiring, S5.c pull-ups + ADIN power-up order + back-power analysis, S5.d payload connector, S5.g footprint library fixes, S5.f ADIN status LEDs, then **S5.e BOM lifecycle + stock check last, once every part is on the schematic** (Nick, 2026-10-06).*
- [x] **R11 → DNP** (D17): as captured, R11 (0 Ω across U9) is fitted and bypasses the load switch (QE S4.c F4)
- [x] **Replace U9** → U11 TPS26621DRCR (D18; S5.a) (FPF2700MX obsolete: Digi-Key "no longer manufactured", LTB 2023-06-15 per distributor data,
      checked 2026-10-05) with a part **JLC can source** (Nick, D17): 36 V class, ≈ 0.74 A current limit, active-low
      ON, FLAGB/PGOOD; ideally SO-8 pin-compatible; cited, potting-safe; R34/R33/R35 values re-derived; check output-cap /
      hard-short behaviour up to 32 V (FPF2700 Table 2 vs Eq. 2 conflict at 32 V for this limit; C50 is only 100 nF; QE N6)
      — **closed by D18**: TPS26621 needs C_OUT ≥ 0.01 µF, current-limits a start into a short, fast-trips at 1.6 A
- [x] S5.a: QE review (fresh S5 session): **APPROVED WITH NITS** in round 2, nit fixed — `docs/design-review/qe/S5.md`
- [x] S5.a: Nick's KiCad look (PR #11 merged, `10d64d0`)
- [x] S5.e (last in S5): lifecycle + LCSC stock check of all 50 BOM parts for a 20-board build → `docs/design-review/bom_lifecycle.md`.
      29 OK; flagged: D1 SMA6F33A (ST) obsolete (Sofar's second source Vishay SMA6F33A-M3/H), J1 no part number (height
      open), U2/U3 low stock, 6 out of stock, 12 with no LCSC listing found. All flagged parts except J1 are Active at Digi-Key
- [x] S5.e: QE review (standing S5 session): round 1 CHANGES REQUESTED (F1: constraints 7/8), fixed; **APPROVED WITH NITS** in
      round 2, fixed — `docs/design-review/qe/S5.md`
- [x] S5.e: Nick's review of bom_lifecycle.md (PR #18 merged, `f5b2279`)
- [x] Sourcing policy (Nick, D26): critical parts via JLC global sourcing; passives keep the specified part with LCSC
      `ALT…` field proposals for Sofar's design review (S5.h); constraint amendments only after Sofar weighs in
- [x] S5.h: BOM alternates as hidden `ALT1/ALT2 MPN/MFR/LCSC` + `ALT NOTE` + `SOURCING` fields on the 24 flagged passives,
      `SOURCING` on the critical parts (U1–U3, L3/L6, Y1, D1–D3, MP1–MP4, J5, J1); `tools/check.sh` writes the tracked
      `docs/design-review/bom.csv`: Sofar's specified part first (`Value (MPN)`), alternates beside it (Nick). Grouped by
      Value and DNP (R11 kept apart from R12/R13/R17/R19). Values: `docs/design-review/bom_alternates.md`
- [x] S5.h: QE review (standing S5 session): **APPROVED WITH NITS** in round 1, nits fixed; **APPROVED** in round 2 — `docs/design-review/qe/S5.md`
- [x] S5.h: Symbol Fields Table view "Sofar review (alternates)" in the `.kicad_pro`, opened by default; matches `bom.csv` cell for
      cell (Nick's first look: new fields are hidden columns until enabled); QE **APPROVED** in round 3
- [x] S5.h: Nick's KiCad look: fields and values present; KiCad 9 on macOS draws the Symbol Fields Table header row blank with these
      columns shown (its Export has the headers and equals `bom.csv` cell for cell), so `bom.csv` is the review table (PR #20)
- [x] S5.i: **Planned part** fields `PLANNED MPN/MFR/LCSC` + `PLANNED NOTE` (why) on all 106 purchased parts, right after Sofar's
      `Value` in the view "Sofar review (planned parts)" and `bom.csv` (one definition: check.sh exports the preset), so Sofar
      reviews one diff column (D27). Nick: Value stays Sofar's part; first build buys planned parts **after Sofar's review**;
      ALT1/ALT2 stay as backups. 10 lines change (R34, R20/R39, R21 group, C31, C17/C26, C21, C16 group, C19/C27, R14/R18, D1 →
      Vishay second source); R8 stays (ROHM gives no land pattern); J1 TBD; the rest as specified
- [x] S5.i: QE review (standing S5 session): **APPROVED WITH NITS** in round 1, nits fixed — `docs/design-review/qe/S5.md`
- [x] S5.i: merged on Nick's instruction ("if the QE approves, merge"); S5 complete except J1's part number → S6
- [ ] J1 socket part number (height) — when the board spacing is known (Nick)
- [x] S5.b: wire the pin map in DESIGN.md (stub + same-name label per signal pin); reserved (26, 29, 32, 33),
      avoided (8, 10, 27, 28) and all other unused GPIO pins free with no-connect flags (17); Pi 3V3 pins 1/17 stay NC
- [x] S5.c: ADIN_PWR **R43 100 kΩ** pull-down (AP22913 has none, DS41203); ADIN_RST none (internal pull-up,
      ADIN2111 Rev. B); no pull-up on MISO (SPI_CFG0 strap) — D21
- [x] S5.c: ADIN power-up order documented (DESIGN "ADIN power and boot"; Option 1: software, Nick)
- [x] S5.c: R10 removed, TP19 tied to SW_EN (Nick: Pi is the only controller) — D22
- [x] S5.b: SW_EN → pin 36 (**active high** now; R42 pull-down keeps the payload off) and SW_FLAGB → pin 38 (R35
      pull-up, TP35); SW_FLAGB's sheet pin (unconnected since import) now has a stub + label. SW_PGOOD dropped (D18)
- [x] S5.b: QE review (standing S5 session): **APPROVED WITH NITS** in round 1, nits fixed — `docs/design-review/qe/S5.md`
- [x] S5.b: Nick's KiCad look (PR #13 merged, `31bc0f3`)
- [x] S5.d (D23): VBUS_OUT + GND → **J5 JST GH 2-pin** SM02B-GHS-TB (C189893, from the UrchinCam), 1.0 A per contact
      ≥ 890 mA (D12), 50 V; pin 1 VBUS_OUT, pin 2 GND; on the right side of the Top-Level sheet under MP1–MP4 (Nick: interconnects live on the right); Sofar's "Molex 2-pin"
      bus note → "M3 threaded inserts MP1-MP4"
- [x] S5.d: QE review (standing S5 session): **APPROVED WITH NITS** in round 1, fixed — `docs/design-review/qe/S5.md`
- [ ] S5.d: Nick's KiCad look
- [x] S5.g (D24): PoDL insert model (MP1–MP4) visible (opacity 0 → 1); stock 3D models on 7 footprints (C31, C19/C27,
      R15/R16, R1, R8, R22/R34/R40, plus R10's spare), orientation checked (non-polarised, pads and models on x);
      U2/U3 without a model (no stock WLB0909-4); R10's footprint kept (Nick). Insert pads unchanged: contact → Sofar Q6
- [x] S5.g: insert model sits body-up in KiCad's 3D viewer; stock models check out (Nick, 2026-10-06)
- [x] S5.g: QE review (standing S5 session): round 1 CHANGES REQUESTED (F1: the bus contact is a front copper arc) →
      pad change reverted, Sofar Q6 added; **APPROVED WITH NITS** in round 2, nits fixed — `docs/design-review/qe/S5.md`
- [ ] S5.g: Nick's KiCad look
- [x] S5.c (D20): Add I2C pull-ups on I2C1_SDA/SCL to the shield's 3V3 (Nick, 2026-10-05: the Pi
      needs them; also for a bench MCU). Reuse the mote's vetted parts: R26/R27 = 4.7 kΩ ERJ-2RKF4701X, 0402
      (reference Processor sheet). Note the combined value if the Pi also has pull-ups
      (QE: the Pi documents 1.8 kΩ on GPIO2/3 → ≈1.3 kΩ combined; cite a primary source) — cited: Pi Zero 2 W
      reduced schematic R23/R24 1.8 kΩ; ≥ 967 Ω R_P(min) (TI SLVA689)
- [x] S5.c: Choose the pull-up rail and document power sequencing: shield 3V3 and Pi 3V3 are
      separate rails, so one powered while the other is off can back-power through pull-ups /
      IO clamp diodes (applies to the ADIN SPI/control lines too) — QE S2 risk. Cover specifically (QE S5.b): CE0/GPIO8
      (ADIN_NSS) defaults high at Pi reset and SPI0 idles CS high while ADIN_PWR keeps ADIN_VDDIO off; R35 (100 kΩ to
      shield 3V3) feeds GPIO20 when the Pi is off (≈ 33 µA); the Pi's own I²C pull-ups go to Pi 3V3, U4 is on shield 3V3
      — done: shield 3V3; back-power table in DESIGN "ADIN power and boot"
- [x] S5.c: QE review (standing S5 session): **APPROVED** in round 2 (round 1 F1 + nits fixed) — `docs/design-review/qe/S5.md`
- [x] S5.c: Nick's KiCad look (PR #14 merged, `d5bc13b`)
- [x] S5.f (D25): ADIN status LEDs on the ADIN sheet — D8 red KT-0603R (C2286) "ADIN powered", D9 / D10 yellow-green
      KT-0603YG (C2289) port 1 / port 2 link/activity on ADIN pins 21 / 48 (active low, R3 / R5 stay as pull-ups: straps
      unchanged; D10 added at Nick's request); R44/R45/R46 1.5 kΩ (R1's part); one shared bridged cut jumper JP2 from
      ADIN_VDDIO (Nick: option a). Open: visible after potting?
- [x] S5.f: QE review (standing S5 session): round 1 **APPROVED WITH NITS**, nits fixed; round 2 (port-2 LED D10) **APPROVED**
      — `docs/design-review/qe/S5.md`
- [x] S5.f: Nick's KiCad look (PR #17 merged, `e62d974`)
- [ ] Every new net verified from the exported netlist
**Demo (Nick):** net diff lists every new net with exactly its intended pins.
S5.i: `tools/check.sh` → ERC 531 / 27 / 504 (unchanged), netcheck 51/51, midwire 0, exit 0, `BOM: docs/design-review/bom.csv
(54 rows)` with Planned MPN/Mfr/LCSC/note after Value (MPN); 11 rows where Planned ≠ Value (10 changes + J1 TBD).
S5.h: `tools/check.sh` → ERC 531 / 27 / 504 (unchanged), netcheck 51/51, midwire 0, exit 0, `BOM: docs/design-review/bom.csv
(54 rows)`; netlist identical except the new `ALT…`/`SOURCING` fields; `bom.csv` row R8 shows UR73D1JTTD10L0F then the ROHM and
Vishay alternates.
S5.d: `tools/check.sh` → ERC 535 / 27 / 508 (unchanged), netcheck 51/51, midwire 0, exit 0; netlist: VBUS_OUT + J5.1,
GND + J5.2, nothing else.
S5.c: `tools/check.sh` → ERC 535 / 27 / 508 (unchanged), **netcheck 51/51**, midwire 0, exit 0; netlist: R26 on
I2C1_SCL + 3V3, R27 on I2C1_SDA + 3V3, R43 on ADIN_PWR + GND, TP19 on SW_EN, R10 gone, nothing else.
S5.b: `tools/check.sh` → `ERC messages: 535  Errors 27  Warnings 508`, netcheck 50/50, midwire 0, exit 0;
netlist: ADIN_INT/MISO/MOSI/NSS/PWR/RST/SCK, I2C1_SDA/SCL, SW_EN, SW_FLAGB each gain exactly their J1 pin (22/21/19/24/16/18/23, 3/5, 36, 38).

### S6 — Design review package  `[~]`
*Bites (Nick, 2026-10-06; run overnight, each QE-approved and merged before the next): S6.a BOM hygiene, S6.b ERC clean or
justified (title block: name = file name, rev AA, part number PCB-000001-AA), S6.c footprint attributes + courtyards (library
only), S6.d minor schematic tidy (Sofar's design: overlaps, uniform spacing, no overhaul), S6.e review package. Fresh S6 QE session.*
- [x] S6.b ERC clean (D28): **0 errors** / 504 warnings. Title block set (PCBPARTNAME = file name, PCBPARTNUMBER = PCB-000001-AA,
      rev AA); 18 errors excluded with reasons from `docs/design-review/erc_justifications.csv` via `tools/ercexclude.py`
      (`check.sh` fails if an exclusion goes stale). Author: Nick Buemond (set in S6.f)
- [x] S6.b: QE review (S6 session): round 1 CHANGES REQUESTED (tool exited 0 on unjustified errors), fixed; **APPROVED WITH NITS**
      in round 2, nits fixed — `docs/design-review/qe/S6.md`; merged (PR #23)
- [x] S6.d stale note: "Processor + onboard logic runs off 3V3, and ADIN AVDD off 1V8." → "Shield logic runs off 3V3; ADIN
      AVDD runs off 1V8." (the "Molex 2-pin" bus note was updated in S5.d)
- [x] S6.d minor tidy (Nick: small readability fixes on Sofar's design, no overhaul): R26/R27 on J1's I²C stubs; ADIN status
      LEDs D8–D10 at an even 17.78 mm pitch with R3/R5 under D9/D10; ADIN_LED_VDD label off the D9 junction; R4/R6 text off
      pins and labels; "Set for 1Vp-p comms." note no longer overlaps the SWPD note; bus note 3 lines (was wrapping to 5);
      dead 3V3 stub and 7 dangling ADIN lead-ins removed (warnings 504 → 495). Netlist identical. **Not done** (more than
      minor): moving J1 so every interconnect sits on the right of the Top-Level sheet; Sofar's PoDL PHY1_N/PHY2_N wire ends
      (2 dangling-end warnings) left as Sofar drew them
- [x] S6.d: QE review (S6 session): **APPROVED WITH NITS** in round 1 (rendered and checked as minor), nits fixed —
      `docs/design-review/qe/S6.md`; merged (PR #25)
- [x] S6.e Net check: kept nets match the copper (51/51); every new net listed — `netcheck.md` "Schematic nets with new parts"
      (new section in `tools/netcheck.py`, + test)
- [x] S6.e Schematic PDF (all sheets, rev AA): `docs/design-review/schematic.pdf` (reviewed snapshot; check.sh keeps writing `out/`)
- [x] S6.e Change log of every edit: `docs/design-review/changelog.md` (S1–S6)
- [x] S6.e Open questions and proposed values, with datasheet citations: package README (Sofar Q2/Q6/Q7 + the planned parts;
      C56/C57 DC bias and U10 input caps from SPEC; Nick's layout/release items)
- [x] S6.e Pin map, power budget, BOM changes: linked from the package README (DESIGN pin map, `power_budget.md`, `bom.csv` +
      lifecycle + alternates); README notes the Mfr column mixes Sofar's spellings with the lifecycle table's (QE S6.a N1)
- [x] S6.e Stale import data (SPEC open question): the five CRCW1210 0 Ω jumpers R11/R12/R13/R17/R19 had the Description
      "RES SMD 205K OHM 1% 1/2W 1992" → "RES SMD 0 OHM JUMPER 1210"
- [x] S6.e Package index: `docs/design-review/README.md` (status, reading order, open questions, how to regenerate)
- [x] S6.e: QE review (S6 session): **APPROVED WITH NITS** in round 1, fixed — `docs/design-review/qe/S6.md`; merged (PR #26)
- [x] S6.f (Nick, 2026-10-07): title-block author = Nick Buemond (text variable AUTHOR, was the Altium placeholder
      "=ProjectAuthor"); review PDF of the BOM `docs/design-review/bom.pdf` (`tools/bompdf.py`, + `tools/html2pdf.js`);
      `schematic.pdf` re-exported
- [x] S6.f: QE review (S6 session): **APPROVED WITH NITS**, fixed (bompdf test; README: snapshots rebuilt by hand; commands run
      from the repo root) — `docs/design-review/qe/S6.md`; merged (PR #27)
- [x] S6.g (Nick's KiCad review list, 2026-10-07): VBUS_OUT beside the Load Switch; short I²C stubs at the PoDL block; R43 beside
      the ADIN block's HW_EN; J5 beside the Load Switch on the VBUS_OUT wire (Nick: connector with its switch); R11 note as
      an open / fitted summary; headers for J1 and the Load Switch block; cover renders → TBD box + real sheet index; ADIN and Power sheets spread with headers;
      title blocks filled, Altium overlays removed, revision table about this board; active-low overbars + PAYLOAD_EN /
      ~{PAYLOAD_FAULT} names (D30). Connections unchanged. Signal table beside J1: not now (Nick)
- [x] S6.g: QE review (S6 session): **APPROVED WITH NITS** (round 2), nit fixed, **APPROVED** (round 3) —
      `docs/design-review/qe/S6.md`; merged (PR #28)
- [ ] S6: Nick's demo — open `docs/design-review/README.md`, `schematic.pdf`, `bom.pdf` and the project in KiCad; S6 is then complete
- [x] S6.c Footprint attributes (D29): all 43 `Vault` footprints now have a type (`smd`; fiducial `smd exclude_from_bom`; test pad /
      mounting hole `exclude_from_pos_files exclude_from_bom`) and an F.CrtYd courtyard (39 from Sofar's own outlines, 4 computed);
      library only, pads verified (`fpextract --verify` 0 problems). `tools/fpattrs.py`; record `docs/design-review/footprints.md`.
      **Nick (layout):** pcbnew → Tools → Update Footprints from Library to pick them up (its options decide whether text/field
      positions are kept); U2/U3's courtyard is tight (0.05 mm past the body, Sofar's outline)
- [x] S6.c: QE review (S6 session): **APPROVED WITH NITS** in round 1, fixed — `docs/design-review/qe/S6.md`; merged (PR #24)
- [x] S6.a BOM for a JLC order: TP×16, FID1–6, MTG1–4 → `in_bom no` (bare copper / holes; QE S5.h N2); `MANUFACTURER` filled on
      the 75 BOM parts that had none (from `bom_lifecycle.md`; J1 open), Sofar's other maker fields untouched; LCSC field
      harmonisation covered by S5.i's `PLANNED LCSC`. `bom.csv` 54 → 51 rows, Mfr on every row but J1
- [x] S6.a: QE review (S6 session): **APPROVED WITH NITS** in round 1 — `docs/design-review/qe/S6.md`; merged (PR #22)
**Demo (Nick):** open `docs/design-review/` → a complete package, ready to review.
S6.g: `tools/check.sh` → `ERC messages: 494  Errors 0  Warnings 494`, ercexclude 18/0/0/0, midwire 0, netcheck 51/51, exit 0;
same pin partition as S6.f with 7 nets renamed (D30); schematic.pdf shows the new layout.
S6.e: open `docs/design-review/README.md` (status, reading order, open questions) and `schematic.pdf`; `tools/check.sh` →
495/0/495, ercexclude 18/0/0/0, midwire 0, netcheck 51/51 with the new-nets table in `netcheck.md`, exit 0.
S6.d: `tools/check.sh` → `ERC messages: 495  Errors 0  Warnings 495`, ercexclude 18/0/0/0, netcheck 51/51, midwire 0, exit 0;
netlist identical to S6.c; PDF: Top-Level (I²C pull-ups on J1, notes) and ADIN sheet (LED columns).
S6.c: `$PY tools/fpattrs.py nereus_Pi_shield_ADIN2111/mote.pretty` → every line "type kept; courtyard kept"; `$PY tools/fpextract.py
KiCAD_reference_designs/20250409_BM_Mote_000639-AB/BM_Mote_000639-AB.kicad_pcb nereus_Pi_shield_ADIN2111/mote.pretty
docs/design-review/vault_footprints.txt --verify` → 0 problems; `tools/check.sh` unchanged (504/0/504, 51/51).
S6.b: `tools/check.sh` → `ERC messages: 504  Errors 0  Warnings 504`, `ercexclude: 18 errors justified, 0 unjustified, 0 stale / 0
missing exclusions`, netcheck 51/51, midwire 0, exit 0; PDF title blocks read "Rev: AA" and PCB-000001-AA.
S6.a: `tools/check.sh` → ERC 531 / 27 / 504 (unchanged), netcheck 51/51, midwire 0, exit 0, `BOM: … (51 rows)`; no TP/FID/MTG
row; `Mfr` blank only on J1.

### S7 — Layout experiment (agent port of the mote layout)  `[~]`
*Nick, 2026-10-07: see how well a Fable session (high effort) can carry Sofar's proven copper onto the shield, block by
block. Scoped exception to rules 8/9 (D31): the run writes only its own board in `experiments/fable_layout_01/`, on
`experiment/fable-layout-01`, never merged.*
- [x] S7.a Mechanical envelope (Nick, 2026-10-07): 46 × 65 mm (south may grow ≤ 2 mm), Pi Zero portrait (SD north,
      header east, camera south); 40-pin **stacking** header; 4 bus inserts down the west wall (port 2 north, port 1
      south; 2 mm between rings, 2 mm from the edge); PoDL inductor envelopes sized for 50 W (15.5 mm, 2 mm clear); Micro-Fit
      3.0 payload connector on the south edge facing south (experiment only); 4 M3 housing holes + the Pi's 4 M2.5 holes;
      LEDs green/red/green between the insert pairs; bottom parts ≤ 3 mm; copy Sofar's open items as drawn
- [x] S7.a Brief `experiments/fable_layout_01/BRIEF.md` + kickoff prompt `KICKOFF.md` + layer renderer
      `tools/render_layers.py`; Sofar layout questions Q9–Q12 (Q6 reworded); SPEC insert-contact fact corrected
- [x] S7.a: QE review (S7 session): round 1 CHANGES REQUESTED (bus/power widths vs copied copper; plane pullback 3.85 mm;
      notch mapping; renderer net names; D6 vs D31), fixed; round 2 **APPROVED WITH NITS**, nits fixed; round 3 **APPROVED** (plain
      outline, QE agent file D31 exception) — `docs/design-review/qe/S7.md`. Waiting on Nick's read of the brief, then merge
- [ ] S7.b Nick starts the Fable session (KICKOFF.md); review its REPORT.md, renders and draft PR
**Demo (Nick):** read `experiments/fable_layout_01/BRIEF.md`; `$PY experiments/fable_layout_01/tools/render_layers.py
KiCAD_reference_designs/20250409_BM_Mote_000639-AB/BM_Mote_000639-AB.kicad_pcb /tmp/mote_layers` → six SVGs (top, in1–in4,
bot) that match the walkthrough's layer views.

### S8 — First build (20 boards)  `[~]`
*Nick, 2026-10-14 (D32): 20 boards (6 for Sofar, paid on receipt, due at Sofar Mon 11/30; 10 for Nick; 4 scrap); dev units,
no potting. Critical parts bought into JLC parts stock as soon as possible (planned Mon 10/19) so their lead time runs during layout; JLC PCBA order target
Fri 10/30 (fallback Tue 11/3).*
- [x] S8.a Parts buy plan → `docs/design-review/jlc_parts_buy_2026-10.md`: 8 lines ≈ $556 (7 JLC global sourcing; J5 back in
      JLC stock, C189893); quantities, attrition, prices, stock and lead times read 2026-10-15; steps for Nick. Global
      sourcing (9–20 business days) is the critical path: parts at JLC 10/30–11/16 if paid Mon 10/19 (China time; re-anchored 10/17, was 10/16); a 10/30 PCBA
      order arrives ≈ 11/13–11/18; the PCBA order also waits on Sofar's review of the planned passives (D27)
- [x] S8.a: QE review (fresh S8 session): **APPROVED WITH NITS** in round 1 (4 minor, 6 nits), fixed; round 2 **APPROVED WITH NITS** (3 wording nits), fixed —
      `docs/design-review/qe/S8.md`
- [x] S8.a: Nick's review; PR #32 merged 2026-10-17 (`56e1e1a`)
- [x] S8.a: Nick bought the parts (2026-10-18 14:24 PT, Mon 10/19 in China): JLC global-sourcing order DOB202610190524705,
      all 7 lines from Digi-Key, $956.05 (U1 at JLC's $27.76); **ready for assembly est. 2026-11-05** → PCBA order ≈ 11/5,
      boards ≈ 11/19–11/24+. J5 not pre-bought: picked from JLC stock (31,805 on 10/18) at the PCBA order (Nick). Record in the doc
- [ ] Flagged passives (R8, R15/R16, C22/C23, commodity R/C) bought after Sofar's review (D27)
- [ ] JLC PCBA order (target Fri 10/30, fallback Tue 11/3; parts ready est. Thu 11/5, so ≈ 11/5; no J5 part since D34: wire pads on the S9 board)
- [ ] J5 `SOURCING` field (QE S8 N10): on the S9 board J5 is wire pads with no part (D34); the live project's schematic and `bom.csv` still list the JST part
**Demo (Nick):** open `docs/design-review/jlc_parts_buy_2026-10.md`: the "In short" box, the buy table and the steps;
`git diff main...HEAD --stat` touches only docs and the viewer (no KiCad file).

### S9 — Finish the routing on `nick_raw_routing` for JLC  `[~]`
*Nick, 2026-11-10: finish the board in `experiments/nick_raw_routing/` and get it through JLC's checks. Base: the board in
`nereus_step2_power_2026-11-09.zip` (= `reload_old_mote` 3d596b9 + the earlier session's steps 1–2). Nick's go on the plan
is the approval for an agent to edit this board (rules 8/9, D33). Plan page: https://claude.ai/artifact/WW6S2MLhrNHYLe7zbg5Wsc.
Branch: `Fable_5.2` (Nick, 2026-11-10; pushed only on his approval). Since 2026-11-11 (after step 16) the work continues on
`claude/fable-5-2-continue-55a515`, cut from `Fable_5.2` at 5180c47, because the app could not share the old worktree (Nick,
previous session's chat, 2026-11-11: "Yes, new branch"); its commits return to `Fable_5.2` by fast-forward later, on Nick's word.
Edits are scripted (`experiments/nick_raw_routing/scripts/`); after each step: refill, DRC with parity, render, one commit.*
- [x] Review + plan with drawings; Nick: A base = zip, B inserts option 1, C part moves approved (2026-11-10)
- [x] Step 0, fixes before routing, no copper changed (58365af): outline circles off Edge.Cuts; MP1↔MP2, MP3↔MP4; MTG1–4
      removed; J5, TP38 on the board; GND strip priority. DRC 424 → 324 errors, open 77 → 63 (46 → 41 nets), parity 0; ERC unchanged (39)
- [x] Decision D (Nick, 2026-11-10; D34): JLC rule values + standard stackup JLC06161H-3313, in one revertible commit (6f54c27;
      `docs/design-review/jlc_rules_2026-11.md`); data pairs and the 16 GND vias kept as on the mote; Sofar Q13 + note on the PoDL sheet (f9fe3b7)
- [x] Step 0b, no copper changed (cf6ec47): J5 → two through-hole wire pads (new footprint, not in BOM); J6 one pitch west and
      FID1/FID3 as on Nick's `reload_old_mote`; TP38 re-placed. DRC under JLC rules: 134 errors, 63 open (41 nets), parity 0; ERC unchanged (39)
- [ ] Nick: confirm J5's pad size (4.2 × 2.6 mm), hole (1.3 mm) and pitch (3.81 mm) in KiCad
- [x] Step 1 ADIN SPI (a0e6640): SCK + CS on Internal 2, MOSI + MISO on Internal 1, J1 pin → Sofar's via, no new via;
      the PI_3V3 branch on Internal 2 that crossed them is removed (back in step 4); MOSI's via removed (nothing left to join).
      DRC 134 errors (none on the new copper), open 63 → 60 (38 nets), parity 0
- [x] Nick's requests of 2026-11-10, done as step 1b (see the next item):
      (a) copper keep-out on every layer around H1–H4, so a screw head or thread cannot short to a plane;
      (b) LEDs D8–D10 on the board's centreline (x 148.80), evenly spaced, one line 3–4 mm from the south edge (now x 146.69 / 149.72 / 152.40, y ≈ 126.9, 5.2 mm from the edge);
      (c) inserts on one line, each pair the same distance from its edge, mirrored (now x 129.51 / 139.10 / 160.10 / 169.70, y 127.40–127.56; 13.21 mm from the west edge, 11.60 mm from the east);
      (d) J4 as the same two wire pads as J5, no connector
- [x] Step 1b: inserts at x 128.70 / 138.30 / 159.30 / 168.90, y 127.45 (12.40 mm from each edge, mirrored), rings concentric,
      trunk ends follow; LEDs at x 145.80 / 148.80 / 151.80, y 128.60 (3.5 mm from the south edge); J4 → wire pads at (119.0, 92.1);
      copper keep-out r 3.0 mm on all layers at H1–H4 (radius from `Pi_HAT_outline.dxf`, layer HOLE_KEEPOUT).
      DRC 151 errors (17 more, all at the insert footprint), 60 open, parity 0; ERC 39
- [x] Insert footprint + step 3 bus pairs: the insert's unplated hole is a plain hole again (the import had left a net-less 5.5 mm
      copper disc on the bottom and size 0 inside); two scoped rules for the insert hole; trunk ends pulled back to 3.45 mm from
      the insert centre; BM2_P's vertical run off Sofar's GND via; fiducials 0.2 mm west. DRC 151 → 25 errors, open 47, parity 0
- [x] Step 2 ADIN control + straps: INT on top, RST and ADIN_PWR on the bottom to Sofar's stub and vias; CFG0 strap (JP4, R9) at the
      SPI landing; CFG1 strap (JP3, R2, R47) south of U1, because R2's strap pad could not be reached under U1; ADIN_TIMER 77 mm on
      the bottom along the south and east edges. DRC 151 errors (none on the new copper), open 60 → 47 (30 nets), parity 0
- [x] Nick's KiCad look after steps 0–2 (2026-11-10, 3D view; no changes asked)
- [x] Step 4 power: GND zone fills the north-west notch of Sofar's GND plane (5 V converter, J4, J3); J4 → F1; TP38; U11_RTN;
      PI_3V3 pins joined, J2 pins 9/11/13 from a new PI_3V3 zone on the PWR plane; VBUS_OUT → J5 (1.0 mm, top then bottom);
      J5 GND to two vias. DRC 25 errors (none new), open 47 → 36 (26 nets), parity 0
- [ ] Nick's KiCad look after steps 3–4: the bus trunks at the inserts, the new GND and PI_3V3 zones, VBUS_OUT down the west edge
- [x] Step 7 Pi → J2 breakout, all 11 nets (aa8cd65, bcfe41f): channel re-laned (INT, ADIN_PWR, RST to the north lanes), TP38 to the
      bottom side; UART_TX, ADC_ALERT on Internal 1; UART_RX, SPI1_CE1, MOTOR_nSLEEP/IN1/IN2 on top; SPI1_CE0 on the bottom;
      SPI1_MISO/MOSI/SCLK on Internal 2. No via
- [x] Step 5, I2C0 (bcfe41f): one small via per stub, SCL on Internal 1, SDA on Internal 2, to J1 27/28 and J2 15/16; R26/R27 moved
      below J2 beside PI_3V3 pin 13 (clears the 3V3 / PI_3V3 short). DRC 22 errors, open 19 on 12 nets, parity 0
- [x] Mock-up of the last 19 connections on the plan page; Nick: "routing approved" (2026-11-10)
- [x] Step 5b, I2C3 (53ff783): SCL on top, SDA on the bottom from J1 13/15 to J2 8/7; on the bottom below J2 and J6 to two vias,
      then Internal 1 past the 5 V converter to two vias beside J3; R10/R24 on the bottom side beside J3. Mote leftovers removed
      (old I2C3 copper, the PI_3V3 trunk to the old pull-up place). Two changes from the mock-up: the converter's 5V_PI and
      VBUS tracks wall off the bottom layer, hence Internal 1 and two more vias; R10 on the bottom, not the top (its
      courtyard overlapped J3's). Open 19 → 13
- [x] Step 6, payload switch (1688971): PAYLOAD_EN (J1.37) and ~PAYLOAD_FAULT (J1.31) on Internal 1 down a J2 pin gap, one via each,
      west on the bottom (y 97.50 / 93.40) to Sofar's vias at U11 (FAULT's last 12 mm on Internal 2); PAYLOAD_EN on to TP19 on
      Internal 2 with a via beside the pad. A dead 3V3 stub and its via removed. Open 13 → 10
- [x] Step 8, LEDs (0772b8a): JP2 at (148.60, 124.30) above the LEDs; ADIN_LED_VDD through one via to R44–R46 on the bottom; the two
      link-LED lines on Internal 2 from Sofar's vias at U1; one via per anode; D8's GND pad to JP3 pad 3 on top (no GND plane
      south of y 123). Open 10 → 0
- [x] Board fully routed: 0 open connections, parity 0, ERC 39 (unchanged); DRC 22 errors, all carried: 16 GND vias in U1's
      keepout (as on the mote), 3 skew (Sofar Q13), 3 courtyards (C54/C55/U10)
- [ ] `sofar_brief.md` has no row for the Qwiic connector J3 and the I2C3 pull-ups R10/R24 (schematic additions on this board)
- [x] Bottom silkscreen "PCBA-000639-AB BM Mote" (Sofar's board name): replaced by "Pi Shield / ADIN2111 Rev0" (Nick, step 9g)
- [ ] Nick's KiCad look after steps 5–8: I2C3 past the 5 V converter, R10/R24 under J3, the payload lines below J2, JP2 and the LEDs
- [x] Step 9a (f4faaca): dead mote copper removed, 58 segments / 46.8 mm that ended in the open (found by repeated DRC on a scratch copy)
- [x] Step 9b (c9db5f8): the 3 courtyard overlaps at the 5 V converter cleared (C55 0.50 mm west, C54 0.30 mm south, their GND via moved)
- [x] Step 9c (e1eedf3), Nick's request of 2026-11-10: silkscreen names on the straps (JP1 5V-PI, JP2 LED, JP3 CFG1, JP4 CFG0 with
      1 / 0 ends), the wire pads (J4 5V IN, J5 PAYLOAD), J6 (PI 5V, rows 5V / GND), J3 (I2C3), every J2 pin, the inserts (BM1 / BM2,
      both sides) and the LEDs (P1 / PWR / P2); reference texts moved off other parts; refs of F1, D8–D10, H1–H4, MP1–MP4 hidden
- [x] Step 9d (ab8baae): DRC exclusions with comments for the 16 GND vias in Sofar's keepout under U1 (kept, D34)
- [x] State after 9a–9d: DRC 3 errors not excluded (skew on Sofar's BM data pairs, Sofar Q13), 16 excluded, 0 open, parity 0, ERC 39.
      Draft fab files export cleanly (13 gerbers, 2 drill files, positions; `~/NereusData/nereus_Pi_shield_ADIN2111/step9_2026-11-10/fab_draft/`)
- [x] Step 9e (88e55ae), Nick's request: JP3 (CFG1) to the north-east corner at (168.60, 96.40), in one row with JP4 and with the
      same order (0 west, 1 east); CFG1_STRAP 61 mm on Internal 1 from R2 along the south and east edges; R2 and R47 stay at U1
- [x] Step 9f (779c331), Nick's request: R26 / R27 to the bottom side, 4 mm south of J2's pads, fed from J2 pins 13 / 15 / 16
- [x] Step 9g (488cfbd), Nick's request: board name "Pi Shield / ADIN2111 Rev0" with the Bristlemouth logo in the north-east
      corner (top) and the name on the bottom in place of Sofar's part number and "BM Mote"
- [x] State after 9e–9g: DRC 3 errors not excluded (skew), 16 excluded, 0 open, parity 0, ERC 39
- [x] Step 9h (0bd5d89), Nick approved mock round 2 on 2026-11-11 ("Yes, build it"): silkscreen style (DESIGN D39). Menlo Bold
      (slashed zero); function names large with the designator small under them; J4 "+5V / AUX OUT / GND" and J5 "VBUS OUT" boxed
      on both sides; all 128 designators 0.8 mm (six turned 90°: C10 C30 C31 D1 D8 L3; F1 stays hidden); board name and logo in the
      east strip beside L1, turned 90°; bottom: ratings under J2, screw sizes (inserts M3, mounting holes M2.5) and the USB warning
- [x] State after 9h: no copper change (tracks, vias, zones, pads and footprint positions identical to e686111); DRC 3 errors not
      excluded (skew), 16 excluded, 0 open, parity 0, ERC 39 (`~/NereusData/nereus_Pi_shield_ADIN2111/step9_2026-11-11/`)
- [x] Step 10 (7c30e8f), Nick approved the mock on 2026-11-11 ("Yes, build it"): D9 / R45 swap places with D10 / R46, so the east
      LED (by BM1) shows port 1 and the west LED (by BM2) port 2; PWR stays in the middle; names P1 / P2 follow (DESIGN D40).
      Only the four LED nets change. DRC 3 errors not excluded (skew), 16 excluded, 0 open, parity 0, warnings unchanged; ERC 39
- [x] Step 11 (6874391), Nick 2026-11-11 ("rotate JP2 clockwise, then add a silk screen label above D8 to say ADIN ... After that
      change push"): JP2 lies east-west at (149.00, 124.00); "ADIN" stands above D8, which shows the ADIN's power, not the
      board's (DESIGN D41). 5 top segments of ADIN_VDDIO / ADIN_LED_VDD re-laid. DRC and ERC counts unchanged, 0 open, parity 0
- [x] Step 12 (3054b8c), Nick 2026-11-11 ("Yes build it, but say Bold Box instead of Heavy Box", "remove the Pi Shield name on
      the bottom"): the schematic's table "ADIN2111 SPI CFG Straps" stands on the bottom as a ruled table in the east strip
      (CFG 1 | CFG 0 | SPI MODE, bold frame on the as-built row 1 / 0 = generic SPI with CRC); screw sizes and the USB warning
      moved behind JP1; "Pi Shield / ADIN2111 Rev0" removed from the bottom, Sofar's frame around it left empty (DESIGN D42).
      No copper or footprint change. DRC silkscreen overlaps 25 → 24, all else unchanged; 0 open, parity 0, ERC 39
- [x] Step 12b (0a885e9), Nick 2026-11-11 (comment on the summary doc: 'Please try to fit "Threaded Inserts" and "Mounting Holes" if
      you can'): the bottom reads "THREADED INSERTS M3" / "MOUNTING HOLES M2.5" on two lines above the USB warning. Silkscreen
      only; DRC and ERC counts unchanged, 0 open, parity 0
- [x] Step 12c (242e46c), Nick 2026-11-11 (comment on the summary doc: "change P1 and P2 to BM1 and BM2 so they match the silk
      screen above the threaded inserts"): the port LEDs read BM2 (D10, west) / PWR / BM1 (D9, east). Silkscreen only; DRC and
      ERC counts unchanged, 0 open, parity 0
- [x] Step 13 (0595d79), Nick 2026-11-11 (comment on the mock picture in the summary doc: "I approve the mock"): Qwiic connector J3 on
      the centre line (y 104.10, 0.70 mm further west), J4 2.15 mm south with "AUX OUT" above its pads and a box like VBUS OUT's
      (DESIGN D43). VBUS_OUT's bottom track turns at (122.30, 99.60); J3's four top tracks re-laid; its GND via now at
      (122.80, 101.40). 9 segments and 1 via out, 19 segments and 1 via in. DRC and ERC counts unchanged, 0 open, parity 0.
      Smallest J3 copper to BM2_N 1.02 mm (was 2.37 mm), measured on the board
- [x] Step 14 (a41524d), Nick 2026-11-11 (comment on the proposal in the summary doc: "Proposal approved"): the zone "GND north-west
      fill" is redrawn 0.5 mm clear of Sofar's west ground wing and slot (review finding R-S4, DESIGN D44). Sofar's zone is
      untouched; its copper refills the wing, which joins the main ground only at the slot's south end again, as on the mote.
      No part, track or via change. DRC and ERC counts unchanged, 0 open, parity 0
- [x] Step 15 (d6a4fb8), Nick 2026-11-11 (comment in the summary doc: "lets put back the sofar footprint"): R15 and R16 carry
      `Vault:CRCW08057R50FKEAHP-Footprint-1` again, on the board and in the PoDL sheet's two Footprint fields (review finding
      M-S5, DESIGN D45). Pads sit exactly where the mote's do; no track or via change. DRC and ERC counts unchanged, 0 open,
      parity 0
- [x] Step 16 (b0115b9), Nick 2026-11-11 (comment on the proposal in the summary doc: "approved"): J6's GND pads 2 / 4 / 6 set to
      thermal relief on the pad (review finding M-S6, DESIGN D45); each pin stands in a ring with four spokes on the GND plane.
      No part, track or via change. DRC and ERC counts unchanged, 0 open, parity 0
- [x] Step 17, Nick 2026-11-11 (comment on the summary doc: "Remove it"): Sofar's empty name frame is off the bottom silkscreen
      (five lines, DESIGN D46). Silkscreen only. DRC against a clean-checkout baseline: counts unchanged (3 skew errors, 16
      excluded), 0 open, parity 0, ERC 39 (`~/NereusData/nereus_Pi_shield_ADIN2111/steps_2026-11-11/drc_17.json`, `erc_17.json`)
- [x] Step 18 (c445bff), Nick 2026-11-11 (comment on the mock in the summary doc: "approved"): top-layer GND fill at U10 (12.2 mm²,
      as Sofar has at U5) and two more GND vias at (132.70, 90.10) and (133.14, 87.75); pin 1 reaches the GND plane through five
      vias (review finding R-S1, DESIGN D47). No part or track moves. DRC counts unchanged, 0 open, parity 0, ERC 39
- [x] Step 19 (ae8380d), Nick 2026-11-11 (comment on the mock: "Approved, but instead of [fingers] how [about] a polygon like Sofar
      did under [the] large L1 L2 inductors?"): the three vias at L6 sit under the inductor at (124.60 / 126.40 / 128.20, 87.15),
      joined to pad 2 by a top-layer 5V_PI polygon in Sofar's style, and land on a new 5V_PI fill on the PWR Plane, 57.2 mm²
      (review finding M-S4, DESIGN D47). DRC: via_dangling 7 → 4, nothing new; 0 open, parity 0, ERC 39
      (`~/NereusData/nereus_Pi_shield_ADIN2111/steps_2026-11-11/drc_19.json`, `erc_19.json`, `after_steps18_19_converter.png`)
- [ ] R47 = 1 kΩ (Nick, this session's chat, 2026-11-11: "Ok, so the 1kOHM it is based on your suggestion"). Value and PART NUMBER
      already say RC0402FR-071KL; the PLANNED MPN / LCSC fields still name the 1.5 kΩ part and are corrected in the BOM session
      (the LCSC number of the 1 kΩ part is not looked up yet). Software rule that goes with it: GPIO16 stays an input while the
      ADIN leaves reset, unless the Pi means to override CFG1
- [x] Found 2026-11-11: port LEDs sat on the far side from their ports. D9 (west, by BM2) is on ~ADIN_P1_LED1 and port 1 is BM1 (east);
      D10 (east, by BM1) is on ~ADIN_P2_LED1 and port 2 is BM2 (west). The names P1 / P2 match the nets. Nick wants each LED
      beside its own port with PWR in the middle: swap D9 / R45 with D10 / R46 and re-route the two LED lines (mock first).
      Mock made 2026-11-11 on a scratch copy: 0 open, parity 0, no new DRC error (`~/NereusData/nereus_Pi_shield_ADIN2111/led_swap_mock_2026-11-11/`)
- [x] Nick 2026-11-11: the schematic's table "ADIN2111 SPI CFG Straps" should go on the board bottom if possible. Two mocks (text
      lines, then a ruled table); built as step 12. Summary of changes and findings for Nick's comments:
      https://claude.ai/artifact/Jy3PvmmmkEJk8qQLjoTvq2
- [x] Nick 2026-11-11 (built as step 13): Qwiic connector J3 on the board's centre line, moved south so that AUX OUT's name fits above J4's pads as on
      VBUS OUT. Mock on a scratch copy, not on the board (`scripts/step13_qwiic_centre_aux_label.py`; pictures and DRC report in
      `~/NereusData/nereus_Pi_shield_ADIN2111/qwiic_mock_2026-11-11/`): J4 2.15 mm south (F1 sits right above it), J3 2.50 mm south
      to y 104.10 and 0.70 mm west, VBUS_OUT's bottom track turned earlier to clear J4's GND pad, J3's four top tracks re-laid,
      its GND via moved to (122.80, 101.40). DRC counts as after step 12, 0 open, parity 0. Smallest J3 copper to BM2_N:
      2.37 mm before, 1.02 mm in the mock (the SCL track; measured on both boards)
- [x] Review finding R-S4 (built as step 14), Nick 2026-11-11 (comment on the summary doc): "Please show me the mock of this". Checked on the board and
      on a refilled scratch copy of the mote (same coordinates): Sofar's GND zone has a 0.38 mm slot (x 131.31–131.69 from y 93.4
      to 101.6, then east along y 101.81–102.2 to x 138.4, then south to y ≈ 113.6) that leaves the wing under L2 joined to the main
      ground only at the south; the zone "GND north-west fill" (prio 2) covers the wing's north tip and the slot's north end.
      Mock on a scratch copy, not on the board (`~/NereusData/nereus_Pi_shield_ADIN2111/rs4_mock_2026-11-11/`, `mock_rs4.py`):
      fill outline redrawn 0.5 mm outside the wing and slot: (116.80, 87.50) (132.90, 87.50) (132.90, 92.89) (131.10, 92.89)
      (128.10, 95.89) (128.10, 97.65) (124.50, 101.25) (124.50, 102.45) (124.10, 103.20) (116.80, 103.20). Sofar's copper refills
      the wing; DRC counts unchanged, 0 open, parity 0. Why Sofar cut the slot stays open (Q10)
- [ ] Nick's answers of 2026-11-11 to the seven open items (comments on the summary doc, read in the threads):
      · J2 pin 22: "Tie it to GND"; ADIN_TIMER stays on the Pi header only. To build (schematic and board)
      · Fiducials: "approved make it happen" (1 mm dots, 2 mm openings, the two near the edge moved inboard). To build
      · Sofar's empty name frame on the bottom: "Remove it". Built as step 17
      · U10 input capacitor: "Leave as the mote has it". Closed, no change; Sofar question stays
      · JP1 end marks: "Leave them off". Closed, no change
      · R47: Nick meant 1.5 kΩ as a way for the Pi to override the CFG1 strap at boot; by divider arithmetic 1.5 kΩ puts pin 19
        at 0.80 V against V_IL 0.8 V (SPEC), 1 kΩ at 0.58 V. Recommended 1 kΩ; Nick picked 1 kΩ (see the R47 item)
      · The three vias at L6: "Make them useful like the mote". Mocked on a 5V_PI fill on the PWR Plane
        (`~/NereusData/nereus_Pi_shield_ADIN2111/ms4_mock_2026-11-11/`); L6 makes 26 mW at 1 A, so the gain is small. Built as step 19
      · R-S1: "show me a mock". Mocked: top GND fill at U10 and two GND vias (`rs1_mock_2026-11-11/`). Built as step 18
- [ ] Found 2026-11-11: a clean checkout shows 2 DRC warnings more than `drc_16.json` (`nonmirrored_text_on_back_layer`, the "*"
      texts of U5 and U10 on B.Fab, Sofar's footprint); the old worktree's local `.kicad_prl` hid that layer. No effect on
      fabrication. Baseline for comparisons from here on: `ms4_mock_2026-11-11/drc_base.json`
- [ ] Still open with Nick after steps 12–16 (list kept in the summary doc, section "Still open"; answered 2026-11-11, see the item above): J2 pin 22 once ADIN_TIMER leaves
      it (unconnected or GND), R47's value, the U10 input capacitor, the three vias at L6 together with R-S1, fiducials, Sofar's
      empty frame on the bottom, JP1 end marks. Not done: datasheet check of three strap rows; Sofar brief and DESIGN.md pin map
      behind the board (routing review N12, not gone through by the design session); nothing since c0edb77 pushed; no PR; no QE
- [ ] Open items after Nick's second batch of doc comments, 2026-11-11 (all answered in the summary doc; pictures and mocks in
      `~/NereusData/nereus_Pi_shield_ADIN2111/`; nothing built, Nick decides each):
      · ADIN_TIMER off J2 (Nick: "should only go to the primary Pi Header"): today on J1 pin 36 (GPIO16), J2 pin 22 and R47; the
        track runs through J2 pin 22's pad. Needs a schematic change, about 3 mm of track re-laid, "TM" removed on both sides.
        Open: J2 pin 22 unconnected or GND
      · R47 value: Value / PART NUMBER say RC0402FR-071KL (1 kΩ), PLANNED MPN says RC0402FR-071K5L (1.5 kΩ, C11702). Nick picks
      · R-S5 input capacitor at U10: U10 has the same input capacitors as U5 on shield and mote (UMK107BBJ225KA-T 2.2 µF,
        GRM188R72A104KA35D 0.1 µF). Options: leave, add, or add an unfitted footprint
      · R-S6, decided by Nick 2026-11-11: leave as is, see the design review doc item (`rs6_2026-11-11/`): the 0.2 mm link (4.25 mm) joins L1 pad 3 to the via at (165.88, 107.95), which feeds only T1 pad 6
        over a 0.2 mm Internal 2 track that the mote has too; the bus trunk is 2 mm on both boards. Rated low by the design session
      · M-S4 (`ms4_2026-11-11/`): the three 5V_PI vias at L6 meet 5V_PI copper on the top layer only (the mote's vias at L3 land on
        a 3V3 fill on the PWR plane) and overlap L6 pad 2's edge by about 0.25 mm. Delete, or give them a fill; settle with R-S1
      · M-S5, built as step 15 (`ms5_2026-11-11/`): R15 / R16, same part; mote pads 0.85 × 1.35 mm at pitch 1.65, shield (KiCad R_0805_2012Metric)
        1.02 × 1.40 mm at pitch 1.83; gap 0.80 mm on both. Put Sofar's footprint back, or note it in the Sofar brief
      · M-S6, built as step 16 (`ms6_mock_2026-11-11/`, `mock_ms6.py`): mock with J6 pads 2 / 4 / 6 set to thermal relief on the pad; today they are
        solid in Sofar's GND zone on three sides. DRC counts unchanged, 0 open, parity 0
      · Fiducials: FID1–FID6 are 0.75 mm dots in 2.25 mm openings at (117.90, 83.60), (123.70, 128.60), (178.70, 122.00), top and
        bottom; 1.6 / 3.5 / 2.6 mm from the board edge. JLC's help page (updated 2026-09-09) asks for 1 mm dots, 2 mm openings,
        3 to 4 along the edges, 3.35 mm from the edge, and edge rails of 5 mm for standard assembly:
        https://jlcpcb.com/help/article/how-to-add-edge-rails-fiducials-for-pcb-assembly-order . Proposal: 1 mm dots, moved inboard
- [ ] Reviews of e686111, 2026-11-11 (read-only agents), reports in `~/NereusData/nereus_Pi_shield_ADIN2111/review_2026-11-11/`:
      `dfm_review.md` (1 blocker: the draft export is stale; 6 should fix) and `routing_review.md` (0 blockers; 6 should fix).
      Spot-checked on the board by the design session: the three unused 5V_PI vias at L6 (127.90 / 128.46 / 128.99, 84.2); BM1_P
      from T1 to L1 on 0.2 mm tracks; no top-side GND zone at U10; R47 value 1 kΩ against planned part 1.5 kΩ; JP3 bridged to
      ADIN_VDDIO (CFG1 = 1; the mote had 0). The other findings are not yet checked. Nick decides which to fix before Sofar's review
- [x] Nick confirmed 2026-11-11 (his comment on the summary doc): "The as built is correct, Sofar found issues getting the ADIN2111
      to work with Open Alliance + CRC ... so we want to keep Generic with CRC". CFG1 = 1, CFG0 = 0 stays (review finding R-S2
      closed, no board change). His schematic table has no row named "OPEN Alliance + CRC"; its OPEN Alliance rows are
      "+ protection" (0 / 0, the mote's setting) and "no protection" (0 / 1)
- [ ] Nick: the four strap modes on the bottom silkscreen (step 12) are copied from the schematic's table. Only 0 / 0 = OPEN
      Alliance SPI with protection is checked against the datasheet (SPEC, Table 22); the datasheet could not be fetched on
      2026-11-10 to check the other three. Check them before the board is ordered
- [x] Nick accepted 2026-11-11 (his comment on the summary doc, row "Text stroke weight", 199 warnings): "accept, lets see if JLC
      pushes back once I submit designs". The stroke-weight warnings stay
- [x] Nick approved 2026-11-11 (his comment on the summary doc, row "Text height": "approve, see if JLC pushes back once we submit
      designs"): the designators stay 0.8 mm high. What was asked: silkscreen text size after 9h. The 128 designators are 0.8 mm high (JLC rule set: 1.0 mm; Sofar's were 0.6 / 0.64 mm).
      KiCad flags 199 texts for TrueType stroke weight under 0.15 mm (thin details such as the zero's slash; main strokes measure
      about 0.15 mm on the render at designator size). Accept, or go to 1.0 mm designators (they fit, more of them far from their part)
- [x] Nick decided 2026-11-11 (his comment on the summary doc, on "3 not excluded (skew on Sofar's data pairs)"): the 3 skew
      errors stay as they are, not excluded, "pending Sofar confirmation and agreement" (Q13)
- [ ] Design review doc, when Nick asks for it ("Once the changes are done, I'll ask your help to put together a design review
      doc"): the 3 skew errors are its first item, with the proposal to keep them as is pending Sofar. Also in it (Nick's comment
      on R-S6, 2026-11-11: "call this out in the design doc, with the suggestion that we approve as is pending Sofar's check"):
      the 0.2 mm, 4.25 mm link from L1 pad 3 to the via that feeds T1, where the mote had wide copper
- [ ] Left in DRC as warnings: 24 silkscreen overlaps (25 before step 12) and 8 silkscreen-on-copper after 9h (mostly Sofar's part outlines), 7 vias that join
      one layer only (3 on 5V_PI at L6, 1 on U11_RTN, 3 GND), 3 no-net fills of Sofar's, 106 footprint-vs-library and 34 pad-stack notes
- [x] Nick 2026-11-11 (his comment on the summary doc, row "Footprint differs from library", 106 warnings): "If there is no impact on
      manufacturing or assembly then ignore the warning". Ignored: gerbers come from the board's own footprint copies. Checked the
      same day with `kicad-cli pcb export pos` and pcbnew: 105 of 143 footprints have no SMD / through-hole attribute; the export
      lists 139 footprints (all but the 4 flagged no-pos), among them 30 no-BOM ones (H1–H4, FID1–FID6, JP1–JP4, 16 test points)
      and the unfitted R11
- [ ] Final silkscreen pass, the last task before the design freeze; the BOM clean-up follows it. Nick 2026-11-11 (comment on the
      summary doc, row "Silkscreen overlap"): "lets review this as the final task before freezing the design and moving to the BOM
      clean up ... adjust the silkscreen so that they do not overlap and it's clean what they belong to ... knowing the label of
      each part is important for future debug". Scope: every designator clear of outlines and other text and plainly beside its
      own part, both sides, shown to Nick in pictures. Start point (DRC after step 12c): 24 overlap warnings = 9 designators
      0.10–0.13 mm from a part outline (C21, D8, U2 ×2, C24, C25, C26, R24, R11), 7 of Sofar's outlines touching each other,
      4 box or board lines on a part outline, 2 "VBUS OUT" texts 0.14 mm from their box, 2 pin-1 marks (U1, U4) on their outline
      Also in this pass (Nick, same day, row "Silkscreen over copper": "Same as above, lets review this as last step before design
      freeze"): the 8 silkscreen-on-copper warnings = pin-1 marks of U1, U5, U10; outline segments of R34 (2) and C59; the two
      "-" marks at the BM2 inserts (top and bottom)
- [x] Nick 2026-11-11 (comment on the summary doc, row "Isolated copper", 3 warnings, proposal "Leave"): "agree, so long as no issue
      with assembly". Read from the board: zones `NoConnect_Left` (68.8 mm²) and `NoConnect_Right` (46.9 mm²) on the inner PWR
      plane; one no-net zone on the top layer under L3, filled as two patches (1.76 and 0.70 mm²), no mask opening on or within
      0.5 mm of them, 0.28 mm from L3 pad 1 (box to box). No exposed copper, so left as they are
- [x] Nick asked 2026-11-11 (comment on the summary doc) what the 34 pad-stack warnings are. Read from the board: Sofar's library
      footprints (library `Vault`), not layout. 16 test points and 6 fiducials: pad paste margin −2 mm, so no paste (wanted). U6
      (TPS62840YBGR, 6 pads, 12 warnings): pad mask and paste margins −1000 mm, replaced by shapes drawn in the footprint (six
      0.33 mm mask circles, six 0.25 mm paste polygons). Nothing to change
- [ ] Order of work to the JLC order (Nick's comments on the summary doc, 2026-11-11; nothing more changes on the board until Nick
      and the design session have talked through the open items, his chat message of the same day):
      1. the remaining layout and schematic changes; 2. the final silkscreen pass; 3. layout freeze; 4. schematics and BOM documents
      brought up to date ("we need to freeze the layout and update all BOM docs and schematics first"); the BOM clean-up runs in
      its own Fable 5.2 session that Nick starts ("a solo Fable 5.2 session just for BOM review and updates + fixes"), which
      cross-references Sofar's suggested alternative parts first, then JLC stock ("we are out of time for global sourcing"),
      before any generic JLC part is specified; 5. export in JLC's form from the frozen board, never from the draft folder
- [ ] Final fab outputs (gerbers, drill, BOM, CPL) → QE review → Nick's KiCad look. Check U6's mask openings and paste dots in the
      gerbers. CPL: filter the placement export against the
      BOM (see the item above) and never use the "SMD only" option, which would drop the footprints without an attribute
**Demo (Nick):** `kicad-cli pcb drc --refill-zones --schematic-parity --severity-all experiments/nick_raw_routing/nick_raw_routing.kicad_pcb`
→ after step 7 and I2C0 (JLC rules): 22 errors, 19 unconnected items, 0 parity issues.

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
