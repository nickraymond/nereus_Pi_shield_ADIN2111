"""The pad row J15..J19 against header J1 and against other copper. New-frame mm. Usage: <KiCad python> row_measure.py <board>
Per row pad: copper gap and solder-mask web to the nearest J1 pad (both round: centre distance less the radii; mask opening = pad + the pad's own
mask expansion as pcbnew gives it), annular ring; hole edge to the nearest copper of another net, per layer: tracks, vias, pads that are flashed on
that layer (pcbnew's FlashLayer), zone fills (every zone, ours too), copper graphics."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage3_routing'))
import s3lib, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); mm = pcbnew.ToMM; N = s3lib.N; sn = s3lib.sn; ROW = ('J15', 'J16', 'J17', 'J18', 'J19')
cu = list(b.GetEnabledLayers().CuStack()); name = {l: b.GetLayerName(l) for l in cu}
fps = {f.GetReference(): f for f in b.GetFootprints()}
j1 = [(N(p.GetPosition()), mm(p.GetSize(pcbnew.F_Cu).x) / 2, mm(p.GetSolderMaskExpansion(pcbnew.F_Cu)), p.GetNumber(), sn(p.GetNetname())) for p in fps['J1'].Pads()]
items = {l: [] for l in cu}          # layer -> (kind, net, data, desc)
for t in b.GetTracks():
    net = sn(t.GetNetname())
    if t.GetClass() == 'PCB_VIA':
        p = N(t.GetStart())
        for l in cu: items[l].append(('cap', net, (p, p, mm(t.GetWidth(l)) / 2), 'via %s (%.2f, %.2f)' % (net, *p)))
    else: a, c = N(t.GetStart()), N(t.GetEnd()); items[t.GetLayer()].append(('cap', net, (a, c, mm(t.GetWidth()) / 2), 'track %s (%.2f, %.2f)-(%.2f, %.2f)' % (net, *a, *c)))
for f in b.GetFootprints():
    for p in f.Pads():
        if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH: continue
        bb = p.GetBoundingBox(); x0, y0 = N(bb.GetPosition()); x1, y1 = N(bb.GetEnd()); w, h = x1 - x0, y1 - y0; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if p.GetShape(pcbnew.F_Cu) in (pcbnew.PAD_SHAPE_CIRCLE, pcbnew.PAD_SHAPE_OVAL): rr = min(w, h) / 2; it = ('cap', ((cx - (w / 2 - rr), cy - (h / 2 - rr)), (cx + (w / 2 - rr), cy + (h / 2 - rr)), rr))
        else: it = ('poly', [[(x0, y0), (x1, y0), (x1, y1), (x0, y1)]])
        for l in p.GetLayerSet().CuStack():
            if l in items and p.FlashLayer(l): items[l].append((it[0], sn(p.GetNetname()), it[1], 'pad %s.%s %s' % (f.GetReference(), p.GetNumber(), sn(p.GetNetname()))))
for z in b.Zones():
    if z.GetIsRuleArea(): continue
    for l in z.GetLayerSet().CuStack():
        ps = z.GetFilledPolysList(l)
        for i in range(ps.OutlineCount()):
            rings = [[N(ps.Outline(i).CPoint(k)) for k in range(ps.Outline(i).PointCount())]] + [[N(ps.Hole(i, hh).CPoint(k)) for k in range(ps.Hole(i, hh).PointCount())] for hh in range(ps.HoleCount(i))]
            items[l].append(('poly', sn(z.GetNetname()), rings, 'zone fill %s' % (sn(z.GetNetname()) or '(no net)')))
for d in b.GetDrawings():
    if d.GetLayer() in items and d.GetClass() == 'PCB_SHAPE':
        bb = d.GetBoundingBox(); x0, y0 = N(bb.GetPosition()); x1, y1 = N(bb.GetEnd()); items[d.GetLayer()].append(('poly', sn(d.GetNetname()), [[(x0, y0), (x1, y0), (x1, y1), (x0, y1)]], 'copper shape'))
worst = {l: (9, '') for l in cu}; gmin = (9, ''); wmin = (9, ''); rings_ = set(); rows = []
for ref in ROW:
    for p in sorted(fps[ref].Pads(), key=lambda p: p.GetNumber()):
        c = N(p.GetPosition()); r = mm(p.GetSize(pcbnew.F_Cu).x) / 2; hr = mm(p.GetDrillSize().x) / 2; me = mm(p.GetSolderMaskExpansion(pcbnew.F_Cu)); net = sn(p.GetNetname()); tag = '%s.%s %s' % (ref, p.GetNumber(), net)
        g, w, who = min((math.hypot(c[0] - q[0], c[1] - q[1]) - r - qr, math.hypot(c[0] - q[0], c[1] - q[1]) - r - qr - me - qm, 'J1 pin %s %s' % (n_, nn.replace('unconnected-(J1-', '(').replace('{slash}', '/'))) for q, qr, qm, n_, nn in j1)
        rings_.add(round(r - hr, 3)); gmin = min(gmin, (g, tag + ' / ' + who)); wmin = min(wmin, (w, tag + ' / ' + who)); per = []
        for l in cu:
            best = (9, '')
            for kind, n2, data, desc in items[l]:
                if n2 == net: continue
                if kind == 'cap': d_ = s3lib._pt_seg(c[0], c[1], data[0][0], data[0][1], data[1][0], data[1][1]) - data[2] - hr
                else:
                    xs = [q[0] for q in data[0]]; ys = [q[1] for q in data[0]]
                    if min(xs) - c[0] > 3 or c[0] - max(xs) > 3 or min(ys) - c[1] > 3 or c[1] - max(ys) > 3: continue
                    d_ = s3lib.seg_poly(c, c, data) - hr
                if d_ < best[0]: best = (d_, desc)
            per.append(best); worst[l] = min(worst[l], (best[0], tag + ' / ' + best[1]))
        rows.append('  %-16s (%.2f, %.2f) pad %.2f hole %.2f ring %.3f mask +%.3f | J1 gap %.3f web %.3f (%s) | hole to copper %s' % (tag, *c, 2 * r, 2 * hr, r - hr, me, g, w, who[:22], '  '.join('%.3f' % x[0] for x in per)))
print('\n'.join(rows))
print('row pad to J1 pad: least copper gap %.3f mm (%s); least mask web %.3f mm (%s); ring %s mm' % (gmin[0], gmin[1], wmin[0], wmin[1], sorted(rings_)))
for l in cu: print('hole to other-net copper, least on %-15s %.3f mm  (%s)' % (name[l], worst[l][0], worst[l][1]))
