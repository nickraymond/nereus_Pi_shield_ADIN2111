#!/usr/bin/env python3
"""M3: copy each block's mote copper (tracks, arcs, vias, zones) onto the board with the block's transform.

Applied by tools/build_all.sh after m2_place.py. The RING blocks were copied in M1; every other block in blocks.json is
copied here. The selection rule lives in motecopy.select (shared with blockcheck.py).

Session 2 (QE round 1 F2): (1) HAND_VIAS re-add, by hand and with a written reason, a mote via that a region clip
dropped although it carried a pad-to-pad connection of the block; each is checked on the board (it touches the stubs it
joins, keeps the edge clearance and 0.15 mm from other-net copper) and recorded in blocks.json "hand". (2) The board
copies of every mote item on a pad-to-pad path of its block (motecopy.Mote.pad_paths) are recorded in blocks.json
"protected" with their geometry; tools/dangling.py refuses to trim them.
"""
import json

import pcbnew

import geom
import motecopy
import router
from geom import MM, mm, V

import os
# the hand via is only needed when the ADIN block sits at the west edge (VARIANT=pocket); in the centre placement the
# region keeps Sofar's own via (mote y 107.509 is inside the full region's west edge 107.5)
# centre (U1 at rot 0, the full region): no hand via, Sofar's ~{ADIN_INT} via is copied; pocket (rot 90, region clipped at
# mote y 107.9 for the board edge): the via at the clip line's stub ends, (-5.05, -2.25) from U1 (session 2: (-6.75, 30.25) for U1 at (-1.7, 32.5))
HAND_VIAS = [] if os.environ.get("VARIANT", "pocket") == "centre" else [
    {"block": "ADIN", "net": "/Top-Level Schematic/~{ADIN_INT}", "mote_via": [156.571, 107.509], "rel_u1": [-5.05, -2.25], "dia": 0.45, "drill": 0.2,
     "joins": "Sofar's ~{ADIN_INT} fan-out: the Top lead-out from U1.39 (ends at (-6.804, 30.3)) and the Bottom lead-out to R1.1 "
              "(ends at (-6.804, 30.2)), both clipped at the ADIN region's west edge (mote y 107.9, OPTIONS Q5)",
     "why": "on the mote the via joins the two; transformed it lands at (-7.19, 29.93), 0.08 mm inside the board edge and inside "
            "the 0.5 mm edge clearance (BRIEF §2), so the region could not keep it; 0.44 mm further east both clipped stub "
            "ends lie under a 0.45 mm via that keeps 0.53 mm from the edge"},
]


def hand_vias(board, data):
    """Add HAND_VIAS and prove each on the board (fail loudly otherwise)."""
    o = geom.OUTLINE
    recs = []
    blocks = {b["name"]: b for b in data["blocks"]}
    for hv in HAND_VIAS:
        if "rel_u1" in hv:          # session 2.b: the spot follows the ADIN block (session 2 had it absolute at (-6.75, 30.25) for U1 at (-1.7, 32.5))
            d = blocks[hv["block"]]["dst"]
            hv["at"] = [round(d[0] + hv["rel_u1"][0], 3), round(d[1] + hv["rel_u1"][1], 3)]
        x, y = hv["at"]
        r = hv["dia"] / 2
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(V(x, y))
        v.SetViaType(pcbnew.VIATYPE_THROUGH)
        v.SetWidth(MM(hv["dia"]))
        v.SetDrill(MM(hv["drill"]))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetNet(board.FindNet(hv["net"]))
        board.Add(v)
        edge = min(x - r - o["x0"], o["x1"] - x - r, y - r - o["y0"], o["y1"] - y - r)
        joined, worst = [], 9.0
        for t in board.GetTracks():
            if t is v or t.m_Uuid.AsString() == v.m_Uuid.AsString():
                continue
            layers = geom.CU if t.GetClass() == "PCB_VIA" else [t.GetLayer()]
            for l in layers:
                d = mm(t.GetEffectiveShape(l).GetClearance(v.GetEffectiveShape(l)))
                if t.GetNetname() == hv["net"]:
                    if d <= 0:
                        joined.append(board.GetLayerName(l))
                elif d < worst:
                    worst = d
        for f in board.GetFootprints():
            for pd in f.Pads():
                if pd.GetNetname() == hv["net"]:
                    continue
                for l in (geom.CU if pd.GetDrillSize().x > 0 else [ll for ll in geom.CU if pd.IsOnLayer(ll)]):
                    d = mm(pd.GetEffectiveShape(l).GetClearance(v.GetEffectiveShape(l)))
                    if d < worst:
                        worst = d
        rec = dict(hv)
        rec.update({"edge_mm": round(edge, 3), "joins_layers": sorted(set(joined)), "min_other_net_clearance_mm": round(worst, 3)})
        recs.append(rec)
        print(f"hand via {hv['net'].rsplit('/', 1)[-1]} at {hv['at']}: edge {edge:.3f} mm, joins {sorted(set(joined))}, other-net clearance {worst:.3f} mm")
        if edge < geom.EDGE_CLEARANCE - 1e-6 or len(set(joined)) < 2 or worst < 0.15 - 1e-6:
            raise SystemExit(f"hand via {hv['net']} at {hv['at']} fails its check (edge {edge:.3f} >= {geom.EDGE_CLEARANCE}, joins {sorted(set(joined))} on >= 2 layers, "
                             f"clearance {worst:.3f} >= 0.15): move it or drop it from HAND_VIAS")
    data["hand"] = recs


def protected_records(mote, blk, T, sel):
    """Board-frame geometry of the block's mote pad-to-pad items (after the transform and the region clip)."""
    out = []
    nmap = mote.block_net_map(blk)
    clip_of = {id(item): rect for item, rect in sel["copper"]}
    for item in mote.pad_paths(blk, sel):
        net = nmap.get(item.GetNetname())
        if net is None:
            continue
        cls = item.GetClass()
        if cls == "PCB_VIA":
            p = T.apply_xy(geom.xy(item.GetPosition()))
            out.append({"block": blk["name"], "kind": "via", "net": net, "at": [round(p[0], 3), round(p[1], 3)]})
        elif cls == "PCB_ARC":
            m = T.apply_xy(geom.xy(item.GetMid()))
            out.append({"block": blk["name"], "kind": "arc", "net": net, "mid": [round(m[0], 3), round(m[1], 3)]})
        else:
            s0, e0 = item.GetStart(), item.GetEnd()
            rect = clip_of.get(id(item))
            if rect is not None:
                s0, e0 = motecopy.clip_segment(s0, e0, rect)
            a, b = T.apply_xy(geom.xy(s0)), T.apply_xy(geom.xy(e0))
            out.append({"block": blk["name"], "kind": "track", "net": net, "layer": mote.board.GetLayerName(item.GetLayer()),
                        "start": [round(a[0], 3), round(a[1], 3)], "end": [round(b[0], 3), round(b[1], 3)]})
    return out


def main():
    board = geom.load()
    mote = motecopy.Mote(board)
    data = json.load(open(geom.EXP / "blocks.json"))
    protected = []
    for blk in data["blocks"]:
        if blk["name"].startswith("RING_"):
            continue
        T = motecopy.transform_of(blk)
        sel = mote.select(blk)
        blk["copied"] = mote.copy_copper(blk, T, sel)
        recs = protected_records(mote, blk, T, sel)
        blk["protected"] = len(recs)
        protected += recs
        print(f"{blk['name']:6s} {blk['copied']} protected (mote pad-to-pad) {len(recs)}")
    data["protected"] = protected
    hand_vias(board, data)
    geom.save(board)
    json.dump(data, open(geom.EXP / "blocks.json", "w"), indent=1)
    if mote.net_conflicts:
        print("net map conflicts:", mote.net_conflicts)


if __name__ == "__main__":
    main()
