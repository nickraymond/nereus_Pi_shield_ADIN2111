#!/usr/bin/env python3
"""Before / after data for tools/before_after.py (read only): for a board file, the footprint table (position, rotation,
side), the copper per layer (segments, mm, vias, zones) and the copper per net; the net diff between two such tables;
the whole-layer SVGs (tools/render_layers.py) and the review regions' crops (tools/review_views.REGIONS).

  $PY tools/ba_data.py snapshot BOARD.kicad_pcb out/before_after/before      # before.json + before/<layer>.svg + region crops
  $PY tools/ba_data.py snapshot board/nereus_Pi_shield_ADIN2111.kicad_pcb out/before_after/after
  $PY tools/ba_data.py diff out/before_after                                  # net_diff.json from before.json / after.json

The "before" board of session 2.b is session 2's final board (commit b22752f): `git show b22752f:experiments/fable_layout_01a/
board/nereus_Pi_shield_ADIN2111.kicad_pcb > /tmp/before.kicad_pcb`. The frames differ (46 × 65 vs 49 × 68): each SVG is
rendered in its own board's frame; the region crops use the review regions' rectangles in the board frame.
"""
import json
import subprocess
import sys
from pathlib import Path

import pcbnew

import geom
import review_views as rv

PY = "/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3"
mm = pcbnew.ToMM


def snapshot(board_path, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    b = pcbnew.LoadBoard(str(board_path))
    fps = {f.GetReference(): [round(mm(f.GetPosition().x), 3), round(mm(f.GetPosition().y), 3), round(f.GetOrientationDegrees(), 1), "B" if f.IsFlipped() else "F"]
           for f in b.GetFootprints()}
    copper, nets = {}, {}
    for t in b.GetTracks():
        n = t.GetNetname().rsplit("/", 1)[-1]
        e = nets.setdefault(n, {"mm": 0.0, "vias": 0, "layers": set()})
        if t.GetClass() == "PCB_VIA":
            copper["vias"] = copper.get("vias", 0) + 1
            e["vias"] += 1
        else:
            ln = b.GetLayerName(t.GetLayer())
            c = copper.setdefault(ln, {"segments": 0, "length_mm": 0.0})
            c["segments"] += 1
            c["length_mm"] = round(c["length_mm"] + mm(t.GetLength()), 1)
            e["mm"] = round(e["mm"] + mm(t.GetLength()), 1)
            e["layers"].add(ln)
    for n in nets:
        nets[n]["layers"] = sorted(nets[n]["layers"])
    bb = b.GetBoardEdgesBoundingBox()
    data = {"board": str(board_path), "size": [round(mm(bb.GetWidth()), 1), round(mm(bb.GetHeight()), 1)],
            "origin": [round(mm(bb.GetLeft()), 2), round(mm(bb.GetTop()), 2)],
            "footprints": fps, "copper": copper, "zones": sum(1 for z in b.Zones() if not z.GetIsRuleArea()), "nets": nets}
    json.dump(data, open(out.with_suffix(".json"), "w"), indent=1)
    subprocess.run([PY, str(geom.HERE / "render_layers.py"), str(board_path), str(out)], check=True, capture_output=True)
    # the region crops, in this board's frame (its own edge-bbox origin)
    ox, oy = data["origin"]
    for name, (rect, block, layers, cap) in rv.REGIONS.items():
        for layer in layers:
            svg = out / f"{layer}.svg"
            if svg.exists():
                (out.parent / f"{name}_{layer}_{out.name}.svg").write_text(rv.crop(svg.read_text(), rect, (ox, oy), title=f"{name} {layer} ({out.name})"))
    print(f"{out.name}: {len(fps)} footprints, {copper.get('vias', 0)} vias, {data['zones']} zones, {data['size']}")


def diff(out_dir):
    out = Path(out_dir)
    a, b = json.load(open(out / "before.json")), json.load(open(out / "after.json"))
    rows = []
    for n in sorted(set(a["nets"]) | set(b["nets"])):
        ea, eb = a["nets"].get(n, {"mm": 0, "vias": 0, "layers": []}), b["nets"].get(n, {"mm": 0, "vias": 0, "layers": []})
        if abs(ea["mm"] - eb["mm"]) >= 2.0 or ea["vias"] != eb["vias"]:
            rows.append([n, ea["mm"], eb["mm"], ea["vias"], eb["vias"], ", ".join(l.replace(" Layer", "").replace("6 Bottom", "Bottom") for l in ea["layers"]),
                         ", ".join(l.replace(" Layer", "").replace("6 Bottom", "Bottom") for l in eb["layers"])])
    json.dump(rows, open(out / "net_diff.json", "w"), indent=1)
    print(f"net diff: {len(rows)} nets changed by ≥ 2 mm or in via count")


if __name__ == "__main__":
    if sys.argv[1] == "snapshot":
        snapshot(sys.argv[2], sys.argv[3])
    else:
        diff(sys.argv[2])
