"""Read-only: find Sofar's mote block on the starting board by comparison with Sofar's reference board
(same reference, same offset, same rotation), then measure the block: footprint courtyards per side, and the
copper (tracks, vias) that sits at the reference position. Usage: python n6_mote_extent.py start.kicad_pcb mote_ref.kicad_pcb out.json"""
import sys, json, collections, pcbnew
mm = pcbnew.ToMM
a = pcbnew.LoadBoard(sys.argv[1]); r = pcbnew.LoadBoard(sys.argv[2])
rf = {f.GetReference(): f for f in r.GetFootprints()}
offs = collections.Counter()
for f in a.GetFootprints():
    g = rf.get(f.GetReference())
    if g: offs[(round(mm(f.GetPosition().x - g.GetPosition().x), 2), round(mm(f.GetPosition().y - g.GetPosition().y), 2))] += 1
(ox, oy), n = offs.most_common(1)[0]
print("offset start - reference:", ox, oy, "shared by", n, "footprints; next:", offs.most_common(3)[1:])
def box(f):
    cy = f.GetCourtyard(pcbnew.F_CrtYd if f.GetLayer() == pcbnew.F_Cu else pcbnew.B_CrtYd)
    b = cy.BBox() if cy.OutlineCount() else f.GetBoundingBox(False)
    return [mm(b.GetLeft()), mm(b.GetTop()), mm(b.GetRight()), mm(b.GetBottom())]
core = []
for f in a.GetFootprints():
    g = rf.get(f.GetReference())
    if g and abs(mm(f.GetPosition().x - g.GetPosition().x) - ox) < 0.01 and abs(mm(f.GetPosition().y - g.GetPosition().y) - oy) < 0.01 \
       and abs(f.GetOrientationDegrees() - g.GetOrientationDegrees()) < 0.1 and f.GetLayer() == g.GetLayer():
        core.append(dict(ref=f.GetReference(), val=f.GetValue(), side="T" if f.GetLayer() == pcbnew.F_Cu else "B", box=box(f)))
def key(t, dx=0.0, dy=0.0):
    if t.Type() == pcbnew.PCB_VIA_T: return ("v", round(mm(t.GetPosition().x) + dx, 2), round(mm(t.GetPosition().y) + dy, 2))
    p = sorted([(round(mm(t.GetStart().x) + dx, 2), round(mm(t.GetStart().y) + dy, 2)), (round(mm(t.GetEnd().x) + dx, 2), round(mm(t.GetEnd().y) + dy, 2))])
    return ("t", t.GetLayerName(), p[0], p[1], round(mm(t.GetWidth()), 2))
refkeys = {key(t, ox, oy) for t in r.GetTracks()}
cu = []; other = 0
for t in a.GetTracks():
    k = key(t)
    if k in refkeys:
        if k[0] == "v": cu.append(("v", k[1], k[2], k[1], k[2], mm(t.GetWidth(pcbnew.F_Cu)) if hasattr(t, "GetWidth") else 0.6, ""))
        else: cu.append(("t", k[2][0], k[2][1], k[3][0], k[3][1], k[4], k[1]))
    else: other += 1
def ext(boxes):
    return [round(min(b[0] for b in boxes), 2), round(min(b[1] for b in boxes), 2), round(max(b[2] for b in boxes), 2), round(max(b[3] for b in boxes), 2)]
fb = ext([c["box"] for c in core]); cb = ext([[min(c[1], c[3]) - c[5] / 2, min(c[2], c[4]) - c[5] / 2, max(c[1], c[3]) + c[5] / 2, max(c[2], c[4]) + c[5] / 2] for c in cu])
print("core footprints:", len(core), "top", sum(c["side"] == "T" for c in core), "bottom", sum(c["side"] == "B" for c in core))
print("footprint courtyard extent:", fb, "size", round(fb[2] - fb[0], 2), "x", round(fb[3] - fb[1], 2))
print("Sofar copper kept:", len(cu), "items; extent", cb, "size", round(cb[2] - cb[0], 2), "x", round(cb[3] - cb[1], 2), "; other copper items:", other)
e = a.GetBoardEdgesBoundingBox(); print("board edge box:", [round(mm(v), 2) for v in (e.GetLeft(), e.GetTop(), e.GetRight(), e.GetBottom())])
zs = [(z.GetNetname(), z.GetLayerName(), [round(mm(v), 1) for v in (z.GetBoundingBox().GetLeft(), z.GetBoundingBox().GetTop(), z.GetBoundingBox().GetRight(), z.GetBoundingBox().GetBottom())], z.GetZoneName()) for z in a.Zones()]
for z in zs: print("zone", z)
json.dump(dict(offset=[ox, oy], core=core, copper=cu, fp_extent=fb, cu_extent=cb), open(sys.argv[3], "w"))
