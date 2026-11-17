"""Semantic diff of a library symbol: embedded copy in a sheet vs the library file (pins, graphics, properties, flags)."""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'stage17_schematic_docs')); import sx

def parse(s):
    toks = re.findall(r'"(?:[^"\\]|\\.)*"|\(|\)|[^\s()"]+', s); i = 0
    def rd():
        nonlocal i
        t = toks[i]; i += 1
        if t == '(':
            l = []
            while toks[i] != ')': l.append(rd())
            i += 1; return l
        return t
    return rd()

def emb(f, full):
    t = open(f).read(); lb = [b for s, e, k, b in sx.items(t) if k == 'lib_symbols'][0]
    i = lb.index('\n\t\t(symbol "%s"' % full) + 3; return lb[i:sx._close(lb, i)]

def lib(f, name):
    t = open(f).read(); i = t.index('\n\t(symbol "%s"' % name) + 2; return t[i:sx._close(t, i)]

def flat(node, path=''):
    """leaf facts: path -> value, with sub-symbol and item names in the path"""
    out = []
    if isinstance(node, list):
        head = node[0] if node else ''
        key = head
        if head in ('symbol', 'property') and len(node) > 1: key += ' ' + node[1].replace('"', '')
        if head == 'pin': key += ' ' + ' '.join(str(x) for x in node[1:3])
        kids = [k for k in node[1:] if isinstance(k, list)]; atoms = [k for k in node[1:] if not isinstance(k, list)]
        if atoms and head not in ('symbol', 'property'): out.append((path + '/' + key, ' '.join(atoms)))
        if head == 'property': out.append((path + '/' + key, node[2] if len(node) > 2 else ''))
        if head == 'pin':
            nm = [k for k in kids if k[0] == 'number'][0][1]; key = 'pin #' + nm.replace('"', '')
            out.append((path + '/' + key + '/type', node[1] + ' ' + node[2]))
        for n, k in enumerate(kids): out += flat(k, path + '/' + key + ('' if head in ('pin', 'symbol', 'property') else '[%d]' % n))
    return out

if __name__ == '__main__':
    f, full, lf, name = sys.argv[1:5]
    a = emb(f, full).replace('"%s"' % full, '"%s"' % name)
    A = sorted(flat(parse(a))); B = sorted(flat(parse(lib(lf, name))))
    sa, sb = set(A), set(B)
    for x in sorted(sb - sa): print('  lib only:', x)
    for x in sorted(sa - sb): print('  sheet only:', x)
