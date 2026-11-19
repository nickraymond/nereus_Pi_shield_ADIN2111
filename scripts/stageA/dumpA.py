"""Read-only: bus nets BM1_P/N, BM2_P/N on the stage 0c board, in the mock frame (X' = x - 100, y = 100 - ky), mm.
KiCad's Python: dumpA.py <board .kicad_pcb>"""
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); mm = pcbnew.ToMM
def F(p): return "(%.3f, %.3f)" % (mm(p.x) - 100, 100 - mm(p.y))
NETS = tuple("/Top-Level Schematic/" + n for n in ("BM1_P", "BM1_N", "BM2_P", "BM2_N"))
for f in b.GetFootprints():
    for p in f.Pads():
        if p.GetNetname() in NETS:
            bb = p.GetBoundingBox()
            print("PAD %-4s %-3s %-28s at %s box X' %.3f..%.3f y %.3f..%.3f layer %s" % (f.GetReference(), p.GetNumber(), p.GetNetname(), F(p.GetPosition()),
                  mm(bb.GetLeft()) - 100, mm(bb.GetRight()) - 100, 100 - mm(bb.GetBottom()), 100 - mm(bb.GetTop()), b.GetLayerName(p.GetLayer())))
for t in b.GetTracks():
    if t.GetNetname() in NETS:
        if t.Type() == pcbnew.PCB_VIA_T: print("VIA %-6s at %s" % (t.GetNetname(), F(t.GetPosition())))
        else: print("TRK %-6s %-10s w %.2f %s -> %s" % (t.GetNetname(), b.GetLayerName(t.GetLayer()), mm(t.GetWidth()), F(t.GetStart()), F(t.GetEnd())))
for d in b.GetDrawings():
    if pcbnew.IsCopperLayer(d.GetLayer()) and hasattr(d, "GetNetname") and d.GetNetname() in NETS:
        bb = d.GetBoundingBox(); print("SHAPE %s %s X' %.3f..%.3f y %.3f..%.3f" % (d.GetNetname(), b.GetLayerName(d.GetLayer()), mm(bb.GetLeft()) - 100, mm(bb.GetRight()) - 100, 100 - mm(bb.GetBottom()), 100 - mm(bb.GetTop())))
for z in b.Zones():
    if z.GetNetname() in NETS: print("ZONE", z.GetNetname(), z.GetZoneName())
for r in ("J9", "J10", "L1", "L2", "T1", "T2", "J8", "J3", "J7"):
    f = b.FindFootprintByReference(r)
    if f:
        c = f.GetCourtyard(f.GetLayer()).BBox()
        print("FP %-4s at %s rot %.0f %s courtyard X' %.3f..%.3f y %.3f..%.3f" % (r, F(f.GetPosition()), f.GetOrientationDegrees(), b.GetLayerName(f.GetLayer()), mm(c.GetLeft()) - 100, mm(c.GetRight()) - 100, 100 - mm(c.GetBottom()), 100 - mm(c.GetTop())))
