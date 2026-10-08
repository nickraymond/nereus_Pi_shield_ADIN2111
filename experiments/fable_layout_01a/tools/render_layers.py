#!/usr/bin/env python3
"""Render each copper layer of a KiCad board as a net-coloured SVG (read only; the board is never saved).

Runs on KiCad 9's bundled Python (it needs the pcbnew module):
  PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
  $PY render_layers.py BOARD.kicad_pcb OUT_DIR

Writes OUT_DIR/<layer>.svg for every copper layer (top, in1 … bot), drawn looking down from the top: filled zones,
tracks (arcs included), pads, vias and holes, coloured by net group. Used for the mote "before" and the shield
"after" views in this experiment, so both sides of a comparison come from the same code.
"""
import re
import sys
from pathlib import Path

import pcbnew

COLOURS = {"gnd": "#8b928e", "vbus": "#d2412f", "pin": "#de8519", "3v3": "#2d67d2", "rail": "#8b4cc6",
           "bus": "#178a42", "data": "#cc3597", "pi5v": "#c9a000", "sig": "#2a302d", "none": "#b5bbb7"}


def group(net):
    net = net.rsplit("/", 1)[-1]          # schematic nets are hierarchical (/Top-Level Schematic/PoDL/.../P_IN)
    if net == "GND":
        return "gnd"
    if net in ("VBUS", "VBUS_OUT"):
        return "vbus"
    if net == "P_IN":
        return "pin"
    if net == "3V3":
        return "3v3"
    if net in ("5V_PI", "PI_5V"):
        return "pi5v"
    if net in ("1V8", "ADIN_AVDD", "ADIN_VDDIO", "DVDD1_1P1", "DVDD2_1P1", "VDD11"):
        return "rail"
    if re.match(r"BM[12]_[PN]$", net):
        return "bus"
    if "DATA" in net:
        return "data"
    return "sig" if net else "none"


def main(board_path, out_dir):
    board = pcbnew.LoadBoard(str(board_path))
    mm = pcbnew.ToMM
    bb = board.GetBoardEdgesBoundingBox()
    x0, y0, w, h = mm(bb.GetX()), mm(bb.GetY()), mm(bb.GetWidth()), mm(bb.GetHeight())
    if w <= 0 or h <= 0:
        raise SystemExit(f"{board_path}: no board outline on Edge.Cuts; draw the outline first")

    def p(v):
        return f"{mm(v.x) - x0:.3f},{mm(v.y) - y0:.3f}"

    def path(ps):
        out = []
        for i in range(ps.OutlineCount()):
            for ch in [ps.Outline(i)] + [ps.Hole(i, k) for k in range(ps.HoleCount(i))]:
                pts = [ch.CPoint(j) for j in range(ch.PointCount())]
                if pts:
                    out.append("M" + " L".join(p(q) for q in pts) + "Z")
        return " ".join(out)

    outline = pcbnew.SHAPE_POLY_SET()
    board.GetBoardPolygonOutlines(outline)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    names = {pcbnew.F_Cu: "top", pcbnew.B_Cu: "bot"}
    copper = [l for l in board.GetEnabledLayers().CuStack()]
    for n, lid in enumerate(copper):
        name = names.get(lid, f"in{n}")
        s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-0.5 -0.5 {w + 1:.2f} {h + 1:.2f}" width="{(w + 1) * 20:.0f}" '
             f'height="{(h + 1) * 20:.0f}"><rect x="-0.5" y="-0.5" width="{w + 1:.2f}" height="{h + 1:.2f}" fill="#ffffff"/>'
             f'<path d="{path(outline)}" fill="#e4e8e1" stroke="#7d8781" stroke-width="0.12"/>']
        for z in board.Zones():
            if z.GetIsRuleArea() or not z.IsOnLayer(lid):
                continue
            s.append(f'<path d="{path(z.GetFilledPolysList(lid))}" fill="{COLOURS[group(z.GetNetname())]}" '
                     f'fill-opacity="0.55" fill-rule="evenodd"><title>{z.GetNetname() or "no net"}</title></path>')
        for t in board.GetTracks():
            if t.GetClass() == "PCB_VIA" or t.GetLayer() != lid:
                continue
            c = COLOURS[group(t.GetNetname())]
            if t.GetClass() == "PCB_ARC":
                ang, r = t.GetAngle().AsDegrees(), mm(t.GetRadius())
                s.append(f'<path d="M{p(t.GetStart())} A{r:.3f},{r:.3f} 0 {1 if abs(ang) > 180 else 0},{1 if ang > 0 else 0} '
                         f'{p(t.GetEnd())}" stroke="{c}" stroke-width="{mm(t.GetWidth()):.3f}" fill="none" stroke-linecap="round"/>')
            else:
                s.append(f'<path d="M{p(t.GetStart())} L{p(t.GetEnd())}" stroke="{c}" stroke-width="{mm(t.GetWidth()):.3f}" '
                         f'stroke-linecap="round"/>')
        for f in board.GetFootprints():
            for pad in f.Pads():
                if not pad.IsOnLayer(lid) or (lid not in (pcbnew.F_Cu, pcbnew.B_Cu) and not pad.FlashLayer(lid)):
                    continue
                s.append(f'<path d="{path(pad.GetEffectivePolygon(lid, pcbnew.ERROR_INSIDE))}" '
                         f'fill="{COLOURS[group(pad.GetNetname())]}"/>')
        for t in board.GetTracks():
            if t.GetClass() == "PCB_VIA":
                c = t.GetPosition()
                s.append(f'<circle cx="{mm(c.x) - x0:.3f}" cy="{mm(c.y) - y0:.3f}" r="{mm(t.GetWidth(lid)) / 2:.3f}" '
                         f'fill="{COLOURS[group(t.GetNetname())]}"/>')
        for f in board.GetFootprints():
            for pad in f.Pads():
                if pad.GetDrillSize().x > 0:
                    c = pad.GetPosition()
                    s.append(f'<circle cx="{mm(c.x) - x0:.3f}" cy="{mm(c.y) - y0:.3f}" r="{mm(pad.GetDrillSize().x) / 2:.3f}" fill="#ffffff"/>')
        s.append("</svg>")
        (out_dir / f"{name}.svg").write_text("\n".join(s))
        print(f"{name}: {board.GetLayerName(lid)} -> {out_dir / (name + '.svg')}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2])
