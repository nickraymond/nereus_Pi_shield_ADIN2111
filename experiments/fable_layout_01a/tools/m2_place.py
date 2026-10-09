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
     "dst": [-1.7, 32.5], "rot": 90,
     "region": [[148.2, 107.9, 159.5, 114.1], [149.1, 114.1, 159.5, 119.7]],
     "zone_region": [[148.0, 107.9, 159.5, 120.6]],
     "exclude_nets": ["BM1_DATA_P", "BM1_DATA_N", "BM2_DATA_P", "BM2_DATA_N"],
          "why": "whole ADIN block (U1 top; switches, decoupling, crystal below) in the west pocket, rotated 90 so port 1's "
            "data pins face north toward T1 in the band and port 2's face south; U1 clear of x 2.99 and both insert keep-outs"},
    {"name": "P1L", "refs": ["L1", "D4", "R12", "R13", "TP3", "TP5", "C17", "D2"],
     "dst": [12.74, 44.25], "rot": 90,
     "region": [[158.9, 102.0, 172.2, 115.0]],
     "exclude_region": [[165.0, 101.9, 168.3, 105.0]],
     "why": "L1 centred in its envelope with the bottom-side parts Sofar put under it; rotated 90 so the bus pads face "
            "west toward MP1/MP2 (BM1_P north-west, BM1_N south-west) and VBUS/GND face east"},
    {"name": "P1T", "refs": ["T1", "C16", "C18", "C19", "R14"],
     "dst": [6.7, 28.4], "rot": 0,
     "region": [[158.8, 115.2, 165.4, 119.8]], "exclude_nets": ["BM1_DATA_P", "BM1_DATA_N"],
     "why": "T1 cluster split from L1 (on the mote T1 sits 9.6 mm from L1's centre, inside the 50 W envelope + 2 mm); "
            "in the band between the envelopes, data pins facing U1 (west). Session 2: tried at 7.0 (0.3 mm east) while the "
            "pair's straight approach was 1.4 mm long and ran into the ADIN block's crystal via at (2.9, 29.775); the "
            "approach is 0.9 mm now and clears it from 6.7, so the M1 position stands"},
    {"name": "P2L", "refs": ["L2", "D5", "R17", "R19", "TP7", "TP13"],
     "dst": [12.74, 16.75], "rot": 90,
     "region": [[125.0, 101.5, 138.3, 112.7]],
     "why": "as P1L: bus pads west (BM2_P north-west toward MP3, BM2_N south-west toward MP4)"},
    {"name": "P2T", "refs": ["T2", "C24", "C25", "C27", "R18"],
     "dst": [13.7, 32.5], "rot": 180,
     "region": [[133.0, 113.1, 138.6, 121.0]], "exclude_nets": ["BM2_DATA_P", "BM2_DATA_N"],
     "why": "T2 cluster in the band east of T1, rotated 180 so its data pins face west (toward U1's port-2 pins). Region "
            "east edge 139.2 -> 138.6 (session 2): Sofar's GND pour-stitching via at mote (138.751, 116.854) serves the "
            "U5 cell's R23 on the mote and lands 0.4 mm in front of T2's data pads after the 180 rotation, where it blocked "
            "the pair's approach (the bottom pour is stitched by this board's own vias)"},
    {"name": "B33", "refs": ["U5", "C30", "L3", "C28", "C29", "R20", "R21", "R22", "R23"],
     "dst": [31.551, 34.44], "rot": 0,
     "region": [{"rect": [138.2, 104.6, 146.4, 112.9], "layers": ["F.Cu", "In1.Cu", "In3.Cu"]},
                {"rect": [138.2, 112.9, 144.3, 119.0], "layers": ["F.Cu", "B.Cu", "In1.Cu", "In3.Cu"]}],
     "clip_zone_nets": ["3V3"],
     "why": "U5 cell (switch loop U5–C30–L3, bottom-side dividers and caps, top pours, In3 GND patch) in the east strip; "
            "the output cap C31 is the only part split off (the cell is 8.55 mm wide with it 9.65: the strip is 8.9)"},
    {"name": "B5V", "refs": ["U5", "C30", "L3", "C28", "C29", "R20", "R21", "R22", "R23"],
     "ref_map": {"U5": "U10", "C30": "C55", "L3": "L6", "C28": "C53", "C29": "C54", "R20": "R39", "R21": "R37", "R22": "R40", "R23": "R38"},
     "dst": [31.551, 21.24], "rot": 0,
     "region": [{"rect": [138.2, 104.6, 146.4, 112.9], "layers": ["F.Cu", "In1.Cu", "In3.Cu"]},
                {"rect": [138.2, 112.9, 144.3, 119.0], "layers": ["F.Cu", "B.Cu", "In1.Cu", "In3.Cu"]}],
     "clip_zone_nets": ["3V3"],
     "why": "5 V buck = U5's cell copied again with its parts mapped by function (D13); C56/C57/C58/TP38 placed beside it"},
    {"name": "SENSE", "refs": ["U4", "R8", "R7", "C15", "TP22"],
     "dst": [19.8, 15.0], "rot": 0,
     "region": [[144.4, 112.4, 148.0, 120.2], [148.0, 114.2, 149.0, 120.2],
                {"rect": [143.6, 115.2, 144.4, 118.5], "layers": ["B.Cu"]}],
     "why": "R8 shunt + INA232 with Sofar's sense routing (all bottom-side parts) under L2's south-east, 4 mm from L2's "
            "P_IN pad as on the mote; J1's pin field leaves no ≥ 0.5 mm path for P_IN into the strip east of J1. The third "
            "rect (Bottom only) holds the west detour of the two Kelvin traces U4.1-R8.2 / U4.2-R8.1 (QE S7.b R2-F1)"},
    {"name": "DAMP3", "refs": ["C23"],
     "dst": [33.5, 40.95], "rot": 90,
     "region": [],
     "why": "C23 (the sense block's 47 uF damping electrolytic, the block's only top part) alone in the strip; R16 beside U11"},
    {"name": "DAMP1", "refs": ["C21", "C20", "TP23"],
     "dst": [8.9, 57.5], "rot": 90,
     "region": [[151.9, 117.5, 156.5, 121.2]],
     "why": "VBUS 10 uF + its test pad in the south-west pocket beside J5 (R16 moved next to C23's partner U11 row)"},
    {"name": "DAMP2", "refs": ["C22"],
     "dst": [33.5, 48.6], "rot": 0,
     "region": [[146.8, 100.4, 155.8, 107.0]],
     "why": "second damping electrolytic in the strip, Sofar's orientation (8.8 mm wide: pads 0.5 mm from the edge); its resistor R15 placed beside it"},
    {"name": "B18", "refs": ["U6", "L4", "C32", "C33", "TP21"],
     "dst": [19.0, 31.4], "rot": 90,
     "region": [{"rect": [141.8, 108.4, 148.3, 113.2], "layers": ["B.Cu"]}],
     "exclude_vias_on": ["3V3", "GND"],
     "why": "1.8 V buck (all bottom) east of L1 beside J1, rotated 90 to clear D2/C17 under L1"},
]

# ---- fresh placements: ref -> (x, y, rot, side) -------------------------------------------------------------------
FRESH = {
    # strip, top (north -> south): JP1, 5 V cell (block), 3.3 V cell (block) + C31, C23, C22 (blocks), U11 cell
    "JP1": (32.05, 9.45, 0, "F"),
    "C31": (36.6, 34.44, 0, "F"),
    "U11": (32.5, 54.35, -90, "F"), "C49": (35.7, 54.35, 90, "F"), "R34": (29.6, 55.6, 90, "F"),
    # strip, bottom
    "C56": (31.6, 12.5, 0, "B"), "C57": (31.6, 14.7, 0, "B"), "C58": (36.6, 14.0, 0, "B"), "TP38": (36.6, 16.3, 0, "B"),
    "TP20": (37.0, 8.8, 0, "B"), "TP24": (34.6, 9.0, 0, "B"),
    "R26": (36.6, 21.5, 0, "B"), "R27": (36.6, 23.1, 0, "B"),
    "R15": (37.0, 45.5, 90, "B"), "R16": (37.0, 42.5, 90, "B"),
    "D3": (33.0, 53.9, 90, "B"), "R35": (30.6, 52.3, 90, "B"), "R41": (36.0, 52.3, 0, "B"), "R42": (36.0, 53.6, 0, "B"),
    "C50": (36.4, 55.5, 0, "B"), "TP35": (36.6, 48.5, 0, "B"), "TP19": (30.6, 43.3, 0, "B"),
    # north edge: status LEDs west -> east D10 (port 2), D8 (power), D9 (port 1), top; JP2 and R44-R46 under them, bottom
    "D10": (11.6, 1.4, 0, "F"), "D8": (15.0, 1.4, 0, "F"), "D9": (18.4, 1.4, 0, "F"),
    "JP2": (15.0, 4.3, 0, "B"), "R46": (10.8, 4.2, 90, "B"), "R44": (18.0, 4.2, 90, "B"), "R45": (19.4, 4.2, 90, "B"),
    # pocket south, bottom
    "R43": (7.5, 36.3, 0, "B"), "TP8": (9.8, 36.3, 0, "B"),
    # band / P2 leftovers, bottom
    "C26": (17.0, 23.3, 0, "B"),
    # south pockets
    "D1": (20.9, 59.0, 90, "F"), "R11": (21.0, 58.0, 90, "B"), "TP36": (19.5, 62.3, 0, "B"),
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
    rings = [b for b in prev["blocks"] if b["name"].startswith("RING_")]      # M1's ring blocks stay; a rerun (START=m2) replaces the rest
    json.dump({"frame": prev["frame"], "blocks": rings + out,
               "fresh": {r: {"x": v[0], "y": v[1], "rot": v[2], "side": v[3]} for r, v in FRESH.items()}},
              open(geom.EXP / "blocks.json", "w"), indent=1)
    placed = {r for b in out for r in b["placed"]} | set(FRESH)
    print(f"M2 placed: {len(out)} blocks ({sum(len(b['placed']) for b in out)} parts) + {len(FRESH)} fresh parts")
    parked = [f.GetReference() for f in board.GetFootprints() if geom.xy(f.GetPosition())[0] > 40]
    print("still parked:", parked)


if __name__ == "__main__":
    main()
