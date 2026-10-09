"""Shared constants and helpers for layout experiment 01 (KiCad 9 pcbnew).

Board frame (BRIEF §2) = KiCad board coordinates in mm: the Pi Zero 2 W's north-west corner is (0, 0), x east, y south.
"""
import math
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
BOARD = EXP / "board" / "nereus_Pi_shield_ADIN2111.kicad_pcb"
MOTE = EXP.parents[1] / "KiCAD_reference_designs" / "20250409_BM_Mote_000639-AB" / "BM_Mote_000639-AB.kicad_pcb"
OUT = EXP / "out"

MM = pcbnew.FromMM
mm = pcbnew.ToMM


def V(x, y):
    """Board frame mm -> VECTOR2I."""
    return pcbnew.VECTOR2I(MM(x), MM(y))


def xy(v):
    return (mm(v.x), mm(v.y))


def deg(a):
    return pcbnew.EDA_ANGLE(a, pcbnew.DEGREES_T)


# ---- BRIEF §2 outline, grown in session 2.b (Nick, 2026-10-08: 3 mm wider, 3 mm taller; LESSONS §3) -----------------
# The Pi's frame is unchanged (J1, H1–H4, the camera ribbon, the north band between the Pi's standoffs). The extra
# width goes WEST (x0 −7.5 → −10.5): the inserts and the west housing holes move with the edge, and the band between the
# inductor envelopes gains 3 mm between the port-2 insert keep-out and J1's socket for the T2 cluster – U1 – T1 cluster
# chain (OPTIONS.md addendum: the first trial, with the width on the east, had T2's bottom cap C25 inside MP4's r 4.8
# keep-out and T1 against J1's socket courtyard at the same time; the strip east of J1 gained nothing from the width).
# The extra height goes SOUTH and is spent on the band: L1's envelope, the port-1 inserts, J5 and the south band move
# 3 mm south (the inserts 2.5: MP2's courtyard would otherwise come within 2.91 mm of the Pi's H3 standoff keep-out),
# so the band grows from 8.0 to 11.0 mm (y 26.5 … 37.5) and J1's SPI pins (y 31.2 … 36.3) sit at its latitude.
OUTLINE = {"x0": -10.5, "x1": 38.5, "y0": 0.0, "y1": 68.0, "r": 3.0}
GROWTH = {"west": 3.0, "south": 3.0}
EDGE_CLEARANCE = 0.5

# ---- BRIEF §3 fixed placements (frame mm) -----------------------------------------------------------------------
J1_PIN1 = (25.23, 8.37)              # seen from the top; pin 2 at (27.77, 8.37); pins advance 2.54 mm south
PI_HOLES = {"H1": (3.5, 3.5), "H2": (26.5, 3.5), "H3": (3.5, 61.5), "H4": (26.5, 61.5)}        # M2.5, r 3.0 clear
HOUSING_HOLES = {"MTG1": (-6.5, 3.5), "MTG2": (34.5, 3.5), "MTG3": (-6.5, 64.5), "MTG4": (34.5, 64.5)}  # M3, r 3.5; 4 / 3.5 mm in from the corners
# Inserts 1.5 mm nearer the west wall (Nick, 2026-10-08: 1–2 mm): the ring copper (bottom ring pad r 3.69, the arc's
# outer edge r 3.63) now keeps exactly the brief's 0.5 mm from the edge (JLCPCB's own figure is 0.2 mm, DFM.md row 15:
# 2 mm would need 0 mm at the rings, as the mote has it). The mote's corner inserts sit 3.5 mm from its edge.
INSERT_X = OUTLINE["x0"] + EDGE_CLEARANCE + 3.69          # −6.31 (was −1.81: 1.5 mm nearer the wall on the 3 mm wider board)
INSERTS = {"MP3": (INSERT_X, 12.0), "MP4": (INSERT_X, 21.4), "MP1": (INSERT_X, 46.1), "MP2": (INSERT_X, 55.5)}   # port 1 2.5 mm south
INSERT_NET = {"MP1": "BM1_P", "MP2": "BM1_N", "MP3": "BM2_P", "MP4": "BM2_N"}
INSERT_KEEPOUT_R = 4.8               # no part, no other-net copper, planes pulled back (BRIEF §4, §6)
import os
# J5WEST=1 (Nick's suggestion, 2026-10-08, trialled in session 2.b): the payload connector on the west wall in the pocket
# between the insert pairs, mating face west (C21 / D1 stay in the south band), and L1's envelope 1.5 mm further south
# (its 2 mm clearance then touches the Pi's H3 / H4 standoff keep-outs at y 58.5), so the band grows to 12.5 mm.
J5_WEST = os.environ.get("J5WEST") == "1"
L1_EXTRA = 1.5 if J5_WEST else 0.0
ENVELOPES = {"L2": (4.99, 9.0, 20.49, 24.5), "L1": (4.99, 39.5 + L1_EXTRA, 20.49, 55.0 + L1_EXTRA)}   # 50 W inductor envelopes (x0,y0,x1,y1); L1 3 mm south
ENVELOPE_CLEAR = 2.0
BAND = (ENVELOPES["L2"][3] + ENVELOPE_CLEAR, ENVELOPES["L1"][1] - ENVELOPE_CLEAR)   # y 26.5 … 37.5 between the envelopes' clearances
# J5 JST GH SM02B-GHS-TB (Nick, 2026-10-07: keep the schematic's JST part, not the brief's Molex). Stock footprint:
# origin between the two signal pads (local y -1.85), mechanical tab pads at local y 1.35 (copper to +2.7), housing
# front (mating face) at local y +2.45, courtyard x ±3.525, y -3.245 … +3.245. Rotation 0 faces south; the origin
# 3.2 mm above the south edge keeps the tab copper 0.5 mm from it, so the housing front is 0.75 mm inside the edge.
J5_POS = (OUTLINE["x0"] + 3.2, 33.75) if J5_WEST else (15.0, OUTLINE["y1"] - 3.2)
J5_ROT = -90.0 if J5_WEST else 0.0          # rotation 0 faces south; -90 (clockwise) faces west
CAMERA_RIBBON = (7.0, 61.6, 23.0, 65.0)   # under the Pi's camera connector (bottom side): nothing taller than 3 mm
BOTTOM_MAX_HEIGHT = 3.0

# ---- layers ------------------------------------------------------------------------------------------------------
CU = [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.In3_Cu, pcbnew.In4_Cu, pcbnew.B_Cu]
LAYER_NAMES = {pcbnew.F_Cu: "Top Layer", pcbnew.In1_Cu: "Internal 1", pcbnew.In2_Cu: "GND Plane",
               pcbnew.In3_Cu: "Internal 2", pcbnew.In4_Cu: "PWR Plane", pcbnew.B_Cu: "6 Bottom Layer"}


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def load(path=BOARD):
    return pcbnew.LoadBoard(str(path))


def save(board, path=BOARD):
    pcbnew.SaveBoard(str(path), board, True)    # never rewrite the .kicad_pro from here


def fp_by_ref(board):
    return {f.GetReference(): f for f in board.GetFootprints()}


def courtyard_bbox(fp):
    """Courtyard bounding box on the footprint's own side, as (x0, y0, x1, y1) mm; None if it has no courtyard."""
    layer = pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd
    fp.BuildCourtyardCaches()
    poly = fp.GetCourtyard(layer)
    if poly.OutlineCount() == 0:
        return None
    bb = poly.BBox()
    return (mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom()))


def rect_overlap(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def rect_gap(a, b):
    """Smallest axis-aligned gap between two rects (0 if they overlap)."""
    dx = max(b[0] - a[2], a[0] - b[2], 0)
    dy = max(b[1] - a[3], a[1] - b[3], 0)
    return math.hypot(dx, dy)
