"""Via holes against the built logo and name (bottom silkscreen group "Bristlemouth logo and board name"). New-frame mm.
Usage: <KiCad python> counters.py <board>
For every via whose hole (its drill) touches the box of the logo or of a text line: where the hole lies. Logo: on the drawn shape / in the eye /
in the open inside or outside. Text: pcbnew's own glyph outlines (TransformTextToPolySet); "counter" = a closed hole of a glyph (P, d, e, A, D, R, 0),
"on a stroke" = the centre is on ink, else "between strokes". Lists the tenting of each via."""
import sys, math, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); mm = pcbnew.ToMM; DX, DY = 113.47, 89.34
grp = [g for g in b.Groups() if g.GetName() == 'Bristlemouth logo and board name']; assert len(grp) == 1
items = [d for d in b.GetDrawings() if d.GetParentGroup() and d.GetParentGroup().GetName() == grp[0].GetName()]
vias = [(t.GetPosition(), t.GetDrill() / 2, t) for t in b.GetTracks() if t.GetClass() == 'PCB_VIA']
def ring(o): return [(o.CPoint(i).x, o.CPoint(i).y) for i in range(o.PointCount())]
def inside(p, x, y):
    c = False; n = len(p)
    for i in range(n):
        (x1, y1), (x2, y2) = p[i], p[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1): c = not c
    return c
def dist(p, x, y):
    best = 1e18; n = len(p)
    for i in range(n):
        (x1, y1), (x2, y2) = p[i], p[(i + 1) % n]; dx, dy = x2 - x1, y2 - y1; L = dx * dx + dy * dy; t = 0 if L == 0 else max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / L)); best = min(best, math.hypot(x - x1 - t * dx, y - y1 - t * dy))
    return best
rows = []; bad = 0
polys = sorted((ring(d.GetPolyShape().Outline(0)) for d in items if d.GetClass() == 'PCB_SHAPE'), key=len)
eye, body = polys[0], polys[1]
for d in items:
    bb = d.GetBoundingBox()
    if d.GetClass() == 'PCB_TEXT':
        ps = pcbnew.SHAPE_POLY_SET(); d.TransformTextToPolySet(ps, 0, 2000, pcbnew.ERROR_INSIDE); ps.Simplify()
        outs = [(ring(ps.Outline(i)), [ring(ps.Hole(i, h)) for h in range(ps.HoleCount(i))]) for i in range(ps.OutlineCount())]
        nh = sum(len(h) for o, h in outs)
    for pos, r, t in vias:
        if not (bb.GetLeft() - r <= pos.x <= bb.GetRight() + r and bb.GetTop() - r <= pos.y <= bb.GetBottom() + r): continue
        where = None
        if d.GetClass() == 'PCB_TEXT':
            for o, hs in outs:
                for h in hs:
                    if inside(h, pos.x, pos.y) or dist(h, pos.x, pos.y) < r: where = 'COUNTER of a letter'; bad += 1
            if not where: where = 'on a stroke' if any(inside(o, pos.x, pos.y) and not any(inside(h, pos.x, pos.y) for h in hs) for o, hs in outs) else 'between strokes'
            what = '"%s" (%d glyph outlines, %d counters)' % (d.GetText(), len(outs), nh)
        else:
            if d.GetPolyShape().Outline(0).PointCount() != len(body): continue
            if inside(eye, pos.x, pos.y) or dist(eye, pos.x, pos.y) < r: where = 'EYE'; bad += 1
            elif inside(body, pos.x, pos.y): where = 'on the drawn shape'
            else: where = 'open (inside or beside the outline)'
            what = 'logo'
        rows.append('   via (%.3f, %.3f) hole %.2f mm, %s, %s: %s, %s' % (mm(pos.x) - DX, mm(pos.y) - DY, mm(2 * r), t.GetNetname().split('/')[-1], 'tented' if t.IsTented(pcbnew.B_Mask) else 'NOT TENTED', what, where))
print('\n'.join(sorted(set(rows)))); print('vias under the logo and name: %d; in the eye or in a letter counter: %d' % (len(set(rows)), bad))
