"""Shared helpers for the stage-2 schematic steps (pi_zero_fit_01). Standard library only.

All edits go to the scratch copy in ../board/. The repo is never written. The schematic text-edit library is the
project's own tools/schedit.py, copied unchanged into repo_tools/ so the steps run without importing from the repo.
"""
import re
import sys
import uuid
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "repo_tools"))
import schedit  # noqa: E402
from midwire import JUNCTION, WIRE, fmt, symbol_pins  # noqa: E402
from netcheck import blocks  # noqa: E402

SCRATCH = HERE.parent
BOARD = SCRATCH / "board"
TOP = BOARD / "Nereus_Pi_Shield_Adin2111_TopLevel.kicad_sch"
URCHIN_SCH = SCRATCH / "urchin_ref" / "UrchinCam_01.kicad_sch"  # copy of the repo's read-only reference, upgraded to KiCad 10 format
URCHIN_SYM = BOARD / "urchin.kicad_sym"
PROJECT = "Nereus_Pi_Shield_Adin2111"
SHEET_PATH = "/30e82bf5-1344-486b-817c-02d3b0649ce4/3c398828-e355-49f6-be37-cb3640d2c671"  # Top-Level sheet (as J1's instance)
GND_SRC, V3_SRC = "#PWR01", "#PWR089"  # existing GND (rot 0) and shield 3V3 (rot 180) power symbols to copy


def read_top():
    return TOP.read_text(encoding="utf-8")


def write_top(text):
    assert text.count("(") == text.count(")"), "unbalanced parentheses"
    TOP.write_text(text, encoding="utf-8")


def pins(text, ref):
    return {n: (round(x, 4), round(y, 4)) for r, n, x, y in symbol_pins(text) if r == ref}


def refs(text):
    return {schedit.symbol_ref(b) for _, _, b in schedit.top_level(text, "symbol")}


def _origin(block):
    return tuple(map(float, re.search(r'\(lib_id "[^"]+"\)\s*\(at ([-\d.]+) ([-\d.]+)', block).groups()))


def _insert_symbol(text, block, new_ref, x, y):
    ox, oy = _origin(block)
    b = schedit._new_uuids(schedit._shift(block, x - ox, y - oy))
    b = re.sub(r'(\(property "Reference" )"[^"]*"', rf'\1"{new_ref}"', b, count=1)
    b = re.sub(r'\(reference "[^"]*"\)', f'(reference "{new_ref}")', b)
    b = re.sub(r'\(project "[^"]*"', f'(project "{PROJECT}"', b)
    b = re.sub(r'\(path "[^"]*"', f'(path "{SHEET_PATH}"', b)
    assert b.count("(path ") == 1, "expected one instance path"
    return schedit._insert_after_last(text, "symbol", b)


def clone_urchin(text, src_ref, new_ref, x, y, lib_name=None, drop_pins=()):
    """Copy part `src_ref` of the Urchin schematic (all fields kept) as `new_ref` at (x, y).

    The lib symbol comes from the scratch project's urchin.kicad_sym as "urchin:<name>"; lib_name picks a derived
    symbol (step 0) instead of the instance's own."""
    assert new_ref not in refs(text), new_ref + " exists"
    src = URCHIN_SCH.read_text(encoding="utf-8")
    block = next(b for _, _, b in schedit.top_level(src, "symbol") if schedit.symbol_ref(b) == src_ref)
    old = re.search(r'\(lib_id "([^"]+)"\)', block).group(1)
    new = "urchin:" + (lib_name or old.split(":", 1)[1])
    block = block.replace(f'(lib_id "{old}")', f'(lib_id "{new}")', 1)
    for p in drop_pins:
        block, n = re.subn(r'\t\t\(pin "%s"\n\t\t\t\(uuid "[^"]+"\)\n\t\t\)\n' % re.escape(p), "", block)
        assert n == 1, (src_ref, p, n)
    text = schedit.ensure_lib_symbol(text, new, URCHIN_SYM)
    return _insert_symbol(text, block, new_ref, x, y)


_pwr = [100]


def power(text, kind, x, y):
    """Place a GND or shield-3V3 power symbol (a copy of an existing one on this sheet) with its pin at (x, y)."""
    src_ref = {"GND": GND_SRC, "3V3": V3_SRC}[kind]
    block = next(b for _, _, b in schedit.top_level(text, "symbol") if schedit.symbol_ref(b) == src_ref)
    px, py = pins(text, src_ref)[""] if "" in pins(text, src_ref) else list(pins(text, src_ref).values())[0]
    ox, oy = _origin(block)
    have = set(re.findall(r'\(reference "(#PWR\d+)"\)', "".join(p.read_text() for p in BOARD.glob("*.kicad_sch")) + text))
    while True:
        _pwr[0] += 1
        ref = f"#PWR{_pwr[0]}"
        if ref not in have:
            break
    return _insert_symbol(text, block, ref, x - (px - ox), y - (py - oy))


def wire(text, *pts):
    for a, b in zip(pts, pts[1:]):
        assert a != b and (a[0] == b[0] or a[1] == b[1]), ("wire must be axis-aligned", a, b)
        text = schedit.add_wire(text, a[0], a[1], b[0], b[1])
    return text


def junction(text, x, y):
    b = (f'\t(junction\n\t\t(at {fmt(x)} {fmt(y)})\n\t\t(diameter 0)\n\t\t(color 0 0 0 0)\n'
         f'\t\t(uuid "{uuid.uuid4()}")\n\t)\n')
    return schedit._insert_after_last(text, "junction", b, fallback_kind="wire")


def stub_label(text, pin, name, dx):
    """Wire from a pin dx mm sideways and a local label of `name` at its end (reading away from the pin)."""
    x, y = pin
    text = wire(text, (x, y), (round(x + dx, 4), y))
    return schedit.add_label(text, name, round(x + dx, 4), y, 180 if dx < 0 else 0)


def note(text, body, x, y, size=1.27):
    b = (f'\t(text "{body}"\n\t\t(exclude_from_sim no)\n\t\t(at {fmt(x)} {fmt(y)} 0)\n\t\t(effects\n\t\t\t(font\n'
         f'\t\t\t\t(size {size} {size})\n\t\t\t)\n\t\t\t(justify left top)\n\t\t)\n\t\t(uuid "{uuid.uuid4()}")\n\t)\n')
    return schedit._insert_after_last(text, "text", b, fallback_kind="wire")


def title(text, body, x, y, w, h=6.35):
    """Section title in the sheet's style (3.048 mm text, no frame)."""
    b = (f'\t(text_box "{body}"\n\t\t(exclude_from_sim no)\n\t\t(at {fmt(x)} {fmt(y)} 0)\n\t\t(size {fmt(w)} {fmt(h)})\n'
         '\t\t(margins 0.9525 0.9525 0.9525 0.9525)\n\t\t(stroke\n\t\t\t(width -0.0001)\n\t\t\t(type solid)\n'
         '\t\t\t(color 0 0 0 1)\n\t\t)\n\t\t(fill\n\t\t\t(type none)\n\t\t)\n\t\t(effects\n\t\t\t(font\n'
         '\t\t\t\t(size 3.048 3.048)\n\t\t\t)\n\t\t\t(justify left top)\n\t\t)\n'
         f'\t\t(uuid "{uuid.uuid4()}")\n\t)\n')
    return schedit._insert_after_last(text, "text_box", b, fallback_kind="wire")


def set_props(text, ref, values):
    """schedit.set_properties, with new fields written in this file's KiCad 10 form (hidden)."""
    block = next(b for _, _, b in schedit.top_level(text, "symbol") if schedit.symbol_ref(b) == ref)
    have = set(re.findall(r'^\t\t\(property "([^"]+)"', block, re.M))
    text = schedit.set_properties(text, ref, {k: v for k, v in values.items() if k in have})
    new = {k: v for k, v in values.items() if k not in have}
    if not new:
        return text
    for s, e, b in schedit.top_level(text, "symbol"):
        if schedit.symbol_ref(b) != ref:
            continue
        x, y = _origin(b)
        extra = "".join(
            f'\t\t(property "{k}" "{v}"\n\t\t\t(at {fmt(x)} {fmt(y)} 0)\n\t\t\t(hide yes)\n\t\t\t(show_name no)\n'
            '\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n'
            '\t\t\t)\n\t\t)\n' for k, v in new.items())
        last = list(schedit.PROP.finditer(b))[-1]
        return text[:s] + b[:last.end()] + extra + b[last.end():] + text[e:]
    raise ValueError(ref)


def box_delete(text, box, expect_refs):
    """Remove every symbol, wire, label, junction and no-connect flag that lies wholly inside box=(x0, y0, x1, y1).

    The set of removed non-power parts must equal expect_refs. Returns (text, report)."""
    x0, y0, x1, y1 = box

    def inside(x, y):
        return x0 <= float(x) <= x1 and y0 <= float(y) <= y1

    spans, rep = [], {"parts": [], "power": [], "wires": 0, "labels": [], "junctions": 0, "no_connects": 0}
    for s, e, b in schedit.top_level(text, "symbol"):
        if inside(*_origin(b)):
            r = schedit.symbol_ref(b)
            rep["power" if r.startswith("#") else "parts"].append(r)
            spans.append((s, e))
    for m in WIRE.finditer(text):
        a = m.groups()[:4]
        if inside(a[0], a[1]) and inside(a[2], a[3]):
            spans.append((m.start(), m.end()))
            rep["wires"] += 1
        else:
            assert not (inside(a[0], a[1]) or inside(a[2], a[3])), ("wire crosses the box edge", a)
    for m in schedit.LABEL.finditer(text):
        if inside(m.group(3), m.group(4)):
            spans.append((m.start(), m.end()))
            rep["labels"].append(m.group(2))
    for m in JUNCTION.finditer(text):
        if inside(m.group(1), m.group(2)):
            spans.append((m.start(), m.end()))
            rep["junctions"] += 1
    for m in schedit.NO_CONNECT.finditer(text):
        if inside(m.group(1), m.group(2)):
            spans.append((m.start(), m.end()))
            rep["no_connects"] += 1
    assert sorted(rep["parts"]) == sorted(expect_refs), (rep["parts"], expect_refs)
    return schedit._remove_spans(text, spans), rep


def remove_exact(text, kind, startswith):
    """Remove the one top-level item of `kind` whose block starts with the given text."""
    hits = [(s, e) for s, e, b in schedit.top_level(text, kind) if b.startswith(startswith)]
    assert len(hits) == 1, (kind, startswith, len(hits))
    return text[:hits[0][0]] + text[hits[0][1]:]


def gh4_ganged(text, src_ref, ref, x, y, net12, net34, function, note_from):
    """A JST GH 4-pin side-entry connector copied from the Urchin's `src_ref` (SM04B-GHS), pins 1+2 on net12 and
    3+4 on net34 by same-name labels. The symbol has no mounting-pin pin, as on the Urchin (its footprint's two
    MP pads carry no net there)."""
    text = clone_urchin(text, src_ref, ref, x, y)
    p = pins(text, ref)
    for a, b, net in (("1", "2", net12), ("3", "4", net34)):
        (xa, ya), (xb, yb) = p[a], p[b]
        text = stub_label(text, (xa, ya), net, -7.62)
        text = wire(text, (xb, yb), (xa - 2.54, yb), (xa - 2.54, ya))
        text = junction(text, xa - 2.54, ya)
    text = set_props(text, ref, {"FUNCTION": function, "PLANNED MPN": "SM04B-GHS-TB", "PLANNED MFR": "JST",
                                 "PLANNED LCSC": "", "PLANNED NOTE": note_from + "; LCSC number not looked up"})
    return text


def urchin_fields(text, ref, urchin_ref, mpn, extra=""):
    return set_props(text, ref, {"PLANNED MPN": mpn, "PLANNED LCSC": "",
                                 "PLANNED NOTE": f"Copied from the Urchin board ({urchin_ref}){extra}; LCSC number not looked up"})


def fields_right(text, ref, dx=3.81):
    """Put a part's Reference and Value texts to the right of its body, left-justified (two lines)."""
    for s, e, b in schedit.top_level(text, "symbol"):
        if schedit.symbol_ref(b) != ref:
            continue
        x, y = _origin(b)
        for name, dy in (("Reference", -1.27), ("Value", 1.27)):
            m = re.search(r'\t\t\(property "%s" "[^"]*"\n\t\t\t\(at [-\d.]+ [-\d.]+ [-\d.]+\)\n(?:\t\t\t[^\n]*\n)*?\t\t\)\n' % name, b)
            p = m.group(0)
            q = re.sub(r'\(at [-\d.]+ [-\d.]+ [-\d.]+\)', f'(at {fmt(x + dx)} {fmt(y + dy)} 0)', p, count=1)
            q = re.sub(r'\t\t\t\t\(justify [^)]*\)\n', '', q)
            q = q.replace("\t\t\t\t)\n\t\t\t)\n\t\t)\n", "\t\t\t\t)\n\t\t\t\t(justify left)\n\t\t\t)\n\t\t)\n", 1)
            assert "(justify left)" in q, (ref, name, p)
            b = b.replace(p, q, 1)
        return text[:s] + b + text[e:]
    raise ValueError(ref)
