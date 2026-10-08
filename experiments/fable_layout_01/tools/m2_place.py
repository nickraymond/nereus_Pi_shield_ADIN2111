#!/usr/bin/env python3
"""M2: place every part. Copied blocks are rigid (translate + rotate by multiples of 90°, same side as the mote,
proven by pads); everything else is placed fresh. Records every block transform in blocks.json (M3 copies the copper
with the same definitions). Applied by tools/build_all.sh after m1_fixed.py.

Why the blocks are what they are (details in LOG.md M2): the brief's PORT, SPINE and BUCK blocks are larger than the
room the fixed items leave (the 8.9 mm strip east of J1, the 8 mm band between the inductor envelopes, the west
pocket), so each is split into the largest rigid pieces that fit; the copper between the pieces is new routing.
"""
import json

import geom
import motecopy
from geom import V

# ---- rigid blocks: refs on the mote, anchor = the first ref's mote position; dst = where that anchor lands --------
# region: rects in mote mm (optionally with a "layers" list) selecting the copper that belongs to the block (M3).
BLOCKS = [
    {"name": "ADIN", "refs": ["U1", "U2", "U3", "Y1", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10", "C11",
                              "C12", "C13", "C14", "R1", "R2", "R3", "R4", "R5", "R6", "TP1", "TP2"],
     "dst": [-1.7, 32.8], "rot": 90,
     "region": [[148.0, 108.0, 159.5, 114.1], [149.1, 114.1, 159.5, 120.6]],
     "zone_region": [[148.0, 107.9, 159.5, 120.6]],
     "why": "whole ADIN block (U1 top; switches, decoupling, crystal below) in the west pocket, rotated 90 so port 1's "
            "data pins face north toward T1 in the band and port 2's face south; U1 clear of x 2.99 and both insert keep-outs"},
    {"name": "P1L", "refs": ["L1", "D4", "R12", "R13", "TP3", "TP5", "C17", "D2"],
     "dst": [12.74, 44.25], "rot": 90,
     "region": [[158.9, 102.0, 172.2, 115.0]],
     "why": "L1 centred in its envelope with the bottom-side parts Sofar put under it; rotated 90 so the bus pads face "
            "west toward MP1/MP2 (BM1_P north-west, BM1_N south-west) and VBUS/GND face east"},
    {"name": "P1T", "refs": ["T1", "C16", "C18", "C19", "R14"],
     "dst": [8.7, 30.5], "rot": 0,
     "region": [[158.8, 115.2, 165.4, 119.8]],
     "why": "T1 cluster split from L1 (on the mote T1 sits 9.6 mm from L1's centre, inside the 50 W envelope + 2 mm); "
            "in the band between the envelopes, data pins facing U1 (west)"},
    {"name": "P2L", "refs": ["L2", "D5", "R17", "R19", "TP7", "TP13", "C26"],
     "dst": [12.74, 16.75], "rot": 90,
     "region": [[125.0, 101.5, 138.3, 113.0], [125.0, 113.0, 131.5, 115.0]],
     "why": "as P1L: bus pads west (BM2_P north-west toward MP3, BM2_N south-west toward MP4)"},
    {"name": "P2T", "refs": ["T2", "C24", "C25", "C27", "R18"],
     "dst": [16.7, 30.5], "rot": 180,
     "region": [[133.0, 113.1, 139.2, 121.0]],
     "why": "T2 cluster in the band east of T1, rotated 180 so its data pins face west (toward U1's port-2 pins)"},
    {"name": "B33", "refs": ["U5", "C30", "L3", "C28", "C29", "R20", "R21", "R22", "R23"],
     "dst": [31.551, 17.704], "rot": 0,
     "region": [{"rect": [138.2, 104.6, 146.4, 112.9], "layers": ["F.Cu", "In1.Cu", "In3.Cu"]},
                {"rect": [138.2, 112.9, 144.3, 119.0], "layers": ["F.Cu", "B.Cu", "In1.Cu", "In3.Cu"]}],
     "clip_zone_nets": ["3V3"],
     "why": "U5 cell (switch loop U5–C30–L3, bottom-side dividers and caps, top pours, In3 GND patch) in the east strip; "
            "the output cap C31 is the only part split off (the cell is 8.55 mm wide with it 9.65: the strip is 8.9)"},
    {"name": "B5V", "refs": ["U5", "C30", "L3", "C28", "C29", "R20", "R21", "R22", "R23"],
     "ref_map": {"U5": "U10", "C30": "C55", "L3": "L6", "C28": "C53", "C29": "C54", "R20": "R39", "R21": "R37", "R22": "R40", "R23": "R38"},
     "dst": [31.551, 31.4], "rot": 0,
     "region": [{"rect": [138.2, 104.6, 146.4, 112.9], "layers": ["F.Cu", "In1.Cu", "In3.Cu"]},
                {"rect": [138.2, 112.9, 144.3, 119.0], "layers": ["F.Cu", "B.Cu", "In1.Cu", "In3.Cu"]}],
     "clip_zone_nets": ["3V3"],
     "why": "5 V buck = U5's cell copied again with its parts mapped by function (D13); C56/C57/C58/TP38 placed beside it"},
    {"name": "SENSE", "refs": ["C23", "R8", "U4", "R7", "C15", "TP22"],
     "dst": [33.88, 39.3], "rot": 90,
     "region": [[144.4, 112.4, 148.0, 120.2], [148.0, 114.2, 149.0, 120.2]],
     "why": "R8 shunt + INA232 with Sofar's sense routing, and C23 above them; rotated 90 to fit the strip"},
    {"name": "DAMP1", "refs": ["C21", "R16", "C20", "TP23"],
     "dst": [8.9, 57.5], "rot": 90,
     "region": [[149.9, 117.5, 156.5, 121.2]],
     "why": "VBUS 10 uF + damping resistor (R16 pairs with C23 in SENSE) in the south-west pocket beside J5"},
    {"name": "DAMP2", "refs": ["C22"],
     "dst": [33.9, 47.7], "rot": 90,
     "region": [[146.8, 99.8, 155.8, 107.0]],
     "why": "second damping electrolytic in the strip; its resistor R15 could not ride along (it would land under J1 or off the edge)"},
    {"name": "B18", "refs": ["U6", "L4", "C32", "C33", "TP21"],
     "dst": [20.7, 47.2], "rot": 90,
     "region": [{"rect": [141.8, 108.4, 148.3, 113.2], "layers": ["B.Cu"]}],
     "exclude_vias_on": ["3V3", "GND"],
     "why": "1.8 V buck (all bottom) east of L1 beside J1, rotated 90 to clear D2/C17 under L1"},
]

# ---- fresh placements: ref -> (x, y, rot, side) -------------------------------------------------------------------
FRESH = {
    # strip, top: output cap of the 3.3 V cell, the payload switch cell
    "C31": (36.6, 17.7, 0, "F"),
    "U11": (31.5, 54.3, 0, "F"), "C49": (36.2, 53.5, 0, "F"), "R35": (36.2, 55.6, 0, "F"),
    # strip, bottom
    "JP1": (32.0, 9.0, 0, "B"), "R26": (37.0, 20.2, 0, "B"), "R27": (37.0, 22.0, 0, "B"),
    "TP20": (37.2, 16.8, 0, "B"), "TP24": (34.9, 22.4, 0, "B"),
    "C56": (31.6, 23.0, 0, "B"), "C57": (31.6, 25.2, 0, "B"), "C58": (36.5, 30.8, 0, "B"), "TP38": (36.5, 32.9, 0, "B"),
    "R11": (21.0, 58.0, 90, "B"), "R34": (30.6, 45.3, 0, "B"), "R41": (30.7, 43.3, 0, "B"), "R42": (36.9, 52.5, 0, "B"),
    "C50": (36.9, 50.0, 90, "B"), "R15": (30.5, 49.2, 90, "B"), "TP35": (36.9, 54.6, 0, "B"), "TP36": (19.5, 62.3, 0, "B"),
    "D3": (31.2, 54.8, 90, "B"), "TP19": (37.2, 57.0, 0, "B"),
    # band, top: status LEDs north -> south D10 (port 2), D8 (power), D9 (port 1); bottom: their resistors and JP2
    "D10": (21.5, 28.3, 0, "F"), "D8": (21.5, 30.0, 0, "F"), "D9": (21.5, 31.7, 0, "F"),
    "JP2": (21.0, 28.5, 0, "B"), "R46": (21.5, 31.3, 0, "B"), "R44": (21.5, 32.7, 0, "B"), "R45": (21.5, 34.1, 0, "B"),
    "R43": (7.5, 36.3, 0, "B"), "TP8": (9.8, 36.3, 0, "B"),
    # south pockets, top
    "D1": (20.9, 59.0, 90, "F"),
    # fiducials
    "FID4": (8.0, 2.5, 0, "F"), "FID3": (21.5, 2.5, 0, "F"), "FID5": (15.0, 56.0, 0, "F"),
    "FID2": (8.0, 2.5, 0, "B"), "FID1": (21.5, 2.5, 0, "B"), "FID6": (15.0, 56.0, 0, "B"),
}


def place_fresh(board):
    fps = geom.fp_by_ref(board)
    for ref, (x, y, rot, side) in FRESH.items():
        fp = fps[ref]
        if fp.IsFlipped() != (side == "B"):
            fp.Flip(fp.GetPosition(), __import__("pcbnew").FLIP_DIRECTION_LEFT_RIGHT)
        fp.SetPosition(V(x, y))
        fp.SetOrientationDegrees(rot)


def main():
    board = geom.load()
    mote = motecopy.Mote(board)
    out = []
    for blk in BLOCKS:
        anchor = blk["refs"][0]
        blk = dict(blk)
        blk["src"] = list(geom.xy(mote.mote_fp[anchor].GetPosition()))
        blk["anchor"] = anchor
        T = motecopy.transform_of(blk)
        blk["placed"] = mote.place_footprints(blk, T)
        out.append(blk)
    place_fresh(board)
    geom.save(board)
    prev = json.load(open(geom.EXP / "blocks.json"))
    json.dump({"frame": prev["frame"], "blocks": prev["blocks"] + out,
               "fresh": {r: {"x": v[0], "y": v[1], "rot": v[2], "side": v[3]} for r, v in FRESH.items()}},
              open(geom.EXP / "blocks.json", "w"), indent=1)
    placed = {r for b in out for r in b["placed"]} | set(FRESH)
    print(f"M2 placed: {len(out)} blocks ({sum(len(b['placed']) for b in out)} parts) + {len(FRESH)} fresh parts")
    parked = [f.GetReference() for f in board.GetFootprints() if geom.xy(f.GetPosition())[0] > 40]
    print("still parked:", parked)


if __name__ == "__main__":
    main()
