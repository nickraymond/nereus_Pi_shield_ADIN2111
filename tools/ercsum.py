#!/usr/bin/env python3
"""Summarise a kicad-cli ERC report: counts by severity and type, and the items in each.

Use it to write the ERC tables in DESIGN.md instead of hand-filtering (QE S2 F1:
a hand filter missed 'Hidden pin' and 'Hierarchical Sheet Pin' items).

  python3 tools/ercsum.py [docs/design-review/out/erc.rpt] [--items]

Prints each type's count; with --items, each error type's items grouped (a
connector's pins collapsed to one line that still lists the pin numbers).
Exit 1 if the per-type counts don't add up to the report's own totals, or if the
report has no totals line to check against.
"""
import collections
import re
import sys
from pathlib import Path


def parse(text):
    """Return [(severity, type, first item line)] for every violation."""
    out = []
    for block in re.split(r'\n(?=\[)', text):
        m = re.match(r'\[([a-z_]+)\]:', block)
        sev = re.search(r'^\s*; (error|warning)', block, re.M)
        if m and sev:
            item = re.search(r'@\([^)]*\): (.*)', block)
            out.append((sev.group(1), m.group(1), item.group(1).strip() if item else ""))
    return out


def group_item(item):
    item = re.sub(r'^Symbol (J\d+) Pin \d+ .*', r'\1 pins', item)
    return re.sub(r'\s*\[.*$', '', item)


def main(argv=None):
    args = [a for a in (argv if argv is not None else sys.argv[1:]) if not a.startswith("--")]
    show = "--items" in (argv if argv is not None else sys.argv[1:])
    text = Path(args[0] if args else "docs/design-review/out/erc.rpt").read_text()
    rows = parse(text)
    totals = re.search(r'ERC messages: (\d+)\s+Errors (\d+)\s+Warnings (\d+)', text)
    by = collections.defaultdict(list)
    for sev, typ, item in rows:
        by[(sev, typ)].append(item)
    for (sev, typ), items in sorted(by.items()):
        print(f"{sev:8} {typ:28} {len(items):4}")
        if show and sev == "error":
            pins = collections.defaultdict(list)
            for i in items:
                m = re.match(r'Symbol (J\d+) Pin (\S+)', i)
                if m:
                    pins[f"{m.group(1)} pins"].append(m.group(2))
            for it, n in sorted(collections.Counter(group_item(i) for i in items).items()):
                nums = sorted(pins.get(it, []), key=lambda p: int(p) if p.isdigit() else 0)
                print(f"{'':14}{n:4} × {it}" + (f" ({', '.join(nums)})" if nums else ""))
    n_err = sum(1 for r in rows if r[0] == "error")
    n_warn = len(rows) - n_err
    print(f"total    errors {n_err}, warnings {n_warn}" + (f"  (report: {totals.group(2)}/{totals.group(3)})" if totals else ""))
    if not totals:
        print("ercsum: no 'ERC messages … Errors … Warnings' totals line; can't cross-check", file=sys.stderr)
        return 1
    if (n_err, n_warn) != (int(totals.group(2)), int(totals.group(3))):
        print("ercsum: counts don't match the report totals", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
