# REPORT — layout experiment 1.a (fit everything at the proper widths by moving blocks, then a JLCPCB DFM sweep)

*Branch `experiment/fable-layout-01a`, 2026-10-08. Never merge. QE: round 1 CHANGES REQUESTED, round 2 APPROVED WITH NITS, round 3
CHANGES REQUESTED (fixed below), round 4 requested. Session 1 ran M0–M2 and stopped on Nick's instruction; session 2
brought **M2 to its bar** (QE round 2: APPROVED WITH NITS, `qe/S7b_01a_round2.md`); **session 2.b** (this report) did Nick's
wind-down list (LESSONS §3/§4) in order: JLCPCB's limits fetched and encoded first (**M3**, `DFM.md`), the board grown to
**49 × 68**, the inserts moved, U1 in the centre of the band tried against U1 in the pocket through M2 on scratch copies (OPTIONS
addendum), the router made to emit 45° runs as single segments with a pair-length margin, the SPI routed first on a reserved
Internal 2 lane, the cut jumpers on top at the north edge, then a rebuild from M0 with every check, the renders and the review
pages. Everything here was produced by the scripts in `tools/` (`tools/build_all.sh`, `VARIANT=pocket` by default); the numbers
are read from `out/m4/summary.json` and the check outputs in `out/m4/`, `out/m5/`, not typed in. Board frame: KiCad coordinates =
the brief's frame (Pi NW corner (0, 0), mm). The session-2.b record is LOG.md "Session 2.b"; the design review is
`out/review/index.html`, the before / after page `out/before_after/index.html`.*

## 1. Result in one paragraph

The board is **49 × 68 mm** (x −10.5 … 38.5, y 0 … 68; the width went west, the height south into the band between the inductor
envelopes, which is 11 mm now), the inserts 1.5 mm nearer the west wall, the port-1 side 2.5–3 mm south. **U1 stays in the west
pocket** (3 mm taller than before): the centre of the band, Nick's preferred answer, was tried first in eight routed trials and
cannot meet the pairs' bar with this pair emitter (§3, OPTIONS addendum A3: 9.7–10.0 mm for port 1 at the rotation that faces
the SPI toward J1; 19–47 mm at the mote's own rotation, where the swap figure finds no straight run). The routing is complete at
the brief's widths and clearances: **0 open links but J1's no-connect pair, 0 new segments below their class width, 0 links at
0.15 mm beyond a pad field, 0 class-clearance items**, the Kelvin links pad-to-pad by tracks, **all four pair legs within the
mote's length (9.39 / 8.77 / 19.93 / 20.61 mm vs 9.5 / 9.5 / 21.3 / 21.3)**, checked on the board for P–N clearance (0.15 mm), their
45° runs single segments (**15 / 15 / 24 / 24 segments per leg**, session 2: 25 / 25 / 40 / 40). The SPI goes from U1 straight east
to J1 on its Internal 2 lane, routed first: **31 / 32 / 38 / 39 mm** of new track (session 2: 66.5 / 67.6 down the west edge). DRC:
**109 errors, all Sofar-copied features with a reason each, 0 of new copper; 68 warnings**, none a copper defect. **DFM: 30 of 31
rows pass** against JLCPCB's published limits, the one fail declared (the 0.23–0.24 mm pads of U6, U2, U3 and U11, per footprint).
**No new via sits in a solder pad** (QE round 3 F1: the router forbids it; DFM row 30 is measured). After the first rebuild Nick
asked for two more changes from the renders (OPTIONS A6): the fitted **20 W inductors' courtyards + 2 mm are the keep-out**, not the
50 W envelope (the band is 12.9 mm), and **U1 is 3 mm further from the west edge** (8.8 mm; Sofar's ~{ADIN_INT} via is inside the
board again, no hand via). 138 footprints, every §3 position within 0.001 mm, `check_fixed.py` 0 failures, blockcheck 0 missing /
128 trimmed (listed), 0 of Sofar's pad-to-pad paths cut. Board md5 3a4dbf328b93efb1f5d06ab63fe45648.

## 2. Final board size and stack

**49 × 68 mm** (Nick, 2026-10-08: 3 mm wider, 3 mm taller; supersedes the brief's 2 mm south allowance), r 3 corners. Six copper
layers in the mote's order with **JLCPCB's JLC06161H-3313 stackup** written into the board (DFM.md row 21: outer 1 oz, inner
0.5 oz, 3313 / 0.55 core / 2116 / 0.55 core / 3313, 1.538 mm of material, 1.6 mm nominal). Where the 3 + 3 mm went and why:
OPTIONS addendum A1 (the first trial with the width on the east gained nothing in the strip and failed on the west).

## 3. Block moves (OPTIONS §3 + addendum, as built; `VARIANT=pocket`)

| Block | session 2: dst, rot | 2.b: dst, rot | Why |
|---|---|---|---|
| frame | 46 × 65, x −7.5 … 38.5 | **49 × 68, x −10.5 … 38.5, y 0 … 68** | A1 |
| MP3 / MP4 / MP1 / MP2 (rings) | x −1.81; y 12.0 / 21.4 / 43.6 / 53.0 | **x −6.31; y 12.0 / 21.4 / 46.1 / 55.5** | 1.5 mm nearer the wall (A2); port 1 2.5 mm south (3 put MP2 2.91 mm from H3's keep-out) |
| MTG1–4 | (−3.5, 3.5) (34.5, 3.5) (−3.5, 61.5) (34.5, 61.5) | **(−6.5, 3.5) (34.5, 3.5) (−6.5, 64.5) (34.5, 64.5)** | with the corners; the MTG/H courtyard overlaps are gone |
| inductor keep-outs | 50 W envelope 15.5 × 15.5 + 2 mm: L2 y 9.0–24.5, L1 y 36.5–52.0 | **the SRF1260's courtyard 13.1 × 13.6 + 2 mm: L2 (6.19, 9.95, 19.29, 23.55), L1 (6.19, 40.45, 19.29, 54.05)**; L1 (12.74, 47.25) | Nick, 2026-10-08: only the 20 W inductors for this board (OPTIONS A6); L1's centre 3 mm south: the band y 25.55 … 38.45 |
| ADIN | (−1.7, 32.5), 90° | **(−1.7, 33.75), 90°** | 8.8 mm from the new west edge (Nick: "too close to the edge, move it east"); centred in the taller pocket (26.2 … 41.3); the mote's full region (107.5), Sofar's ~{ADIN_INT} via at x −7.2 is inside: no hand via |
| P1T (T1, C16, C18) | (6.7, 28.4) | **(6.7, 29.45)** | session 2's relation to U1 but 0.2 mm north: at the exact relation BM1_DATA_P came out 9.59 (trial 3) |
| P1C (C19, R14) | in P1T | **(8.95, 26.05)** | the mote's spot relative to T1, as its own rigid piece (the split exists for the centre variant) |
| P2T | (13.7, 32.5), 180° | **(13.7, 33.75), 180°** | session 2's relation to U1 |
| B18 | (19.0, 31.4), 90° | **(19.0, 32.9), 90°** | with U1's latitude |
| DAMP1 / D1 / R11 / TP36 / FID5 / FID6 / J5 | y 57.5 / 59.0 / 58.0 / 62.3 / 55.6 / 55.6 / 61.8 | **+3.0 mm** | with the south band |
| JP1 | (32.05, 9.45) top, strip's north end | **(20.4, 2.2) top, north band** | Nick: on top at an edge, no tall part beside (A4) |
| JP2 | (15.0, 4.3) bottom under the LEDs | **(12.5, 5.2) top, north band** | same |
| D10 / D8 / D9 | (11.6 / 15.0 / 18.4, 1.4) | **(8.1 / 11.5 / 14.9, 1.4)** | room for JP1 at the band's east end |
| R46 / R44 / R45 | (10.8 / 18.0 / 19.4, 4.2) bottom | **(8.1 / 11.5 / 14.9, 3.0) bottom** | under their LEDs |
| FID3 / FID4 (top), FID1 / FID2 (bottom) | (21.5 / 8.0, 2.5) | **(17.0, 5.3) / (7.8, 5.0)** | JLCPCB: pad edge ≥ 3.35 mm from the edge (DFM row 26) |
| R43 / TP8 | (7.5 / 9.8, 36.3) bottom | **(7.5 / 9.8, 37.8) bottom** | with U1's latitude |
| B5V, B33, DAMP3, DAMP2, SENSE, P2L, U11 cell, C56–C58, TP20/24/38, R26/R27, R15/R16, C26, the Pi holes, J1 | unchanged | unchanged | |

## 4. Planes and routing

- Planes as session 2, parametrised by the frame: the GND plane's slots around each inductor island follow the envelopes
  (port 1's are 3 mm south), the VBUS / P_IN / 3V3 islands and the 5V_PI pour and patch reach the new edges, the inner planes
  keep **0.3 mm** from holes (JLCPCB's inner PTH-to-copper, DFM row 12; was 0.25: 7 DRC items at the M3 housing holes), the outer
  pours drop islands that hold no via (the bottom GND island under C58 / TP38 of session 2 is gone). Bus feeds 1.5 mm on Top from
  3.31 mm east of each insert centre to its inductor pad (3.0 put the track's round end 0.05 mm from the Ø4.4 hole, DFM row 13).
- **Order** (Nick, LESSONS §3/§4): the **SPI first** (SCK, MOSI, MISO, ~{CS}; Internal 2 at cost 1.0, Internal 1 at 1.5, Top only
  for the pin escape, Bottom forbidden), then the regulators' fan-out vias (anywhere but the pairs' exit lanes), the pairs, the
  bus legs, the 5 V links, the load switch, the pocket's other nets (~{INT}, ~{RST}, 3V3, 1V8, ADIN_PWR), the LED nets, the rest,
  stitching, zone vias. New track: SPI 31.3 / 32.2 / 37.5 / 39.1; ~{INT} 36.8; ~{RST} 26.1; 1V8 23.8; ADIN_PWR 40.6; PI_5V 11.2; the LED
  nets 40.7 / 35.7; VBUS_OUT 23.2; I²C 24.5 / 17.4 mm. 36 stitching vias, 265 vias in all.
- **No via in a solder pad** (QE round 3 F1): `router.Grid.padvia` forbids a new via wherever its copper would touch an SMD pad
  (test pads and thermal pads > 4 mm² excepted); the 64 stitching / escape vias that sat in pads at 03b2adb are beside them now.
  With the via beside the pad, a plane net's link from a pad narrower than 1.0 mm runs at 0.2 mm (BRIEF §6: "small decoupling
  stubs keep the mote's 0.2 mm"; `m4_route.small_stub_class`): 6 such stubs on VBUS (C20.1, C49.1, R15.2, R16.2, R41.1, U11.1;
  0.3–0.9 mm each, ≤ 2 mm per pad), counted and listed by `check_rules.py`, their clearance the rail class's 0.15 as DRC checks it.
- **Pairs** as session 2 (coupled, Top + Internal 1, the mote's geometry, checked on the board) plus: every candidate's 45° runs
  are straightened (`Grid.straighten`: a staircase sub-run becomes one orthogonal + one 45° segment when the new cells are free on
  the A*'s own maps; the figures' runs stay), and `PAIR_MARGIN` 0.3 mm prefers a candidate under the limit by that much (QE N2).
  Port 1: two vias straight out of the pins (1.0 / 1.53 mm), Internal 1, one swap, Top into T1; port 2: Top, one swap, Top.
  **9.39 / 8.77 / 20.19 / 20.87 mm**; the blank-board tests (18) and the real-board test pass (`tools/test_pair.py`: "ALL OK",
  min clearance to other nets 0.175).
- **The 5 V path** (JP1 in the north band): L6 → JP1 across J1's north end on an inner layer, JP1 → J1 pins 2 / 4; 5V_PI ≈ 22 mm +
  PI_5V 11.2 mm of 1.0 mm track (≈ 35 mV at 1 A, OPTIONS A4).

## 5. DRC summary (kicad-cli, `--schematic-parity --severity-all`, `out/m4/drc_summary.txt`)

| Item | Count | Status |
|---|---|---|
| errors | **109** | **all** Sofar-copied features in the exclusion table (`out/m5/drc_exclusions.md`): insert contact 76 (shorting 28, hole clearance 36, mask 8, padstack 4), transformer footprint 22 (clearance 6, shorting 6, mask 10), courtyards 10 (Sofar's intra-block pairs; the 2 MTG/H pairs of session 2 are gone), the P1L BM1_N stub vs Sofar's GND via 1; **0 of new copper, 0 without a reason** |
| unconnected | **1** | J1 pins 1/17 (by design, SPEC 4) |
| schematic parity | 4 | MP1–MP4 "no pad for pin 1" (Sofar Q6) |
| warnings | **68** | lib_footprint_mismatch 28 (the silk edits of `tools/dfm_fix.py` live on the board's footprint copies, so they differ from the library: expected; a KiCad "Update Footprints from Library" would undo them, QE round 3 N4), padstack 38 (Sofar's imported footprints), silk_overlap 2 (Sofar's rigid-block silk); **0 track_dangling, 0 via_dangling, 0 silk_over_copper, 0 text_height / text_thickness** (session 2: 254 warnings, 112 of them text_height) |

## 6. Pass criteria of BRIEF 1.a §5 and §7 M2 / M3

| # | Criterion | Result |
|---|---|---|
| 1 | DRC: 0 errors of new copper, 0 unconnected but J1's pair, exclusions with reasons | **Pass with the table**: 109 errors, 109 with reasons (all Sofar's); 1 unconnected (by design); 4 parity (Q6) |
| 2 | §3 positions ±0.05; J1 pin 1 at (25.23, 8.37) from the top | **Pass** (`check_fixed.py` 0 failures, no allowance) |
| 3 | §4 keep-outs, 2 mm around both envelopes, bottom ≤ 3 mm | **Pass** |
| 4 | blockcheck 100 % | **Pass with trimming declared**: 0 missing, 128 trimmed (dead-end lead-outs, listed), 0 of Sofar's pad-to-pad paths cut |
| 5 | §5 widths on new routing; pairs no longer than the mote's; R8 sense by track; rings identical | **Pass**: 0 below class, 0 thin links, 0 clearance items (6 small-pad 0.2 mm stubs on VBUS per BRIEF §6, listed); 4 of 4 pairs within, P–N 0.15; Kelvin yes / yes; rings 100 % |
| 6 | M3: every `DFM.md` row pass or fail with a reason; §5 still holds | **30 pass, 1 fail with a reason** (row 29: pads under 0.25 on U6 0.23, U2 / U3 0.235 (Sofar's footprints) and U11 0.24 (KiCad's stock DRC0010J, this design's part); Nick's call per part); row 30 measured: 0 new vias in solder pads; §5 holds (row 5 of this table is on the M3 board) |
| 7 | Renders | **Pass**: `out/m4/render_*.png`, `out/m4/layers/*.svg`, `out/review/`, `out/before_after/` |

## 7. What the tactic bought (vs experiment 01, session 1 and session 2)

| Measure | 01 | 1.a session 2 (b22752f) | **1.a session 2.b** |
|---|---|---|---|
| board | 46 × 65 | 46 × 65 | **49 × 68** |
| open links (besides J1's pair) | 0 | 0 | **0** |
| new segments below class / thin links / clearance items | 10 / 13 / 1 | 0 / 0 / 0 | **0 / 0 / 0** |
| DRC errors of new copper / without a reason | 1 | 0 / 0 | **0 / 0** |
| DRC warnings | 258 | 254 | **68** |
| pairs (mm) | 9.4 / 7.9 / 21.3 / **23.4** | 9.46 / 8.80 / 17.98 / 18.62 | **9.39 / 8.77 / 20.19 / 20.87** |
| pair legs, segments | ? | 25 / 25 / 40 / 40 (staircases) | **15 / 15 / 24 / 24** |
| SPI new track (SCK / MOSI / MISO / ~CS) | 32–48 | — / — / 66.5 / 67.6 (west-edge detour) | **31.3 / 32.2 / 37.5 / 39.1**, Internal 2 lane, first |
| new vias in solder pads | ? | 64 (found by QE round 3) | **0** (the router forbids it; measured) |
| inductor keep-out | 50 W envelope | 50 W envelope | **the fitted 20 W inductor + 2 mm** (Nick) |
| U1 from the west edge | 5.8 | 5.8 | **8.8 mm** (Nick) |
| JP1 / JP2 | bottom / bottom | top (strip, beside L6) / bottom | **top / top, north edge, nothing tall beside** |
| JLCPCB limits in the design rules; DFM table | no | no | **yes: 31 rows, 30 pass** |
| stackup | generic | generic | **JLC06161H-3313** |
| silk at JLC's legend limits | no | no | **yes** (59 lines, 128 references; 37 hidden, listed in `out/m2/dfm_fix.json`) |
| fiducials ≥ 3.35 mm from the edge | — | 2.12 | **≥ 3.35** |
| U1 | pocket | pocket | pocket (**centre tried, 8 trials: OPTIONS A3**) |
| grid build / routing run | 268 s / 390 s | 17 s / ≈ 330 s | 17 s / 184 s |

## 8. The DFM table (`DFM.md`, summary)

31 rows, each with JLCPCB's limit quoted, its URL and the date read (2026-10-08), how it is enforced (`.kicad_pro` design rules,
`.kicad_dru` rules, or `tools/dfm.py`'s own measurement where DRC cannot express it), the board's measured worst case with where,
pass / fail, and what 2.b changed. **30 pass.** The fail: row 29, min SMD pad 0.25 — every footprint under it is listed: U6's
TPS62840 DSBGA 0.23 (Sofar's), U2 / U3's AP22913 WLCSP 0.235 (Sofar's), U11's Texas_DRC0010J 0.24 (KiCad stock, this design's part);
a footprint change is Nick's per part (QE round 3 F2). Row 30 (via in pad) is measured against the mote's copied vias: 34 vias
touch an SMD pad — Sofar's 16, in test pads 10, in thermal pads 8 — and **0 new ones in a solder pad** (03b2adb had 64: QE round 3
F1; the router forbids them now). Declared within passing rows: the 10 courtyard overlaps and 6 test-point overlaps inside Sofar's
copied blocks; the 0.75 mm fiducial copper (JLC says ≈ 1.0 is common; mask 2.25 ≥ 2×). Not done: a top-side GND pour (judged: the pairs'
and the bus feeds' clearances come first; the bottom pour and the two planes carry the GND; copper balance Top 25 % / Bottom 77 %
is reported, JLC reviews balance at order time), impedance (no published figure to meet: the 10BASE-T1L MDI pairs are 0.2 / 0.2 mm
over the In2 GND plane 0.665 mm below Top on this stackup; to be checked in JLC's calculator if Nick wants a number).

## 9. Declared items (for Nick)

| # | Item | Numbers | Why |
|---|---|---|---|
| 1 | U1 in the pocket, not the centre | centre trials: port 1 9.69 / 10.04 / fail / fail / 21.7 mm; port 2 13.2 / 13.8 / fail / 39.7 / 46.9 | OPTIONS A3: the pair emitter needs 2 mm of straight run for its swap figure; the next step is a body-side pad entry (Sofar's figure) |
| 2 | BM1_DATA_P's margin | 9.39 vs 9.5: 0.11 (the 0.3 mm margin rule found no candidate with more) | a rerun is not byte-identical |
| 3 | 37 references hidden | listed in `out/m2/dfm_fix.json` (0402 / 0603 passives, test points, U3, U6, Y1, the LEDs D8–D10) | no clear spot for a 1.0 mm text within 1.5 mm of their courtyard |
| 3b | 6 small-pad 0.2 mm stubs on VBUS | C20.1, C49.1, R15.2, R16.2, R41.1, U11.1: 0.3–0.9 mm each | BRIEF §6's "small decoupling stubs keep the mote's 0.2 mm"; with no via allowed in the pad, a 0.5 mm track from an 0402 pad in the strip's bottom had no room (R41.1 was open) |
| 3c | lib_footprint_mismatch 28 | the silk edits are on the board's footprint copies | a KiCad "Update Footprints from Library" would undo them (QE round 3 N4): do not run it on this experiment board, or move the edits into the experiment's library copies |
| 4 | U2.B2 / U3.A2 fan-out | no via spot within 1.7 mm; routed afterwards (connected) | as session 2 |
| 5 | Q7 (exclusion keys) | not attempted | the table is for Nick to apply in KiCad |
| 6 | DFM row 29 | pads under 0.25: U6 0.23, U2 / U3 0.235 (Sofar's), U11 0.24 (stock KiCad) | Nick's call per part |
| 7 | The 5 V path | ≈ 33 mm of 1.0 mm track, ≈ 35 mV at 1 A | the jumpers at the north edge (Nick) |

Carried from session 2: the 2 mm envelope clearance applied to top-side parts (bottom parts under the inductors as Sofar placed
them, OPTIONS Q4); J5 stays the JST GH; Sofar's T1/T2 pads 6/7 at 0.24 mm; the insert contact as drawn; Sofar's 2.0 mm BM1_N stub
0.31 mm from Sofar's GND via; three of Sofar's GND pad links made by the pours (QE round 2 N1).

## 10. What I would do next (in order)

1. QE round 3 of this state; Nick's design review (`out/review/index.html`, `out/before_after/index.html`).
2. The centre placement (`VARIANT=centre`): a pair emitter that enters the transformer pads from the body side through a staggered
   via pair (the swap happens in the layer change, no straight run needed), then rerun trial 5's placement; the SPI would be 10–14 mm.
3. Nick's J5-west / L1-south variant (`J5WEST=1`, OPTIONS A3) once the centre routes.
4. A top GND pour with stitching, measured against the pairs' P–N and the bus feeds; JLC's impedance calculator for the pairs.
5. Q7 once more (marker positions from a pcbnew-saved copy).
