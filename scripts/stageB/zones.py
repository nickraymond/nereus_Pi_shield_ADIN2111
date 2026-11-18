"""Read-only: every zone and rule area, mock frame (X' = x - 100, y = 100 - ky), with how far it passes the board
outline's box and which J21 / J22 pads its outline box touches. KiCad's Python: zones.py <board>"""
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); mm = pcbnew.ToMM
e = b.GetBoardEdgesBoundingBox()
E = (mm(e.GetLeft()) - 100, mm(e.GetRight()) - 100, 100 - mm(e.GetBottom()), 100 - mm(e.GetTop()))
print("outline box X' %.3f..%.3f y %.3f..%.3f" % E)
hp = [(f.GetReference(), p) for f in b.GetFootprints() if f.GetReference() in ("J21", "J22") for p in f.Pads()]
for i, z in enumerate(b.Zones()):
    q = z.GetBoundingBox(); Q = (mm(q.GetLeft()) - 100, mm(q.GetRight()) - 100, 100 - mm(q.GetBottom()), 100 - mm(q.GetTop()))
    o = z.Outline(); over = []
    if Q[0] < E[0]: over.append("W %.2f" % (E[0] - Q[0]))
    if Q[1] > E[1]: over.append("E %.2f" % (Q[1] - E[1]))
    if Q[2] < E[2]: over.append("S %.2f" % (E[2] - Q[2]))
    if Q[3] > E[3]: over.append("N %.2f" % (Q[3] - E[3]))
    hit = sorted({r for r, p in hp if o.Collide(p.GetPosition(), pcbnew.FromMM(0.9))})
    lay = ",".join(b.GetLayerName(l).split()[0] + ("" if len(b.GetLayerName(l).split()) < 2 else b.GetLayerName(l).split()[1][:1]) for l in z.GetLayerSet().Seq())
    ra = ""
    if z.GetIsRuleArea(): ra = "RULE no:" + "".join(c for c, v in (("T", z.GetDoNotAllowTracks()), ("V", z.GetDoNotAllowVias()), ("P", z.GetDoNotAllowPads()), ("Z", z.GetDoNotAllowZoneFills()), ("F", z.GetDoNotAllowFootprints())) if v)
    print("%3d %-22s %-18s %-14s prio %d  X' %7.2f..%7.2f y %7.2f..%7.2f  %5d vtx  %s %s %s" % (i, (z.GetZoneName() or "-")[:22], z.GetNetname().split("/")[-1] or "-", lay, z.GetAssignedPriority(), *Q, o.TotalVertices(), ra, ("PAST " + " ".join(over)) if over else "", ("pads of " + "/".join(hit)) if hit else ""))
