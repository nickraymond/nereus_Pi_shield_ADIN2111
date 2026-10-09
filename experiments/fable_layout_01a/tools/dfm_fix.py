#!/usr/bin/env python3
"""DFM fixes that are not copper (BRIEF 1.a §6, DFM.md rows 17–19): silkscreen to JLCPCB's legend limits.
Applied by tools/build_all.sh right after m2_place.py (placement), before the copper copy, so a START=m2 rerun redoes it.

  - every silk line thinner than 0.15 mm is set to 0.15 (JLC: legend minimum line width ≥ 0.15 mm);
  - every visible reference designator on silk is set to 1.0 mm high, 0.15 mm thick (JLC: min text height 1.0 mm) and
    moved to the first clear spot beside its courtyard (north, south, west, east, then the corners) where it touches no
    pad (0.15 mm, JLC pad-to-silk), no mask aperture and no other reference; a reference with no clear spot within
    1.5 mm of its courtyard is hidden and listed (the part is still identified by the assembly files);
  - a footprint silk line that crosses a pad of the same side (0.15 mm) is removed (clipped: JLC's own silk clip
    would erase it in production anyway, and KiCad's DRC warns about it until then).
Writes out/m2/dfm_fix.json with what changed. Nothing on a copper layer is touched.
"""
import json

import pcbnew

import geom
from geom import MM, mm, V

MIN_LINE = 0.15
TEXT_H, TEXT_T = 1.0, 0.15
PAD_CLR = 0.15


def silk_of(side):
    return pcbnew.F_SilkS if side == "F" else pcbnew.B_SilkS


def mask_of(side):
    return pcbnew.F_Mask if side == "F" else pcbnew.B_Mask


def main():
    board = geom.load()
    rep = {"lines_widened": 0, "lines_removed": [], "refs_resized": 0, "refs_moved": [], "refs_hidden": [], "values_hidden": 0}
    fps = list(board.GetFootprints())
    # obstacles per side: pads (copper or mask on that side) and the fiducials' mask apertures
    obst = {"F": [], "B": []}
    for f in fps:
        for p in f.Pads():
            for side, cu in (("F", pcbnew.F_Cu), ("B", pcbnew.B_Cu)):
                if p.IsOnLayer(cu) or p.GetDrillSize().x > 0:
                    obst[side].append(p.GetEffectiveShape(cu))
                    try:                    # a pad with its own mask margin (the fiducials: 0.75 copper, 2.25 aperture) bares that much copper-free
                        m = p.GetLocalSolderMaskMargin()
                        m = m.value() if hasattr(m, "value") else m
                    except Exception:
                        m = None
                    if m and m > 0:
                        sz = p.GetSize(cu)
                        obst[side].append(pcbnew.SHAPE_CIRCLE(p.GetPosition(), max(sz.x, sz.y) // 2 + int(m)))
        for g in f.GraphicalItems():
            if g.GetClass() == "PCB_SHAPE" and g.GetLayer() in (pcbnew.F_Mask, pcbnew.B_Mask):
                obst["F" if g.GetLayer() == pcbnew.F_Mask else "B"].append(g.GetEffectiveShape(g.GetLayer()))
    # 1. line widths, 2. lines over pads, 2b. footprint silk texts (pin-1 marks and the like) to the legend limits
    silk_lines = {"F": [], "B": []}
    for f in fps:
        side = "B" if f.IsFlipped() else "F"
        for g in list(f.GraphicalItems()):
            if g.GetClass() == "PCB_TEXT" and g.IsVisible() and pcbnew.IsBackLayer(g.GetLayer()) != g.IsMirrored():
                g.SetMirrored(pcbnew.IsBackLayer(g.GetLayer()))          # a back-layer text reads mirrored (QE round 4 N1: the stock
                rep["texts_mirrored"] = rep.get("texts_mirrored", 0) + 1  # SOT-23-THIN's '*' on B.Fab under U5 / U10, DRC nonmirrored_text)
            if g.GetClass() == "PCB_TEXT" and g.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS) and g.IsVisible():
                if mm(g.GetTextThickness()) < TEXT_T:
                    g.SetTextThickness(MM(TEXT_T))
                    rep["texts_thickened"] = rep.get("texts_thickened", 0) + 1
                if mm(g.GetTextHeight()) < TEXT_H:
                    g.SetTextSize(pcbnew.VECTOR2I(MM(TEXT_H), MM(TEXT_H)))
                    rep["texts_enlarged"] = rep.get("texts_enlarged", 0) + 1
                continue
            if g.GetClass() != "PCB_SHAPE" or g.GetLayer() not in (pcbnew.F_SilkS, pcbnew.B_SilkS):
                continue
            if 0 < mm(g.GetWidth()) < MIN_LINE:
                g.SetWidth(MM(MIN_LINE))
                rep["lines_widened"] += 1
            gs = "F" if g.GetLayer() == pcbnew.F_SilkS else "B"
            shape = g.GetEffectiveShape(g.GetLayer())
            if any(shape.Collide(o, MM(PAD_CLR)) for o in obst[gs]):
                f.Remove(g)
                rep["lines_removed"].append(f.GetReference())
            else:
                silk_lines[gs].append(g.GetEffectiveShape(g.GetLayer()))
    for d in board.GetDrawings():
        if d.GetClass() == "PCB_SHAPE" and d.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS) and 0 < mm(d.GetWidth()) < MIN_LINE:
            d.SetWidth(MM(MIN_LINE))
            rep["lines_widened"] += 1
    # 3. references: size, then a clear spot
    placed_refs = {"F": [], "B": []}
    order = sorted(fps, key=lambda f: -(geom.courtyard_bbox(f) or (0, 0, 0, 0))[2])
    for f in sorted(fps, key=lambda f: f.GetReference()):
        t = f.Reference()
        if t.GetLayer() not in (pcbnew.F_SilkS, pcbnew.B_SilkS):
            continue
        v = f.Value()
        if v.IsVisible() and v.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS):
            v.SetVisible(False)
            rep["values_hidden"] += 1
        if not t.IsVisible() or geom.xy(f.GetPosition())[0] > 45:
            continue
        side = "F" if t.GetLayer() == pcbnew.F_SilkS else "B"
        t.SetTextSize(pcbnew.VECTOR2I(MM(TEXT_H), MM(TEXT_H)))
        t.SetTextThickness(MM(TEXT_T))
        t.SetTextAngleDegrees(0)
        t.SetMirrored(side == "B")
        rep["refs_resized"] += 1
        cy = geom.courtyard_bbox(f)
        if cy is None:
            continue
        tb = t.GetBoundingBox()
        tw, th = mm(tb.GetWidth()) + 0.3, mm(tb.GetHeight()) + 0.3
        cx, cyy = (cy[0] + cy[2]) / 2, (cy[1] + cy[3]) / 2

        def clear(x, y):
            t.SetPosition(V(x, y))
            bb = t.GetBoundingBox()           # DRC's silk overlap test is by the text's box, not its glyphs
            s = pcbnew.SHAPE_RECT(bb.GetPosition(), bb.GetWidth(), bb.GetHeight())
            if any(s.Collide(o, MM(PAD_CLR)) for o in obst[side]):
                return False
            if any(s.Collide(o, MM(0.1)) for o in placed_refs[side]):
                return False
            if any(s.Collide(o, MM(0.05)) for o in silk_lines[side]):
                return False          # other footprints' silk outlines (DRC silk_overlap)
            o = geom.OUTLINE
            b = t.GetBoundingBox()
            return mm(b.GetLeft()) > o["x0"] + 0.5 and mm(b.GetRight()) < o["x1"] - 0.5 and mm(b.GetTop()) > o["y0"] + 0.5 and mm(b.GetBottom()) < o["y1"] - 0.5
        cands = []
        for gap in (0.2, 0.6, 1.0, 1.5):
            cands += [(cx, cy[1] - th / 2 - gap), (cx, cy[3] + th / 2 + gap), (cy[0] - tw / 2 - gap, cyy), (cy[2] + tw / 2 + gap, cyy),
                      (cy[0] - tw / 2 - gap, cy[1] - th / 2 - gap), (cy[2] + tw / 2 + gap, cy[1] - th / 2 - gap),
                      (cy[0] - tw / 2 - gap, cy[3] + th / 2 + gap), (cy[2] + tw / 2 + gap, cy[3] + th / 2 + gap)]
        # first the footprint's own spot (Sofar's / the library's), then the candidates
        own = geom.xy(t.GetPosition())
        found = None
        for x, y in [own] + cands:
            if clear(x, y):
                found = (x, y)
                break
        if found is None:
            t.SetPosition(V(*own))
            t.SetVisible(False)
            rep["refs_hidden"].append(f.GetReference())
        else:
            t.SetPosition(V(*found))
            bb = t.GetBoundingBox()
            placed_refs[side].append(pcbnew.SHAPE_RECT(bb.GetPosition(), bb.GetWidth(), bb.GetHeight()))
            if geom.dist(found, own) > 0.01:
                rep["refs_moved"].append(f.GetReference())
    geom.save(board)
    (geom.OUT / "m2").mkdir(parents=True, exist_ok=True)
    json.dump(rep, open(geom.OUT / "m2" / "dfm_fix.json", "w"), indent=1)
    print(f"dfm_fix: {rep['lines_widened']} silk lines widened to {MIN_LINE}, {len(rep['lines_removed'])} lines over pads removed "
          f"({len(set(rep['lines_removed']))} footprints), {rep['refs_resized']} references at {TEXT_H}/{TEXT_T}, {len(rep['refs_moved'])} moved, "
          f"{len(rep['refs_hidden'])} hidden: {' '.join(rep['refs_hidden'])}; {rep['values_hidden']} silk values hidden")


if __name__ == "__main__":
    main()
