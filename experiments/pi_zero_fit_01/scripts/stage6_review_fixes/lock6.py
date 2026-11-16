"""Stage 6 lock check: stage 5's (lock5.py) with stage 6's own, listed changes. Passes only if nothing of the stage-2c board is missing
(but the orphan via of phase K and the two dangling converter stubs of step1_review.DROP), nothing is changed but the footprints
earlier stages moved on instruction and R9 (to the top layer beside U1, same footprint and pad nets), and the added footprints are exactly NEW.
Usage: <KiCad python> lock6.py <stage-2c board> <board>"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage3_routing'))
import s3lib, pcbnew
DROP = ('T 89214ad6-26b4-421d-8de0-e5b3b5f7cfb4', 'T 1745e174-32ff-4215-9962-73b7e474f208')
NEW = {'J15', 'J16', 'J17', 'J18', 'J19', 'TP40', 'TP41', 'TP42', 'TP43'}
a = s3lib.snapshot(pcbnew.LoadBoard(sys.argv[1])); bb = pcbnew.LoadBoard(sys.argv[2]); b = s3lib.snapshot(bb)
for k in a:
    if k not in b and k in DROP + s3lib.REMOVED_OK: print('  removed on instruction:', k, a[k][:5])
missing = [k for k in a if k not in b and k not in s3lib.REMOVED_OK + DROP]; bad = []; mm = s3lib.mm
for k in a:
    if k not in b or a[k] == b[k]: continue
    if k[0] != 'F': bad.append(k); continue
    ref = a[k][0]
    if ref in s3lib.MOVED_OK + ('FID5', 'FID6') and a[k][3:6] == b[k][3:6] and a[k][7] == b[k][7]: tag = 'moved on instruction'
    elif ref in s3lib.TURNED_OK and ref != 'R9' and a[k][4:6] == b[k][4:6] and a[k][7] == b[k][7]: tag = 'moved on instruction'
    elif ref == 'R9' and a[k][5] == b[k][5] and a[k][7] == b[k][7]: tag = 'moved on instruction (stage 6, side %s -> %s)' % ('bottom' if a[k][4] else 'top', 'bottom' if b[k][4] else 'top')
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
