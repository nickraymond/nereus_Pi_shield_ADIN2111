"""Stage 18: the board's pads follow the corrected pin types (pintype is copied from the symbol); text level.
Proof: only the (pintype ...) lines of these pads change.  Usage: python3 board_sync.py <board.kicad_pcb>"""
import re, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage17_schematic_docs')); import sx
CH = {('U5', '2'): 'power_out', ('U5', '6'): 'passive', ('U10', '2'): 'power_out', ('U10', '6'): 'passive', ('U6', 'B2'): 'power_out'}
p = sys.argv[1]; t = open(p, encoding='utf-8').read(); out = []; i = 0; done = []
for s, e, k, b in sx.items(t):
    if k != 'footprint': continue
    ref = re.search(r'\(property "Reference" "([^"]+)"', b).group(1)
    if ref not in {r for r, _ in CH}: continue
    def fix(m):
        pad = m.group(0); num = re.match(r'\(pad "([^"]+)"', pad).group(1)
        if (ref, num) not in CH: return pad
        new, n = re.subn(r'\(pintype "[^"]+"\)', '(pintype "%s")' % CH[(ref, num)], pad); assert n == 1
        done.append((ref, num, re.search(r'\(pintype "([^"]+)"\)', pad).group(1), CH[(ref, num)])); return new
    b2 = re.sub(r'\(pad "[^"]+"[\s\S]*?\n\t\t\)', fix, b)
    out += [t[i:s], b2]; i = e
out.append(t[i:]); new = ''.join(out)
assert sorted((r, n) for r, n, _, _ in done) == sorted(CH), done
la, lb = t.split('\n'), new.split('\n'); diff = [(x, y) for x, y in zip(la, lb) if x != y]
assert len(la) == len(lb) and all('(pintype ' in y for _, y in diff), diff
print('board pads retyped:', done, '; lines changed:', len(diff), '(pintype only)')
open(p, 'w', encoding='utf-8').write(new)
