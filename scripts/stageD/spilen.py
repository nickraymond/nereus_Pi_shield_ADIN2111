"""Read-only: copper length per SPI line from the ADIN2111 pad to the N6 header pin: all track segments of the ADIN-side
net plus the N6-side net plus 0.86 mm across the series resistor (pad centre to pad centre). Branches (R9's and R52's
taps, test stubs) are included, so the figure is an upper bound of the path. spilen.py <board>"""
import sys, pcbnew, math
b = pcbnew.LoadBoard(sys.argv[1]); mm = pcbnew.ToMM
def L(suffix):
    tot = 0; lay = {}
    for t in b.GetTracks():
        n = t.GetNetname()
        if (n == suffix or n.endswith("/" + suffix)) and t.Type() != pcbnew.PCB_VIA_T:
            l = mm(t.GetLength()); tot += l; lay[b.GetLayerName(t.GetLayer())] = lay.get(b.GetLayerName(t.GetLayer()), 0) + l
    v = sum(1 for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T and (t.GetNetname() == suffix or t.GetNetname().endswith("/" + suffix)))
    return tot, lay, v
res = {}
for name, a, n in (("MOSI", "ADIN_MOSI", "N6_MOSI"), ("MISO", "ADIN_MISO", "N6_MISO"), ("SCK", "ADIN_SCK", "N6_SCK"), ("CS", "~{ADIN_CS}", "~{N6_CS}")):
    (la, laya, va), (ln, layn, vn) = L(a), L(n); res[name] = la + ln + 0.86
    print("%-5s ADIN side %5.1f mm (%s; %d vias)  N6 side %4.1f mm  total with the resistor %5.1f mm" % (name, la, ", ".join("%s %.1f" % kv for kv in sorted(laya.items())), va, ln, res[name]))
print("longest %.1f mm, spread %.1f mm (plan: 20 mm or less, spread 5 mm or less)" % (max(res.values()), max(res.values()) - min(res.values())))
