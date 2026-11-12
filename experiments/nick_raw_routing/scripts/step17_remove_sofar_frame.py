"""Step 17: Sofar's empty name frame comes off the bottom silkscreen (Nick's comment on the summary doc,
2026-11-11: "Remove it").

The frame stood around Sofar's part number and "BM Mote" (x 124.50-138.85, y 109.13-112.63). Step 9g put the
shield's name into it and step 12 took that name off the bottom again, which left the frame empty. It is five
board-level lines on B.SilkS, 0.2 mm wide. Nothing else changes.
"""
import sys
import pcbnew
import boardio

mm = pcbnew.ToMM
FRAME = [((124.50, 109.13), (138.85, 109.13)), ((124.50, 112.63), (136.48, 112.63)), ((136.48, 111.10), (138.53, 111.10)),
         ((136.48, 112.63), (136.48, 111.10)), ((138.85, 110.43), (138.85, 109.13))]

b = boardio.load()
silk = b.GetLayerID("B.SilkS")
assert silk >= 0
drawings = list(b.GetDrawings())


def ends(d):
    return (round(mm(d.GetStart().x), 2), round(mm(d.GetStart().y), 2)), (round(mm(d.GetEnd().x), 2), round(mm(d.GetEnd().y), 2))


found = []
for want in FRAME:
    hits = [d for d in drawings if d.GetClass() == "PCB_SHAPE" and d.GetLayer() == silk and d.GetShape() == pcbnew.SHAPE_T_SEGMENT
            and ends(d) in (want, want[::-1])]
    found.append(hits)
if not any(found):
    sys.exit("step 17 already applied (the frame's lines are gone); nothing done")
assert all(len(h) == 1 for h in found), [len(h) for h in found]
# nothing else may stand inside the frame: it must be empty before it goes
inside = pcbnew.BOX2I(pcbnew.VECTOR2I(pcbnew.FromMM(124.80), pcbnew.FromMM(109.43)), pcbnew.VECTOR2I(pcbnew.FromMM(11.38), pcbnew.FromMM(1.40)))
for d in drawings:
    if d.GetLayer() == silk and d.GetBoundingBox().Intersects(inside):
        raise AssertionError("the frame is not empty: %s at %s" % (d.GetClass(), ends(d) if d.GetClass() == "PCB_SHAPE" else d.GetText()))
for hits in found:
    b.Remove(hits[0])
boardio.save(b)
print("  5 lines of Sofar's frame removed from B.SilkS")
