#!/usr/bin/env python3
"""M2: place every part. Copied blocks are rigid (translate + rotate by multiples of 90°, same side as the mote,
proven by pads); everything else is placed fresh. Records every block transform in blocks.json (M3 copies the copper
with the same definitions). Applied by tools/build_all.sh after m1_fixed.py.

Session 2.b: two placements, chosen by VARIANT=pocket (default, the built one) or VARIANT=centre (OPTIONS.md addendum A3, LESSONS §3):
  centre  U1 in the middle of the 11 mm band between the inductor envelopes, rotated 270° (port-2 pins north toward
          T2 and L2, port-1 pins south toward T1 and L1, SPI pins east toward J1); the ADIN block's bottom parts under
          the band; the 1.8 V buck in the west pocket U1 leaves behind.
  pocket  session 2's placement moved with the frame (U1 in the taller west pocket, T1 / T2 in the band beside it).
Both: the board 49 × 68 (geom.py), the port-1 blocks 3 mm south with L1's envelope, the jumpers JP1 / JP2 on top in the
north band beside the LEDs, the fiducials ≥ 3.35 mm from the edge (DFM.md row 26).

Why the blocks are what they are (details in LOG.md M2): the brief's PORT, SPINE and BUCK blocks are larger than the
room the fixed items leave (the strip east of J1, the band between the inductor envelopes, the west pocket), so each
is split into the largest rigid pieces that fit; the copper between the pieces is new routing.
"""
import json
import os

import geom
import motecopy
from geom import V

VARIANT = os.environ.get("VARIANT", "pocket")       # the built placement (OPTIONS addendum A3); "centre" is kept for the next router step
S = geom.GROWTH["south"]            # 3.0: the port-1 side and the south band move with L1's envelope
SB = S + geom.L1_EXTRA              # the south band's parts: 1.5 more when L1 is 1.5 further south (J5WEST=1)

# ---- rigid blocks: refs on the mote, anchor = the first ref's mote position; dst = where that anchor lands --------
# region: rects in mote mm (optionally with a "layers" list) selecting the copper that belongs to the block (M3).
COMMON = [
    {"name": "P1L", "refs": ["L1", "D4", "R12", "R13", "TP3", "TP5", "C17", "D2"],
     "dst": [12.74, 44.25 + S + geom.L1_EXTRA], "rot": 90,
     "region": [[158.9, 102.0, 172.2, 115.0]],
     "exclude_region": [[165.0, 101.9, 168.3, 105.0]],
     "why": "L1 centred in its envelope (3 mm south in 2.b) with the bottom-side parts Sofar put under it; rotated 90 so the bus "
            "pads face west toward MP1/MP2 (BM1_P north-west, BM1_N south-west) and VBUS/GND face east"},
    {"name": "P2L", "refs": ["L2", "D5", "R17", "R19", "TP7", "TP13"],
     "dst": [12.74, 16.75], "rot": 90,
     "region": [[125.0, 101.5, 138.3, 112.7]],
     "why": "as P1L: bus pads west (BM2_P north-west toward MP3, BM2_N south-west toward MP4)"},
    {"name": "B33", "refs": ["U5", "C30", "L3", "C28", "C29", "R20", "R21", "R22", "R23"],
     "dst": [31.551, 34.44], "rot": 0,
     "region": [{"rect": [138.2, 104.6, 146.4, 112.9], "layers": ["F.Cu", "In1.Cu", "In3.Cu"]},
                {"rect": [138.2, 112.9, 144.3, 119.0], "layers": ["F.Cu", "B.Cu", "In1.Cu", "In3.Cu"]}],
     "clip_zone_nets": ["3V3"],
     "why": "U5 cell (switch loop U5–C30–L3, bottom-side dividers and caps, top pours, In3 GND patch) in the east strip; "
            "the output cap C31 is the only part split off (the cell is 8.55 mm wide with it 9.65: the strip was 8.9, is 11.9 in 2.b)"},
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
     "dst": [8.9, 57.5 + SB], "rot": 90,
     "region": [[151.9, 117.5, 156.5, 121.2]],
     "why": "VBUS 10 uF + its test pad in the south-west pocket beside J5 (3 mm south with the south band in 2.b)"},
    {"name": "DAMP2", "refs": ["C22"],
     "dst": [33.5, 48.6], "rot": 0,
     "region": [[146.8, 100.4, 155.8, 107.0]],
     "why": "second damping electrolytic in the strip, Sofar's orientation (8.8 mm wide: pads 0.5 mm from the old edge, 3.5 mm from the new one); its resistor R15 placed beside it"},
]

# the ADIN block, the two transformer clusters and the 1.8 V buck differ per variant
ADIN_REFS = ["U1", "U2", "U3", "Y1", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10", "C11",
             "C12", "C13", "C14", "R1", "R2", "R3", "R4", "R5", "R6", "TP1", "TP2"]
P1T_REFS = ["T1", "C16", "C18"]            # session 2.b: C19 / R14 (the centre-tap cap and resistor) leave the rigid cluster (P1C)
P1C_REFS = ["C19", "R14"]
P2T_REFS = ["T2", "C24", "C25", "C27", "R18"]
B18_REFS = ["U6", "L4", "C32", "C33", "TP21"]
# U1's spot: x 11.8 = 0.9 mm west of the inductors' axis so T1's cluster (C19) clears J1's socket courtyard at x 23.43 and
# T1's data pads clear U1's courtyard (trials 1 and 2); y 31.1 = U1's courtyard on the band's north limit (26.5), so the
# port-1 pins (south edge, y 34.6) exit 1 mm south and meet T1's data pads at their own latitude (35.6) in a straight run
# (trial 2 at y 32.0: the pair went 2 mm south and back, 9.90 mm against the 9.5 limit)
U1_CENTRE = (11.8, geom.BAND[0] + 4.65 + (geom.BAND[1] - geom.BAND[0] - 11.0) / 2)      # any band growth beyond 11 mm is shared above and below      # x: 0.9 west of the inductors' axis so T1's C19 clears J1's socket courtyard; y: U1's courtyard on the band's north limit (its 9.3 mm + T1's 1.85 below U1's centre line fill the 11 mm)

VARIANTS = {
    "centre": [
        {"name": "ADIN", "refs": ADIN_REFS, "dst": list(U1_CENTRE), "rot": 0,
         "region": [[148.2, 107.5, 159.5, 114.1], [149.1, 114.1, 159.5, 119.7]],
         "zone_region": [[148.0, 107.5, 159.5, 120.6]],
         "exclude_nets": ["BM1_DATA_P", "BM1_DATA_N", "BM2_DATA_P", "BM2_DATA_N"],
         "why": "whole ADIN block in the CENTRE of the 11 mm band (Nick, 2026-10-08: central to the inductors and the header, away "
                "from the edge where strain and deflection concentrate), in the MOTE's own orientation (rot 0): port 1's data pins on "
                "the east edge toward T1 south-east of U1 (the mote's T1 position relative to U1, so the port-1 pair has the mote's "
                "own 9.5 mm geometry), port 2's on the west edge toward T2 south-west, the SPI / INT / RST pins and Sofar's fan-out "
                "vias on the north edge (under L2's envelope clearance: copper only), from where the SPI lane turns east to J1 on "
                "Internal 2. Trials 2-4 had U1 at rot 270 (SPI pins facing J1): the port-1 pins then sit on U1's south-WEST and T1 "
                "can only stand south-east (J1 bounds it), 7 mm away, so the pair came out 9.7-10.0 mm against the 9.5 limit, and "
                "Sofar's fan-out vias landed on T1's pads. The full region (mote y 107.5) is copied: nothing is clipped"},
        {"name": "P1T", "refs": P1T_REFS, "dst": [U1_CENTRE[0] + 8.6, U1_CENTRE[1] + 4.45], "rot": 0,
         "region": [[158.8, 115.2, 165.4, 119.8]], "exclude_nets": ["BM1_DATA_P", "BM1_DATA_N"],
         "why": "T1 (with its bottom caps C16 / C18) 1.0 mm further east than the mote has it relative to U1 (+8.6, +4.45: the "
                "courtyard stays inside the band's south limit), data pads facing west toward U1's port-1 pins. Trials 5 and 6 at the "
                "mote's +7.6 failed the pair: the swap figure needs 2 mm of straight run and found it only behind the pads (a U-turn "
                "the emitter cannot make); 1 mm more lets the figure sit on the south leg between U1's pads and T1's. The "
                "centre-tap cap C19 and R14 leave the cluster (P1C) because C19 would otherwise cross J1's socket courtyard"},
        {"name": "P1C", "refs": P1C_REFS, "dst": [18.3, 32.0], "rot": 90,
         "region": [],
         "why": "T1's centre-tap cap C19 (anchor) and R14 as one rigid piece on the bottom between U1's east side and T1 (the "
                "mote's copper between them and T1 lies outside the P1T region anyway: new routing)"},
        {"name": "P2T", "refs": P2T_REFS, "dst": [2.0, U1_CENTRE[1] + 4.35], "rot": 0,
         "region": [[133.0, 113.1, 138.6, 121.0]], "exclude_nets": ["BM2_DATA_P", "BM2_DATA_N"],
         "why": "T2 cluster south-west of U1 at the band's south edge, the mote's own rotation (block rot 0: T2 at 180 on the mote, "
                "data pads facing east toward U1's port-2 pins), 9.8 mm from U1 instead of the mote's 18.5 (trial 6 at 8.8: no room for the swap figure); region east edge 138.6 "
                "as session 2 (Sofar's R23 GND via dropped). Its bus legs run north to L2 past U1's west side"},
        {"name": "B18", "refs": B18_REFS, "dst": [-6.0, 33.5], "rot": 90,
         "region": [{"rect": [141.8, 108.4, 148.3, 113.2], "layers": ["B.Cu"]}],
         "exclude_vias_on": ["3V3", "GND"],
         "why": "1.8 V buck (all bottom) in the west pocket U1 left (x -10 .. -1.5 between the insert keep-outs); 1V8 runs east to U2 "
                "under the band, 3V3 comes from the island in the strip"},
    ],
    "pocket": [
        {"name": "ADIN", "refs": ADIN_REFS, "dst": [-1.7, (26.2 + 41.3) / 2], "rot": 90,
         "region": [[148.2, 107.5, 159.5, 114.1], [149.1, 114.1, 159.5, 119.7]],
         "zone_region": [[148.0, 107.5, 159.5, 120.6]],
         "exclude_nets": ["BM1_DATA_P", "BM1_DATA_N", "BM2_DATA_P", "BM2_DATA_N"],
         "why": "whole ADIN block in the west pocket (15.1 mm tall now that MP1 is 2.5 mm south), rotated 90 so port 1's data pins "
                "face north toward T1 in the band and port 2's face south. x -1.7 = session 2's spot on the OLD edge, i.e. 3 mm "
                "further from the new west edge (8.8 mm): Nick, 2026-10-08, 'the ADIN is too close to the west edge, move it east'; "
                "the insert keep-outs do not reach U1's latitude, so nothing else limits it but T1 / T2 / B18 east of it. The region "
                "is the mote's full 107.5 again: Sofar's ~{ADIN_INT} via lands at x -7.2, 2.8 mm inside the edge (no hand via)"},
        {"name": "P1T", "refs": P1T_REFS, "dst": [6.7, 29.45], "rot": 0,
         "region": [[158.8, 115.2, 165.4, 119.8]], "exclude_nets": ["BM1_DATA_P", "BM1_DATA_N"],
         "why": "T1 cluster in the band beside U1 as session 2 relative to U1 but 0.2 mm north (trial 3 at session 2's relation gave "
                "BM1_DATA_P 9.59 against the 9.5 limit: the pads sit 0.2 above the pins' exit stub now; trial 2 at 0.25 mm south had "
                "C16's track meet C8's pad). C19 / R14 stay in this cluster here (P1C is the centre variant's split)"},
        {"name": "P1C", "refs": P1C_REFS, "dst": [6.7 + 2.25, 29.45 - 3.4], "rot": 0,
         "region": [],
         "why": "C19 / R14 at their mote spot relative to T1 (the split is only needed by the centre variant)"},
        {"name": "P2T", "refs": P2T_REFS, "dst": [13.7, 33.75], "rot": 180,
         "region": [[133.0, 113.1, 138.6, 121.0]], "exclude_nets": ["BM2_DATA_P", "BM2_DATA_N"],
         "why": "T2 cluster in the band east of T1, rotated 180 so its data pins face west (toward U1's port-2 pins), as session 2"},
        {"name": "B18", "refs": B18_REFS, "dst": [19.0, 32.9], "rot": 90,
         "region": [{"rect": [141.8, 108.4, 148.3, 113.2], "layers": ["B.Cu"]}],
         "exclude_vias_on": ["3V3", "GND"],
         "why": "1.8 V buck (all bottom) under the band's east end beside J1, as session 2"},
    ],
}
BLOCKS = COMMON + VARIANTS[VARIANT]

# ---- fresh placements: ref -> (x, y, rot, side) -------------------------------------------------------------------
# North band (x 6.5 … 23.5 between the Pi's standoff keep-outs, y 0.5 … 7.0 under L2's envelope clearance), top:
# row 1 at the edge: the LEDs D10 / D8 / D9 (light up, nothing north of them) and JP1 (5 V to the Pi) at the band's east
# end; row 2: FID4, JP2 (the LED supply) and FID3 ≥ 3.35 mm from the edge (DFM.md row 26). Both jumpers are on top, at
# the north edge, with no tall part beside them (Nick, 2026-10-08); their nets' cost is in OPTIONS.md (addendum).
# Bottom under the band: the LED resistors R44–R46 in a row at y 3.0 and the bottom fiducials FID2 / FID1 under FID4 / FID3.
FRESH_COMMON = {
    "D10": (8.1, 1.4, 0, "F"), "D8": (11.5, 1.4, 0, "F"), "D9": (14.9, 1.4, 0, "F"),
    "JP1": (20.4, 2.2, 0, "F"), "JP2": (12.5, 5.2, 0, "F"),
    "FID4": (7.8, 5.0, 0, "F"), "FID3": (17.0, 5.3, 0, "F"), "FID2": (7.8, 5.0, 0, "B"), "FID1": (17.0, 5.3, 0, "B"),
    "R46": (8.1, 3.0, 0, "B"), "R44": (11.5, 3.0, 0, "B"), "R45": (14.9, 3.0, 0, "B"),
    # strip, top (north -> south): 5 V cell (block), 3.3 V cell (block) + C31, C23, C22 (blocks), U11 cell
    "C31": (36.6, 34.44, 0, "F"),
    "U11": (32.5, 54.35, -90, "F"), "C49": (35.7, 54.35, 90, "F"), "R34": (29.6, 55.6, 90, "F"),
    # strip, bottom
    "C56": (31.6, 12.5, 0, "B"), "C57": (31.6, 14.7, 0, "B"), "C58": (36.6, 14.0, 0, "B"), "TP38": (36.6, 16.3, 0, "B"),
    "TP20": (37.0, 8.8, 0, "B"), "TP24": (34.6, 9.0, 0, "B"),
    "R26": (36.6, 21.5, 0, "B"), "R27": (36.6, 23.1, 0, "B"),
    "R15": (37.0, 45.5, 90, "B"), "R16": (37.0, 42.5, 90, "B"),
    "D3": (33.0, 53.9, 90, "B"), "R35": (30.6, 52.3, 90, "B"), "R41": (36.0, 52.3, 0, "B"), "R42": (36.0, 53.6, 0, "B"),
    "C50": (36.4, 55.5, 0, "B"), "TP35": (36.6, 48.5, 0, "B"), "TP19": (30.6, 43.3, 0, "B"),
    # band / P2 leftovers, bottom
    "C26": (17.0, 23.3, 0, "B"),
    # south band (3 mm south with the frame)
    "D1": (20.9, 59.0 + SB, 90, "F"), "R11": (21.0, 58.0 + SB, 90, "B"), "TP36": (19.5, 62.3 + S, 0, "B"),
    "FID5": (15.0, 55.6 + SB, 0, "F"), "FID6": (15.0, 55.6 + SB, 0, "B"),
}
FRESH_VARIANT = {
    # ADIN_PWR pull-down and its test pad (bottom) near U2 / U3
    "centre": {"R43": (4.0, 30.0, 0, "B"), "TP8": (2.0, 30.0, 0, "B")},
    "pocket": {"R43": (7.5, 37.8, 0, "B"), "TP8": (9.8, 37.8, 0, "B")},
}
FRESH = {**FRESH_COMMON, **FRESH_VARIANT[VARIANT]}


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
    json.dump({"frame": prev["frame"], "variant": VARIANT, "blocks": rings + out,
               "fresh": {r: {"x": v[0], "y": v[1], "rot": v[2], "side": v[3]} for r, v in FRESH.items()}},
              open(geom.EXP / "blocks.json", "w"), indent=1)
    print(f"M2 ({VARIANT}) placed: {len(out)} blocks ({sum(len(b['placed']) for b in out)} parts) + {len(FRESH)} fresh parts")
    parked = [f.GetReference() for f in board.GetFootprints() if geom.xy(f.GetPosition())[0] > 45]
    print("still parked:", parked)


if __name__ == "__main__":
    main()
