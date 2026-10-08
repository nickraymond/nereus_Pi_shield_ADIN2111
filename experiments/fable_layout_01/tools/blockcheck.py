#!/usr/bin/env python3
"""blockcheck: prove each copied block matches the mote after the inverse transform (BRIEF M3 / §8.4).

  $PY tools/blockcheck.py [out/m3/blockcheck.md]

For every block in blocks.json it re-selects the mote items with the same rule the copy used (motecopy.select),
transforms them with the block's transform and looks for each on the board: footprint pads (centre and net), tracks
(start, end, width, layer, net), arcs (start, mid, end), vias (position, diameter, drill), zones (outline vertices).
Tolerance 0.001 mm. Reports per block: matched / missing / extra, where "extra" is board copper on the block's nets
inside the block's transformed region that no mote item explains (new routing, or a mistake).
"""
import sys

import pcbnew

import geom
import motecopy
from geom import mm

TOL = 0.001


def key_pt(p):
    return (round(p[0], 3), round(p[1], 3))


def close(a, b):
    return abs(a[0] - b[0]) <= TOL and abs(a[1] - b[1]) <= TOL


def main(out_path=None):
    board = geom.load()
    mote = motecopy.Mote(board)
    data = motecopy.load_blocks()
    bfp = geom.fp_by_ref(board)
    tracks = [t for t in board.GetTracks() if t.GetClass() == "PCB_TRACK"]
    arcs = [t for t in board.GetTracks() if t.GetClass() == "PCB_ARC"]
    vias = [t for t in board.GetTracks() if t.GetClass() == "PCB_VIA"]
    zones = [z for z in board.Zones() if not z.GetIsRuleArea()]
    lines = ["# blockcheck — copied blocks vs the mote\n",
             "| Block | transform (src → dst, rot) | pads | tracks | arcs | vias | zones | missing | extra |", "|---|---|---|---|---|---|---|---|---|"]
    total_missing = 0
    details = []
    for blk in data["blocks"]:
        T = motecopy.transform_of(blk)
        sel = mote.select(blk)
        nmap = mote.block_net_map(blk)
        ref_map = blk.get("ref_map", {})
        miss, counts = [], {"pads": [0, 0], "tracks": [0, 0], "arcs": [0, 0], "vias": [0, 0], "zones": [0, 0]}
        # pads
        for f in sel["footprints"]:
            dref = ref_map.get(f.GetReference(), f.GetReference())
            got = {p.GetNumber(): p for p in bfp[dref].Pads() if p.GetNumber()}
            for p in f.Pads():
                if not p.GetNumber():
                    continue
                counts["pads"][1] += 1
                want = T.apply_xy(geom.xy(p.GetPosition()))
                g = got.get(p.GetNumber())
                wnet = nmap.get(p.GetNetname(), "") if p.GetNetname() else ""
                if g and close(want, geom.xy(g.GetPosition())) and (not wnet or g.GetNetname() == wnet):
                    counts["pads"][0] += 1
                else:
                    miss.append(f"pad {dref}.{p.GetNumber()} want {key_pt(want)} net {wnet}")
        matched_ids = set()
        for item, rect in sel["copper"]:
            cls = item.GetClass()
            net = nmap.get(item.GetNetname())
            if net is None:
                continue
            if cls == "PCB_VIA":
                counts["vias"][1] += 1
                want = T.apply_xy(geom.xy(item.GetPosition()))
                w, d = mm(item.GetWidth(pcbnew.F_Cu)), mm(item.GetDrillValue())
                hit = next((v for v in vias if close(want, geom.xy(v.GetPosition())) and abs(mm(v.GetWidth(pcbnew.F_Cu)) - w) <= TOL
                            and abs(mm(v.GetDrillValue()) - d) <= TOL and v.GetNetname() == net), None)
                if hit:
                    counts["vias"][0] += 1
                    matched_ids.add(id(hit))
                else:
                    miss.append(f"via {key_pt(want)} {w}/{d} {net}")
            elif cls == "PCB_ARC":
                counts["arcs"][1] += 1
                s, m, e = (T.apply_xy(geom.xy(q)) for q in (item.GetStart(), item.GetMid(), item.GetEnd()))
                w, lay = mm(item.GetWidth()), item.GetLayer()
                hit = next((a for a in arcs if a.GetLayer() == lay and abs(mm(a.GetWidth()) - w) <= TOL and a.GetNetname() == net
                            and close(m, geom.xy(a.GetMid()))
                            and ((close(s, geom.xy(a.GetStart())) and close(e, geom.xy(a.GetEnd())))
                                 or (close(e, geom.xy(a.GetStart())) and close(s, geom.xy(a.GetEnd()))))), None)
                if hit:
                    counts["arcs"][0] += 1
                    matched_ids.add(id(hit))
                else:
                    miss.append(f"arc {key_pt(s)}-{key_pt(e)} w{w} {net}")
            else:
                counts["tracks"][1] += 1
                s0, e0 = item.GetStart(), item.GetEnd()
                if rect is not None:
                    s0, e0 = motecopy.clip_segment(s0, e0, rect)
                s, e = T.apply_xy(geom.xy(s0)), T.apply_xy(geom.xy(e0))
                w, lay = mm(item.GetWidth()), item.GetLayer()
                hit = next((t for t in tracks if t.GetLayer() == lay and abs(mm(t.GetWidth()) - w) <= TOL and t.GetNetname() == net
                            and ((close(s, geom.xy(t.GetStart())) and close(e, geom.xy(t.GetEnd())))
                                 or (close(e, geom.xy(t.GetStart())) and close(s, geom.xy(t.GetEnd()))))), None)
                if hit:
                    counts["tracks"][0] += 1
                    matched_ids.add(id(hit))
                else:
                    miss.append(f"track {key_pt(s)}-{key_pt(e)} w{w} {board.GetLayerName(lay)} {net}" + (" (clipped)" if rect is not None else ""))
        for z, rect in sel["zones"]:
            net = nmap.get(z.GetNetname())
            if net is None:
                continue
            counts["zones"][1] += 1
            outline = pcbnew.SHAPE_POLY_SET(z.Outline())
            if rect is not None:
                outline.BooleanIntersection(motecopy.rect_poly(rect))
                outline.Fracture()
            want = sorted(key_pt(T.apply_xy(geom.xy(outline.Outline(0).CPoint(i)))) for i in range(outline.Outline(0).PointCount()))
            hit = None
            for bz in zones:
                if bz.GetNetname() != net or bz.GetLayer() != z.GetLayer():
                    continue
                o = bz.Outline().Outline(0)
                got = sorted(key_pt(geom.xy(o.CPoint(i))) for i in range(o.PointCount()))
                if len(got) == len(want) and all(close(a, b) for a, b in zip(got, want)):
                    hit = bz
                    break
            if hit:
                counts["zones"][0] += 1
                matched_ids.add(id(hit))
            else:
                miss.append(f"zone {net} {board.GetLayerName(z.GetLayer())} {len(want)} pts")
        # extra: board copper on block nets inside the transformed region, not matched
        extra = 0
        region = blk.get("region")
        if region:
            rects = [(r["rect"] if isinstance(r, dict) else r) for r in region]
            polys = []
            for r in rects:
                c = [T.apply_xy((r[0], r[1])), T.apply_xy((r[2], r[1])), T.apply_xy((r[2], r[3])), T.apply_xy((r[0], r[3]))]
                xs, ys = [p[0] for p in c], [p[1] for p in c]
                polys.append((min(xs), min(ys), max(xs), max(ys)))
            bnets = {nmap[n] for n in sel["nets"] if n in nmap}

            def inside(p):
                return any(r[0] - TOL <= p[0] <= r[2] + TOL and r[1] - TOL <= p[1] <= r[3] + TOL for r in polys)
            for t in tracks + arcs + vias:
                if id(t) in matched_ids or t.GetNetname() not in bnets:
                    continue
                pts = [geom.xy(t.GetPosition())] if t.GetClass() == "PCB_VIA" else [geom.xy(t.GetStart()), geom.xy(t.GetEnd())]
                if all(inside(p) for p in pts):
                    extra += 1
        total_missing += len(miss)
        c = counts
        lines.append(f"| {blk['name']} | {tuple(round(v, 3) for v in blk['src'])} → {tuple(blk['dst'])}, {blk.get('rot', 0)}° | "
                     f"{c['pads'][0]}/{c['pads'][1]} | {c['tracks'][0]}/{c['tracks'][1]} | {c['arcs'][0]}/{c['arcs'][1]} | "
                     f"{c['vias'][0]}/{c['vias'][1]} | {c['zones'][0]}/{c['zones'][1]} | {len(miss)} | {extra} |")
        if miss:
            details.append(f"\n## {blk['name']}: missing\n" + "\n".join(f"- {m}" for m in miss[:40]) + ("\n- …" if len(miss) > 40 else ""))
    lines.append(f"\nTotal missing: {total_missing}. Tolerance {TOL} mm. 'extra' = board copper on the block's nets inside its region not explained by the mote (new routing or a mistake).")
    text = "\n".join(lines + details)
    if out_path:
        open(out_path, "w").write(text + "\n")
    print(text)
    return 1 if total_missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
