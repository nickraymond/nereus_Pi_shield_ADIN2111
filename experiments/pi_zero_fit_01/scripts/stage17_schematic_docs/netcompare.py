"""Compare two kicadxml netlists: connectivity as sets of (ref, pin) per net, names ignored; then list renamed nets and
components whose sheet changed. Exit 1 if the connectivity differs.  Usage: python3 netcompare.py <before.xml> <after.xml>"""
import sys
import xml.etree.ElementTree as ET


def load(p):
    r = ET.parse(p).getroot()
    nets = {n.get('name'): frozenset((x.get('ref'), x.get('pin')) for x in n.iter('node')) for n in r.iter('net')}
    comps = {c.get('ref'): (c.findtext('value'), c.findtext('footprint'), c.find('sheetpath').get('names'),
                            c.find('sheetpath').get('tstamps'), c.findtext('tstamps')) for c in r.iter('comp')}
    return nets, comps


(na, ca), (nb, cb) = load(sys.argv[1]), load(sys.argv[2])
sa, sb = set(na.values()), set(nb.values())
print('nets before %d, after %d; connectivity identical (pad sets): %s' % (len(sa), len(sb), sa == sb))
for s in sa - sb: print('  only before:', sorted(s)[:8])
for s in sb - sa: print('  only after:', sorted(s)[:8])
inv = {v: k for k, v in nb.items()}
ren = sorted((k, inv[v]) for k, v in na.items() if v in inv and inv[v] != k)
print('renamed nets (%d):' % len(ren)); [print('  %s -> %s' % r) for r in ren]
print('components before %d, after %d; same refs: %s' % (len(ca), len(cb), set(ca) == set(cb)))
moved = sorted(r for r in ca if r in cb and ca[r][2] != cb[r][2])
same_vf = all(ca[r][:2] == cb[r][:2] and ca[r][4] == cb[r][4] for r in ca if r in cb)
print('value / footprint / symbol uuid unchanged for every part: %s' % same_vf)
print('parts whose sheet changed (%d): %s' % (len(moved), ' '.join(moved)))
other = sorted(r for r in ca if r in cb and r not in moved and ca[r] != cb[r])
print('other parts with any change:', other or 'none')
sys.exit(0 if sa == sb and set(ca) == set(cb) and same_vf else 1)
