"""Minimal reader for a KiCad `kicadsexpr` netlist (what `kicad-cli sch export netlist` writes).

Plain Python, no KiCad needed. Returns components (ref, value, footprint, sheet path + symbol uuid, dnp /
exclude-from-BOM flags, fields) and nets (name -> [(ref, pin)]).
"""
import re
from dataclasses import dataclass, field


def tokenize(text):
    # strings are double-quoted with backslash escapes; everything else splits on whitespace and parens
    for m in re.finditer(r'"((?:[^"\\]|\\.)*)"|([()])|([^\s()"]+)', text):
        if m.group(1) is not None:
            yield ("str", m.group(1).replace('\\"', '"').replace("\\\\", "\\"))
        elif m.group(2):
            yield ("par", m.group(2))
        else:
            yield ("sym", m.group(3))


def parse(text):
    """Return the nested list form of an s-expression file (strings and symbols both become str)."""
    stack = [[]]
    for kind, tok in tokenize(text):
        if kind == "par" and tok == "(":
            stack.append([])
        elif kind == "par":
            node = stack.pop()
            stack[-1].append(node)
        else:
            stack[-1].append(tok)
    assert len(stack) == 1, "unbalanced parentheses"
    return stack[0][0]


def children(node, key):
    return [c for c in node[1:] if isinstance(c, list) and c and c[0] == key]


def child(node, key, default=None):
    cs = children(node, key)
    return cs[0] if cs else default


def value(node, key, default=""):
    c = child(node, key)
    return c[1] if c and len(c) > 1 else default


@dataclass
class Component:
    ref: str
    value: str
    footprint: str
    path: str                      # "/<sheet uuids...>/<symbol uuid>" as KiCad's footprint path
    dnp: bool = False
    exclude_from_bom: bool = False
    datasheet: str = ""
    description: str = ""
    fields: dict = field(default_factory=dict)


def read(path):
    root = parse(open(path, encoding="utf-8").read())
    comps = []
    for c in children(child(root, "components"), "comp"):
        props = {p[1][1] if isinstance(p[1], list) else p[1] for p in children(c, "property")}
        # (property (name "dnp")) has the name nested; plain (property "x") not used here
        names = set()
        for p in children(c, "property"):
            n = child(p, "name")
            if n:
                names.add(n[1])
        sheet = child(c, "sheetpath")
        sheet_ts = value(sheet, "tstamps", "/") if sheet else "/"
        ts = value(c, "tstamps")
        fields = {}
        f = child(c, "fields")
        if f:
            for fl in children(f, "field"):
                fields[value(fl, "name")] = fl[2] if len(fl) > 2 else ""
        comps.append(Component(
            ref=value(c, "ref"), value=value(c, "value"), footprint=value(c, "footprint"),
            path=(sheet_ts.rstrip("/") + "/" + ts), dnp="dnp" in names,
            exclude_from_bom="exclude_from_bom" in names, datasheet=value(c, "datasheet"),
            description=value(c, "description"), fields=fields))
    nets = {}
    for n in children(child(root, "nets"), "net"):
        name = value(n, "name")
        nets[name] = [(value(nd, "ref"), value(nd, "pin")) for nd in children(n, "node")]
    return comps, nets


if __name__ == "__main__":
    import sys
    comps, nets = read(sys.argv[1])
    print(len(comps), "components,", len(nets), "nets")
    for c in comps[:3]:
        print(c)
