"""Stage 5 lock check: stage 3's snapshot comparison (s3lib.snapshot) against the stage-2c board, with stage 4's own, listed changes.
Passes only if: nothing of the input is missing (but the one orphan via of phase K); nothing is changed but the footprints stage 3
moved on instruction, FID5 / FID6 (moved 2.4 mm north for J14) and J1 (six pad nets, same place); and the added footprints are exactly NEW.
Usage: <KiCad python> lock4.py <stage-2c board> <board>"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage3_routing'))
import s3lib, pcbnew
NEW = {'J15', 'J16', 'J17', 'J18', 'J19', 'TP40', 'TP41', 'TP42', 'TP43'}
a = s3lib.snapshot(pcbnew.LoadBoard(sys.argv[1])); bb = pcbnew.LoadBoard(sys.argv[2]); b = s3lib.snapshot(bb)
missing = [k for k in a if k not in b and k not in s3lib.REMOVED_OK]; bad = []; mm = s3lib.mm
for k in a:
    if k not in b or a[k] == b[k]: continue
    if k[0] != 'F': bad.append(k); continue
    ref = a[k][0]
    if ref in s3lib.MOVED_OK + ('FID5', 'FID6') and a[k][3:6] == b[k][3:6] and a[k][7] == b[k][7]: tag = 'moved on instruction'
    elif ref in s3lib.TURNED_OK and a[k][4:6] == b[k][4:6] and a[k][7] == b[k][7]: tag = 'moved on instruction'
    elif ref == 'J1' and a[k][1:6] == b[k][1:6]: tag = 'pad nets by the schematic, same place'
    else: bad.append(k); continue
    print('  %s: %s (%.2f, %.2f) %.0f deg -> (%.2f, %.2f) %.0f deg' % (tag, ref, mm(a[k][1]) - s3lib.DX, mm(a[k][2]) - s3lib.DY, a[k][3], mm(b[k][1]) - s3lib.DX, mm(b[k][2]) - s3lib.DY, b[k][3]))
added = {b[k][0] for k in b if k not in a and k[0] == 'F'}
cnt = lambda s, c: sum(1 for k in s if k[0] == c)
print('  input items: %d footprints, %d tracks+vias, %d zones, %d copper graphics' % (cnt(a, 'F'), cnt(a, 'T'), cnt(a, 'Z'), cnt(a, 'D')))
print('  missing: %d   changed (not on the lists): %d   added footprints: %s   added tracks+vias: %d, zones: %d' % (len(missing), len(bad), sorted(added), sum(1 for k in b if k not in a and k[0] == 'T'), sum(1 for k in b if k not in a and k[0] == 'Z')))
for k in (missing + bad)[:20]: print('   !', k, a[k], b.get(k))
ok = not missing and not bad and added == NEW
print('  LOCK', 'PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)
