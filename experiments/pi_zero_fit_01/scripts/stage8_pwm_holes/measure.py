"""Stage 8, job 3: the two PWM nets (and the spare-pad net), measured on a board. New-frame mm; distances in plan view, copper edge to copper edge.
  per net: layers and lengths, vias; minimum distance of any track / via of the net to Y1's pads (all four, and the two crystal pads 1 / 3) and to
  U1's pads and to the pads on the converter's switch node 5V_Buck_SW. GND fill above / below and slot crossings: stage 6's checks.py (same run.sh).
Usage: <KiCad python> measure.py <board> NET..."""
import sys, pcbnew
DX, DY = 113.47, 89.34; mm = pcbnew.ToMM; sn = lambda n: n.split('/')[-1]
b = pcbnew.LoadBoard(sys.argv[1]); fp = {f.GetReference(): f for f in b.GetFootprints()}
def shape(item, layer): return item.GetEffectiveShape(layer)
def dist(t, pads):
    best = (1e9, '')
    for ref, p in pads:
        for L in ([t.GetLayer()] if t.GetClass() != 'PCB_VIA' else [pcbnew.F_Cu, pcbnew.B_Cu]):
            pl = L if p.IsOnLayer(L) else (pcbnew.B_Cu if p.IsOnLayer(pcbnew.B_Cu) else pcbnew.F_Cu)      # plan view: the pad's own layer
            a = shape(t, L); c = shape(p, pl)
            ok, d = False, 0
            try: d = a.GetClearance(c); ok = True
            except Exception: pass
            if not ok:
                e = t.GetStart(); q = p.GetPosition(); d = int(((e.x - q.x) ** 2 + (e.y - q.y) ** 2) ** 0.5)
            if mm(d) < best[0]: best = (mm(d), '%s.%s' % (ref, p.GetNumber()))
    return best
y1 = [('Y1', p) for p in fp['Y1'].Pads()]; y1x = [x for x in y1 if x[1].GetNumber() in ('1', '3')]; u1 = [('U1', p) for p in fp['U1'].Pads()]
sw = [(f.GetReference(), p) for f in b.GetFootprints() for p in f.Pads() if sn(p.GetNetname()) == '5V_Buck_SW']
print('Y1 pads:', ', '.join('%s %s (%.2f, %.2f)' % (p.GetNumber(), sn(p.GetNetname()), mm(p.GetPosition().x) - DX, mm(p.GetPosition().y) - DY) for _, p in y1), '(%s)' % ('bottom' if fp['Y1'].IsFlipped() else 'top'))
for net in sys.argv[2:]:
    tr = [t for t in b.GetTracks() if sn(t.GetNetname()) == net]
    if not tr: print('%-10s not on this board' % net); continue
    lay = {}
    for t in tr:
        if t.GetClass() != 'PCB_VIA': lay[t.GetLayerName()] = lay.get(t.GetLayerName(), 0) + mm(t.GetLength())
    vias = [t for t in tr if t.GetClass() == 'PCB_VIA']
    dy = min(dist(t, y1) for t in tr); dx = min(dist(t, y1x) for t in tr); du = min(dist(t, u1) for t in tr)
    ds = min(dist(t, sw) for t in tr)
    pads = ['%s.%s' % (f.GetReference(), p.GetNumber()) for f in b.GetFootprints() for p in f.Pads() if sn(p.GetNetname()) == net]
    print('%-10s pads %s | %s | total %.1f mm, %d via(s) | nearest Y1 pad %.2f mm (%s), crystal pad 1 / 3 %.2f mm (%s) | nearest U1 pad %.2f mm (%s) | nearest switch-node pad (5V_Buck_SW) %.2f mm (%s)' % (
        net, ' '.join(pads), '; '.join('%s %.1f mm' % (k, v) for k, v in sorted(lay.items())), sum(lay.values()), len(vias), dy[0], dy[1], dx[0], dx[1], du[0], du[1], ds[0], ds[1]))
