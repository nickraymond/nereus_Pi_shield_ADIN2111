"""Step 9g: board name and Bristlemouth logo (Nick, 2026-11-10: name "Pi Shield, ADIN2111 Rev0", no part
number, in the north-east space). No copper changes.

- The logo (two silkscreen polygons that sat outside the outline at x 203..206) moves into the north-east
  corner, unchanged in size; the name stands left of it in two lines.
- The frame lines of Sofar's old title block outside the outline (9 lines, y < 65) are removed.
- Bottom side: Sofar's "PCBA-000639-AB" and "BM Mote" are replaced by the same name.
"""
import sys
import pcbnew
import boardio
from boardio import mm

F = pcbnew.FromMM
b = boardio.load()
TOP, BOT = b.GetLayerID("Top Overlay"), b.GetLayerID("Bottom Overlay")
draw = list(b.GetDrawings())
if any(d.Type() == pcbnew.PCB_TEXT_T and d.GetText() == "Pi Shield" for d in draw):
    sys.exit("step 9g already applied (text 'Pi Shield' exists); nothing done")


def text(s, x, y, w, h, th, layer=TOP, just=pcbnew.GR_TEXT_H_ALIGN_CENTER):
    t = pcbnew.PCB_TEXT(b)
    t.SetText(s); t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(F(w), F(h))); t.SetTextThickness(F(th))
    t.SetHorizJustify(just); t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
    t.SetMirrored(layer == BOT)
    t.SetPosition(pcbnew.VECTOR2I(F(x), F(y)))
    b.Add(t)


logo = [d for d in draw if d.Type() == pcbnew.PCB_SHAPE_T and d.GetLayer() == TOP and d.GetShape() == pcbnew.SHAPE_T_POLY
        and mm(d.GetBoundingBox().GetX()) > 181.3]
assert len(logo) == 2, len(logo)
x0 = min(mm(d.GetBoundingBox().GetX()) for d in logo); x1 = max(mm(d.GetBoundingBox().GetRight()) for d in logo)
y0 = min(mm(d.GetBoundingBox().GetY()) for d in logo); y1 = max(mm(d.GetBoundingBox().GetBottom()) for d in logo)
cx, cy = 178.30, 93.30
for d in logo:
    d.Move(pcbnew.VECTOR2I(F(cx - (x0 + x1) / 2), F(cy - (y0 + y1) / 2)))
text("Pi Shield", 176.30, 92.20, 1.0, 1.3, 0.2, just=pcbnew.GR_TEXT_H_ALIGN_RIGHT)
text("ADIN2111 Rev0", 176.30, 94.10, 0.65, 1.0, 0.15, just=pcbnew.GR_TEXT_H_ALIGN_RIGHT)

frame = [d for d in draw if d.Type() == pcbnew.PCB_SHAPE_T and d.GetLayer() == TOP and d.GetShape() == pcbnew.SHAPE_T_SEGMENT
         and mm(d.GetBoundingBox().GetBottom()) < 70]
assert len(frame) == 9, len(frame)
old = [d for d in draw if d.Type() == pcbnew.PCB_TEXTBOX_T and d.GetLayer() == BOT and d.GetText() in ("PCBA-000639-AB", "BM Mote")]
assert len(old) == 2, len(old)
for d in frame + old:
    b.Remove(d)
text("Pi Shield", 131.60, 110.20, 1.0, 1.3, 0.2, layer=BOT)
text("ADIN2111 Rev0", 131.60, 111.90, 0.7, 1.0, 0.15, layer=BOT)

boardio.save(b)
print("  logo moved by (%.2f, %.2f) mm, size %.2f x %.2f mm; 4 texts added; %d old items removed" % (cx - (x0 + x1) / 2, cy - (y0 + y1) / 2, x1 - x0, y1 - y0, len(frame) + len(old)))
