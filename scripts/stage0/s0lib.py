"""Shared helpers for the N6 shield's stage 0 schematic steps (0a remove, 0b add and re-map). Standard library only.

Where this came from: adapted from `experiments/pi_zero_fit_01/scripts/stage2_schematic/s2lib.py` on the `development`
branch (the previous scripted schematic stage on this same schematic). Taken over unchanged in behaviour: pins, refs,
wire, junction, stub_label, note, title, set_props, box_delete, remove_exact. New here: sheet file access for all
sheets, clone_part (copy a part from any sheet, optionally turned, with its shown fields placed), power symbols by
copy, global_label, split_wire, table helpers, connector placement in KiCad 10's own symbol-instance form.
The text-edit library is the project's own `tools/schedit.py` (with `midwire.py`, `netcheck.py`), copied unchanged
from `development` into this folder.

The steps edit the sheets of `N6_Shield_ADIN2111/` in place (text edits in the format KiCad writes). They never
touch a .kicad_pcb, .kicad_pro, .kicad_dru or a footprint library.
"""
import re
import sys
import uuid
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import schedit  # noqa: E402
from midwire import JUNCTION, WIRE, fmt, on_interior, symbol_pins  # noqa: E402
from netcheck import blocks  # noqa: E402

PROJECT_DIR = HERE.parent.parent / "N6_Shield_ADIN2111"
PROJECT = "Nereus_Pi_Shield_Adin2111"
ROOT_UUID = "30e82bf5-1344-486b-817c-02d3b0649ce4"
TOP_PATH = f"/{ROOT_UUID}/3c398828-e355-49f6-be37-cb3640d2c671"            # Top-Level sheet
MOTOR_PATH = TOP_PATH + "/645ec816-357b-5a25-ba19-618b53952414"            # Motor + ADC sheet
KICAD_SYMBOLS = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols")
SHEETS = {"root": "", "top": "_TopLevel", "adin": "_ADIN2111", "load": "_LoadSwitch", "motor": "_MotorADC",
          "podl": "_PoDL", "power": "_Power", "pmon": "_PowerMonitor"}


def sheet_file(key):
    return PROJECT_DIR / f"{PROJECT}{SHEETS[key]}.kicad_sch"


def read(key):
    return sheet_file(key).read_text(encoding="utf-8")


def write(key, text):
    assert text.count("(") == text.count(")"), "unbalanced parentheses in " + key
    sheet_file(key).write_text(text, encoding="utf-8")


def pins(text, ref):
    return {n: (round(x, 4), round(y, 4)) for r, n, x, y in symbol_pins(text) if r == ref}


def refs(text):
    return {schedit.symbol_ref(b) for _, _, b in schedit.top_level(text, "symbol")}


def block_of(text, ref):
    hits = [b for _, _, b in schedit.top_level(text, "symbol") if schedit.symbol_ref(b) == ref]
    assert len(hits) == 1, (ref, len(hits))
    return hits[0]


def _origin(block):
    return tuple(map(float, re.search(r'\(lib_id "[^"]+"\)\s*\(at ([-\d.]+) ([-\d.]+)', block).groups()))


def all_refs():
    out = set()
    for k in SHEETS:
        if sheet_file(k).exists():
            out |= set(re.findall(r'\(reference "([^"]+)"\)', read(k)))
    return out


_pwr = [200]


def new_power_ref(text):
    have = all_refs() | set(re.findall(r'\(reference "([^"]+)"\)', text))
    while True:
        _pwr[0] += 1
        if f"#PWR{_pwr[0]}" not in have:
            return f"#PWR{_pwr[0]}"


# ---------------------------------------------------------------- lib symbols

def copy_lib_symbol(dst, src, lib_id):
    """Copy the embedded lib symbol `lib_id` from sheet text `src` into sheet text `dst` (if missing)."""
    if f'(symbol "{lib_id}"' in dst:
        return dst
    lsym = next(blocks(next(schedit.top_level(src, "lib_symbols"))[2], f'symbol "{lib_id}"'))
    ls = next(schedit.top_level(dst, "lib_symbols"))
    pos = ls[1] - len("\t)\n")
    return dst[:pos] + "\t\t" + lsym.rstrip("\n").lstrip("\t") + "\n" + dst[pos:]


def drop_lib_symbol(text, lib_id):
    """Remove an embedded lib symbol that no instance uses any more."""
    assert f'(lib_id "{lib_id}")' not in text, lib_id + " is still used"
    ls = next(schedit.top_level(text, "lib_symbols"))
    hits = list(blocks(ls[2], f'symbol "{lib_id}"'))
    assert len(hits) == 1, (lib_id, len(hits))
    i = text.index(hits[0], ls[0])
    start = text.rindex("\n", 0, i) + 1
    end = i + len(hits[0]) + 1
    assert text[start:i].strip() == "" and text[end - 1] == "\n"
    return text[:start] + text[end:]


# ---------------------------------------------------------------- parts

def _set_prop_at(block, name, x, y, angle, justify="keep"):
    m = re.search(r'\t\t\(property "%s" "(?:[^"\\]|\\.)*"\n(?:\t\t\t[^\n]*\n)*?\t\t\)\n' % re.escape(name), block)
    assert m, name
    p = m.group(0)
    q = re.sub(r'\(at [-\d.]+ [-\d.]+ [-\d.]+\)', f'(at {fmt(x)} {fmt(y)} {fmt(angle)})', p, count=1)
    if justify != "keep":
        q = re.sub(r'\t\t\t\t\(justify [^)]*\)\n', '', q)
        if justify:
            q = q.replace("\t\t\t\t)\n\t\t\t)\n\t\t)\n", f"\t\t\t\t)\n\t\t\t\t(justify {justify})\n\t\t\t)\n\t\t)\n", 1)
            assert f"(justify {justify})" in q, (name, p)
    return block.replace(p, q, 1)


def clone_part(dst, src, src_ref, new_ref, x, y, sheet_path, rot=None, shown=None):
    """Place a copy of part `src_ref` (from sheet text `src`) in sheet text `dst` at (x, y), every field kept.

    rot=None keeps the source's rotation and moves every field with the part. With rot given, the symbol gets that
    rotation, hidden fields go to the origin and the fields named in `shown` = {name: (dx, dy, angle, justify)} are
    placed relative to (x, y). New uuids, reference `new_ref`, instance path `sheet_path`; the lib symbol is copied
    into dst's lib_symbols if it is not there yet."""
    block = block_of(src, src_ref)
    assert new_ref not in refs(dst) and new_ref not in all_refs(), new_ref + " exists"
    lib_id = re.search(r'\(lib_id "([^"]+)"\)', block).group(1)
    dst = copy_lib_symbol(dst, src, lib_id)
    ox, oy = _origin(block)
    if rot is None:
        b = schedit._shift(block, x - ox, y - oy)
    else:
        b = re.sub(r'(\(lib_id "[^"]+"\)\s*)\(at [-\d.]+ [-\d.]+ [-\d.]+\)', lambda m: m.group(1) + f"(at {fmt(x)} {fmt(y)} {fmt(rot)})",
                   block, count=1)
        assert "(mirror " not in b
        for name in re.findall(r'^\t\t\(property "([^"]+)"', b, re.M):
            if shown and name in shown:
                dx, dy, ang, just = shown[name]
                b = _set_prop_at(b, name, x + dx, y + dy, ang, just)
            else:
                b = _set_prop_at(b, name, x, y, 0)
        for name in (shown or {}):
            assert re.search(r'\(property "%s" "[^"]*"\n\t\t\t\(at [^\n]*\n\t\t\t\(show_name' % re.escape(name), b), name + " is hidden"
    b = schedit._new_uuids(b)
    b = re.sub(r'(\(property "Reference" )"[^"]*"', rf'\1"{new_ref}"', b, count=1)
    b = re.sub(r'\(reference "[^"]*"\)', f'(reference "{new_ref}")', b)
    b = re.sub(r'\(project "[^"]*"', f'(project "{PROJECT}"', b)
    b = re.sub(r'\(path "[^"]*"', f'(path "{sheet_path}"', b)
    assert b.count("(path ") == 1, "expected one instance path"
    return schedit._insert_after_last(dst, "symbol", b)


def power(text, src_ref, x, y, sheet_path, src=None, rot=None, value_at=None):
    """A power symbol (copy of the existing power symbol `src_ref`, from this sheet or from sheet text `src`) with
    its pin at (x, y). value_at = (dx, dy, angle, justify) places the visible Value text when rot is given."""
    src = src or text
    assert pins(src, src_ref)[""] == tuple(round(v, 4) for v in _origin(block_of(src, src_ref))), "pin is not at the origin"
    shown = {"Value": value_at} if rot is not None else None
    return clone_part(text, src, src_ref, new_power_ref(text), x, y, sheet_path, rot=rot, shown=shown)


def set_props(text, ref, values):
    """schedit.set_properties, with new fields written in this file's KiCad 10 form (hidden)."""
    block = block_of(text, ref)
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


def get_props(text, ref):
    return dict(re.findall(r'^\t\t\(property "([^"]+)" "((?:[^"\\]|\\.)*)"', block_of(text, ref), re.M))


def swap_power_symbol(text, ref, old_lib, new_lib, new_value):
    """Turn one power-symbol instance into another power symbol in place (same position, rotation and uuid)."""
    for s, e, b in schedit.top_level(text, "symbol"):
        if schedit.symbol_ref(b) != ref:
            continue
        assert f'(lib_id "{old_lib}")' in b, (ref, old_lib)
        b2 = b.replace(f'(lib_id "{old_lib}")', f'(lib_id "{new_lib}")', 1)
        b2, n = re.subn(r'(\(property "Value" )"[^"]*"', rf'\1"{new_value}"', b2, count=1)
        assert n == 1
        return text[:s] + b2 + text[e:]
    raise ValueError(ref)


def connector(text, lib_id, ref, value, footprint, x, y, sheet_path, fields=None):
    """Place a new symbol instance of `lib_id` (already embedded) in the form KiCad 10 writes (modelled on J3)."""
    assert ref not in all_refs() and ref not in refs(text), ref

    def prop(name, val, px, py, hide):
        return (f'\t\t(property "{name}" "{val}"\n\t\t\t(at {fmt(px)} {fmt(py)} 0)\n' + ("\t\t\t(hide yes)\n" if hide else "")
                + '\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n'
                '\t\t\t\t)\n' + ("" if hide else "\t\t\t\t(justify left)\n") + '\t\t\t)\n\t\t)\n')
    desc = re.search(r'\(property "Description" "([^"]*)"', next(blocks(text, f'symbol "{lib_id}"'))).group(1)
    b = (f'\t(symbol\n\t\t(lib_id "{lib_id}")\n\t\t(at {fmt(x)} {fmt(y)} 0)\n\t\t(unit 1)\n\t\t(body_style 1)\n'
         '\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(in_pos_files yes)\n\t\t(dnp no)\n'
         f'\t\t(uuid "{uuid.uuid4()}")\n')
    b += prop("Reference", ref, x - 1.27, y - 13.97, False) + prop("Value", value, x - 1.27, y - 11.43, False)
    b += prop("Footprint", footprint, x, y, True) + prop("Datasheet", "", x, y, True) + prop("Description", desc, x, y, True)
    for k, v in (fields or {}).items():
        b += prop(k, v, x, y, True)
    for num in schedit.lib_pin_numbers(text, lib_id):
        b += f'\t\t(pin "{num}"\n\t\t\t(uuid "{uuid.uuid4()}")\n\t\t)\n'
    b += (f'\t\t(instances\n\t\t\t(project "{PROJECT}"\n\t\t\t\t(path "{sheet_path}"\n'
          f'\t\t\t\t\t(reference "{ref}")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n')
    return schedit._insert_after_last(text, "symbol", b)


# ---------------------------------------------------------------- wires, labels, text

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


def global_label(text, name, x, y, angle=180):
    """A global label in the form KiCad 10 writes (modelled on the sheet's own ADIN_TIMER label)."""
    just = "right" if angle == 180 else "left"
    ix = x - 13.69 if angle == 180 else x + 13.69
    b = (f'\t(global_label "{name}"\n\t\t(shape input)\n\t\t(at {fmt(x)} {fmt(y)} {fmt(angle)})\n\t\t(fields_autoplaced yes)\n'
         f'\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify {just})\n\t\t)\n'
         f'\t\t(uuid "{uuid.uuid4()}")\n'
         f'\t\t(property "Intersheetrefs" "${{INTERSHEET_REFS}}"\n\t\t\t(at {fmt(ix)} {fmt(y)} 0)\n\t\t\t(hide yes)\n'
         '\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n'
         f'\t\t\t\t(justify {just})\n\t\t\t)\n\t\t)\n\t)\n')
    return schedit._insert_after_last(text, "global_label", b, fallback_kind="label")


def note(text, body, x, y, size=1.27, justify="left top"):
    b = (f'\t(text "{body}"\n\t\t(exclude_from_sim no)\n\t\t(at {fmt(x)} {fmt(y)} 0)\n\t\t(effects\n\t\t\t(font\n'
         f'\t\t\t\t(size {fmt(size)} {fmt(size)})\n\t\t\t)\n\t\t\t(justify {justify})\n\t\t)\n\t\t(uuid "{uuid.uuid4()}")\n\t)\n')
    return schedit._insert_after_last(text, "text", b, fallback_kind="wire")


def split_wire(text, x, y):
    """Split the one wire whose interior holds (x, y) there and add a junction (KiCad connects pins at wire ends only)."""
    hits = [m for m in WIRE.finditer(text) if on_interior(x, y, *map(float, m.groups()[:4]))]
    assert len(hits) == 1, ("expected one wire through", x, y, len(hits))
    m = hits[0]
    x1, y1, x2, y2 = m.groups()[:4]
    text = text[:m.start()] + text[m.end():]
    text = wire(text, (float(x1), float(y1)), (x, y), (float(x2), float(y2)))
    return junction(text, x, y)


def remove_wire(text, a, b):
    hits = [m for m in WIRE.finditer(text)
            if {(float(m.group(1)), float(m.group(2))), (float(m.group(3)), float(m.group(4)))} == {tuple(a), tuple(b)}]
    assert len(hits) == 1, ("wire", a, b, len(hits))
    return text[:hits[0].start()] + text[hits[0].end():]


def remove_label(text, kind, name, x, y):
    hits = [m for m in schedit.LABEL.finditer(text)
            if m.group(1) == kind and m.group(2) == name and (float(m.group(3)), float(m.group(4))) == (x, y)]
    assert len(hits) == 1, (kind, name, x, y, len(hits))
    return text[:hits[0].start()] + text[hits[0].end():]


def remove_junction(text, x, y):
    hits = [m for m in JUNCTION.finditer(text) if (float(m.group(1)), float(m.group(2))) == (x, y)]
    assert len(hits) == 1, ("junction", x, y, len(hits))
    return text[:hits[0].start()] + text[hits[0].end():]


def remove_exact(text, kind, startswith):
    """Remove the one top-level item of `kind` whose block starts with the given text."""
    hits = [(s, e) for s, e, b in schedit.top_level(text, kind) if b.startswith(startswith)]
    assert len(hits) == 1, (kind, startswith, len(hits))
    return text[:hits[0][0]] + text[hits[0][1]:]


def replace_once(text, old, new):
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new)


def box_delete(text, box, expect_refs):
    """Remove every symbol, wire, label, junction and no-connect flag that lies wholly inside box=(x0, y0, x1, y1).

    The set of removed non-power parts must equal expect_refs; no wire may cross the box edge. Returns (text, report)."""
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
    for kind in ("label", "global_label", "hierarchical_label"):
        for s, e, b in schedit.top_level(text, kind):
            m = re.match(r'\t\(\w+ "([^"]+)"\n(?:\t\t\(shape \w+\)\n)?\t\t\(at ([-\d.]+) ([-\d.]+)', b)
            if inside(m.group(2), m.group(3)):
                spans.append((s, e))
                rep["labels"].append(m.group(1))
    for m in JUNCTION.finditer(text):
        if inside(m.group(1), m.group(2)):
            spans.append((m.start(), m.end()))
            rep["junctions"] += 1
    for m in schedit.NO_CONNECT.finditer(text):
        if inside(m.group(1), m.group(2)):
            spans.append((m.start(), m.end()))
            rep["no_connects"] += 1
    assert sorted(rep["parts"]) == sorted(expect_refs), (sorted(rep["parts"]), sorted(expect_refs))
    for k in ("parts", "power", "labels"):
        rep[k].sort()
    return schedit._remove_spans(text, spans), rep


# ---------------------------------------------------------------- tables

def _table(text, first_cell):
    hits = [(s, e, b) for s, e, b in schedit.top_level(text, "table") if f'(table_cell "{first_cell}"' in b[:b.index("(table_cell") + 200]]
    assert len(hits) == 1, (first_cell, len(hits))
    return hits[0]


def table_remove(text, first_cell):
    s, e, _ = _table(text, first_cell)
    return text[:s] + text[e:]


def table_drop_rows(text, first_cell, row_keys):
    """Remove whole rows from a table and close the gap. A row is named by the text of one of its cells; that text
    must occur in exactly one row of the table."""
    s, e, b = _table(text, first_cell)
    ncol = int(re.search(r'\(column_count (\d+)\)', b).group(1))
    heights = re.search(r'\(row_heights ([^)]*)\)', b).group(1).split()
    cells = list(blocks(b, 'table_cell "'))
    assert len(cells) == ncol * len(heights), (len(cells), ncol, len(heights))
    rows = [cells[r * ncol:(r + 1) * ncol] for r in range(len(heights))]
    texts = [[re.match(r'\(table_cell "((?:[^"\\]|\\.)*)"', c).group(1) for c in row] for row in rows]
    drop = set()
    for key in row_keys:
        hit = [r for r, row in enumerate(texts) if key in row]
        assert len(hit) == 1, (key, hit)
        drop.add(hit[0])
    assert len(drop) == len(row_keys)
    out, shift, keep_h = b, 0.0, []
    for r, row in enumerate(rows):
        if r in drop:
            for c in row:
                i = out.index(c)
                start = out.rindex("\n", 0, i) + 1
                out = out[:start] + out[i + len(c) + 1:]
            shift += float(heights[r])
            continue
        keep_h.append(heights[r])
        if shift:
            for c in row:
                c2 = re.sub(r'\(at ([-\d.]+) ([-\d.]+) 0\)', lambda m: f"(at {m.group(1)} {fmt(float(m.group(2)) - shift)} 0)", c, count=1)
                assert out.count(c) == 1
                out = out.replace(c, c2, 1)
    out = re.sub(r'\(row_heights [^)]*\)', "(row_heights " + " ".join(keep_h) + ")", out, count=1)
    return text[:s] + out + text[e:]


def cell_text(text, old, new):
    """Replace the text of the one table cell (or text / text box) that reads exactly `old`."""
    hits = [m for m in re.finditer(r'\((table_cell|text|text_box) "((?:[^"\\]|\\.)*)"', text) if m.group(2) == old]
    assert len(hits) == 1, (old, len(hits))
    m = hits[0]
    return text[:m.start(2)] + new + text[m.end(2):]
