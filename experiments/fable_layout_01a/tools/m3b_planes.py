#!/usr/bin/env python3
"""M3b: add the plane zones (m4_route.make_planes) right after the block copy, so the pre-route dangling trim sees
Sofar's plane-stitching vias as connected and only removes the clipped lead-outs. Applied by tools/build_all.sh.
"""
import pcbnew

import geom
import m4_route


def main():
    board = geom.load()
    for i in range(board.GetNetInfo().GetNetCount()):
        ni = board.GetNetInfo().GetNetItem(i)
        if ni and ni.GetNetname():
            m4_route.NETS[ni.GetNetname().rsplit("/", 1)[-1]] = ni.GetNetname()
    polys = m4_route.planes(board)
    geom.save(board)
    print("M3b planes:", sorted(n.rsplit("/", 1)[-1] for n in polys))


if __name__ == "__main__":
    main()
