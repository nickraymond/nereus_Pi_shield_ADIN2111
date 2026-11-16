"""Stage 2c, step 4: silkscreen for J4's library footprint (outline, "+" and "GND", in the style of the library's other
WirePads footprint: 1 mm text, 0.15 mm thick), and the same graphics on the board's J4. Pads, courtyard, fab graphics and
position are not touched. Usage: <KiCad python> step4_j4_silk.py <board in> <board out>"""
import sys, uuid
from s3lib import *
NAME = 'WirePads_1x02_P3.20mm_Oval2.2x3.3mm_Drill1.1mm'
uid = lambda s: str(uuid.uuid5(uuid.NAMESPACE_URL, 'nereus/' + NAME + '/silk/' + s))    # stable, so a re-run gives the same file
HALF, LINE = (2.9, 1.85), 0.12              # outline between the fab outline (2.8, 1.75) and the courtyard (2.95, 1.9)
MARKS = (('+', -2.3, 2.65), ('GND', 4.6, -0.5))   # "+" under the south-west corner (pad 1), "GND" east of pad 2: the only free places on this board
def text(t, x, y):
    return ('\t(fp_text user "%s"\n\t\t(at %s %s 0)\n\t\t(layer "F.SilkS")\n\t\t(uuid "%s")\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1 1)\n\t\t\t\t(thickness 0.15)\n\t\t\t)\n\t\t)\n\t)\n' % (t, x, y, uid('text' + t)))
rect = ('\t(fp_rect\n\t\t(start %s %s)\n\t\t(end %s %s)\n\t\t(stroke\n\t\t\t(width %s)\n\t\t\t(type solid)\n\t\t)\n\t\t(fill no)\n\t\t(layer "F.SilkS")\n\t\t(uuid "%s")\n\t)\n'
        % (-HALF[0], -HALF[1], HALF[0], HALF[1], LINE, uid('rect')))
path = os.path.join(PROJ, 'nereus.pretty', NAME + '.kicad_mod'); s = open(path, encoding='utf-8').read()
assert '"F.SilkS")\n\t\t(uuid "%s")' % uid('rect') not in s, 'step 4 already applied to the library'
i = s.index('\t(fp_rect'); s = s[:i] + ''.join(text(*m) for m in MARKS) + rect + s[i:]
old = 'Origin midway between the pads, pad 1 at x -1.6.'
assert s.count(old) == 1; s = s.replace(old, old + ' Silkscreen: outline, + under the pad-1 corner, GND beside pad 2.')
open(path, 'w', encoding='utf-8').write(s); print('  wrote', path)
lf = lib_footprint('nereus:' + NAME)        # loads back: the file is valid

b = pcbnew.LoadBoard(sys.argv[1]); j4 = by_ref(b)['J4']
assert fpid_str(j4) == 'nereus:' + NAME and j4.GetOrientationDegrees() == 0 and not j4.IsFlipped()
sig = lambda f, o: sorted((p.GetNumber(), p.GetPosition().x - o.x, p.GetPosition().y - o.y, p.GetSize(pcbnew.F_Cu).x, p.GetSize(pcbnew.F_Cu).y, p.GetDrillSize().x, p.GetShape(pcbnew.F_Cu), p.GetAttribute()) for p in f.Pads())
before = sig(j4, j4.GetPosition()); assert before == sig(lf, lf.GetPosition()), 'library pads differ from the board'
o = j4.GetPosition(); assert not [g for g in j4.GraphicalItems() if g.GetLayer() == pcbnew.F_SilkS]
n_added = 0
for g in lf.GraphicalItems():
    if g.GetLayer() != pcbnew.F_SilkS: continue
    if g.GetClass() == 'PCB_SHAPE':
        n = pcbnew.PCB_SHAPE(j4); n.SetShape(pcbnew.SHAPE_T_RECT); n.SetStart(g.GetStart() + o); n.SetEnd(g.GetEnd() + o); n.SetWidth(g.GetWidth())
    else:
        n = pcbnew.PCB_TEXT(j4); n.SetText(g.GetText()); n.SetPosition(g.GetPosition() + o); n.SetTextSize(g.GetTextSize()); n.SetTextThickness(g.GetTextThickness())
    n.SetLayer(pcbnew.F_SilkS); j4.Add(n); n_added += 1
j4.SetLibDescription(lf.GetLibDescription())
assert n_added == 3 and sig(j4, j4.GetPosition()) == before and j4.GetPosition() == o
print('  board J4 at %s: pads unchanged; silkscreen outline, "+" and "GND" added' % (N(o),))
pcbnew.SaveBoard(sys.argv[2], b); print('saved', sys.argv[2])
