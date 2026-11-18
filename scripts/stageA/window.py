"""Read-only: everything with copper on one layer (or a through hole / via) inside a window, mock frame, mm.
KiCad's Python: window.py <board> <layer name> <X'min> <X'max> <ymin> <ymax>"""
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); mm = pcbnew.ToMM
lay = b.GetLayerID(sys.argv[2]); x0, x1, y0, y1 = map(float, sys.argv[3:7])
def box(bb): return (mm(bb.GetLeft()) - 100, mm(bb.GetRight()) - 100, 100 - mm(bb.GetBottom()), 100 - mm(bb.GetTop()))
def inwin(q): return q[0] < x1 and q[1] > x0 and q[2] < y1 and q[3] > y0
def short(n): return n.split("/")[-1] or "-"
for f in b.GetFootprints():
    for p in f.Pads():
        if p.IsOnLayer(lay) or p.HasHole():
            q = box(p.GetBoundingBox())
            if inwin(q): print("PAD  %-5s %-3s %-16s X' %7.3f..%7.3f y %7.3f..%7.3f%s" % (f.GetReference(), p.GetNumber(), short(p.GetNetname()), *q, " hole" if p.HasHole() else ""))
    if f.GetLayer() == lay:
        c = f.GetCourtyard(lay)
        if c.OutlineCount():
            q = box(c.BBox())
            if inwin(q): print("CRT  %-5s %-22s X' %7.3f..%7.3f y %7.3f..%7.3f" % (f.GetReference(), f.GetValue()[:22], *q))
for t in b.GetTracks():
    isvia = t.Type() == pcbnew.PCB_VIA_T
    if isvia or t.GetLayer() == lay:
        q = box(t.GetBoundingBox())
        if inwin(q):
            if isvia: print("VIA  %-16s (%.3f, %.3f) dia %.2f" % (short(t.GetNetname()), mm(t.GetPosition().x) - 100, 100 - mm(t.GetPosition().y), mm(t.GetWidth(lay))))
            else: print("TRK  %-16s w %.2f (%.3f, %.3f) -> (%.3f, %.3f)" % (short(t.GetNetname()), mm(t.GetWidth()), mm(t.GetStart().x) - 100, 100 - mm(t.GetStart().y), mm(t.GetEnd().x) - 100, 100 - mm(t.GetEnd().y)))
for d in b.GetDrawings():
    if d.GetLayer() == lay:
        q = box(d.GetBoundingBox())
        if inwin(q): print("SHP  %-16s X' %7.3f..%7.3f y %7.3f..%7.3f" % (short(d.GetNetname()) if hasattr(d, "GetNetname") else d.GetClass(), *q))
for z in b.Zones():
    if z.IsOnLayer(lay):
        q = box(z.GetBoundingBox())
        if inwin(q): print("%s %-16s '%s' X' %7.3f..%7.3f y %7.3f..%7.3f" % ("RULE" if z.GetIsRuleArea() else "ZONE", short(z.GetNetname()), z.GetZoneName(), *q))
