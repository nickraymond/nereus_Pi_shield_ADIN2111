"""Counts by severity and type of a kicad-cli DRC JSON report (violations, unconnected items, schematic parity), against a second report if given.
Usage: drcsum.py <drc.json> [<baseline drc.json>]. Written new."""
import collections, json, sys
def load(p):
    d = json.load(open(p)); out = {}
    for sec in ("violations", "unconnected_items", "schematic_parity"):
        c = collections.Counter((v.get("severity", ""), v["type"]) for v in d.get(sec, [])); out[sec] = c
    return d, out
d, now = load(sys.argv[1]); base = load(sys.argv[2])[1] if len(sys.argv) > 2 else None
for sec in ("violations", "unconnected_items", "schematic_parity"):
    c = now[sec]; print("%s: %d%s" % (sec, sum(c.values()), "   (starting board: %d)" % sum(base[sec].values()) if base else ""))
    for k in sorted(set(c) | set(base[sec] if base else [])):
        print("   %-8s %-34s %5d%s" % (k[0], k[1], c[k], "   (starting board %d)" % base[sec][k] if base else ""))
if "-v" in sys.argv:
    for sec in ("violations", "schematic_parity"):
        seen = collections.Counter()
        for v in d.get(sec, []):
            if v.get("severity") == "error" or sec == "schematic_parity":
                seen[v["type"]] += 1
                if seen[v["type"]] <= 6: print("  ", v["type"], "|", v["description"][:90], "|", "; ".join(i["description"][:70] for i in v.get("items", []))[:200])
