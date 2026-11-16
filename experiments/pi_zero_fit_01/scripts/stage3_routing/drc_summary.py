"""Summarise a kicad-cli DRC JSON: errors by type, warnings by type, unconnected, parity.
Usage: python3 drc_summary.py <drc.json> [-v] [-vv] [-u]   (-v lists new errors, -vv all errors, -u unconnected items; new-frame mm)"""
import json, sys, collections
DX, DY = 113.47, 89.34
d = json.load(open(sys.argv[1])); v = '-v' in sys.argv
err = collections.Counter(); warn = collections.Counter()
for x in d.get('violations', []):
    (err if x['severity'] == 'error' else warn)[x['type']] += 1
print('errors %d: %s' % (sum(err.values()), dict(err)))
print('warnings %d: %s' % (sum(warn.values()), dict(warn)))
print('unconnected %d  parity %d' % (len(d.get('unconnected_items', [])), len(d.get('schematic_parity', []))))
def loc(i): return '(%.2f, %.2f)' % (i['pos']['x'] - DX, i['pos']['y'] - DY)
if v or '-u' in sys.argv:
    for x in (d.get('violations', []) if v else []):
        if x['severity'] == 'error' and x['type'] not in ('skew_out_of_range', 'items_not_allowed') or '-vv' in sys.argv and x['severity']=='error':
            print('E', x['type'], x['description'][:100], ' | '.join(i['description'][:70] + ' ' + loc(i) for i in x['items']))
    for x in (d.get('unconnected_items', []) if '-u' in sys.argv else []):
        print('U', ' | '.join(i['description'][:80] + ' ' + loc(i) for i in x['items']))
    for x in d.get('schematic_parity', []): print('P', x['description'])
if '-w' in sys.argv:
    for x in d.get('violations', []):
        if x['type'] in sys.argv: print('W', x['type'], ' | '.join(i['description'][:70] + ' ' + loc(i) for i in x['items']))
