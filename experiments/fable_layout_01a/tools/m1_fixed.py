#!/usr/bin/env python3
"""M1: outline, J1, holes, inserts with Sofar's ring copper, J5, inductor envelopes (BRIEF §2–§3).

  $PY tools/m1_fixed.py            # applied to the M0 board by tools/build_all.sh (run the pipeline, not this alone)
"""
import json
import math

import pcbnew

import geom
import motecopy
from geom import MM, V, mm, deg

# JLCPCB JLC06161H-3313 (https://jlcpcb.com/impedance, read 2026-10-08; DFM.md row 21): outer 1 oz, inner 0.5 oz
# ("H/H without copper" cores of 0.55 mm), 3313 prepregs outside, one 2116 in the middle; εr 3313 4.1, 2116 4.16, core 4.6.
# Sum of the copper and dielectrics 1.538 mm; JLC's nominal finished thickness 1.6 mm (±10 %).
STACKUP = """		(stackup
			(layer "F.SilkS" (type "Top Silk Screen"))
			(layer "F.Paste" (type "Top Solder Paste"))
			(layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))
			(layer "F.Cu" (type "copper") (thickness 0.035))
			(layer "dielectric 1" (type "prepreg") (thickness 0.0994) (material "3313 prepreg (JLC06161H-3313)") (epsilon_r 4.1) (loss_tangent 0.02))
			(layer "In1.Cu" (type "copper") (thickness 0.0152))
			(layer "dielectric 2" (type "core") (thickness 0.55) (material "FR4 core 0.55 H/H") (epsilon_r 4.6) (loss_tangent 0.02))
			(layer "In2.Cu" (type "copper") (thickness 0.0152))
			(layer "dielectric 3" (type "prepreg") (thickness 0.1088) (material "2116 prepreg (JLC06161H-3313)") (epsilon_r 4.16) (loss_tangent 0.02))
			(layer "In3.Cu" (type "copper") (thickness 0.0152))
			(layer "dielectric 4" (type "core") (thickness 0.55) (material "FR4 core 0.55 H/H") (epsilon_r 4.6) (loss_tangent 0.02))
			(layer "In4.Cu" (type "copper") (thickness 0.0152))
			(layer "dielectric 5" (type "prepreg") (thickness 0.0994) (material "3313 prepreg (JLC06161H-3313)") (epsilon_r 4.1) (loss_tangent 0.02))
			(layer "B.Cu" (type "copper") (thickness 0.035))
			(layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))
			(layer "B.Paste" (type "Bottom Solder Paste"))
			(layer "B.SilkS" (type "Bottom Silk Screen"))
			(copper_finish "None")
			(dielectric_constraints no)
		)
"""


def shape(board, kind, layer, width=0.1):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(kind)
    s.SetLayer(layer)
    s.SetWidth(MM(width))
    return s


def add_line(board, a, b, layer=pcbnew.Edge_Cuts, width=0.1):
    s = shape(board, pcbnew.SHAPE_T_SEGMENT, layer, width)
    s.SetStart(V(*a))
    s.SetEnd(V(*b))
    board.Add(s)


def add_arc(board, centre, r, a0, a1, layer=pcbnew.Edge_Cuts, width=0.1):
    """Arc from angle a0 to a1 (degrees, y-down maths: 0 = east, 90 = south), the short way through the midpoint."""
    def pt(a):
        return (centre[0] + r * math.cos(math.radians(a)), centre[1] + r * math.sin(math.radians(a)))
    s = shape(board, pcbnew.SHAPE_T_ARC, layer, width)
    s.SetArcGeometry(V(*pt(a0)), V(*pt((a0 + a1) / 2)), V(*pt(a1)))
    board.Add(s)


def add_rect(board, r, layer, width=0.1):
    s = shape(board, pcbnew.SHAPE_T_RECT, layer, width)
    s.SetStart(V(r[0], r[1]))
    s.SetEnd(V(r[2], r[3]))
    board.Add(s)


def add_text(board, text, pos, layer, size=1.0):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetPosition(V(*pos))
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size)))
    t.SetTextThickness(MM(0.15))
    board.Add(t)


def draw_outline(board):
    o = geom.OUTLINE
    x0, x1, y0, y1, r = o["x0"], o["x1"], o["y0"], o["y1"], o["r"]
    add_line(board, (x0 + r, y0), (x1 - r, y0))
    add_line(board, (x1, y0 + r), (x1, y1 - r))
    add_line(board, (x1 - r, y1), (x0 + r, y1))
    add_line(board, (x0, y1 - r), (x0, y0 + r))
    add_arc(board, (x1 - r, y0 + r), r, -90, 0)
    add_arc(board, (x1 - r, y1 - r), r, 0, 90)
    add_arc(board, (x0 + r, y1 - r), r, 90, 180)
    add_arc(board, (x0 + r, y0 + r), r, 180, 270)


def inside_outline(p, margin=0.0):
    o = geom.OUTLINE
    x0, x1, y0, y1, r = o["x0"] + margin, o["x1"] - margin, o["y0"] + margin, o["y1"] - margin, o["r"]
    x, y = p
    if not (x0 <= x <= x1 and y0 <= y <= y1):
        return False
    for cx, cy in ((x0 + r, y0 + r), (x1 - r, y0 + r), (x0 + r, y1 - r), (x1 - r, y1 - r)):
        if (x < cx) == (cx == x0 + r) and (y < cy) == (cy == y0 + r):   # in the corner square
            if math.hypot(x - cx, y - cy) > r:
                return False
    return True


def clip_silk_circle(fp):
    """Replace the footprint's F.Silkscreen circle by the arcs of it that lie inside the outline (BRIEF §3)."""
    for g in list(fp.GraphicalItems()):
        if g.GetClass() == "PCB_SHAPE" and g.GetLayer() == pcbnew.F_SilkS and g.GetShape() == pcbnew.SHAPE_T_CIRCLE:
            c, r, w = geom.xy(g.GetStart()), mm(g.GetRadius()), mm(g.GetWidth())
            ok = [inside_outline((c[0] + r * math.cos(math.radians(a)), c[1] + r * math.sin(math.radians(a))), 0.3)
                  for a in range(360)]
            if all(ok):
                continue
            fp.Remove(g)
            # runs of allowed angles -> arcs
            start = next((i for i in range(360) if ok[i] and not ok[i - 1]), None)
            if start is None:
                continue
            a = start
            runs = []
            for _ in range(360):
                if ok[a % 360]:
                    b = a
                    while ok[(b + 1) % 360]:
                        b += 1
                    runs.append((a, b))
                    a = b + 1
                else:
                    a += 1
                if a >= start + 360:
                    break
            for a0, a1 in runs:
                if a1 - a0 < 5:
                    continue
                s = pcbnew.PCB_SHAPE(fp)
                s.SetShape(pcbnew.SHAPE_T_ARC)
                s.SetLayer(pcbnew.F_SilkS)
                s.SetWidth(MM(w))

                def pt(ang):
                    return V(c[0] + r * math.cos(math.radians(ang)), c[1] + r * math.sin(math.radians(ang)))
                s.SetArcGeometry(pt(a0), pt((a0 + a1) / 2), pt(a1))
                fp.Add(s)


def place_fixed(board, mote):
    fps = geom.fp_by_ref(board)
    # J1: socket body on the bottom, pin 1 at (25.23, 8.37) seen from the top, pin 2 east, pins advancing south.
    j1 = fps["J1"]
    if not j1.IsFlipped():
        j1.Flip(j1.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    j1.SetPosition(V(*geom.J1_PIN1))
    j1.SetOrientationDegrees(180)
    for ref, p in {**geom.PI_HOLES, **geom.HOUSING_HOLES}.items():
        fps[ref].SetPosition(V(*p))
        fps[ref].SetOrientationDegrees(0)
        clip_silk_circle(fps[ref])
    j5 = fps["J5"]
    j5.SetPosition(V(*geom.J5_POS))
    j5.SetOrientationDegrees(geom.J5_ROT)
    # inductors centred in their envelopes, top side, the mote's orientation (M2 may rotate the port blocks)
    for ref, e in geom.ENVELOPES.items():
        fps[ref].SetPosition(V((e[0] + e[2]) / 2, (e[1] + e[3]) / 2))
        fps[ref].SetOrientationDegrees(90)
    # inserts: the Altium import left the insert's NPTH pad with size 0 (DRC "padstack_invalid"); give it its drill size
    for ref in geom.INSERTS:
        for pad in fps[ref].Pads():
            if pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH and pad.GetDrillSize().x > 0:
                pad.SetSize(pcbnew.F_Cu, pad.GetDrillSize())
    # inserts: Sofar's MP1 ring (arc + 7 vias) translated to each position; the footprint as the mote's (bottom)
    blocks = []
    src = geom.xy(mote.mote_fp["MP1"].GetPosition())
    for ref, p in geom.INSERTS.items():
        blk = {"name": f"RING_{ref}", "refs": ["MP1"], "ref_map": {"MP1": ref}, "src": list(src), "dst": list(p),
               "rot": 0, "radius": 3.7, "kinds": ["arc", "via"], "nets": ["BM1_P"],
               "net_map": {"BM1_P": f"/Top-Level Schematic/{geom.INSERT_NET[ref]}"},
               "note": "Sofar's insert contact copied from MP1: C arc r 3.03 w 1.2 ~290 deg on L1, 7 vias 0.6/0.254 at r 3.0"}
        T = motecopy.transform_of(blk)
        mote.place_footprints(blk, T)
        n = mote.copy_copper(blk, T)
        blk["copied"] = n
        blocks.append(blk)
    return blocks


def draw_envelopes(board):
    c = geom.ENVELOPE_CLEAR
    for ref, e in geom.ENVELOPES.items():
        add_rect(board, e, pcbnew.Eco1_User, 0.15)
        add_rect(board, (e[0] - c, e[1] - c, e[2] + c, e[3] + c), pcbnew.Eco2_User, 0.1)
        add_text(board, f"{ref} 50 W envelope 15.5 x 15.5 (+2 mm clear)", ((e[0] + e[2]) / 2, e[1] - 0.9), pcbnew.Eco1_User, 0.8)
    b = geom.BAND
    add_rect(board, (geom.OUTLINE["x0"] + 0.5, b[0], 23.2, b[1]), pcbnew.Eco2_User, 0.1)
    add_text(board, f"band y {b[0]}..{b[1]} ({b[1] - b[0]:.0f} mm)", (-2.0, b[0] + 0.6), pcbnew.Eco2_User, 0.8)


def insert_rule_areas(board):
    for ref, p in geom.INSERTS.items():
        z = pcbnew.ZONE(board)
        z.SetIsRuleArea(True)
        z.SetDoNotAllowCopperPour(True)
        z.SetDoNotAllowTracks(False)
        z.SetDoNotAllowVias(False)
        z.SetDoNotAllowPads(False)
        z.SetDoNotAllowFootprints(False)
        ls = pcbnew.LSET()
        for l in geom.CU:
            ls.addLayer(l)
        z.SetLayerSet(ls)
        ch = pcbnew.SHAPE_LINE_CHAIN()
        n = 72
        for k in range(n):
            a = 2 * math.pi * k / n
            ch.Append(V(p[0] + geom.INSERT_KEEPOUT_R * math.cos(a), p[1] + geom.INSERT_KEEPOUT_R * math.sin(a)))
        ch.SetClosed(True)
        z.Outline().AddOutline(ch)
        z.SetZoneName(f"insert pullback {ref} r{geom.INSERT_KEEPOUT_R}")
        board.Add(z)


def write_stackup(path):
    text = open(path, encoding="utf-8").read()
    if "(stackup" in text:
        return
    key = "\t(setup\n"
    i = text.index(key) + len(key)
    open(path, "w", encoding="utf-8").write(text[:i] + STACKUP + text[i:])


def main():
    board = geom.load()
    draw_outline(board)
    mote = motecopy.Mote(board)
    blocks = place_fixed(board, mote)
    draw_envelopes(board)
    insert_rule_areas(board)
    board.GetDesignSettings().SetAuxOrigin(V(0, 0))
    geom.save(board)
    write_stackup(str(geom.BOARD))
    json.dump({"frame": "board mm, Pi NW corner = (0,0)", "blocks": blocks}, open(geom.EXP / "blocks.json", "w"), indent=1)
    print("M1 drawn; ring blocks:", [(b["name"], b["copied"]) for b in blocks])


if __name__ == "__main__":
    main()
