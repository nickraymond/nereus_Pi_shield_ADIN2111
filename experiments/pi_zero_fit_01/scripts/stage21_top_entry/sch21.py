"""Stage 21: schematic fields of the connectors that became top-entry (text edit of the symbol block, nothing else in the file).
Usage: python3 sch21.py <board dir>
SOURCING is cleared too: its 'JLC stock (read ...)' was read for the side-entry part, not for this one."""
import sys, re, os
NOTE = 'top-entry variant: LCSC number not looked up'
EDIT = {('Nereus_Pi_Shield_Adin2111_TopLevel.kicad_sch', 'J9'): {
    'Value': 'BM04B-GHS', 'Footprint': 'Connector_JST:JST_GH_BM04B-GHS-TBT_1x04-1MP_P1.25mm_Vertical',
    'PLANNED MPN': 'BM04B-GHS-TBT', 'PLANNED LCSC': '', 'PLANNED NOTE': NOTE, 'SOURCING': ''}}
for (fn, ref), fields in EDIT.items():
    p = os.path.join(sys.argv[1], fn); s = open(p, encoding='utf-8').read()
    i = s.index('(property "Reference" "%s"' % ref); a = s.rindex('\n\t(symbol\n', 0, i); e = s.find('\n\t(symbol', i); e = len(s) if e < 0 else e
    blk = s[a:e]
    for k, v in fields.items():
        blk, n = re.subn(r'\(property "%s" "[^"]*"' % re.escape(k), '(property "%s" "%s"' % (k, v), blk)
        assert n == 1, (ref, k, n)
        print('  %s %s %s = %r' % (fn, ref, k, v))
    open(p, 'w', encoding='utf-8').write(s[:a] + blk + s[e:])
