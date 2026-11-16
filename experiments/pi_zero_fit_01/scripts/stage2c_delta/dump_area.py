"""Read-only: what is on and near the two new groups. Usage: <KiCad python> dump_area.py <board>"""
import sys
from s3lib import *
b = pcbnew.LoadBoard(sys.argv[1])
def court(f):
    f.BuildCourtyardCaches(); c = f.GetCourtyard(pcbnew.B_CrtYd if f.IsFlipped() else pcbnew.F_CrtYd).BBox()
    return tuple(round(v, 3) for v in (mm(c.GetLeft()) - DX, mm(c.GetTop()) - DY, mm(c.GetRight()) - DX, mm(c.GetBottom()) - DY))
BOX = [(-1, 29, 14, 40), (16, 29, 34, 40)]
inb = lambda x, y: any(a <= x <= c and bb <= y <= d for a, bb, c, d in BOX)
for f in sorted(b.GetFootprints(), key=lambda f: f.GetReference()):
    x, y = N(f.GetPosition())
    c = court(f)
    if inb(x, y) or inb(c[0], c[1]) or inb(c[2], c[3]):
        print('%-5s %-6s %-44s at (%.3f, %.3f) rot %g court %s' % (f.GetReference(), 'bot' if f.IsFlipped() else 'top', fpid_str(f)[:44], x, y, f.GetOrientationDegrees(), c))
        for p in f.Pads():
            if p.IsOnLayer(pcbnew.B_Cu):
                r = pad_rect(p); print('        pad %-3s %-28s box %.3f..%.3f / %.3f..%.3f drill %.2f' % (p.GetNumber(), p.GetNetname().split('/')[-1], r[0], r[2], r[1], r[3], mm(p.GetDrillSize().x)))
print('vias / B.Cu tracks in the boxes:')
for t in b.GetTracks():
    a, c = N(t.GetStart()), N(t.GetEnd())
    if not (inb(*a) or inb(*c)): continue
    if t.GetClass() == 'PCB_VIA': print('  via %s at %s dia %.2f drill %.2f' % (t.GetNetname().split('/')[-1], a, mm(t.GetWidth(pcbnew.B_Cu)), mm(t.GetDrill())))
    elif t.GetLayer() == pcbnew.B_Cu: print('  track %s %s-%s w %.2f' % (t.GetNetname().split('/')[-1], a, c, mm(t.GetWidth())))
for z in b.Zones():
    bb = z.GetBoundingBox(); zr = tuple(round(v, 2) for v in (mm(bb.GetLeft()) - DX, mm(bb.GetTop()) - DY, mm(bb.GetRight()) - DX, mm(bb.GetBottom()) - DY))
    if zr[2] > -1 and zr[0] < 34 and zr[3] > 29 and (z.IsOnLayer(pcbnew.B_Cu) or z.GetIsRuleArea()):
        print('  zone %s rule=%s layers=%s box %s %s' % (z.GetNetname(), z.GetIsRuleArea(), [b.GetLayerName(l) for l in z.GetLayerSet().Seq()][:8], zr, z.GetZoneName()))
for name in ('Vault:FP-RC0402-0_4-IPC_C', 'Vault:FP-CL278-IPC_C', 'Vault:FP-RMCF0402-IPC_C', 'Capacitor_SMD:C_0805_2012Metric'):
    f = lib_footprint(name); f.BuildCourtyardCaches(); c = f.GetCourtyard(pcbnew.F_CrtYd).BBox()
    print(name, 'court %.3f x %.3f centre (%.3f, %.3f)' % (mm(c.GetWidth()), mm(c.GetHeight()), mm(c.GetCenter().x), mm(c.GetCenter().y)),
          ['%s (%.3f, %.3f) %.3fx%.3f' % (p.GetNumber(), mm(p.GetPosition().x), mm(p.GetPosition().y), mm(p.GetSize(pcbnew.F_Cu).x), mm(p.GetSize(pcbnew.F_Cu).y)) for p in f.Pads()],
          'silk items', sum(1 for g in f.GraphicalItems() if g.GetLayer() == pcbnew.F_SilkS))
