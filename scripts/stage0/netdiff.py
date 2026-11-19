#!/usr/bin/env python3
"""Net-by-net and part-by-part diff of a netlist against the baseline netlist (pins compared as REF.pin).

Adapted from experiments/pi_zero_fit_01/scripts/stage2_schematic/netdiff.py (development branch): the two files are
arguments; added are the "kept nets" section (nets whose kept pins are the same set, under the same or a new name)
and the check that every changed pin set differs only by pins of removed or added parts."""
import re
import sys
import netparse

bp, bn = netparse.load(sys.argv[1])
sp, sn = netparse.load(sys.argv[2])


def short(n):
    return n.replace("/Top-Level Schematic/", "/TL/")


def nat(s):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]


def ref(p):
    return p.rsplit(".", 1)[0]


gone, new = set(bp) - set(sp), set(sp) - set(bp)
print(f"baseline: {len(bp)} parts, {len(bn)} nets;  now: {len(sp)} parts, {len(sn)} nets\n")
print("PARTS REMOVED:", ", ".join(sorted(gone, key=nat)))
print("PARTS ADDED:  ", ", ".join(sorted(new, key=nat)))
print("\nPARTS CHANGED (value, footprint or any field):")
n = 0
for r in sorted(set(bp) & set(sp), key=nat):
    if bp[r] != sp[r]:
        n += 1
        d = {k: (bp[r].get(k), sp[r].get(k)) for k in bp[r] if k != "fields" and bp[r].get(k) != sp[r].get(k)}
        f = {k: (bp[r]["fields"].get(k), sp[r]["fields"].get(k)) for k in set(bp[r]["fields"]) | set(sp[r]["fields"])
             if bp[r]["fields"].get(k) != sp[r]["fields"].get(k)}
        print("  ", r, d, f)
print("   none" if not n else "")
bpin = {p: k for k, v in bn.items() for p in v}
spin = {p: k for k, v in sn.items() for p in v}
print("\nNETS REMOVED (name gone):")
for k in sorted(set(bn) - set(sn)):
    print("  -", short(k), " ".join(sorted(bn[k], key=nat)))
print("\nNETS ADDED (new name):")
for k in sorted(set(sn) - set(bn)):
    print("  +", short(k), " ".join(sorted(sn[k], key=nat)))
print("\nNETS CHANGED (same name, different pins):")
same = 0
for k in sorted(set(bn) & set(sn)):
    if bn[k] != sn[k]:
        print("  ~", short(k), "  removed pins:", " ".join(sorted(set(bn[k]) - set(sn[k]), key=nat)) or "-",
              "  added pins:", " ".join(sorted(set(sn[k]) - set(bn[k]), key=nat)) or "-")
    else:
        same += 1
print(f"\nNETS IDENTICAL pin for pin: {same}")
print("\nKEPT PINS THAT CHANGED NET (pins of parts present in both):")
n = 0
for p in sorted(set(bpin) & set(spin), key=nat):
    if bpin[p] != spin[p]:
        n += 1
        print("  ", p, short(bpin[p]), "->", short(spin[p]))
print(f"   {n} pins")
# every baseline net, reduced to the pins of kept parts: is that pin set still one net, with nothing else of the kept parts on it?
print("\nBASELINE NETS BY THEIR KEPT PINS (pins of parts present in both netlists):")
ok = split = merged = 0
skept = {k: frozenset(p for p in v if ref(p) not in new) for k, v in sn.items()}
for k in sorted(bn):
    kept = frozenset(p for p in bn[k] if ref(p) not in gone)
    if not kept:
        continue
    homes = {spin[p] for p in kept}
    if len(homes) > 1:
        split += 1
        print("  SPLIT ", short(k), {short(h): sorted(p for p in kept if spin[p] == h) for h in homes})
    elif skept[next(iter(homes))] != kept:
        merged += 1
        h = next(iter(homes))
        print("  JOINED", short(k), "->", short(h), " other kept pins now on it:", " ".join(sorted(skept[h] - kept, key=nat)))
    else:
        ok += 1
        h = next(iter(homes))
        if h != k:
            print("  RENAMED", short(k), "->", short(h))
print(f"   {ok} baseline nets keep exactly their kept pins (same or new name), {split} split, {merged} joined with other kept pins")
