#!/usr/bin/env python3
"""Net-by-net and part-by-part diff of netlist_stage2.net against netlist_baseline.net (pins compared as REF.pin)."""
import netparse

bp, bn = netparse.load("../netlist_baseline.net")
sp, sn = netparse.load("../netlist_stage2.net")


def short(n):
    return n.replace("/Top-Level Schematic/", "/TL/")


print(f"baseline: {len(bp)} parts, {len(bn)} nets;  stage 2: {len(sp)} parts, {len(sn)} nets\n")
print("PARTS REMOVED:", ", ".join(sorted(set(bp) - set(sp))))
print("PARTS ADDED:  ", ", ".join(sorted(set(sp) - set(bp))))
print("\nPARTS CHANGED (value, footprint or any field):")
n = 0
for r in sorted(set(bp) & set(sp)):
    if bp[r] != sp[r]:
        n += 1
        print("  ", r, {k: (bp[r].get(k), sp[r].get(k)) for k in bp[r] if bp[r].get(k) != sp[r].get(k)})
print("   none" if not n else "")
# pin -> net maps
bpin = {p: k for k, v in bn.items() for p in v}
spin = {p: k for k, v in sn.items() for p in v}
print("\nNETS REMOVED (name gone):")
for k in sorted(set(bn) - set(sn)):
    print("  -", short(k), bn[k])
print("\nNETS ADDED (new name):")
for k in sorted(set(sn) - set(bn)):
    print("  +", short(k), sn[k])
print("\nNETS CHANGED (same name, different pins):")
same = 0
for k in sorted(set(bn) & set(sn)):
    if bn[k] != sn[k]:
        print("  ~", short(k), "  removed pins:", sorted(set(bn[k]) - set(sn[k])), "  added pins:", sorted(set(sn[k]) - set(bn[k])))
    else:
        same += 1
print(f"\nNETS IDENTICAL pin for pin: {same}")
print("\nKEPT PINS THAT CHANGED NET (pins of parts present in both):")
n = 0
for p in sorted(set(bpin) & set(spin)):
    if bpin[p] != spin[p]:
        n += 1
        print("  ", p, short(bpin[p]), "->", short(spin[p]))
print(f"   {n} pins")
