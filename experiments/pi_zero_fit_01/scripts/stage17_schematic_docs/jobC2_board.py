"""Stage 17, job C step 2: the board follows the new sub-sheet, as text (no pcbnew, so nothing else is rewritten).

Per moved footprint: (path) gets the sub-sheet UUID, (sheetname) / (sheetfile) name the sub-sheet. Nets local to the block
get the sub-sheet's prefix. Then the proof: the board before and after, with only those strings mapped back, are
byte-identical (so no track, via, zone, pad or footprint moved or changed).
Usage: python3 jobC2_board.py <board.kicad_pcb> <after netlist kicadxml>
"""
import re, sys
import xml.etree.ElementTree as ET
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent)); import sx

pcb = Path(sys.argv[1]); before = pcb.read_text(encoding='utf-8')
r = ET.parse(sys.argv[2]).getroot()
SUB = '/Top-Level Schematic/Motor + ADC/'; SUBFILE = 'Nereus_Pi_Shield_Adin2111_MotorADC.kicad_sch'
moved = {c.get('ref'): c.find('sheetpath').get('tstamps') + c.findtext('tstamps').strip()
         for c in r.iter('comp') if c.find('sheetpath').get('names') == SUB}
NETS = {'/Top-Level Schematic/' + n: SUB + n for n in ('MOTOR_OUT1', 'MOTOR_OUT2', 'MOTOR_VISEN', 'POT_WIPER')}
assert {n.get('name') for n in r.iter('net')} >= set(NETS.values())

out, i, done = [], 0, {}
for s, e, k, b in sx.items(before):
    if k != 'footprint': continue
    ref = re.search(r'\(property "Reference" "([^"]+)"', b).group(1)
    if ref not in moved: continue
    path = moved[ref][len('/30e82bf5-1344-486b-817c-02d3b0649ce4'):]     # the board path leaves out the root sheet
    b2, n1 = re.subn(r'\n\t\t\(path "[^"]+"\)', '\n\t\t(path "%s")' % path, b)
    b2, n2 = re.subn(r'\n\t\t\(sheetname "[^"]+"\)', '\n\t\t(sheetname "%s")' % SUB, b2)
    b2, n3 = re.subn(r'\n\t\t\(sheetfile "[^"]+"\)', '\n\t\t(sheetfile "%s")' % SUBFILE, b2)
    assert (n1, n2, n3) == (1, 1, 1), (ref, n1, n2, n3)
    out.append(before[i:s]); out.append(b2); i = e; done[ref] = path
out.append(before[i:]); after = ''.join(out)
assert sorted(done) == sorted(moved), sorted(set(moved) - set(done))
counts = {}
for a, z in NETS.items():
    counts[z] = after.count('(net "%s")' % a); after = after.replace('(net "%s")' % a, '(net "%s")' % z)
    assert after.count(a + '"') == 0, a
print('footprints relinked (%d): %s' % (len(done), ' '.join(sorted(done))))
print('net renames (items):', counts)

# proof: map the changed strings back and compare byte for byte
back = after
for a, z in NETS.items(): back = back.replace('(net "%s")' % z, '(net "%s")' % a)
la, lb = before.split('\n'), back.split('\n')
assert len(la) == len(lb), 'line count changed'
diff = [(x, y) for x, y in zip(la, lb) if x != y]
assert all(re.fullmatch(r'\t\t\((path|sheetname|sheetfile) "[^"]*"\)', y) for _, y in diff), 'other lines changed'
assert len(diff) == 3 * len(done), len(diff)
print('lines differing after mapping net names back: %d, all footprint path / sheetname / sheetfile of the %d moved parts'
      % (len(diff), len(done)))
print('PROOF: board before == board after, once net names and footprint path / sheetname / sheetfile are mapped back')
pcb.write_text(after, encoding='utf-8')
