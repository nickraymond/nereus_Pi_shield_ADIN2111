#!/usr/bin/env python3
"""Net-by-net and part-by-part diff of two netlists. Usage: netdiff.py <before.net> <after.net>"""
import sys
import netparse
bp, bn = netparse.load(sys.argv[1]); sp, sn = netparse.load(sys.argv[2])
short = lambda n: n.replace("/Top-Level Schematic/", "/TL/")
print(f"before: {len(bp)} parts, {len(bn)} nets;  after: {len(sp)} parts, {len(sn)} nets\n")
print("PARTS REMOVED:", ", ".join(sorted(set(bp) - set(sp))) or "none")
print("PARTS ADDED:  ", ", ".join(sorted(set(sp) - set(bp))) or "none")
for r in sorted(set(sp) - set(bp)):
    print("   ", r, sp[r]["value"], "|", sp[r]["footprint"], "|", {k: v for k, v in sp[r]["fields"].items() if k.startswith("PLANNED")})
print("\nPARTS CHANGED (value, footprint or any field):")
n = 0
for r in sorted(set(bp) & set(sp)):
    if bp[r] != sp[r]:
        n += 1
        d = {k: (bp[r].get(k), sp[r].get(k)) for k in bp[r] if k != "fields" and bp[r].get(k) != sp[r].get(k)}
        d.update({"field " + k: (bp[r]["fields"].get(k), sp[r]["fields"].get(k)) for k in set(bp[r]["fields"]) | set(sp[r]["fields"]) if bp[r]["fields"].get(k) != sp[r]["fields"].get(k)})
        print("  ", r)
        for k, (a, b) in sorted(d.items()): print("       %-20s %r -> %r" % (k, a, b))
print(f"   {n} parts")
print("\nNETS REMOVED (name gone):", [short(k) for k in sorted(set(bn) - set(sn))] or "none")
print("NETS ADDED (new name):", [short(k) for k in sorted(set(sn) - set(bn))] or "none")
print("\nNETS CHANGED (same name, different pins):")
same = 0
for k in sorted(set(bn) & set(sn)):
    if bn[k] != sn[k]: print("  ~", short(k), "  removed pins:", sorted(set(bn[k]) - set(sn[k])), "  added pins:", sorted(set(sn[k]) - set(bn[k])))
    else: same += 1
print(f"\nNETS IDENTICAL pin for pin: {same}")
bf, sf = netparse.pinfuncs(sys.argv[1]), netparse.pinfuncs(sys.argv[2])
ch = [p for p in sorted(set(bf) & set(sf)) if bf[p] != sf[p]]
print("KEPT PINS THAT CHANGED NET, PIN NAME OR PIN TYPE:", ch or "none")
