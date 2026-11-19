#!/usr/bin/env python3
"""Final tables from the exported netlist: every pin of J21 / J22 (pin number, N6 signal, net), checked against
n6_pinmap.py, and every part that is new against the baseline netlist (reference, value, footprint, MPN, LCSC).
Usage: pintable.py <netlist>   (the baseline netlist is read from the stage 0 output folder). Written new."""
import os
import re
import sys
import netparse
from n6_pinmap import HEADERS

base = os.path.expanduser("~/NereusData/nereus_Pi_shield_ADIN2111/n6_shield/stage0/baseline/netlist_baseline.net")
bp, _ = netparse.load(base)
sp, sn = netparse.load(sys.argv[1])
pin = {p: k for k, v in sn.items() for p in v}
bad = 0
print("| Header | Pin | N6 signal | Net | Check |\n|---|---|---|---|---|")
for ref in ("J21", "J22"):
    for num, (sig, net) in sorted(HEADERS[ref].items()):
        got = pin.get(f"{ref}.{num}", "(no net)")
        if net is None:
            ok = got.startswith("unconnected-(") and len(sn[got]) == 1
        elif net in ("GND", "N6_3V3"):
            ok = got == net
        else:
            ok = got == "/Top-Level Schematic/" + net
        bad += not ok
        print(f"| {ref} | {num} | {sig} | {'no-connect' if net is None and ok else got.replace('/Top-Level Schematic/', '')} | {'ok' if ok else 'MISMATCH'} |")
print("\n| Ref | Value | Footprint | MPN (PLANNED MPN) | LCSC (PLANNED LCSC) | Nets |\n|---|---|---|---|---|---|")
nat = lambda s: [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]
for ref in sorted(set(sp) - set(bp), key=nat):
    p = sp[ref]
    nets = ", ".join(f"{q.split('.')[1]}: {pin[q].replace('/Top-Level Schematic/', '')}" for q in sorted((q for q in pin if q.rsplit('.', 1)[0] == ref), key=nat)
                     if not pin[q].startswith("unconnected")) if not ref.startswith("J2") else "see above"
    print(f"| {ref} | {p['value']} | {p['footprint']} | {p['fields'].get('PLANNED MPN') or '-'} | {p['fields'].get('PLANNED LCSC') or '-'} | {nets} |")
print(f"\nheader pins checked against n6_pinmap.py: {32 - bad} of 32 as mapped; new parts: {len(set(sp) - set(bp))}")
sys.exit(1 if bad else 0)
