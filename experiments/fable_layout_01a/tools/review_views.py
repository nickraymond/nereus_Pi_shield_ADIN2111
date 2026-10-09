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


# the design review's text per region (session 2, for Nick): what is fixed, how it compares with the mote, what is open
NOTES = {
    "port1_pair": {"fixed": "QE round 1 F1: BM1_DATA_P no longer crosses T1 pad 2. The pair leaves U1 pins 27/28 by two vias straight out of the pins (1.0 / 1.48 mm, staggered because two 0.45 mm vias do not fit side by side at the 0.5 mm pin pitch), runs on Internal 1, swaps P and N once (the pin and pad order demand it) and comes back to Top, then enters T1 pads 1/2 along a straight lane, spreading from the 0.4 mm track pitch to the pads' 0.65 mm pitch before the pad edge. Lengths 9.46 / 8.80 mm (mote 9.5).",
                   "mote": "Sofar also leaves the pins by vias 0.75 / 1.1 mm out and runs the port on Internal 1, but routes P and N as two separate tracks and enters T1's pads from the transformer body side with a via 0.9 mm behind each pad. Here the pads face U1, so the pair enters from the open side.",
                   "open": "P is 0.04 mm under the mote's length: no slack left. The crystal Y1's bottom pad under the approach forbids a via pair at T1, which is why the port's layer change sits at the pins."},
    "port2_pair": {"fixed": "QE round 1 F1: BM2_DATA_N no longer crosses T2 pad 1. The pair leaves U1 pins 4/5 on Top, runs south then east through the pocket's exit along y 38, north-east across the band, swaps once, and gets its via pair beside T2's approach (0.65 mm apart, as the pads). Lengths 17.98 / 18.62 mm (mote 21.3; 01 had 21.3 / 23.4).",
                   "mote": "Sofar's port 2 is 21 mm of Internal 1 with vias at both ends; the mote's T2 sits on the far side of the processor. Here T2 is 11 mm from U1 and the pair is 3 mm shorter.",
                   "open": "The pocket's exit (U2's fan-out vias, the port-2 pair, the Internal 2 corridors for 3V3 / 1V8 / ADIN_PWR / ~{CS}) is the tightest place on the board: 0.15 mm P-N, 0.175 mm to the nearest other net."},
    "int_fanout": {"fixed": "QE round 1 F2: Sofar's ~{ADIN_INT} fan-out is whole again. The mote's via lands 0.08 mm inside the board edge (inside the 0.5 mm edge clearance); a hand via 0.44 mm further in joins both of Sofar's clipped lead-outs (edge 0.525 mm, 0.207 mm from other-net copper, proven by the copy script). U1.39 -> Top -> via -> Bottom -> R1.1, as the mote.",
                   "mote": "Identical copper but for the via's position (the mote view shows Sofar's via cut by our edge).",
                   "open": "None here. Every copied item that carries a pad-to-pad connection on the mote is now protected from the dangling trim (0 of them cut on this board). QE round 2 N1: three of Sofar's GND pad links lie outside the block regions (C29.2-C30.2 in the 3.3 V and 5 V cells, C21.2 in DAMP1) and are made by the GND pours instead of his tracks."},
    "u2_u3_pocket_exit": {"fixed": "The three open links of 293dc11 are closed: 1V8 and ADIN_PWR reach U2's balls, VBUS reaches U11 (not in this view). U2 / U3's power balls get their vias before anything else is routed (fan-out first), on the ball's own layer, in the exit's south-west corner so the pair's lane stays free.",
                          "mote": "Sofar has U2 / U3 beside the processor with room on three sides; here they sit in a 1.5 mm gap between U1 and the insert MP1's keep-out, which the pair and four corridors also cross.",
                          "open": "U2's ADIN_PWR ball found no fan-out spot in the corner and is routed afterwards (it is connected; the reservation failed). This exit is where any further change will bite."},
    "t1_cluster": {"fixed": "T1 stays at its M1 position (6.7, 28.4); the bus legs to L1 pads 6/7 at 0.2 mm keep 0.35 mm from everything.",
                   "mote": "The T1 cluster is a rigid copy (pads, Sofar's tracks and vias to 0.001 mm); only the data-pad approach is new.",
                   "open": "Sofar's pads 6/7 are 0.24 mm apart (the bus class asks 0.35): 4 DRC items per transformer, in the exclusion table as on the mote."},
    "t2_cluster": {"fixed": "The P2T copy region now ends at mote x 138.6: Sofar's GND pour-stitching via at mote (138.751, 116.854) belongs to the U5 cell's R23 on the mote and, after the 180 degree rotation, landed 0.4 mm in front of T2's data pads, where no pair could enter.",
                   "mote": "Everything else in the cluster is the mote's copper; the dropped via's job (stitching the bottom GND pour) is done by this board's own stitching vias.",
                   "open": "None."},
    "u11_payload": {"fixed": "VBUS at U11 pin 1 was open in 293dc11: the ball is now pre-stitched to the VBUS plane before U11's own signals take the row. VBUS_OUT (0.6 mm) to J5 and its 6 class-clearance items are gone (0 items).",
                    "mote": "No mote counterpart (the load switch is new on this board).",
                    "open": "None at M2; the DFM sweep (M3) has not looked at it yet."},
    "pi5v_strip_north": {"fixed": "The two 5V_PI pours were open in 293dc11 and a zone via dangled. The bottom pour reaches under the whole 5 V cell again and a 5V_PI patch on Internal 2 covers the same rectangle (as the mote carries the buck's output on a plane island); every bottom island cut by the dividers R37-R40 gets a via into the patch, and zone vias are only placed where the net has copper on another layer.",
                         "mote": "Sofar's 3V3 output sits on an In4 plane island with the same divider tap; here the same cell is copied twice (3.3 V and 5 V) and the 5 V copy gets the In3 patch because In4 is the VBUS / 3V3 plane.",
                         "open": "A bottom GND pour island under C58 / TP38 holds no via (none fits); it carries no pad and KiCad's island removal should drop it. To confirm in KiCad."},
    "insert_mp1": {"fixed": "Unchanged from session 1: the insert rings, Sofar's 7 vias per ring, the 1.5 mm bus feeds to L1, the P1L block.",
                   "mote": "Rigid copy of the inductor block; the feeds and the data legs are new (the mote's inserts are elsewhere).",
                   "open": "Sofar's 2.0 mm BM1_N stub at L1 pad 2 is 0.31 mm from Sofar's GND via (the bus rule asks 0.35): 1 DRC item, declared. The insert contact's 76 DRC items are the mote's (Sofar Q6)."},
}

LAYER_NAMES = {"top": "Top", "in1": "Internal 1", "in3": "Internal 2 (In3)", "bot": "Bottom"}


def write_page(out, index, head):
    css = """
    :root{--bg:#f6f6f3;--fg:#1f2421;--mut:#5f6a64;--line:#d7dbd6;--ok:#178a42;--warn:#b8700f;--card:#ffffff}
    @media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#15181a;--fg:#e6e8e4;--mut:#a6ada8;--line:#2d3331;--card:#1d2124}}
    :root[data-theme=dark]{--bg:#15181a;--fg:#e6e8e4;--mut:#a6ada8;--line:#2d3331;--card:#1d2124}
    body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,Helvetica,Arial,sans-serif}
    main{max-width:1200px;margin:0 auto;padding:24px 16px}
    h1{font-size:24px;margin:0 0 4px}h2{font-size:18px;margin:36px 0 6px;border-top:1px solid var(--line);padding-top:16px}
    p{margin:6px 0}.mut{color:var(--mut)}
    .pair{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:10px 0}
    @media(max-width:700px){.pair{grid-template-columns:1fr}}
    figure{margin:0;background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px}
    figure img{width:100%;height:auto;display:block;background:#fff;border-radius:4px}
    figcaption{font-size:13px;color:var(--mut);margin-top:6px}
    .note{border-left:3px solid var(--line);padding:2px 12px;margin:8px 0}.note.fixed{border-color:var(--ok)}.note.open{border-color:var(--warn)}
    table{border-collapse:collapse;font-size:14px;margin:8px 0}td,th{border:1px solid var(--line);padding:4px 10px;text-align:left}
    .legend span{display:inline-block;width:12px;height:12px;border-radius:3px;margin:0 4px 0 10px;vertical-align:middle}
    """
    h = [f"<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Layout 1.a design review</title><style>{css}</style></head><body><main>"]
    h.append(head)
    h.append("<p class='legend mut'>Colours: <span style='background:#cc3597'></span>data pairs <span style='background:#178a42'></span>bus <span style='background:#d2412f'></span>VBUS <span style='background:#2d67d2'></span>3V3 <span style='background:#8b4cc6'></span>rails <span style='background:#c9a000'></span>5 V to the Pi <span style='background:#2a302d'></span>signals / GND tracks <span style='background:#8b928e'></span>GND fills. Left: Sofar's mote, its copper placed as this board places the block. Right: this board. Same renderer, same region, same scale (grid 0.1 mm cells; the images are 40 px/mm).</p>")
    for row in index:
        n = NOTES.get(row["region"], {})
        x0, y0, x1, y1 = row["rect"]
        h.append(f"<h2>{row['region'].replace('_', ' ')} <span class='mut' style='font-weight:normal;font-size:13px'>x {x0}…{x1}, y {y0}…{y1} mm{(' · block ' + row['block']) if row['block'] else ' · no mote counterpart'}</span></h2>")
        h.append(f"<p>{row['caption']}</p>")
        if n.get("fixed"):
            h.append(f"<div class='note fixed'><b>Fixed / as built:</b> {n['fixed']}</div>")
        if n.get("mote"):
            h.append(f"<div class='note'><b>Versus the mote:</b> {n['mote']}</div>")
        if n.get("open"):
            h.append(f"<div class='note open'><b>Still open:</b> {n['open']}</div>")
        for v in row["views"]:
            lname = LAYER_NAMES.get(v["layer"], v["layer"])
            h.append("<div class='pair'>")
            if "mote" in v:
                h.append(f"<figure><img src='{v['mote']}' alt='mote {row['region']} {lname}'><figcaption>Sofar's mote, {lname} (block {row['block']} transform)</figcaption></figure>")
            else:
                h.append(f"<figure><figcaption>no mote counterpart on {lname}</figcaption></figure>")
            h.append(f"<figure><img src='{v['board']}' alt='board {row['region']} {lname}'><figcaption>This board, {lname}</figcaption></figure>")
            h.append("</div>")
    h.append("</main></body></html>")
    (out / "index.html").write_text("\n".join(h))


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
    head_path = geom.EXP / "review_head.html"
    head = head_path.read_text() if head_path.exists() else "<h1>Layout experiment 1.a: design review</h1>"
    write_page(out, index, head)
    print(f"page: {out / 'index.html'}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(geom.OUT / "review"))
