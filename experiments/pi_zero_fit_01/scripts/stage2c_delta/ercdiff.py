#!/usr/bin/env python3
"""ERC items of two kicad-cli JSON reports, compared as (sheet, type, description, items). Usage: ercdiff.py <before> <after>"""
import collections, json, sys
def items(path):
    c = collections.Counter()
    for s in json.load(open(path))["sheets"]:
        for v in s["violations"]:
            c[(s["path"], v["type"], v.get("severity", ""), v["description"], tuple(sorted(i["description"] for i in v["items"])))] += 1
    return c
b, s = items(sys.argv[1]), items(sys.argv[2])
print("VANISHED:"); [print("  -", n, k) for k, n in sorted((b - s).items())]
print("NEW:"); [print("  +", n, k) for k, n in sorted((s - b).items())]
print(f"before {sum(b.values())} items, after {sum(s.values())} items")
