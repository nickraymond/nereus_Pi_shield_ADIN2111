#!/usr/bin/env python3
"""M3: copy each block's mote copper (tracks, arcs, vias, zones) onto the board with the block's transform.

Applied by tools/build_all.sh after m2_place.py. The RING blocks were copied in M1; every other block in blocks.json is
copied here. The selection rule lives in motecopy.select (shared with blockcheck.py).
"""
import json

import geom
import motecopy


def main():
    board = geom.load()
    mote = motecopy.Mote(board)
    data = json.load(open(geom.EXP / "blocks.json"))
    for blk in data["blocks"]:
        if blk["name"].startswith("RING_"):
            continue
        T = motecopy.transform_of(blk)
        sel = mote.select(blk)
        blk["copied"] = mote.copy_copper(blk, T, sel)
        print(f"{blk['name']:6s} {blk['copied']}")
    geom.save(board)
    json.dump(data, open(geom.EXP / "blocks.json", "w"), indent=1)
    if mote.net_conflicts:
        print("net map conflicts:", mote.net_conflicts)


if __name__ == "__main__":
    main()
