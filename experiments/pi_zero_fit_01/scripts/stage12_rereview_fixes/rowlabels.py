"""Every pad-row label on the board against the pad it names: the text must be the one the pad's net gives (GPIOnn -> nn, PI_5V -> 5V, PI_3V3 -> 3V3,
GND -> GND), on both sides, and stand under its own pad (|dx| <= 0.6 mm, 0.6 .. 1.2 mm south of the pad's south edge to the text's middle).
Usage: <KiCad python> rowlabels.py <board> <silk report.json>"""
import sys, os, json, re, pcbnew
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage3_routing'))
import s3lib
b = pcbnew.LoadBoard(sys.argv[1]); rep = json.load(open(sys.argv[2])); ok = 0; bad = []
texts = [(d.GetText(), s3lib.N(d.GetPosition()), d.GetLayer()) for d in b.GetDrawings() if d.GetClass() == 'PCB_TEXT' and d.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS)]
fps = {f.GetReference(): f for f in b.GetFootprints()}
for l in rep['labels']:
    m = re.fullmatch(r'(J1[5-9]) pad (\d)', l[0])
    if not m: continue
    p = [p for p in fps[m.group(1)].Pads() if p.GetNumber() == m.group(2)][0]; net = s3lib.sn(p.GetNetname()); g = re.fullmatch(r'GPIO(\d+)', net)
    want = g.group(1) if g else {'PI_5V': '5V', 'PI_3V3': '3V3', 'GND': 'GND'}[net]; c = s3lib.N(p.GetPosition()); r = s3lib.mm(p.GetSize(pcbnew.F_Cu).y) / 2
    lay = pcbnew.F_SilkS if l[7] == 'top' else pcbnew.B_SilkS
    hit = [t for t in texts if t[2] == lay and t[0] == want == l[1] and abs(t[1][0] - l[2]) < 0.006 and abs(t[1][1] - l[3]) < 0.006 and abs(t[1][0] - c[0]) <= 0.6 and 0.6 <= t[1][1] - (c[1] + r) <= 1.2]
    if len(hit) == 1: ok += 1
    else: bad.append((l, net, c))
print('pad-row labels on the board against their pads (text by the pad net, place under the pad): %d OK, %d not' % (ok, len(bad)))
for x in bad: print('   !', x)
sys.exit(1 if bad else 0)
