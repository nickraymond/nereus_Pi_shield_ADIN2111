"""Warning and error counts per type, head -> now; names any type the head run does not have. Usage: python3 drcdiff.py <head drc.json> <drc.json>"""
import json, sys, collections
def cnt(p):
    c = collections.Counter()
    for v in json.load(open(p))['violations']: c[(v['severity'], v['type'])] += 1
    return c
a, b = cnt(sys.argv[1]), cnt(sys.argv[2])
for k in sorted(set(a) | set(b)):
    if a[k] != b[k]: print('   %s %s: %d -> %d%s' % (k[0], k[1], a[k], b[k], '   (NEW TYPE)' if not a[k] else ''))
print('   total: %d -> %d; new types: %s' % (sum(a.values()), sum(b.values()), [k[1] for k in b if not a[k]] or 'none'))
