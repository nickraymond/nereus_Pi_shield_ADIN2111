"""Read-only dump of the starting board: footprints (ref, value, side, position, courtyard box), J1 pin nets,
board outline box. Run with KiCad's Python. Writes nothing into the project."""
import sys, json, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
mm = pcbnew.ToMM
out = {"fps": [], "j1": {}}
bb = b.GetBoardEdgesBoundingBox()
out["edge"] = [mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())]
for f in b.GetFootprints():
    box = f.GetBoundingBox(False)
    cy = f.GetCourtyard(pcbnew.F_CrtYd if f.GetLayer() == pcbnew.F_Cu else pcbnew.B_CrtYd)
    if cy.OutlineCount():
        cb = cy.BBox(); box = cb
    out["fps"].append(dict(ref=f.GetReference(), val=f.GetValue(), side="T" if f.GetLayer() == pcbnew.F_Cu else "B",
        x=mm(f.GetPosition().x), y=mm(f.GetPosition().y), rot=f.GetOrientationDegrees(), locked=f.IsLocked(),
        box=[mm(box.GetLeft()), mm(box.GetTop()), mm(box.GetRight()), mm(box.GetBottom())],
        fp=str(f.GetFPID().GetLibItemName()), nets=sorted({p.GetNetname() for p in f.Pads() if p.GetNetname()})))
    if f.GetReference() == "J1":
        for p in f.Pads():
            out["j1"][p.GetNumber()] = p.GetNetname()
json.dump(out, open(sys.argv[2], "w"), indent=0)
