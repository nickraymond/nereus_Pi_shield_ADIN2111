#!/usr/bin/env python3
"""Small text edits on KiCad 9 .kicad_sch files, in the format KiCad writes.

Library of functions used by sprint edits (not a CLI). Every edit returns new
text; callers write files and then verify with tools/check.sh (kicad-cli must
load the result, netcheck must show only the intended change).

  delete(text, refs, labels)     remove parts/labels, then clean up what they
                                 leave behind on the same wire islands:
                                 power symbols and no-connect flags with
                                 nothing else to connect to, dead wires, dead
                                 stubs, and junctions with < 3 connections
  ensure_lib_symbol(text, lib_id, kicad_sym_path)
  add_symbol(text, lib_id, ref, value, x, y, ...)
  add_wire / add_no_connect / add_label
  next_ref(texts, prefix)
  copy_block(text, box, dx, dy, ref_map, label_map, new_power_ref)
                                 duplicate a boxed circuit with new refs,
                                 renamed labels and fresh uuids
  set_properties(text, ref, values, drop, keep_only)

Python standard library only.
"""
import collections
import math
import re
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from midwire import JUNCTION, WIRE, fmt, on_interior, symbol_pins  # noqa: E402
from netcheck import blocks  # noqa: E402

SHEET_PIN = re.compile(r'\(pin "([^"]+)" \w+\n\t\t\t\(at ([-\d.]+) ([-\d.]+)')
LABEL = re.compile(r'\t\((label|global_label|hierarchical_label) "([^"]+)"\n(?:\t\t\(shape \w+\)\n)?'
                   r'\t\t\(at ([-\d.]+) ([-\d.]+)[^\n]*\n.*?\n\t\)\n', re.S)
PROP = re.compile(r'\t\t\(property "([^"]+)" "((?:[^"\\]|\\.)*)"\n(?:\t\t\t[^\n]*\n)*\t\t\)\n')
NO_CONNECT = re.compile(r'\t\(no_connect\n\t\t\(at ([-\d.]+) ([-\d.]+)\)\n.*?\n\t\)\n', re.S)


def _key(x, y):
    return (round(float(x), 3), round(float(y), 3))


def top_level(text, kind):
    """Yield (start, end, block) for each top-level '\\t(kind' item (block includes its newline)."""
    for m in re.finditer(r'^\t\(' + re.escape(kind) + r'\b', text, re.M):
        end = text.index("\n\t)\n", m.start()) + 4
        yield m.start(), end, text[m.start():end]


def symbol_ref(block):
    m = re.search(r'\(property "Reference" "([^"]+)"', block)
    return m.group(1) if m else None


def _remove_spans(text, spans):
    for s, e in sorted(spans, reverse=True):
        text = text[:s] + text[e:]
    return text


class Graph:
    """Wire islands of one sheet and the items attached to each."""

    def __init__(self, text):
        self.wires = [(m.start(), m.end(), tuple(map(float, m.groups()[:4]))) for m in WIRE.finditer(text)]
        self.parent = {}
        for i, (_, _, w) in enumerate(self.wires):
            self._union(("w", i), _key(w[0], w[1]))
            self._union(("w", i), _key(w[2], w[3]))
        # a wire end, or a junction, on another wire's interior joins the two
        points = [(w[0], w[1]) for _, _, w in self.wires] + [(w[2], w[3]) for _, _, w in self.wires]
        points += [tuple(map(float, j)) for j in JUNCTION.findall(text)]
        for x, y in points:
            for i, (_, _, w) in enumerate(self.wires):
                if on_interior(x, y, *w):
                    self._union(("w", i), _key(x, y))
        self.items = collections.defaultdict(list)  # island root -> [(kind, name)]
        for ref, num, x, y in symbol_pins(text):
            self._attach(x, y, ("pin", f"{ref}.{num}"))
        for m in LABEL.finditer(text):
            self._attach(float(m.group(3)), float(m.group(4)), ("label", m.group(2)))
        for _, _, sheet in top_level(text, "sheet"):
            for name, x, y in SHEET_PIN.findall(sheet):
                self._attach(float(x), float(y), ("sheetpin", name))
        for m in NO_CONNECT.finditer(text):
            self._attach(float(m.group(1)), float(m.group(2)), ("nc", fmt(float(m.group(1))) + "," + fmt(float(m.group(2)))))

    def _find(self, a):
        self.parent.setdefault(a, a)
        while self.parent[a] != a:
            self.parent[a] = self.parent[self.parent[a]]
            a = self.parent[a]
        return a

    def _union(self, a, b):
        self.parent[self._find(a)] = self._find(b)

    def _attach(self, x, y, item):
        k = _key(x, y)
        if k not in self.parent:
            for i, (_, _, w) in enumerate(self.wires):
                if on_interior(x, y, *w):
                    self._union(("w", i), k)
                    break
        self.items[self._find(k)].append(item)

    def island_of_wire(self, i):
        return self._find(("w", i))

    def islands(self):
        out = collections.defaultdict(lambda: {"wires": [], "items": []})
        for i in range(len(self.wires)):
            out[self.island_of_wire(i)]["wires"].append(i)
        for root, items in self.items.items():
            out[self._find(root)]["items"] += items
        return out


def _is_power_ref(name):
    return name.startswith("#")


def delete(text, refs=(), labels=()):
    """Delete parts and labels, then clean up their islands. Returns (text, report dict)."""
    refs, labels = set(refs), set(labels)
    g = Graph(text)

    def doomed(item):
        kind, name = item
        return (kind == "pin" and name.rsplit(".", 1)[0] in refs) or (kind == "label" and name in labels)

    affected = {root: isl for root, isl in g.islands().items() if any(doomed(i) for i in isl["items"])}
    report = {"parts": [], "labels": [], "power_symbols": [], "no_connects": 0, "wires": 0, "junctions": 0}
    drop_refs, drop_nc, drop_wires = set(refs), set(), set()
    for isl in affected.values():
        left = [i for i in isl["items"] if not doomed(i)]
        anchors = [i for i in left if not (i[0] == "nc" or (i[0] == "pin" and _is_power_ref(i[1])))]
        if not anchors:  # nothing real remains: the whole island goes
            drop_wires.update(isl["wires"])
            for kind, name in left:
                if kind == "pin":
                    drop_refs.add(name.rsplit(".", 1)[0])
                elif kind == "nc":
                    drop_nc.add(name)
    # spans to remove
    spans = []
    for s, e, b in top_level(text, "symbol"):
        r = symbol_ref(b)
        if r in drop_refs:
            spans.append((s, e))
            report["power_symbols" if _is_power_ref(r) else "parts"].append(r)
    for m in LABEL.finditer(text):
        if m.group(1) == "label" and m.group(2) in labels:
            spans.append((m.start(), m.end()))
            report["labels"].append(m.group(2))
    for m in NO_CONNECT.finditer(text):
        if fmt(float(m.group(1))) + "," + fmt(float(m.group(2))) in drop_nc:
            spans.append((m.start(), m.end()))
            report["no_connects"] += 1
    for i in drop_wires:
        spans.append(g.wires[i][:2])
    report["wires"] += len(drop_wires)
    text = _remove_spans(text, spans)
    # trim dead stubs left on surviving affected islands
    region = {_key(w[0], w[1]) for i in range(len(g.wires)) if g.island_of_wire(i) in affected
              for w in [g.wires[i][2]]} | {_key(w[2], w[3]) for i in range(len(g.wires))
                                           if g.island_of_wire(i) in affected for w in [g.wires[i][2]]}
    while True:
        text, n = _trim_stubs(text, region)
        report["wires"] += n
        if not n:
            break
    text, report["junctions"] = _drop_weak_junctions(text, region)
    for key in ("parts", "labels", "power_symbols"):
        report[key].sort()
    return text, report


def _connection_points(text):
    """Counter of how many things connect at each point (pins, labels, sheet pins, NCs, wire ends)."""
    c = collections.Counter()
    for _, _, x, y in symbol_pins(text):
        c[_key(x, y)] += 1
    for m in LABEL.finditer(text):
        c[_key(m.group(3), m.group(4))] += 1
    for _, _, sheet in top_level(text, "sheet"):
        for _, x, y in SHEET_PIN.findall(sheet):
            c[_key(x, y)] += 1
    for m in NO_CONNECT.finditer(text):
        c[_key(m.group(1), m.group(2))] += 1
    return c


def _trim_stubs(text, region):
    """Fix wires (inside region) that have an end touching nothing else.

    If something sits part-way along the wire (a label, pin, sheet pin, another
    wire's end or a junction), the free end is pulled back to the nearest such
    point; otherwise the wire is removed. One wire per call; callers loop.
    """
    wires = list(WIRE.finditer(text))
    geo = [tuple(map(float, m.groups()[:4])) for m in wires]
    items = _connection_points(text)
    ends = collections.Counter()
    for w in geo:
        ends[_key(w[0], w[1])] += 1
        ends[_key(w[2], w[3])] += 1
    attach = set(items) | set(ends) | {_key(*j) for j in JUNCTION.findall(text)}
    for m, w in zip(wires, geo):
        for (x, y), (ox, oy) in (((w[0], w[1]), (w[2], w[3])), ((w[2], w[3]), (w[0], w[1]))):
            k = _key(x, y)
            if k not in region or ends[k] != 1 or items[k]:
                continue
            if any(on_interior(x, y, *o) for o in geo if o is not w):
                continue
            inner = [p for p in attach if on_interior(p[0], p[1], *w)]
            if not inner:
                return text[:m.start()] + text[m.end():], 1
            nx, ny = min(inner, key=lambda p: math.hypot(p[0] - x, p[1] - y))
            pts = f"(xy {fmt(nx)} {fmt(ny)}) (xy {fmt(ox)} {fmt(oy)})"
            new = re.sub(r"\(xy [-\d.]+ [-\d.]+\) \(xy [-\d.]+ [-\d.]+\)", pts, m.group(0), count=1)
            return text[:m.start()] + new + text[m.end():], 1
    return text, 0


def _drop_weak_junctions(text, region):
    wires = [tuple(map(float, m.groups()[:4])) for m in WIRE.finditer(text)]
    items = _connection_points(text)
    spans = []
    for m in JUNCTION.finditer(text):
        x, y = float(m.group(1)), float(m.group(2))
        k = _key(x, y)
        if k not in region:
            continue
        n = items[k]
        for w in wires:
            if _key(w[0], w[1]) == k or _key(w[2], w[3]) == k:
                n += 1
            elif on_interior(x, y, *w):
                n += 2
        if n < 3:
            spans.append((m.start(), m.end()))
    return _remove_spans(text, spans), len(spans)


# ---------------------------------------------------------------- additions

def _effects(hide=False, justify=None):
    out = "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n"
    if justify:
        out += f"\t\t\t\t(justify {justify})\n"
    if hide:
        out += "\t\t\t\t(hide yes)\n"
    return out + "\t\t\t)\n"


def _prop(name, value, x, y, hide=False, justify=None, angle=0):
    return (f'\t\t(property "{name}" "{value}"\n\t\t\t(at {fmt(x)} {fmt(y)} {fmt(angle)})\n'
            + _effects(hide, justify) + "\t\t)\n")


def _insert_after_last(text, kind, block, fallback_kind="sheet_instances"):
    spans = list(top_level(text, kind))
    if spans:
        pos = spans[-1][1]
    else:
        m = re.search(r'^\t\(' + fallback_kind + r'\b', text, re.M)
        pos = m.start() if m else text.rstrip().rfind(")")
    return text[:pos] + block + text[pos:]


def ensure_lib_symbol(text, lib_id, kicad_sym_path):
    """Copy a symbol from a .kicad_sym library into the sheet's lib_symbols as `lib_id`."""
    if f'(symbol "{lib_id}"' in text:
        return text
    name = lib_id.split(":", 1)[1]
    lib = Path(kicad_sym_path).read_text()
    m = re.search(r'^\t\(symbol "' + re.escape(name) + r'"\n', lib, re.M)
    if not m:
        raise ValueError(f"symbol {name} not found in {kicad_sym_path}")
    block = lib[m.start():lib.index("\n\t)\n", m.start()) + 4]
    if "(extends " in block:
        raise ValueError(f"{name} extends another symbol; flatten it first")
    block = block.replace(f'(symbol "{name}"', f'(symbol "{lib_id}"', 1)
    block = "".join("\t" + line if line.strip() else line for line in block.splitlines(True))
    ls = next(top_level(text, "lib_symbols"))
    pos = ls[1] - len("\t)\n")
    return text[:pos] + block + text[pos:]


def lib_pin_numbers(text, lib_id):
    ls = next(top_level(text, "lib_symbols"))[2]
    sym = next(b for b in blocks(ls, f'symbol "{lib_id}"'))
    return re.findall(r'\(number "([^"]*)"', sym)


def add_symbol(text, lib_id, ref, value, x, y, rot=0, footprint="", unit=1,
               sheet_path="", hide_ref=False, hide_value=False, ref_offset=(0, -3.81), value_offset=(0, 3.81)):
    """Place an instance of `lib_id` (already in lib_symbols). Returns (text, uuid)."""
    u = str(uuid.uuid4())
    b = (f'\t(symbol\n\t\t(lib_id "{lib_id}")\n\t\t(at {fmt(x)} {fmt(y)} {fmt(rot)})\n\t\t(unit {unit})\n'
         '\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)\n'
         f'\t\t(uuid "{u}")\n')
    b += _prop("Reference", ref, x + ref_offset[0], y + ref_offset[1], hide=hide_ref)
    b += _prop("Value", value, x + value_offset[0], y + value_offset[1], hide=hide_value)
    b += _prop("Footprint", footprint, x, y, hide=True)
    b += _prop("Datasheet", "", x, y, hide=True)
    b += _prop("Description", "", x, y, hide=True)
    for num in lib_pin_numbers(text, lib_id):
        b += f'\t\t(pin "{num}"\n\t\t\t(uuid "{uuid.uuid4()}")\n\t\t)\n'
    b += (f'\t\t(instances\n\t\t\t(project ""\n\t\t\t\t(path "{sheet_path}"\n'
          f'\t\t\t\t\t(reference "{ref}")\n\t\t\t\t\t(unit {unit})\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n')
    return _insert_after_last(text, "symbol", b), u


def add_wire(text, x1, y1, x2, y2):
    b = (f"\t(wire\n\t\t(pts\n\t\t\t(xy {fmt(x1)} {fmt(y1)}) (xy {fmt(x2)} {fmt(y2)})\n\t\t)\n"
         "\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)\n"
         f'\t\t(uuid "{uuid.uuid4()}")\n\t)\n')
    return _insert_after_last(text, "wire", b)


def add_no_connect(text, x, y):
    b = f'\t(no_connect\n\t\t(at {fmt(x)} {fmt(y)})\n\t\t(uuid "{uuid.uuid4()}")\n\t)\n'
    return _insert_after_last(text, "no_connect", b, fallback_kind="wire")


def add_label(text, name, x, y, angle=0):
    """Local label; angle 180 reads leftward from (x, y), as KiCad writes it (justify right)."""
    just = "right bottom" if angle == 180 else "left bottom"
    b = (f'\t(label "{name}"\n\t\t(at {fmt(x)} {fmt(y)} {fmt(angle)})\n'
         f"\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify {just})\n\t\t)\n"
         f'\t\t(uuid "{uuid.uuid4()}")\n\t)\n')
    return _insert_after_last(text, "label", b)


def next_ref(texts, prefix):
    """Next free reference for a prefix across sheets, keeping existing zero-padding ('#PWR65' -> '#PWR66')."""
    found = [n for t in texts for n in re.findall(r'\(reference "' + re.escape(prefix) + r'(\d+)"\)', t)]
    width = max((len(n) for n in found), default=1)
    return f"{prefix}{max((int(n) for n in found), default=0) + 1:0{width}d}"


def bbox_clear(text, x0, y0, x1, y1):
    """Return the items (pins, wire ends, labels) found inside a rectangle; [] means clear."""
    hits = []
    for ref, num, x, y in symbol_pins(text):
        if x0 <= x <= x1 and y0 <= y <= y1:
            hits.append(f"{ref}.{num}")
    for _, _, w in [(0, 0, tuple(map(float, m.groups()[:4]))) for m in WIRE.finditer(text)]:
        if not (max(w[0], w[2]) < x0 or min(w[0], w[2]) > x1 or max(w[1], w[3]) < y0 or min(w[1], w[3]) > y1):
            hits.append(f"wire({fmt(w[0])},{fmt(w[1])})-({fmt(w[2])},{fmt(w[3])})")
    for m in LABEL.finditer(text):
        if x0 <= float(m.group(3)) <= x1 and y0 <= float(m.group(4)) <= y1:
            hits.append(f"label {m.group(2)}")
    for s, e, b in top_level(text, "symbol"):
        x, y = map(float, re.search(r'\(lib_id "[^"]+"\)\s*\(at ([-\d.]+) ([-\d.]+)', b).groups())
        if x0 <= x <= x1 and y0 <= y <= y1:
            hits.append(f"symbol {symbol_ref(b)}")
    return hits


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


# ---------------------------------------------------------------- copying

def _shift(block, dx, dy):
    def at(m):
        return f"({m.group(1)} {fmt(float(m.group(2)) + dx)} {fmt(float(m.group(3)) + dy)}"
    return re.sub(r'\((at|xy) ([-\d.]+) ([-\d.]+)', at, block)


def _new_uuids(block):
    return re.sub(r'\(uuid "[^"]*"\)', lambda m: f'(uuid "{uuid.uuid4()}")', block)


def _in_box(x, y, box):
    return box[0] <= x <= box[2] and box[1] <= y <= box[3]


def copy_block(text, box, dx, dy, ref_map, label_map, new_power_ref):
    """Copy everything inside box=(x0, y0, x1, y1) to (+dx, +dy), as a duplicate circuit.

    Copied: symbols whose origin is in the box, wires with both ends in it,
    junctions, labels (all kinds) and no-connect flags in it. Every non-power
    symbol in the box must be in ref_map (old -> new reference); power symbols
    get new_power_ref(). Label names are renamed through label_map; names not
    in it (e.g. a hierarchical label to reuse) are kept. All uuids are new.
    Returns (text, report) with report = {"symbols": {old: new}, "wires": n,
    "junctions": n, "labels": [(old, new)], "no_connects": n}.
    """
    report = {"symbols": {}, "wires": 0, "junctions": 0, "labels": [], "no_connects": 0}
    new_syms, new_wires, new_juncs, new_labels, new_ncs = [], [], [], [], []
    for _, _, b in top_level(text, "symbol"):
        x, y = map(float, re.search(r'\(lib_id "[^"]+"\)\s*\(at ([-\d.]+) ([-\d.]+)', b).groups())
        if not _in_box(x, y, box):
            continue
        old = symbol_ref(b)
        if _is_power_ref(old):
            new = new_power_ref()
        elif old in ref_map:
            new = ref_map[old]
        else:
            raise ValueError(f"{old} is inside the copy box but not in ref_map")
        c = _new_uuids(_shift(b, dx, dy))
        c = c.replace(f'(property "Reference" "{old}"', f'(property "Reference" "{new}"', 1)
        c = c.replace(f'(reference "{old}")', f'(reference "{new}")')
        new_syms.append(c)
        report["symbols"][old] = new
    for m in WIRE.finditer(text):
        x1, y1, x2, y2 = map(float, m.groups()[:4])
        if _in_box(x1, y1, box) and _in_box(x2, y2, box):
            new_wires.append(_new_uuids(_shift(m.group(0), dx, dy)))
    for m in JUNCTION.finditer(text):
        if _in_box(float(m.group(1)), float(m.group(2)), box):
            new_juncs.append(_new_uuids(_shift(m.group(0), dx, dy)))
    for m in LABEL.finditer(text):
        if _in_box(float(m.group(3)), float(m.group(4)), box):
            old = m.group(2)
            new = label_map.get(old, old)
            c = _new_uuids(_shift(m.group(0), dx, dy)).replace(f'({m.group(1)} "{old}"', f'({m.group(1)} "{new}"', 1)
            new_labels.append(c)
            report["labels"].append((old, new))
    for m in NO_CONNECT.finditer(text):
        if _in_box(float(m.group(1)), float(m.group(2)), box):
            new_ncs.append(_new_uuids(_shift(m.group(0), dx, dy)))
    missing = set(ref_map) - set(report["symbols"])
    if missing:
        raise ValueError(f"ref_map names parts not inside the copy box: {sorted(missing)}")
    report["wires"], report["junctions"], report["no_connects"] = len(new_wires), len(new_juncs), len(new_ncs)
    for kind, items in (("junction", new_juncs), ("no_connect", new_ncs), ("wire", new_wires),
                        ("label", new_labels), ("symbol", new_syms)):
        if items:
            text = _insert_after_last(text, kind, "".join(items), fallback_kind="sheet_instances")
    return text, report


def set_properties(text, ref, values=None, drop=(), keep_only=None):
    """Edit one symbol's properties: set existing ones (values), remove some (drop),
    or remove every non-standard property not named in keep_only. A property in
    values that doesn't exist yet is added, hidden, at the symbol origin."""
    values = dict(values or {})
    standard = {"Reference", "Value", "Footprint", "Datasheet", "Description"}
    for s, e, b in top_level(text, "symbol"):
        if symbol_ref(b) != ref:
            continue
        props = list(PROP.finditer(b))
        if len(props) != len(re.findall(r'^\t\t\(property ', b, re.M)):
            raise ValueError(f"{ref}: a property didn't parse; refusing to edit it partially")
        out, last = b, None
        for m in reversed(props):
            name = m.group(1)
            gone = name in drop or (keep_only is not None and name not in standard
                                    and name not in keep_only and name not in values)
            if gone:
                out = out[:m.start()] + out[m.end():]
            elif name in values:
                new = m.group(0).replace(f'"{name}" "{m.group(2)}"', f'"{name}" "{values.pop(name)}"', 1)
                out = out[:m.start()] + new + out[m.end():]
        if values:
            x, y = map(float, re.search(r'\(lib_id "[^"]+"\)\s*\(at ([-\d.]+) ([-\d.]+)', b).groups())
            last = list(PROP.finditer(out))[-1]
            extra = "".join(_prop(k, v, x, y, hide=True) for k, v in values.items())
            out = out[:last.end()] + extra + out[last.end():]
        return text[:s] + out + text[e:]
    raise ValueError(f"no symbol {ref}")
