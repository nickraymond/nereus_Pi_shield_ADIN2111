"""Step 4: J4's stage-1 footprint (two oblong through-hole pads) becomes a library footprint, and the schematic points at it.
 a) writes nereus.pretty/WirePads_1x02_P3.20mm_Oval2.2x3.3mm_Drill1.1mm.kicad_mod (pads exactly as on the board);
 b) sets J4's Footprint field in the Top-Level sheet (the only schematic edit of this stage);
 c) adds the library footprint's fab outline and fab polarity marks to J4 on the board (no pad, position or copper change).
Usage: <KiCad python> step4_j4_footprint.py <board in> <board out>"""
import sys, re, uuid
from s3lib import *
NAME = 'WirePads_1x02_P3.20mm_Oval2.2x3.3mm_Drill1.1mm'; OLD = 'nereus:WirePads_1x02_P3.81mm_Oval4.2x2.6mm_Drill1.3mm'
DESCR = ('Two through-hole wire pads for soldering leads directly to the board, no connector. Oval pads 2.2 x 3.3 mm, 1.1 mm plated hole, '
         '3.2 mm pitch, side by side. Origin midway between the pads, pad 1 at x -1.6. Made for J4, AUX 5 V in, Pi Zero fit experiment (2026-11-15)')
TAGS = 'wire pads solder lead through hole 2 pin'
CY, FAB = (2.95, 1.9), (2.8, 1.75)       # half sizes: courtyard as stage 1 drew it on the board; fab outline 0.1 mm outside the pads
uid = lambda s: str(uuid.uuid5(uuid.NAMESPACE_URL, 'nereus/' + NAME + '/' + s))    # stable, so a re-run gives the same file
def prop(n, v, x, y, layer, hide=False, size=1.0):
    return ('\t(property "%s" "%s"\n\t\t(at %s %s 0)\n\t\t(layer "%s")\n%s\t\t(uuid "%s")\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size %s %s)\n\t\t\t\t(thickness 0.15)\n\t\t\t)\n\t\t)\n\t)\n'
            % (n, v, x, y, layer, '\t\t(hide yes)\n' if hide else '', uid('prop' + n), size, size))
def text(t, x, y):
    return ('\t(fp_text user "%s"\n\t\t(at %s %s 0)\n\t\t(layer "F.Fab")\n\t\t(uuid "%s")\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 0.6 0.6)\n\t\t\t\t(thickness 0.1)\n\t\t\t)\n\t\t)\n\t)\n' % (t, x, y, uid('text' + t)))
def rect(h, w, layer):
    return ('\t(fp_rect\n\t\t(start %s %s)\n\t\t(end %s %s)\n\t\t(stroke\n\t\t\t(width %s)\n\t\t\t(type solid)\n\t\t)\n\t\t(fill no)\n\t\t(layer "%s")\n\t\t(uuid "%s")\n\t)\n'
            % (-h[0], -h[1], h[0], h[1], w, layer, uid('rect' + layer)))
def pad(n, x):
    return ('\t(pad "%s" thru_hole oval\n\t\t(at %s 0)\n\t\t(size 2.2 3.3)\n\t\t(drill 1.1)\n\t\t(layers "*.Cu" "*.Mask")\n\t\t(remove_unused_layers no)\n\t\t(uuid "%s")\n\t)\n' % (n, x, uid('pad' + n)))
mod = ('(footprint "%s"\n\t(version 20241229)\n\t(generator "nereus_tools")\n\t(layer "F.Cu")\n\t(descr "%s")\n\t(tags "%s")\n' % (NAME, DESCR, TAGS)
       + prop('Reference', 'REF**', 0, -2.7, 'F.SilkS') + prop('Value', NAME, 0, 2.8, 'F.Fab') + prop('Datasheet', '', 0, 0, 'F.Fab', True, 1.27)
       + prop('Description', '', 0, 0, 'F.Fab', True, 1.27) + '\t(attr through_hole exclude_from_pos_files exclude_from_bom)\n'
       + text('+', -1.6, -1.2) + text('GND', 1.6, -1.2) + rect(CY, 0.05, 'F.CrtYd') + rect(FAB, 0.1, 'F.Fab') + pad('1', -1.6) + pad('2', 1.6)
       + '\t(embedded_fonts no)\n)\n')
path = os.path.join(PROJ, 'nereus.pretty', NAME + '.kicad_mod'); open(path, 'w', encoding='utf-8').write(mod); print('  wrote', path)
lf = lib_footprint('nereus:' + NAME)        # loads back: the file is valid

# b) the schematic field
sch = os.path.join(PROJ, 'Nereus_Pi_Shield_Adin2111_TopLevel.kicad_sch'); s = open(sch, encoding='utf-8').read()
i = s.index('(property "Reference" "J4"'); j = s.index('(property "Footprint" "', i); k = s.index('\n', j)
assert s.count('(property "Reference" "J4"') == 1 and j - i < 1500
line = s[j:k]
if OLD in line:
    s = s[:j] + line.replace(OLD, 'nereus:' + NAME) + s[k:]; open(sch, 'w', encoding='utf-8').write(s); print('  schematic J4 Footprint: %s -> nereus:%s' % (OLD, NAME))
else: assert ('nereus:' + NAME) in line, line; print('  schematic J4 Footprint already set')

# c) the board's J4: same pads as the library? then add the library's fab graphics
b = pcbnew.LoadBoard(sys.argv[1]); j4 = by_ref(b)['J4']
assert fpid_str(j4) == 'nereus:' + NAME and j4.GetOrientationDegrees() == 0 and not j4.IsFlipped()
sig = lambda f, o: sorted((p.GetNumber(), p.GetPosition().x - o.x, p.GetPosition().y - o.y, p.GetSize(pcbnew.F_Cu).x, p.GetSize(pcbnew.F_Cu).y, p.GetDrillSize().x, p.GetShape(pcbnew.F_Cu), p.GetAttribute()) for p in f.Pads())
assert sig(j4, j4.GetPosition()) == sig(lf, lf.GetPosition()), 'library pads differ from the board'
o = j4.GetPosition(); has = {(g.GetClass(), g.GetLayer()) for g in j4.GraphicalItems()}
assert ('PCB_SHAPE', pcbnew.F_CrtYd) in has and ('PCB_SHAPE', pcbnew.F_Fab) not in has
for g in lf.GraphicalItems():
    if g.GetLayer() != pcbnew.F_Fab: continue
    if g.GetClass() == 'PCB_SHAPE':
        n = pcbnew.PCB_SHAPE(j4); n.SetShape(pcbnew.SHAPE_T_RECT); n.SetStart(g.GetStart() + o); n.SetEnd(g.GetEnd() + o); n.SetWidth(g.GetWidth())
    else:
        n = pcbnew.PCB_TEXT(j4); n.SetText(g.GetText()); n.SetPosition(g.GetPosition() + o); n.SetTextSize(g.GetTextSize()); n.SetTextThickness(g.GetTextThickness())
    n.SetLayer(pcbnew.F_Fab); j4.Add(n)
j4.SetLibDescription(DESCR); j4.SetKeywords(TAGS)
print('  board J4 at %s: pads match the library; fab outline and "+" / "GND" fab marks added' % (N(o),))
pcbnew.SaveBoard(sys.argv[2], b); print('saved', sys.argv[2])
