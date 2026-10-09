#!/usr/bin/env python3
"""Side-by-side region views: Sofar's mote vs this board, same region, same orientation, same renderer (read only).

  $PY tools/review_views.py OUT_DIR            (run from experiments/fable_layout_01a/; needs out/m4/layers/*.svg
                                                 from tools/render_layers.py and ../fable_layout_01/out/m5/mote_layers/)

For every region in REGIONS (a board rectangle in the brief's frame and the block whose transform maps the mote onto
it) and every listed copper layer, writes OUT_DIR/<region>_<layer>_board.svg (the board's layer SVG cropped to the
rectangle) and OUT_DIR/<region>_<layer>_mote.svg (the mote's layer SVG with the block's transform applied, cropped to
the same rectangle: what Sofar's copper looks like placed as this board places the block). Regions with no block
(new routing with no mote counterpart) get the board view only. The mote SVGs' origin is the mote's edge bounding box
(render_layers.py), so the transform is: translate(dst − board origin) rotate(−rot) translate(−(src − mote origin)).
"""
import json
import re
import sys
from pathlib import Path

import pcbnew

import geom

MOTE_SVGS = geom.EXP.parent / "fable_layout_01" / "out" / "m5" / "mote_layers"
BOARD_SVGS = geom.OUT / "m4" / "layers"
LAYERS = ["top", "in1", "in3", "bot"]
SCALE = 40          # px per mm

# name: (board rect x0, y0, x1, y1 in the brief's frame, block name or None, layers, caption)
REGIONS = {
    "port1_pair": ((-3.5, 25.0, 9.0, 32.0), "ADIN", ["top", "in1", "bot"], "Port-1 data pair: U1 pins 27/28 (north edge of U1) to T1 pads 1/2; the mote's U1 and T1 sit elsewhere, so the mote view shows only the ADIN block's copper placed as here"),
    "port2_pair": ((-4.0, 33.0, 14.0, 40.0), "ADIN", ["top", "in1", "bot"], "Port-2 data pair: U1 pins 4/5 (south edge) through the pocket's south exit to T2 pads 1/2"),
    "int_fanout": ((-7.5, 28.0, -3.0, 33.0), "ADIN", ["top", "bot"], "~{ADIN_INT} fan-out at the board's west edge: U1.39 → via → R1.1 (QE round 1 F2)"),
    "u2_u3_pocket_exit": ((-7.0, 35.0, 5.0, 40.0), "ADIN", ["top", "in3", "bot"], "The pocket's south exit: U2 / U3 (1.8 V and 3.3 V switches, bottom) with their fan-out vias, the port-2 pair above, 3V3 / 1V8 / ADIN_PWR leaving east"),
    "t1_cluster": ((2.5, 23.5, 11.5, 31.5), "P1T", ["top", "bot"], "T1 cluster (P1T block) and the bus legs to L1"),
    "t2_cluster": ((9.0, 29.0, 18.0, 36.5), "P2T", ["top", "bot"], "T2 cluster (P2T block): the region clip at mote x 138.6 dropped the GND via that sat in front of the data pads"),
    "u11_payload": ((27.0, 49.0, 38.5, 59.0), None, ["top", "in3", "bot"], "Load switch U11 at the strip's south end: VBUS in (pre-stitched via), VBUS_OUT to J5 (0.6 mm), its signals to J1"),
    "pi5v_strip_north": ((28.5, 6.0, 38.5, 25.0), "B5V", ["top", "bot"], "5 V cell under JP1 at the strip's north end: the bottom 5V_PI pour under the output caps and the divider tap"),
    "insert_mp1": ((-7.5, 38.0, 12.0, 56.0), "P1L", ["top", "in1"], "Port-1 inductor L1 with the insert rings MP1 / MP2 and the bus feeds; the P1L block's copper"),
}


def mote_origin():
    b = pcbnew.LoadBoard(str(geom.MOTE))
    bb = b.GetBoardEdgesBoundingBox()
    return pcbnew.ToMM(bb.GetX()), pcbnew.ToMM(bb.GetY())


def board_origin():
    return geom.OUTLINE["x0"], geom.OUTLINE["y0"]


def crop(svg_text, rect, origin, transform=None, title=""):
    """The SVG's content with a new viewBox over `rect` (board frame mm; `origin` = the SVG's own origin in that
    frame), optionally wrapped in a <g transform>. Scale SCALE px/mm."""
    x0, y0, x1, y1 = rect
    w, h = x1 - x0, y1 - y0
    body = re.sub(r"^<svg[^>]*>", "", svg_text.strip(), count=1)
    body = re.sub(r"</svg>\s*$", "", body)
    body = re.sub(r'^<rect [^>]*fill="#ffffff"/>', "", body, count=1)
    if transform:
        body = f'<g transform="{transform}">{body}</g>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0 - origin[0]:.3f} {y0 - origin[1]:.3f} {w:.3f} {h:.3f}" '
            f'width="{w * SCALE:.0f}" height="{h * SCALE:.0f}">'
            f'<rect x="{x0 - origin[0]:.3f}" y="{y0 - origin[1]:.3f}" width="{w:.3f}" height="{h:.3f}" fill="#ffffff"/>'
            f'<title>{title}</title>{body}</svg>')


def main(out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    blocks = {b["name"]: b for b in json.load(open(geom.EXP / "blocks.json"))["blocks"]}
    mx0, my0 = mote_origin()
    bx0, by0 = board_origin()
    index = []
    for name, (rect, block, layers, caption) in REGIONS.items():
        row = {"region": name, "rect": rect, "block": block, "caption": caption, "views": []}
        for layer in layers:
            bsvg = BOARD_SVGS / f"{layer}.svg"
            if not bsvg.exists():
                raise SystemExit(f"{bsvg} missing: run tools/render_layers.py board/...kicad_pcb out/m4/layers first")
            bo = out / f"{name}_{layer}_board.svg"
            bo.write_text(crop(bsvg.read_text(), rect, (bx0, by0), title=f"{name} {layer} (this board)"))
            view = {"layer": layer, "board": bo.name}
            if block:
                blk = blocks[block]
                src, dst, rot = blk["src"], blk["dst"], blk.get("rot", 0)
                tr = (f"translate({dst[0] - bx0:.4f},{dst[1] - by0:.4f}) rotate({-rot:.1f}) "
                      f"translate({-(src[0] - mx0):.4f},{-(src[1] - my0):.4f})")
                # the board SVG's own origin is (bx0, by0): the crop's viewBox is in board-origin coordinates, so the
                # transformed mote content must land in that same frame
                msvg = MOTE_SVGS / f"{layer}.svg"
                mo = out / f"{name}_{layer}_mote.svg"
                mo.write_text(crop(msvg.read_text(), rect, (bx0, by0), transform=tr, title=f"{name} {layer} (Sofar's mote, {block} transform)"))
                view["mote"] = mo.name
            row["views"].append(view)
        index.append(row)
        print(f"{name}: {len(layers)} layer(s){' + mote' if block else ''}")
    json.dump(index, open(out / "index.json", "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(geom.OUT / "review"))
