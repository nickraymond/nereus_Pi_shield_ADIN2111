"""Is the board built now the proposal Nick approved? Every silkscreen item (board texts and lines, footprint texts and graphics on the two silkscreen
layers) of the two boards, compared without their ids. Usage: <KiCad python> same_silk.py <approved scratch board> <new scratch board>"""
import sys, pcbnew
F, B = pcbnew.F_SilkS, pcbnew.B_SilkS
def items(path):
    b = pcbnew.LoadBoard(path); o = []
    def T(t, own): return ('text', own, t.GetText(), t.GetPosition().x, t.GetPosition().y, t.GetTextSize().x, t.GetTextSize().y, t.GetTextThickness(), t.GetTextAngleDegrees(), t.IsVisible(), t.GetLayer(), t.IsMirrored(), t.GetHorizJustify(), t.GetVertJustify(), t.GetFontName(), t.IsBold())
    def G(g, own): bb = g.GetBoundingBox(); return ('shape', own, g.GetShape(), g.GetLayer(), bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom(), g.GetWidth())
    for d in b.GetDrawings():
        if d.GetLayer() in (F, B): o.append(T(d, '') if d.GetClass() == 'PCB_TEXT' else G(d, ''))
    for f in b.GetFootprints():
        r = f.GetReference()
        for t in [f.Reference(), f.Value()] + [g for g in f.GraphicalItems() if g.GetClass() == 'PCB_TEXT']: o.append(T(t, r))
        for g in f.GraphicalItems():
            if g.GetClass() == 'PCB_SHAPE' and g.GetLayer() in (F, B): o.append(G(g, r))
    return sorted(map(repr, o))
a, c = items(sys.argv[1]), items(sys.argv[2]); d = sorted(set(a) ^ set(c))
print('silkscreen items and footprint texts: approved proposal %d, this build %d, different %d' % (len(a), len(c), len(d)))
for x in d[:10]: print('   !', x[:200])
print('SAME AS APPROVED', 'PASS' if a == c else 'FAIL'); sys.exit(0 if a == c else 1)
