"""List ERC items (kicad-cli json), one line per distinct item (type + item uuids), with how often each is reported."""
import json, sys, collections
e = json.load(open(sys.argv[1])); seen = collections.OrderedDict()
for s in e['sheets']:
    for v in s['violations']:
        key = (v['type'], tuple(sorted(i['uuid'] for i in v['items'])))
        if key not in seen: seen[key] = [('EXCL ' if v.get('excluded') else '') + v['severity'], s['path'], v['description'], [i['description'] for i in v['items']], 0]
        seen[key][4] += 1
print('reported %d, distinct %d' % (sum(x[4] for x in seen.values()), len(seen)))
print(collections.Counter((x[0], k[0]) for k, x in seen.items()))
for k, x in seen.items(): print('%-8s %-24s x%d %s | %s' % (x[0], k[0], x[4], x[1], ' ; '.join(x[3]))[:260])
