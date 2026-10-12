#!/usr/bin/env python3
"""Where the P and N legs of each ADIN data pair differ in length (read only): walks each net from U1's pin to the transformer
pad, lists every segment in order, and splits the length into the parts of the route (the pins' exit with its staggered vias,
the swap figure, the straight runs, the approach into the pads), so the P–N mismatch is attributed to the geometry that made it.
Writes out/review/pair_lengths.json and out/review/pair_<port>_legs.svg (both legs drawn, Top solid, Internal 1 dashed, the
mismatch sources called out). Lengths are track lengths (vias not counted), as tools/check_rules.py measures them.

  $PY tools/pair_lengths.py
"""
import json
import math
import re
from pathlib import Path

import pcbnew

import geom
from geom import mm

PAIRS = {1: ("BM1_DATA_P", "BM1_DATA_N", ("U1", "28", "27"), ("T1", "1", "2")),
         2: ("BM2_DATA_P", "BM2_DATA_N", ("U1", "5", "4"), ("T2", "1", "2"))}
TOP = "/Top-Level Schematic/"
OUT = geom.OUT / "review"
SCALE = 60


def walk(board, net, pin_pad):
    """Ordered chain of the net's tracks / vias from the pin pad to the far end: [(kind, layer, a, b, length)]."""
    items = [t for t in board.GetTracks() if t.GetNetname() == net]
    used = set()
    out = []
    # the first track touches the pin pad
    cur = None
    for t in items:
        if t.GetClass() == "PCB_TRACK" and t.GetEffectiveShape(t.GetLayer()).Collide(pin_pad.GetEffectiveShape(t.GetLayer()), 1):
            ta, tb = geom.xy(t.GetStart()), geom.xy(t.GetEnd())
            pc = geom.xy(pin_pad.GetPosition())
            if geom.dist(ta, pc) > geom.dist(tb, pc):
                ta, tb = tb, ta
            cur, p, layer = t, tb, t.GetLayer()
            used.add(t.m_Uuid.AsString())
            out.append(("track", board.GetLayerName(layer), ta, tb, mm(t.GetLength())))
            break
    while cur is not None:
        nxt = None
        for t in items:
            if t.m_Uuid.AsString() in used:
                continue
            if t.GetClass() == "PCB_VIA":
                if geom.dist(geom.xy(t.GetPosition()), p) < 0.002:
                    nxt = t
                    out.append(("via", "via", p, p, 0.0))
                    layer = None
                    break
            else:
                ta, tb = geom.xy(t.GetStart()), geom.xy(t.GetEnd())
                if layer is not None and t.GetLayer() != layer:
                    continue
                if geom.dist(ta, p) < 0.002:
                    nxt, p2 = t, tb
                elif geom.dist(tb, p) < 0.002:
                    nxt, p2, ta, tb = t, ta, tb, ta
                else:
                    continue
                layer = t.GetLayer()
                out.append(("track", board.GetLayerName(layer), ta, tb, mm(t.GetLength())))
                p = p2
                break
        if nxt is None:
            break
        used.add(nxt.m_Uuid.AsString())
        cur = nxt
    return out


def main():
    board = geom.load()
    fps = geom.fp_by_ref(board)
    notes = json.load(open(geom.OUT / "m4" / "routing.json"))["notes"]
    swaps = {}
    for n in notes:
        m = re.search(r"pair port (\d).*swap figures at \[\(\(([-\d.]+), ([-\d.]+)\)", n)
        if m:
            swaps[int(m.group(1))] = (float(m.group(2)), float(m.group(3)))
    result = {}
    for port, (pn, nn, (uref, up, un), (tref, tp, tn)) in PAIRS.items():
        pads = {pn: next(p for p in fps[uref].Pads() if p.GetNumber() == up), nn: next(p for p in fps[uref].Pads() if p.GetNumber() == un)}
        tpads = {pn: next(p for p in fps[tref].Pads() if p.GetNumber() == tp), nn: next(p for p in fps[tref].Pads() if p.GetNumber() == tn)}
        # every track and via of the net (the walk's order is not needed: the parts are classified by geometry; a walk that
        # started from the wrong of two tracks touching the pin pad once skipped a 0.45 mm piece of BM2_DATA_N)
        chains = {}
        for k in (pn, nn):
            ch = []
            for t in board.GetTracks():
                if t.GetNetname() != TOP + k:
                    continue
                if t.GetClass() == "PCB_VIA":
                    q = geom.xy(t.GetPosition())
                    ch.append(("via", "via", q, q, 0.0))
                elif t.GetClass() == "PCB_TRACK":
                    ch.append(("track", board.GetLayerName(t.GetLayer()), geom.xy(t.GetStart()), geom.xy(t.GetEnd()), mm(t.GetLength())))
            chains[k] = ch
        swap = swaps.get(port)
        parts = {}
        for k, ch in chains.items():
            acc = {"pins' exit (stub + start vias)": 0.0, "swap figure": 0.0, "approach into the pad": 0.0, "runs and bends": 0.0}
            pin = geom.xy(pads[k].GetPosition())
            pad = geom.xy(tpads[k].GetPosition())
            first_via = next((i for i, it in enumerate(ch) if it[0] == "via"), None)
            last_via = max((i for i, it in enumerate(ch) if it[0] == "via"), default=None)
            for i, (kind, layer, a, b, L) in enumerate(ch):
                if kind != "track":
                    continue
                mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
                if swap and geom.dist(mid, swap) <= 1.0:
                    acc["swap figure"] += L
                elif geom.dist(mid, pad) <= 1.6:
                    acc["approach into the pad"] += L
                elif geom.dist(mid, pin) <= 1.8:
                    acc["pins' exit (stub + start vias)"] += L
                else:
                    acc["runs and bends"] += L
            parts[k] = {kk: round(v, 2) for kk, v in acc.items()}
            parts[k]["total"] = round(sum(acc.values()), 2)
            parts[k]["segments"] = sum(1 for it in ch if it[0] == "track")
            parts[k]["vias"] = sum(1 for it in ch if it[0] == "via")
        result[port] = {"P": pn, "N": nn, "parts": parts, "swap": swap, "limit": 9.5 if port == 1 else 21.3,
                        "chains": {k: [(kind, layer, [round(a[0], 3), round(a[1], 3)], [round(b[0], 3), round(b[1], 3)], round(L, 3)) for kind, layer, a, b, L in ch] for k, ch in chains.items()}}
        # the drawing
        xs = [q[0] for ch in chains.values() for it in ch for q in (it[2], it[3])]
        ys = [q[1] for ch in chains.values() for it in ch for q in (it[2], it[3])]
        x0, y0, x1, y1 = min(xs) - 1.5, min(ys) - 1.5, max(xs) + 1.5, max(ys) + 2.2
        W, H = (x1 - x0) * SCALE, (y1 - y0) * SCALE

        def X(x):
            return (x - x0) * SCALE

        def Y(y):
            return (y - y0) * SCALE
        svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}" font-family="Helvetica, Arial, sans-serif">',
               f'<rect width="{W:.0f}" height="{H:.0f}" fill="#ffffff"/>']
        for ref in (uref, tref):
            for p in fps[ref].Pads():
                bb = p.GetBoundingBox()
                bx0, by0, bx1, by1 = mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())
                if bx1 < x0 or bx0 > x1 or by1 < y0 or by0 > y1:
                    continue
                net = p.GetNetname().rsplit("/", 1)[-1]
                col = "#cc3597" if net == pn else ("#2d67d2" if net == nn else "#d9ddd8")
                svg.append(f'<rect x="{X(bx0):.1f}" y="{Y(by0):.1f}" width="{(bx1 - bx0) * SCALE:.1f}" height="{(by1 - by0) * SCALE:.1f}" fill="{col}" fill-opacity="0.35" stroke="{col}" stroke-width="1"/>')
        for k, col in ((pn, "#cc3597"), (nn, "#2d67d2")):
            for kind, layer, a, b, L in chains[k]:
                if kind == "via":
                    svg.append(f'<circle cx="{X(a[0]):.1f}" cy="{Y(a[1]):.1f}" r="{0.225 * SCALE:.1f}" fill="none" stroke="{col}" stroke-width="2"/>')
                else:
                    dash = ' stroke-dasharray="6,4"' if layer != "Top Layer" else ""
                    svg.append(f'<line x1="{X(a[0]):.1f}" y1="{Y(a[1]):.1f}" x2="{X(b[0]):.1f}" y2="{Y(b[1]):.1f}" stroke="{col}" stroke-width="{0.2 * SCALE:.1f}" stroke-linecap="round"{dash}/>')
        if swap:
            svg.append(f'<circle cx="{X(swap[0]):.1f}" cy="{Y(swap[1]):.1f}" r="{1.0 * SCALE:.1f}" fill="none" stroke="#b8700f" stroke-width="1.5" stroke-dasharray="3,3"/>')
            svg.append(f'<text x="{X(swap[0]) + 1.05 * SCALE:.1f}" y="{Y(swap[1]) - 0.2 * SCALE:.1f}" font-size="13" fill="#b8700f">swap figure: the far track swings out</text>')
        pP, pN = parts[pn], parts[nn]
        svg.append(f'<text x="8" y="18" font-size="14" fill="#cc3597">{pn}: {pP["total"]} mm ({pP["segments"]} segments, {pP["vias"]} vias)</text>')
        svg.append(f'<text x="8" y="36" font-size="14" fill="#2d67d2">{nn}: {pN["total"]} mm ({pN["segments"]} segments, {pN["vias"]} vias)</text>')
        svg.append(f'<text x="8" y="54" font-size="13" fill="#1f2421">difference {pP["total"] - pN["total"]:+.2f} mm; limit {result[port]["limit"]} mm each (the mote); solid = Top, dashed = Internal 1</text>')
        svg.append("</svg>")
        (OUT / f"pair_{port}_legs.svg").write_text("\n".join(svg))
    json.dump(result, open(OUT / "pair_lengths.json", "w"), indent=1)
    for port, r in result.items():
        print(f"port {port}: " + "; ".join(f"{k} {v['total']} ({v['segments']} seg)" for k, v in r["parts"].items()))
        for cat in ("pins' exit (stub + start vias)", "swap figure", "runs and bends", "approach into the pad"):
            vals = [r["parts"][k][cat] for k in (r["P"], r["N"])]
            print(f"   {cat:34s} P {vals[0]:6.2f}  N {vals[1]:6.2f}  Δ {vals[0] - vals[1]:+.2f}")


if __name__ == "__main__":
    main()
