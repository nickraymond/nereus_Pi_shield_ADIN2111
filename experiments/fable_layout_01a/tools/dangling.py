#!/usr/bin/env python3
"""Dangling copper by KiCad's own definition (QE S7.b F1): run kicad-cli DRC, read the track_dangling / via_dangling
items, remove them, refill, repeat until DRC lists none (a chain goes one segment per round: DRC is the only judge). Runs once, after M4: copied
stubs clipped at a block's edge, Sofar's pour-stitching vias with no pour here, and the router's own tails. Items of a
net DRC still reports as unconnected are kept: they are the partial route of an open link, and the report lists them.
Every removed item is recorded in blocks.json "trimmed", so blockcheck accounts for copied items that were removed.
Copied items on a mote pad-to-pad path of their block (blocks.json "protected", written by m3_copy.py) are never
trimmed (QE round 1 F2): a dangling one means the path is cut on this board, and it is listed in "protected_dangling".

  $PY tools/dangling.py m4          # trims the board in place, appends to blocks.json "trimmed", prints a summary
"""
import json
import math
import re
import subprocess
import sys

import pcbnew

import geom
from geom import mm

K = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"


def drc_dangling(out):
    """(dangling violations, names of the nets with unconnected items)."""
    subprocess.run([K, "pcb", "drc", "--severity-all", "--format", "json", "-o", str(out), str(geom.BOARD)],
                   check=True, capture_output=True)
    d = json.load(open(out))
    open_nets = set()
    for u in d["unconnected_items"]:
        for it in u["items"]:
            m = re.search(r"\[(.*?)\]", it["description"])
            if m:
                open_nets.add(m.group(1))
    return [v for v in d["violations"] if v["type"] in ("track_dangling", "via_dangling")], open_nets


def junctions(board, t, same_net):
    """Parameters s in [0, 1] along track t where same-net copper touches it: a via centre or another track's end
    inside t's copper, t's own end inside another item's copper or a zone fill, a pad overlapping t (at the pad
    centre's projection). KiCad's connectivity is anchor-in-shape, which this mirrors."""
    a, b = geom.xy(t.GetStart()), geom.xy(t.GetEnd())
    L2 = (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2
    if L2 == 0:
        return []
    layer = t.GetLayer()
    hw = mm(t.GetWidth()) / 2 + 0.002
    shape = t.GetEffectiveShape(layer)

    def proj(p):
        s = ((p[0] - a[0]) * (b[0] - a[0]) + (p[1] - a[1]) * (b[1] - a[1])) / L2
        s = max(0.0, min(1.0, s))
        q = (a[0] + s * (b[0] - a[0]), a[1] + s * (b[1] - a[1]))
        return s, math.hypot(p[0] - q[0], p[1] - q[1])
    out = []
    ends = [(0.0, t.GetStart()), (1.0, t.GetEnd())]
    for o in same_net:
        if o is t or o.m_Uuid.AsString() == t.m_Uuid.AsString():
            continue
        if o.GetClass() == "PCB_VIA":
            s, d = proj(geom.xy(o.GetPosition()))
            if d <= hw:
                out.append(s)
            for s0, e in ends:
                if o.GetEffectiveShape(layer).Collide(e, 1):
                    out.append(s0)
        elif o.GetLayer() == layer:
            for q in (o.GetStart(), o.GetEnd()):
                s, d = proj(geom.xy(q))
                if d <= hw:
                    out.append(s)
            for s0, e in ends:
                if o.GetEffectiveShape(layer).Collide(e, 1):
                    out.append(s0)
    net = t.GetNetname()
    for f in board.GetFootprints():
        for pad in f.Pads():
            if pad.GetNetname() == net and (pad.IsOnLayer(layer) or pad.GetDrillSize().x > 0):
                if pad.GetEffectiveShape(layer).Collide(shape, 0):
                    out.append(proj(geom.xy(pad.GetPosition()))[0])
    for z in board.Zones():
        if not z.GetIsRuleArea() and z.GetNetname() == net and z.IsOnLayer(layer):
            fill = z.GetFilledPolysList(layer)
            for s0, e in ends:
                if fill.OutlineCount() and fill.Contains(e):
                    out.append(s0)
    return sorted(set(round(s, 4) for s in out))


def is_protected(t, protected, board):
    """The protected record this board item is a copy of (same net, kind, layer and geometry within 0.002 mm), else None."""
    net = t.GetNetname()
    cls = t.GetClass()
    if cls == "PCB_VIA":
        p = geom.xy(t.GetPosition())
        for r in protected:
            if r["kind"] == "via" and r["net"] == net and geom.dist(p, tuple(r["at"])) <= 0.002:
                return r
        return None
    if cls == "PCB_ARC":
        m = geom.xy(t.GetMid())
        for r in protected:
            if r["kind"] == "arc" and r["net"] == net and geom.dist(m, tuple(r["mid"])) <= 0.002:
                return r
        return None
    a, b = geom.xy(t.GetStart()), geom.xy(t.GetEnd())
    layer = board.GetLayerName(t.GetLayer())
    for r in protected:
        if r["kind"] == "track" and r["net"] == net and (layer is None or r["layer"] == layer):
            s0, e0 = tuple(r["start"]), tuple(r["end"])
            if (geom.dist(a, s0) <= 0.002 and geom.dist(b, e0) <= 0.002) or (geom.dist(a, e0) <= 0.002 and geom.dist(b, s0) <= 0.002):
                return r
    return None


def describe(t, board):
    if t.GetClass() == "PCB_VIA":
        p = geom.xy(t.GetPosition())
        return {"kind": "via", "net": t.GetNetname(), "at": [round(p[0], 3), round(p[1], 3)],
                "dia": mm(t.GetWidth(pcbnew.F_Cu)), "drill": mm(t.GetDrillValue())}
    s, e = geom.xy(t.GetStart()), geom.xy(t.GetEnd())
    return {"kind": "arc" if t.GetClass() == "PCB_ARC" else "track", "net": t.GetNetname(), "layer": board.GetLayerName(t.GetLayer()),
            "start": [round(s[0], 3), round(s[1], 3)], "end": [round(e[0], 3), round(e[1], 3)], "width": mm(t.GetWidth()),
            "length": round(mm(t.GetLength()), 3)}


ALL = "--all" in sys.argv       # pre-route trim (stage m3): nothing is routed yet, so the open-net rule would keep everything


def one_round(stage, rnd):
    """One DRC + removal pass. Runs in its own process: after board.Remove, a second LoadBoard in the same process
    hands back SWIG proxies whose methods no longer resolve (seen in 9.0.6)."""
    out = geom.OUT / stage
    out.mkdir(parents=True, exist_ok=True)
    data = json.load(open(geom.EXP / "blocks.json"))
    trimmed = data.setdefault("trimmed", [])
    viol, open_nets = drc_dangling(out / "drc_dangling.json")
    board = geom.load()
    by_uuid = {t.m_Uuid.AsString(): t for t in board.GetTracks()}
    protected = data.get("protected", [])
    prot_dangling = data.setdefault("protected_dangling", [])
    remove, seen, kept_open, kept_prot = [], set(), 0, 0
    for v in viol:
        for it in v["items"]:
            t = by_uuid.get(it["uuid"])
            if t is None or it["uuid"] in seen:
                continue
            seen.add(it["uuid"])
            if t.GetNetname() in open_nets and not ALL:
                kept_open += 1          # the partial route of an open link stays visible
                continue
            prot = is_protected(t, protected, board)
            if prot is not None:
                # a copied item on a mote pad-to-pad path is never trimmed (QE round 1 F2): if DRC calls it dangling, the
                # path was cut elsewhere (a region clip) and the loss is recorded for the report, loudly
                kept_prot += 1
                rec = describe(t, board)
                rec.update({"stage": stage, "round": rnd, "block": prot["block"]})
                if not any(r.get("uuid") == t.m_Uuid.AsString() for r in prot_dangling):
                    rec["uuid"] = t.m_Uuid.AsString()
                    prot_dangling.append(rec)
                    print(f"PROTECTED BUT DANGLING ({prot['block']}): {rec['net'].rsplit('/', 1)[-1]} {rec['kind']} at {rec.get('start', rec.get('at'))}: a mote pad-to-pad path is cut on this board")
                continue
            remove.append(t)
    # A dangling TRACK is shortened to the copper it still joins (a stub whose body carries a via or a pad connection
    # keeps that part, plus half its width); it is deleted only when nothing touches it. Vias and arcs are deleted.
    by_net = {}
    for t in board.GetTracks():
        by_net.setdefault(t.GetNetname(), []).append(t)
    shortened = 0
    kept = []
    already = {r.get("uuid") for r in trimmed if r.get("action") == "shortened"}
    for t in remove:
        if t.GetClass() != "PCB_TRACK" or t.m_Uuid.AsString() in already:
            continue          # shortened once and still dangling: delete it (DRC is the judge)
        js = junctions(board, t, by_net.get(t.GetNetname(), []))
        if not js:
            continue
        a, b = geom.xy(t.GetStart()), geom.xy(t.GetEnd())
        L = geom.dist(a, b)
        margin = (mm(t.GetWidth()) / 2) / L if L else 0
        s0, s1 = max(0.0, js[0] - margin), min(1.0, js[-1] + margin)
        if s1 - s0 <= 1e-6 or (s0 <= 1e-6 and s1 >= 1 - 1e-6):
            continue          # nothing to keep, or no change (DRC and this geometry disagree): delete it
        rec = describe(t, board)
        rec.update({"stage": stage, "round": rnd, "action": "shortened", "uuid": t.m_Uuid.AsString(), "kept": [[round(a[0] + s0 * (b[0] - a[0]), 3), round(a[1] + s0 * (b[1] - a[1]), 3)],
                                                                                   [round(a[0] + s1 * (b[0] - a[0]), 3), round(a[1] + s1 * (b[1] - a[1]), 3)]]})
        trimmed.append(rec)
        t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(a[0] + s0 * (b[0] - a[0])), pcbnew.FromMM(a[1] + s0 * (b[1] - a[1]))))
        t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(a[0] + s1 * (b[0] - a[0])), pcbnew.FromMM(a[1] + s1 * (b[1] - a[1]))))
        kept.append(t)
        shortened += 1
    kept_ids = {t.m_Uuid.AsString() for t in kept}
    remove = [t for t in remove if t.m_Uuid.AsString() not in kept_ids]
    kinds = {"track": 0, "via": 0, "arc": 0}
    for t in remove:
        rec = describe(t, board)
        rec["stage"] = stage
        rec["round"] = rnd
        rec["action"] = "removed"
        trimmed.append(rec)
        kinds[rec["kind"]] += 1
    for t in remove:
        board.Remove(t)
    if remove or shortened:
        pcbnew.ZONE_FILLER(board).Fill(board.Zones())
        geom.save(board)
        json.dump(data, open(geom.EXP / "blocks.json", "w"), indent=1)
        print(f"{stage} dangling round {rnd}: removed {len(remove)} {kinds}, shortened {shortened} (DRC listed {len(viol)} dangling items; {kept_open} kept on open nets {sorted(n.rsplit('/', 1)[-1] for n in open_nets)}; {kept_prot} kept as mote pad-to-pad copper)")
    else:
        if kept_prot:
            json.dump(data, open(geom.EXP / "blocks.json", "w"), indent=1)
        print(f"{stage} dangling: none left after {rnd - 1} round(s); DRC lists {len(viol)} dangling items, all on open nets {sorted(n.rsplit('/', 1)[-1] for n in open_nets)} or protected ({kept_prot})" if viol
              else f"{stage} dangling: none left after {rnd - 1} round(s); DRC lists 0 dangling items")
    return len(remove) + shortened


def main(stage):
    for rnd in range(1, 41):
        for attempt in (1, 2):
            r = subprocess.run([sys.executable, __file__, stage, "--round", str(rnd)] + (["--all"] if ALL else []), capture_output=True, text=True)
            if r.returncode == 0:
                break
            # a round's child process died (seen once: kicad-cli / pcbnew crashing on exit after the work was saved, exit 1
            # with no traceback); the board and blocks.json are written atomically per round, so one retry is safe
            sys.stderr.write(f"dangling round {rnd} attempt {attempt} exited {r.returncode}; stderr tail:\n" + r.stderr[-2000:] + "\n")
        for line in r.stdout.splitlines():
            if "dangling" in line:
                print(line)
        if r.returncode != 0:
            raise SystemExit(f"dangling round {rnd} failed twice (see the stderr above); the board holds rounds 1..{rnd - 1}; rerun the stage from its snapshot")
        if "dangling round" not in r.stdout:
            break
    pd = json.load(open(geom.EXP / "blocks.json")).get("protected_dangling", [])
    if pd:
        print(f"{stage} dangling: {len(pd)} copied item(s) on a mote pad-to-pad path are dangling on this board (kept, listed in blocks.json 'protected_dangling'): "
              + "; ".join(f"{r['block']} {r['net'].rsplit('/', 1)[-1]} {r['kind']} {r.get('start', r.get('at'))}" for r in pd[:12]))


if __name__ == "__main__":
    if "--round" in sys.argv:
        one_round(sys.argv[1], int(sys.argv[sys.argv.index("--round") + 1]))
    else:
        main(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "m4")
