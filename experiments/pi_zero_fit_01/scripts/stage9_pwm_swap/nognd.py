"""Stage 9 (copy of stage 8's nognd.py): where a net's inner-layer tracks have no GND fill on the GND plane (centre line, 0.1 mm steps, the test of stage 6's checks.py), as runs.
Usage: <KiCad python> nognd.py <board> NET..."""
import sys, pcbnew
DX, DY = 113.47, 89.34; mm = pcbnew.ToMM; sn = lambda n: n.split('/')[-1]
b = pcbnew.LoadBoard(sys.argv[1]); GP = [l for l in b.GetEnabledLayers().CuStack() if b.GetLayerName(l) == 'GND Plane'][0]
gnd = [z.GetFilledPolysList(GP) for z in b.Zones() if not z.GetIsRuleArea() and z.IsOnLayer(GP) and sn(z.GetNetname()) == 'GND']
P = lambda p: (round(mm(p.x) - DX, 2), round(mm(p.y) - DY, 2))
for net in sys.argv[2:]:
    tot = 0
    for t in b.GetTracks():
        if t.GetClass() == 'PCB_VIA' or sn(t.GetNetname()) != net or 'Internal' not in t.GetLayerName(): continue
        s, e = t.GetStart(), t.GetEnd(); L = mm(t.GetLength()); k = max(1, int(L / 0.05)); run = []
        for i in range(k + 2):
            pt = pcbnew.VECTOR2I(int(s.x + (e.x - s.x) * min(i, k) / k), int(s.y + (e.y - s.y) * min(i, k) / k))
            if i <= k and not any(f.Contains(pt) for f in gnd): run.append(P(pt))
            else:
                if len(run) > 1:
                    d = ((run[-1][0] - run[0][0]) ** 2 + (run[-1][1] - run[0][1]) ** 2) ** 0.5; tot += d
                    print('  %-10s %-10s no GND fill %s .. %s  %.2f mm' % (net, t.GetLayerName(), run[0], run[-1], d))
                run = []
    print('  %-10s total %.1f mm' % (net, tot))
