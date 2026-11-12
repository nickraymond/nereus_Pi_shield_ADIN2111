"""Print a short state summary of the saved board: report.py [REF ...]"""
import sys
import pcbnew
import boardio
from boardio import pos

b = boardio.load()
fp = boardio.footprints(b)
print("footprints:", len(fp), " tracks+vias:", len(b.GetTracks()), " zones:", len(b.Zones()))
print("Edge.Cuts items:", sum(1 for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts))
for r in sys.argv[1:]:
    if r not in fp:
        print(" ", r, "not on the board")
        continue
    nets = sorted({p.GetNetname().split("/")[-1] for p in fp[r].Pads() if p.GetNetname()})
    print("  %-5s at %s rot %g %s %s" % (r, pos(fp[r]), fp[r].GetOrientationDegrees(), fp[r].GetLayerName(), nets))
