"""Plane continuity: every filled zone on the two plane layers (and any other zone the pad row touches), as net, name, filled area and
number of separate pieces; with a second board, the same table side by side. A plane lane cut into islands shows as more pieces
(or, with island removal, as lost area). Also: which zone pieces the row's plane-connected pads sit in.
Usage: <KiCad python> planes.py <board> > table      (run once per board, each in its own process; compare with diff / paste)"""
import pcbnew, sys
DX, DY = 113.47, 89.34
b = pcbnew.LoadBoard(sys.argv[1]); mm = pcbnew.ToMM
for z in sorted(b.Zones(), key=lambda z: (z.GetNetname(), z.GetZoneName(), z.GetBoundingBox().GetLeft(), z.GetBoundingBox().GetTop())):
    if z.GetIsRuleArea(): continue
    for l in z.GetLayerSet().Seq():
        name = b.GetLayerName(l); ps = z.GetFilledPolysList(l); bb = z.GetBoundingBox()
        if 'Plane' not in name and not (mm(bb.GetTop()) - DY < 8.5 and mm(bb.GetBottom()) - DY > 5.5 and mm(bb.GetRight()) - DX > 10): continue
        areas = sorted((round(ps.Outline(i).Area() / 1e12 - sum(ps.Hole(i, h).Area() for h in range(ps.HoleCount(i))) / 1e12, 2) for i in range(ps.OutlineCount())), reverse=True)
        print('%-11s %-8s %-46s box (%.1f, %.1f)-(%.1f, %.1f)  pieces %d  area %.2f mm2  %s' % (name, z.GetNetname().split('/')[-1] or '(none)', (z.GetZoneName() or '-')[:46],
              mm(bb.GetLeft()) - DX, mm(bb.GetTop()) - DY, mm(bb.GetRight()) - DX, mm(bb.GetBottom()) - DY, len(areas), sum(areas), areas[:6]))
