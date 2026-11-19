"""Gate check asked for by the QE review of pull request 39 (finding 2): the unconnected items of a DRC report against the
report of the board before the step, net by net. A step may only take connections away; a net that has MORE unconnected
items than before is named, and GND or a supply net among them is marked. Counting all items together missed an open
ground once (stage C part 2), because the total still fell.
uncdiff.py <drc.json> <drc of the board before .json>"""
import collections, json, re, sys
def nets(p):
    c = collections.Counter()
    for u in json.load(open(p)).get("unconnected_items", []):
        m = re.search(r"\[([^\]]*)\]", u["items"][0]["description"]); c[(m.group(1) if m else "?").split("/")[-1]] += 1
    return c
now, base = nets(sys.argv[1]), nets(sys.argv[2])
POWER = re.compile(r"^(GND|VBUS.*|P_IN|.*3V3.*|5V.*|ADIN_AVDD|ADIN_VDDIO|DVDD.*)$")
worse = [(n, base[n], now[n]) for n in sorted(now) if now[n] > base[n]]
for n, a, b in worse: print("MORE UNCONNECTED on %-28s %d -> %d%s" % (n, a, b, "   <== GND or a supply net" if POWER.match(n) else ""))
print("nets with more unconnected items than before: %d (unconnected by net: %d nets before, %d now)" % (len(worse), len(base), len(now)))
