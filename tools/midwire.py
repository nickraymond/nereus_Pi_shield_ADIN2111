#!/usr/bin/env python3
"""Find (and optionally fix) symbol pins whose end sits in the middle of a wire.

Altium connects a pin that touches a wire anywhere along it; KiCad only
connects at wire ends. The Altium import left such pins unconnected. KiCad 9
needs the wire split at the pin (a junction alone is not enough when loading
from file; measured 2026-10-05), so --fix splits the wire there and adds a
junction, which is what KiCad's own editor does.

Labels on a wire's interior are fine in KiCad and are not reported.

  python3 tools/midwire.py                 # report; exit 1 if any are found
  python3 tools/midwire.py --fix           # split + junction at every one found

Parts in the netcheck exclusion file (scheduled for deletion) are skipped.
Python standard library only.
"""
import argparse
import math
import re
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from netcheck import DEFAULT_EXCLUDE, blocks, read_exclusions  # noqa: E402

PROJECT = Path("nereus_Pi_shield_ADIN2111")
WIRE = re.compile(r'\t\(wire\n\t\t\(pts\n\t\t\t\(xy ([-\d.]+) ([-\d.]+)\) \(xy ([-\d.]+) ([-\d.]+)\)\n'
                  r'\t\t\)\n(.*?)\n\t\)\n', re.S)
JUNCTION = re.compile(r'\t\(junction\n\t\t\(at ([-\d.]+) ([-\d.]+)\)\n.*?\n\t\)\n', re.S)
TOL = 1e-3


def fmt(v):
    return f"{round(v, 4):.4f}".rstrip("0").rstrip(".")


def on_interior(x, y, x1, y1, x2, y2):
    """True if (x, y) lies on an axis-aligned wire but not at either end."""
    if math.hypot(x - x1, y - y1) < TOL or math.hypot(x - x2, y - y2) < TOL:
        return False
    if abs(x1 - x2) < TOL:
        return abs(x - x1) < TOL and min(y1, y2) - TOL <= y <= max(y1, y2) + TOL
    if abs(y1 - y2) < TOL:
        return abs(y - y1) < TOL and min(x1, x2) - TOL <= x <= max(x1, x2) + TOL
    return False


def lib_pins(text):
    """{lib_id: {unit: {pin number: (x, y)}}}; unit 0 pins are common to all units."""
    out = {}
    for sym in blocks(next(blocks(text, "lib_symbols")), 'symbol "'):
        name = re.match(r'\(symbol "([^"]+)"', sym).group(1)
        parent = re.match(r'(.*)_\d+_\d+$', name)
        if parent and parent.group(1) in out:  # a unit sub-symbol of a symbol already read
            continue
        units = out.setdefault(name, {})
        for sub in blocks(sym[1:], 'symbol "'):
            unit = int(re.match(r'\(symbol "[^"]*_(\d+)_\d+"', sub).group(1))
            for p in blocks(sub, "pin "):
                num = re.search(r'\(number "([^"]*)"', p).group(1)
                units.setdefault(unit, {})[num] = tuple(map(float, re.search(r'\(at ([-\d.]+) ([-\d.]+)', p).groups()))
    return out


def symbol_pins(text):
    """Yield (ref, pin, x, y) for every placed symbol pin, in sheet coordinates."""
    lib = lib_pins(text)
    for s in blocks(text, "symbol\n\t\t(lib_id"):
        lib_id = re.search(r'\(lib_id "([^"]+)"\)', s).group(1)
        ref = re.search(r'\(property "Reference" "([^"]+)"', s).group(1)
        x0, y0, rot = map(float, re.search(r'\(lib_id "[^"]+"\)\s*\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\)', s).groups())
        mirror = re.search(r'^\t\t\(mirror ([xy])\)', s, re.M)
        unit = int(re.search(r'^\t\t\(unit (\d+)\)', s, re.M).group(1))
        units = lib.get(lib_id, {})
        pins = dict(units.get(0, {}))
        if unit == 0:  # Altium import: single-unit parts are placed as unit 0
            for u in units.values():
                pins.update(u)
        else:
            pins.update(units.get(unit, {}))
        a = math.radians(-rot)
        for num, (px, py) in pins.items():
            py = -py
            if mirror and mirror.group(1) == "x":
                py = -py
            if mirror and mirror.group(1) == "y":
                px = -px
            yield (ref, num, round(x0 + px * math.cos(a) - py * math.sin(a), 4),
                   round(y0 + px * math.sin(a) + py * math.cos(a), 4))


def find(text, excluded):
    """{(x, y): [ref.pin, ...]} for pins on kept parts that sit mid-wire."""
    wires = [tuple(map(float, m.groups()[:4])) for m in WIRE.finditer(text)]
    found = {}
    for ref, num, x, y in symbol_pins(text):
        if ref in excluded or ref.startswith("#"):
            continue
        if any(on_interior(x, y, *w) for w in wires):
            found.setdefault((x, y), []).append(f"{ref}.{num}")
    return found


def split_and_join(text, x, y):
    """Split the single wire whose interior holds (x, y) and add a junction there."""
    hits = [m for m in WIRE.finditer(text) if on_interior(x, y, *map(float, m.groups()[:4]))]
    if len(hits) != 1:
        raise ValueError(f"expected 1 wire through ({x}, {y}), found {len(hits)}")
    m = hits[0]
    x1, y1, x2, y2, rest = m.groups()
    rest2 = re.sub(r'\(uuid "[^"]+"\)', f'(uuid "{uuid.uuid4()}")', rest)
    X, Y = fmt(x), fmt(y)
    wires = (f"\t(wire\n\t\t(pts\n\t\t\t(xy {x1} {y1}) (xy {X} {Y})\n\t\t)\n{rest}\n\t)\n"
             f"\t(wire\n\t\t(pts\n\t\t\t(xy {X} {Y}) (xy {x2} {y2})\n\t\t)\n{rest2}\n\t)\n")
    text = text[:m.start()] + wires + text[m.end():]
    if not any(math.hypot(float(a) - x, float(b) - y) < TOL for a, b in JUNCTION.findall(text)):
        j = (f"\t(junction\n\t\t(at {X} {Y})\n\t\t(diameter 0)\n\t\t(color 0 0 0 0)\n"
             f"\t\t(uuid \"{uuid.uuid4()}\")\n\t)\n")
        js = list(JUNCTION.finditer(text))
        pos = js[-1].end() if js else WIRE.search(text).start()
        text = text[:pos] + j + text[pos:]
    return text


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fix", action="store_true", help="split the wire and add a junction at each pin found")
    ap.add_argument("--project", default=str(PROJECT))
    ap.add_argument("--exclude", default=DEFAULT_EXCLUDE)
    a = ap.parse_args(argv)
    excluded = read_exclusions(Path(a.exclude).read_text()) if a.exclude else {}
    total = 0
    for sheet in sorted(Path(a.project).glob("*.kicad_sch")):
        text = sheet.read_text()
        if "(lib_symbols" not in text or "(symbol\n\t\t(lib_id" not in text:
            continue
        found = find(text, excluded)
        for (x, y), names in sorted(found.items()):
            print(f"{sheet.name}: ({fmt(x)}, {fmt(y)}) {'+'.join(names)}{'  → split + junction' if a.fix else ''}")
            if a.fix:
                text = split_and_join(text, x, y)
        if a.fix and found:
            sheet.write_text(text)
        total += len(found)
    print(f"midwire: {total} pin location(s) mid-wire{' fixed' if a.fix else ''}")
    return 0 if (a.fix or total == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
