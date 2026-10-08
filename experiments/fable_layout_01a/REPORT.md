# REPORT — layout experiment 1.a (fit everything at the proper widths by moving blocks)

*Branch `experiment/fable-layout-01a`, 2026-10-08. Never merge. Stopped after milestone M2 on Nick's instruction
(wind down after ~2 h and have the QE review the work so far): **M2 did not reach its bar** and **M3 (the JLCPCB DFM
sweep) was not started**. Everything here was produced by the scripts in `tools/` (`tools/build_all.sh` rebuilds the
board from the schematic; `START=m4` reruns the routing from the M3 snapshot); the numbers are read from the check
outputs in `out/m4/`, not typed in. Board frame: KiCad coordinates = the brief's frame (Pi NW corner (0, 0), mm).*

## 1. Result in one paragraph

The placement of OPTIONS §3 holds: 138 footprints, every §3 position within 0.001 mm, U1's courtyard 2.09 mm from the
L1 envelope (01's 0.3 mm allowance is gone), 0 new courtyard overlaps, the LEDs on the north edge, JP1 on top at the
strip's north end, U11 facing its loads, B18 under the band's east end. Every copied block matches the mote to
0.001 mm (blockcheck: pads 242/242, tracks 606/729, vias 161/173, arcs 4/4, zones 6/6, **0 missing**, 135 copied
items trimmed as dangling, listed in `out/m4/blockcheck.md`). The routing is at the brief's widths and clearances
everywhere it exists: **0 new segments below their class width, 0 links at 0.15 mm beyond a pad field** (01: 10 and
13), the Kelvin links pad-to-pad by tracks, three of the four ADIN pair legs within the mote's length and all four
routed as coupled pairs with the mote's geometry. It is short of M2's bar by: **3 open links** (~{ADIN_INT} at U1
pin 39, VBUS at U11 pin 1, the two 5V_PI pours), **port 1's P leg 1.2 mm over** the mote's length, **12 DRC errors
of new copper** (11 are the port-1 pair's swap figure colliding with itself), **6 class-clearance items** on
VBUS_OUT's escapes, and 1 dangling zone via. The exclusions are a reviewed table again (Q7 not attempted).

## 2. Final board size

**46 × 65 mm, unchanged** (x −7.5 … 38.5, y 0 … 65, r 3 corners). No growth was needed. Stack: 6 copper layers in the
mote's order, 01's generic 1.6 mm build (M3 was to replace it with JLCPCB's stackup; not done).

## 3. Block moves (OPTIONS §3, as built)

| Block | 01: dst, rot | 1.a: dst, rot | Why |
|---|---|---|---|
| ADIN | (−1.4, 32.8), 90° | **(−1.7, 32.5), 90°**; region clipped at mote y 107.9 (west), x 148.2 (south), y 119.7 (east) | Q5 (2.0 mm restored); the south exit 0.3 mm wider; a 1V8 stub and a GND stub that collided with T1's C16 dropped |
| P1T (T1) | (8.7, 28.4), 0° | **(6.7, 28.4), 0°** | Q1; stops at the ADIN block's C8 |
| P2T (T2) | (16.0, 32.3), 180° | **(13.7, 32.5), 180°** | Q1; stops at P1T's C18 / its via |
| P2L | unchanged | region clipped at mote y 112.7 | its BM2_P leg stub was 0.31 mm from SENSE's via |
| B5V | (31.551, 31.4) | **(31.551, 21.24)** | Q3/Q6: under JP1 |
| B33 | (31.551, 17.704) | **(31.551, 34.44)** | swapped with B5V |
| DAMP3 (C23) | (33.5, 40.0), 0° | **(33.5, 40.95), 90°** | rotated to 8.8 wide × 7.4 tall |
| DAMP2 (C22) | (33.9, 48.2) | **(33.5, 48.6)** | follows the stack |
| B18 | (20.7, 47.2), 90° | **(19.0, 31.4), 90°** | Q2 |
| P1L, P2L, SENSE, DAMP1, rings | unchanged | unchanged | |

Fresh parts as OPTIONS §3 with these corrections after the M0 trial: JP1 (32.35, 9.45) top; U11 (32.5, 54.35) rot
−90 top, C49 (35.7, 54.35), R34 (29.6, 55.6) rot 90; R16 is C23's resistor, not C21's, so it sits under C23 at
(37.0, 42.5) bottom; TP19 (30.6, 43.3), C58 (36.6, 14.0), TP38 (36.6, 16.3) bottom.

## 4. Planes and routing

- Planes as 01 (GND In2 with the two inductor slots, the PWR plane In4 split), the 3V3 island moved with the 3.3 V
  cell to x 33.4–38, y 24–38; the 5V_PI pour on the bottom x 29.7–38, y 7.5–24 (solid connections); **new: a
  bottom-side GND pour over the whole board as the mote's bottom layer, solid pad connections as Sofar's pours**; the
  fiducials' mask apertures cut out of it.
- Bus feeds by hand (1.5 mm, Top), the bus legs at 0.2 mm / 0.35 from everything incl. the opposite leg (12.4 / 21.1 /
  17.4 / 9.6 mm), the bus rule in `.kicad_dru` unchanged.
- **Pairs**: routed as coupled pairs (two 0.2 mm tracks, 0.2 mm gap, via pairs 0.65 mm apart or the swap figure with
  two vias 0.6 mm apart along the track), Top + Internal 1, one swap each (the pin and pad order demands it):
  BM1 10.7 / 8.59 mm (limit 9.5: **P over by 1.2**), BM2 18.24 / 18.88 mm (limit 21.3; 01: 21.3 / 23.4).
- Corridors (OPTIONS §2.3) held: SPI + ~{CS} on Internal 2 under U1 to J1 (31.8–39.0 mm), ~{RST} 26.7 mm, the LED
  nets north (43.0 / 36.1 mm), ADIN_VDDIO to the LED block 31.1 mm, 5V_PI 1.0 mm on top from L6 to JP1, PI_5V 2.3 mm to
  J1 pins 2/4, VBUS_OUT 0.6 mm on Internal 2 to J5.

## 5. DRC summary (kicad-cli, `--schematic-parity --severity-all`, `out/m4/drc_summary.txt`)

| Item | Count | Status |
|---|---|---|
| errors | 127 | 115 Sofar-copied features in the exclusion table (`out/m5/drc_exclusions.md`: insert contact 76, transformer footprint 26, courtyards 12, the P1L BM1_N stub vs Sofar's GND via 1) + **12 of the new copper, unjustified** (§6 #1, #2) |
| unconnected | 4 | J1 pins 1/17 (by design, SPEC 4) + **3 open links** (§6 #3) |
| schematic parity | 4 | MP1–MP4 "no pad for pin 1" (Sofar Q6) |
| warnings | 255 | silk / text / padstack / lib mismatch from the imported footprints (254) + **1 via_dangling** (§6 #4); 0 track_dangling, hole_to_hole, holes_co_located, starved_thermal |

## 6. Shortfalls against BRIEF 1.a §5 / §7 M2 (every one unjustified; for Nick)

| # | Item | Numbers | Why / what to do next |
|---|---|---|---|
| 1 | Port-1 pair's swap figure collides with itself | 11 DRC errors (clearance 0.0–0.12, shorting, tracks_crossing) on Internal 1 at (0.1–0.6, 27.1–27.5); BM1_DATA_P 10.7 mm (limit 9.5) | the figure passes its 7-case unit test on a blank board; the real path has a case it does not cover (the entry run after a turn, or the via pair at (0.23, 27.2) too near the swap at (1.1, 27.0)). The run before this one had 8.95 / 9.11 mm with the same kind of defect. Next: dump the real path into the unit test and fix the emitter; or give port 1 a hand-laid pair |
| 2 | 3V3 stitching via 0.14 mm from R21 pad 2 (3V3_FB) | 1 clearance error at (31.4, 34.0) | the near-miss exact via check reads the pad's net from the netlist; R21's FB pad and the 3V3 via are different nets 0.14 apart — the map's 0.07 mm margin was removed by the exact check at the wrong radius (dia from ρ). Next: use the class's real via diameter in `via_free_exact` |
| 3 | 3 open links | ~{ADIN_INT} U1.39 ↔ R1.1/J1.22; VBUS U11.1 ↔ the plane; the Top 5V_PI pour ↔ the bottom pour (C56/C57/C58 to JP1/L6) | INT: Sofar's west fan-out leaves no via spot (VDDIO's bottom track and R1 cover it); next: a hand via at (−6.75, 30.3) + a 0.2 mm Top track along Sofar's old path. VBUS: U11 pin 1's 0.5 mm escape has no path to a plane via after the signals; next: pre-stitch U11.1 before its row's signals. 5V_PI: the copied Top output pour reaches no via that the bottom pour also holds; next: one via in both fills (zone_stitch skips islands that already hold a via of the net) |
| 4 | Class-clearance items on new copper | 6: VBUS_OUT's 0.15 mm escapes at U11 pins 9/10 and its 0.6 mm track vs VBUS / GND copper at J5 (19.6, 57.1 / 61.6) and (35.1, 56.0), 0.15–0.25 instead of 0.25 | the escape stubs are inside the pad field (the brief allows 0.15 width there; the clearance is the netclass 0.15); the three track items are real: next: 0.25 for the payload class in the router's cross map was applied to signal routes only |
| 5 | 1 dangling via | a 5V_PI zone-island via at (31.7, 21.0) with no copper on another layer | zone_stitch places a via where it fits without checking that another layer's copper of the net is there; next: require it |
| 6 | GND pour island with no via | bottom pour island near (37.1, 13.9) (under C58/TP38) | none fits; the island carries no pad, so KiCad may remove it; harmless, to be confirmed |
| 7 | Q7 exclusion keys | not attempted | the table (`out/m5/drc_exclusions.md`) is for Nick to apply in KiCad |
| 8 | M3 DFM sweep, `DFM.md`, JLCPCB stackup | not started | |

Declared deviations carried from 01 that still hold: the 2 mm envelope clearance applied to top-side parts (bottom parts
under the inductors as Sofar placed them, OPTIONS Q4); J5 stays the JST GH; Sofar's T1/T2 pads 6/7 at 0.24 mm; the
insert contact as drawn; Sofar's 2.0 mm BM1_N stub 0.31 mm from Sofar's GND via (new in the table: the bottom pour
keeps the via that 01 trimmed).

## 7. What the tactic bought (vs experiment 01's final table)

| Measure | 01 | 1.a (this commit) |
|---|---|---|
| open links (besides J1's pair) | 0 | **3** |
| new segments below class width | 10 | **0** |
| links at 0.15 mm beyond a pad field | 13 | **0** |
| class-clearance items (new copper) | 1 | 6 |
| DRC errors of new copper | 1 (declared 1V8) | 12 (unjustified) |
| pairs (mm) | 9.4 / 7.9 / 21.3 / **23.4** | **10.7** / 8.59 / 18.24 / 18.88 |
| U1 to the L1 envelope | 1.79 (allowance) | 2.09 |
| bottom parts under the envelopes | yes (declared) | yes (declared, OPTIONS Q4) |
| JP1 | bottom | **top** |
| LEDs | band's east end | **north edge** |
| grid build | 268 s | 19 s |
| full routing run | 390 s | ≈ 300 s |

## 8. Pass criteria of BRIEF 01 §8, re-scored (BRIEF 1.a §8)

| # | Criterion | Result |
|---|---|---|
| 1 | DRC: 0 errors, 0 unconnected, 0 parity (exclusions with reasons) | **Fail**: 127 errors, 115 with reasons, 12 without; 4 unconnected (3 real); 4 parity (Q6) |
| 2 | §3 positions ±0.05; J1 pin 1 at (25.23, 8.37) from the top | **Pass** (`check_fixed.py` 0 failures) |
| 3 | §4 keep-outs, 2 mm around both envelopes, bottom ≤ 3 mm | **Pass** (no allowance; inserts' copper pull-back clear) |
| 4 | blockcheck 100 % | **Pass with trimming declared**: 0 missing, 135 trimmed (182 before routing incl. Sofar's lead-outs, re-counted after the final trim) |
| 5 | §6 widths on new routing; pairs no longer than the mote's; R8 sense identical; rings identical | **Partial**: widths all at class, 0 thin links; 3 of 4 pairs within (BM1_DATA_P +1.2); Kelvin yes / yes; rings 100 % |
| 6 | Renders | **Pass**: `out/m4/render_*.png`, `out/m4/layers/*.svg` (the mote's in `../fable_layout_01/out/m5/mote_layers/`) |

## 9. What I would do next (in order)

1. Reproduce the port-1 pair's real path in `test_pair.py` and fix the emitter case; re-run `START=m4` (5 min).
2. The three opens (§6 #3) — each is a local fix in `m4_route.py`.
3. `via_free_exact` with the class's real via diameter (§6 #2); the payload clearance in the cross map for power
   routes (§6 #4); zone_stitch's "another layer has copper" test (§6 #5).
4. M3: the JLCPCB DFM sweep per BRIEF §6 (limits fetched and cited in `DFM.md`, encoded in the design rules, the
   stackup, outer-layer pours — the bottom one exists now — and the silk clean-up).
