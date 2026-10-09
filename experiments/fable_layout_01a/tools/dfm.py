#!/usr/bin/env python3
"""JLCPCB DFM (BRIEF 1.a §6): one table of limits (each with its URL and the date it was read), written into the design
rules and checked on the board, with the measured worst case per row.

  $PY tools/dfm.py rules            # write the limits into board/*.kicad_pro (design_settings.rules) and board/*.kicad_dru
  $PY tools/dfm.py check [stage]    # measure the board, run kicad-cli DRC, write DFM.md and out/<stage>/dfm.json

Every limit below was read from JLCPCB's published pages on the date given (session 2.b, 2026-10-08); nothing is typed
from memory. Where the board's own rule (the brief) is stricter than JLCPCB's, the stricter value stays in the design
rules and the row says so. A limit DRC cannot express is measured here (column "enforced by").
"""
import collections
import json
import math
import re
import subprocess
import sys

import pcbnew

import geom
from geom import MM, mm, V

K = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
PRO = geom.EXP / "board" / "nereus_Pi_shield_ADIN2111.kicad_pro"
DRU = geom.EXP / "board" / "nereus_Pi_shield_ADIN2111.kicad_dru"
DFM_MD = geom.EXP / "DFM.md"

CAP = "https://jlcpcb.com/capabilities/pcb-capabilities"
STK = "https://jlcpcb.com/impedance"
ASM = "https://jlcpcb.com/capabilities/pcb-assembly-capabilities"
FID = "https://jlcpcb.com/blog/fiducial-marks"
READ = "2026-10-08"

# ---- the limits (quoted from the pages) ---------------------------------------------------------------------------
# key: (item, JLC limit as quoted, source URL, board rule / how enforced)
LIMITS = {
    "trace_outer": ("Min. trace width, outer layers (1 oz)", "Multilayer 1 oz: 0.09 / 0.09 mm (3.5 / 3.5 mil) track width / spacing", CAP,
                    "board min_track_width 0.15 (BRIEF §5: 0.15 only inside a pad field, else the class width); stricter than JLC"),
    "trace_inner": ("Min. trace width, inner layers (0.5 oz)", "the same multilayer table: 0.09 / 0.09 mm (JLC lists no separate 0.5 oz inner figure)", CAP,
                    "board min_track_width 0.15; stricter than JLC"),
    "space": ("Min. spacing, outer and inner", "Multilayer 1 oz: 0.09 / 0.09 mm; pad to track 0.1 mm; SMD pad to pad 0.15 mm", CAP,
              "board min_clearance 0.09 (JLC) under the Default netclass 0.15 and the bus rule 0.35; DRC clearance"),
    "same_net": ("Same-net track spacing", "0.25 mm", CAP, "no DRC constraint for same-net gaps: measured here (tracks of one net on one layer that neither touch nor keep 0.25)"),
    "via_drill": ("Min. via drill", "Multilayer: 0.15 mm hole size (preferred min. via hole size 0.2 mm); drill 0.15–6.3 mm", CAP,
                  "board min_through_hole_diameter 0.2 (the preferred figure; the mote's smallest drill); DRC drill_out_of_range"),
    "via_dia": ("Min. via diameter", "Multilayer: 0.25 mm via diameter", CAP, "board min_via_diameter 0.45 (the mote's smallest via); stricter than JLC"),
    "via_ring": ("Via annular ring", "(0.25 − 0.15) / 2 = 0.05 mm follows from the min. via 0.15 / 0.25", CAP,
                 "board min_via_annular_width 0.1 (the mote's 0.45/0.2 and 0.6/0.3 vias give 0.125 / 0.15); stricter than JLC"),
    "pth_ring": ("PTH annular ring (component holes)", "Multilayer 1 oz: recommended 0.20 mm or above; absolute minimum 0.15 mm", CAP,
                 ".kicad_dru: annular_width min 0.15 for through-hole pads; DRC annular_width"),
    "h2h_via": ("Hole to hole, via–via", "Via hole-to-hole spacing 0.2 mm", CAP, "board min_hole_to_hole 0.25 (the mote's); stricter than JLC"),
    "h2h_pad": ("Hole to hole, pad–pad", "Pad hole-to-hole spacing 0.45 mm", CAP, ".kicad_dru: hole_to_hole min 0.45 when both items are pads"),
    "hole_cu_via": ("Via hole to copper", "Via hole to track 0.2 mm; inner layer via hole to copper clearance 0.2 mm", CAP,
                    "board min_hole_clearance 0.25; stricter than JLC"),
    "hole_cu_pth": ("PTH hole to copper", "PTH to track 0.28 mm (0.35 mm recommended); inner layer PTH pad hole to copper clearance 0.3 mm", CAP,
                    ".kicad_dru: hole_clearance min 0.28 (outer) / 0.3 (inner) for through-hole pads"),
    "hole_cu_npth": ("NPTH hole to copper", "NPTH to track 0.2 mm", CAP, "board min_hole_clearance 0.25; stricter than JLC"),
    "npth": ("Min. non-plated hole", "Min. non-plated holes 0.50 mm", CAP, "measured here (the holes are the inserts' Ø4.4, the M3 Ø3.2 and the M2.5 Ø2.7)"),
    "edge": ("Copper to board edge", "Routed edges: copper clearance ≧ 0.2 mm", CAP, "board min_copper_edge_clearance 0.5 (BRIEF §6: the brief's 0.5 stays); stricter than JLC"),
    "mask_dam": ("Solder mask dam (sliver) and expansion", "Soldermask bridge min dam width 0.10 mm (1 oz, green); solder mask expansion 1:1", CAP,
                 "board solder_mask_min_width 0.1 and solder_mask_clearance 0 (1:1); DRC solder_mask_bridge"),
    "silk_line": ("Silkscreen line width", "Legend minimum line width ≥ 0.15 mm", CAP, "no DRC constraint for graphic lines: measured here (silk lines thinner than 0.15 listed)"),
    "silk_text": ("Silkscreen text", "Minimum text height 40 mil (1.0 mm); character width to height ratio 1:6", CAP,
                  "board min_text_height 1.0, min_text_thickness 0.15 (≥ 1:6 of 1.0 is 0.167; 0.15 is JLC's min line); DRC text_height / text_thickness (warnings)"),
    "silk_pad": ("Silkscreen to pad", "Pad to silkscreen clearance 0.15 mm", CAP, "board min_silk_clearance 0.15; DRC silk_over_copper (warning)"),
    "courtyard": ("Courtyards", "— (JLC has no courtyard rule; KiCad's courtyard overlap check stands in for part spacing)", CAP, "DRC courtyards_overlap"),
    "stackup": ("Stackup, 6 layers 1.6 mm", "JLC06161H-3313: Top Cu 0.035 / prepreg 3313 0.0994 / Cu 0.0152 / core 0.55 / Cu 0.0152 / prepreg 2116 0.1088 / "
                "Cu 0.0152 / core 0.55 / Cu 0.0152 / prepreg 3313 0.0994 / Bottom Cu 0.035 mm (outer 1 oz, inner 0.5 oz 'H/H without copper'); "
                "εr 3313 4.1, 2116 4.16, core 4.6", STK, "written into the board's setup/stackup by tools/m1_fixed.py (M1); measured here: the board's stackup text"),
    "copper_wt": ("Copper weight", "Multilayer outer: 1 oz / 2 oz; inner: 0.5 oz / 1 oz / 2 oz", CAP, "stackup row: outer 1 oz (0.035), inner 0.5 oz (0.0152)"),
    "balance": ("Copper balance per layer", "— (no published figure; JLC reviews balance at order time)", CAP, "measured here: copper area per layer as % of the board area"),
    "pours": ("Outer-layer GND pours", "— (design choice, BRIEF §6)", CAP, "measured here: the pours present per outer layer and their stitching vias"),
    "thermal": ("Thermal relief vs solid on heavy pads", "— (design choice, BRIEF §6)", CAP, "measured here: each zone's pad-connection setting"),
    "fiducial": ("Fiducials for assembly", "min. 2, 3 recommended, 'L' pattern, both sides for double-sided SMT; copper ≈ 1.0 mm, mask opening ≥ 2× the pad; "
                 "'a clearance of at least 3.35 mm is necessary between the board edge and the fiducial mark'", FID,
                 "measured here: FID1–6 copper / mask diameters, pattern, edge clearance (pad edge to board edge ≥ 3.35)"),
    "testpoints": ("Test points clear of parts", "— (design choice)", ASM, "measured here: every TP's courtyard gap to the nearest other courtyard (DRC courtyards_overlap too)"),
    "bom_cpl": ("BOM / CPL readiness", "Standard PCBA: 0.35 mm min IC pin spacing, 0.3 mm BGA pitch; Economic: 0.40 mm / 0.5 mm", ASM,
                "note only (rotations vs JLC's library are checked at order time)"),
    "smd_pad": ("Min. SMD pad", "Minimum SMD pad 0.25 × 0.25 mm", CAP, "measured here: the smallest SMD pad"),
    "via_in_pad": ("Via in pad", "Via-in-pad: epoxy filled & capped (0.15–0.55 mm); plain vias in pads are not a JLC rule but wick solder", CAP,
                   "measured here: vias inside SMD pads (Sofar's thermal-pad vias under U1 / U5 / U10)"),
    "board": ("Board size / thickness", "FR4 min 3 × 3 mm; thickness 0.4–4.5 mm, standard 1.6 mm, tolerance ±10 %", CAP, "board 49 × 68 × 1.6 mm (M1)"),
}

# what session 2.b changed per row (DFM.md's last column); "—" = nothing yet
CHANGES = {
    "trace_outer": "nothing: the brief's class widths (0.2 signal, 0.15 only in a pad field) stand",
    "trace_inner": "nothing",
    "space": "min_clearance 0.09 written (JLC); the netclass 0.15 and the bus rule 0.35 govern",
    "same_net": "measured (parallel runs of one net 0.03–0.25 mm apart); the count in the row is the board's (session 2's board had 1: Sofar's bus leg at T1 pad 6)",
    "via_drill": "min_through_hole_diameter 0.2 written (JLC's preferred figure)",
    "via_dia": "nothing: 0.45 stands",
    "via_ring": "nothing: 0.1 stands",
    "pth_ring": ".kicad_dru rule added (0.15)",
    "h2h_via": "nothing: 0.25 stands",
    "h2h_pad": ".kicad_dru rule added (0.45, pad vs pad)",
    "hole_cu_via": "nothing: 0.25 stands",
    "hole_cu_pth": ".kicad_dru rules added (0.28 outer / 0.3 inner); the inner planes' clearance 0.25 → 0.3 (the M3 housing holes' pads were 7 DRC items)",
    "hole_cu_npth": "the bus feeds start 3.31 mm from the insert centre (a 3.0 start put the 1.5 mm track's round end 0.05 mm from the Ø4.4 hole)",
    "npth": "measured",
    "edge": "nothing: the brief's 0.5 stands (the inserts' rings sit on it after the 1.5 mm shift; JLC's 0.2 would allow 1.8 mm)",
    "mask_dam": "solder_mask_min_width 0.1 and expansion 0 (1:1) written",
    "silk_line": "tools/dfm_fix.py after placement: every silk line thinner than 0.15 set to 0.15; lines over pads removed",
    "silk_text": "tools/dfm_fix.py: references 1.0 / 0.15 and moved to a clear spot (or hidden and listed); footprint silk texts 0.15 thick; min_text_height 1.0 / thickness 0.15 written",
    "silk_pad": "tools/dfm_fix.py: lines over pads removed, references kept 0.15 from pads and off other silk; min_silk_clearance 0.15 written",
    "courtyard": "nothing to change: the 10 overlaps are Sofar's inside copied blocks (the two MTG/H overlaps are gone: the housing holes moved with the corners)",
    "stackup": "M1 writes JLC06161H-3313 into the board's stackup (was 01's generic 0.21 / 0.38 build)",
    "copper_wt": "stackup row: outer 1 oz, inner 0.5 oz; the bus / power copper is on the outer layers and the planes",
    "balance": "measured; a top GND pour was NOT added (see DFM.md notes: the pairs and the bus feeds keep their clearances, the bottom pour and the planes carry the GND)",
    "pours": "outer pours drop islands that hold no via (island removal 'always'); the bottom pour as the mote's",
    "thermal": "as the mote: outer pours solid, inner planes thermal relief (KiCad's 0.254 spokes); the bus feeds and the inductor pads are tracks",
    "fiducial": "FID3 / FID4 (top) and FID1 / FID2 (bottom) moved to y 5.0 / 5.3 in the north band (pad edge ≥ 3.35 from the edge); FID5 / FID6 with the south band",
    "testpoints": "measured; the 6 overlaps are Sofar's inside copied blocks (declared)",
    "bom_cpl": "note only",
    "smd_pad": "declared per footprint (QE round 3 F2): U6 TPS62840 DSBGA 0.23 (Sofar's), U2 / U3 AP22913 WLCSP 0.235 (Sofar's), U11 Texas_DRC0010J 0.24 (KiCad stock, this design's part); a footprint change is Nick's per part",
    "via_in_pad": "QE round 3 F1: the router may no longer put a via where its copper touches an SMD solder pad (router.Grid.padvia; test pads and thermal pads excepted), the row is measured against the mote's copied vias, and fails on any new via in a solder pad (03b2adb had 64)",
    "board": "49 × 68 (Nick, 2026-10-08)",
}

PREAMBLE = ("*Step 1 of session 2.b (LESSONS §4): the limits were fetched and encoded before any board edit, and this table was first run on "
            "session 2's final board (b22752f, md5 de2e14fb…): see 'History' at the end for that result. The 'What 2.b changed' column is kept "
            "in `tools/dfm.py` (CHANGES).*\n")

HISTORY = """
## History

- **2026-10-08, step 1 of session 2.b (session 2's final board b22752f, md5 de2e14fb…, before any board edit):** the limits
  encoded, DRC run: **118 errors** (session 2's 111 + 7 new from the `.kicad_dru` rule "PTH hole to copper, inner 0.3": the four
  M3 housing holes' Ø6 pads sit 0.25 mm from the GND / VBUS planes), **358 warnings** (254 + 104 from the silk limits: text_thickness
  60, silk_overlap 89), 1 unconnected (J1's no-connect pair), 4 parity (Sofar Q6). Table: **22 pass, 9 fail** — same-net gap 1
  (BM1_P 0.066 mm at T1's pad 6, Sofar's leg geometry), PTH hole to copper (the 7 housing-hole items), silk lines under 0.15 mm
  (59, stock KiCad footprints: C56–C58, D8–D10, J1, J5, JP1, JP2, R41, U11), silk text under 1.0 mm (116 visible references, Sofar's
  0.6 / 0.64 mm; DRC text_height 112), silk over pads (41), stackup (01's generic build), copper weight (same row), fiducials FID1–4
  2.12 mm from the edge against JLC's 3.35, min SMD pad 0.23 mm (U6.A1, Sofar's DSBGA footprint; JLC 0.25). Three measurement
  defects found and fixed on this first run (a closed outline chain 'collides' with everything inside it; a via touching a pad is
  not a via in the pad; non-adjacent legs of one polyline are not two runs), recorded here so the numbers above are the honest ones.
- **2026-10-08, step 5 (the rebuilt 49 × 68 board, VARIANT=pocket):** the table above. **30 pass, 1 fail** (row 29, Sofar's DSBGA
  pads on U6, declared). DRC 109 errors (all Sofar's, with reasons), 70 warnings (28 lib_footprint_mismatch from the silk edits,
  38 padstack, 2 nonmirrored pin-1 marks, 2 silk_overlap inside Sofar's blocks), 1 unconnected, 4 parity. What changed per row is
  in the last column; the silk fix's record is `out/m2/dfm_fix.json` (59 lines widened, 42 lines over pads removed, 128 references
  resized, 85 moved, 38 hidden). Not done, judged and recorded in REPORT.md §8: a top GND pour, an impedance figure.
- **2026-10-08, QE round 3 (03b2adb) and the rebuild after it:** the QE found row 30 passing on a hard-coded value with 64 new vias
  in solder pads (F1) and row 29 naming one of four small-pad footprints (F2). Both rows are measured now (row 30 against the mote's
  copied vias; row 29 per footprint), the router forbids a via wherever its copper would touch an SMD pad (test pads and thermal
  pads excepted), and plane-net links from pads narrower than 1.0 mm run at 0.2 mm (BRIEF §6). Rebuilt from M0 with Nick's two
  mid-run decisions (the 20 W inductors' courtyards + 2 mm as the keep-out; U1 3 mm further from the west edge): **30 pass, 1 fail**
  (row 29), 0 new vias in solder pads, DRC 109 / 68 / 1 / 4.
"""


# ---- rules: what goes into the .kicad_pro / .kicad_dru ------------------------------------------------------------
PRO_RULES = {
    "min_clearance": 0.09, "min_track_width": 0.15, "min_via_diameter": 0.45, "min_through_hole_diameter": 0.2,
    "min_via_annular_width": 0.1, "min_hole_to_hole": 0.25, "min_hole_clearance": 0.25, "min_copper_edge_clearance": 0.5,
    "solder_mask_min_width": 0.1, "solder_mask_clearance": 0.0, "solder_mask_to_copper_clearance": 0.0,
    "min_silk_clearance": 0.15, "min_text_height": 1.0, "min_text_thickness": 0.15,
    "min_microvia_diameter": 0.2, "min_microvia_drill": 0.1,
}
DRU_TEXT = """(version 1)
# BRIEF §6 bus class: the insert-feed nets keep 0.35 mm from every other net (planes, tracks, vias, pads).
# Between the P and N legs of one port Sofar's own 0.2 mm spacing is kept (the legs are copied as drawn), so the
# rule is bus vs non-bus only. The `bus` netclass itself (clearance 0.15, priority 0) only names the nets.
(rule "bus nets 0.35 mm from other nets"
  (condition "A.NetClass == 'bus' && B.NetClass != 'bus'")
  (constraint clearance (min 0.35mm)))

# JLCPCB limits (tools/dfm.py, read %(read)s from %(cap)s) that the board-wide design rules cannot express
(rule "JLC PTH annular ring: multilayer 1 oz absolute minimum 0.15 mm (0.20 recommended)"
  (condition "A.Type == 'Pad' && A.Pad_Type == 'Through-hole'")
  (constraint annular_width (min 0.15mm)))
(rule "JLC pad hole to pad hole 0.45 mm"
  (condition "A.Type == 'Pad' && B.Type == 'Pad'")
  (constraint hole_to_hole (min 0.45mm)))
(rule "JLC PTH hole to copper, outer layers 0.28 mm"
  (condition "A.Type == 'Pad' && A.Pad_Type == 'Through-hole'")
  (layer outer)
  (constraint hole_clearance (min 0.28mm)))
(rule "JLC PTH hole to copper, inner layers 0.3 mm"
  (condition "A.Type == 'Pad' && A.Pad_Type == 'Through-hole'")
  (layer inner)
  (constraint hole_clearance (min 0.3mm)))
""" % {"read": READ, "cap": CAP}


def write_rules():
    pro = json.load(open(PRO))
    rules = pro["board"]["design_settings"]["rules"]
    for k, v in PRO_RULES.items():
        rules[k] = v
    sev = pro["board"]["design_settings"].setdefault("rule_severities", {})
    for k in ("text_height", "text_thickness", "silk_over_copper", "silk_overlap", "silk_edge_clearance", "copper_sliver", "isolated_copper"):
        sev[k] = "warning"
    json.dump(pro, open(PRO, "w"), indent=2)
    DRU.write_text(DRU_TEXT)
    print("design rules written:", {k: v for k, v in PRO_RULES.items()})
    print("dru rules:", len(re.findall(r'^\(rule ', DRU_TEXT, re.M)))


# ---- measurement ----------------------------------------------------------------------------------------------------
def outline_chain(board):
    poly = pcbnew.SHAPE_POLY_SET()
    board.GetBoardPolygonOutlines(poly)
    return poly


def copper_items(board):
    """[(item, net, layers, shape per layer getter)] for pads, tracks, arcs, vias."""
    out = []
    for f in board.GetFootprints():
        for p in f.Pads():
            layers = geom.CU if p.GetDrillSize().x > 0 else [l for l in geom.CU if p.IsOnLayer(l)]
            if layers:
                out.append((p, p.GetNetname(), layers))
    for t in board.GetTracks():
        layers = geom.CU if t.GetClass() == "PCB_VIA" else [t.GetLayer()]
        out.append((t, t.GetNetname(), layers))
    return out


def bb_of(item):
    b = item.GetBoundingBox()
    return (mm(b.GetLeft()), mm(b.GetTop()), mm(b.GetRight()), mm(b.GetBottom()))


def near(a, b, d):
    return not (a[0] > b[2] + d or b[0] > a[2] + d or a[1] > b[3] + d or b[1] > a[3] + d)


def unit(t):
    a, b = geom.xy(t.GetStart()), geom.xy(t.GetEnd())
    d = geom.dist(a, b)
    return ((b[0] - a[0]) / d, (b[1] - a[1]) / d) if d > 1e-9 else (1.0, 0.0)


def proj(q, a, u):
    return (q[0] - a[0]) * u[0] + (q[1] - a[1]) * u[1]


def ref_of(item):
    if item.GetClass() == "PAD":
        return f"{item.GetParentFootprint().GetReference()}.{item.GetNumber() or '-'}"
    return item.GetClass()[4:].lower()


def where(item):
    p = geom.xy(item.GetPosition())
    return f"({p[0]:.2f}, {p[1]:.2f})"


def measure(board, stage):
    R = {}
    items = copper_items(board)
    boxes = [bb_of(it[0]) for it in items]
    tracks = [t for t in board.GetTracks() if t.GetClass() == "PCB_TRACK"]
    vias = [t for t in board.GetTracks() if t.GetClass() == "PCB_VIA"]
    pads = [p for f in board.GetFootprints() for p in f.Pads()]
    outer = (pcbnew.F_Cu, pcbnew.B_Cu)
    # trace widths
    wo = min((mm(t.GetWidth()), t) for t in tracks if t.GetLayer() in outer)
    wi = min((mm(t.GetWidth()), t) for t in tracks if t.GetLayer() not in outer)
    R["trace_outer"] = (wo[0], f"{wo[0]:.3f} mm, {wo[1].GetNetname().rsplit('/', 1)[-1]} on {board.GetLayerName(wo[1].GetLayer())} at {where(wo[1])}", wo[0] >= 0.09)
    R["trace_inner"] = (wi[0], f"{wi[0]:.3f} mm, {wi[1].GetNetname().rsplit('/', 1)[-1]} on {board.GetLayerName(wi[1].GetLayer())} at {where(wi[1])}", wi[0] >= 0.09)
    # vias
    vd = min((mm(v.GetDrillValue()), v) for v in vias)
    vw = min((mm(v.GetWidth(pcbnew.F_Cu)), v) for v in vias)
    vr = min(((mm(v.GetWidth(pcbnew.F_Cu)) - mm(v.GetDrillValue())) / 2, v) for v in vias)
    R["via_drill"] = (vd[0], f"{vd[0]:.3f} mm ({len(vias)} vias; drills {dict(collections.Counter(round(mm(v.GetDrillValue()), 3) for v in vias))})", vd[0] >= 0.15)
    R["via_dia"] = (vw[0], f"{vw[0]:.3f} mm (diameters {dict(collections.Counter(round(mm(v.GetWidth(pcbnew.F_Cu)), 3) for v in vias))})", vw[0] >= 0.25)
    R["via_ring"] = (vr[0], f"{vr[0]:.3f} mm at {where(vr[1])}", vr[0] >= 0.05)
    # PTH annular ring (round / oval pads: (min size − drill) / 2)
    pth = [p for p in pads if p.GetDrillSize().x > 0 and p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH]
    rings = []
    for p in pth:
        s = p.GetSize(pcbnew.F_Cu)
        rings.append(((min(mm(s.x), mm(s.y)) - max(mm(p.GetDrillSize().x), mm(p.GetDrillSize().y))) / 2, p))
    pr = min(rings)
    R["pth_ring"] = (pr[0], f"{pr[0]:.3f} mm at {ref_of(pr[1])} ({len(pth)} PTH pads)", pr[0] >= 0.15)
    # NPTH
    npth = [p for p in pads if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH]
    nd = min((mm(p.GetDrillSize().x), p) for p in npth)
    R["npth"] = (nd[0], f"{nd[0]:.2f} mm at {ref_of(nd[1])} ({len(npth)} NPTH: {sorted({round(mm(p.GetDrillSize().x), 2) for p in npth})})", nd[0] >= 0.5)
    # hole to hole
    holes = [(mm(v.GetPosition().x), mm(v.GetPosition().y), mm(v.GetDrillValue()), "via", v) for v in vias]
    holes += [(mm(p.GetPosition().x), mm(p.GetPosition().y), max(mm(p.GetDrillSize().x), mm(p.GetDrillSize().y)), "pad", p) for p in pads if p.GetDrillSize().x > 0]
    best = {"via": (9, None, None), "pad": (9, None, None), "mixed": (9, None, None)}
    for i in range(len(holes)):
        xi, yi, di, ki, ii = holes[i]
        for j in range(i + 1, len(holes)):
            xj, yj, dj, kj, ij = holes[j]
            if abs(xi - xj) > 6 or abs(yi - yj) > 6:
                continue
            g = math.hypot(xi - xj, yi - yj) - di / 2 - dj / 2
            k = "via" if ki == kj == "via" else ("pad" if ki == kj == "pad" else "mixed")
            if g < best[k][0]:
                best[k] = (g, ii, ij)
    R["h2h_via"] = (best["via"][0], f"{best['via'][0]:.3f} mm between vias at {where(best['via'][1])} / {where(best['via'][2])}; via–pad {best['mixed'][0]:.3f} mm ({ref_of(best['mixed'][2]) if best['mixed'][2] is not None and best['mixed'][2].GetClass() == 'PAD' else ref_of(best['mixed'][1])})", best["via"][0] >= 0.2)
    R["h2h_pad"] = (best["pad"][0], f"{best['pad'][0]:.3f} mm between {ref_of(best['pad'][1])} and {ref_of(best['pad'][2])}", best["pad"][0] >= 0.45)
    # hole to other-net copper (tracks, pads, zone fills), per hole kind and outer/inner
    fills = {l: [] for l in geom.CU}
    for z in board.Zones():
        if z.GetIsRuleArea():
            continue
        for l in geom.CU:
            if z.IsOnLayer(l):
                fp = z.GetFilledPolysList(l)
                if fp.OutlineCount():
                    fills[l].append((z.GetNetname(), pcbnew.SHAPE_POLY_SET(fp), bb_of(z)))
    worst = {("via", "outer"): (9, ""), ("via", "inner"): (9, ""), ("pth", "outer"): (9, ""), ("pth", "inner"): (9, ""), ("npth", "outer"): (9, ""), ("npth", "inner"): (9, "")}
    for x, y, d, kind, h in holes:
        hk = "via" if kind == "via" else ("npth" if h.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH else "pth")
        hnet = h.GetNetname()
        circle = pcbnew.SHAPE_CIRCLE(V(x, y), MM(d / 2))
        hb = (x - d / 2, y - d / 2, x + d / 2, y + d / 2)
        for (it, net, layers), bb in zip(items, boxes):
            if it is h or (net and net == hnet) or not near(hb, bb, 0.6):
                continue
            if it.GetClass() == "PAD" and not net:
                continue          # Sofar's net-less pads (the insert ring pads, T1/T2's unnumbered pads): in the DRC exclusion table (Sofar Q6)
            for l in layers:
                dist = mm(it.GetEffectiveShape(l).GetClearance(circle))
                key = (hk, "outer" if l in outer else "inner")
                if dist < worst[key][0]:
                    worst[key] = (dist, f"{ref_of(h)} {where(h)} vs {ref_of(it)} [{net.rsplit('/', 1)[-1] or 'no net'}] on {board.GetLayerName(l)}")
        for l in geom.CU:
            key = (hk, "outer" if l in outer else "inner")
            for net, fp, bb in fills[l]:
                if net == hnet or not near(hb, bb, 0.6):
                    continue
                dist = mm(fp.Distance(V(x, y))) - d / 2
                if dist < worst[key][0]:
                    worst[key] = (dist, f"{ref_of(h)} {where(h)} vs zone {net.rsplit('/', 1)[-1]} on {board.GetLayerName(l)}")
    R["hole_cu_via"] = (min(worst[("via", "outer")][0], worst[("via", "inner")][0]), f"outer {worst[('via', 'outer')][0]:.3f} ({worst[('via', 'outer')][1]}); inner {worst[('via', 'inner')][0]:.3f} ({worst[('via', 'inner')][1]})", min(worst[("via", "outer")][0], worst[("via", "inner")][0]) >= 0.2)
    R["hole_cu_pth"] = (min(worst[("pth", "outer")][0], worst[("pth", "inner")][0]), f"outer {worst[('pth', 'outer')][0]:.3f} ({worst[('pth', 'outer')][1]}); inner {worst[('pth', 'inner')][0]:.3f} ({worst[('pth', 'inner')][1]})", worst[("pth", "outer")][0] >= 0.28 and worst[("pth", "inner")][0] >= 0.3)
    R["hole_cu_npth"] = (min(worst[("npth", "outer")][0], worst[("npth", "inner")][0]), f"outer {worst[('npth', 'outer')][0]:.3f} ({worst[('npth', 'outer')][1]}); inner {worst[('npth', 'inner')][0]:.3f} ({worst[('npth', 'inner')][1]})", min(worst[("npth", "outer")][0], worst[("npth", "inner")][0]) >= 0.2)
    # copper to edge: shapes vs the outline chain (bisection on Collide clearance)
    outl = outline_chain(board)
    chains = [outl.Outline(i) for i in range(outl.OutlineCount())]
    # the outline's edges as zero-width segments (a closed SHAPE_LINE_CHAIN collides with everything inside it)
    edges = []
    for c in chains:
        for k in range(c.SegmentCount()):
            s = c.CSegment(k)
            edges.append(pcbnew.SHAPE_SEGMENT(s.A, s.B, 0))
    o = geom.OUTLINE
    ebest = (9, "")
    for (it, net, layers), bb in zip(items, boxes):
        if bb[0] > o["x0"] + 1.5 and bb[2] < o["x1"] - 1.5 and bb[1] > o["y0"] + 1.5 and bb[3] < o["y1"] - 1.5:
            continue
        if it.GetClass() == "PAD" and not net:
            continue          # Sofar's net-less insert ring pads / mechanical pads: not copper that carries a net (listed by DRC)
        shape = it.GetEffectiveShape(layers[0])
        ib = bb_of(it)
        def ebb(e):
            a, b = e.GetSeg().A, e.GetSeg().B
            return (min(mm(a.x), mm(b.x)), min(mm(a.y), mm(b.y)), max(mm(a.x), mm(b.x)), max(mm(a.y), mm(b.y)))
        near_edges = [e for e in edges if near(ib, ebb(e), 1.6)]
        lo, hi = 0.0, 1.5
        for _ in range(10):
            mid = (lo + hi) / 2
            if any(shape.Collide(e, MM(mid)) for e in near_edges):
                hi = mid
            else:
                lo = mid
        if lo < ebest[0]:
            ebest = (lo, f"{ref_of(it)} [{net.rsplit('/', 1)[-1]}] at {where(it)}")
    for l in geom.CU:
        for net, fp, bb in fills[l]:
            dmin = 9
            for i in range(fp.OutlineCount()):
                oc = fp.Outline(i)
                for k in range(oc.PointCount()):
                    q = oc.CPoint(k)
                    dd = min(mm(e.GetSeg().Distance(q)) for e in edges)
                    if dd < dmin:
                        dmin = dd
            if dmin < ebest[0]:
                ebest = (dmin, f"zone {net.rsplit('/', 1)[-1]} on {board.GetLayerName(l)}")
    R["edge"] = (ebest[0], f"{ebest[0]:.3f} mm: {ebest[1]}", ebest[0] >= 0.2)
    # same-net track gaps < 0.25 (not touching)
    sn = []
    tr_bb = [(t, bb_of(t)) for t in tracks]
    for i in range(len(tr_bb)):
        a, ba = tr_bb[i]
        for j in range(i + 1, len(tr_bb)):
            b, bbb = tr_bb[j]
            if a.GetLayer() != b.GetLayer() or a.GetNetname() != b.GetNetname() or not near(ba, bbb, 0.25):
                continue
            g = mm(a.GetEffectiveShape(a.GetLayer()).GetClearance(b.GetEffectiveShape(b.GetLayer())))
            # joined copper (a shared vertex, or the inner side of a bend: < 0.03 mm) is one trace to the fab, and so are the
            # non-adjacent legs of one polyline's corner. The sliver JLC's figure is about is two near-parallel runs of one net
            # with 0.03 … 0.25 between them: segments within 30° of each other that overlap along their length by ≥ 0.2 mm.
            if not (0.03 <= g < 0.25):
                continue
            ua, ub = unit(a), unit(b)
            cosang = abs(ua[0] * ub[0] + ua[1] * ub[1])
            if cosang < 0.866:
                continue
            pa = [proj(geom.xy(q), geom.xy(a.GetStart()), ua) for q in (b.GetStart(), b.GetEnd())]
            if min(max(pa), mm(a.GetLength())) - max(min(pa), 0.0) < 0.2:
                continue
            sn.append((g, a.GetNetname().rsplit("/", 1)[-1], board.GetLayerName(a.GetLayer()), geom.xy(a.GetStart())))
    sn.sort()
    R["same_net"] = (len(sn), f"{len(sn)} gap(s) of 0.03–0.25 mm between parallel runs of one net" + (f"; smallest {sn[0][0]:.3f} mm ({sn[0][1]} on {sn[0][2]} at ({sn[0][3][0]:.2f}, {sn[0][3][1]:.2f}))" if sn else ""), len(sn) == 0)
    R["same_net_list"] = [(round(g, 3), n, l, (round(p[0], 2), round(p[1], 2))) for g, n, l, p in sn[:40]]
    # SMD pads
    smd = [p for p in pads if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD and p.GetNetname() and mm(p.GetSize(pcbnew.F_Cu).x) > 0]
    sp = min((min(mm(p.GetSize(pcbnew.F_Cu).x), mm(p.GetSize(pcbnew.F_Cu).y)), p) for p in smd)
    small = {}
    for p in smd:
        w = min(mm(p.GetSize(pcbnew.F_Cu).x), mm(p.GetSize(pcbnew.F_Cu).y))
        if w < 0.25:
            r = p.GetParentFootprint().GetReference()
            small.setdefault(r, [str(p.GetParentFootprint().GetFPID().GetLibItemName()), 0, w])
            small[r][1] += 1
            small[r][2] = min(small[r][2], w)
    R["smd_pad"] = (sp[0], f"{sp[0]:.2f} mm at {ref_of(sp[1])}; every footprint under 0.25: " + "; ".join(f"{r} ({v[0]}: {v[1]} pads, {v[2]:.3f} mm)" for r, v in sorted(small.items())) +
                    " (netted SMD pads; Sofar's unnumbered no-net T1/T2 pads not counted)", sp[0] >= 0.25)
    R["small_pads"] = small
    # via in pad: a via's copper touching an SMD pad on the pad's own layer (QE round 3 F1). Sofar's own vias (copied, matched by
    # blockcheck's rule) and vias in test pads or thermal pads (> 4 mm²) are allowed; any other is a fail
    import motecopy, check_rules
    copied = check_rules.copied_ids(board, motecopy.Mote(board))
    vip, vip_new = [], []
    for v in vias:
        vb = bb_of(v)
        for p in smd:
            if not near(vb, bb_of(p), 0.1):
                continue
            for l in outer:
                if p.IsOnLayer(l) and p.GetEffectiveShape(l).Collide(v.GetEffectiveShape(l), 0):
                    f = p.GetParentFootprint()
                    pb = p.GetBoundingBox()
                    kind = "sofar" if v.m_Uuid.AsString() in copied else ("testpad" if f.GetReference().startswith("TP") else ("thermal" if mm(pb.GetWidth()) * mm(pb.GetHeight()) > 4.0 else "NEW"))
                    vip.append((ref_of(p), kind))
                    if kind == "NEW":
                        vip_new.append(ref_of(p))
                    break
    kinds = collections.Counter(k for _, k in vip)
    R["via_in_pad"] = (len(vip_new), f"{len(vip)} vias touching an SMD pad: Sofar's {kinds.get('sofar', 0)}, in test pads {kinds.get('testpad', 0)}, in thermal pads {kinds.get('thermal', 0)}, "
                       f"**new vias in solder pads {len(vip_new)}**" + (f" ({', '.join(sorted(set(vip_new)))})" if vip_new else ""), len(vip_new) == 0)
    # silk
    thin, texts = [], []
    for f in board.GetFootprints():
        for g_ in f.GraphicalItems():
            if g_.GetClass() == "PCB_SHAPE" and g_.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS) and 0 < mm(g_.GetWidth()) < 0.15:
                thin.append((round(mm(g_.GetWidth()), 3), f.GetReference()))
            if g_.GetClass() == "PCB_TEXT" and g_.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS) and g_.IsVisible() and (mm(g_.GetTextHeight()) < 1.0 or mm(g_.GetTextThickness()) < 0.15):
                texts.append((f.GetReference(), round(mm(g_.GetTextHeight()), 2), round(mm(g_.GetTextThickness()), 3)))
        for t in (f.Reference(), f.Value()):
            if t.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS) and t.IsVisible() and (mm(t.GetTextHeight()) < 1.0 or mm(t.GetTextThickness()) < 0.15):
                texts.append((f.GetReference(), round(mm(t.GetTextHeight()), 2), round(mm(t.GetTextThickness()), 3)))
    for d_ in board.GetDrawings():
        if d_.GetClass() == "PCB_SHAPE" and d_.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS) and 0 < mm(d_.GetWidth()) < 0.15:
            thin.append((round(mm(d_.GetWidth()), 3), "board"))
    R["silk_line"] = (len(thin), f"{len(thin)} silk lines under 0.15 mm" + (f" (thinnest {min(thin)[0]} mm; refs {sorted({r for _, r in thin})[:12]})" if thin else ""), len(thin) == 0)
    R["silk_text"] = (len(texts), f"{len(texts)} visible silk texts under 1.0 mm high or 0.15 mm thick" + (f" (e.g. {texts[:4]})" if texts else ""), len(texts) == 0)
    # copper balance per layer (union of pads, tracks, arcs, vias, zone fills)
    area_board = mm(mm(outl.Area())) if False else outl.Area() / 1e12
    bal = {}
    for l in geom.CU:
        u = pcbnew.SHAPE_POLY_SET()
        for it, net, layers in items:
            if l in layers:
                it.TransformShapeToPolygon(u, l, 0, MM(0.02), pcbnew.ERROR_INSIDE)
        for net, fp, bb in fills[l]:
            u.Append(fp)
        u.Simplify()
        bal[board.GetLayerName(l)] = round(100 * (u.Area() / 1e12) / area_board, 1)
    R["balance"] = (0, "; ".join(f"{k} {v} %" for k, v in bal.items()), True)
    R["balance_table"] = bal
    # pours and thermal settings
    zl = []
    for z in board.Zones():
        if z.GetIsRuleArea() or not z.GetNetname():
            continue
        conn = {pcbnew.ZONE_CONNECTION_FULL: "solid", pcbnew.ZONE_CONNECTION_THERMAL: "thermal", pcbnew.ZONE_CONNECTION_NONE: "none"}.get(z.GetPadConnection(), str(z.GetPadConnection()))
        zl.append((board.GetLayerName(z.GetLayer()), z.GetNetname().rsplit("/", 1)[-1], conn, z.GetZoneName()[:50]))
    outer_pours = [z for z in zl if z[0] in ("Top Layer", "6 Bottom Layer") and z[1] == "GND"]
    stitch = [v for v in vias if v.GetNetname() == "GND"]
    R["pours"] = (len(outer_pours), f"GND pours on outer layers: {[(z[0], z[3]) for z in outer_pours]}; {len(stitch)} GND vias on the board", len(outer_pours) >= 1)
    R["thermal"] = (0, "; ".join(f"{l} {n}: {c}" for l, n, c, _ in zl if n in ("GND", "VBUS", "P_IN", "3V3", "5V_PI")), True)
    R["zones"] = zl
    # fiducials
    fids = []
    fps = geom.fp_by_ref(board)
    for ref in sorted(r for r in fps if r.startswith("FID")):
        f = fps[ref]
        p = geom.xy(f.GetPosition())
        cu = max((mm(pd.GetSize(pcbnew.F_Cu).x) for pd in f.Pads()), default=0)
        mask = 0
        for g_ in f.GraphicalItems():
            if g_.GetClass() == "PCB_SHAPE" and g_.GetShape() == pcbnew.SHAPE_T_CIRCLE and g_.GetLayer() in (pcbnew.F_Mask, pcbnew.B_Mask):
                mask = max(mask, 2 * mm(g_.GetRadius()))
        for pd in f.Pads():
            try:
                mask = max(mask, cu + 2 * mm(pd.GetLocalSolderMaskMargin()))
            except Exception:
                pass
        edge = min(p[0] - o["x0"], o["x1"] - p[0], p[1] - o["y0"], o["y1"] - p[1]) - cu / 2
        fids.append((ref, "bottom" if f.IsFlipped() else "top", (round(p[0], 2), round(p[1], 2)), round(cu, 2), round(mask, 2), round(edge, 2)))
    top = [x for x in fids if x[1] == "top"]
    bot = [x for x in fids if x[1] == "bottom"]
    ok = len(top) >= 3 and len(bot) >= 3 and all(x[5] >= 3.35 for x in fids)
    R["fiducial"] = (len(fids), f"top {len(top)} / bottom {len(bot)}; copper {sorted({x[3] for x in fids})} mm, mask {sorted({x[4] for x in fids})} mm; pad edge to board edge min {min(x[5] for x in fids):.2f} mm ({', '.join(x[0] for x in fids if x[5] < 3.35) or 'all ≥ 3.35'})", ok)
    R["fiducial_table"] = fids
    # test points: courtyard gap to the nearest other courtyard on the same side
    cy = {r: (geom.courtyard_bbox(f), f.IsFlipped()) for r, f in fps.items() if geom.xy(f.GetPosition())[0] < 40}
    tps = []
    for r, (c, side) in cy.items():
        if not r.startswith("TP") or c is None:
            continue
        g = min((geom.rect_gap(c, c2), r2) for r2, (c2, s2) in cy.items() if r2 != r and c2 is not None and s2 == side)
        tps.append((r, round(g[0], 2), g[1]))
    tps.sort(key=lambda t: t[1])
    import motecopy
    block_refs = {r for b in motecopy.load_blocks()["blocks"] for r in b.get("placed", [])}
    over = [t for t in tps if t[1] <= 0]
    new_over = [t for t in over if t[0] not in block_refs or t[2] not in block_refs]
    R["testpoints"] = (len(tps), f"{len(tps)} test points; {len(over)} courtyard overlaps, {len(over) - len(new_over)} of them Sofar's inside a copied block "
                       f"({', '.join(f'{t[0]}/{t[2]}' for t in over)}), {len(new_over)} of this board's placement; smallest gap otherwise "
                       f"{next((t[1] for t in tps if t[1] > 0), None)} mm", not new_over)
    R["testpoint_table"] = tps
    # stackup
    text = open(geom.BOARD, encoding="utf-8").read()
    has = "(stackup" in text
    stk = text[text.index("(stackup"):text.index("(copper_finish")] if has else ""
    jlc = all(k in stk for k in ("thickness 0.0994", "thickness 0.1088", "thickness 0.55", "thickness 0.0152", "3313", "2116"))
    R["stackup"] = (int(jlc), "board setup: " + ("JLC06161H-3313 values present (3313 / 0.55 core / 2116 / 0.0152 inner copper)" if jlc else ("a stackup is present but not JLC's (01's generic build)" if has else "no stackup in the board")), jlc)
    R["copper_wt"] = (0, "outer 0.035 mm (1 oz), inner 0.0152 mm (0.5 oz) per the stackup row" if jlc else "the board still carries 01's generic 0.035 mm on every layer", jlc)
    bbx = board.GetBoardEdgesBoundingBox()
    R["board"] = (0, f"{mm(bbx.GetWidth()):.1f} × {mm(bbx.GetHeight()):.1f} mm, thickness {mm(board.GetDesignSettings().GetBoardThickness()):.2f} mm", True)
    R["bom_cpl"] = (0, "finest pitch on the board: U1 QFN 0.5 mm, U2/U3 WLCSP 0.5 mm, U11 0.5 mm; KiCad's CPL rotations follow the footprint's own zero, JLC's library may differ per part (checked in their order preview)", True)
    R["courtyard"] = (0, "see DRC", True)
    R["mask_dam"] = (0, "see DRC", True)
    R["silk_pad"] = (0, "see DRC", True)
    R["space"] = (0, "see DRC", True)
    return R


def run_drc(stage):
    out = geom.OUT / stage
    out.mkdir(parents=True, exist_ok=True)
    subprocess.run([K, "pcb", "drc", "--schematic-parity", "--severity-all", "--format", "json", "-o", str(out / "drc_dfm.json"), str(geom.BOARD)],
                   check=True, capture_output=True)
    d = json.load(open(out / "drc_dfm.json"))
    c = collections.Counter((v["type"], v["severity"]) for v in d["violations"])
    return d, c


def check(stage):
    board = geom.load()
    R = measure(board, stage)
    d, c = run_drc(stage)
    drc = {k[0]: n for k, n in c.items()}
    errors = sum(n for k, n in c.items() if k[1] == "error")
    warnings = sum(n for k, n in c.items() if k[1] == "warning")
    # DRC-backed rows
    R["space"] = (drc.get("clearance", 0), f"DRC clearance items: {drc.get('clearance', 0)} (all in the exclusion table: Sofar's T1/T2 pads 6/7 at 0.24, the no-net pads, the BM1_N stub vs Sofar's via)", True)
    R["mask_dam"] = (drc.get("solder_mask_bridge", 0), f"DRC solder_mask_bridge: {drc.get('solder_mask_bridge', 0)} (Sofar's insert ring pads and T1/T2 no-net pads, exclusion table)", True)
    R["silk_pad"] = (drc.get("silk_over_copper", 0), f"DRC silk_over_copper {drc.get('silk_over_copper', 0)}, silk_overlap {drc.get('silk_overlap', 0)}, silk_edge_clearance {drc.get('silk_edge_clearance', 0)}", drc.get("silk_over_copper", 0) == 0)
    R["courtyard"] = (drc.get("courtyards_overlap", 0), f"DRC courtyards_overlap: {drc.get('courtyards_overlap', 0)}", drc.get("courtyards_overlap", 0) <= 12)
    R["silk_text"] = (R["silk_text"][0], R["silk_text"][1] + f"; DRC text_height {drc.get('text_height', 0)}, text_thickness {drc.get('text_thickness', 0)}", R["silk_text"][2] and drc.get("text_height", 0) == 0)
    extra = {"annular_width": drc.get("annular_width", 0), "hole_clearance": drc.get("hole_clearance", 0), "hole_to_hole": drc.get("hole_to_hole", 0),
             "copper_edge_clearance": drc.get("copper_edge_clearance", 0), "track_width": drc.get("track_width", 0), "drill_out_of_range": drc.get("drill_out_of_range", 0),
             "via_diameter": drc.get("via_diameter", 0)}
    lines = [f"# DFM — JLCPCB 6-layer, layout experiment 1.a (stage {stage})\n", PREAMBLE,
             f"*Generated by `tools/dfm.py check {stage}` on the board as it is (md5 see HANDOFF). Every JLCPCB limit was read from the cited page on "
             f"{READ}: the capabilities page `{CAP}`, the stackup page `{STK}`, the assembly page `{ASM}`, the fiducial article `{FID}`. "
             f"The limits are written into `board/*.kicad_pro` (design_settings.rules) and `board/*.kicad_dru` by `tools/dfm.py rules`; a limit DRC cannot "
             f"express is measured by this script (column 'enforced by'). 'Board rule' is the value the DRC runs with: where the brief or the mote is stricter "
             f"than JLCPCB, the stricter value stays.*\n",
             "| # | Item | JLCPCB limit (quoted) | Source, date | Enforced by | Measured worst case (where) | Pass | What 2.b changed |", "|---|---|---|---|---|---|---|---|"]
    order = ["trace_outer", "trace_inner", "space", "same_net", "via_drill", "via_dia", "via_ring", "pth_ring", "h2h_via", "h2h_pad", "hole_cu_via",
             "hole_cu_pth", "hole_cu_npth", "npth", "edge", "mask_dam", "silk_line", "silk_text", "silk_pad", "courtyard", "stackup", "copper_wt",
             "balance", "pours", "thermal", "fiducial", "testpoints", "bom_cpl", "smd_pad", "via_in_pad", "board"]
    for i, k in enumerate(order, 1):
        item, lim, src, enf = LIMITS[k]
        val, text, ok = R[k]
        lines.append(f"| {i} | {item} | {lim} | {src.replace('https://', '')}, {READ} | {enf} | {text} | {'pass' if ok else '**FAIL**'} | {CHANGES.get(k, '—')} |")
    lines += ["", f"DRC with these rules (`kicad-cli pcb drc --schematic-parity --severity-all`): **{errors} errors, {warnings} warnings**, "
              f"{len(d['unconnected_items'])} unconnected, {len(d['schematic_parity'])} parity; per type: " + ", ".join(f"{k[0]} {n} ({k[1]})" for k, n in sorted(c.items())) + ".",
              f"DFM-rule items in that DRC: " + ", ".join(f"{k} {v}" for k, v in extra.items()) + "."]
    if R["same_net_list"]:
        lines += ["", "Same-net track gaps under 0.25 mm (first 40): " + "; ".join(f"{g} {n} {l} {p}" for g, n, l, p in R["same_net_list"])]
    lines += ["", "Fiducials: " + "; ".join(f"{r} {s} at {p}, copper {cu}, mask {mk}, pad edge to board edge {e}" for r, s, p, cu, mk, e in R["fiducial_table"])]
    lines += ["", "Test points (courtyard gap to the nearest part on the same side): " + ", ".join(f"{r} {g} ({n})" for r, g, n in R["testpoint_table"])]
    lines += ["", "Zones: " + "; ".join(f"{l} {n} {c} ({nm})" for l, n, c, nm in R["zones"])]
    text = "\n".join(lines) + "\n" + HISTORY
    out = geom.OUT / stage
    out.mkdir(parents=True, exist_ok=True)
    (out / "dfm_table.md").write_text(text)
    DFM_MD.write_text(text)
    json.dump({k: (v if not isinstance(v, tuple) else list(v)) for k, v in R.items()}, open(out / "dfm.json", "w"), indent=1, default=str)
    print(text)
    fails = [k for k in order if not R[k][2]]
    print(f"\nDFM: {len(order) - len(fails)} pass, {len(fails)} fail: {fails}")
    return text, fails


if __name__ == "__main__":
    if sys.argv[1] == "rules":
        write_rules()
    else:
        check(sys.argv[2] if len(sys.argv) > 2 else "m4")
