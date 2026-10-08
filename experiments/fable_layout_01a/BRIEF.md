# Layout experiment 1.a — fit everything at the proper widths by moving blocks, then a JLCPCB DFM sweep

*Brief for an autonomous layout agent (Fable 5.1, high effort). Owner: Nick Buemond. Written 2026-10-08 after
experiment 01 closed (QE approved with nits, PR #30, never merged). This is an **experiment**: its board is never
merged into the live project. The questions it answers: can an agent, by re-placing blocks (same side, rigid) and a
better routing tactic, reach a board with every new track at its class width and clearance, 0 open connections and
no routing exceptions — and then make it manufacturable at JLCPCB by a documented DFM sweep — without Nick editing
a trace?*

---

## 0. Hard rules (unchanged from experiment 01, read first)

1. **Write only inside `experiments/fable_layout_01a/`**, on the branch `experiment/fable-layout-01a` (created from
   `experiment/fable-layout-01`, so experiment 01's record sits beside you, read only). Never modify
   `experiments/fable_layout_01/`, `nereus_Pi_shield_ADIN2111/` (the live project), `KiCAD_reference_designs/` or
   `Archive/`, and never touch `main`. This is the one place an agent may write a `.kicad_pcb` (DESIGN D31).
2. **KiCad stays closed.** Work through KiCad 9's bundled Python (`pcbnew`) and `kicad-cli`:
   `PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3`,
   `K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`.
3. **Trust artifacts, not exit codes.** Every step ends with a check you ran on the output files and a render you looked at.
4. **Don't change the circuit.** Pin connections come from the schematic. No schematic edit at all (J5 stays the JST GH,
   Nick 2026-10-07).
5. **Copied blocks are rigid.** Translate and rotate (multiples of 90°) only. Never mirror and never move a block or a
   part to the other side of the board. Moving a block is allowed and expected in this experiment.
6. **Never invent a fact.** A dimension, rating or manufacturing limit you can't find in a file, a datasheet or the
   manufacturer's published page goes in `REPORT.md` as an open question.
7. **Stop and report** (in `REPORT.md`, then commit) if the board would have to grow more than allowed in §2, or a hard
   rule would have to break.
8. **Nick is hands-off.** He will not edit traces and will not answer questions mid-run. Write your options review
   (M0), choose, and continue; he reads the record afterwards.

## 1. Starting point

`experiments/fable_layout_01a/` starts as a copy of experiment 01's `tools/`, `board/` (schematic copy, libraries,
`.kicad_pro` with the design rules and the `bus` netclass, `.kicad_dru` with the bus rule, and 01's final board),
`blocks.json` and `heights.json`. Everything in experiment 01's `BRIEF.md` §1–§6 (inputs, frame, fixed placements,
keep-outs, blocks, routing classes) still applies, except where this brief says otherwise. Read 01's `REPORT.md`,
`LOG.md` and the four QE reports in `experiments/fable_layout_01/qe/` before touching anything: they are the record
of what worked, what did not, and why.

The pipeline is `tools/build_all.sh` (M0 netlist → board → M1 fixed items → M2 placement → M3 block copper → M4 planes,
routing, dangling cleanup; `START=m4` reruns the routing from the M3 snapshot). Keep it the only way the board changes.
Change the scripts as you need; keep every check (`check_fixed.py`, `blockcheck.py`, `check_rules.py`, `drcexclude.py`,
`drc_summary.py`, `dangling.py`) running and honest.

## 2. Board

As experiment 01 §2: 46 × 65 mm, x −7.5 … 38.5, y 0 … 65, r 3, 6 layers in the mote's order. **Allowed growth:** the
south edge may move up to 2.0 mm south (46 × 67). Report the final size. Prefer no growth.

## 3. Open questions from experiment 01 — review them first (M0)

Experiment 01 ended with these declared deviations (its `REPORT.md` §6, §7, §10). Your first deliverable is
`OPTIONS.md`: for each question, the options, what each would move or change, what it frees, its risk, and your
recommendation with the reason. Then act on your recommendations.

| # | Open item (01) | What Nick wants reviewed |
|---|---|---|
| Q1 | BM2_DATA_N 23.4 mm vs the mote's 21.3 | T2's and/or the ADIN block's placement and rotation (270°: port-2 pins north?), a pair-aware route, both pairs over unbroken GND |
| Q2 | 1V8 passes a port-1 bus-leg via at 0.225 mm (bus rule 0.35); one DRC error with a reason | move the 1.8 V buck block (B18), or give 1V8 another lane; no exception in this experiment |
| Q3 | 10 new segments narrower than their class (5V_PI, VBUS stitching links, VBUS_OUT at U11) and 13 links routed at 0.15 mm instead of 0.2 | placement that leaves room: U11's cell, the ADIN pocket's exits, the strip east of J1; no fallback widths in the final board |
| Q4 | Bottom-side parts under the inductor envelopes (01 deviation #2) | state the assumption (the 50 W envelope is a top-side volume) and offer the alternative placement that keeps the bottom clear under both envelopes, with its cost |
| Q5 | U1 0.3 mm east of the pocket (courtyard 1.79 mm from the L1 envelope) | a placement that restores 2.0 mm, or a documented reason it cannot |
| Q6 | JP1 on the bottom beside J1; LEDs in a column at the band's east end | whether the new placement can put JP1 on top. **LEDs (Nick, 2026-10-08): can D8/D9/D10 move safely to the centre of the north edge** (the band between the Pi's north standoff holes, y < 7, so that another board stacked on top of this one still leaves them visible from the edge)? Keep their footprints (no part change; a side-view LED would be a schematic/BOM change for Nick to decide later); place them as close to the north edge as the edge clearance, H1/H2's keep-outs and L2's envelope clearance allow, light facing up and unobstructed northward; say what their resistors R44–R46 and the LED_VDD routing cost. If it is not safe, say why and give the nearest placement that is |
| Q7 | DRC exclusions must be applied by hand (kicad-cli cannot store them) | try once more to write exclusions KiCad accepts (marker position = KiCad's own, from a `kicad-cli pcb drc --format json` run in a scratch copy opened and re-saved by `pcbnew`), else keep the table |

Not for this experiment: tying J1's 3V3 pins (circuit), the stacking-header part choice, Sofar's open questions.

## 4. The new tactic

You choose it and justify it in `OPTIONS.md`. Candidates the 01 report named: rotate the ADIN block 270° so the
port-2 pins face north; move the LED resistors out of the band's east end; move B18 (1.8 V buck) to free the 1V8 lane;
plan the ADIN pocket's exits (west-wall lane, north and south strips, under U1) net by net before routing; a
pair-aware router (route P and N together); a 0.05 mm grid near U1; rip-up that targets one lane. Blocks may move
anywhere on their own side; the fixed items of 01 §3 do not move.

## 5. Routing rules

As experiment 01 §6, now as **pass criteria, not defaults**: every new segment at or above its class width and at or
above its class clearance; the bus nets 0.35 mm from every other net (the `.kicad_dru` rule stays active); the data
legs 0.2 mm; the ADIN pairs no longer than the mote's and on unbroken GND; R8's Kelvin links to U4 pad-to-pad by tracks
alone; insert rings and the pull-backs as 01. The 0.15 mm fan-out width is allowed only inside a part's pad field
(≤ 2 mm of track per net). No "declared" narrower links and no clearance exceptions in the final board.

## 6. DFM sweep for JLCPCB (after the routing is clean)

Once M2 holds, review the board as a fabrication house would and make it manufacturable at **JLCPCB** (6-layer,
1.6 mm, their standard process) without Nick editing a trace. Rules:

- **Every limit comes from JLCPCB's published capabilities**, fetched during the run (their PCB capabilities page
  and their 6-layer stackup table), quoted with the URL and the date read in `DFM.md`. Never type a limit from memory;
  if a value cannot be found, say so and use the brief's own figure.
- **Encode every limit in the design rules** (`.kicad_pro` design-rule constraints, netclasses, or `.kicad_dru`
  rules) so `kicad-cli pcb drc` checks it, then run DRC. A limit that is not enforced by DRC is checked by a script
  you write, and `DFM.md` says which.
- `DFM.md`: one row per item — the JLC limit, its source, the board's measured worst case (with where), pass/fail,
  and what you changed. Items to cover at least: minimum trace width and spacing (outer and inner layers); minimum
  via drill, via diameter and annular ring; hole-to-hole and hole-to-copper (same net and different net); copper to
  board edge (the brief's 0.5 mm stays; note JLC's figure); minimum drill and NPTH handling; solder-mask slivers and
  mask-to-copper expansion; silkscreen line width, text height and silk over pads (01's 258 warnings are mostly
  this: clean them up or clip them); courtyards; the stackup — replace 01's "generic 1.6 mm build" with JLC's
  actual 6-layer stackup (copper weights, prepreg and core thicknesses) written into the board, and say what that
  does to the pairs and to the planes' capacitance (Sofar Q11 is open; this is the board's own choice, not Sofar's
  answer); copper balance per layer; outer-layer **GND pours** with stitching vias where the review recommends them
  (state why and where, and what they do to the pairs and the bus feeds); thermal relief vs solid connections on
  the heavy pads (bus feeds, buck inductors, U10's heat); fiducials (FID1–6) placement for assembly; test points
  clear of parts; a `BOM` / `CPL` readiness note (footprint rotations vs JLC's library convention) if assembly at
  JLC is in reach, else say so.
- Keep every pass criterion of §5 while doing it: a DFM fix that breaks a width, a clearance or a pair length is not
  a fix.

## 7. Milestones

| | Milestone | Done when |
|---|---|---|
| M0 | `OPTIONS.md` committed: the §3 review, the chosen tactic, the planned block moves (which blocks, where, why) | Nick can read it; nothing on the board changed yet |
| M1 | Placement: blocks moved per M0, fixed items proven, keep-outs, heights | `check_fixed.py` 0 failures, courtyards 0 overlaps, renders |
| M2 | Block copper copied, planes, routing, cleanup | DRC: 0 unconnected but J1's no-connect pair; errors only Sofar's copied features (01's table) with reasons; 0 copper-defect warnings; `check_rules.py` 0 items below class, 0 clearance items, 0 thin links beyond fan-out, pairs within, Kelvin yes |
| M3 | DFM sweep (§6): `DFM.md`, limits in the design rules, fixes applied, DRC re-run | every `DFM.md` row pass, or fail with a reason Nick can act on; §5 still holds; renders |
| M4 | `REPORT.md` with the §8 table of 01 plus §5 and §6 of this brief, renders, draft PR `EXPERIMENT (do not merge): fable layout 1.a` | QE review requested (docs/PROMPTS.md §5: a separate QE session; save its reports in `qe/`; fix and resend until it approves) |

Commit after each milestone with renders in `out/` and an entry in `LOG.md`. If M2 or M3 cannot reach its bar, finish,
report exactly what is short and why (in numbers), and still open the draft PR: a documented shortfall is a result.

## 8. Report

As 01 §9, plus: the block moves (old → new transform per block), the tactic and what it bought in numbers (open links,
segments below class, thin links, clearance items, pair lengths, DRC) compared with experiment 01's final table, the
DFM table's summary, and what you would do next.
