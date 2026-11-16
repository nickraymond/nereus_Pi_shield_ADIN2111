"""Gate numbers from kicad-cli's JSON reports. Usage: python3 drc_summary.py <drc in> <drc out> <erc in> <erc out>"""
import json, sys, collections
a, c = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))
def cnt(d, k, sev=None): return collections.Counter(v['type'] for v in d[k] if sev is None or v['severity'] == sev)
print('schematic parity: in %d -> out %d %s' % (len(a['schematic_parity']), len(c['schematic_parity']), dict(cnt(c, 'schematic_parity')) or ''))
for v in c['schematic_parity']: print('    ', v['type'], v['description'], [i['description'] for i in v['items']])
print('errors: in %s -> out %s' % (dict(cnt(a, 'violations', 'error')), dict(cnt(c, 'violations', 'error'))))
print('unconnected: in %d -> out %d' % (len(a['unconnected_items']), len(c['unconnected_items'])))
wa, wc = cnt(a, 'violations', 'warning'), cnt(c, 'violations', 'warning')
print('warnings: in %d -> out %d; changes: %s' % (sum(wa.values()), sum(wc.values()), {k: '%d -> %d' % (wa[k], wc[k]) for k in sorted(set(wa) | set(wc)) if wa[k] != wc[k]} or 'none'))
import re
key = lambda v: (v['type'], re.sub(r'actual.*', '', v['description']), tuple(sorted(i['description'] for i in v['items'])))   # measured values wobble between runs
ka = collections.Counter(key(v) for v in a['violations'])
new = [v for v in c['violations'] if not ka.get(key(v))]
print('violations not in the input report, by type and items (%d): %s' % (len(new), dict(collections.Counter(v['severity'] + ' ' + v['type'] for v in new))))
for v in new: print('    %-8s %-24s %s | %s' % (v['severity'], v['type'], v['description'][:90], ' / '.join(i['description'][:70] for i in v['items'])))
e0, e1 = json.load(open(sys.argv[3])), json.load(open(sys.argv[4]))
ek = lambda e: collections.Counter((v['type'], v['description'], tuple(sorted(i['description'] for i in v['items']))) for s in e['sheets'] for v in s['violations'])
print('ERC: in %d -> out %d; same items: %s' % (sum(ek(e0).values()), sum(ek(e1).values()), ek(e0) == ek(e1)))
