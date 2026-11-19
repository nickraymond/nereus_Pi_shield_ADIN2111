"""Parse a KiCad s-expression netlist (kicad-cli sch export netlist) into parts and nets. Stdlib only."""
import re


def sexpr(text):
    tok = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+')
    stack, cur = [], []
    for m in tok.finditer(text):
        t = m.group(0)
        if t == "(":
            stack.append(cur)
            cur = []
        elif t == ")":
            done = cur
            cur = stack.pop()
            cur.append(done)
        else:
            cur.append(t[1:-1].replace('\\"', '"') if t.startswith('"') else t)
    return cur[0]


def find(node, key):
    return [c for c in node if isinstance(c, list) and c and c[0] == key]


def val(node, key, default=""):
    f = find(node, key)
    return (f[0][1] if len(f[0]) > 1 else "") if f else default


def load(path):
    """Return (parts, nets): parts[ref] = {value, footprint, fields{}, sheet}; nets[name] = sorted ['REF.pin', ...]."""
    root = sexpr(open(path, encoding="utf-8").read())
    parts = {}
    for c in find(find(root, "components")[0], "comp"):
        fields = {}
        for fs in find(c, "fields"):
            for f in find(fs, "field"):
                fields[val(f, "name")] = f[2] if len(f) > 2 else ""
        sheet = ""
        for p in find(c, "sheetpath"):
            sheet = val(p, "names")
        parts[val(c, "ref")] = {"value": val(c, "value"), "footprint": val(c, "footprint"), "fields": fields,
                                "sheet": sheet, "description": val(c, "description")}
    nets = {}
    for n in find(find(root, "nets")[0], "net"):
        nets[val(n, "name")] = sorted(val(x, "ref") + "." + val(x, "pin") for x in find(n, "node"))
    return parts, nets


def pinfuncs(path):
    root = sexpr(open(path, encoding="utf-8").read())
    out = {}
    for n in find(find(root, "nets")[0], "net"):
        for x in find(n, "node"):
            out[val(x, "ref") + "." + val(x, "pin")] = (val(n, "name"), val(x, "pinfunction"), val(x, "pintype"))
    return out
