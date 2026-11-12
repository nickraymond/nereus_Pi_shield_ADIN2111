#!/usr/bin/env python3
"""BOM review 2026-11: copy the part fields that bom_fields_2026_11.py set on the symbols into the board's
footprint fields, so that DRC's schematic parity reads 0 again.

The layout is frozen (tag s9-layout-freeze). This script changes nothing but hidden footprint fields: the value
string of an existing field, the name of J3's three lower-case fields, and new hidden fields copied from the
footprint's own PLANNED MPN field (same layer, place and size; a fresh uuid). `--verify OLD NEW` proves it: with
those fields taken out, the two board files are identical byte for byte.

  python3 bom_fields_board_sync_2026_11.py            # dry run
  python3 bom_fields_board_sync_2026_11.py --write
  python3 bom_fields_board_sync_2026_11.py --verify <board at the freeze tag> <board now>
"""
import re
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bom_fields_2026_11 as sch  # noqa: E402

BOARD = sch.HERE / "Nereus_Pi_Shield_Adin2111.kicad_pcb"
FIELDS = sorted({name for _, fields in sch.LINES for name in fields})
RENAMED_FROM = sorted({old for names in sch.RENAME.values() for old in names})
PROP = re.compile(r'\t\t\(property "((?:[^"\\]|\\.)*)" "((?:[^"\\]|\\.)*)"\n(?:\t\t\t[^\n]*\n)*\t\t\)\n')


def read(path):
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def footprint_blocks(text):
    """Yield (start, end) of every top-level '\\t(footprint' block, newline included."""
    for m in re.finditer(r'^\t\(footprint "', text, re.M):
        end = text.index("\n\t)\n", m.start()) + 4
        yield m.start(), end


def symbol_values():
    """ref -> {field: value} for the fields of the table, read from the sheets as they are now."""
    out = {}
    for path in sch.SHEETS:
        text = path.read_text(encoding="utf-8")
        for s, e in sch.symbol_blocks(text):
            block = text[s:e]
            ref = re.search(r'\(property "Reference" "([^"]*)"', block).group(1)
            if "(in_bom yes)" not in block or ref.startswith("#"):
                continue
            props = {m.group(1): m.group(2) for m in PROP.finditer(block)}
            vals = {f: props[f] for f in FIELDS if f in props}
            assert out.setdefault(ref, vals) == vals, (ref, "units disagree")
    return out


def edit_footprint(block, ref, vals, changes):
    for old, new in sch.RENAME.get(ref, {}).items():
        if f'\t\t(property "{old}" ' in block and f'\t\t(property "{new}" ' not in block:
            block = block.replace(f'\t\t(property "{old}" ', f'\t\t(property "{new}" ', 1)
            changes.append((ref, new, f"(field named {old})", "(renamed)"))
    for name, value in vals.items():
        found = [m for m in PROP.finditer(block) if m.group(1) == name]
        assert len(found) <= 1, (ref, name)
        if found:
            m = found[0]
            if m.group(2) != value:
                new = m.group(0).replace(f'"{name}" "{m.group(2)}"', f'"{name}" "{value}"', 1)
                block = block[:m.start()] + new + block[m.end():]
                changes.append((ref, name, m.group(2), value))
        elif value:
            tpl = [m for m in PROP.finditer(block) if m.group(1) == "PLANNED MPN"]
            assert tpl and "(hide yes)" in tpl[0].group(0), (ref, name, "no hidden PLANNED MPN to copy")
            t = tpl[0]
            new = t.group(0).replace(f'"PLANNED MPN" "{t.group(2)}"', f'"{name}" "{value}"', 1)
            new, n = re.subn(r'\(uuid "[0-9a-f-]+"\)', f'(uuid "{uuid.uuid4()}")', new)
            assert n == 1, (ref, name)
            block = block[:t.end()] + new + block[t.end():]
            changes.append((ref, name, "(no field)", value))
    return block


def strip_fields(text):
    """The board text with every field this script may touch taken out of every footprint."""
    names = set(FIELDS) | set(RENAMED_FROM)
    out, pos = [], 0
    for s, e in footprint_blocks(text):
        block = text[s:e]
        block = PROP.sub(lambda m: "" if m.group(1) in names else m.group(0), block)
        out += [text[pos:s], block]
        pos = e
    return "".join(out) + text[pos:]


def main():
    if "--verify" in sys.argv:
        a, b = (read(p) for p in sys.argv[sys.argv.index("--verify") + 1:][:2])
        same = strip_fields(a) == strip_fields(b)
        print("identical apart from the BOM fields" if same else "DIFFERENT outside the BOM fields")
        sys.exit(0 if same else 1)
    want = symbol_values()
    text = read(BOARD)
    changes, seen = [], set()
    for s, e in reversed(list(footprint_blocks(text))):
        block = text[s:e]
        ref = re.search(r'\t\t\(property "Reference" "([^"]*)"', block).group(1)
        if ref in want:
            assert ref not in seen, ref
            seen.add(ref)
            text = text[:s] + edit_footprint(block, ref, want[ref], changes) + text[e:]
    for ref, name, old, new in sorted(changes):
        print(f"{ref:5} {name:13} {old!r} -> {new!r}"[:200])
    print(f"{len(changes)} footprint field changes on {len({c[0] for c in changes})} footprints; "
          f"BOM parts with no footprint: {sorted(set(want) - seen)}")
    if "--write" in sys.argv and text != read(BOARD):
        with open(BOARD, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        print("wrote", BOARD.name)


if __name__ == "__main__":
    main()
