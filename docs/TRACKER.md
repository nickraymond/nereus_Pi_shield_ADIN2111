# TRACKER.md — Sprint Ladder & Rules

*The agent entry point and the single source of truth for progress.*
*Last updated: 2026-10-06 · Owner/gate: **Nick***

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
`python3 tools/test_netcheck.py` and `python3 tools/test_midwire.py`, `python3 tools/test_schedit.py`, `python3 tools/test_ercsum.py` and `python3 tools/test_fpextract.py`. ERC tables: `python3 tools/ercsum.py --items`.

### Project layout

```
docs/                         SPEC TRACKER DESIGN POWER_PATH SOFAR_QUESTIONS DEV_LOG PROMPTS
docs/design-review/           netcheck.md, out/ (check outputs), final review package
nereus_Pi_shield_ADIN2111/    live KiCad project (the only design agents edit)
tools/                        check.sh, netcheck.py, midwire.py, schedit.py, ercsum.py, fpextract.py (+ tests)
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

### S5 — Pi header wiring, ADIN details, load switch  `[~]`
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
- [ ] S5.h: Nick's KiCad look (Tools → Edit Symbol Fields); S5 is then complete → S6
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
S5.h: `tools/check.sh` → ERC 531 / 27 / 504 (unchanged), netcheck 51/51, midwire 0, exit 0, `BOM: docs/design-review/bom.csv
(54 rows)`; netlist identical except the new `ALT…`/`SOURCING` fields; `bom.csv` row R8 shows UR73D1JTTD10L0F then the ROHM and
Vishay alternates.
S5.d: `tools/check.sh` → ERC 535 / 27 / 508 (unchanged), netcheck 51/51, midwire 0, exit 0; netlist: VBUS_OUT + J5.1,
GND + J5.2, nothing else.
S5.c: `tools/check.sh` → ERC 535 / 27 / 508 (unchanged), **netcheck 51/51**, midwire 0, exit 0; netlist: R26 on
I2C1_SCL + 3V3, R27 on I2C1_SDA + 3V3, R43 on ADIN_PWR + GND, TP19 on SW_EN, R10 gone, nothing else.
S5.b: `tools/check.sh` → `ERC messages: 535  Errors 27  Warnings 508`, netcheck 50/50, midwire 0, exit 0;
netlist: ADIN_INT/MISO/MOSI/NSS/PWR/RST/SCK, I2C1_SDA/SCL, SW_EN, SW_FLAGB each gain exactly their J1 pin (22/21/19/24/16/18/23, 3/5, 36, 38).

### S6 — Design review package  `[ ]`
- [ ] ERC clean, or every remaining item justified (incl. FID1–6 hidden NC pins, the
      regulator switch-node/rail power pins, #PWR34 ADIN_VDDIO)
- [ ] Remove/update stale sheet notes (e.g. "Processor + onboard logic runs off 3V3…" on Top-Level; the "Molex 2-pin" bus
      note was updated in S5.d)
- [ ] Schematic tidy, after all technical work (Nick, 2026-10-06): R26/R27 drawn onto J1's I²C stubs instead of floating
      with labels; every board interconnect on the right of the Top-Level sheet; widen the bus text box (wraps to 5 lines,
      QE); general cosmetic layout
- [ ] Net check: kept nets match the copper; every new net listed
- [ ] Schematic PDF (all sheets)
- [ ] Change log of every edit
- [ ] Open questions and proposed values, with datasheet citations
- [ ] Pin map, power budget, BOM changes
- [ ] Footprint attributes: the Altium import left every footprint's type unspecified (no SMD/THT `attr`) and no
      courtyards (they're on User layers). Set them before fab outputs, or JLC's SMD-only position file drops parts
      (QE S4.d N3; Nick's layout or a schematic/library pass)
- [ ] BOM for a JLC order: `bom.csv` also lists the 16 test points, FID1–6 and MTG1–4 (`in_bom yes` since the import; QE S5.h
      N2). Set `in_bom no` on them or filter the export
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
