#!/usr/bin/env python3
"""Set footprint type (attr) and an F.CrtYd courtyard on every footprint in a .pretty library.

Runs on KiCad's bundled Python (pcbnew module, used to read the footprints and compute geometry). The change
is written as plain text inserts (one `(attr ...)` line, four `fp_line`s on F.CrtYd), so the diff is exactly what
was added: KiCad's own writer would also regenerate every uuid. Each written file is re-loaded with pcbnew.

  PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
  $PY tools/fpattrs.py LIB.pretty            # report what would change
  $PY tools/fpattrs.py LIB.pretty --write    # change and save

Type (KiCad stock-library conventions): fiducials "smd exclude_from_bom"; test pads and mounting holes
"exclude_from_pos_files exclude_from_bom"; everything else with SMD pads "smd". A footprint that already has
a type or a courtyard is left alone for that item.
Courtyard (rectangle on F.CrtYd, 0.05 mm lines), first match wins:
  1. the footprint's own Altium courtyard: four thin (<= 0.05 mm) axis-aligned lines on one User layer forming a
     rectangle that encloses every pad;
  2. otherwise its largest User-layer outline that encloses every pad (Altium mechanical layers carry the
     body/assembly outline there, not on Fab);
  3. otherwise the bounding box of pads, silkscreen and fab plus 0.25 mm (IPC-7351 nominal), rounded out to 0.01 mm.
Pads are never touched.
"""
import re
import sys
import uuid
from pathlib import Path

pcbnew = None        # imported in main(): KiCad's bundled Python only; the text helpers below don't need it

MM = 1_000_000      # pcbnew internal units per mm (nm)
NOT_PLACED = {"PCB_TP_1.5mm", "Hole_M3"}     # bare copper test pad / mounting hole
FIDUCIAL = {"FIDUCIAL_075MM"}
MARGIN = 0.25


def mm(v):
    return v / MM


def want_attr(fp):
    name = fp.GetFPID().GetLibItemName().wx_str()
    if name in FIDUCIAL:
        return pcbnew.FP_SMD | pcbnew.FP_EXCLUDE_FROM_BOM, "smd exclude_from_bom"
    if name in NOT_PLACED:
        return pcbnew.FP_EXCLUDE_FROM_POS_FILES | pcbnew.FP_EXCLUDE_FROM_BOM, "exclude_from_pos_files exclude_from_bom"
    attrs = {p.GetAttribute() for p in fp.Pads()}
    if pcbnew.PAD_ATTRIB_PTH in attrs:
        raise ValueError(f"{name}: plated through-hole pads; classify by hand")
    return pcbnew.FP_SMD, "smd"


def bbox(items):
    """(left, top, right, bottom) in IU over the items' bounding boxes (plain min/max); for drawn shapes
    the stroke half-width is taken off, so the box is the drawn geometry (line centres)."""
    out = []
    for i in items:
        b = i.GetBoundingBox()
        w = i.GetWidth() // 2 if i.GetClass() == "PCB_SHAPE" else 0
        out.append((b.GetLeft() + w, b.GetTop() + w, b.GetRight() - w, b.GetBottom() - w))
    return (min(b[0] for b in out), min(b[1] for b in out), max(b[2] for b in out), max(b[3] for b in out))


def user_outline(fp, pads):
    """The largest User-layer outline (all drawn shapes on one User layer) that encloses the pads."""
    best, best_layer = None, None
    layers = {}
    for s in fp.GraphicalItems():
        if s.GetClass() == "PCB_SHAPE" and pcbnew.LayerName(s.GetLayer()).startswith("User."):
            layers.setdefault(s.GetLayer(), []).append(s)
    for layer, shapes in layers.items():
        b = bbox(shapes)
        if b[0] <= pads[0] and b[1] <= pads[1] and b[2] >= pads[2] and b[3] >= pads[3]:
            if best is None or (b[2] - b[0]) * (b[3] - b[1]) > (best[2] - best[0]) * (best[3] - best[1]):
                best, best_layer = b, pcbnew.LayerName(layer)
    return best, best_layer


def altium_courtyard(fp, pads):
    """Four thin axis-aligned lines on one User layer forming a rectangle that encloses the pads."""
    by_layer = {}
    for s in fp.GraphicalItems():
        if s.GetClass() != "PCB_SHAPE" or s.GetShape() != pcbnew.SHAPE_T_SEGMENT:
            continue
        if not pcbnew.LayerName(s.GetLayer()).startswith("User.") or mm(s.GetWidth()) > 0.051:
            continue
        a, b = s.GetStart(), s.GetEnd()
        if a.x != b.x and a.y != b.y:
            continue
        by_layer.setdefault(s.GetLayer(), []).append((a, b))
    for layer, segs in by_layer.items():
        xs = sorted({p.x for s in segs for p in s})
        ys = sorted({p.y for s in segs for p in s})
        if len(segs) < 4:
            continue
        x0, x1, y0, y1 = xs[0], xs[-1], ys[0], ys[-1]
        edges = {((min(a.x, b.x), min(a.y, b.y)), (max(a.x, b.x), max(a.y, b.y))) for a, b in segs}
        rect = {((x0, y0), (x1, y0)), ((x0, y1), (x1, y1)), ((x0, y0), (x0, y1)), ((x1, y0), (x1, y1))}
        if rect <= edges and x0 <= pads[0] and y0 <= pads[1] and x1 >= pads[2] and y1 >= pads[3]:
            return (x0, y0, x1, y1), pcbnew.LayerName(layer)
    return None, None


def computed_courtyard(fp, pads):
    fab = [s for s in fp.GraphicalItems() if s.GetClass() == "PCB_SHAPE"
           and s.GetLayer() in (pcbnew.F_Fab, pcbnew.B_Fab, pcbnew.F_SilkS)]
    l, t, r, b = pads
    if fab:
        fl, ft, fr, fb = bbox(fab)
        l, t, r, b = min(l, fl), min(t, ft), max(r, fr), max(b, fb)
    m = int(MARGIN * MM)
    step = int(0.01 * MM)
    return ((l - m) // step * step, (t - m) // step * step, -((-(r + m)) // step) * step, -((-(b + m)) // step) * step)


def fmt(iu):
    v = f"{iu / MM:.6f}".rstrip("0").rstrip(".")
    return "0" if v in ("-0", "") else v


def insert_text(text, attr_label, rect):
    """Insert `(attr ...)` before the first graphic/pad item and the courtyard lines before the first pad."""
    lines = text.split("\n")
    if attr_label:
        i = next(k for k, l in enumerate(lines) if re.match(r"^\t\((fp_|pad |model|embedded_fonts)", l))
        lines.insert(i, f"\t(attr {attr_label})")
    if rect:
        x0, y0, x1, y1 = rect
        block = []
        for (ax, ay), (bx, by) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
            block += ["\t(fp_line", f"\t\t(start {fmt(ax)} {fmt(ay)})", f"\t\t(end {fmt(bx)} {fmt(by)})",
                      "\t\t(stroke", "\t\t\t(width 0.05)", "\t\t\t(type solid)", "\t\t)",
                      '\t\t(layer "F.CrtYd")', f'\t\t(uuid "{uuid.uuid4()}")', "\t)"]
        i = next(k for k, l in enumerate(lines) if l.startswith("\t(pad "))
        lines[i:i] = block
    return "\n".join(lines)


def main(argv):
    global pcbnew
    import pcbnew as _pcbnew
    pcbnew = _pcbnew
    assert pcbnew.pcbIUScale.IU_PER_MM == MM
    lib = Path(argv[0]).resolve()
    write = "--write" in argv
    io = pcbnew.PCB_IO_MGR.PluginFind(pcbnew.PCB_IO_MGR.KICAD_SEXP)
    for path in sorted(lib.glob("*.kicad_mod")):
        name = path.stem
        fp = io.FootprintLoad(str(lib), name)
        notes = []
        attr, label = want_attr(fp)
        new_label, new_rect = None, None
        if fp.GetAttributes() & (pcbnew.FP_SMD | pcbnew.FP_THROUGH_HOLE | pcbnew.FP_EXCLUDE_FROM_POS_FILES):
            notes.append("type kept")
        else:
            new_label = label
            notes.append(f"type {label}")
        has_crtyd = any(s.GetLayer() == pcbnew.F_CrtYd for s in fp.GraphicalItems())
        if has_crtyd:
            notes.append("courtyard kept")
        else:
            pads = bbox(fp.Pads())
            rect, src = altium_courtyard(fp, pads)
            if rect is not None:
                src = f"Sofar's courtyard rectangle, {src}"
            else:
                rect, src = user_outline(fp, pads)
                if rect is not None:
                    src = f"Sofar's outer outline, {src}"
                else:
                    rect, src = computed_courtyard(fp, pads), "computed: pads+silk+fab+0.25"
            new_rect = rect
            notes.append(f"courtyard {mm(rect[2] - rect[0]):.2f}x{mm(rect[3] - rect[1]):.2f} mm ({src})")
        print(f"{name}: " + "; ".join(notes))
        if write and (new_label or new_rect):
            text = path.read_text()
            if "(attr " in text and new_label:
                raise ValueError(f"{name}: has an (attr) line pcbnew didn't report")
            path.write_text(insert_text(text, new_label, new_rect))
            check = io.FootprintLoad(str(lib), name)        # KiCad must parse it back
            got = check.GetAttributes() & (pcbnew.FP_SMD | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES)
            crt = [g for g in check.GraphicalItems() if g.GetLayer() == pcbnew.F_CrtYd]
            if (new_label and got != attr) or (new_rect and len(crt) != 4) or len(list(check.Pads())) != len(list(fp.Pads())):
                raise RuntimeError(f"{name}: written file doesn't read back as intended")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
