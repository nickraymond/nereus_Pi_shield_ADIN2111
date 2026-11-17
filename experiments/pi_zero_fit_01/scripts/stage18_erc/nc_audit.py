"""List every pin that is alone on its net (netlist), with its sheet, position and whether a no-connect flag sits on it.
Usage: python3 nc_audit.py <board dir> <netlist kicadxml>"""
import sys, glob, os, re
import xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import geom
from geom import sx
D = sys.argv[1]; r = ET.parse(sys.argv[2]).getroot()
alone = [(n.get('name'), x.get('ref'), x.get('pin'), x.get('pinfunction'), x.get('pintype')) for n in r.iter('net') for x in [list(n.iter('node'))] if len(x) == 1 for x in x]
where = {}
for f in glob.glob(D + '/*.kicad_sch'):
    t = open(f).read(); nc = {(round(sx.at(b)[0], 3), round(sx.at(b)[1], 3)) for _, _, k, b in sx.items(t) if k == 'no_connect'}
    for ref, num, nm, typ, x, y, hid in geom.symbol_pins(t):
        where[(ref, num)] = (os.path.basename(f).replace('Nereus_Pi_Shield_Adin2111', '').replace('.kicad_sch', '') or 'cover', x, y, hid, (round(x, 3), round(y, 3)) in nc)
missing = []
for name, ref, pin, fn, typ in sorted(alone, key=lambda a: (a[1], a[2])):
    w = where.get((ref, pin), ('?', 0, 0, False, False))
    print('%-6s %-4s %-28s %-12s %-14s (%.2f, %.2f)%s  %s' % (ref, pin, fn, typ, w[0], w[1], w[2], ' hidden' if w[3] else '', 'NC flag' if w[4] else 'NO FLAG'))
    if not w[4]: missing.append((ref, pin, w))
print('alone on their net: %d; without a no-connect flag: %d' % (len(alone), len(missing)))
