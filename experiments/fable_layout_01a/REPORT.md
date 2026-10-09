# REPORT — layout experiment 1.a (fit everything at the proper widths by moving blocks)

*Branch `experiment/fable-layout-01a`, 2026-10-08. Never merge. Session 1 ran M0–M2 and stopped on Nick's
instruction with M2 short of its bar (QE round 1: CHANGES REQUESTED, `qe/S7b_01a_round1.md`); session 2 took the QE's
findings and the rest of the shortfall and brought **M2 to its bar**. **M3 (the JLCPCB DFM sweep) is not started** and
M4's report is this file as it stands. Everything here was produced by the scripts in `tools/` (`tools/build_all.sh`
rebuilds the board from the schematic; `START=m4` reruns the routing from the M3 snapshot); the numbers are read from
the check outputs in `out/m4/` and `out/m5/`, not typed in. Board frame: KiCad coordinates = the brief's frame (Pi NW
corner (0, 0), mm). The session-2 record is LOG.md "M2, session 2".*

## 1. Result in one paragraph

The placement of OPTIONS §3 holds (one block definition changed: the P2T region is clipped at mote x 138.6, §3): 138
footprints, every §3 position within 0.001 mm, U1's courtyard 2.09 mm from the L1 envelope, 0 new courtyard overlaps,
the LEDs on the north edge, JP1 on top at the strip's north end, U11 facing its loads, B18 under the band's east end.
Every copied block matches the mote to 0.001 mm (blockcheck: **0 missing**, 127 copied items trimmed as dangling and
listed; 0 of the mote's pad-to-pad paths cut). The routing is complete and at the brief's widths and clearances: **0
open links but J1's no-connect pair, 0 new segments below their class width, 0 links at 0.15 mm beyond a pad field, 0
class-clearance items**, the Kelvin links pad-to-pad by tracks, **all four ADIN pair legs within the mote's length**
(9.46 / 8.80 / 17.98 / 18.62 mm vs 9.5 / 9.5 / 21.3 / 21.3) as coupled pairs with the mote's geometry, checked on the
board for P–N clearance (0.15 mm). DRC: **111 errors, all Sofar-copied features with a reason each, 0 of new copper**;
0 copper-defect warnings. What remains is declared in §6: one bottom GND pour island without a via, Q7 (exclusion
keys) as a table, and M3 not started.

*The first version of this report (session 1, commit 293dc11) said 115 Sofar + 12 new DRC errors; QE round 1 found
both pairs shorted P–N at the transformer pads and hidden by `tools/drcexclude.py`'s T1/T2 patterns: the true split
was 111 + 16 (the 11 swap-figure items, the 3V3 via vs R21.2, the 2 shorts, their 2 mask bridges). Fixed in session 2.*

## 2. Final board size

**46 × 65 mm, unchanged** (x −7.5 … 38.5, y 0 … 65, r 3 corners). No growth was needed. Stack: 6 copper layers in the
mote's order, 01's generic 1.6 mm build (M3 is to replace it with JLCPCB's stackup; not done).

## 3. Block moves (OPTIONS §3, as built)

| Block | 01: dst, rot | 1.a: dst, rot | Why |
|---|---|---|---|
| ADIN | (−1.4, 32.8), 90° | **(−1.7, 32.5), 90°**; region clipped at mote y 107.9 (west), x 148.2 (south), y 119.7 (east) | Q5 (2.0 mm restored); the south exit 0.3 mm wider; a 1V8 stub and a GND stub that collided with T1's C16 dropped. The west clip also dropped Sofar's ~{ADIN_INT} via (it lands inside the edge clearance): re-added by hand at (−6.75, 30.25), §4 |
| P1T (T1) | (8.7, 28.4), 0° | **(6.7, 28.4), 0°** | Q1; stops at the ADIN block's C8. (Session 2 tried 7.0 while the pair's approach was 1.4 mm; the 0.9 mm approach clears the crystal's via from 6.7) |
| P2T (T2) | (16.0, 32.3), 180° | **(13.7, 32.5), 180°**; region's east edge mote x 139.2 → **138.6** (session 2) | Q1; stops at P1T's C18 / its via. The clip drops Sofar's GND pour-stitching via at mote (138.751, 116.854), which serves the U5 cell's R23 on the mote and landed 0.4 mm in front of T2's data pads after the 180° rotation |
| P2L | unchanged | region clipped at mote y 112.7 | its BM2_P leg stub was 0.31 mm from SENSE's via |
| B5V | (31.551, 31.4) | **(31.551, 21.24)** | Q3/Q6: under JP1 |
| B33 | (31.551, 17.704) | **(31.551, 34.44)** | swapped with B5V |
| DAMP3 (C23) | (33.5, 40.0), 0° | **(33.5, 40.95), 90°** | rotated to 8.8 wide × 7.4 tall |
| DAMP2 (C22) | (33.9, 48.2) | **(33.5, 48.6)** | follows the stack |
| B18 | (20.7, 47.2), 90° | **(19.0, 31.4), 90°** | Q2 |
| P1L, SENSE, DAMP1, rings | unchanged | unchanged | |

Fresh parts as OPTIONS §3 with these corrections after the M0 trial: JP1 (32.35, 9.45) top; U11 (32.5, 54.35) rot
−90 top, C49 (35.7, 54.35), R34 (29.6, 55.6) rot 90; R16 is C23's resistor, not C21's, so it sits under C23 at
(37.0, 42.5) bottom; TP19 (30.6, 43.3), C58 (36.6, 14.0), TP38 (36.6, 16.3) bottom.

## 4. Planes and routing

- Planes as 01 (GND In2 with the two inductor slots, the PWR plane In4 split), the 3V3 island moved with the 3.3 V
  cell to x 33.4–38, y 24–38; the 5V_PI pour on the bottom x 29.7–38, y 7.5–24 (solid connections) **plus a 5V_PI
  patch on Internal 2 over the same rectangle** (session 2: the bottom pour's islands, cut by the dividers R37–R40,
  each get a via into the patch, as the mote carries the buck's output on a plane island); a bottom-side GND pour over
  the whole board as the mote's bottom layer, solid pad connections as Sofar's pours; the fiducials' mask apertures cut
  out of it.
- Bus feeds by hand (1.5 mm, Top), the bus legs at 0.2 mm / 0.35 from everything incl. the opposite leg, the bus rule
  in `.kicad_dru` unchanged.
- **Pairs** (session 2, `router.route_pair` / `commit_pair`, LOG §1): two 0.2 mm tracks, 0.2 mm gap, on Top +
  Internal 1, one swap figure each (the pin and pad order demand it), the layer changes at the ends as Sofar's mote
  makes them: port 1 leaves U1's pins by two vias straight out of the pins (staggered 1.0 / 1.48 mm: two 0.45 vias do
  not fit side by side at the 0.5 mm pin pitch) and reaches T1 on Top; port 2 leaves on Top and gets its via pair
  beside T2's approach. The approach to the pads is a straight lane along the pads' entry direction, the pair spreading
  to the pads' 0.65 mm pitch over 0.2 mm, finished at the pad edge. Every emitted pair is checked on the board (one
  cluster per net, P–N ≥ 0.15 on every shared layer) before it is kept. **BM1 9.46 / 8.80 mm (limit 9.5), BM2 17.98 /
  18.62 mm (limit 21.3)**; 01: 9.4 / 7.9 / 21.3 / 23.4.
- **~{ADIN_INT}**: Sofar's own fan-out, whole: U1.39 → the Top lead-out → a hand via at (−6.75, 30.25) (QE round 1 F2:
  the mote's via lands 0.08 mm inside the edge, inside the 0.5 mm edge clearance) → the Bottom lead-out → R1.1; the
  via is proven on the board (edge 0.525 mm, 0.207 mm from other-net copper). Copied items on a mote pad-to-pad path
  are now never trimmed (`blocks.json` "protected"; 0 of them dangling here).
- **Fan-out first**: U2 / U3's non-GND balls get their vias before the pairs (`m4_route.fanout`): 1V8 at (−2.9, 38.6),
  3V3 at (−4.4, 37.4); U2's ADIN_PWR ball found no spot within 1.7 mm and was routed normally. The vias sit in the
  pocket exit's south-west corner so the port-2 pair's lane (y 37.4–38.3) stays free.
- Corridors (OPTIONS §2.3) held: SPI + ~{CS} on Internal 2 under U1 to J1, ~{RST} from U1's east side, the LED nets
  north, ADIN_VDDIO to the LED block, 5V_PI on top from L6 to JP1, PI_5V to J1 pins 2/4, VBUS_OUT on Internal 2 to J5
  (0.6 mm), VBUS pre-stitched at U11 pin 1 before U11's signals, 3V3 / 1V8 / ADIN_PWR into the pocket on Internal 2
  (the bottom costs 2.0 for them, so U2's layer stays free for its balls).

## 5. DRC summary (kicad-cli, `--schematic-parity --severity-all`, `out/m4/drc_summary.txt`)

| Item | Count | Status |
|---|---|---|
| errors | **111** | **all** Sofar-copied features in the exclusion table (`out/m5/drc_exclusions.md`): insert contact 76 (shorting 28, hole clearance 36, mask 8, padstack 4), transformer footprint 22 (clearance 6, shorting 6, mask 10), courtyards 12 (10 inside copied blocks, 2 MTG/H), the P1L BM1_N stub vs Sofar's GND via 1; **0 of new copper** |
| unconnected | **1** | J1 pins 1/17 (by design, SPEC 4) |
| schematic parity | 4 | MP1–MP4 "no pad for pin 1" (Sofar Q6) |
| warnings | 254 | silk / text / padstack / lib mismatch from the imported footprints; **0 track_dangling, 0 via_dangling**, 0 hole_to_hole, 0 holes_co_located, 0 starved_thermal |

## 6. Declared items against BRIEF 1.a §5 / §7 M2 (for Nick)

| # | Item | Numbers | Why |
|---|---|---|---|
| 1 | Bottom GND pour island with no via | one island near (37.1, 13.9), under C58 / TP38 | no via of the GND class fits in it over the plane; it carries no pad, so KiCad's island removal may drop it on a refill; harmless, to be confirmed in KiCad |
| 2 | Q7 exclusion keys | not attempted | the table (`out/m5/drc_exclusions.md`) is for Nick to apply in KiCad; every one of the 111 has a reason |
| 3 | M3 DFM sweep, `DFM.md`, JLCPCB stackup | not started | session 2 stopped at M2's bar for QE round 2 and Nick's own design review (his instruction, 2026-10-08) |
| 4 | U2.B2 (ADIN_PWR) fan-out | no via spot within 1.7 mm in the allowed corner | the ball is routed (normally, after the pairs); only the "fan-out first" reservation failed for it |

Declared deviations carried from 01 that still hold: the 2 mm envelope clearance applied to top-side parts (bottom parts
under the inductors as Sofar placed them, OPTIONS Q4); J5 stays the JST GH; Sofar's T1/T2 pads 6/7 at 0.24 mm; the
insert contact as drawn; Sofar's 2.0 mm BM1_N stub 0.31 mm from Sofar's GND via (the bottom pour keeps the via that 01
trimmed). New block-copy changes in session 2: the P2T region clip (§3) and the ~{ADIN_INT} hand via (§4).

## 7. What the tactic bought (vs experiment 01's final table and session 1)

| Measure | 01 | 1.a session 1 (293dc11) | **1.a session 2** |
|---|---|---|---|
| open links (besides J1's pair) | 0 | 3 | **0** |
| new segments below class width | 10 | 0 | **0** |
| links at 0.15 mm beyond a pad field | 13 | 0 | **0** |
| class-clearance items (new copper) | 1 | 6 | **0** |
| DRC errors of new copper | 1 (declared 1V8) | 16 (incl. 2 P–N shorts) | **0** |
| pairs (mm) | 9.4 / 7.9 / 21.3 / **23.4** | 10.7 / 8.59 / 18.24 / 18.88 (shorted) | **9.46 / 8.80 / 17.98 / 18.62** |
| pairs P–N clearance checked on the board | no | no | **yes, 0.15** |
| mote pad-to-pad paths cut by the copy | ? | 1 (~{ADIN_INT}) | **0** |
| U1 to the L1 envelope | 1.79 (allowance) | 2.09 | 2.09 |
| bottom parts under the envelopes | yes (declared) | yes (declared) | yes (declared) |
| JP1 | bottom | top | top |
| LEDs | band's east end | north edge | north edge |
| grid build | 268 s | 19 s | 17 s |
| full routing run | 390 s | ≈ 300 s | ≈ 330 s |

## 8. Pass criteria of BRIEF 01 §8, re-scored (BRIEF 1.a §8)

| # | Criterion | Result |
|---|---|---|
| 1 | DRC: 0 errors, 0 unconnected, 0 parity (exclusions with reasons) | **Pass with the table**: 111 errors, 111 with reasons (all Sofar-copied features); 1 unconnected (J1's no-connect pair, by design); 4 parity (Q6) |
| 2 | §3 positions ±0.05; J1 pin 1 at (25.23, 8.37) from the top | **Pass** (`check_fixed.py` 0 failures) |
| 3 | §4 keep-outs, 2 mm around both envelopes, bottom ≤ 3 mm | **Pass** (no allowance; inserts' copper pull-back clear) |
| 4 | blockcheck 100 % | **Pass with trimming declared**: 0 missing, 127 trimmed (dead-end lead-outs, listed), 0 mote pad-to-pad paths cut |
| 5 | §6 widths on new routing; pairs no longer than the mote's; R8 sense identical; rings identical | **Pass**: 0 below class, 0 thin links, 0 clearance items; 4 of 4 pairs within, P–N 0.15; Kelvin yes / yes; rings 100 % |
| 6 | Renders | **Pass**: `out/m4/render_*.png`, `out/m4/layers/*.svg`, region views `out/review/` |

## 9. What I would do next (in order)

1. QE round 2 of this state; Nick's design review (`tools/review_views.py` output, the mote's copper beside ours per
   region).
2. M3: the JLCPCB DFM sweep per BRIEF §6 (limits fetched and cited in `DFM.md`, encoded in the design rules, the
   stackup, outer-layer pours — the bottom one exists — and the silk clean-up: 254 warnings are mostly silk / text).
3. The bottom GND island (§6 #1): confirm KiCad drops it, or give the pour an island-removal setting.
4. Q7 once more (marker positions from a pcbnew-saved copy).
