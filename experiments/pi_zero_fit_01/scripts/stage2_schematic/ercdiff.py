#!/usr/bin/env python3
"""ERC items of erc_stage2.json against erc_baseline.json, compared as (sheet, type, description, items)."""
import collections
import json


def items(path):
    c = collections.Counter()
    for s in json.load(open(path))["sheets"]:
        for v in s["violations"]:
            c[(s["path"], v["type"], v.get("severity", ""), v["description"], tuple(sorted(i["description"] for i in v["items"])))] += 1
    return c


b, s = items("../erc_baseline.json"), items("../erc_stage2.json")
print("VANISHED:")
for k, n in sorted((b - s).items()):
    print("  -", n, k)
print("NEW:")
for k, n in sorted((s - b).items()):
    print("  +", n, k)
print(f"baseline {sum(b.values())} items, stage 2 {sum(s.values())} items")
