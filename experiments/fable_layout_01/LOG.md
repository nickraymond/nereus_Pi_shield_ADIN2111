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

## M2 — all parts placed; blocks rigid, transforms in blocks.json (2026-10-07)

- **Where the brief's blocks could not stay whole** (the fixed items leave three strips: the band between the inductor
  envelopes, 8.0 mm tall; the strip east of J1, 8.9 mm wide; the west pocket, 10.0 mm wide):
  - PORT1/PORT2: the transformer cluster sits 9.6 mm from the inductor's centre on the mote, inside the 50 W envelope +
    2 mm, so each port is two rigid pieces: **P1L/P2L** = inductor + the bottom-side parts Sofar put under it (D4, R12,
    R13, TP3, TP5 + C17, D2 under L1; D5, R17, R19, TP7, TP13 + C26 under L2) and **P1T/P2T** = T1/T2 with C16, C18,
    C19, R14 / C24, C25, C27, R18, in the band. The inductor–transformer copper becomes new routing (M4).
  - BUCK3V3: the U5 cell (U5, C30, L3, the bottom-side C28, C29, R20–R23, its pours and In3 GND patch) is 8.55 mm wide
    and fits the strip; the output cap **C31** is placed beside it (with C31 the cell is 9.65 mm). **B5V** is the same
    cell copied again with its parts mapped by function (U10, C55, L6, C53, C54, R39, R37, R40, R38; checked by nets);
    C56/C57/C58/TP38 placed on the bottom under L6.
  - SPINE: **SENSE** = R8 + U4 + R7 + C15 + TP22 with C23 above them (Sofar's sense routing stays), rotated 90 in the
    strip; **DAMP1** = C21 + R16 (+ C20, TP23) in the south-west pocket; **DAMP2** = C22 in the strip with R15 beside it
    (R15 would have landed under J1 or off the edge); D1 in the south-east pocket; C17/D2 and C26 ride under L1/L2.
  - ADIN: whole, in the west pocket (option (a)), **rotated 90** so port 1's data pins face north toward T1 (≈ 5 mm) and
    port 2's face south (T2 reached under the band, ≈ 18 mm); U1's courtyard x −6.3…2.9 stays west of the envelope
    clearance line (2.99) and ≥ 4.8 mm from both inserts. U2 ends 4.95 mm from MP1 (the tightest spot).
  - BUCK1V8 (**B18**, all bottom) under the band east of T2; LOAD placed fresh around U11 at the strip's south end.
- **Interpretation recorded (for Nick):** the 2 mm envelope clearance is applied to top-side parts; bottom-side parts
  may sit under an inductor as Sofar placed them (the 50 W part is a top-side volume). Without this the port blocks
  could not be copied at all.
- Fresh parts: LEDs D10/D8/D9 north→south in a column at the band's east end (x 20.3) with JP2 and R44–R46 under them;
  JP1 on the bottom beside J1 pins 2/4 (no room on top: cut before stacking); R26/R27, TP20, TP24 bottom east of J1;
  D1 (SE pocket), fiducials FID3/4/5 top and FID1/2/6 bottom at (8, 2.5), (21.5, 2.5), (15, 56).
- Heights: `heights.json` (datasheet maxima per footprint; J1 exempt as the stacking socket). Every bottom part ≤ 1.5 mm.
- Checks: `check_fixed.py --heights` 0 failures (positions, keep-outs, envelope clearance, heights); DRC
  `out/m2/drc_summary.txt`: **courtyard overlaps 12** = the 2 MTG/H pairs (M1) + **10 pairs inside Sofar's own blocks**
  (U4/C15, U4/R7, TP22/R8, TP5/R13, R12/D2, C10/TP1, C4/C12, TP21/U6, U5/C30, U10/C55): Sofar's placement with the
  courtyards S6.c added; copying rigidly keeps them (to exclude with that reason). 4 clearance errors are T1/T2's
  unnumbered footprint pads lying on pads 3/4 (Sofar's footprint, as on the mote). Default netclass clearance set to the
  brief's 0.15 mm for signals (§6); larger classes are enforced on new routing by script (M4).
- Renders: `out/m2/render_top.png`, `render_bottom.png`.

## M3 — block copper copied; blockcheck 100 % (2026-10-07)

- `tools/m3_copy.py` copies every block's tracks, vias and island pours with the block transform through
  `motecopy.select` (one selection rule shared with the checker): copper on the block's pad nets inside its region
  rect(s), tracks crossing a rect boundary clipped at it (the stub is where new routing continues), zones only when
  wholly inside (ADIN_VDDIO / ADIN_AVDD islands under U1; the U5 cell's switch-node pour, its In3 GND patch and the
  3V3 output pour clipped at the strip edge). The big GND / VBUS / 3V3 / P_IN planes are M4's. Nets mapped by pad.
- `tools/blockcheck.py` → `out/m3/blockcheck.md`: **1,064 items, 0 missing, 0 extra** within 0.001 mm (pads 385/385,
  tracks 660/660, arcs 4/4, vias 207/207, zones 6/6). The ring blocks copied in M1 are checked the same way.
- What the checker caught on the way: KiCad silently re-nets a copied via or track that lands on a pad of another net
  (it reports the item on the pad's net), so three fresh parts that sat on copied copper (R15, C57, TP24) showed up as
  "missing" with the wrong net; they were moved to spots proven free against the copied vias. B5V's rows were sat on
  B33's clipped stubs the same way; the strip stack is B33 7.8–20.25, C31 beside U5, B5V 21.5–33.95, SENSE 35.5–43.0,
  DAMP2 43.3–52.1, U11 row 52.3–56.3 (y, mm).
- Regions were tightened so clipped stubs stay ≥ 0.5 mm from the east edge (B33/B5V x ≤ 146.4 mote, SENSE y ≤ 120.2,
  DAMP2 y ≤ 107.0) and P2T's bus-leg stubs no longer reach the LED column (x ≥ 133.0).
- B18 rotated 90 east of L1 beside J1 (its 1V8 copper hit D2 under L1); LEDs at x 21.5 with JP2/R44–R46 under them.
- DRC `out/m3/drc_summary.txt`: unconnected 216 (M4); errors only in the known groups: insert contact (28 shorting,
  36 hole-clearance, 8 mask-bridge, 4 padstack), T1/T2's unnumbered pads (4 clearance, 6 shorting, 10 mask-bridge,
  as on the mote), courtyards 12 (10 Sofar intra-block + 2 MTG/H).
- Renders: `out/m3/render_top.png`, `render_bottom.png`, `out/m3/layers/*.svg`.

## M4 — planes, routing, zone fill (2026-10-08)

- **Planes** (`tools/m4_route.py planes()`): GND on In2 (0.5 mm from the edge) with one 0.5 mm slot past each
  inductor on the band side and one on the outer side (port 2: y 6.5–7.0 and 26.2–26.7; port 1: 39.0–39.5 and
  54.0–54.5, x −7.5…22.7), so each inductor island joins the plane only on its east (far) side; the insert pull-backs
  (r 4.8, M1) cut both planes. PWR plane In4 split: VBUS (the strip east of J1, the whole west half from y 26 down, and
  port 2's east x 16.8–23.2), P_IN island under port 2's east half (x 11–16.6, y 8–25.7; R8 straddles the boundary),
  a 3V3 island at the 3.3 V buck output (x 33.4–38, y 8–23), the copied ADIN_AVDD / ADIN_VDDIO islands (priority 7)
  and Sofar's two no-net islands (NoConnect_P2 / _P1, 6 × 6.5 mm between each port's inserts and its inductor, Q10).
  5V_PI is a bottom-side pour x 29.7–38, y 7.5–26.5 from L6's output to JP1 (BRIEF §6 "≥ 1.0 mm or a pour").
- **Router** (`tools/router.py`, pure Python, no numpy in KiCad's Python): 0.1 mm grid, four routing layers (Top,
  Internal 1, Internal 2, Bottom), through vias; every existing copper item stamped with its net and dilated per class
  (strict halos, pre-existing copper inflated by half a cell diagonal so off-grid vias and pads keep their clearance);
  exact board-edge distance map; A* per cluster pair from the whole copper cluster (copied stubs count), 8-way except
  the 0.15 mm fan-out class (orthogonal only). Classes (§6): bus 1.0/0.35, power 0.5/0.25, Pi 5 V 1.0/0.25, payload
  0.6/0.25, rail 0.3/0.15, signal 0.2/0.15, fan-out 0.15/0.15; fallbacks to the next class are logged.
- **Order:** insert feeds by hand (1.5 mm, Top, ring → inductor bus pad); the ADIN pairs on Top + Internal 1 (inner
  pin first); two hand-laid 0.15 mm links (U11 pin 7 → R34, U11 pin 1 → a via into the VBUS plane) and U3's 3V3 escape
  on Internal 2 between Sofar's vias; GND pads given a via within 1.2 mm (except in the ADIN pocket); U11's west-side
  signals; the rest short-first; then stitching vias from every plane-net cluster into its plane (up to 16 spots
  tried); plane leftovers by track; zone fill; split pour islands joined and refilled.
- **Result** (`out/m4/routing.json`, `drc_summary.txt`): 216 open connections → **2**: U3's 3V3 (its hand-laid escape
  reaches (2.5, 38.0) on Internal 2 but no path continues: the pocket's south exit is shared with the port-2 pair,
  1V8 and ADIN_PWR) and J1 pins 1/17, which the schematic puts on one no-connect net (`unconnected-(J1-3V3-Pad1)`, the
  Pi's 3V3: SPEC constraint 4, left open on purpose). 72 stitching vias. ADIN pairs: BM1 7.9 / 9.4 mm (≤ 9.5), BM2
  21.3 / **23.4** mm (≤ 21.3: N is 2.1 mm over; P/N skew 2.1 mm vs the mote's 3.0). DRC errors are only the known
  groups (insert contact 92, T1/T2 footprint pads 22, courtyards 12) — see M5 exclusions; blockcheck still 0 missing.
- **What did not work, kept in the script behind flags:** rip-up rounds (RIPUP_ROUNDS) thrashed; routing the pocket's
  nets first or stitching before the signals each boxed a different net in. The ADIN pocket (U1 rotated into the
  10 mm west pocket) has three exits — the one-track lane along the west edge, the strip north of the pins and the
  strip south of U2/U3 — for ten nets; this is the layout's weak spot (REPORT).
- Placement changes made for routing (all in `tools/m2_place.py`): T1 at (8.7, 28.4), T2 at (16.0, 32.3), the ADIN
  block 0.3 mm east (allowance recorded), U11's group 1 mm east with R34/R41 on the top beside it, R35 bottom at
  (17.5, 58.5), D3/C50 under U11's thermal-pad side, R15 beside C22, R26/R27/TP24/TP20/C56–C58/TP38 in via-free spots.
- Renders: `out/m4/render_top.png`, `render_bottom.png`, `out/m4/layers/*.svg`.
