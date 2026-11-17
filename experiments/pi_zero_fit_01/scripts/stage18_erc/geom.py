"""Stage 18: connection points of a schematic sheet (symbol pin tips, wire ends, junctions, labels, no-connects, sheet pins),
read from the text. Standard library only."""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'stage17_schematic_docs')); import sx  # noqa: E402


def lib_pins(text):
    """{lib_id: [(unit, style, number, name, type, x, y, hidden)]} from the sheet's lib_symbols."""
    lb = next(b for _, _, k, b in sx.items(text) if k == 'lib_symbols')
    out = {}
    for m in re.finditer(r'\n\t\t\(symbol "((?:[^"\\]|\\.)*)"', lb):
        st = m.start() + 1; blk = lb[st:sx._close(lb, st + 2)]; name = m.group(1); pins = []
        for sm in re.finditer(r'\n\t\t\t\(symbol "((?:[^"\\]|\\.)*)_(\d+)_(\d+)"', blk):
            s2 = sm.start() + 1; sub = blk[s2:sx._close(blk, s2 + 2)]
            for pm in re.finditer(r'\(pin (\w+) \w+\s*\(at ([-\d.]+) ([-\d.]+) [-\d.]+\)', sub):
                s3 = pm.start(); pb = sub[s3:sx._close(sub, s3)]
                num = re.search(r'\(number "([^"]*)"', pb).group(1); nm = re.search(r'\(name "([^"]*)"', pb).group(1)
                hid = bool(re.search(r'^\t+\(hide yes\)', pb, re.M))
                pins.append((int(sm.group(2)), int(sm.group(3)), num, nm, pm.group(1), float(pm.group(2)), float(pm.group(3)), hid))
        out[name] = pins
    return out


def symbol_pins(text, libs=None):
    """[(ref, number, name, type, x, y, hidden)] for every placed symbol (pin tip in sheet coordinates)."""
    libs = libs or lib_pins(text); res = []
    for _, _, k, b in sx.items(text):
        if k != 'symbol': continue
        lid = re.search(r'\(lib_id "((?:[^"\\]|\\.)*)"\)', b).group(1)
        X, Y, R = map(float, re.search(r'\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\)', b).groups())
        unit = int(re.search(r'\(unit (\d+)\)', b).group(1)); mir = re.search(r'\(mirror (\w)\)', b)
        for u, st, num, nm, typ, px, py, hid in libs.get(lid, []):
            if u not in (0, unit) and unit != 0: continue
            if st not in (0, 1): continue
            x, y = px, -py
            if mir and mir.group(1) == 'x': y = -y
            if mir and mir.group(1) == 'y': x = -x
            r = int(round(R)) % 360
            for _ in range(r // 90): x, y = y, -x
            res.append((sx.ref(b), num, nm, typ, round(X + x, 4), round(Y + y, 4), hid))
    return res


def points(text):
    """connection points other than wires: {(x, y): [what]}"""
    pts = {}
    add = lambda p, w: pts.setdefault((round(p[0], 4), round(p[1], 4)), []).append(w)
    for r, num, nm, typ, x, y, hid in symbol_pins(text): add((x, y), 'pin %s.%s' % (r, num))
    for _, _, k, b in sx.items(text):
        if k in ('junction', 'no_connect', 'label', 'hierarchical_label', 'global_label'):
            add(sx.at(b), k + ' ' + (sx.label_name(b) or ''))
        if k == 'sheet':
            for pm in re.finditer(r'\(pin "([^"]*)" \w+\s*\(at ([-\d.]+) ([-\d.]+)', b): add((float(pm.group(2)), float(pm.group(3))), 'sheetpin ' + pm.group(1))
    return pts


def wires(text):
    return [(re.search(r'\(uuid "([^"]+)"\)', b).group(1), sx.pts(b)) for _, _, k, b in sx.items(text) if k == 'wire']


def on_seg(p, a, b, tol=1e-3):
    if abs(a[0] - b[0]) < tol: return abs(p[0] - a[0]) < tol and min(a[1], b[1]) - tol <= p[1] <= max(a[1], b[1]) + tol
    if abs(a[1] - b[1]) < tol: return abs(p[1] - a[1]) < tol and min(a[0], b[0]) - tol <= p[0] <= max(a[0], b[0]) + tol
    return False
