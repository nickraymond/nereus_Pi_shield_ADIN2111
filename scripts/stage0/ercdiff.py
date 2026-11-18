#!/usr/bin/env python3
"""ERC items of a report against the baseline report: counts by (severity, type), then items vanished and new.

Adapted from experiments/pi_zero_fit_01/scripts/stage2_schematic/ercdiff.py (development branch): the two files are
arguments, and the counts by type are printed. Items are compared as (sheet, type, severity, description, items)."""
import collections
import json
import sys


def items(path):
    c = collections.Counter()
    for s in json.load(open(path))["sheets"]:
        for v in s["violations"]:
            c[(s["path"], v["type"], v.get("severity", ""), v["description"], tuple(sorted(i["description"] for i in v["items"])))] += 1
    return c


def by_type(c):
    out = collections.Counter()
    for k, n in c.items():
        out[(k[2], k[1])] += n
    return out


b, s = items(sys.argv[1]), items(sys.argv[2])
print("COUNTS BY TYPE (severity, type: baseline -> now):")
bt, st = by_type(b), by_type(s)
for k in sorted(set(bt) | set(st)):
    print(f"  {k[0]:8} {k[1]:28} {bt[k]:3} -> {st[k]:3}")
print("VANISHED:")
for k, n in sorted((b - s).items()):
    print("  -", n, k)
print("NEW:")
for k, n in sorted((s - b).items()):
    print("  +", n, k)
err = lambda c: sum(n for k, n in c.items() if k[2] == "error")
print(f"baseline {sum(b.values())} items ({err(b)} errors, {sum(b.values()) - err(b)} warnings)")
print(f"now      {sum(s.values())} items ({err(s)} errors, {sum(s.values()) - err(s)} warnings)")
