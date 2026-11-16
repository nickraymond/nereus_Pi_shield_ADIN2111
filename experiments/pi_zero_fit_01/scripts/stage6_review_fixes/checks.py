"""Stage 6 measurements on our own tracks (uuid not in the stage-2c board), with the electrical review's methods (its retpath.py / slots.py / sw.py):
  per net and layer: length; length with no GND fill on the GND plane above / below (inner and bottom layers); Internal 1 length lying
  under a top-layer BM power trunk, motor output, switch node, P_IN or VBUS track or pad (centre-line hit test, 0.1 mm steps);
  slot crossings: runs of 0.2 mm or more with no GND fill that are not within 0.75 mm of a via or 1.7 mm of a through hole (the review's radii) (antipads);
  Internal 1 / Internal 2 length within 0.15 / 0.3 mm (plan view, edge to edge) of 5V_Buck_SW copper.
Usage: <KiCad python> checks.py <board> <stage-2c board>      (new-frame mm)"""
import pcbnew, sys, re, collections
DX, DY = 113.47, 89.34; mm = pcbnew.ToMM; sn = lambda n: n.split('/')[-1]
base = set(re.findall(r'\(uuid "([0-9a-f-]{36})"\)', open(sys.argv[2]).read()))
b = pcbnew.LoadBoard(sys.argv[1]); P = lambda p: (round(mm(p.x) - DX, 2), round(mm(p.y) - DY, 2))
lid = {b.GetLayerName(l): l for l in b.GetEnabledLayers().CuStack()}; TOP, I1, GP, I2, BOT = (lid[n] for n in ('Top Layer', 'Internal 1', 'GND Plane', 'Internal 2', '6 Bottom Layer'))
gnd = [z.GetFilledPolysList(GP) for z in b.Zones() if not z.GetIsRuleArea() and z.IsOnLayer(GP) and sn(z.GetNetname()) == 'GND']
isg = lambda pt: any(f.Contains(pt) for f in gnd)
holes = [(t.GetPosition(), 0.75) for t in b.GetTracks() if t.GetClass() == 'PCB_VIA'] + [(p.GetPosition(), 1.7) for f in b.GetFootprints() for p in f.Pads() if p.GetDrillSize().x > 0]
def nearhole(pt):
    for h, r in holes:
        R = pcbnew.FromMM(r)
        if abs(h.x - pt.x) < R and abs(h.y - pt.y) < R and (h.x - pt.x) ** 2 + (h.y - pt.y) ** 2 < R * R: return True
    return False
noisy = lambda n: n.startswith('BM') and 'DATA' not in n or n.startswith('MOTOR_OUT') or n in ('5V_Buck_SW', 'P_IN', 'VBUS')
ntr = [(sn(t.GetNetname()), t) for t in b.GetTracks() if t.GetClass() != 'PCB_VIA' and t.GetLayer() == TOP and noisy(sn(t.GetNetname()))]
npad = [(sn(p.GetNetname()) + '@' + f.GetReference(), p) for f in b.GetFootprints() for p in f.Pads() if p.IsOnLayer(TOP) and noisy(sn(p.GetNetname())) and sn(p.GetNetname()) not in ('P_IN', 'VBUS')]
sw = [t for t in b.GetTracks() if t.GetClass() == 'PCB_TRACK' and sn(t.GetNetname()) == '5V_Buck_SW'] + [p for f in b.GetFootprints() for p in f.Pads() if sn(p.GetNetname()) == '5V_Buck_SW']
res = collections.defaultdict(collections.Counter); spots = collections.defaultdict(list); slots = []
for t in b.GetTracks():
    if t.GetClass() == 'PCB_VIA' or t.m_Uuid.AsString() in base: continue
    L = t.GetLayer(); n = sn(t.GetNetname()); ln = b.GetLayerName(L); s, e = t.GetStart(), t.GetEnd(); length = mm(t.GetLength()); k = max(1, int(length / 0.1)); d = length / (k + 1); run = []
    for i in range(k + 2):
        pt = pcbnew.VECTOR2I(int(s.x + (e.x - s.x) * min(i, k) / k), int(s.y + (e.y - s.y) * min(i, k) / k)); g = isg(pt)
        if i <= k:
            res[(n, ln)]['len'] += d
            if L in (I1, I2, BOT) and not g: res[(n, ln)]['noGND'] += d; spots[(n, ln, 'noGND')].append(P(pt))
            if L == I1:
                hit = [nn for nn, tt in ntr if tt.HitTest(pt, 0)] or [nn for nn, pp in npad if pp.HitTest(pt, 0)]
                if hit: res[(n, ln)]['under_' + hit[0]] += d; spots[(n, ln, 'under ' + hit[0])].append(P(pt))
            if L in (I1, I2) and n != 'GND':
                for marg in (0.15, 0.3):
                    if any(x.HitTest(pt, pcbnew.FromMM(marg + mm(t.GetWidth()) / 2)) for x in sw): res[(n, ln)]['SW%.2f' % marg] += d
        if i <= k and L in (TOP, I1, I2) and not g and not nearhole(pt): run.append(P(pt))
        else:
            if len(run) >= 2: slots.append((n, ln, run[0], run[-1], round(len(run) * d, 2), mm(t.GetWidth())))
            run = []
tot = collections.Counter()
for k in sorted(res):
    c = res[k]; tot[k[0]] += c['len']; print('%-34s %-14s %6.1f  %s' % (k[0], k[1], c['len'], ' '.join('%s=%.1f' % (a, v) for a, v in sorted(c.items()) if a != 'len' and v >= 0.2)))
print('--- net totals (own copper, mm):', ', '.join('%s %.1f' % (n, tot[n]) for n in ('I2C3_SCL', 'I2C3_SDA', 'MOTOR_nSLEEP', 'ADIN_TIMER', 'MOTOR_IN1', 'MOTOR_IN2', 'PAYLOAD_EN', 'ADIN_MISO', 'CFG0_STRAP', 'CFG1_STRAP', 'GPIO17') if n in tot))
print('--- where')
for k in sorted(spots):
    if len(spots[k]) >= 3: xs = [p[0] for p in spots[k]]; ys = [p[1] for p in spots[k]]; print('  %-60s x %.1f..%.1f y %.1f..%.1f n=%d' % (k, min(xs), max(xs), min(ys), max(ys), len(xs)))
print('--- slot crossings (no GND fill above / below, away from holes)')
for o in sorted(slots, key=lambda x: (x[2][0], x[2][1])): print('  %-22s %-12s %s .. %s  %.2f mm  w %.2f' % o)
