"""Do two same-net zone fills on one layer really touch? Prints the gap (mm) between each S3 zone's fill and the other
fills of the same net on the same layer, by growing the S3 fill in steps until the intersection is not empty.
Usage: <KiCad python> zone_touch.py <board>"""
import pcbnew, sys
b = pcbnew.LoadBoard(sys.argv[1])
for z in b.Zones():
    if not z.GetZoneName().startswith('S3 ') or z.GetIsRuleArea(): continue
    L = z.GetLayer()
    for o in b.Zones():
        if o.m_Uuid == z.m_Uuid or o.GetIsRuleArea() or o.GetNetCode() != z.GetNetCode() or not o.IsOnLayer(L): continue
        A = o.GetFilledPolysList(L); gap = None
        for g in (0, 1, 5, 10, 20, 50, 100, 150, 200, 300, 500):          # micrometres
            P = pcbnew.SHAPE_POLY_SET(z.GetFilledPolysList(L))
            if g: P.Inflate(g * 1000, pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, 2000)
            P.BooleanIntersection(A)
            if P.OutlineCount() and P.Area() > 0: gap = g; break
        print('%s  <->  zone %s "%s" on %s: fills meet when grown by %s um' % (z.GetZoneName(), o.GetNetname(), o.GetZoneName(), b.GetLayerName(L), gap))
