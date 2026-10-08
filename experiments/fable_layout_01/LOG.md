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
