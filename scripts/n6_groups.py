"""Read-only: pad nets of chosen parts, extents of the 5 V converter and motor driver groups, and the filled
copper area near them per layer. Usage: python n6_groups.py start.kicad_pcb"""
import sys, pcbnew
mm = pcbnew.ToMM
b = pcbnew.LoadBoard(sys.argv[1])
fp = {f.GetReference(): f for f in b.GetFootprints()}
short = lambda n: n.split("/")[-1]
for r in ["U12", "U13", "U10", "JP2", "D8", "D9", "D10", "U11", "JP1", "F1", "J4", "J5", "J7", "J8", "J9", "J10", "J3", "U4"]:
    print(r, fp[r].GetValue(), " ".join("%s=%s" % (p.GetNumber(), short(p.GetNetname())) for p in fp[r].Pads()))
def box(f):
    cy = f.GetCourtyard(pcbnew.F_CrtYd if f.GetLayer() == pcbnew.F_Cu else pcbnew.B_CrtYd)
    q = cy.BBox() if cy.OutlineCount() else f.GetBoundingBox(False)
    return [mm(q.GetLeft()), mm(q.GetTop()), mm(q.GetRight()), mm(q.GetBottom())]
groups = {"5V converter": "U10 L6 C53 C54 C55 C56 C57 C58 R37 R38 R39 R40".split(),
          "motor driver": "U12 C60 C61 C62 C63 C64 C66 R48".split(),
          "ADC + pot": "U13 C65 C67 R49 R50 R51".split(),
          "load switch": "U11 C59 R34 R36 R41 R42 R35 D3 C50 J5".split()}
for g, refs in groups.items():
    bs = [box(fp[r]) for r in refs]
    e = [min(q[0] for q in bs), min(q[1] for q in bs), max(q[2] for q in bs), max(q[3] for q in bs)]
    print(g, "extent %.1f x %.1f mm" % (e[2] - e[0], e[3] - e[1]), [round(v, 1) for v in e], "sides", "".join(sorted({"T" if fp[r].GetLayer() == pcbnew.F_Cu else "B" for r in refs})))
# filled copper area of named zones and of every zone inside a window round U10 / U12
for z in b.Zones():
    if z.GetIsRuleArea(): continue
    n = z.GetZoneName()
    if n.startswith("S3") or "U10" in n:
        for l in z.GetLayerSet().Seq():
            print("zone '%s' %s %s filled %.0f mm2" % (n, short(z.GetNetname()), b.GetLayerName(l), z.GetFilledPolysList(l).Area() / 1e12))
ds = b.GetDesignSettings(); st = ds.GetStackupDescriptor()
print("layers", b.GetCopperLayerCount(), "thickness", mm(ds.GetBoardThickness()))
for f in ["L1", "L6", "L3", "C22", "J7", "J3"]:
    m = fp[f].Models()
    print(f, "3D:", [x.m_Filename.split("/")[-1] for x in m][:1])
