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

## 2026-11-12 — Sprint S10 — The project is Nereus_Pi_Shield_Adin2111 at the repo root; strap tables checked (rename session)

**Branch:** sprint/10-repo-rename, cut from `main` at `4a4c14b`; seven commits (17830f6, fd5e61f, 01ef6c8, dffe78c,
d3f2de6, 1cc11b8 and the docs commit). Not pushed, no PR.
**Files touched:** the whole project folder (moved and renamed), `tools/check.sh`, `tools/boardpdf.sh`, `tools/pdfmerge.js`,
`tools/bompdf.py`, three legacy tool docstrings, `docs/design-review/` (`bom.csv`, `bom.pdf`, `schematic.pdf`, `board.pdf`,
README note, BOM review paths), TRACKER, DESIGN (D57), SPEC, CLAUDE.md, README, QE agent file, checklist, this entry
**ERC:** 39 items, unchanged  ·  **Net diff:** none (143 parts, 110 nets, values, footprints and fields identical; DRC 3
errors not excluded, 16 excluded, 0 unconnected, 0 parity; the board equals tag `s9-layout-freeze` apart from the hidden
BOM fields and 143 sheet file names)
**Done:**
- /agent-entry; plan with 16 questions for Nick (https://claude.ai/artifact/4SbhgpZhw9QLdpF1voLRtV); the rename tried on
  a scratch copy first. Nick, this session's chat: "make the changes"; KiCad closed on his word ("Closed, go ahead"),
  confirmed with pgrep. He typed no answer to the plan's questions, so its recommendations were followed.
- Seven steps, each with its checks in the commit message: old schematic-only project out (tag
  `archive/schematic-only-project`); folder moved; project files and six sheets renamed by
  `scripts/rename_project_2026_11.py`; leftovers into `history/`; cover revision line; check script, BOM names and PDFs;
  docs. Details: TRACKER S10, DESIGN D57.
- ADIN strap tables checked against the datasheet Nick supplied (`~/Downloads/adin2111.pdf`, the SHA-256 SPEC cites),
  Table 22 on page 27 read from the rendered page: all four rows of the schematic table and the bottom silkscreen
  match; "OPEN Alliance with CRC" is the datasheet's "OPEN Alliance with Protection" (0 / 0). Nothing edited.
- New `scripts/verify_against_freeze.py` (also run by `tools/check.sh`): the board against the freeze tag with the BOM
  fields taken out and the sheet file names blanked.
**Broke/surprised us:**
- This Mac's disk is case-insensitive: `Nereus_Pi_Shield_Adin2111/` and the old `nereus_Pi_shield_ADIN2111/` are one
  path, so the old project had to leave the tree before the move. Tried in a throwaway repo: a clean checkout gets the
  new capitals on pull; a folder that still holds untracked files keeps its old name.
- The board file never names the project; it names the six sheet files, once per footprint (143 lines).
- `tools/netcheck.py` reads no nets from a KiCad 10 netlist ("parsed no nets"); `check.sh` no longer calls it.
- `kicad-cli pcb export pdf` with `--scale` 2, 1.5 or 0 gave empty or near-empty pages; only 1 : 1 plots the board on
  the page. `board.pdf` is therefore 1 : 1 on A4 (vector).
- The plan's cover wording "First build, silkscreen Rev0; …" ran past the revision table; "First build (Rev0); …" fits.
- KiCad was open on the main checkout's `experiments/nick_raw_routing/` when the go came; work started after Nick quit it.
- No PDF tool is installed (no poppler, no Python PDF library); the datasheet and the PDFs were read through macOS
  PDFKit from `osascript`.
**Not done:** the renamed project has not been opened in the KiCad application; nothing pushed; no QE; the review
package README still describes S6's package; Sofar Q8 not sent (the cover keeps Sofar's CC BY-ND notice, the GitHub
repository is public).
- Later the same morning, Nick, this session's chat: "I am keeping and inheriting the sale lisence as Sofar" (the same licence as Sofar's). Recorded in
  TRACKER S10 and on Q8 in SOFAR_QUESTIONS; the cover already carries Sofar's notice word for word, so no KiCad file
  changed. He also gave the word for the push and the draft PR ("The Push onpen draft PR - this is the last step now I
  am sending to Sofar").
**Next:** QE in a fresh S10 session on the draft PR; Nick's KiCad look; merge.

## 2026-11-11 — Sprint S9 — PR 35 merged; J1 socket decided (BOM session, late evening)

**Branch:** sprint/9-j1-socket, cut from `main` at `4acd4ff`
**Files touched:** `BM_Mote_1_Master.kicad_sch` (J1's fields), `nick_raw_routing.kicad_pcb` (J1's hidden footprint fields),
`scripts/bom_fields_2026_11.py`, BOM CSV / PDF, `bom_review_2026-11.md`, DESIGN (D56), SPEC, TRACKER, checklist, this entry
**ERC:** 39 items, unchanged  ·  **Net diff:** none (nets identical to the freeze; DRC counts unchanged, 0 open, parity 0)
**Done:**
- PR 35 merged to main at 9:03 PM Pacific as `4acd4ff`, on Nick's instruction, after QE round 3 APPROVED on `81879a3`
  with 0 findings (posted on the PR). Main's files equal the approved commit. The PR branch is deleted on GitHub;
  only `main` and the three `archive/` tags remain there.
- Nick, this session's chat: "I would like to use the 8mm or 8.5mm tall header. Add that decision please so all order
  decisions are final". J1's planned part is ZHOURI 2.54-2*20, JLC C2977589: insulation height 8.5 mm, pin length
  3.2 mm, gold on brass, 2.5 A by JLC's attributes, stock 37,633 (read 9:06 PM). Backup Megastar C7499354. DESIGN D56.
- He had asked for the shortest socket first. JLC lists one 5 mm 2×20 through-hole socket (Kinghelm, C55160398): 12 in
  stock, no datasheet link, fit on the Pi's pins unchecked; nothing shorter at 2.54 mm pitch. Search record:
  `~/NereusData/nereus_Pi_shield_ADIN2111/bom_review_2026-11-11/j1_socket_search_2026-11-11.md`.
- The schematic PDF of the merged board was exported for Nick's look at the cover sheet:
  `~/NereusData/nereus_Pi_shield_ADIN2111/bom_review_2026-11-11/pr35_head/nick_raw_routing_schematic_pr35_1d35732.pdf`.
**Broke/surprised us:**
- JLC's page gives J1's assembly type as wave soldering; J1 is on the bottom side of a board with parts on both
  sides. How JLC fits it is not checked.
- An unquoted shell here-document ate three back-quoted names in a docs commit of PR 35; caught on the diff, fixed in
  `81879a3` before QE's last round. Here-documents with back-quotes are quoted from now on.
**Next:** this branch needs a PR, QE and merge on Nick's word; then the JLC export and the Sofar package from main.
U1 (ADIN2111BCPZ) is the one line not yet at JLC.

## 2026-11-11 — Sprint S9 / S8 — BOM review of the frozen board for the JLC order (BOM session)

**Branch:** claude/adoring-mclaren-10dc39 (the BOM session's own; fast-forwarded to tag `s9-layout-freeze`). Pushed on
Nick's word the same evening as draft PR 35 to main; see the end of this entry.
**Files touched:** the six sheets in `experiments/nick_raw_routing/` (fields only), `nick_raw_routing.kicad_pcb`
(hidden footprint fields only), `scripts/bom_fields_2026_11.py`, `scripts/bom_fields_board_sync_2026_11.py`,
`docs/design-review/bom_nick_raw_routing.csv` / `.pdf`, `bom_review_2026-11.md`, `tools/bompdf.py`, this entry, TRACKER
**ERC:** 39 items, unchanged  ·  **Net diff:** none (nets, values and footprints identical; DRC counts as `drc_24.json`,
0 open, parity 0)
**Done:**
- /agent-entry; Nick's go in this session's chat ("otherwise [the] plan sounds good"), with two directions: "reference
  all the alternatives given in the source mote file in the reference folder" and "The ideal outcome is that you find
  alternatives on the Sofar list that JLC stocks".
- Sofar's alternates read from the mote reference (8 sheets, 170 parts, every field): only R8 (seven part numbers), D1
  (two) and Y2 (one; not on the shield) carry any. The review sheet of 10/23 holds no reply from Sofar.
- JLC stock read for every line, its planned part and its backups: jlcpcb.com parts search, 2026-11-11 4:24 to 4:31 PM
  Pacific, not signed in. Table and a second reading: `~/NereusData/nereus_Pi_shield_ADIN2111/bom_review_2026-11-11/`.
- R8: Sofar's alternate 7, Stackpole CSRF0603FT10L0 (C346485), is in JLC stock (9,822); alternate 1 has 16; the
  other five have 0 or no listing. Both are in R8's ALT fields.
- Five lines went back to Sofar's specified part, which JLC stocks now: C16 / C18 / C24 / C25, C19 / C27, C21,
  R21 / R35 / R36 / R37 / R43, R34. Four keep a generic part (C17 / C26, C31, R14 / R18, R20 / R39).
- R47's planned part is the 1 kΩ RC0402FR-071KL (C106235); C59's planned part is its 220 nF value; J3's fields carry
  the upper-case names; text placeholders in PLANNED LCSC replaced by JLC's part numbers.
- BOM of this board: 53 lines, 108 fitted parts and R11. Export:
  `kicad-cli sch export bom -o docs/design-review/bom_nick_raw_routing.csv --fields 'Reference,${QUANTITY},Value,MANUFACTURER,PLANNED MPN,PLANNED MFR,PLANNED LCSC,PLANNED NOTE,${DNP},SOURCING,ALT1 MPN,ALT1 MFR,ALT1 LCSC,ALT2 MPN,ALT2 MFR,ALT2 LCSC,ALT NOTE,Footprint' --labels 'Refs,Qty,Value (MPN),Mfr,Planned MPN,Planned Mfr,Planned LCSC,Planned note,DNP,Sourcing,Alt1 MPN,Alt1 Mfr,Alt1 LCSC,Alt2 MPN,Alt2 Mfr,Alt2 LCSC,Alt note,Footprint' --group-by 'Value,${DNP}' experiments/nick_raw_routing/nick_raw_routing.kicad_sch`
**Broke/surprised us:**
- This worktree's branch was cut at 5180c47 (step 16), 14 commits behind the freeze tag; fast-forwarded on Nick's go.
- KiCad 10's schematic parity compares every symbol field with the footprint's copy: the sheet edits alone gave 109
  parity items. The same values went into the board's hidden footprint fields (285 changes, 70 new hidden fields on
  the Fab layers). With those fields taken out the board equals the tag byte for byte (`--verify`); its SHA-256 is no
  longer 3728e882…: the freeze is now "tag `s9-layout-freeze` plus BOM fields".
- `tools/schedit.py` writes new fields in KiCad 9's form; the sheets are KiCad 10 files, so the new script copies the
  symbol's own PLANNED MPN field as the pattern.
- Fields differed inside one BOM line (C22 / C23, R15 / R16, D2 / D3, L1 / L2, L3 / L6, MP1 / MP2 to MP4, U2 / U3), so
  the export joined two texts in one cell. Each line now has one text.
- F1 is a PPTC resettable fuse (SPEC constraint 8). C597304 (Sofar's 08051C474KAT2A) shows no maker on JLC's page.
- R12, R13, R17, R19 are not on this board (Nick's commit 1c75bd3); R38 is 13.3 kΩ (Nick's commit 629d4e8) while
  DESIGN D16 says 13.7 kΩ.
- A direct request to JLC's search from the shell was refused by the permission check; the figures were read through
  the browser pane and copied into the table, then checked against a second reading (one stock figure had moved).
- Not done: no datasheet read (CSRF0603 land pattern against R8's pads, C2012X7S2A105KT000N's thickness); no QE
  review; `pi-shield-checklist.html`, DESIGN and the Sofar brief are left to the design session.
- Later the same day (about 4:45 PM Pacific): Nick sent two screenshots of his JLC Parts Order History. Orders
  DOB202610210529840 (2026-10-20: R8 25, C22 / C23 60, R15 / R16 50) and POB0202610210527741 (L1 / L2 42) read
  "Complete", as do six of the seven lines of DOB202610190524705. **U1 (ADIN2111BCPZ, 22) still reads "Purchasing"**,
  six days past JLC's estimate of 2026-11-05. Its order line carries JLC part C3226961, which JLC's public listing
  names ADIN2111BCPZ-R7; the field now says C3226961 (was C3226964, from the public search). SOURCING of the eleven
  bought lines names its order, quantity and status. Checks again: ERC 39, DRC counts unchanged, parity 0, nets
  identical, board identical to the tag apart from the BOM fields. Open lines: six → three (U1, F1, J1).
- Nick, this session's chat, 2026-11-11, after the screenshots: "Keep F1". F1 (PPTC) stays for this unpotted build, an exception to SPEC
  constraint 8, written into F1's SOURCING field and the review; SPEC and DESIGN are not edited. Checks again: ERC 39,
  parity 0. Open lines: U1 (not at JLC yet) and J1 (socket).
- Evening: Nick, this session's chat: "Lets merge all of this [onto] main and delete all other branches". He chose the
  route "PR, QE, then merge", "Tag, then delete" for branch tips main lacks, and to leave the two other sessions'
  worktrees until the design session is done. Done: the design session's step 25 (4ae53a7) merged in without
  conflict; checklist synced; **draft PR 35** to main (104 commits, fast-forward); 35 remote branches deleted, each
  tip recorded in `~/NereusData/nereus_Pi_shield_ADIN2111/bom_review_2026-11-11/branches_to_delete_2026-11-11.txt`;
  tags pushed for the three tips main lacks (`archive/reload_old_mote`, `archive/experiment-fable-layout-01a`,
  `archive/sprint-8a-jlc-parts-buy`). Left: local `Fable_5.2` and `claude/fable-5-2-continue-55a515`.
- QE round 1 on PR 35 (`docs/design-review/qe/S9.md`): CHANGES REQUESTED, 3 major, 5 minor, 3 nits; board, freeze,
  netlist, BOM CSV and stock table confirmed. Fixed here: findings 4, 7, 8, 9, 10 (11 needs no change). Waiting on
  Nick: R38's value (13.3 kΩ puts the Pi rail's worst case at 5.28 V per `power_budget.md` §5), his OK to record the F1
  exception and the merge of the experiment folder in SPEC and DESIGN, the two spare board files, and whether J4
  should be live as shipped.
- Nick's answers (this session's chat, same evening): "Keep 13.3 kΩ"; "Yes, write both"; "Remove from the folder";
  "Yes, selector as built". Written: DESIGN D52 (R38, bench check 4.75–5.25 V at J1), D53 (F1), D54 (this board on
  main), D55 (JP1's three states); SPEC constraints 1 and 8 amended, R38's fact and open question updated; the two
  old board files deleted from the folder. No 13.5 kΩ 0402 part had JLC stock (12 listings, all 0). Round 2 sent to QE.
- QE round 2 (head 95fb538): APPROVED WITH NITS. All 11 findings closed, finding 11 withdrawn by the QE, one new nit
  (DESIGN pin map, J1 pins 1 / 17 are PI_3V3 on this board), fixed. The QE's check of that fix push and the merge
  itself are recorded on PR 35, so that the merged commit is the one the QE saw.
**Next:** U1's arrival at JLC (Nick asks JLC support; the order cannot include U1 before); Nick's pick for J1;
QE review of the BOM session's commits; the design session's JLC export from this branch's board.

## 2026-11-11 — Sprint S9 — New design session: Nick's answers to the open items; two mocks

**Branch:** claude/fable-5-2-continue-55a515, cut from `Fable_5.2` at 5180c47. Nick approved it in the previous
session's chat on 2026-11-11 ("Yes, new branch", 2:04 PM Pacific, read in that session's transcript): the app could
not share the old worktree. The commits return to `Fable_5.2` by fast-forward later, on Nick's word. Nothing pushed.
**Files touched:** this entry, TRACKER (S9)
**ERC:** 39 items on the mock copies, unchanged  ·  **Net diff:** none (no board or schematic change yet)
**Done:**
- /agent-entry; summary doc read and trimmed to open items on Nick's request (a copy of the doc before the trim:
  `~/NereusData/nereus_Pi_shield_ADIN2111/summary_doc_backup_2026-11-11/`). Doc comments reach this session.
- Nick answered the seven open items as comments on the summary doc (read in the threads, 2:17 to 2:26 PM Pacific):
  pin 22 "Tie it to GND"; U10 input capacitor "Leave as the mote has it"; fiducials "approved make it happen";
  Sofar's empty frame "Remove it"; JP1 end marks "Leave them off"; the vias at L6 "Make them useful like the mote, so
  they help with thermal" / "show me"; R-S1 "show me a mock ... What thermal vias, if any, should be added?"; R47 "I
  believe the intent was the 1.5kohm ... Does the 1.5kohm still work as intended".
- R47 answered in its thread: with R2 4.7 kΩ to 3.3 V, GPIO16 low through 1.5 kΩ puts pin 19 at 0.80 V, on the ADIN's
  V_IL of 0.8 V (SPEC, Rev. B Table 1); 1 kΩ gives 0.58 V. Recommended 1 kΩ. Nick's pick is open.
- Mock M-S4 (`ms4_mock_2026-11-11/`): the three 5V_PI vias under L6 between its pads at (124.60 / 126.40 / 128.20,
  87.15), on a new 5V_PI fill on the PWR Plane (57.2 mm², x 123.55..131.00, y 86.75..95.00). The PWR Plane was empty
  there; the copper under the old via places is the PI_5V pour. 0 open, parity 0, no new DRC item, via_dangling 7 → 4.
- Mock R-S1 (`rs1_mock_2026-11-11/`): a top-layer GND fill at U10 (12.2 mm², settings of Sofar's fill at U5) and two
  GND vias at (132.70, 90.10) and (133.14, 87.75). 0 open, parity 0, no new DRC item; Sofar's 3V3 fill 525.4 → 522.1 mm².
- Both mocks are in the summary doc; nothing is built. Nick decides each.
**Broke/surprised us:**
- A clean checkout gives 2 more DRC warnings than `drc_16.json`: `nonmirrored_text_on_back_layer` for the "*" texts
  of U5 and U10 on B.Fab (Sofar's footprint). The old worktree's `nick_raw_routing.kicad_prl` (local, not in git)
  hides that layer; with that file copied in, the report equals `drc_16.json` exactly. New baseline for comparisons:
  `ms4_mock_2026-11-11/drc_base.json` (untouched copy, all layers visible).
- The power budget puts 26 mW in L6 and 0.53 W in U10 at 1 A (`power_budget.md` §3): the fill at L6 has little heat
  to spread; R-S1 is the change that matters for heat. Said so in the doc.
- Sofar's U5 has a top GND fill under its body but no via under the body; the R-S1 mock's via under U10 is new
  against the mote. Said so in the doc.
- analog.com timed out again; the ADIN2111 datasheet is still unread this month (strap table rows, internal pull-up).
- Sofar's rule areas on the GND and PWR planes around the old mote outline carry no restriction (all flags off).
- Later, once KiCad was closed (2:40 PM Pacific): step 17, Sofar's empty name frame off the bottom silkscreen on
  Nick's "Remove it" (DESIGN D46). 50 lines out of the board file, nothing else. DRC counts unchanged against the
  clean-checkout baseline, 0 open, parity 0, ERC 39 (`steps_2026-11-11/drc_17.json`, `erc_17.json`).
- Nick's second round (2:43 PM, doc comments and chat): R-S1 "approved"; the L6 vias "Approved, but ... a polygon like
  Sofar did under [the] large L1 L2 inductors"; R47 "the 1kOHM it is" (chat). Step 18 (c445bff): top GND fill and two
  GND vias at U10, built as mocked. Step 19 (ae8380d): the L6 vias on the 5V_PI fill, with one top-layer polygon in
  place of the mock's three necks (Sofar's polygons are net-tied shapes with 0.25 mm chamfers; 17 on the board).
  DESIGN D47. After step 19: 3 skew errors not excluded, 16 excluded, via_dangling 4, 0 open, parity 0, ERC 39.
- R47 needs no board or symbol change for 1 kΩ (Value and PART NUMBER say so already); only the PLANNED fields are
  wrong, left for the BOM session.
- Fiducial search (read only): no place within 8 mm of the north-west pair is free on both sides for a 1 mm dot
  in a 2 mm opening 3.5 mm from the edge; the other two pairs have free places 0.4 and 0.9 mm away. Not built yet.
- Third round (about 2:55 PM, chat): "board looks good"; two silkscreen requests for the next round. Step 20: ADIN_TIMER
  off J2, pin 22 to GND, schematic and board (DESIGN D48). Step 21: board name turned 180°, J2's top-side names
  0.30 mm south (DESIGN D49). After step 21: 3 skew errors not excluded, 16 excluded, 0 open, parity 0, ERC 39.
- The schematic edit of step 20 is a text edit of the Master sheet (label block out, two wire ends and the GND
  symbol's coordinates changed); parity 0 against the board and ERC 39 are the check that KiCad reads it as meant.
- Turning the logo with the name put it on its head at the south end (first trial); built with the logo left
  upright in place. That variant was run on the board directly, without a second trial.
- `run_step.sh` hid a failed assertion once (its output filter dropped the line) and went on to DRC an untouched
  scratch copy; it now stops when the step script fails.
- Fiducials (step 22 script written, tried, not built): a place free on both sides exists for the north-west pair
  at (125.90, 92.00), 11.6 mm from the old one, between L6, the AUX OUT box and C55.
- Fourth round (about 3:15 PM, chat, with a picture): the logo as in step 21's first trial; fiducials good; notes
  block to the edge, boxes around both note blocks; then refine the small designators; then the freeze. Step 22
  (fiducials, DESIGN D50), step 23 (logo with the name, notes and boxes), step 24 (designators) built (D51).
- Step 24's planner works on bounding boxes, which are larger than the drawn letters: it calls most present places
  "blocked" and finds free ones for eleven designators; ten in the dense areas have no clearly better place and stay.
- Six tented vias lie under the bottom notes' text, three of them from step 19. Not moved.
- After step 24: 3 skew errors not excluded, 16 excluded, 0 open, parity 0, ERC 39; silk_overlap 13, silk_over_copper 6.
- **Layout frozen** on Nick's "Yes, freeze it" (about 3:35 PM): the board as of step 24 (456752d), SHA-256
  3728e882268f10ad619c7eda81b289087a70814d26bca223493e208346a3518e; local tag `s9-layout-freeze`. Nothing pushed.
- After the freeze (3:45 PM): step 25, the schematic's cover sheet shows the board's top and bottom view with
  dimension lines (Nick's request in chat). KiCad takes an embedded picture without a resolution tag at 300 ppi; the
  placeholder frame had a grey fill that hid the picture, now none. Sheet +328 kB. ERC 39, parity 0, board untouched.
**Handoff state (for a rotation or the BOM session):**
- Branch claude/fable-5-2-continue-55a515, tree clean, 43 commits ahead of `origin/Fable_5.2` (c0edb77), no PR, no QE yet.
- Checks of the frozen board: `~/NereusData/nereus_Pi_shield_ADIN2111/steps_2026-11-11/drc_24.json`, `erc_24.json`
  (clean checkout, all layers visible): 3 skew errors not excluded, 16 excluded, 0 open, parity 0, ERC 39.
- Step runner and helper scripts of this session: the session scratchpad (`run_step.sh`, `layerplot.py`, `fidfind.py`,
  `desig_audit.py`, `near.py`, `zonearea.py`), copied to `~/NereusData/nereus_Pi_shield_ADIN2111/session_tools_2026-11-11b/`.
- BOM facts found on the way: R47 PLANNED MPN / LCSC name the 1.5 kΩ part, the decision is 1 kΩ (RC0402FR-071KL);
  the manufacturability review's list (J3 no part number, J1 "TBD", C59 mismatch, no LCSC number for U1, L3 / L6, Y1,
  D1, R8, R15 / R16, R38 13.3 kΩ against D16's 13.7 kΩ) is not checked by this session; `bom.csv` is the live
  project's, not this board's. Where Sofar's list of alternates lives is not known.
- The summary doc (https://claude.ai/artifact/Jy3PvmmmkEJk8qQLjoTvq2) shows open items only; its comments reach this session.
**Next:** schematics and BOM documents (the BOM session is Nick's to start); DESIGN pin map and Sofar brief against
the board; JLC export from the frozen board; design review doc on Nick's word; draft PR and QE.

## 2026-11-11 — Sprint S9 — Handoff after steps 12–16 (session rotation, 2:01 PM Pacific)

**Branch:** Fable_5.2 (work only here; push only on Nick's approval, each time)
**Files touched:** this entry only
**ERC:** 39 items (`erc_16.json`)  ·  **Net diff:** none in this entry
**State:**
- Board `experiments/nick_raw_routing/` is at step 16 (b0115b9). DRC after step 16 (`~/NereusData/nereus_Pi_shield_ADIN2111/step9_2026-11-11/drc_16.json`): 3 errors not excluded (skew, kept pending Sofar), 16 excluded, 0 open, parity 0.
- Tree clean at this commit; 28 commits (3054b8c … 14c826a) plus this one are ahead of `origin/Fable_5.2` (c0edb77). No PR on the branch (`gh pr list --head Fable_5.2 --state all` → `[]`). No QE review of steps 12–16 yet.
- Summary doc for Nick, where he comments and approves: https://claude.ai/artifact/Jy3PvmmmkEJk8qQLjoTvq2 (sections "Built on your approvals of 2026-11-11" and "Still open"). Plan page https://claude.ai/artifact/WW6S2MLhrNHYLe7zbg5Wsc is stale since step 9.
- Helper scripts of the outgoing session (scratch trial, DRC diff, board compare, net and plane plots, doc-edit scripts): `~/NereusData/nereus_Pi_shield_ADIN2111/session_tools_2026-11-11/`. They carry the old session's scratchpad path inside; adjust before use.
**Open with Nick (no change without his word; layout changes are mocked first):**
1. J2 pin 22 once ADIN_TIMER leaves the breakout header: unconnected or GND (schematic change, about 3 mm of track re-laid around the pad, "TM" removed on both sides).
2. R47's value: fields disagree (Value / PART NUMBER `RC0402FR-071KL`, PLANNED MPN `RC0402FR-071K5L`).
3. Extra input capacitor at U10: leave, add, or an unfitted footprint.
4. The three vias at L6: delete or give them a 5V_PI fill; settle together with R-S1 (U10 thermal copper, not mocked).
5. Fiducials: 1 mm dots in 2 mm openings, moved inboard (mock on his word).
6. Sofar's empty name frame on the bottom: remove or keep.
7. JP1 end marks (recommended: leave out).
**Not done:** datasheet check of three of the four strap-table rows; Sofar brief and DESIGN.md pin map behind the board (routing review N12); where Sofar's list of alternate parts lives is not known.
**Order after the decisions (TRACKER "Order of work to the JLC order"):** layout and schematic changes → final silkscreen pass → freeze → schematics and BOM documents (BOM in its own session that Nick starts) → JLC export from the frozen board → design review doc (skew errors first, then R-S6) → draft PR and QE.
**Next:** Nick answers the open items in the new session; first one is pin 22.

## 2026-11-11 — Sprint S9 — Step 9h: silkscreen style; two read-only reviews started

**Branch:** Fable_5.2
**Files touched:** experiments/nick_raw_routing/ (board: silkscreen only; scripts/step9h_silk_style.py, .json, step9h_plan/); TRACKER, DESIGN D39, sofar_brief row 13, checklist
**ERC:** 39 items, unchanged  ·  **Net diff:** none (tracks, vias, zones, pads and footprint positions identical to e686111)
**Done:**
- Two mock rounds on scratch copies (`~/NereusData/nereus_Pi_shield_ADIN2111/silk_mock_2026-11-10/`, `silk_mock_2026-11-11/`), then step 9h (0bd5d89) on Nick's "Yes, build it".
- Menlo Bold for the slashed zero; function names large with the designator under them; J4 / J5 boxed; all 128 designators at 0.8 mm; name and logo in the east strip; ratings and screw sizes on the bottom (DESIGN D39).
- DRC: 3 errors not excluded (skew), 16 excluded, 0 open, parity 0. Silkscreen overlaps 54 → 25, silkscreen on copper 14 → 8.
- Two read-only reviews of e686111 started as background agents (routing and reliability; manufacturability at JLC). The manufacturability report is in `~/NereusData/nereus_Pi_shield_ADIN2111/review_2026-11-11/dfm_review.md`.
**Broke/surprised us:**
- J4 is a 5 V output (converter → JP1 → F1 → J4); the 9c label "5V IN" was wrong.
- KiCad checks TrueType stroke weight: 199 texts flagged under 0.15 mm, even some 1.5 mm ones (thin details such as the zero's slash).
- The port LEDs sit on the far side from their ports (D9 on port 1 is by BM2). The names match the nets; Nick wants the LEDs swapped.
- KiCad writes each TrueType text's outlines into the board file (render cache), about 10 000 lines.
- Later the same day: both review reports came in (0 blockers in the design; 12 should-fix items), summary doc for Nick's comments at https://claude.ai/artifact/Jy3PvmmmkEJk8qQLjoTvq2.
- Step 10 (7c30e8f) on Nick's "Yes, build it": port LEDs swapped so each sits beside its own port (DESIGN D40). Only the four LED nets change; DRC and ERC counts unchanged.
- Step 11 (6874391): JP2 turned to lie east-west, "ADIN" above D8 (DESIGN D41); then pushed on Nick's word.
- Step 12 (3054b8c) on Nick's "Yes build it": the ADIN strap table on the bottom as a ruled table, "Pi Shield / ADIN2111 Rev0" off the bottom (DESIGN D42). Silkscreen only. DESIGN's strap table corrected: CFG1 reads 1 as built (JP3), not 0.
- Step 12b (0a885e9): screw sizes on the bottom spelled out, "THREADED INSERTS M3" / "MOUNTING HOLES M2.5" (Nick's doc comment).
- Step 12c (242e46c): port LED names P1 / P2 become BM1 / BM2 (Nick's doc comment).
- Nick's doc comment: the 3 skew errors stay as they are pending Sofar; they open the design review doc he will ask for.
- Step 13 (0595d79) on Nick's "I approve the mock": Qwiic J3 on the centre line, J4 2.15 mm south with AUX OUT labelled like VBUS OUT (DESIGN D43). J3 copper to BM2_N 2.37 → 1.02 mm.
- Step 14 (a41524d) on Nick's "Proposal approved": north-west GND fill pulled 0.5 mm clear of Sofar's west ground wing (R-S4, DESIGN D44). Outline only; checks unchanged.
- Step 15 (d6a4fb8): R15 / R16 back on Sofar's footprint, board and PoDL sheet (M-S5). Step 16 (b0115b9): thermal relief on J6's GND pins (M-S6). DESIGN D45; checks unchanged.
**Next:** Nick's remaining decisions in the summary doc (which review fixes to make before Sofar's review).

---

## 2026-11-10 — Sprint S9 — Routing plan for nick_raw_routing; step 0 (fixes before routing)

**Branch:** Fable_5.2 (from reload_old_mote 3d596b9; Nick 2026-11-10: this work gets its own branch, pushed on his approval)
**Files touched:** experiments/nick_raw_routing/ (board, .kicad_pro, .kicad_dru; Master sheet: MTG1–4 off board, J5; PoDL sheet: note; nereus.pretty: wire pads; scripts/ new); TRACKER (S9), DESIGN D33–D38, SOFAR_QUESTIONS Q13, sofar_brief row 8, jlc_rules_2026-11.md, viewer
**ERC:** 39 items, identical before and after  ·  **Net diff:** tracks and vias identical to the zip board; only MTG1–4's pads gone
**Done:**
- Reviewed the zip board (2026-11-09): 77 open connections on 46 nets, 424 DRC errors under its own rules, parity 0. Plan
  page with drawings; Nick: base = zip, inserts option 1, part moves approved
- Step 0 (58365af), by script: 44 circles + caption off Edge.Cuts; MP1↔MP2, MP3↔MP4; MTG1–4 removed; J5 and TP38 onto the
  board; GND north strip priority 1; zones refilled. DRC 324 errors, 63 open (41 nets), parity 0
- Read JLC's capability and stackup pages (jlcpcb.com, 2026-11-10 10:36 AM PT). With JLC-based rule values on a scratch
  copy: 134 errors, none from track, clearance or via size in the existing copper
**Broke/surprised us:**
- The Edge.Cuts circles were why J1's GND and PI_5V pins had no plane connection; the refill confirmed it
- Which insert shows "shorting" in DRC depends on item order; the pad/copper mismatch was at all four inserts
- pcbnew's writer settles only on the second save, and a second LoadBoard in one process breaks GetDrawings: the save
  helper runs its second pass in a fresh process
- J5 does not fit at y 111 on the west edge (pads overlap the BM2_N trunk by 0.2 mm); placed at y 122.2
- The BM data pairs and the 16 GND vias in U1's keepout are identical to the mote; the 0.5 mm skew rule is not met by the mote
- Later the same day (Nick's decisions, D34): JLC rule values and the standard stackup JLC06161H-3313 written into the
  settings in one revertible commit (6f54c27), record in `docs/design-review/jlc_rules_2026-11.md`: 324 → 134 errors
- BM data pairs compared item by item with the mote: identical. Sofar Q13 and a note on the PoDL sheet (f9fe3b7)
- Step 0b (cf6ec47): J5 is now two through-hole wire pads (new footprint in nereus.pretty, symbol out of the BOM);
  J6 one pitch west and the fiducials as on Nick's `reload_old_mote` 7cc5f04; TP38 re-placed. Parity 0, ERC unchanged
- Schematic parity compares symbol fields with footprint fields: a swapped footprint needs the symbol's fields copied
- The board's silkscreen already marks the inserts − + − + west to east, which matches the copper and option 1
- Step 1 (a0e6640): ADIN SPI routed. SCK + CS on Internal 2, MOSI + MISO on Internal 1, through J2's first two pin gaps
  to Sofar's vias; J1 pin to U1 pad 32.7 / 36.4 / 39.5 / 34 mm (SCK / CS / MOSI / MISO). Open connections 63 → 60
- The PI_3V3 feed to J2 pins 9/11/13 (Internal 2, y 89.5) crossed SCK and CS and had to go; it returns in step 4
- After a `board.Remove()`, pcbnew's Python bindings cannot list tracks again: the scripts collect first and remove last
- Nick's four requests for the south edge and the holes are captured in TRACKER S9
- Step 1b: Nick's four requests applied. Inserts mirrored about the centreline with their rings and trunk ends; LEDs in
  one line 3.5 mm from the south edge; J4 as wire pads; copper keep-outs (r 3.0 mm, all layers) at H1–H4, plane copper
  checked to be pulled back. DRC errors 134 → 151: the 17 extra are all at the insert footprint
- KiCad's ERC picks one of several net names at random for a "multiple net names" warning: same 39 items, wording varies
- The pink Nick saw over Sofar's tracks is KiCad's locked-item shadow (158 locked segments), not copper
- Step 2: ADIN control nets and both straps routed. Two nets on one layer in the header channel cross unless their
  west-to-east order at J1 equals their order at J2: RST and ADIN_PWR share the bottom, INT has the top
- R2's CFG1_STRAP pad sat boxed in under U1 (thermal vias, U1's pad on the other side): R2, R47 and JP3 now sit together
  south of U1 and the pin-19 node comes to them on Internal 2 from its existing via. Open connections 60 → 47
- Around noon the repo folder was renamed by mistake and a fresh clone took its name; the work continues in a new
  worktree of that clone on Fable_5.2 (nothing was lost: everything was pushed)
- Step 3: the insert errors traced to the Altium import of the unplated hole (size 0 on inner layers, a net-less 5.5 mm
  disc on the bottom). Plain hole + two scoped rules + trunk ends 0.25 mm off the hole: DRC 151 → 25 errors
- The "solder mask bridge" at MP4 only was the fiducial's 2.25 mm mask opening touching the insert's, not the insert itself
- The 25 left: 16 GND vias in U1's keepout (as on the mote, kept), 3 skew (Sofar Q13), 3 courtyards, R26/R27 (step 5)
- Step 4, power. Sofar's GND plane has a notch in its north-west corner; U10, C54/C55 and J4 sat in it with GND vias
  that reached nothing. A GND zone now fills it and joins the north strip. Open connections 47 → 36
- A plane cannot pass between two 2.54 mm header pins at 0.3 mm clearance (the web is 0.24 mm, under the 0.25 mm
  minimum); the new PI_3V3 zone uses 0.25 mm (web 0.34 mm). JLC's 0.3 mm hole-to-copper still holds (0.6 mm)
- U11's exposed pad overlapped its RTN island by 0.05 mm but was not connected; a short track into the island fixes it
- The bottom silkscreen still carries Sofar's "PCBA-000639-AB BM Mote" label
- Step 7 (all 11 breakout nets) and I2C0 with R26/R27: open connections 36 → 19 on 12 nets, DRC 25 → 22 errors.
  The header channel now holds 4 lanes on top, 4 on the bottom, 2 to 3 on each inner layer
- Stopped there (time box). Left: I2C3 (6), payload switch signals (3), LEDs (10). The area between x 150 and 160 is
  walled north to south on the top and both inner layers; westbound nets from the east J1 pins can only cross on the bottom
- Afternoon: mock-up of the last 19 connections on the plan page, approved by Nick. Steps 5b, 6 and 8 built
  (53ff783, 1688971, 0772b8a): open connections 19 → 13 → 10 → 0. DRC 22 errors, all carried; parity 0; ERC 39
- The mock-up took I2C3 past the 5 V converter on the bottom layer. The trial DRC showed the converter's own 5V_PI and
  VBUS tracks there (2 shorts, 3 crossings): the pair now changes to Internal 1 at two vias south of J6. SDA passes
  between the 5V_FB via and the VBUS via, SCL south of both
- R10 on the top beside J3 overlapped J3's courtyard; both pull-ups sit on the bottom side next to J3's two vias
- A 3V3 stub on the bottom near U11 ended in the open (DRC had it as a dangling track); removing it left its via with
  nothing to join, so the via went too
- There is no GND plane under the LEDs (the plane ends at y 123, with a slot at y 121.5–122.5): D8's cathode runs
  16 mm on top along the south edge to JP3's GND pad instead of dropping into a via
- JP2 is an R1210-size bridged jumper (courtyard 3.3 × 4.7 mm); it fits between C23 and the LED row at y 124.30
- Pushed on Nick's word (3:46 PM), then step 9 a–d (f4faaca, c9db5f8, e1eedf3, ab8baae): dead copper, courtyards, silkscreen
  names, exclusions. DRC 22 → 3 errors not excluded (the skew rule on Sofar's data pairs), 16 excluded, 0 open, parity 0
- Dead copper: removing the tracks DRC calls dangling exposes the next segment of the same stub; it took 4 rounds (30, 17,
  7, 4 segments) to reach none. The open-connection count stayed 0 in every round
- U10's courtyard is 5.1 × 4.4 mm for a SOT-23-6; the capacitors beside it were placed against the body, not the courtyard
- The fiducial FID2 sits beside JP1 and the screw-head area of H1 above it: JP1's name fits only in two short lines
- J2's footprint outline leaves 2.2 mm between it and J1's pads: 3-letter pin names at 1.0 mm height need a 0.6 mm
  character width to fit the 2.54 mm pitch; names with M (MOSI, MISO, TIMER) are cut to two letters at 0.8 mm
- KiCad 10 reads DRC exclusions from the project file as [marker string, comment] pairs; kicad-cli honours them and
  still lists them with `--severity-all`, marked excluded
- The ADIN2111 datasheet could not be fetched (analog.com timed out), so the silkscreen names the straps and their 1 / 0
  ends but not what each combination selects
- Later (Nick's three requests), steps 9e–9g (88e55ae, 779c331, 488cfbd): JP3 beside JP4 in the north-east corner, R26 / R27
  to the bottom side away from J2, board name and Bristlemouth logo. DRC unchanged: 3 skew errors, 0 open, parity 0
- Sofar's GND and PWR planes follow the mote's outline: the north-east corner (east of x 166.5, north of y 96) has no plane
  copper. JP3's first GND via landed in nothing (1 open connection in the trial); it now sits at (167.90, 99.80) in the fill
- The bottom layer next to ADIN_TIMER has no room for a second track past the GND via at (156.55, 120.75) (4 µm short at
  0.127 mm clearance), and a lane south of ADIN_TIMER cannot turn north without crossing it: CFG1_STRAP runs on Internal 1
- The Bristlemouth logo was on the board file all along, 22 mm east of the outline, with the frame of Sofar's title block
  above the north edge
**Next:** Nick's decisions: silkscreen text size, the 3 skew errors, the CFG table. Then final fab outputs and the QE review.

## 2026-10-15 — Sprint S8.a — JLC parts buy plan for the first build (20 boards)

**Branch:** sprint/8a-jlc-parts-buy
**Files touched:** docs/design-review/jlc_parts_buy_2026-10.md (new), docs/design-review/qe/S8.md (new); TRACKER (S8),
DESIGN D32, viewer
**ERC:** not run (no KiCad file touched; Nick is in KiCad on the layout)  ·  **Net diff:** none
**Done:**
- Nick (10/14): 20 boards (6 Sofar by 11/30, 10 Nick, 4 scrap), dev units without potting; buy the critical parts into
  JLC stock this week; PCBA order target 10/30 (fallback 11/3) → D32, S8
- Read today, without logging in: JLC library listings, stock and attrition (jlcpcb.com parts search), the global-sourcing
  and consignment help pages, the instant quote (6 layers, 49 × 68 mm, 20 pcs: PCB 8–9 days, DHL 2–4 BD), and Digi-Key /
  Mouser stock and prices. Buy: 8 lines ≈ $556; steps and a purchase record for Nick
- QE round 1 (fresh S8 session): APPROVED WITH NITS, all 10 fixed: PCBA timeline now takes Standard PCBA's ≥ 4-day floor
  (10/30 order → 11/13–11/18+); "11/3 realistic" → plan on 11/6–11/13; the PCBA order also waits on Sofar's review (a
  rejected alternate falls back to global sourcing); dates in China time; Y1 look-alike -6-K2Z-T3; demo uses
  `main...HEAD`; J5's SOURCING field ticketed for the next schematic edit
- QE round 2: APPROVED WITH NITS (3 wording nits, fixed; no further round needed)
- 2026-10-17: dates re-anchored on a Mon 10/19 payment (PjM 003 relayed a QE 004 nit: Nick buys Monday). Parts at JLC
  10/30–11/16 (11/19 worst); 10/30 needs the very best case; plan on 11/9–11/16. Buy list unchanged
- 2026-10-18: Nick bought: JLC order DOB202610190524705, $956.05, all 7 lines from Digi-Key (shortest lead 10–14 days,
  lowest price on JLC's list); ready for assembly est. 11/5 → boards ≈ 11/19–11/24+. U1 cost JLC's $27.76 vs Digi-Key's
  $15.39 (+$270): he first thought a JLC pre-order (est. $15.48) worth trying to save the $270, though worried JLC would buy from
  Digi-Key anyway at the higher fee; after the session's reading of the pre-order terms (price fixed only after payment,
  up to 18 days) he kept Digi-Key.
  J5 not pre-bought: 31,805 in JLC stock, picked at the PCBA order (Nick)
- Nick merged PR #32 on 2026-10-17 (`56e1e1a`, at ada4e1a). I then pushed the purchase record to #32's branch without
  checking the PR state, so it missed main; cherry-picked onto `sprint/8a-purchase-record` from main (PjM 003 caught it)
- S8 QE date check: APPROVED WITH NITS. Fixed: the pay window that keeps 10/30 possible (Sun 10/18 09:00 – Mon 10/19
  09:00 PT); in the planning case boards arrive ≈ 11/24–12/3, so Sofar's 11/30 is at risk; Timeline 2 rows 11/9, 11/16, 11/19
**Broke/surprised us:**
- JLC now lists U1, L3/L6, D1, D2/D3 and MP1–MP4 (stock 0 or short); the 10/6 check found no LCSC listing. J5 is back in
  JLC stock (34,285), so it skips global sourcing
- Global sourcing is quoted at 9–20 business days (guide) or 9–15 days (sourcing page): the parts, not the board build,
  set the 10/30 date; only the best case makes it
- JLC lists 0 attrition for U1, U2/U3, L3/L6, D2/D3: offered +2 spares (≈ $36) as Nick's call
- R8, R15/R16 (no JLC listing) and C22/C23 (JLC stock 3) will need global sourcing too if Sofar keeps them: a second
  9–20-day wait after Sofar's review unless bought now (≈ $30, Nick's call)
- Digi-Key showed a bot check after ~10 pages; stopped there, used Findchips for the last two prices
- In passing (not fixed): TRACKER still shows S7 open although experiment 1.a merged via PR #31 on 10/9
**Next:** PCBA order once the parts are ready (JLC est. 11/5), after Sofar's review of the planned passives (D27)

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
