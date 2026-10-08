# LOG — layout experiment 01

*One entry per milestone, newest last. Board frame = KiCad board coordinates (mm): the Pi Zero's north-west corner is
(0, 0), x east, y south (BRIEF §2), so KiCad shows the brief's numbers directly.*

## M0 — workspace, schematic copy, board from the netlist (2026-10-07)

- Branch `experiment/fable-layout-01` from `main` (a5f812c). Copied `nereus_Pi_shield_ADIN2111/` (7 sheets, .kicad_pro,
  lib tables, 2 .kicad_sym, mote.pretty, nereus.pretty) into `board/`, without the old `.kicad_pcb`.
- **No schematic edit.** The brief's one allowed edit (J5 → Molex Micro-Fit) was made and then reverted on Nick's
  instruction (2026-10-07: "use the JST footprint like in the schematic, not the molex in the brief"), so `board/`
  holds the live schematic unchanged: J5 = SM02B-GHS-TB, `Connector_JST:JST_GH_SM02B-GHS-TB_1x02-1MP_P1.25mm_Horizontal`.
  ERC on the copy: `ERC messages: 494  Errors 0  Warnings 494`, the same as the live project. Netlist: 134
  components, 109 nets.
- `tools/build_board.py` (pcbnew): new board, 6 copper layers with the mote's names and roles (Top Layer, Internal 1,
  GND Plane [power], Internal 2, PWR Plane [power], 6 Bottom Layer), 1.6 mm. Every netlist component gets its footprint
  from `Vault` / `nereus` / the stock KiCad 9 libraries, its schematic path, DNP (R11) and exclude-from-BOM flags, and
  every numbered pad its net (the only numbered pads without a schematic node are J5's two mechanical tab pads `MP`, which carry no net). H1–H4 `MountingHole_2.7mm_M2.5` added as
  board-only footprints at the §3 positions. 138 footprints. Parts parked on a grid at x ≥ 70 mm for now.
- Board rules in the `.kicad_pro` (plain JSON edit): min track 0.15, via 0.45 / drill 0.20 (BRIEF §6: the mote's own
  0.45 vias and 0.254 drills must pass), hole clearance 0.25, edge clearance 0.5; one netclass `Default` 0.2 / 0.2 /
  via 0.6–0.3 (Sofar's values; the imported duplicate "All Nets" class dropped). The brief's larger widths and
  clearances for **new** routing are enforced by the experiment's own check script (M4), so that Sofar's copied
  0.2 mm copper is not flagged by DRC.
- Check: `kicad-cli pcb drc --schematic-parity --severity-all` → `out/m0/drc_summary.txt`. Parity: **no missing or
  extra footprints**; 4 `net_conflict` warnings "No pad found for pin 1" on MP1–MP4 — Sofar's insert footprint has no
  numbered pad (SPEC fact, Sofar Q6), expected and carried as a known item. The 272 other items are the parked grid
  (overlaps, no outline yet) and the usual import leftovers; they are M1/M2's job.
- Render: `out/m0/render_top.png` (parked grid).
- Stackup: pcbnew's Python has no stackup API; a standard 6-layer 1.6 mm build is written into the board file's setup
  in M1 and noted as an assumption (Sofar Q11).

## M1 — outline, J1, holes, inserts with Sofar's ring copper, J5, envelopes (2026-10-07)

- **Pipeline:** `tools/build_all.sh [m1|m2|…]` rebuilds the board from the schematic every time (M0 build, then
  `m1_fixed.py`, `m2_place.py`, …). No script edits a board in place: a first attempt at an idempotent M1 (remove the
  previous run's items, redraw) crashed KiCad's Python (segfault in `board.Remove`, crash report from Nick 22:39), so
  the pipeline is the only way the board changes. Milestone outputs: `out/m<n>/` (DRC summary, renders, layer SVGs).
- **Frame:** board coordinates = the brief's frame (Pi NW corner (0,0), x east, y south); aux origin at (0,0).
- **Outline** 46 × 65 mm, r 3 corners, on Edge.Cuts (x −7.5…38.5, y 0…65). **Stackup** written into the board file:
  generic 6-layer 1.6 mm (35 µm copper ×6, FR4 prepreg 0.21 ×3, core 0.38 ×2; assumption, Sofar Q11).
- **J1** flipped to the bottom, orientation 180 (KiCad mirrors a flipped footprint's local y; the 180 puts pin 2 east and
  the pins south). Proven by pads: pin 1 (25.230, 8.370), pin 2 (27.770, 8.370), pin 39 (25.230, 56.630), pin 40
  (27.770, 56.630), seen from the top.
- **Holes:** H1–H4 (board-only, M2.5) and MTG1–MTG4 (Vault Hole_M3) at the §3 positions. The M3 silk circle (r 4.0)
  is clipped to the arcs that lie ≥ 0.3 mm inside the outline (per instance). MTG courtyards (±4.25) cross the outline
  at the corners and overlap H1/H3's courtyard by 0.25 mm (both positions are the brief's): 2 `courtyards_overlap`
  errors to exclude with that reason in M5.
- **Inserts:** MP1–MP4 at x −1.81, y 12.0 / 21.4 / 43.6 / 53.0, bottom side, Sofar's footprint orientation (176°).
  Their contact copper is **Sofar's MP1 ring copied by translation** (blocks RING_MP1…4 in `blocks.json`, via
  `tools/motecopy.py`): one C arc r 3.03 mm, 1.2 mm wide, 290°, on Top Layer, gap facing the west edge, plus seven
  0.6/0.254 mm vias at r 3.0 mm, on the insert's bus net (BM2_P, BM2_N, BM1_P, BM1_N north → south). The import's
  zero-size NPTH pad on the insert footprint is given its drill size (4.4 mm) on the four board instances
  (`padstack_invalid` on the mote; 4 `lib_footprint_mismatch` warnings as a result). Insert pull-back: four rule
  areas r 4.8 mm "no copper pour" on all six copper layers (tracks allowed, so the bus feed can enter the ring).
- **J5** (JST GH, per Nick) at (15.0, 61.8), rotation 0: housing front 0.75 mm inside the south edge, tab copper 0.5 mm
  from it, centred at x 15.0 between the Pi's south holes.
- **Envelopes:** L1/L2 centred in their 15.5 × 15.5 envelopes at (12.74, 44.25) / (12.74, 16.75), top side, Sofar's
  90° for now (M2 may rotate the port blocks); envelope rectangles on Eco1.User, +2 mm clearance on Eco2.User.
- **Check:** `tools/check_fixed.py` → every §3 position within 0.001 mm, J1 pins proven, rings verified (arc
  radius/width/angle/net, 7 vias 0.6/0.254), keep-outs clear (holes are not "parts"; 122 parts still parked). 0 failures.
- **DRC** (`out/m1/drc_summary.txt`): on placed items the only errors are the insert contact as Sofar drew it
  (28 `shorting_items`: bus via in the net-less insert pad; 36 `hole_clearance`: arc/vias 0.23 mm from the 4.4 mm
  hole, as on the mote; 8 `solder_mask_bridge`) and the 2 MTG/H courtyard overlaps; the rest is the parked grid.
  Parity unchanged (MP1–4 pin 1, Q6).
- **Renders:** `out/m1/render_top.png`, `render_bottom.png`, `out/m1/layers/*.svg`.
