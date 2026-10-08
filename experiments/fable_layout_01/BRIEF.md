# Layout experiment 01 — port Sofar's mote layout onto the Pi shield

*Brief for an autonomous layout agent (Fable 5.1, high effort). Owner: Nick Buemond. Written 2026-10-07 (S7.a, DESIGN
D31). This is an **experiment**: its board is never merged into the live project. The question it answers: how close
can an agent get to a working, DRC-clean shield by carrying Sofar's proven copper over block by block?*

---

## 0. Hard rules (read first)

1. **Write only inside `experiments/fable_layout_01/`**, on the branch `experiment/fable-layout-01`. Never modify
   `nereus_Pi_shield_ADIN2111/` (the live project), `KiCAD_reference_designs/` or `Archive/`, and never touch `main`.
   This is the one place an agent may write a `.kicad_pcb` (D31).
2. **KiCad stays closed.** Work through KiCad 9's bundled Python (`pcbnew`) and `kicad-cli`:
   `PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3`,
   `K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`.
3. **Trust artifacts, not exit codes.** Every step ends with a check you ran on the output files and a render you looked at.
4. **Don't change the circuit.** Pin connections come from the schematic. The only schematic edit allowed (in your copy,
   §1) is J5's footprint and value.
5. **Copied blocks are rigid.** Translate and rotate (multiples of 90°) only. Never mirror and never move a block to the
   other side of the board.
6. **Never invent a fact.** A dimension or rating you can't find in a file or datasheet goes in `REPORT.md` as an open
   question.
7. **Stop and report** (in `REPORT.md`, then commit) if the board would have to grow more than allowed in §2, or a hard
   rule would have to break.

## 1. Inputs and workspace

| What | Where |
|---|---|
| Sofar's reference board (copper to copy; read only) | `KiCAD_reference_designs/20250409_BM_Mote_000639-AB/BM_Mote_000639-AB.kicad_pcb` |
| Our schematic, libraries, project | `nereus_Pi_shield_ADIN2111/` (copy it; don't edit it) |
| Our pin map, decisions, constraints | `docs/DESIGN.md`, `docs/SPEC.md` |
| Mote layout walkthrough (layers, blocks, routing) | <https://claude.ai/artifact/3r8FU8hymFa5kMCDC82kXK> |
| Questions open with Sofar (layout) | <https://claude.ai/artifact/EGFhjTuFXwPFSurFLPqQx4>, `docs/SOFAR_QUESTIONS.md` Q6, Q9–Q12 |
| Layer renderer (same code for mote "before" and shield "after") | `experiments/fable_layout_01/tools/render_layers.py` |

**Set-up.** Copy `nereus_Pi_shield_ADIN2111/` (all `.kicad_sch`, `.kicad_pro`, `sym-lib-table`, `fp-lib-table`,
`*.kicad_sym`, `mote.pretty/`, `nereus.pretty/`) into `experiments/fable_layout_01/board/`, **without** its
`.kicad_pcb` (that file is still the mote's old layout). Create a new `board/nereus_Pi_shield_ADIN2111.kicad_pcb` from
the schematic's netlist (`$K sch export netlist`), loading each footprint from the project libraries with `pcbnew` and
assigning pad nets. `kicad-cli` 9 has no "update PCB from schematic" command; if the API route fails, write it in
`REPORT.md` and stop at M0 so Nick can run Update PCB from Schematic once in KiCad.

**The one schematic edit (your copy only):** J5 → Molex Micro-Fit 3.0, 2-pin, right angle, through hole: footprint
`Connector_Molex:Molex_Micro-Fit_3.0_43650-0200_1x02_P3.00mm_Horizontal`, value `43650-0200`. Pin 1 VBUS_OUT, pin 2 GND
(unchanged). Reason: the payload connector is sized now for the planned 50 W revision (Nick); this board's payload is
still limited to ≈ 0.73 A by U11.

## 2. Board

**Frame.** All coordinates below are in mm, looking down on the top side: origin at the Pi Zero 2 W's north-west
corner, x east, y south. The Pi Zero is portrait under the shield: micro-SD at the north end, 40-pin header along the
east edge, camera connector at the south end.

**Outline: 46 × 65 mm**, x −7.5 … 38.5, y 0 … 65, corner radius 3 mm, plus Nick's north notch for the SD card. Copy the notch exactly from his `User.3 "Outline_PiZero"` shape in the live
board file (read only), translated by (−194.53, −58.48) into this frame: that centres his 31.5 mm-wide outline on the
30 mm Pi. It is a fillet–chamfer–fillet cut 1.5 mm deep, ≈ 22.7 mm wide at the edge and 16.3 mm at full depth, spanning
x ≈ 5.84 … 25.66. Its east end comes ≈ 2.76 mm from H2's centre, inside H2's r 3.0 keep-out: keep Nick's shape (the board
edge is exempt) and list it for Nick (§11). **Allowed growth:** the
south edge may move up to 2.0 mm south (46 × 67) if U1 can't be placed otherwise (see §4). Report the final size.

**Stack.** 6 copper layers, 1.6 mm, in the mote's order and roles: L1 top (parts, bus copper, buck pours) · L2 signal ·
L3 GND plane · L4 signal · L5 split power plane · L6 bottom (parts). Use the mote's names. Dielectrics and copper weights
are unknown (Sofar Q11): use a standard 6-layer 1.6 mm build and note it.

**Sides.** Top = tall and heavy parts (as on the mote). Bottom = the Pi side: the J1 socket body and small parts only,
**max 3 mm tall** (the stacking header leaves ≈ 8.5 mm or more; 3 mm is the brief's margin).

## 3. Fixed placements

| Item | Ref | Position (frame §2) | Notes |
|---|---|---|---|
| 40-pin **stacking** header | J1 | Pin 1 at (25.23, 8.37), pin 2 at (27.77, 8.37); odd pins in column x 25.23, even in x 27.77, 2.54 mm pitch southward to pins 39/40 at y 56.63 | Socket body on the **bottom** (mates with the Pi's male pins), long tails up through the board. Footprint already `PinSocket_2x20_P2.54mm_Vertical`; place it on B.Cu and prove pin 1 lands at (25.23, 8.37) seen from the top. Source: Raspberry Pi Zero 2 W mechanical drawing (header centred 32.5 mm along the long edge, 3.5 mm in) |
| Pi standoff holes, M2.5 | H1–H4 (board-only footprints) | (3.5, 3.5), (26.5, 3.5), (3.5, 61.5), (26.5, 61.5) | `MountingHole:MountingHole_2.7mm_M2.5`, footprint attribute "not in schematic". Nothing within r 3.0 mm, both sides |
| Housing holes, M3 | MTG1–MTG4 | (−3.5, 3.5), (34.5, 3.5), (−3.5, 61.5), (34.5, 61.5) | Keep the mote's `Vault:Hole_M3`. Nothing within r 3.5 mm (screw head / washer), both sides. Its courtyard (±4.25 mm) and silk (r 4.0) run past the outline at these corners and its Ø6 pad sits exactly 0.5 mm from the north/south edges: clip the silk, and record the courtyard-edge DRC items with that reason |
| Bus inserts (M3, Sofar's contact) | MP3 = 2+ (BM2_P), MP4 = 2− (BM2_N), MP1 = 1+ (BM1_P), MP2 = 1− (BM1_N) | x −1.81 for all; y 12.0, 21.4, 43.6, 53.0 | Port 2 north, port 1 south, "+" north of "−". Ring copper r 3.69 → 2.0 mm from the west edge and 2.0 mm between the two rings of a pair; 14.8 mm between the ports |
| PoDL inductors | L2 (port 2), L1 (port 1) | 50 W envelope 15.5 × 15.5 mm at x 4.99–20.49; L2 y 9.0–24.5, L1 y 36.5–52.0 | Fit today's SRF1260 (12.5 mm) centred in its envelope. Keep 2.0 mm clear around each **envelope** (to edges, holes, J1, J5 and every part). The envelope reserves room for the 50 W MSD1514 (15.5 × 15.5 × 14.2 mm, `docs/POWER_PATH.md`) |
| Payload connector | J5 (Micro-Fit, §1) | Courtyard x 9.67–20.33, front at the south edge | Top side, mating face **south**, between the Pi's south holes |
| Link / power LEDs | D10 (port 2, green), D8 (ADIN power, red), D9 (port 1, green) | West wall between the two insert pairs, in that order north → south, D10 nearest port 2 | Top side. Exact spot is yours |

**Insert copper (reproduce Sofar's contact exactly, per Nick):** on L1 a C-shaped bus arc, width 1.2 mm, radius 3.03 mm,
≈ 290°; seven 0.6 mm vias of the bus net on r 3.0 mm, landing in the insert's bottom ring pad (r 2.2–3.69 mm); body
Ø6.0 × 1.5 mm on the bottom. The footprint pad has no net (Sofar Q6): copy the copper as Sofar drew it.

## 4. Keep-outs and the one known squeeze

- **Inserts:** no part and no other-net copper within r 4.8 mm of an insert centre, any layer (the inner planes on the
  mote stop 3.85 mm (MP2, MP4) to 4.78 mm (MP1, MP3) from each insert; 4.8 mm here is the brief's choice).
- **Edges:** copper 0.5 mm from the board edge; inner planes as the mote.
- **Camera ribbon:** the Pi's camera connector is under x ≈ 7–23, y ≈ 61.6–65 (scaled from the drawing, not dimensioned);
  nothing on the shield may hang below the bottom-side 3 mm limit there.
- **The squeeze:** the band between the two inductor keep-outs is y 26.5–34.5 (8.0 mm), but U1's courtyard is
  9.12 × 9.12 mm. Options in order: (a) U1 in the west-wall pocket between the insert pairs (x −7.0…2.99, y 26.2…38.8,
  10.0 × 12.6 mm; the LEDs move), keeping U1 between T1 and T2 as on the mote; (b) grow the south edge up to 2.0 mm (§2).
  Report which you used and why.

Area check (Claude, 2026-10-07): with every part on Sofar's side, the top side's part envelopes fill 46 % of the usable
top area with 50 W inductors (Sofar's top: 69 %), the bottom 28 % (Sofar's: 46 %). It fits overall; the free top area
comes in strips (east of J1 ≈ 8.5 × 50 mm, the inductor band, the west pocket, small north/south bands).

## 5. Blocks: what to copy and what is new

Map mote nets to ours **by pad** (the schematic net on the same ref + pad), not by name: some nets were renamed (D30) and
`docs/design-review/netcheck.md` lists all 51 kept nets.

| Block | Refs (mote copper to copy) | Notes |
|---|---|---|
| PORT1 | L1, T1, D4, R12, R13, R14, C16, C18, C19, TP3, TP5 (+ MP1, MP2) | Copy the cluster; the insert-to-cluster copper is new routing (the inserts moved) |
| PORT2 | L2, T2, D5, R17, R19, R18, C24, C25, C27, TP7, TP13 (+ MP3, MP4) | As PORT1 |
| SPINE | R8, U4, R7, C15, C20, C21, C22, C23, R15, R16, D1, D2, C17, C26, TP22, TP23 | R8's sense connections to U4 exactly as Sofar routed them |
| ADIN | U1, U2, U3, Y1, C1–C14, R1–R6, TP1, TP2 | Decoupling, crystal and U2/U3 under U1 on the bottom, as on the mote |
| BUCK3V3 | U5, L3, C28, C29, C30, C31, R20, R21, R22, R23 | Copy with its top-layer pours and the GND patch on inner layer 2 (L4) under it |
| BUCK1V8 | U6, L4, C32, C33, TP21 | |
| LOAD | R34, R35, C49, C50, D3, TP35, R11 (DNP) | U9 became U11 (TPS26621, `Package_SON:Texas_DRC0010J`): place and route U11 fresh |
| **New:** BUCK5V | U10, L6, C53–C58, R37–R40, TP38 (5V_PI) | A copy of BUCK3V3 (D13): reuse U5's copper pattern for U10's cell where the parts match, and give U10 extra copper and vias for heat (≈ 0.53 W at 1 A, `docs/design-review/power_budget.md` §3) |
| **New:** PI | J1, JP1, R26, R27, R43 | J1 position fixed (§3) |
| Test points | TP8, TP19, TP20, TP24, TP36 | Next to their nets, bottom side as on the mote |
| **New:** misc | U11, R41, R42, J5, D8–D10, R44–R46, JP2, FID1–FID6 | |

Mote parts not on the shield: anything not in our netlist (for example U7, U8, U9, J3, J4, P1, Y2, L5, D6, D7, R9, R10
and the processor's passives and test points). Place only what the netlist has.

## 6. Routing rules

| Class | Nets | Width | Clearance | Notes |
|---|---|---|---|---|
| Bus DC path | BM1_P, BM1_N, BM2_P, BM2_N between insert and inductor | ≥ 1.0 mm (mote 1.0–2.0 there) | 0.35 mm | New routing (the inserts moved), short and wide. The data legs to T1/T2, the TVS legs and the 0.2 mm test-point taps keep the mote's widths (0.2–0.5 mm) |
| Power | VBUS, P_IN rail copper | ≥ 0.5 mm + plane | 0.25 mm | As the mote: P_IN on L5 under port 2's side, VBUS band + under port 1. R8/U4 sense legs and small decoupling stubs keep the mote's 0.2 mm |
| Payload | VBUS_OUT | ≥ 0.6 mm (mote) | 0.25 mm | U11 → J5 |
| Pi 5 V | 5V_PI, PI_5V | ≥ 1.0 mm or a pour | 0.25 mm | U10 → JP1 → J1 pins 2/4; 1 A continuous (D15) |
| Switch nodes | 3V3_Buck_SW and U10's | as the mote's U5 cell | | Smallest loop; GND patch below |
| ADIN data pairs | BM1/BM2_DATA_P/N | 0.2 mm | | Layers as the mote (L1 + L2, two vias each) over unbroken GND; **no longer than the mote's** (port 1 ≤ 9.5 mm, port 2 ≤ 21.3 mm) |
| Signals | everything else | 0.2 mm (0.15 in fan-out) | 0.15 mm | |

These widths and clearances are the brief's defaults for **new routing**, taken from the mote where it shows them;
copied block copper keeps Sofar's widths exactly. Never go below the mote's own sizes; vias 0.45/0.2 mm or larger, through-hole only (as the mote).

**Planes (copy Sofar's structure, per Nick):** L3 near-solid GND with a slot past each PoDL inductor that joins the rest
of the plane only on the far side (as the mote's two slots); L5 split as the mote (P_IN, VBUS, 3V3, ADIN_AVDD and
ADIN_VDDIO islands under U1, and Sofar's two unconnected islands, Sofar Q10); planes pulled back 4.8 mm from each insert.
Keep R12, R13, R17, R19 fitted and placed as on the mote (Sofar Q9 is open). Describe how you mapped the slots and
islands onto the new geometry.

## 7. Method and milestones

Run autonomously through M0–M5; commit after each, with renders in `out/` and an entry in `LOG.md`.

| | Milestone | Done when |
|---|---|---|
| M0 | Workspace, schematic copy, board with every footprint and net | DRC parity: no missing or extra footprints (H1–H4 board-only) |
| M1 | Outline, J1, holes, inserts with Sofar's copper, J5, inductor envelopes | A script checks every §3 position and §4 keep-out; top/bottom renders |
| M2 | All parts placed (blocks rigid, transforms recorded in `blocks.json`) | Courtyard overlaps 0; bottom heights ≤ 3 mm (datasheet or 3D model; flag unknowns) |
| M3 | Block copper copied | `tools/blockcheck.py` (you write it): each block's tracks, vias and pads match the mote after the inverse transform within 0.001 mm; per-block matched / missing / extra |
| M4 | Remaining routing, planes, zone fill | Unrouted 0 |
| M5 | Clean-up and report | §8 all pass, `REPORT.md` written |

Push the branch and open a **draft** PR titled `EXPERIMENT (do not merge): fable layout 01`.

## 8. Pass criteria

1. `$K pcb drc --schematic-parity --severity-all` → 0 errors, 0 unconnected items, 0 parity issues (any exclusion has a
   written reason in `REPORT.md`).
2. §3 positions within ±0.05 mm; J1 pin 1 proven at (25.23, 8.37) from the top.
3. §4 keep-outs, 2 mm around both inductor envelopes, bottom parts ≤ 3 mm.
4. `blockcheck.py`: copied blocks 100 % matched (or each difference explained).
5. §6 widths on new routing (copied copper is judged by item 4); ADIN pairs no longer than the mote's; R8's sense connections identical; insert arcs and via rings identical.
6. Renders: every copper layer with `tools/render_layers.py` for the mote and the shield, plus `kicad-cli pcb render`
   top and bottom.

## 9. Report (`REPORT.md`)

Final board size and why; a table of blocks with their transforms and fidelity results; DRC summary; every deviation from
the mote and why; what was hard, where you guessed, what you would do with more time; open questions for Nick and for
Sofar.

## 10. Later, not in this experiment: the OpenMV N6 version

Same 46 × 65 outline, inserts, J5 and M3 housing holes, so one housing fits both. The N6 (≈ 35.6 × 44.5 mm, two 2×8
headers near one end, positions approximate from OpenMV's pinout image) replaces the Pi and J1: it sits on the bottom,
camera looking out (away from the shield), with the inductors on the opposite (top) side. Its west header would hit the
port-1 inserts if centred where the Pi sits, so it is **staggered about 4.2 mm east** of the Pi's centre, and L1 moves
about 4.2 mm east into the room J1 leaves. Confirm against OpenMV's STEP model when that version starts.

## 11. Assumptions to confirm (Nick)

- The outline is centred on the Zero east–west as drawn here (west flange 7.5 mm, east 8.5 mm), and Nick's User.3 notch is
  placed by centring his 31.5 mm outline on the 30 mm Pi (§2).
- The notch's east end sits ≈ 2.76 mm from the north-east M2.5 standoff's centre: confirm it clears the standoff and screw.
- The stacking header is this experiment's assumption; the real J1 part (D6's plain socket or a stacking header) is still
  Nick's choice.
- Bottom-side part height ≤ 3 mm; the exact stacking header part is still open (J1 in the BOM).
- Within each pair "+" is north of "−".
