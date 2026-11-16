"""Stage 11, job 3: J4's two holes 1.1 -> 1.3 mm round, pads unchanged (2.2 x 3.3 mm oval, plated, same places). Text edits, nothing else is rewritten:
  board      J4's footprint block: footprint name ...Drill1.1mm -> ...Drill1.3mm, the two (drill 1.1) lines, "1.1 mm plated hole" in the footprint's descr
  library    nereus.pretty/WirePads_1x02_P3.20mm_Oval2.2x3.3mm_Drill1.1mm.kicad_mod -> ...Drill1.3mm.kicad_mod with the same three changes (and its Value)
  schematic  J4's Footprint field on the Top-Level sheet (one line), so that the parity check finds the footprint the board has
Not changed: J4's Description field (schematic and board), which still reads "1.1 mm hole".
Usage: python3 j4_holes.py <board.kicad_pcb> <nereus.pretty> <Top-Level sheet.kicad_sch>"""
import sys, os
PCB, LIB, SCH = sys.argv[1:4]; OLD = 'WirePads_1x02_P3.20mm_Oval2.2x3.3mm_Drill1.1mm'; NEW = 'WirePads_1x02_P3.20mm_Oval2.2x3.3mm_Drill1.3mm'
def edit(blk, where):
    assert blk.count('(drill 1.1)') == 2 and blk.count('(size 2.2 3.3)') == 2 and blk.count('thru_hole oval') == 2 and blk.count('1.1 mm plated hole') == 1, where
    return blk.replace('(drill 1.1)', '(drill 1.3)').replace('1.1 mm plated hole', '1.3 mm plated hole').replace(OLD, NEW)
t = open(PCB, encoding='utf-8').read(); assert t.count('nereus:' + OLD) == 1
a = t.index('\t(footprint "nereus:%s"' % OLD); e = t.index('\n\t)\n', a) + 4; blk = t[a:e]; assert '(property "Reference" "J4"' in blk and blk.count(OLD) == 1
t = t[:a] + edit(blk, 'board') + t[e:]; open(PCB, 'w', encoding='utf-8').write(t)
m = open(os.path.join(LIB, OLD + '.kicad_mod'), encoding='utf-8').read(); assert m.count(OLD) == 2
open(os.path.join(LIB, NEW + '.kicad_mod'), 'w', encoding='utf-8').write(edit(m, 'library')); os.remove(os.path.join(LIB, OLD + '.kicad_mod'))
s = open(SCH, encoding='utf-8').read(); line = '(property "Footprint" "nereus:%s"' % OLD; assert s.count(line) == 1 and s.count(OLD) == 1
open(SCH, 'w', encoding='utf-8').write(s.replace(line, line.replace(OLD, NEW)))
print('J4: board footprint block (name, 2 drills, descr), library file renamed to %s.kicad_mod, schematic Footprint field: edited' % NEW)
