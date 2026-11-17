"""Stage 21 lock check. Usage: <KiCad python> lock21.py <board of 4676018> <new board>
Allowed differences: the swapped connectors (SWAP in job21.py) themselves; tracks / vias gone or new only on those connectors' nets and
within 6 mm of their courtyards; board silkscreen texts named after a swapped connector moved straight north. Everything else
(footprints by reference: position, angle, side, footprint, pad geometry and nets; tracks, vias, zones, copper graphics, board
drawings on every layer) identical, and every net has the same set of (reference, pad) members."""
import sys, os, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage3_routing'))
import s3lib, pcbnew
SW = ('J9',)
def load(p):
    b = pcbnew.LoadBoard(p); s = s3lib.snapshot(b)
    F = {v[0]: v for k, v in s.items() if k[0] == 'F'}; R = {k: v for k, v in s.items() if k[0] != 'F'}
    nets = collections.defaultdict(set)
    for f in b.GetFootprints():
        for q in f.Pads():
            if q.GetNetname(): nets[q.GetNetname()].add((f.GetReference(), q.GetNumber()))
    crt = {}
    for f in b.GetFootprints():
        if f.GetReference() in SW: bb = f.GetCourtyard(pcbnew.F_CrtYd).BBox(); crt[f.GetReference()] = (s3lib.N(bb.GetPosition()), s3lib.N(bb.GetEnd()))
    dr = {}
    for d in b.GetDrawings():
        txt = d.GetText() if d.GetClass() == 'PCB_TEXT' else ''
        bb = d.GetBoundingBox(); dr[d.m_Uuid.AsString()] = (d.GetClass(), d.GetLayer(), txt, bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom())
    return F, R, nets, crt, dr
F0, R0, N0, C0, D0 = load(sys.argv[1]); F1, R1, N1, C1, D1 = load(sys.argv[2])
bad = []
for r in set(F0) | set(F1):
    if r in SW: continue
    if F0.get(r) != F1.get(r): bad.append(('footprint', r, F0.get(r), F1.get(r)))
nets = {s3lib.sn(n) for n, m in N0.items() if any(x[0] in SW for x in m)}
def near(t):
    pts = [(t[1], t[2])] if t[0] == 'via' else [(t[1], t[2]), (t[3], t[4])]
    for (x0, y0), (x1, y1) in list(C0.values()) + list(C1.values()):
        if all(x0 - 6 <= pcbnew.ToMM(x) - s3lib.DX <= x1 + 6 and y0 - 6 <= pcbnew.ToMM(y) - s3lib.DY <= y1 + 6 for x, y in pts): return True
    return False
gone, new = [], []
for k in set(R0) | set(R1):
    a, c = R0.get(k), R1.get(k)
    if a == c: continue
    if k[0] == 'T' and not (a and c) and s3lib.sn((a or c)[-1]) in nets and near(a or c): (gone if a else new).append(a or c); continue
    bad.append(('item', k, a, c))
for k in set(D0) | set(D1):
    a, c = D0.get(k), D1.get(k)
    if a == c: continue
    if a and c and a[2] in SW and a[:4] == c[:4] and a[5] == c[5] and c[4] < a[4]: print('    board text %r moved %.3f mm north' % (a[2], pcbnew.ToMM(a[4] - c[4]))); continue
    bad.append(('drawing', k, a, c))
for n in set(N0) | set(N1):
    if N0.get(n) != N1.get(n): bad.append(('net members', n, N0.get(n), N1.get(n)))
M = lambda t: '(%.3f, %.3f)' % (pcbnew.ToMM(t[1]) - s3lib.DX, pcbnew.ToMM(t[2]) - s3lib.DY)
E = lambda t: '(%.3f, %.3f)' % (pcbnew.ToMM(t[3]) - s3lib.DX, pcbnew.ToMM(t[4]) - s3lib.DY)
for lab, L in (('removed', gone), ('added', new)):
    for t in sorted(L): print('    %s %s %s %s' % (lab, s3lib.sn(t[-1]), 'via ' + M(t) if t[0] == 'via' else '%s-%s w %.2f layer %d' % (M(t), E(t), pcbnew.ToMM(t[5]), t[6]), ''))
cnt = lambda d, c: sum(1 for k in d if k[0] == c)
print('  compared: %d footprints, %d tracks + vias, %d zones, %d copper graphics, %d board drawings, %d nets' % (len(F0), cnt(R0, 'T'), cnt(R0, 'Z'), cnt(R0, 'D'), len(D0), len(N0)))
print('  swapped: %s; tracks / vias removed %d, added %d (nets %s, all within 6 mm of the connectors); other differences: %d' % (SW, len(gone), len(new), sorted({s3lib.sn(t[-1]) for t in gone + new}), len(bad)))
for x in bad[:20]: print('   !', str(x)[:300])
print('  LOCK', 'PASS' if not bad else 'FAIL'); sys.exit(0 if not bad else 1)
