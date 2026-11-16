"""Silkscreen warnings of a kicad-cli DRC JSON, split into ours / Sofar's. Usage: python3 split.py <drc.json> <silk report.json>
A warning is Sofar's when every footprint it names is one of the 81 locked ones; ours otherwise (our parts, board-level texts)."""
import json, sys, re, collections
d = json.load(open(sys.argv[1])); locked = set(json.load(open(sys.argv[2]))['locked'])
T = ('silk_overlap', 'silk_over_copper', 'silk_edge_clearance', 'text_height', 'text_thickness')
c = {'ours': collections.Counter(), 'sofar': collections.Counter()}
for v in d['violations']:
    if v['type'] not in T: continue
    refs = [m for i in v['items'] for m in re.findall(r'of ([A-Z]+\d+)', i['description'])]
    silk = [i for i in v['items'] if 'Overlay' in i['description'] or 'field' in i['description'] or 'text' in i['description'].lower()]
    srefs = [m for i in silk for m in re.findall(r'of ([A-Z]+\d+)', i['description'])] or refs
    who = 'sofar' if srefs and all(r in locked for r in srefs) and not any('PCB text' in i['description'] or i['description'].startswith('Text') for i in v['items']) else 'ours'
    c[who][v['type']] += 1
    if '-v' in sys.argv and who == 'ours': print(v['type'], ' | '.join(i['description'][:60] for i in v['items']))
for t in T: print('%-20s ours %3d   Sofar %3d' % (t, c['ours'][t], c['sofar'][t]))
