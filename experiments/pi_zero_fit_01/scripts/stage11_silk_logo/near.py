"""DRC items inside the logo-and-name box (+ 0.5 mm). Usage: python3 near.py <drc.json> <logo report.json>"""
import json, sys, collections
d = json.load(open(sys.argv[1])); x0, y0, x1, y1 = json.load(open(sys.argv[2]))['group_box']; c = collections.Counter(); rows = []
for v in d['violations']:
    if any(x0 - .5 <= i['pos']['x'] - 113.47 <= x1 + .5 and y0 - .5 <= i['pos']['y'] - 89.34 <= y1 + .5 for i in v['items']):
        c[v['type']] += 1; rows.append('   %s: %s' % (v['type'], ' | '.join(i['description'][:70] for i in v['items'])))
print('DRC items at the logo and name (box x %.2f..%.2f, y %.2f..%.2f + 0.5 mm): %s' % (x0, x1, y0, y1, dict(c) or 'none')); print('\n'.join(rows))
