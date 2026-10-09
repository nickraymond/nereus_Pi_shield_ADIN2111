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
    "port1_pair": ((-3.5, 25.5, 10.5, 32.5), "ADIN", ["top", "in1", "bot"], "Port-1 data pair: U1 pins 27/28 (north edge of U1 at rot 90) to T1 pads 1/2 in the band; the mote's U1 and T1 sit elsewhere, so the mote view shows only the ADIN block's copper placed as here"),
    "port2_pair": ((-4.0, 34.0, 14.0, 41.5), "ADIN", ["top", "in1", "bot"], "Port-2 data pair: U1 pins 4/5 (south edge) through the pocket's south exit to T2 pads 1/2"),
    "spi_lane": ((-7.5, 27.0, 29.5, 38.5), None, ["in3", "in1", "top"], "The SPI lane: from Sofar's vias at U1's west side east on Internal 2 under U1 and across the band to J1 pins 19-24, routed first (session 2: 25 mm down the west edge past the inserts)"),
    "int_fanout": ((-8.5, 29.0, -2.5, 34.5), "ADIN", ["top", "bot"], "~{ADIN_INT} fan-out west of U1: U1.39 -> Sofar's own via (2.8 mm inside the edge now that U1 is 3 mm east: no hand via) -> R1.1"),
    "u2_u3_pocket_exit": ((-7.0, 36.0, 6.0, 42.0), "ADIN", ["top", "in3", "bot"], "The pocket's south exit: U2 / U3 (1.8 V and 3.3 V switches, bottom) with their fan-out vias, the port-2 pair above, 3V3 / 1V8 / ADIN_PWR leaving east; 3 mm taller than session 2"),
    "t1_cluster": ((2.5, 24.5, 12.0, 32.5), "P1T", ["top", "bot"], "T1 cluster (P1T block) and the bus legs to L1"),
    "t2_cluster": ((9.0, 30.0, 18.5, 38.0), "P2T", ["top", "bot"], "T2 cluster (P2T block) east of T1"),
    "north_band": ((4.5, -0.5, 24.5, 8.0), None, ["top", "bot", "in1"], "North band: the LEDs D10 / D8 / D9 on the edge, JP1 (5 V to the Pi) and JP2 (LED supply) on top beside them, FID3 / FID4; the LED resistors and FID1 / FID2 underneath"),
    "u11_payload": ((27.0, 49.0, 38.5, 62.0), None, ["top", "in3", "bot"], "Load switch U11 at the strip's south end: VBUS in (pre-stitched via), VBUS_OUT to J5 (0.6 mm), its signals to J1"),
    "pi5v_strip_north": ((23.5, 0.0, 38.5, 25.0), "B5V", ["top", "in1", "bot"], "5 V cell at the strip's north end and the 5 V path: L6 -> JP1 in the north band -> J1 pins 2/4 across J1's north end"),
    "insert_mp1": ((-10.5, 39.0, 12.0, 60.0), "P1L", ["top", "in1"], "Port-1 inductor L1 (3 mm south) with the insert rings MP1 / MP2 (1.5 mm nearer the wall, 2.5 mm south) and the bus feeds; the P1L block's copper"),
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
    "port1_pair": {"fixed": "Session 2.b: the pair's 45° runs are single segments (15 segments per leg, was 25) and the P leg keeps 0.11 mm under the mote's 9.5 (9.39 / 8.77; T1 0.2 mm north of session 2's relation). Two vias straight out of U1's pins, Internal 1, one swap, Top into T1's pads along the straight lane.",
                   "mote": "Sofar leaves the pins by vias 0.75 / 1.1 mm out and runs the port on Internal 1 too, but enters T1's pads from the body side with a via behind each pad; here the pads face U1 and the pair enters from the open side.",
                   "open": "0.11 mm of margin on P: a rerun is not byte-identical. The centre placement (OPTIONS addendum A3) would give the mote's own geometry but needs the body-side entry to route."},
    "port2_pair": {"fixed": "Leaves U1 pins 4/5 on Top through the pocket's south exit (3 mm taller than session 2), swaps once, gets its via pair beside T2's approach. 19.93 / 20.61 mm (mote 21.3; session 2 17.98 / 18.62: the exit is 1.25 mm further south now).",
                   "mote": "Sofar's port 2 is 21 mm of Internal 1 to a T2 on the far side of the processor.",
                   "open": "None at the bar; the margin is 0.7 mm."},
    "spi_lane": {"fixed": "Nick's rule for 2.b: the SPI (SCK, MOSI, MISO, ~CS) is routed FIRST on a reserved Internal 2 lane from Sofar's fan-out vias at U1's west side, east under U1 and across the band to J1 pins 19-24; Bottom is forbidden for it and Top serves only the pin escape. Session 2's 25 mm detour down the west edge past the inserts is gone: 34 / 35 / 40 / 41 mm of new track against 66.5 / 67.6.",
                 "mote": "No counterpart: the mote's SPI goes to its own processor on Internal 1.",
                 "open": "The lane crosses the port-1 bus legs (Internal 1) and the 3V3 / 1V8 corridors once each. Length matching is not required (LESSONS §5)."},
    "int_fanout": {"fixed": "Sofar's ~{ADIN_INT} fan-out whole and Sofar's own: with U1 3 mm further from the west edge (Nick, 2026-10-08) the mote's via lands 2.8 mm inside the board, so the ADIN region is the mote's full one again and the hand via of sessions 2 / 2.b is gone (the mechanism stays in m3_copy for a layout that needs it).",
                   "mote": "Identical copper.",
                   "open": "None."},
    "u2_u3_pocket_exit": {"fixed": "The exit is 3 mm taller (MP1 2.5 mm south, the pocket y 26.2 … 41.3) and U1 is 3 mm east of the insert column; U2 / U3's balls get their vias before the pairs (fan-out first) anywhere but the pairs' exit lanes and never in a solder pad (QE round 3 F1); 3V3, 1V8 and ADIN_PWR leave east on Internal 2 under the band.",
                          "mote": "Sofar has U2 / U3 beside the processor with room on three sides.",
                          "open": "U2.B2 (ADIN_PWR) and U3.A2 (3V3) still found no fan-out spot within 1.7 mm and were routed afterwards (connected)."},
    "t1_cluster": {"fixed": "T1 at (6.7, 29.45): session 2's relation to U1 but 0.2 mm north (the pair's margin), the group 3 mm east with U1. Rigid copy; C19 / R14 as their own rigid piece at the mote's spot relative to T1.",
                   "mote": "The T1 cluster is a rigid copy (pads, Sofar's tracks and vias to 0.001 mm); only the data-pad approach is new.",
                   "open": "Sofar's pads 6/7 are 0.24 mm apart (the bus class asks 0.35): 4 DRC items per transformer, in the exclusion table as on the mote."},
    "t2_cluster": {"fixed": "T2 at (13.7, 33.75), session 2's relation to U1; the P2T region ends at mote x 138.6 as session 2.",
                   "mote": "Everything in the cluster is the mote's copper; the dropped GND via's job is done by this board's own stitching vias.",
                   "open": "None."},
    "north_band": {"fixed": "Both cut jumpers on top at the north edge with nothing tall beside them (Nick): JP1 (5 V to the Pi) at the band's east end, JP2 (LED supply) behind the LEDs; FID3 / FID4 ≥ 3.35 mm from the edge (JLCPCB, DFM row 26). The 5 V path L6 → JP1 → J1 pins 2/4 crosses J1's north end on an inner layer.",
                   "mote": "No counterpart (the LEDs, the jumpers and the Pi are new on this board).",
                   "open": "The 5 V path is ≈ 33 mm of 1.0 mm track instead of session 2's 8 (OPTIONS addendum A4: ≈ 35 mV at 1 A)."},
    "u11_payload": {"fixed": "Unchanged from session 2 but for the frame: VBUS pre-stitched at U11 pin 1, VBUS_OUT (0.6 mm) on Internal 2 to J5 3 mm further south.",
                    "mote": "No mote counterpart (the load switch is new on this board).",
                    "open": "None."},
    "pi5v_strip_north": {"fixed": "JP1 left the strip's north end for the north band; the 5 V cell, the bottom 5V_PI pour and the Internal 2 patch are as session 2; the bottom GND island under C58 / TP38 is dropped by the fill now (island removal 'always', DFM row 24).",
                         "mote": "Sofar's 3V3 output sits on an In4 plane island with the same divider tap; here the same cell is copied twice.",
                         "open": "None."},
    "insert_mp1": {"fixed": "The inserts 1.5 mm nearer the wall (ring copper on the brief's 0.5 mm edge line), the port-1 pair 2.5 mm south with L1's envelope (3 mm); the 1.5 mm bus feeds start 3.31 mm from the insert centre (NPTH-to-track, DFM row 13); the planes keep 0.3 mm from holes (DFM row 12).",
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
