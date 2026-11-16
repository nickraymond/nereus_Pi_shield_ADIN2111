"""Stage 11 lock check: stage 9's (lock9.py) against the stage-2c board, with J4 added once job 3 is built, and a comparison with the stage-9 head
board 2fd2945. Passes only if nothing of the stage-2c board is missing (but the orphan via of phase K and stage 6's two dangling stubs), nothing is
changed but
  - the footprints earlier stages moved on instruction (s3lib.MOVED_OK / TURNED_OK, FID5 / FID6, R9 to the top),
  - J1: pad nets by the schematic, same place (pins 12 / 32 / 33 must end on MOTOR_IN2 / GPIO12 / MOTOR_IN1),
  - H1..H4 (stage 8): one pad 2.75 mm, 2.75 mm drill, not plated,
  - J4 (job 3 only): same place, turn, side, pads (number, place, size, net); footprint name J4NEW; both holes 1.3 mm round, plated,
and the added footprints are exactly NEW.
Against the head board, in a child process: every footprint, track, via, zone and copper graphic the same, and every pad's shape, size, drill, kind
and layers the same; job 3: but J4's footprint name and its two drills (1.1 -> 1.3 mm).
Usage: <KiCad python> lock11.py <stage-2c board> <board> <head board> <job 1|2|3>"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage3_routing'))
import s3lib, pcbnew
J4OLD = 'nereus:WirePads_1x02_P3.20mm_Oval2.2x3.3mm_Drill1.1mm'; J4NEW = 'nereus:WirePads_1x02_P3.20mm_Oval2.2x3.3mm_Drill1.3mm'
def padtab(b): return {(f.GetReference(), p.GetNumber(), p.GetPosition().x, p.GetPosition().y): (p.GetShape(pcbnew.F_Cu), p.GetSize(pcbnew.F_Cu).x, p.GetSize(pcbnew.F_Cu).y, p.GetDrillSize().x, p.GetDrillSize().y, p.GetDrillShape(), p.GetAttribute(), p.GetLayerSet().FmtHex(), round(p.GetOrientationDegrees(), 3)) for f in b.GetFootprints() for p in f.Pads()}
if sys.argv[1] == '--head':                     # own process: a second LoadBoard pair
    job = int(sys.argv[4]); hb, nb = pcbnew.LoadBoard(sys.argv[2]), pcbnew.LoadBoard(sys.argv[3]); h, n = s3lib.snapshot(hb), s3lib.snapshot(nb); bad = []; j4 = ''
    for k in set(h) | set(n):
        x, y = h.get(k), n.get(k)
        if x == y: continue
        if job >= 3 and k[0] == 'F' and x and y and x[0] == 'J4' and x[:5] == y[:5] and x[6:] == y[6:] and (x[5], y[5]) == (J4OLD, J4NEW): j4 = 'J4 footprint name ...Drill1.1mm -> ...Drill1.3mm; '
        else: bad.append((k, x, y))
    pa, pb = padtab(hb), padtab(nb); pd = sorted(k for k in set(pa) | set(pb) if pa.get(k) != pb.get(k)); want = []
    if job >= 3: want = sorted(k for k in pa if k[0] == 'J4'); okp = pd == want and all(pa[k][:3] == pb[k][:3] and pa[k][5:] == pb[k][5:] and pb[k][3:5] == (1300000, 1300000) for k in want)
    else: okp = not pd
    cnt = lambda s, c: sum(1 for k in s if k[0] == c)
    print('  against the head board: %d footprints, %d tracks + vias, %d zones, %d copper graphics, %d pads compared; %spads that differ: %s; other differences: %d' % (cnt(h, 'F'), cnt(h, 'T'), cnt(h, 'Z'), cnt(h, 'D'), len(pa), j4,
          ', '.join('%s pad %s drill %.2f -> %.2f mm' % (k[0], k[1], pa[k][3] / 1e6, pb[k][3] / 1e6) for k in pd) or 'none', len(bad)))
    for x in bad[:20]: print('   !', x)
    sys.exit(0 if not bad and okp and (job < 3 or j4) else 1)
JOB = int(sys.argv[4])
DROP = ('T 89214ad6-26b4-421d-8de0-e5b3b5f7cfb4', 'T 1745e174-32ff-4215-9962-73b7e474f208')
NEW = {'J15', 'J16', 'J17', 'J18', 'J19', 'TP40', 'TP41', 'TP42', 'TP43'}
HOLE = pcbnew.FromMM(2.75)
a = s3lib.snapshot(pcbnew.LoadBoard(sys.argv[1])); bb = pcbnew.LoadBoard(sys.argv[2]); b = s3lib.snapshot(bb)
holes = {f.GetReference(): [(p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH, p.GetDrillSize().x, p.GetDrillSize().y, p.GetSize(pcbnew.F_Cu).x) for p in f.Pads()] for f in bb.GetFootprints() if f.GetReference() in ('H1', 'H2', 'H3', 'H4')}
j4d = [(p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH, p.GetDrillSize().x, p.GetDrillSize().y, p.GetSize(pcbnew.F_Cu).x, p.GetSize(pcbnew.F_Cu).y) for f in bb.GetFootprints() if f.GetReference() == 'J4' for p in f.Pads()]
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
    elif JOB >= 3 and ref == 'J4' and a[k][:5] == b[k][:5] and a[k][6:] == b[k][6:] and b[k][5] == J4NEW and j4d == [(True, 1300000, 1300000, 2200000, 3300000)] * 2: tag = 'holes 1.3 mm round, plated, pads 2.2 x 3.3 mm, same place (stage 11); footprint name ...Drill1.3mm'
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
head = subprocess.run([sys.executable, '-B', os.path.abspath(__file__), '--head', sys.argv[3], sys.argv[2], sys.argv[4]], capture_output=True, text=True)
print('\n'.join(l for l in head.stdout.splitlines() if l.startswith('  ')) or head.stderr[-800:])
ok = not missing and not bad and added == NEW and head.returncode == 0 and {n: y for n, x, y in j1 if n in ('12', '32', '33')} == {'12': 'MOTOR_IN2', '32': 'GPIO12', '33': 'MOTOR_IN1'}
print('  LOCK', 'PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)
