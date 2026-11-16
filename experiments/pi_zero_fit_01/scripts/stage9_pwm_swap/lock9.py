"""Stage 9 lock check: stage 8's (lock8.py), and a second comparison with the stage-8 head board. Passes only if nothing of the stage-2c board is missing
(but the orphan via of phase K and stage 6's two dangling converter stubs), nothing is changed but
  - the footprints earlier stages moved on instruction (s3lib.MOVED_OK / TURNED_OK, FID5 / FID6, R9 to the top),
  - J1: pad nets by the schematic, same place (all listed; pins 12 / 32 / 33 must end on MOTOR_IN2 / GPIO12 / MOTOR_IN1: stage 8, job 3 and stage 9),
  - H1..H4 (stage 8, job 1): same place, turn, side, footprint name and (no) nets; the one pad is 2.75 mm, 2.75 mm drill, not plated,
and the added footprints are exactly NEW.
Against the head board (stage 8, 61e1a9d), in a child process: every footprint, zone and copper graphic the same but J1's nets on pins 12 / 33;
every track and via the same but those on MOTOR_IN1 / MOTOR_IN2.
Usage: <KiCad python> lock9.py <stage-2c board> <board> <head board>"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage3_routing'))
import s3lib, pcbnew
if sys.argv[1] == '--head':                     # own process: a second LoadBoard pair
    h = s3lib.snapshot(pcbnew.LoadBoard(sys.argv[2])); n = s3lib.snapshot(pcbnew.LoadBoard(sys.argv[3])); bad = []; pins = []; tr = {'gone': 0, 'new': 0}
    for k in set(h) | set(n):
        x, y = h.get(k), n.get(k)
        if x == y: continue
        if k[0] == 'T':
            if all(v is None or s3lib.sn(v[-1]) in ('MOTOR_IN1', 'MOTOR_IN2') for v in (x, y)) and (x is None or y is None): tr['gone' if y is None else 'new'] += 1
            else: bad.append((k, x, y))
        elif k[0] == 'F' and x and y and x[0] == 'J1' and x[:6] == y[:6]:
            pins = [(p, s3lib.sn(a), s3lib.sn(c)) for (p, a), (p2, c) in zip(x[7], y[7]) if a != c]
            if pins != [('12', 'MOTOR_IN1', 'MOTOR_IN2'), ('33', 'MOTOR_IN2', 'MOTOR_IN1')]: bad.append((k, pins))
        else: bad.append((k, x, y))
    print('  against the head board: J1 %s; tracks + vias on MOTOR_IN1 / MOTOR_IN2: %d gone, %d new; other differences: %d' % (', '.join('pin %s %s -> %s' % p for p in pins), tr['gone'], tr['new'], len(bad)))
    for x in bad[:20]: print('   !', x)
    sys.exit(0 if not bad and pins else 1)
DROP = ('T 89214ad6-26b4-421d-8de0-e5b3b5f7cfb4', 'T 1745e174-32ff-4215-9962-73b7e474f208')
NEW = {'J15', 'J16', 'J17', 'J18', 'J19', 'TP40', 'TP41', 'TP42', 'TP43'}
HOLE = pcbnew.FromMM(2.75)
a = s3lib.snapshot(pcbnew.LoadBoard(sys.argv[1])); bb = pcbnew.LoadBoard(sys.argv[2]); b = s3lib.snapshot(bb)
holes = {f.GetReference(): [(p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH, p.GetDrillSize().x, p.GetDrillSize().y, p.GetSize(pcbnew.F_Cu).x) for p in f.Pads()] for f in bb.GetFootprints() if f.GetReference() in ('H1', 'H2', 'H3', 'H4')}
for k in a:
    if k not in b and k in DROP + s3lib.REMOVED_OK: print('  removed on instruction:', k, a[k][:5])
j1 = []
missing = [k for k in a if k not in b and k not in s3lib.REMOVED_OK + DROP]; bad = []; mm = s3lib.mm
for k in a:
    if k not in b or a[k] == b[k]: continue
    if k[0] != 'F': bad.append(k); continue
    ref = a[k][0]
    if ref in s3lib.MOVED_OK + ('FID5', 'FID6') and a[k][3:6] == b[k][3:6] and a[k][7] == b[k][7]: tag = 'moved on instruction'
    elif ref in s3lib.TURNED_OK and ref != 'R9' and a[k][4:6] == b[k][4:6] and a[k][7] == b[k][7]: tag = 'moved on instruction'
    elif ref == 'R9' and a[k][5] == b[k][5] and a[k][7] == b[k][7]: tag = 'moved on instruction (stage 6, side %s -> %s)' % ('bottom' if a[k][4] else 'top', 'bottom' if b[k][4] else 'top')
    elif ref == 'J1' and a[k][1:6] == b[k][1:6]: tag = 'pad nets by the schematic, same place'
    elif ref in holes and a[k][:6] == b[k][:6] and a[k][7] == b[k][7] and holes[ref] == [(True, HOLE, HOLE, HOLE)]: tag = 'hole 2.75 mm, not plated (stage 8), same place'
    else: bad.append(k); continue
    print('  %s: %s (%.2f, %.2f) %.0f deg -> (%.2f, %.2f) %.0f deg' % (tag, ref, mm(a[k][1]) - s3lib.DX, mm(a[k][2]) - s3lib.DY, a[k][3], mm(b[k][1]) - s3lib.DX, mm(b[k][2]) - s3lib.DY, b[k][3]))
    if ref == 'J1':
        for (n, x), (n2, y) in zip(a[k][7], b[k][7]):
            if x != y: print('        J1 pin %s: %s -> %s' % (n, x.split('/')[-1] or '(none)', y.split('/')[-1] or '(none)')); j1.append((n, x.split('/')[-1], y.split('/')[-1]))
added = {b[k][0] for k in b if k not in a and k[0] == 'F'}
cnt = lambda s, c: sum(1 for k in s if k[0] == c)
print('  input items: %d footprints, %d tracks+vias, %d zones, %d copper graphics' % (cnt(a, 'F'), cnt(a, 'T'), cnt(a, 'Z'), cnt(a, 'D')))
print('  missing: %d   changed (not on the lists): %d   added footprints: %s   added tracks+vias: %d, zones: %d' % (len(missing), len(bad), sorted(added), sum(1 for k in b if k not in a and k[0] == 'T'), sum(1 for k in b if k not in a and k[0] == 'Z')))
for k in (missing + bad)[:20]: print('   !', k, a[k], b.get(k))
import subprocess
head = subprocess.run([sys.executable, '-B', os.path.abspath(__file__), '--head', sys.argv[3], sys.argv[2]], capture_output=True, text=True)
print('\n'.join(l for l in head.stdout.splitlines() if l.startswith('  ')))
ok = not missing and not bad and added == NEW and head.returncode == 0 and {n: y for n, x, y in j1 if n in ('12', '32', '33')} == {'12': 'MOTOR_IN2', '32': 'GPIO12', '33': 'MOTOR_IN1'}
print('  LOCK', 'PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)
