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


# ---- BRIEF §2 outline ------------------------------------------------------------------------------------------
OUTLINE = {"x0": -7.5, "x1": 38.5, "y0": 0.0, "y1": 65.0, "r": 3.0}
EDGE_CLEARANCE = 0.5

# ---- BRIEF §3 fixed placements (frame mm) -----------------------------------------------------------------------
J1_PIN1 = (25.23, 8.37)              # seen from the top; pin 2 at (27.77, 8.37); pins advance 2.54 mm south
PI_HOLES = {"H1": (3.5, 3.5), "H2": (26.5, 3.5), "H3": (3.5, 61.5), "H4": (26.5, 61.5)}        # M2.5, r 3.0 clear
HOUSING_HOLES = {"MTG1": (-3.5, 3.5), "MTG2": (34.5, 3.5), "MTG3": (-3.5, 61.5), "MTG4": (34.5, 61.5)}  # M3, r 3.5
INSERTS = {"MP3": (-1.81, 12.0), "MP4": (-1.81, 21.4), "MP1": (-1.81, 43.6), "MP2": (-1.81, 53.0)}
INSERT_NET = {"MP1": "BM1_P", "MP2": "BM1_N", "MP3": "BM2_P", "MP4": "BM2_N"}
INSERT_KEEPOUT_R = 4.8               # no part, no other-net copper, planes pulled back (BRIEF §4, §6)
ENVELOPES = {"L2": (4.99, 9.0, 20.49, 24.5), "L1": (4.99, 36.5, 20.49, 52.0)}   # 50 W inductor envelopes (x0,y0,x1,y1)
ENVELOPE_CLEAR = 2.0
# J5 JST GH SM02B-GHS-TB (Nick, 2026-10-07: keep the schematic's JST part, not the brief's Molex). Stock footprint:
# origin between the two signal pads (local y -1.85), mechanical tab pads at local y 1.35 (copper to +2.7), housing
# front (mating face) at local y +2.45, courtyard x ±3.525, y -3.245 … +3.245. Rotation 0 faces south; the origin
# at y 61.8 keeps the tab copper 0.5 mm from the south edge, so the housing front is 0.75 mm inside the edge.
J5_POS = (15.0, 61.8)
J5_ROT = 0.0
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
