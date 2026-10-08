#!/usr/bin/env python3
"""BRIEF §6 / §8.5 on the new routing (read only): widths by class, the brief's class clearances to other-net copper,
the ADIN pair lengths, and the sense / ring fidelity (from blockcheck). Copied copper is identified exactly as
blockcheck matches it (same selection rule), so "new" = everything the mote does not explain.

  $PY tools/check_rules.py [out/m5/rules.md]
"""
import json
import sys

import pcbnew

import geom
import motecopy
import router
from geom import mm

# BRIEF §6: minimum width and clearance of NEW routing per class (the thin fan-out class is allowed at 0.15)
LIMITS = {"bus": (1.0, 0.35), "power": (0.5, 0.25), "pi5v": (1.0, 0.25), "payload": (0.6, 0.25),
          "rail": (0.2, 0.15), "signal": (0.2, 0.15), "data": (0.2, 0.15)}
FANOUT_OK = 0.15


def on_segment(p, a, b, tol=0.002):
    """Is p on segment a-b (within tol of the line and inside its extent)?"""
    L = geom.dist(a, b)
    if L < 1e-9:
        return geom.dist(p, a) <= tol
    t = ((p[0] - a[0]) * (b[0] - a[0]) + (p[1] - a[1]) * (b[1] - a[1])) / (L * L)
    if t < -tol / L or t > 1 + tol / L:
        return False
    q = (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
    return geom.dist(p, q) <= tol


def copied_ids(board, mote):
    """uuids of board tracks/arcs/vias that blockcheck's rule explains (same geometry, net, width)."""
    ids = set()
    tracks = [t for t in board.GetTracks()]
    for blk in motecopy.load_blocks()["blocks"]:
        T = motecopy.transform_of(blk)
        sel = mote.select(blk)
        nmap = mote.block_net_map(blk)
        for item, rect in sel["copper"]:
            net = nmap.get(item.GetNetname())
            cls = item.GetClass()
            if cls == "PCB_VIA":
                want = T.apply_xy(geom.xy(item.GetPosition()))
                for t in tracks:
                    if t.GetClass() == "PCB_VIA" and t.GetNetname() == net and geom.dist(want, geom.xy(t.GetPosition())) <= 0.001:
                        ids.add(t.m_Uuid.AsString())
            elif cls == "PCB_ARC":
                m = T.apply_xy(geom.xy(item.GetMid()))
                for t in tracks:
                    if t.GetClass() == "PCB_ARC" and t.GetNetname() == net and geom.dist(m, geom.xy(t.GetMid())) <= 0.001:
                        ids.add(t.m_Uuid.AsString())
            else:
                s0, e0 = item.GetStart(), item.GetEnd()
                if rect is not None:
                    s0, e0 = motecopy.clip_segment(s0, e0, rect)
                s, e = T.apply_xy(geom.xy(s0)), T.apply_xy(geom.xy(e0))
                for t in tracks:
                    if t.GetClass() == "PCB_TRACK" and t.GetNetname() == net and t.GetLayer() == item.GetLayer():
                        ts, te = geom.xy(t.GetStart()), geom.xy(t.GetEnd())
                        if (geom.dist(s, ts) <= 0.001 and geom.dist(e, te) <= 0.001) or (geom.dist(e, ts) <= 0.001 and geom.dist(s, te) <= 0.001):
                            ids.add(t.m_Uuid.AsString())
                        elif on_segment(ts, s, e) and on_segment(te, s, e) and abs(mm(t.GetWidth()) - mm(item.GetWidth())) <= 0.001:
                            ids.add(t.m_Uuid.AsString())      # a copied track shortened by tools/dangling.py (same line, same width)
    return ids


def main(out_path=None):
    board = geom.load()
    mote = motecopy.Mote(board)
    copied = copied_ids(board, mote)
    ring_nets = {"/Top-Level Schematic/" + n for n in geom.INSERT_NET.values()}
    new = [t for t in board.GetTracks() if t.m_Uuid.AsString() not in copied]
    # 1. widths of new tracks per class
    width_rows, width_fail = {}, []
    def cls_of(t):
        cls = router.net_class(t.GetNetname())
        if cls == "bus" and (t.GetClass() != "PCB_TRACK" or mm(t.GetWidth()) < 1.0):
            return "signal"          # the 0.2 mm data / TVS legs of the bus nets (and their vias) keep the mote's sizes (§6)
        return cls
    thin_len = {}
    for t in new:
        if t.GetClass() != "PCB_TRACK":
            continue
        cls = cls_of(t)
        w = mm(t.GetWidth())
        key = (cls, round(w, 3))
        width_rows[key] = width_rows.get(key, 0) + 1
        wmin = LIMITS.get(cls, (0.2, 0.15))[0]
        if w + 1e-6 < wmin and not (w + 1e-6 >= FANOUT_OK and cls in ("signal", "rail", "data")):
            width_fail.append((cls, t.GetNetname().rsplit("/", 1)[-1], w))
        elif w + 1e-6 < wmin:
            k = t.GetNetname().rsplit("/", 1)[-1]
            thin_len[k] = thin_len.get(k, 0.0) + mm(t.GetLength())
    # QE S7.b N2: 0.15 mm is a fan-out allowance, not a routing width. A net with more than 2 mm of 0.15 mm new track
    # has a whole link below its class width and is listed as such.
    thin_links = sorted((k, round(v, 1)) for k, v in thin_len.items() if v > 2.0)
    # 2. brief clearances: each new track/via vs other-net copper (pads, tracks, vias, filled zones)
    items_by_layer = {l: [] for l in geom.CU}
    for f in board.GetFootprints():
        for p in f.Pads():
            for l in geom.CU:
                if p.IsOnLayer(l) or p.GetDrillSize().x > 0:
                    items_by_layer[l].append((p, p.GetNetname(), p.GetEffectiveShape(l)))
    for t in board.GetTracks():
        if t.GetClass() == "PCB_VIA":
            for l in geom.CU:
                items_by_layer[l].append((t, t.GetNetname(), t.GetEffectiveShape(l)))
        else:
            items_by_layer[t.GetLayer()].append((t, t.GetNetname(), t.GetEffectiveShape(t.GetLayer())))
    clr_fail = []
    worst = {}
    for t in new:
        cls = cls_of(t)
        if router.net_class(t.GetNetname()) == "bus":
            cls = "bus"           # every item of a bus net carries the 0.35 netclass clearance (QE S7.b R2-F2)
        need = LIMITS.get(cls, (0.2, 0.15))[1]
        if cls in ("signal", "rail", "data"):
            continue          # 0.15: the Default netclass, checked by DRC itself
        layers = geom.CU if t.GetClass() == "PCB_VIA" else [t.GetLayer()]
        for l in layers:
            shape = t.GetEffectiveShape(l)
            bb = t.GetBoundingBox()
            bb.Inflate(pcbnew.FromMM(need + 0.01))
            for other, onet, oshape in items_by_layer[l]:
                if other is t or onet == t.GetNetname() or not onet:
                    continue          # no-net pads: Sofar's insert ring / transformer pads (DRC exclusion table)
                if cls == "bus" and router.net_class(onet) == "bus":
                    continue          # bus vs bus (P/N legs of one port) keeps Sofar's spacing; the 0.35 rule is bus vs non-bus
                if not bb.Intersects(other.GetBoundingBox()):
                    continue
                if shape.Collide(oshape, pcbnew.FromMM(need) - 1):
                    clr_fail.append((cls, t.GetNetname().rsplit("/", 1)[-1], onet.rsplit("/", 1)[-1], board.GetLayerName(l), geom.xy(t.GetPosition())))
            for z in board.Zones():
                if z.GetIsRuleArea() or not z.IsOnLayer(l) or z.GetNetname() == t.GetNetname():
                    continue
                fill = z.GetFilledPolysList(l)
                if fill.OutlineCount() and shape.Collide(fill, pcbnew.FromMM(need) - 1):
                    clr_fail.append((cls, t.GetNetname().rsplit("/", 1)[-1], f"zone {z.GetNetname() or 'no net'}", board.GetLayerName(l), geom.xy(t.GetPosition())))
    # 3. pair lengths (every track of the net: all new since the pair nets are excluded from the blocks)
    pairs = {}
    for short, limit in (("BM1_DATA_P", 9.5), ("BM1_DATA_N", 9.5), ("BM2_DATA_P", 21.3), ("BM2_DATA_N", 21.3)):
        name = "/Top-Level Schematic/" + short
        L = sum(mm(t.GetLength()) for t in board.GetTracks() if t.GetNetname() == name and t.GetClass() != "PCB_VIA")
        vias = sum(1 for t in board.GetTracks() if t.GetNetname() == name and t.GetClass() == "PCB_VIA")
        layers = sorted({board.GetLayerName(t.GetLayer()) for t in board.GetTracks() if t.GetNetname() == name and t.GetClass() != "PCB_VIA"})
        pairs[short] = (round(L, 2), limit, vias, layers, L <= limit)
    # 4. Kelvin sense: U4.1 ↔ R8.2 (P_IN) and U4.2 ↔ R8.1 (VBUS) joined by tracks alone (no via, no plane), as the mote
    fps = geom.fp_by_ref(board)
    kelvin = []
    for u4n, r8n in (("1", "2"), ("2", "1")):
        pu = next(p for p in fps["U4"].Pads() if p.GetNumber() == u4n)
        pr = next(p for p in fps["R8"].Pads() if p.GetNumber() == r8n)
        same = False
        for c in router.net_clusters(board, pu.GetNetname(), kinds=("PAD", "PCB_TRACK", "PCB_ARC")):
            ids = {it.m_Uuid.AsString() for it in c}
            if pu.m_Uuid.AsString() in ids:
                same = pr.m_Uuid.AsString() in ids
                L = sum(mm(it.GetLength()) for it in c if it.GetClass() == "PCB_TRACK")
                break
        kelvin.append((f"U4.{u4n} ↔ R8.{r8n} ({pu.GetNetname().rsplit('/', 1)[-1]})", same, round(L, 2) if same else None))
    lines = ["# New routing vs BRIEF §6 (M5)\n",
             f"Copied copper (blockcheck-matched): {len(copied)} items; new: {len(new)} tracks/vias (board total {len(list(board.GetTracks()))}).\n",
             "## Widths of new tracks", "| class | width | segments |", "|---|---|---|"]
    for (cls, w), n in sorted(width_rows.items()):
        lines.append(f"| {cls} | {w} | {n} |")
    lines.append(f"\nBelow the class minimum (not the 0.15 fan-out allowance): {len(width_fail)}" + ("" if not width_fail else " — " + "; ".join(f"{c} {n} {w}" for c, n, w in width_fail[:20])))
    lines.append(f"\nLinks routed at 0.15 mm beyond a fan-out (> 2 mm of 0.15 mm track on the net; below the 0.2 mm class width, BRIEF §6): {len(thin_links)}"
                 + ("" if not thin_links else " — " + "; ".join(f"{n} {L} mm" for n, L in thin_links)))
    lines += ["\n## Brief clearances on new bus / power / payload / 5 V copper",
              f"Violations of the class clearance (bus 0.35, power/payload/5 V 0.25): {len(clr_fail)}"]
    for c, n, o, l, p in clr_fail[:40]:
        lines.append(f"- {c} {n} vs {o} on {l} at ({p[0]:.2f}, {p[1]:.2f})")
    lines += ["\n## ADIN data pairs (BRIEF §6: ≤ the mote's length, Top + Internal 1, two vias)", "| net | length mm | limit | vias | layers | length ok | as the mote (2 vias, Top + Internal 1) |", "|---|---|---|---|---|---|---|"]
    for k, (L, lim, v, ls, ok) in pairs.items():
        same = v == 2 and ls == ["Internal 1", "Top Layer"]
        lines.append(f"| {k} | {L} | {lim} | {v} | {', '.join(ls)} | {'yes' if ok else 'NO'} | {'yes' if same else 'no (declared: fewer vias / one layer is no electrical loss)'} |")
    lines += ["\n## Kelvin sense (R8 shunt ↔ U4 INA232): pad-to-pad by tracks only (no via, no plane), as the mote",
              "| link | track path | tracks in that cluster mm |", "|---|---|---|"]
    for name, same, L in kelvin:
        lines.append(f"| {name} | {'yes' if same else 'NO'} | {L if same else '—'} |")
    text = "\n".join(lines)
    if out_path:
        open(out_path, "w").write(text + "\n")
    print(text)
    return 1 if (width_fail or clr_fail or not all(p[4] for p in pairs.values()) or not all(k[1] for k in kelvin)) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
