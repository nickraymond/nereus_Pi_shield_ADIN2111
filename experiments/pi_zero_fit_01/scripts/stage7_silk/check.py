"""The scratch board against the repo board: copper, pads, footprint places and outline must be identical; the silkscreen texts of the locked
(Sofar) footprints must be identical. Usage: <KiCad python> check.py <repo board> <scratch board> <silk report.json>"""
import sys, json, pcbnew
A, Bd = pcbnew.LoadBoard(sys.argv[1]), pcbnew.LoadBoard(sys.argv[2]); locked = set(json.load(open(sys.argv[3]))['locked'])
def copper(b):
    tr = sorted((t.GetClass(), t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y, t.GetWidth() if t.GetClass() != 'PCB_VIA' else t.GetWidth(pcbnew.F_Cu), t.GetLayer(), t.GetNetname(),
                 t.GetDrill() if t.GetClass() == 'PCB_VIA' else 0) for t in b.GetTracks())
    zn = sorted((z.GetZoneName(), z.GetNetname(), z.GetLayerSet().FmtHex(), z.Outline().Format(False), z.GetFilledArea() if hasattr(z, 'GetFilledArea') else 0) for z in b.Zones())
    pads = sorted((f.GetReference(), p.GetNumber(), p.GetPosition().x, p.GetPosition().y, p.GetSize().x, p.GetSize().y, p.GetNetname(), p.GetLayerSet().FmtHex(), p.GetDrillSize().x, p.GetOrientationDegrees()) for f in b.GetFootprints() for p in f.Pads())
    fp = sorted((f.GetReference(), f.GetPosition().x, f.GetPosition().y, f.GetOrientationDegrees(), f.IsFlipped(), f.GetFPID().GetUniStringLibItemName(), f.GetValue()) for f in b.GetFootprints())
    edge = sorted((d.GetClass(), d.GetShape(), d.GetStart().x, d.GetStart().y, d.GetEnd().x, d.GetEnd().y, d.GetWidth()) for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts)
    cu = sorted((d.GetClass(), d.GetLayer(), d.GetBoundingBox().GetLeft(), d.GetBoundingBox().GetTop(), d.GetBoundingBox().GetRight(), d.GetBoundingBox().GetBottom()) for d in b.GetDrawings() if pcbnew.IsCopperLayer(d.GetLayer()))
    fpg = sorted((f.GetReference(), g.GetClass(), g.GetLayer(), g.GetBoundingBox().GetLeft(), g.GetBoundingBox().GetTop(), g.GetBoundingBox().GetRight(), g.GetBoundingBox().GetBottom())
                 for f in b.GetFootprints() for g in f.GraphicalItems() if g.GetClass() != 'PCB_TEXT' or f.GetReference() in locked)
    return {'tracks + vias': tr, 'zones': zn, 'pads': pads, 'footprints': fp, 'outline items': edge, 'copper drawings': cu, 'footprint graphics (texts of ours left out)': fpg}
ca, cb = copper(A), copper(Bd); bad = 0
for k in ca:
    same = ca[k] == cb[k]; bad += not same; print('%-45s repo %4d  scratch %4d  %s' % (k, len(ca[k]), len(cb[k]), 'identical' if same else 'DIFFERENT'))
def texts(b):
    o = {}
    for f in b.GetFootprints():
        if f.GetReference() not in locked: continue
        for i, t in enumerate([f.Reference(), f.Value()] + sorted((g for g in f.GraphicalItems() if g.GetClass() == 'PCB_TEXT'), key=lambda g: (g.GetText(), g.GetPosition().x, g.GetPosition().y))):
            o[(f.GetReference(), i)] = (t.GetText(), t.GetPosition().x, t.GetPosition().y, t.GetTextSize().x, t.GetTextSize().y, t.GetTextThickness(), t.GetTextAngleDegrees(), t.IsVisible(), t.GetLayer(), t.IsMirrored(),
                                         t.GetHorizJustify(), t.GetVertJustify(), t.GetFontName() if hasattr(t, 'GetFontName') else '')
    return o
ta, tb = texts(A), texts(Bd); diff = [k for k in ta if ta[k] != tb.get(k)] + [k for k in tb if k not in ta]
print("Sofar's texts (locked footprints %d): %d texts compared (text, place, size, line, angle, visible, layer, mirror, justify, font), %d different %s" % (len(locked), len(ta), len(diff), diff[:5]))
print('CHECK', 'PASS' if not bad and not diff else 'FAIL')
