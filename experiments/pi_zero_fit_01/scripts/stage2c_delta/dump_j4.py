import sys
from s3lib import *
b = pcbnew.LoadBoard(sys.argv[1]); j = by_ref(b)['J4']
print('J4 at', N(j.GetPosition()), j.GetOrientationDegrees(), j.IsFlipped(), fpid_str(j), 'locked', j.IsLocked())
for p in j.Pads(): print('  pad', p.GetNumber(), p.GetNetname(), pad_rect(p))
for g in j.GraphicalItems(): bb = g.GetBoundingBox(); print('  ', g.GetClass(), b.GetLayerName(g.GetLayer()), N(bb.GetOrigin()), N(bb.GetEnd()), g.GetText() if g.GetClass() == 'PCB_TEXT' else '')
for f in j.GetFields(): print('  field', f.GetName(), repr(f.GetText()[:50]), b.GetLayerName(f.GetLayer()), f.IsVisible(), N(f.GetPosition()))
x0, y0 = N(j.GetPosition())
print('near J4 (top side or through):')
for f in b.GetFootprints():
    bb = f.GetBoundingBox(False); r = (mm(bb.GetLeft()) - DX, mm(bb.GetTop()) - DY, mm(bb.GetRight()) - DX, mm(bb.GetBottom()) - DY)
    if f.GetReference() != 'J4' and rect_rect(r, (x0 - 3.5, y0 - 3.5, x0 + 3.5, y0 + 3.5)) == 0:
        print('  %-5s %s %s box %s' % (f.GetReference(), 'bot' if f.IsFlipped() else 'top', fpid_str(f)[:40], tuple(round(v, 2) for v in r)))
        for g in f.GraphicalItems():
            if g.GetLayer() in (pcbnew.F_SilkS,):
                bb = g.GetBoundingBox(); print('        silk', g.GetClass(), N(bb.GetOrigin()), N(bb.GetEnd()))
        for p in f.Pads():
            if p.IsOnLayer(pcbnew.F_Cu) and rect_rect(pad_rect(p), (x0 - 3.5, y0 - 3.5, x0 + 3.5, y0 + 3.5)) == 0: print('        pad', p.GetNumber(), tuple(round(v, 2) for v in pad_rect(p)))
for d in b.GetDrawings():
    bb = d.GetBoundingBox(); r = (mm(bb.GetLeft()) - DX, mm(bb.GetTop()) - DY, mm(bb.GetRight()) - DX, mm(bb.GetBottom()) - DY)
    if rect_rect(r, (x0 - 3.5, y0 - 3.5, x0 + 3.5, y0 + 3.5)) == 0 and d.GetLayer() != pcbnew.Edge_Cuts: print('  drawing', d.GetClass(), b.GetLayerName(d.GetLayer()), tuple(round(v, 2) for v in r), d.GetText() if hasattr(d, 'GetText') else '')
for z in b.Zones():
    bb = z.GetBoundingBox(); r = (mm(bb.GetLeft()) - DX, mm(bb.GetTop()) - DY, mm(bb.GetRight()) - DX, mm(bb.GetBottom()) - DY)
    if rect_rect(r, (x0 - 3.5, y0 - 3.5, x0 + 3.5, y0 + 3.5)) == 0 and r[2]-r[0] < 20: print('  zone', z.GetNetname(), z.GetIsRuleArea(), [b.GetLayerName(l) for l in z.GetLayerSet().Seq()][:4], tuple(round(v, 2) for v in r))
