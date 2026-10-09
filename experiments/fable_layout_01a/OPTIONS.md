# OPTIONS — layout experiment 1.a, M0 review of experiment 01's open items

*Written 2026-10-08 before anything on the board changed (BRIEF §3, §7 M0). Every dimension below was measured on
experiment 01's final board (`experiments/fable_layout_01/board/…kicad_pcb`, md5 e6938b5…) or on Sofar's mote with
pcbnew, or comes from the brief. Trial placements were run on a scratch copy of this directory (pipeline through M2,
kicad-cli DRC, `check_fixed.py`); the numbers quoted from them are marked "trial". Board frame: Pi NW corner (0, 0), x
east, y south, mm.*

## 0. What the fixed items leave (unchanged from 01)

| Region | Extent (parts, top side) | Notes |
|---|---|---|
| West pocket | x −7.0 … 2.99, y 26.2 … 38.8 (10.0 × 12.6) | between the insert keep-outs (r 4.8 circles, so the corners reach y 23.7 / 41.3 at the edge) |
| Band | x 2.99 … 23.2, y 26.5 … 34.5 (8.0 tall) | between the two inductor envelopes + 2 mm; J1's courtyard is on B.CrtYd only, so top parts may reach x 23.2 |
| East strip | x 28.9 … 38.0 (top), 29.61 … 38.0 (bottom), y 7.8 … 57.2 | top: J1's PTH pads reach x 28.62; bottom: J1's socket courtyard ends at 29.61; the M3 holes' ±4.25 courtyards cut the ends |
| North band | x 6.5 … 23.5, y 0.5 … 7.0 | between the Pi standoff keep-outs (r 3.0) and the L2 envelope + 2 mm |
| South band | x 6.5 … 23.5, y 54.0 … 58.5 | J5 at x 11.47–18.52, y ≥ 58.55; H3/H4 keep-outs |
| Bottom | everything but J1's socket (x 23.43–29.61), the inserts and the hole keep-outs | bottom parts may sit under the inductor envelopes (01 deviation 2, Q4 below) |

Experiment 01's final numbers, for comparison (its `REPORT.md` §9, `out/m5/rules.md`): open links 1 (J1's no-connect
pair, by design); 10 segments below class width; 13 links routed whole at 0.15 mm; 1 class-clearance item; 1 DRC
clearance error of new copper (1V8 vs a BM1_P leg via, 0.225 mm); pairs 9.4 / 7.9 / 21.3 / **23.4** mm (limits 9.5 /
9.5 / 21.3 / 21.3); DRC 111 errors (110 Sofar) / 258 warnings / 1 unconnected / 4 parity.

## 1. The seven questions

### Q1 — BM2_DATA_N 23.4 mm vs the mote's 21.3

Where the length came from: U1 sits in the pocket rotated 90° (port-1 pins north at y 29.4, port-2 pins south at
y 36.2, SPI pins west). T2 stood at (16.0, 32.3) in the band with its data pads at x 14.0; the port-2 pair left U1's
south pins, went east along y ≈ 37 and back north to T2: 21.3 / 23.4 mm, routed one leg at a time.

| Option | Moves / changes | Frees | Risk | Pair length (estimate) |
|---|---|---|---|---|
| (a) ADIN block 270° (port-2 pins north, port-1 pins south, SPI pins east) | U1 turned; T2 north-east in the band; T1 must then sit south of U1 | the SPI pins would face J1 | **port 1's limit is 9.5 mm**: south of U1 the pocket has 1.4 mm (U1 courtyard ends at y 37.4, MP1's keep-out starts at 38.8) and the L1 envelope + 2 mm starts at y 34.5 — T1 (5.5 × 3.7 courtyard) cannot sit there; routed around U1's east side it is ≈ 12 mm | port 2 ✓, **port 1 ✗** |
| (b) ADIN block 0° / 180° (a port's pins facing the west edge) | — | — | the pocket is 10.0 mm wide and U1's courtyard 9.2: no transformer fits west of U1 | ✗ |
| (c) keep 90°, move T2 west, as close to U1's south-east as its bottom-side parts allow | P2T → (13.3, 32.5), its data pads at x 11.3 (were 14.0) | 2.7 mm of band east of T2 | P2T's bottom cap C24 sits 2.45 mm north of T2 and collides with P1T's C18 if T2 goes further west (trial: C24/C18 overlap at T2.x ≤ 12.4) | ≈ 1 + 14 + 3.5 = **18.5–19.5 mm** (≤ 21.3) |
| (d) pair-aware router (both legs on one centre line) | router | — | new code | lengths equal to ≤ 0.2 mm by construction; a straighter path than two independent A* runs |
| (e) T2 directly under T1 (x 6.7) | — | — | rejected by the trial: C24 overlaps C18 | would have been ≈ 14 mm |

**Decision: (c) + (d).** T2 at (13.3, 32.5), T1 at (6.7, 28.4) (T1 moved 2.0 mm west, as far as the ADIN block's C8
allows: trial C16/C8 overlap at T1.x < 6.7), the pairs routed as coupled pairs on Top + Internal 1 with the mote's
geometry (0.2 mm tracks, 0.2 mm gap, via pairs 0.65 mm apart; measured on the mote: edge gap 0.2 mm, via pairs
0.61–0.78 mm). Both pairs run over the GND plane's main island (the port-2 island slot is at y 26.2–26.7 and the
port-1 slot at y 39.0–39.5; the pairs stay between y 28 and 38).

### Q2 — 1V8 passes a port-1 bus-leg via at 0.225 mm (bus rule 0.35)

Where it came from: the 1.8 V buck B18 sat east of L1 (bottom, (20.7, 47.2)); its 1V8 output had to cross the BM1_P
leg's via column at x ≈ 12 on its way to U2 at the pocket's south end, with the L1 island slot and the P1L bottom
parts around it.

| Option | Moves | Frees | Risk |
|---|---|---|---|
| (a) move B18 to the bottom of the band's east end (U6 at (19.0, 31.4)) | B18 (bottom-only copper) | the strip east of L1 | 1V8 then runs west along y ≈ 37–39 on Internal 2 into the pocket's south exit, crossing the BM1 legs only where they run north–south at x ≈ 8–11 on Internal 1 (a crossing, not a parallel run); the 3V3 input of U6 comes from the 3.3 V island through J1's pin field (0.3 mm rail: 0.84 mm between pads) |
| (b) keep B18 where it was and give 1V8 another lane (north of L1, through the band) | nothing | — | the band's south margin is the port-2 pair's corridor; 1V8 would cross both legs and T2's bottom parts |
| (c) B18 in the pocket | — | — | no room: U1's bottom cluster fills it |

**Decision: (a).** No exception is allowed in this experiment (brief §3), so the 1V8 link is routed at the full
0.35 mm from bus copper or reported open.

### Q3 — 10 segments narrower than class, 13 links at 0.15 mm, 1 clearance item

Where they came from: (i) 5V_PI: the bottom pour from L6 to JP1 was split by the U10 cell's bottom parts and joined by
0.5 / 0.3 mm links; (ii) VBUS_OUT at U11: U11's output pin faced east into C49/R16 and the track squeezed past pad 9 at
0.5 mm / below 0.25 mm clearance; (iii) a 0.15 mm VBUS link into U11 pin 1; (iv) 13 whole links at 0.15 mm because the
"thin" fallback class was the only one that found a path (the pocket's exits, U11's west side, the pairs).

| Option | Moves | Frees | Risk |
|---|---|---|---|
| (a) strip re-ordered north → south: JP1 (top), 5 V cell, 3.3 V cell + C31, C23, C22, U11 cell | B5V ↔ B33 swapped; JP1 to the top at the strip's north end beside J1 pins 2/4; C23 rotated (8.8 wide × 7.4 tall instead of 7.4 × 8.8); U11 rotated −90° so VBUS_OUT (pin 10) is at its south-east corner facing J5, PAYLOAD_EN (pin 4) on the north row facing J1 pin 36, ISET / ~{PAYLOAD_FAULT} on the south row | 5V_PI becomes a 5 mm top-layer link from L6's output pad straight up to JP1 (the output pad is the inductor's north pad); PI_5V 2.8 mm to J1 pin 2 | the strip is full: JP1 7.8–11.1, L6 11.35–18.4, U10 18.6–23.8, L3 24.0–31.1, U5 31.3–36.5, C23 36.75–44.1, C22 44.4–51.8, U11 52.1–56.1, R34 beside U11; the M3 hole's square courtyard stops everything at y 57.2 (trial: 0 new courtyard overlaps) |
| (b) JP1 on top at the band's east end instead | JP1 only | the strip keeps 01's order | 5V_PI and PI_5V become ≈ 40 + 30 mm of 1.0 mm track around J1's north end: ≈ 35 mV at 1 A; rejected |
| (c) router: pad-field escape | router | — | a fine-pitch pad (U11 0.5 mm pitch, U1, the BGAs) gets a ≤ 2 mm orthogonal 0.15 mm escape to the nearest cell where the class width fits, then the class-width route; the narrower fallback classes are removed, so a link either routes at its class or is reported open (never narrowed) |
| (d) VBUS stitching | router | — | VBUS pads are pre-stitched into the In4 plane with the power class only (0.5 mm / 0.25); U11 pin 1 (VBUS) is on the north-east corner after the rotation, 1.4 mm from free plane |

**Decision: (a) + (c) + (d).** The pass criterion (brief §5) is enforced by `check_rules.py` as before, now with the
fan-out allowance counted per pad field (≤ 2 mm of 0.15 mm track per net) and no fallback classes in the router.

### Q4 — bottom-side parts under the inductor envelopes

Assumption stated: the 50 W envelope (15.5 × 15.5 × 14.2 mm for the MSD1514) is a **top-side volume**; the 2 mm
clearance around it is for top-side parts; bottom-side parts under it are allowed (as Sofar put D4/R12/R13/TP3/TP5 and
D5/R17/R19/TP7/TP13 under L1/L2 on the mote). What sits under the envelopes on the bottom in this experiment: P1L's
D4, R12, R13, TP3, TP5, C17, D2; P2L's D5, R17, R19, TP7, TP13; SENSE (U4, R8, R7, C15, TP22) under L2's south-east;
C26; P2T's C25 at the L1 envelope's clearance band. Tallest: D2 (SOD-323, 1.1 mm), R12/R13/R17/R19 (1210, 0.6 mm).

The alternative that keeps the bottom clear under both envelopes: R12/R13 and R17/R19 (the 1210 jumpers across the
windings, Sofar Q9) have to stay at the inductor pads, so the inductor + its bottom parts would move as one; the only
bottom area beside each envelope that is free of J1 (x 23.43–29.61) and the inserts is the 2.9 mm strip x 20.5–23.4,
which does not hold a 1210 (3.7 mm courtyard). The 13 parts would otherwise have to leave the port blocks (not rigid
copies any more) and spread over the bottom of the band and the south pocket, with the shunt block SENSE moving to the
band's bottom as well. Cost: 4 new routing groups (≈ 25 mm of 0.5 mm bus-net copper per port for the TVS/jumper legs,
the Kelvin block's P_IN/VBUS feed moved), and the band's bottom, which this plan uses for B18, the P1T/P2T parts and
the LED resistors' former spot, is full. **Decision: keep the assumption, declare it again for Nick (REPORT).**

### Q5 — U1 0.3 mm east of the pocket (courtyard 1.79 mm from the L1 envelope)

Where it came from: Sofar's U1 fan-out on the mote's north side (the SPI / INT stubs toward the STM32) reaches 5.4 mm
from U1's centre; rotated into the pocket that is the west side, and with U1 at x −1.4 the copper ended at x −7.0,
0.5 mm from the edge; at x −1.7 it would be 0.2 mm from the edge.

| Option | Moves | Risk |
|---|---|---|
| (a) ADIN block 0.3 mm west (U1 at x −1.7) and the copy region clipped 0.3 mm on that side (mote y 107.6 → 107.9) | U1, U2, U3, Y1, C1–C14, R1–R6, TP1, TP2 | the clipped stubs are the SPI / INT lead-outs that on the mote go to the processor; here they end at Sofar's own vias at x −5.9 … −6.2 or are trimmed as dangling anyway (01 trimmed 33 ADIN items). Copper ends ≥ 0.6 mm from the edge |
| (b) keep the 0.3 mm allowance | nothing | a declared deviation stays |

**Decision: (a).** Restores the full 2.0 mm (trial: U1 courtyard x −6.3 … 2.9, 2.09 mm from the envelope at 4.99;
`check_fixed.py` 0 failures with the allowance removed).

### Q6 — JP1 on top; LEDs at the centre of the north edge

**JP1:** yes, on top, at (32.05, 9.45) at the strip's north end: courtyard x 29.7–34.4, y 7.8–11.1, which clears
MTG2's ±4.25 mm courtyard (y ≤ 7.79; trial: JP1 at y 8.85 overlapped it by 0.55 mm) and its r 3.5 keep-out (gap 4.3),
and H2's r 3.0 keep-out (gap 4.9). Its pad 1 (PI_5V) is 2.8 mm from J1 pin 2 (27.77, 8.37) on the top layer; its pad 2
(5V_PI) sits 1.3 mm above L6's output pad (36.48, 14.3). Cut it before stacking from the top.

**LEDs:** yes, D10 / D8 / D9 at (11.6, 1.4), (15.0, 1.4), (18.4, 1.4), top, light facing up and nothing north of them
but the edge:

| Rule | Check |
|---|---|
| Edge clearance 0.5 mm (copper) | LED pads reach y 0.925 (0.95 mm pads centred at y 1.4) → 0.93 mm from the edge |
| H1 (3.5, 3.5) / H2 (26.5, 3.5), r 3.0, both sides | courtyards x 10.08–13.12 / 13.48–16.52 / 16.88–19.92: gaps 6.6 / 6.6 |
| MTG1 / MTG2 r 3.5 and ±4.25 courtyards | x ≥ 10.08 vs MTG2's courtyard x ≥ 30.2 / MTG1's x ≤ 0.75 |
| L2 envelope + 2 mm (y ≥ 7.0) | courtyards end at y 2.17: 4.8 mm clear |
| FID3 / FID4 (21.5, 2.5) / (8.0, 2.5), top | courtyards 20.33–22.67 / 6.83–9.17: gaps 0.4 / 0.9 |
| Between the Pi's north standoff holes, y < 7 | x 10.08–19.92, y ≤ 2.17 |
| Pi SD-card slot under the north end | bottom parts here are 0402 resistors (0.4 mm) and JP2 (bare copper), within the brief's 3 mm bottom limit |

Their resistors R44–R46 and JP2 go under them on the bottom (JP2 at (15.0, 4.3), R46 (10.8, 4.2), R44 (18.0, 4.2),
R45 (19.4, 4.2)), so the whole LED block is at the north edge and three nets travel north from the ADIN block:
ADIN_VDDIO (0.3 mm rail, to JP2), ~{ADIN_P1_LED1} (U1 pin 21, east side) and ~{ADIN_P2_LED1} (U1 pin 48, west side).
Cost: ≈ 3 × 35 mm of track (01: the LEDs were 20 mm from U1; P2_LED1 was 36.6 mm, P1_LED1 19.3 mm, LED_VDD 7.2 mm).
Lanes: ~{ADIN_P2_LED1} along the west edge (the 0.39 mm lane at x −7.0 … −6.61 between the edge clearance and MP4/MP3's
r 4.8 copper pull-back: one 0.2 mm track), ~{ADIN_P1_LED1} and ADIN_VDDIO through the band and north between the L2
envelope and J1 (x 20.5–24.1 on Internal 2, nothing else there). If the resistors stayed near U1, five nets would go
north (three anode nets plus the two LED pins), so the resistors move too. ADIN_LED_VDD is local to the LED block.

### Q7 — DRC exclusions kicad-cli accepts

Try once more (in M2, time-boxed): KiCad 9 keys an exclusion `type|x|y|uuid1|uuid2` by the **marker** position, which
the DRC engine computes per test (for a clearance item the point of closest approach; for a courtyard overlap a vertex
of the intersection; for a hole clearance the hole's position). Plan: compute each marker position with pcbnew's own
shape calls (`SHAPE::Collide` with the location out-parameter, the courtyard polygon intersection) for the 110 Sofar
items, write the keys, and prove acceptance by the error count dropping in a fresh `kicad-cli pcb drc`. If the count
does not drop for a type, that type stays in the reviewed table (01's `drcexclude.py`).

## 2. The tactic

1. **Placement first** (M1): the moves in §3 below. Everything that was a routing problem in 01 is given room: the
   pocket's exits are planned (§2.3), U11 faces its loads, the 5 V path is 8 mm long, the LEDs leave the band.
2. **Pair router**: P and N of each ADIN pair are routed as one virtual track 0.6 mm wide (two 0.2 mm tracks at
   0.4 mm pitch, the mote's 0.2 mm gap) with the signal clearance, then emitted as two offset tracks; a layer change
   becomes a via pair 0.65 mm apart perpendicular to the track (0.45/0.2 vias, hole-to-hole 0.45 ≥ 0.25). The pair
   starts between U1's two pins (0.5 mm pitch, so the offset tracks leave the pins straight) and ends between T1/T2's
   pads 1/2 (0.65 mm pitch). Layers: Top + Internal 1, as the mote; length ≤ the mote's checked as before.
3. **Corridor plan** (per net group, as a layer preference in the router's cost, and an order):
   - SPI (MOSI, MISO, SCK, ~{CS}) and ~{INT}: from Sofar's vias at the pocket's west side (x −5.85 … −6.2, y 30.2–34.1)
     east on **Internal 2 under U1** (the mote has 15.8 mm of Internal 2 copper there, nothing else), across the
     band at y 30–34 (T1/T2's copied vias are the only obstacles) to J1 pins 19/21/22/23/24 at y 31.2–36.3 — the SPI
     pins sit exactly at the band's latitude. Length ≈ 34 mm each (01: 32–48 mm).
   - ~{RST}: from Sofar's via at (2.5, 32.15) (U1's east side) east on Internal 1/2 to J1 pin 18 (27.77, 28.7).
   - ADIN_PWR: from U2/U3's ON pins (pocket south) east along y ≈ 38.5 on Internal 2, then to J1 pin 16 (27.77, 26.15)
     and R43 (7.5, 36.3, bottom).
   - 1V8 and 3V3 into the pocket's south: on Internal 2 along y 36–39 to U2 (−1.4, 38.1) and U3's via at (−5.8, 38.65).
   - LED nets north: §1 Q6.
   - Bus legs (0.2 mm, 0.35 from everything else incl. the opposite leg): L1 pads (11.03, 40.0 / 48.5) north to T1
     pads 6/7 (8.69, 27.7 / 27.05); L2 pads (11.03, 12.5 / 21.0) south to T2 pads 6/7 (15.29, 31.8 / 31.15); Internal 1
     preferred, so the Internal 2 corridors above cross them at one point each.
   - 5V_PI / PI_5V: top layer at the strip's north end (JP1 ↔ L6, JP1 ↔ J1 pins 2/4 through a 1.0 mm track at
     x ≈ 29.4 and the PTH pads).
   - VBUS_OUT: U11 pin 10 (33.5, 55.5) → via → Internal 2 west along y ≈ 58.5 (south of J1's last pins at 56.63, north
     of H4's hole) → J5 pin 1 (14.4, 59.95); 0.6 mm.
   - PAYLOAD_EN / ~{PAYLOAD_FAULT}: J1 pins 36/38 (27.77, 51.55 / 54.09) → U11's north row / south row, 4–6 mm.
   - I²C: J1 pins 3/5 (25.23, 10.9 / 13.45) → R26/R27 on the strip's bottom at (36.6, 21.5 / 23.1) on Internal 2.
4. **Order**: pairs → bus legs → 5 V links → VBUS_OUT → the pocket's planned nets (SPI, INT, RST, PWR) → 1V8, 3V3 to
   the pocket → LED nets → PAYLOAD_EN/FAULT, ISET, UVLO → the rest short-first → stitching → plane leftovers.
5. **Pad-field escape** and **no fallback classes** (§1 Q3).
6. **Rip-up** stays off; a net that fails is a placement or corridor problem and is fixed there.
7. Everything else as 01: planes (GND island slots, the PWR plane split, 3V3 island moved with the 3.3 V cell to
   x 33.4–38, y 24–37; the 5V_PI bottom pour shrunk to x 29.7–38, y 7.5–17.5 under JP1/L6), bus feeds by hand, the
   bus rule in `.kicad_dru`, dangling clean-up, blockcheck, check_fixed, check_rules.

## 3. Planned block moves (transform = p' = R(rot)·(p − src) + dst; src = the anchor's mote position)

| Block | 01: dst, rot | 1.a: dst, rot | Why |
|---|---|---|---|
| ADIN | (−1.4, 32.8), 90° | **(−1.7, 32.8), 90°**; copy region's west edge clipped 0.3 mm (mote y 107.6 → 107.9) | Q5: U1 courtyard 2.09 mm from the L1 envelope; copper ≥ 0.6 mm from the edge |
| P1T (T1 cluster) | (8.7, 28.4), 0° | **(6.7, 28.4), 0°** | Q1: T1's data pads 2.0 mm nearer U1's port-1 pins; stops at C8 (ADIN block, bottom) |
| P2T (T2 cluster) | (16.0, 32.3), 180° | **(13.3, 32.5), 180°** | Q1: data pads at x 11.3; stops at P1T's C18 (bottom) |
| B5V (5 V cell) | (31.551, 31.4), 0° | **(31.551, 21.24), 0°** | Q3/Q6: north end of the strip under JP1 |
| B33 (3.3 V cell) | (31.551, 17.704), 0° | **(31.551, 33.94), 0°** | swapped with B5V |
| DAMP3 (C23) | (33.5, 40.0), 0° (board −90°) | **(33.5, 40.45), 90°** (board 0°) | rotated to 8.8 wide × 7.4 tall: saves 1.4 mm of strip |
| DAMP2 (C22) | (33.9, 48.2), 0° | **(33.5, 48.1), 0°** | follows the stack |
| B18 (1.8 V buck) | (20.7, 47.2), 90° | **(19.0, 31.4), 90°** | Q2: bottom of the band's east end; 1V8 no longer crosses the BM1 leg vias |
| P1L, P2L, SENSE, DAMP1, RING_MP1–4 | unchanged | unchanged | fixed by the brief or already right |

Fresh parts (not blocks): JP1 (32.05, 9.45) top; C31 (36.6, 33.94) top beside U5; U11 (32.5, 54.1) rot −90 top, C49
(35.7, 54.1) top, R34 (29.6, 55.3) top; D3 (33.0, 53.9), R35 (30.6, 52.3), R41 (36.0, 52.3), R42 (36.0, 53.6),
C50 (36.4, 55.5), TP35 (36.6, 48.5), TP19 (30.6, 48.6), R15 (37.0, 45.5) bottom; C56 (31.6, 12.5), C57 (31.6, 14.7),
C58 (35.0, 14.0), TP38 (37.0, 14.0), TP20 (37.0, 8.8), TP24 (34.6, 9.0), R26 (36.6, 21.5), R27 (36.6, 23.1) bottom;
LEDs and their block at the north edge (Q6); R43 (7.5, 36.3), TP8 (9.8, 36.3), C26 (17.0, 23.3) bottom; D1 (20.9, 59.0)
top, R16 (6.3, 56.0) top (C21's damping resistor, next to C21 instead of in the strip), R11 (21.0, 58.0), TP36
(19.5, 62.3) bottom; fiducials as 01.

Trial result of this placement (scratch copy, pipeline through M2): `check_fixed.py --heights` 0 failures (U1's
allowance removed); kicad-cli courtyard overlaps = Sofar's 10 intra-block pairs + the 2 MTG/H pairs + 0 new (after
the fixes listed in LOG M1); 138 footprints placed, 0 parked.

## 4. Expected numbers (to be measured in M2)

Open links 0 but J1's pair; segments below class 0; thin links beyond a pad field 0; class-clearance items 0; pairs
≈ 8.4 / 8.9 / 19 / 19 mm (limits 9.5 / 9.5 / 21.3 / 21.3); DRC errors = Sofar's copied features only; 0 copper-defect
warnings. If a net cannot be routed at its class width, it is reported open with the reason, not narrowed.

---

# Addendum — session 2.b (2026-10-08): the 49 × 68 frame, the inserts, U1 in the centre vs the pocket, the jumpers

*Written after the trials, as M0 was (BRIEF §3, §7). Every number below is from a scratch trial run through M2 (`tools/trial.sh`,
logs `trial.sh … .log`, boards never in `board/`) or from the mote with pcbnew. Frame: Pi NW corner (0, 0), x east, y south.*

## A1. Where the extra 3 + 3 mm went (Nick: 3 mm wider, 3 mm taller; LESSONS §3)

| Growth | Where | Why |
|---|---|---|
| +3 mm width | **West**: x0 −7.5 → −10.5; the inserts and MTG1 / MTG3 move with the edge; J1, the Pi holes and the strip east of J1 stay | The first trial put it on the east (x1 41.5): the strip gained 3 mm its parts did not need (nothing in it moved), while on the west the T2 cluster's bottom cap C25 sat inside MP4's r 4.8 keep-out and T1's C19 against J1's socket courtyard at the same time. On the west the band between the port-2 keep-out and J1's socket gains the 3 mm for the T2 – U1 – T1 chain, and the pocket is 13 mm wide |
| +3 mm height | **South**: y1 65 → 68; L1's envelope, J5 and the south band 3 mm south; the port-1 inserts 2.5 mm south; J1, H1–H4 and the north band stay | The band between the envelope clearances grows from 8.0 to **11.0 mm (y 26.5 … 37.5)**, exactly where J1's SPI pins are (y 31.2 … 36.3). Growing north instead would have moved the LEDs' edge and the port-2 side for no gain. MP1 / MP2 move 2.5, not 3: at 3 MP2's courtyard came within 2.91 mm of the Pi's H3 standoff keep-out (r 3.0) |

## A2. Inserts 1.5 mm nearer the west wall (Nick: 1–2 mm)

The mote's corner inserts sit 3.5 mm from its edge (MP1 / MP3 measured: 3.525), with their Ø7.4 ring copper on the outline.
JLCPCB's copper-to-edge figure is **0.2 mm** (routed edges, DFM.md row 15, read 2026-10-08); the brief keeps **0.5 mm** (BRIEF 1.a
§6: "the brief's 0.5 mm stays"). With 0.5 the ring (outer radius 3.69) can come to **4.19 mm** from the edge: centre x = −10.5 + 0.5 +
3.69 = **−6.31**, a **1.5 mm** shift from session 2's 5.69 (x −1.81 on the old edge). 2 mm would need the 0.5 relaxed to 0 at the rings
(as the mote) — declined, the brief's rule stands. What it buys: 1.5 mm more between the keep-out circles (r 4.8) and the band's
parts; the pocket x −10 … −1.5. Sofar's 4.8 mm keep-out is unchanged. The bus feeds start 3.31 mm from the insert centre (DFM row 13).

## A3. U1 in the centre of the band vs U1 in the pocket — the trials

Both placements were run through M2 (placement, copper copy, planes, routing) on scratch copies with the same scripts; the centre
in eight trials (placement and router changes between them), the pocket in four. The table is the last routed trial of each.

| Measure | **Pocket** (trial 9 → final, see REPORT; trial 3 numbers here) | **Centre, best routed** (trial 4: U1 rot 270; trial 8: U1 rot 0) |
|---|---|---|
| U1 | (−4.7, 33.75) rot 90 in the west pocket (x −10 … −1.5, y 26.2 … 41.3): port-1 pins north toward T1, port-2 south, SPI west | (11.8, 31.15): rot 270 (SPI pins east toward J1; trials 2–4) / rot 0 (the mote's: SPI north, port 1 east, port 2 west; trials 5–8) |
| T1 / T2 | (3.7, 29.45) / (10.7, 33.75) in the band beside U1, session 2's relation | T1 south-east (18.6 … 20.4, 35.6), T2 at the band's north edge (rot 270) or south-west (rot 0) |
| Pairs mm (limits 9.5 / 9.5 / 21.3 / 21.3) | **9.59 / 8.97 / 19.93 / 20.61** (P 0.09 over → T1 0.2 mm north in trial 9) | rot 270: 9.40 / **10.04** / 13.17 / 13.81; rot 0: **21.72 / 18.97 / 46.88 / 47.52** (connected, far over) |
| SPI new track mm (SCK / MOSI / MISO / ~CS) | 34.2 / 35.1 / 40.4 / 41.0 — on Internal 2 under U1 straight east to J1, **no edge detour** (session 2: 66.5 / 67.6 down the west edge) | 13.5 / 11.2 / 10.2 / 14.4 (rot 270); 17.4 / 14.0 / 17.1 / 24.6 (rot 0) |
| Open links besides J1's pair | 0 | 2 (rot 270: 3V3 at U3's ball, the GND island); 1 (rot 0: C19's net) |
| DRC errors (Sofar's with reasons / without) | 113 (113 / 0) | 109 (rot 270), 119 (rot 0) |
| Rules: below class / thin / clearance | 0 / 0 / 0 | 0 / 0 / 0 |
| Pair legs, segments | 15 / 15 / 18 / 18 (session 2: 25 / 40 staircases) | 18 / 18 / 25 / 24 |

**What the centre trials showed, in numbers.** The ADIN's port pins are on two opposite edges of a 7 mm QFN, each port's pair at
the middle of its edge; each transformer's data pads must be entered along a straight lane 1.4 mm long, and one P–N swap is needed
per port (the pin and pad order demand it, as on the mote). In the band the transformers can only stand at the band's south edge
(their courtyards 3.7 tall, U1's 9.3 in 11.0), so from the pins to the pads is a 2–7 mm Z at 45–60°:
- rot 270 (SPI facing J1): the port-1 pins sit on U1's south-**west** (x 9.05 / 9.55 for U1 at 10.8) while T1 is bounded by J1's socket
  on the east (its bottom cap C19 ≤ x 23.43 → T1 ≤ 19.1): the pair runs 7 mm sideways, **9.69–10.04 mm** in three trials against
  9.5; Sofar's processor-side fan-out vias (1.9–2.5 mm past the pads) land on T1's data pads unless clipped, and clipping them
  left MISO, VDDIO, 3V3 and two strap nets with no fan-out room of their own (trial 3).
- rot 0 (the mote's): the mote's own port-1 geometry (T1 at +7.6, +4.5), but Sofar routes it with vias at the pins and vias behind
  the pads, entering from the transformer's body side; our emitter enters along the lane and needs 2.0 mm of straight run for
  the swap figure, which the Z does not have — it found it behind the pads and U-turned (every candidate failed the board check,
  trials 5–6), or, with the half-plane behind the pads forbidden and the swap moved to the pins' exit (trial 8), it connected both
  pairs around the ADIN block's own fan-out vias at **21.7 / 19.0 / 46.9 / 47.5 mm**.
- The SPI, which the centre was meant to shorten, is 10–25 mm there against 34–41 in the pocket; in the pocket it no longer
  detours (the lane is reserved first), so the 25 mm the centre would save is on a net that does not need it (LESSONS §5).

**Decision: the pocket** (the only placement that meets the bar in these trials), recorded as Nick asked: the centre is preferred
and was tried first; it cannot meet the pairs' bar with this emitter. What it would take: a pair emitter that enters the pads
from the body side through a staggered via pair (Sofar's figure: the swap happens in the layer change, no 2 mm straight run), or
a hand-routed port-1 pair. That is one router feature, not a placement problem, and the centre's other numbers (SPI 10–14 mm,
port 2 11–14 mm, 0 clearance items) are good. The `VARIANT=centre` placement stays in `m2_place.py` for that next step.

**Nick's J5-west / L1-south idea (2026-10-08, mid-run):** tried as `J5WEST=1` on the centre placement (J5 on the west wall in the
pocket, mating face west, L1's envelope 1.5 mm further south — the most the Pi's H3 / H4 keep-outs allow — so the band is 12.5 mm;
C21 / D1 / the fiducials 1.5 mm south with it). The band height is not what limits the centre (the Z geometry is), the pairs failed
the same way (trials 6–7), and VBUS_OUT grows from 23 to **56 mm** of 0.6 mm track (≈ 75 mΩ, 55 mV at 0.73 A). With U1 in the
pocket the idea does not apply (J5 would take U1's place). Kept as an option for the centre, not built.

## A4. The cut jumpers JP1 / JP2 on top, at an edge, no tall part beside them (Nick)

Both in the **north band** (x 6.5 … 23.5 between the Pi's standoff keep-outs, y 0.5 … 7.0 under L2's envelope clearance), where only
the LEDs are: JP1 (5 V to the Pi) at (20.4, 2.2) at the band's east end, JP2 (the LED supply) at (12.5, 5.2) behind the LEDs; FID3 /
FID4 moved to y 5.0 / 5.3 (DFM row 26). Alternatives: JP1 at the strip's north end beside L6 (session 2): a tall inductor beside it;
JP1 / JP2 in the west pocket: 40 + 30 mm of 1.0 mm track for the 5 V (OPTIONS Q3 b) and U1 is there. Cost of the north band:
- **JP1**: PI_5V from J1 pins 2 / 4 ≈ 11 mm (was 2.8), 5V_PI from L6's output pad ≈ 22 mm of 1.0 mm track across J1's north end on
  an inner layer (0.5 oz) ≈ 25 mΩ, plus PI_5V ≈ 10 mΩ: **≈ 35 mV at 1 A** against the Pi's 5 V ± 5 %; session 2's 8 mm path was ≈ 6 mV.
- **JP2**: ADIN_VDDIO from U1 ≈ 30 mm of 0.2 mm rail to the north band, ADIN_LED_VDD 5.7 mm local to the LED block; the LED
  currents are 2 mA each, the drop is nothing.
Exact routed lengths of both are in REPORT.md §4 (from `out/m4/routing.json`).

## A5. Nick's question: the tall square parts east of the header, and moving them west of it

They are the two buck inductors **L6** (5 V for the Pi) and **L3** (3.3 V), Pulse PA5432.822NLT, 6.9 × 7.1 mm courtyards; the two
47 µF electrolytics **C22 / C23** (Panasonic EEEFT1H470AP, 8.8 × 7.4 courtyards); their bucks U10 / U5, the load switch U11, C31,
C49, R34 and JP1 (moved north in 2.b). Together ≈ **220 mm²** of top courtyard plus the bucks' loops (Sofar's copper, copied rigidly).
West of the header the top side has: the band (now U1 + T1 + T2, full), the west pocket (10 × 15 mm = 150 mm²: one buck cell of
8.6 × 13 fits, the second cell and two 8.8 mm cans do not; it also holds the 1.8 V buck on the bottom), the north band (17 × 6.5,
LEDs + jumpers + fiducials) and the south band (17 × 4.5 + J5). Everything else west of J1 is the two 50 W inductor envelopes +
2 mm. So moving all of it west needs either ≈ 9 mm more width on the west (a 58 mm board) or the cans on the bottom, which the
3 mm bottom limit forbids (the Pi is there). Moving only the 3.3 V cell (L3, U5, C30 + C31) into the pocket is possible if U1 stays
in the band — i.e. only in the centre layout, which does not route yet (A3). Recorded for Nick; not acted on.

## A6. Nick's mid-run decisions after the first rebuild (2026-10-08, from the renders)

1. **"Use the 20 W inductors as the keep-out, not the 50 W design."** The fitted SRF1260's courtyard (13.1 × 13.6 mm, from its
   footprint) + the brief's 2 mm clearance replaces the 15.5 × 15.5 MSD1514 envelope (BRIEF §3). Centres unchanged. The band
   between the inductors' clearances grows from 11.0 to **12.9 mm (y 25.55 … 38.45)** and 0.8 mm on each side; the GND plane's
   island slots follow the inductors (`make_planes`); `check_fixed.py` checks the new rectangles. Recorded in `geom.py` (INDUCTOR_HALF,
   ENVELOPES) and in BRIEF §3 as superseded.
2. **"The ADIN is too close to the west edge; move it east a few mm."** The U1 / T1 / T2 group moves 3 mm east: U1 at (−1.7, 33.75)
   (8.8 mm from the edge, was 5.8), T1 (6.7, 29.45), T2 (13.7, 33.75), R43 / TP8 with them; B18 stays at x 19.0 (J1's socket
   courtyard at 23.43 bounds it). Nothing else limits the move: the insert keep-outs (r 4.8 around y 21.4 and 46.1) do not reach
   U1's latitude. A bonus: Sofar's ~{ADIN_INT} via (mote y 107.509) lands 2.8 mm inside the board, so the ADIN region is the
   mote's full one and the hand via of sessions 2 / 2.b is gone.
Both rebuilt from M0 together with the QE round-3 fixes (no via in a solder pad; the small-pad 0.2 mm stubs of plane nets).
Note for Nick (QE round 4 N4): DESIGN D31 still names the 50 W envelope as the real layout's target; whether the 20 W keep-out
carries over is a decision outside this experiment's folder.
