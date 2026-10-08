# QE review — PR #30 (S7.b, experiment, do not merge) — 2026-10-08, round 1

*Received from the S7 QE session (session message to the design session). Saved here rather than in
`docs/design-review/qe/S7.md` because this branch writes only `experiments/fable_layout_01/` (BRIEF rule 1); the sprint
file on main gets a pointer when S7.b closes.*

**Verdict:** CHANGES REQUESTED (for the report and two M5 board regressions; the PR itself is never merged)
**Reviewed:** 5c12705 vs base a5f812c, from a `git archive` copy in my scratchpad. Fresh kicad-cli 9.0.6 DRC, my own pcbnew checks, a DRC of the mote for comparison, your blockcheck/check_fixed/check_rules re-run on the copy, and a full `tools/build_all.sh` rebuild on a separate scratch copy. Nothing run in your worktree (its board md5 26a3e18… is unchanged).

## Claims checked
| Claim | Result | Evidence |
|---|---|---|
| Only experiments/fable_layout_01/ written | ✓ | `git diff --name-only a5f812c...5c12705` has nothing outside it |
| Schematic copy identical to the live project (no J5 edit) | ✓ | cmp: all 7 .kicad_sch, both .kicad_sym, sym/fp-lib-table, mote.pretty, nereus.pretty identical to a5f812c. The .kicad_pro differs only in design rules (Default clearance 0.2→0.15, min track 0.15, min via 0.45 / drill 0.2; "All Nets" class dropped); DRC severities identical to live |
| 138 footprints, 46 × 65, H1–H4 board-only | ✓ | pcbnew: 138, board-only [H1–H4], edge bbox −7.55…38.55 × −0.05…65.05 (0.1 line) |
| DRC 110 errors / 2 unconnected / 4 parity | ✓ | fresh JSON: clearance 6, courtyards 12, hole_clearance 36, padstack_invalid 4, shorting 34, mask_bridge 18 = 110; unconnected 2; parity 4 = MP1–4 "No pad found for pin 1" |
| Every error is a listed Sofar feature; none from new copper | ✓ | Listed all 110 by item: 76 involve MP1–4 (ring pad, NPTH, ring vias, arc); 22 involve T1/T2's unnumbered pads (the two "copied vias" at (13.00/15.05, 30.85) match mote vias NetC24_1/2 at 0.0004 mm); 12 courtyards (10 pairs each inside one block, 2 MTG/H). Mote DRC also has exactly 34 shorting_items. Zone fills are current (pcbnew refill changes 0 of 13 zones; DRC identical after) |
| Unconnected = U3 3V3 + J1 1/17 | ✓ (location ✗, F4) | DRC: 3V3 track (−4.85, 38.65) B.Cu ↔ (19.93, 43.55); J1 pads 1/17 on `unconnected-(J1-3V3-Pad1)` |
| Blocks: translate + 90° rotations, same side, 0 missing | ✓ | blockcheck re-run byte-identical to out/m3/blockcheck.md, total missing 0. My check: 87 block parts, 0 side mismatches, 0 rotation anomalies vs mote |
| "1,064 items, 385 pads, 0 extra" (REPORT §1, §9.4) | ✗ | F3 |
| §3 positions, J1 pins 1/2/39/40 from the top, rings | ✓ | check_fixed re-run: 0 failures; J1 pin 1 (25.230, 8.370) on B.Cu; rings 1 arc + 7 vias on the right nets |
| U1 1.79 mm allowance; bottom parts under envelopes | ✓ presented honestly | check_fixed prints it as "ALLOWED deviation"; both in REPORT §6 #2/#3, §9 #3, §10 Q1/Q2. Bottom parts ≤ 1.5 mm (heights.json sourced per footprint; MP inserts 1.5 tallest) |
| §4 keep-outs (parts) | ✓ | check_fixed (courtyards only) |
| §4 keep-outs (copper) | ✗ one item | F6. Pi holes: outer layers clear within r 3.0; In2/In4 planes reach 1.6 mm from H centres (0.25 from the hole wall) |
| rules.md: widths, 3 clearance items, pairs 3/4 | ✓ (re-run identical) / reporting gaps F5, N1, N2 | Pairs: BM1_P 9.40 (2 vias), BM1_N 7.90 (0), BM2_P 21.30 (0), BM2_N 23.80 (2), all 0.15 mm |
| R8 sense + rings identical | ✓ | SENSE 75/75 tracks matched; rings via check_fixed |
| Renders | ✓ | out/m5/mote_layers and shield_layers, 6 SVGs each, all parse; render_top/bottom.png 1992² |
| Rebuildable with tools/build_all.sh | ✓ (equivalent, not identical) | Scratch rebuild (3 min): DRC counts and unconnected identical; pairs 7.9/9.4/21.3/23.8; check_fixed 0 failures; segments 2023 vs committed 1944 (N4) |

## Findings
| # | Severity | Finding | Evidence | Suggested fix |
|---|---|---|---|---|
| F1 | **MAJOR** (undeclared) | REPORT §5 calls the ~350 warnings "silk over copper / overlaps and text sizes from the import, not reviewed". 90 of them are copper defects of this layout; the mote has 0 / 0 / 1 / 5 of these types. **hole_to_hole 14:** via pairs 0.10–0.43 mm apart with 0.2–0.3 mm drills, i.e. overlapping drills, e.g. GND (−3.30, 34.70)/(−3.40, 34.80), PAYLOAD_EN (36.50, 52.30)/(36.30, 52.10), 3V3 (20.10, 43.40)/(19.80, 43.50). **holes_co_located 3:** duplicate vias at (35.50, 52.90) ~{PAYLOAD_FAULT}, (1.10, 30.80) and (10.40, 55.20) GND. **via_dangling 23:** 20 GND stitching vias reach only one layer (e.g. a column at x 15.96, y 11.3–13.7), plus BM1_P (9.49, 38.65), 2 VBUS, 1 5V_PI. **track_dangling 50 (52 mm total):** bus-net stubs: the clipped copies of Sofar's 0.2 mm L4 data legs, BM1_P/BM1_N 6.73/6.82 mm on Internal 2 ending at x 18.99, y 44.1/44.45, and BM2_P/BM2_N 5.64/5.50 mm ending at (17.46, 16.4/16.8); a **2.0 mm × 4.54 mm BM2_N stub on Top** (5.96…10.51, 18.98), port 2's twin of the BM1_N stub §3 says was not copied (visible left of L2 in render_top.png); 1.5 mm BM1_P feed fragment (18.64, 38.42); 0.5 mm P_IN stub (16.32…17.46, 20.10); SPI/RST stubs at the ADIN west edge | fresh DRC JSON; mote DRC comparison; pcbnew lookup by UUID | Delete the duplicate vias, merge or space the hole_to_hole pairs to ≥ 0.25 mm, remove dangling vias and stubs (or trim clipped block stubs at copy time). Re-word §5 with the warning breakdown by type, and add a §9 line |
| F2 | **MAJOR** (undeclared, M5 regression) | M5's "planes keep 0.35 mm from everything" closed the plane between J1's pins. In M4 (0.25) GND (In2) and VBUS (In4) ran between the pins down both columns; in M5 neither plane crosses J1 between y 7.2 and 57.9. The header is a ~50 mm wall through both planes, so the east strip (U5/U10 bucks, U11, 5V_PI, 3V3 island) joins GND and VBUS only around J1's two ends. GND In2 is 1 main island + 15 slivers (2.1 mm² each) between the columns. Contradicts §4's "near-solid" GND; the brief's 0.35 is the bus class only (power 0.25) | Sampled the main island along x = 25.23 and 27.77 every 0.02 mm, y 7–58: M4 345/350 points in copper, M5 9/17 (ends only). Zone clearance 0.25 at c5e4f8d → 0.35 at 5c12705 | Planes 0.25 (or 0.2) from non-bus items and 0.35 from BM nets only (netclass or custom rule); refill and re-check that the planes pass between J1's pins. Mention in §4/§6 |
| F3 | MINOR | REPORT §1/§9.4 and LOG M3 say "1,064 copper items and 385 pads, **0 missing, 0 extra**". Those are M3's numbers; blocks.json changed in M4. The committed out/m3/blockcheck.md (and my fresh re-run) gives pads 242, tracks 742, arcs 4, vias 176, zones 6 (928 copper items) and **228 extra**: ADIN 120, P1L 13, P1T 10, P2L 20, P2T 15, B33 2, B5V 24, SENSE 11, DAMP1 1, DAMP2 2, B18 10 | blockcheck.md (fresh == committed) | Quote the current totals; "0 missing" stands; say what "extra" is (new routing in block regions) |
| F4 | MINOR | The U3 3V3 open item is mislocated. §4 says the hand-laid escape is "on Internal 2", and §7 says it "reaches (2.5, 38.0) on Internal 2" and gives a fix from there. Actually it runs U3.A2 → B.Cu → via (−5.50, 38.65) → Top 0.381 mm to (−5.87, 37.92…38.80) at the west wall. There is no 3V3 copper within 3 mm of (2.5, 38.0) on any layer (Internal 2 there carries ~{ADIN_CS} at y 37.8–38.0 and 1V8 at y 38.4–38.8) | pcbnew; DRC unconnected item | Correct §4/§7 and the fix recipe (Nick should start from the via at (−5.5, 38.65)) |
| F5 | MINOR | 4 payload VBUS_OUT segments are 0.3 mm (class 0.6) at U11's output: Top (34.2, 51.1→52.8) and the jog to (34.1, 53.0), B.Cu (34.2, 51.0→51.1). They are among rules.md's 28, but REPORT §6 #10 names only 5V_PI and VBUS, and §9 #5 says "payload 0.6". Also a 0.15 mm VBUS link (31.1, 53.1→52.55) into U11 pin 1 | rules.md table (payload 0.3 × 4); pcbnew | Declare in §6 #10 / §9 #5, or widen |
| F6 | MINOR | A 1V8 track on B.Cu comes 4.7 mm from MP1's centre, inside the brief's "no other-net copper within r 4.8, any layer". check_fixed tests part courtyards only, and the r 4.8 rule areas are "no pour" only (tracks allowed), so §9 #3's "holes/inserts clear" wasn't proven for copper | My copper scan; all other insert approaches are planes at exactly 4.80 | Move the track, or add copper to check_fixed and declare it |
| N1 | NIT | BRIEF §6 (S7.a round 2): pairs "layers as the mote (L1 + L2, two vias each)". BM1_DATA_N and BM2_DATA_P are Top-only with 0 vias; rules.md's "ok" ignores layers/vias | rules.md table | Declare (fewer vias is no electrical loss) |
| N2 | NIT | rules.md exempts every 0.15 mm segment as "fan-out allowance", but routing.json notes whole links routed with the thin class (PAYLOAD_EN, ~{PAYLOAD_FAULT}, U11 UVLO, ~{ADIN_P2_LED1}, ADIN_MOSI, ~{ADIN_CS}; pairs already declared) | routing.json notes | Count those links as below class |
| N3 | NIT | The drc_exclusions hole_clearance reason ("arc and vias 0.23 mm from the 4.4 mm hole") fits 4 of 36. 28 are ring-pad ↔ via-hole and 4 NPTH ↔ ring pad. All are Sofar's contact, so the classification holds | DRC items | Reword |
| N4 | NIT | build_all.sh calls tools/m5_finish.py, which doesn't exist (skipped by the `[ -f ]` guard). A rebuild is DRC-equivalent but not identical (2023 vs 1944 segments), so "rebuild" ≠ "same board" | scratch rebuild | Drop the step or note the router isn't deterministic |
| N5 | NIT | Inner planes come 1.6 mm from the Pi standoff centres and 2.05 mm from the M3 centres (0.25/0.35 from the hole walls). The brief's r 3.0 / 3.5 "both sides" holds on the outer layers | copper scan | Optional: state the interpretation |

## Could not verify
- The 72 stitching-via count and the "216 → 2" history (M3/M4 outputs not re-run individually; the full rebuild ends at 2 unconnected).
- drcexclude.py's matching logic: I classified all 110 errors by hand instead.
- Note: my `drcexclude.py --help` probe ran the script in my scratch copy (it wrote to that copy's .kicad_pro and drc_exclusions.md, not to your files).

## Repo untouched
My worktree git status before: (clean) / after: (clean). Your worktree: status clean, HEAD 5c12705, board md5 unchanged. Everything ran in my scratchpad.
