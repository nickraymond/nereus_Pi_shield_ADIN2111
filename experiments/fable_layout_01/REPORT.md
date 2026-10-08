# REPORT — layout experiment 01 (Fable port of the mote layout)

*Branch `experiment/fable-layout-01`, 2026-10-07/08; revised after QE round 1 (S7.b, 2026-10-08, `qe/S7b_round1.md`). Never merge. Everything here was produced by the scripts in
`tools/` (run `tools/build_all.sh` to rebuild the board from the schematic); the numbers below are read from the
check outputs in `out/`, not typed in. Board frame: KiCad coordinates = the brief's frame (Pi NW corner (0, 0).*

## 1. Result in one paragraph

The board is built, placed and routed: 138 footprints, every §3 position within 0.001 mm, every copied block
reproduced on the mote's geometry to within 0.001 mm (blockcheck: 242/242 pads; copper pads 242/242, tracks 627/742, arcs 4/4, vias 152/176, zones 6/6; copper items 928.; **0 missing**;
139 copied items trimmed after routing because KiCad's DRC called them dangling, listed in `out/m3/blockcheck.md`;
308 "extra" items = new routing inside the block regions), planes filled, 216 open connections brought down to **1**:
J1's pins 1/17, which the schematic puts on one no-connect net and which must stay open (SPEC constraint 4). U3's
3V3 feed, open in the first M5, is connected (its escape from the ADIN pocket was never laid; QE F4). kicad-cli DRC
reports **110 errors, every one in the table of Sofar-copied features below** (insert contact, transformer footprint,
courtyards), 0 errors of the new copper's own, and **0 copper-defect warnings** (no dangling track or via, no
hole-to-hole or co-located holes; QE F1). 3 of the 4 ADIN pairs are within the mote's length, port 2's N is 2.1 mm over. The pass criteria of BRIEF §8 are scored in §9. The honest headline: the port of
Sofar's *blocks* worked very well; fitting Sofar's *arrangement* into this outline did not — the blocks had to be
split, and the ADIN pocket is the layout's weak spot.

## 2. Final board size and why

**46 × 65 mm, unchanged** (x −7.5…38.5, y 0…65, r 3 corners). Option (a) of §4 was used for U1: the ADIN block sits
in the west pocket, rotated 90°, so no growth was needed. One allowance: the ADIN block is 0.3 mm east of the brief's
pocket (U1's courtyard 1.79 mm from the L1 envelope instead of 2.0; its body 2.1 mm) because Sofar's U1 fan-out on the
west side needs 10.3 mm, not 10.0, to keep its copper 0.5 mm from the edge.

Stack: 6 copper layers in the mote's order and roles; a generic 1.6 mm build (35 µm ×6, prepreg 0.21 ×3, core 0.38
×2) written into the board file — an assumption (Sofar Q11).

## 3. Blocks: transforms and fidelity

Translate + rotate by multiples of 90° only, same side as the mote, proven by pads (`tools/blockcheck.py`,
`out/m3/blockcheck.md`). "Transform" is p' = R(rot)·(p − src) + dst with src = the anchor part's mote position.

| Block | Parts | Transform (mote mm → board mm, rotation) | Pads | Tracks | Arcs | Vias | Zones | Trimmed | Missing | Extra |
|---|---|---|---|---|---|---|---|---|---|---|
| RING_MP3 | MP1 | (176.001, 120.004) → (-1.81, 12.0), 0° | 0/0 | 0/0 | 1/1 | 7/7 | 0/0 | 0 | 0 | 0 |
| RING_MP4 | MP1 | (176.001, 120.004) → (-1.81, 21.4), 0° | 0/0 | 0/0 | 1/1 | 7/7 | 0/0 | 0 | 0 | 0 |
| RING_MP1 | MP1 | (176.001, 120.004) → (-1.81, 43.6), 0° | 0/0 | 0/0 | 1/1 | 7/7 | 0/0 | 0 | 0 | 0 |
| RING_MP2 | MP1 | (176.001, 120.004) → (-1.81, 53.0), 0° | 0/0 | 0/0 | 1/1 | 7/7 | 0/0 | 0 | 0 | 0 |
| ADIN | U1, U2, U3, Y1, C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C11, C12, C13, C14, R1, R2, R3, R4, R5, R6, TP1, TP2 | (154.001, 113.004) → (-1.4, 32.8), 90° | 103/103 | 233/267 | 0/0 | 50/50 | 2/2 | 34 | 0 | 174 |
| P1L | L1, D4, R12, R13, TP3, TP5, C17, D2 | (165.501, 108.754) → (12.74, 44.25), 90° | 16/16 | 37/48 | 0/0 | 11/19 | 0/0 | 19 | 0 | 15 |
| P1T | T1, C16, C18, C19, R14 | (161.601, 117.504) → (8.7, 28.4), 0° | 15/15 | 20/27 | 0/0 | 5/5 | 0/0 | 7 | 0 | 13 |
| P2L | L2, D5, R17, R19, TP7, TP13 | (131.679, 108.279) → (12.74, 16.75), 90° | 12/12 | 22/28 | 0/0 | 12/18 | 0/0 | 12 | 0 | 21 |
| P2T | T2, C24, C25, C27, R18 | (135.501, 117.504) → (16.0, 32.3), 180° | 15/15 | 33/34 | 0/0 | 5/6 | 0/0 | 2 | 0 | 16 |
| B33 | U5, C30, L3, C28, C29, R20, R21, R22, R23 | (140.501, 115.054) → (31.551, 17.704), 0° | 22/22 | 84/88 | 0/0 | 15/19 | 2/2 | 8 | 0 | 3 |
| B5V | U10, C55, L6, C53, C54, R39, R37, R40, R38 | (140.501, 115.054) → (31.551, 31.4), 0° | 22/22 | 85/88 | 0/0 | 14/19 | 2/2 | 8 | 0 | 26 |
| SENSE | U4, R8, R7, C15, TP22 | (146.351, 115.704) → (19.8, 15.0), 0° | 15/15 | 51/75 | 0/0 | 5/5 | 0/0 | 24 | 0 | 15 |
| DAMP3 | C23 | (146.001, 116.904) → (33.5, 40.0), 0° | 2/2 | 0/0 | 0/0 | 0/0 | 0/0 | 0 | 0 | 0 |
| DAMP1 | C21, C20, TP23 | (154.201, 119.204) → (8.9, 57.5), 90° | 5/5 | 8/8 | 0/0 | 0/0 | 0/0 | 0 | 0 | 2 |
| DAMP2 | C22 | (151.301, 103.604) → (33.9, 48.2), 0° | 2/2 | 17/36 | 0/0 | 7/7 | 0/0 | 19 | 0 | 7 |
| B18 | U6, L4, C32, C33, TP21 | (144.501, 110.329) → (20.7, 47.2), 90° | 13/13 | 37/43 | 0/0 | 0/0 | 0/0 | 6 | 0 | 16 |

Blocks as the brief listed them vs what was copied:

| Brief block | What happened | Why |
|---|---|---|
| PORT1 / PORT2 | split: inductor + the bottom-side parts Sofar put under it (P1L/P2L) and the transformer cluster (P1T/P2T) | the transformer sits 9.6 mm from the inductor's centre on the mote, inside the 50 W envelope + 2 mm; the insert feeds are new routing anyway (the inserts moved) |
| SPINE | split: SENSE (R8, U4, R7, C15, TP22: Sofar's sense routing intact), DAMP1 (C21, C20, TP23), DAMP2 (C22), DAMP3 (C23); C17/D2 ride under L1, C26 moved out; D1, R15, R16 placed fresh | the mote's spine spans 22 × 21 mm across the whole board; no strip of this outline holds it |
| ADIN | whole, rotated 90°, in the west pocket | the brief's option (a) |
| BUCK3V3 | whole except C31 (B33) | with C31 the cell is 9.65 mm wide, the strip east of J1 is 8.9 |
| BUCK5V | B5V = the same cell copied again with parts mapped by function (U10, C55, L6, C53, C54, R39, R37, R40, R38) | D13; C56/C57/C58/TP38 beside it |
| BUCK1V8 | whole (B18), rotated 90°, east of L1 beside J1 | all bottom-side |
| LOAD | placed fresh around U11 (R34/R41 on the top beside it, R35 bottom) | the brief: U11 is new |
| Insert copper | Sofar's MP1 ring (arc r 3.03 × 1.2 mm, 290°, seven 0.6/0.254 vias at r 3.0) translated to each insert | §3 |

Copper **not** copied although inside a block's region: the ADIN pairs and T1/T2's pair stubs (new routing per §6),
Sofar's 2 mm BM1_N stub from L1 pad 2 toward the old insert (the inserts moved), and the big GND / VBUS / 3V3 / P_IN
planes (rebuilt on the new geometry, §4 below). **Trimmed after routing** (`tools/dangling.py`, every item recorded in
`blocks.json` "trimmed"): copper KiCad's DRC reports as dangling is shortened back to the last copper it joins (a
clipped stub keeps the part that carries a via or a pad) or deleted when nothing touches it: 24 vias deleted
(5V_PI 1, BM1_P 1, GND 20, VBUS 2: Sofar's pour-stitching vias, which had a pour on the mote and only a plane here), 84 track
segments deleted (15 mm, clipped stubs and the router's own tails), 110 shortened. Port 2's 2 mm BM2_N stub
(QE F1) is one of the shortened: it keeps the part under L2's pad 2 and Sofar's via. The ADIN_AVDD / ADIN_VDDIO islands under U1, the U5 cell's switch-node
pour, its In3 GND patch and its (clipped) 3V3 output pour were copied.

## 4. Planes and routing

- **GND (In2):** near-solid, 0.5 mm from the edge, pulled back 4.8 mm from each insert; one 0.5 mm slot on the band
  side and one on the outer side of each inductor island (x −7.5…22.7; port 2 at y 6.5–7.0 / 26.2–26.7, port 1 at
  39.0–39.5 / 54.0–54.5) so each island joins the plane only on its east, far side. Mapping of the mote's two slots:
  the mote isolates the inductor + insert region from the plane on the transformer side and joins it on the far side;
  here "far" is east, toward J1. The port-1 slot sits 2.5 mm into L1's envelope so the port-2 pair (which crosses at
  y ≈ 38) does not cross it. The plane is one island (2,134 mm²) and passes between J1's pins: along x = 26.5
  (between the two pin columns) every sampled point from y 7 to 58 is copper; along each pin column the gaps between
  the pads are copper (345 and 351 of 2,551 sample points; the rest are the pads themselves). QE F2: the first M5 had
  the planes at 0.35 mm from everything, which closed these gaps.
- **PWR (In4):** VBUS = the strip east of J1 (full height), the whole west half from y 26 down, and port 2's east
  (x 16.8–23.2); P_IN island under port 2's west/centre (x 11–16.6, y 8–25.7; R8 straddles the boundary as on the mote);
  3V3 island at the 3.3 V buck output (x 33.4–38, y 8–23); the copied ADIN islands (priority 7); Sofar's two
  unconnected islands reproduced as 6 × 6.5 mm no-net islands between each port's inserts and inductor (Q10). VBUS is
  one island (1,537 mm²) and passes between J1's pins like GND. Plane clearance 0.25 mm (power class); the four BM
  nets are in a `bus` netclass with 0.35 mm clearance in the `.kicad_pro`, which the fill and DRC honour (measured:
  0.35 to BM vias, 0.25 to the others). Inner planes stop 0.25 / 0.35 mm from the hole walls of the Pi standoffs and
  the M3 holes (QE N5): the brief's r 3.0 / 3.5 "both sides" is applied to the outer layers only.
- **5V_PI:** a bottom-side pour x 29.7–38, y 7.5–26.5 from L6 to JP1 (§6 "≥ 1.0 mm or a pour"), joined to the
  U10 cell by a 0.5 mm track where the cell's copper split it.
- **Bus feeds:** insert ring → inductor bus pad, 1.5 mm on Top, by hand (8 segments).
- **Everything else:** `tools/router.py`, a 0.1 mm grid A* on Top / Internal 1 / Internal 2 / Bottom with the brief's
  classes, per-class dilated obstacle maps, exact edge distance, fan-out at 0.15 mm where needed; GND pads stitched
  with a via within 1.2 mm; plane-net clusters stitched into their planes (66 vias, spots chosen inside the plane's
  *filled* copper deflated 0.15 mm, and never closer than 0.25 mm hole-to-hole to any other hole; QE F1). Two links
  laid by hand where the grid could not: U11 pin 7 → R34 and U11 pin 1 → a VBUS via. **U3's 3V3 escape** (QE F4):
  from Sofar's copied via at (−5.5, 38.65) west of U3, the router lays a 0.15 mm track on Internal 2 east to
  (2.5, 38.0) *before* the pocket's signals are routed (9.0 mm); the plane-leftovers step then joins it to the 3V3
  island by track. In the first M5 the lookup radius for that via was too small, so the escape was never laid — the
  "(2.5, 38.0) on Internal 2" of the old §7 did not exist; the QE's reading of the board was right.

## 5. DRC summary (kicad-cli, `--schematic-parity --severity-all`)

| Item | Count | Status |
|---|---|---|
| errors | 110 | all in the exclusion table below (0 from the new copper) |
| unconnected | 1 | J1 pins 1/17 on one no-connect net (must stay open, SPEC 4) |
| schematic parity | 4 | MP1–MP4 "no pad for pin 1": Sofar's insert footprint has no numbered pad (Q6) |
| courtyard overlaps | 12 | in the table |
| warnings | 258 | text_height 112, silk_over_copper 46, silk_overlap 44, padstack 38, lib_footprint_mismatch 8, silk_edge_clearance 4, text_thickness 4, nonmirrored_text_on_back_layer 2 — silk and text from the imported footprints, not reviewed. **Copper-defect warnings: 0** (track_dangling, via_dangling, hole_to_hole, holes_co_located; the first M5 had 50 / 23 / 14 / 3, QE F1) |

kicad-cli could not be given the exclusions: KiCad stores them keyed by the marker position, which the CLI's JSON
report does not contain (keys built from the items' positions are ignored; tested). They are therefore a reviewed
table, generated by `tools/drcexclude.py` from the table of reasons in the script, for Nick to apply in KiCad's DRC
dialog:


| Type | # | Reason |
|---|---|---|
| clearance | 2 | Sofar's transformer footprint: the copied vias of pads 3/4's nets sit beside the unnumbered no-net pads, as on the mote |
| clearance | 4 | Sofar's transformer footprint: two unnumbered no-net pads overlap pads 3/4 (identical on the mote board) |
| courtyards_overlap | 2 | BRIEF §3 positions: the M3 housing hole's ±4.25 mm courtyard overlaps the Pi standoff hole's courtyard by 0.25 mm (7 mm centres); screw head and standoff clear |
| courtyards_overlap | 10 | Sofar's placement inside a copied block (rigid, BRIEF rule 5); the courtyards were added in S6.c and overlap where Sofar packed parts tighter |
| hole_clearance | 36 | Sofar's insert contact copied as drawn: the ring pad vs the 7 via holes (28), the NPTH vs the ring pad (4) and the arc/vias vs the 4.4 mm hole (4), as on the mote (Sofar Q6) |
| padstack_invalid | 4 | Sofar's insert footprint (Altium import): the NPTH pad has no copper size; hole 4.4 mm (DESIGN D19/D24) |
| shorting_items | 28 | Sofar's insert contact copied as drawn (BRIEF §3): bus vias land in the insert's net-less ring pad (Sofar Q6) |
| shorting_items | 6 | Sofar's transformer footprint: tracks to pads 3/4 cross the unnumbered no-net pads, as on the mote |
| solder_mask_bridge | 8 | Sofar's insert contact copied as drawn: the ring pad's mask opening spans the bus vias (Sofar Q6) |
| solder_mask_bridge | 10 | Sofar's transformer footprint: the unnumbered no-net pads' mask openings touch pads 3/4, as on the mote |

kicad-cli DRC: 110 errors, 110 with a reason above, 0 without; 1 unconnected, 4 parity items (the 4 parity items are MP1–4 pin 1, Sofar Q6).


## 6. Deviations from the mote and the brief, and why

| # | Deviation | Why |
|---|---|---|
| 1 | Blocks split as in §3 | the fixed items leave three strips (8.9 mm east of J1, the 8 mm band, the 10 mm pocket); no whole block but ADIN fits |
| 2 | 2 mm envelope clearance applied to top-side parts only; bottom-side parts sit under the inductors as Sofar placed them | otherwise the port blocks could not be copied at all; the 50 W part is a top-side volume (for Nick to confirm) |
| 3 | ADIN block 0.3 mm east of the pocket (U1 courtyard 1.79 mm from the L1 envelope) | Sofar's U1 west fan-out |
| 4 | J5 stays the JST GH (no Molex, no schematic edit) | Nick, 2026-10-07 |
| 5 | JP1 on the bottom beside J1 pins 2/4 | no top-side room left in the strip; cut it before stacking |
| 6 | R35 on the bottom (south-west), R34/R41 on the top beside U11, R15 beside C22, C26 moved out of port 2 | fresh placements, moved to free U11's pins and the strip's bottom |
| 7 | LEDs in a column at the band's east end (x 21.5), not on the west wall | the pocket holds U1 (brief: "the LEDs move") |
| 8 | ADIN pair BM2_DATA_N 23.4 mm vs the mote's 21.3 (BM2_DATA_P 21.3, BM1 7.9 / 9.4 within) | the pair leaves U1's south pins and reaches T2 around U1's south-east; P took the inner lane |
| 9 | Pair tracks 0.15 mm (fan-out class) along their length, routed independently (not as a coupled pair); BM1_DATA_N and BM2_DATA_P run on Top only with 0 vias, the other two Top + Internal 1 with 2 vias as the mote (QE N1) | the router has no pair mode; fewer vias is no electrical loss |
| 10 | 25 new segments narrower than their class (`out/m5/rules.md`): 5V_PI links of 0.5 / 0.3 mm (pour + short links) and VBUS links of 0.3 mm (stitching links) and one 0.15 mm VBUS link into U11 pin 1, instead of ≥ 1.0 / 0.5; 4 payload (VBUS_OUT) segments of 0.3 mm at U11's output instead of 0.6 (QE F5) | fallback classes where the full width found no path |
| 11 | 6 class-clearance items on new copper below the brief's 0.35 / 0.25 (all ≥ the 0.15 default, none a DRC error): bus BM2_N vs GND on Top Layer at (4.00, 21.40); power VBUS vs Net-(U11-UVLO) on Top Layer at (30.00, 56.60); power VBUS vs Net-(U11-UVLO) on Top Layer at (30.00, 56.10); power VBUS vs Net-(U11-UVLO) on Top Layer at (31.00, 55.90); power VBUS vs ~{PAYLOAD_FAULT} on 6 Bottom Layer at (35.40, 55.30); power VBUS vs 3V3 on Internal 1 at (37.00, 21.20) | the router keeps the *new* item's class clearance, not the larger of the two classes; grid discretisation at a feed start |
| 14 | 12 links routed whole at 0.15 mm (the fan-out width) instead of their 0.2 mm class (QE N2): 3V3 9.0 mm; ADIN_MOSI 35.7 mm; BM1_DATA_N 7.9 mm; BM1_DATA_P 9.4 mm; BM2_DATA_N 23.4 mm; BM2_DATA_P 21.3 mm; ISET 2.8 mm; Net-(U11-UVLO) 4.9 mm; PAYLOAD_EN 4.9 mm; ~{ADIN_CS} 39.6 mm; ~{ADIN_P2_LED1} 34.9 mm; ~{PAYLOAD_FAULT} 5.1 mm | the thin class was the only one that found a path (the ADIN pocket, U11's west side, the pairs per #9) |
| 12 | Stitching vias everywhere instead of Sofar's via placement for GND | new geometry |
| 13 | The U1 fan-out's copied vias in the mote's DNC pads are kept as Sofar drew them | fidelity |
| 15 | 139 copied copper items trimmed after routing (§3: clipped stubs, Sofar's pour-stitching vias) | KiCad's DRC calls them dangling here; every one is listed in `out/m3/blockcheck.md` and `blocks.json` |

## 7. Open after M5

1. BM2_DATA_N 2.1 mm over the mote's length (deviation 8).
2. J1 pins 1/17 (Pi 3V3) unconnected by design.
3. The §6 declarations: narrower fallback links (#10), 6 clearance items (#11), 12 thin links (#14).

(U3's 3V3 feed, open in the first M5, is closed: §4.)

## 8. What was hard, where I guessed, what I would do with more time

Rebuilding: `tools/build_all.sh` reproduces the board DRC-for-DRC but not byte-for-byte (the router's tie-breaking
depends on Python set order; QE N4). The committed board is the output of one run of M0–M3 and the M4 step from the
M3 snapshot (`START=m4`), followed by a second pass of `tools/dangling.py` after the "delete on the second flag" rule
was added (LOG, S7.b round 1).

- Hard: fitting rigid blocks into strips 8–9 mm wide; the ADIN pocket's exits; KiCad's silent re-netting of copper
  that lands on a pad of another net (blockcheck caught every case); the grid router's conservatism against
  off-grid copied vias (fixed by inflating pre-existing copper by half a cell diagonal, which then blocks the 0.15 mm
  threading between U1's 1.27 mm thermal vias).
- Guessed / interpreted: the envelope clearance for bottom-side parts (deviation 2); the GND slot mapping (§4); the
  no-net islands' size and place; the stackup; the pull-back applied to copper of other nets only; bottom-part
  heights from datasheet maxima (`heights.json`).
- With more time: a pair-aware router (route N and P together); rip-up that targets one lane, not a region (my
  rip-up rounds thrashed); a 0.05 mm grid near fine-pitch parts; a second look at the ADIN pocket — rotating the
  block 270° (port-2 pins north) or moving the LEDs' resistors would free the south strip; silk clean-up.

## 9. Pass criteria (BRIEF §8)

| # | Criterion | Result |
|---|---|---|
| 1 | DRC: 0 errors, 0 unconnected, 0 parity (exclusions with reasons) | **Partial**: 110 errors, all in the exclusion table with reasons (not applied: CLI limitation); 1 unconnected (J1's no-connect pair, by design); 4 parity items (Q6, documented); 0 copper-defect warnings |
| 2 | §3 positions ±0.05; J1 pin 1 at (25.23, 8.37) from the top | **Pass** (`check_fixed.py`: every position within 0.001; pins 1/2/39/40 proven) |
| 3 | §4 keep-outs, 2 mm around both envelopes, bottom ≤ 3 mm | **Pass with one allowance**: U1 1.79 mm (recorded); bottom parts ≤ 1.5 mm; holes clear (parts); inserts: no other-net copper within r 4.8 on any layer (`check_fixed.py`, QE F6) |
| 4 | blockcheck 100 % | **Pass with trimming declared**: 0 missing on every block; 139 copied items trimmed after routing (listed); 308 extra = new routing in the block regions (`out/m3/blockcheck.md`) |
| 5 | §6 widths on new routing; pairs no longer than the mote's; R8 sense identical; rings identical | **Partial**: feeds 1.5 mm, payload 0.6 (4 segments 0.3), pairs 3/4 within (BM2 N +2.1 mm), 25 fallback segments narrower than their class, 12 thin links, 6 clearance items (table 6); R8/U4 and rings 100 % |
| 6 | Renders: every copper layer for mote and shield, kicad-cli top/bottom | **Pass**: `out/m5/mote_layers/`, `out/m5/shield_layers/`, `out/m5/render_top.png`, `render_bottom.png` |

## 10. Questions

**For Nick**
1. Deviation 2 (bottom parts under the envelopes) — acceptable for the 50 W part?
2. The 0.3 mm pocket allowance for U1, or should U1 sit 0.3 mm further west with Sofar's fan-out re-routed?
3. JP1 on the bottom (cut before stacking) — or drop JP1 to the top by moving C31 again?
4. Is the J1 3V3 pair's DRC item acceptable, or should the two pins be tied with a track (harmless, both are the Pi's rail)?
5. BM2_DATA_N: accept +2.1 mm, or re-route the pair by hand in KiCad?

**For Sofar** (add to `docs/SOFAR_QUESTIONS.md` if useful)
1. Q6: the insert contact — is the net-less ring pad + bus vias intentional, or should the pad carry the net?
2. Q9: R12/R13/R17/R19 across the inductor windings are copied fitted.
3. Q10: the two unconnected In4 islands — purpose? They are reproduced as floating copper here.
4. Q11: the stack-up (this board uses a generic 1.6 mm 6-layer build).
5. The GND slot past each inductor: what is it for, so the mapping in §4 can be checked?
