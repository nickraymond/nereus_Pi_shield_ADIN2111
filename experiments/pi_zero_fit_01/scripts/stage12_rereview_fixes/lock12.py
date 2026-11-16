"""Stage 12 lock check. Usage: <KiCad python> lock12.py <stage-2c board> <board> <head board 2bf006f> <jobs built, e.g. 134>
Against the stage-2c board (d30920b): as stage 11's lock11.py, job 3 (nothing of it missing but the orphan via of phase K, stage 6's two stubs and,
from job 2 on, the one via F1VIA; footprints changed only as the earlier stages list them; added footprints exactly NEW).
Against the head board 2bf006f, in a child process, every difference must be on this list:
  job 1  footprints J15..J19: 0.10 mm south, nothing else; their 15 pads: 1.7 -> 1.5 mm round, 0.10 mm south, same drill, kind, layers, net;
         tracks gone / new only on the nets NETS1, each on the layers it had; no via gone or new;
         silkscreen: the 31 pad-row texts 0.10 mm south or, as built, none; the 15 texts inside J15..J19 (hidden) move with the footprints
  job 2  5V_LIFEPO4: the via (4.267, 17.687) gone, one via and bottom-layer track new; nothing else on that net
  job 3  MOTOR_IN1 / MOTOR_IN2: Internal 2 tracks gone / new; no via
  job 4  bottom silkscreen: the stage-11 logo polygons and the two name texts replaced by new ones with the same strings; no copper difference
Zones (net, layers, priority, name, outline), copper graphics and all other footprints, pads, tracks, vias, silkscreen items: identical."""
import sys, os, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage3_routing'))
import s3lib, pcbnew
mm = pcbnew.ToMM; DX, DY = s3lib.DX, s3lib.DY; F, B = pcbnew.F_SilkS, pcbnew.B_SilkS
ROW = ('J15', 'J16', 'J17', 'J18', 'J19'); DYR = 100000
NETS1 = {'GPIO14': 'B', 'GPIO15': 'B', 'GPIO19': 'B', 'GPIO20': 'B', 'GPIO21': 'B', 'PI_5V': 'B', 'PI_3V3': 'B', 'GPIO17': 'T', 'GPIO7': '1', 'GPIO12': '2', 'I2C3_SCL': '1', 'I2C3_SDA': '1', 'CFG0_STRAP': '1', 'VBUS': '2'}
F1VIA = 'T ' + os.environ.get('F1VIA', '')
NAMES = ('Pi Shield', 'ADIN2111 Rev0')
def padtab(b): return {(f.GetReference(), p.GetNumber()): (p.GetPosition().x, p.GetPosition().y, p.GetShape(pcbnew.F_Cu), p.GetSize(pcbnew.F_Cu).x, p.GetSize(pcbnew.F_Cu).y, p.GetDrillSize().x, p.GetDrillSize().y, p.GetDrillShape(), p.GetAttribute(), p.GetLayerSet().FmtHex(), round(p.GetOrientationDegrees(), 3), p.GetNetname()) for f in b.GetFootprints() for p in f.Pads()}
def silk(b):
    o = []
    def T(t, own): return ('text', own, t.GetText(), t.GetPosition().x, t.GetPosition().y, t.GetTextSize().x, t.GetTextSize().y, t.GetTextThickness(), t.GetTextAngleDegrees(), t.IsVisible(), t.GetLayer(), t.IsMirrored(), t.GetHorizJustify(), t.GetVertJustify(), t.GetFontName(), t.IsBold())
    def G(g, own): bb = g.GetBoundingBox(); return ('shape', own, g.GetShape(), g.GetLayer(), bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom(), g.GetWidth())
    for d in b.GetDrawings():
        if d.GetLayer() in (F, B): o.append(T(d, '') if d.GetClass() == 'PCB_TEXT' else G(d, ''))
    for f in b.GetFootprints():
        r = f.GetReference()
        for t in [f.Reference(), f.Value()] + [g for g in f.GraphicalItems() if g.GetClass() == 'PCB_TEXT']: o.append(T(t, r))
        for g in f.GraphicalItems():
            if g.GetClass() == 'PCB_SHAPE' and g.GetLayer() in (F, B): o.append(G(g, r))
    return o
if sys.argv[1] == '--head':
    job = sys.argv[4]; hb, nb = pcbnew.LoadBoard(sys.argv[2]), pcbnew.LoadBoard(sys.argv[3]); h, n = s3lib.snapshot(hb), s3lib.snapshot(nb); bad = []; notes = []
    lay = {hb.GetLayerID(k): v for k, v in (('Top Layer', 'T'), ('Internal 1', '1'), ('Internal 2', '2'), ('6 Bottom Layer', 'B'))}
    gone = {}; new = {}; rowfp = 0
    for k in set(h) | set(n):
        x, y = h.get(k), n.get(k)
        if x == y: continue
        if k[0] == 'F' and x and y and x[0] in ROW and x[0] == y[0] and y[1] == x[1] and y[2] == x[2] + DYR and x[3:6] == y[3:6] and x[7] == y[7]: rowfp += 1; continue
        if k[0] == 'T' and not (x and y):
            t = x or y; net = s3lib.sn(t[-1]); via = t[0] == 'via'; L = None if via else lay.get(t[6]); ok = False
            if '1' in job and not via and NETS1.get(net) == L: ok = True
            if '2' in job and net == '5V_LIFEPO4' and (via or L == 'B' and y): ok = (k == F1VIA) if (via and x) else True
            if '3' in job and net in ('MOTOR_IN1', 'MOTOR_IN2') and L == '2': ok = True
            if ok: d = gone if x else new; kk = (net, 'via' if via else {'T': 'Top Layer', '1': 'Internal 1', '2': 'Internal 2', 'B': '6 Bottom Layer'}[L]); d[kk] = d.get(kk, 0) + 1; continue
        bad.append((k, x, y))
    pa, pb = padtab(hb), padtab(nb); pd = sorted(k for k in set(pa) | set(pb) if pa.get(k) != pb.get(k))
    okp = all(k[0] in ROW and k in pa and k in pb and pb[k][0] == pa[k][0] and pb[k][1] == pa[k][1] + DYR and pa[k][3:5] == (1700000, 1700000) and pb[k][3:5] == (1500000, 1500000) and pa[k][2] == pb[k][2] and pa[k][5:] == pb[k][5:] for k in pd) and len(pd) == 15 and rowfp == 5
    sa, sb = silk(hb), silk(nb); ra, rb = sorted(map(repr, sa)), sorted(map(repr, sb)); da = [x for x in sa if repr(x) not in set(rb)]; db = [x for x in sb if repr(x) not in set(ra)]; oks = True; lab = 0; logo = ''
    fa = sorted((x[1], x[2], x[3], x[4] + DYR) + x[5:] for x in da if x[0] == 'text' and x[1] in ROW); fb = sorted((x[1],) + x[2:] for x in db if x[0] == 'text' and x[1] in ROW); fpt = len(fa) if fa == fb else -1
    da = [x for x in da if not (x[0] == 'text' and x[1] in ROW)]; db = [x for x in db if not (x[0] == 'text' and x[1] in ROW)]
    moved = {(x[2], x[3], x[4] + DYR) + x[5:] for x in da if x[0] == 'text' and x[1] == ''}
    rest_b = []
    for x in db:
        if x[0] == 'text' and x[1] == '' and (x[2], x[3], x[4]) + x[5:] in moved and x[2] not in NAMES: lab += 1
        elif '4' in job and x[1] == '' and x[10 if x[0] == 'text' else 3] == B and (x[0] == 'shape' and x[2] == pcbnew.SHAPE_T_POLY or x[0] == 'text' and x[2] in NAMES): rest_b.append(x)
        else: oks = False; bad.append(('silk new', x))
    rest_a = [x for x in da if not (x[0] == 'text' and x[1] == '' and x[2] not in NAMES and (x[2], x[3], x[4] + DYR) + x[5:] in {(y[2], y[3], y[4]) + y[5:] for y in db if y[0] == 'text'})]
    if rest_a or rest_b:
        if '4' in job and len(rest_a) == len(rest_b) == 4 and all(x[1] == '' and (x[0] == 'shape' and x[2] == pcbnew.SHAPE_T_POLY and x[3] == B or x[0] == 'text' and x[2] in NAMES) for x in rest_a): logo = 'logo and name on the bottom: 2 polygons + 2 texts replaced; '
        else: oks = False; bad += [('silk gone', x) for x in rest_a]
    if lab not in (0, 31): oks = False
    cnt = lambda s, c: sum(1 for k in s if k[0] == c)
    print('  against the head board 2bf006f: %d footprints, %d tracks + vias, %d zones, %d copper graphics, %d pads, %d silkscreen items and footprint texts compared' % (cnt(h, 'F'), cnt(h, 'T'), cnt(h, 'Z'), cnt(h, 'D'), len(pa), len(sa)))
    print('    footprints moved 0.10 mm south: %d (J15..J19); pads that differ: %d (1.7 -> 1.5 mm, 0.10 mm south: %s)' % (rowfp, len(pd), 'yes' if okp else 'NO'))
    print('    tracks / vias gone:', ', '.join('%s %s %d' % (k[0], k[1], v) for k, v in sorted(gone.items())) or 'none')
    print('    tracks / vias new: ', ', '.join('%s %s %d' % (k[0], k[1], v) for k, v in sorted(new.items())) or 'none')
    print('    silkscreen: %d pad-row texts 0.10 mm south; %d texts inside J15..J19 (hidden reference, value, fabrication-layer name) moved with their footprints; %sother differences: %d' % (lab, fpt, logo, len(bad)))
    for x in bad[:20]: print('   !', str(x)[:260])
    sys.exit(0 if not bad and okp and oks and fpt == 15 else 1)
JOB = sys.argv[4]
J4NEW = 'nereus:WirePads_1x02_P3.20mm_Oval2.2x3.3mm_Drill1.3mm'
DROP = ('T 89214ad6-26b4-421d-8de0-e5b3b5f7cfb4', 'T 1745e174-32ff-4215-9962-73b7e474f208') + ((F1VIA,) if '2' in JOB else ())
NEW = {'J15', 'J16', 'J17', 'J18', 'J19', 'TP40', 'TP41', 'TP42', 'TP43'}
HOLE = pcbnew.FromMM(2.75)
a = s3lib.snapshot(pcbnew.LoadBoard(sys.argv[1])); bb = pcbnew.LoadBoard(sys.argv[2]); b = s3lib.snapshot(bb)
holes = {f.GetReference(): [(p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH, p.GetDrillSize().x, p.GetDrillSize().y, p.GetSize(pcbnew.F_Cu).x) for p in f.Pads()] for f in bb.GetFootprints() if f.GetReference() in ('H1', 'H2', 'H3', 'H4')}
j4d = [(p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH, p.GetDrillSize().x, p.GetDrillSize().y, p.GetSize(pcbnew.F_Cu).x, p.GetSize(pcbnew.F_Cu).y) for f in bb.GetFootprints() if f.GetReference() == 'J4' for p in f.Pads()]
for k in a:
    if k not in b and k in DROP + s3lib.REMOVED_OK: print('  removed on instruction:', k, a[k][:5], '(stage 12, job 2: the via at F1 pad 1, moved)' if k == F1VIA else '')
j1 = []
missing = [k for k in a if k not in b and k not in s3lib.REMOVED_OK + DROP]; bad = []
for k in a:
    if k not in b or a[k] == b[k]: continue
    if k[0] != 'F': bad.append(k); continue
    ref = a[k][0]
    if ref in s3lib.MOVED_OK + ('FID5', 'FID6') and a[k][3:6] == b[k][3:6] and a[k][7] == b[k][7]: tag = 'moved on instruction'
    elif ref in s3lib.TURNED_OK and ref != 'R9' and a[k][4:6] == b[k][4:6] and a[k][7] == b[k][7]: tag = 'moved on instruction'
    elif ref == 'R9' and a[k][5] == b[k][5] and a[k][7] == b[k][7]: tag = 'moved on instruction (stage 6, side %s -> %s)' % ('bottom' if a[k][4] else 'top', 'bottom' if b[k][4] else 'top')
    elif ref == 'J1' and a[k][1:6] == b[k][1:6]: tag = 'pad nets by the schematic, same place'
    elif ref in holes and a[k][:6] == b[k][:6] and a[k][7] == b[k][7] and holes[ref] == [(True, HOLE, HOLE, HOLE)]: tag = 'hole 2.75 mm, not plated (stage 8), same place'
    elif ref == 'J4' and a[k][:5] == b[k][:5] and a[k][6:] == b[k][6:] and b[k][5] == J4NEW and j4d == [(True, 1300000, 1300000, 2200000, 3300000)] * 2: tag = 'holes 1.3 mm round, plated, pads 2.2 x 3.3 mm, same place (stage 11)'
    else: bad.append(k); continue
    print('  %s: %s (%.2f, %.2f) %.0f deg -> (%.2f, %.2f) %.0f deg' % (tag, ref, mm(a[k][1]) - DX, mm(a[k][2]) - DY, a[k][3], mm(b[k][1]) - DX, mm(b[k][2]) - DY, b[k][3]))
    if ref == 'J1':
        for (n, x), (n2, y) in zip(a[k][7], b[k][7]):
            if x != y: j1.append((n, x.split('/')[-1], y.split('/')[-1]))
        print('        J1 pins changed since stage 2c: %s' % ', '.join('%s %s -> %s' % (n, x or '(none)', y or '(none)') for n, x, y in j1))
added = {b[k][0] for k in b if k not in a and k[0] == 'F'}
cnt = lambda s, c: sum(1 for k in s if k[0] == c)
print('  input items (stage 2c): %d footprints, %d tracks+vias, %d zones, %d copper graphics' % (cnt(a, 'F'), cnt(a, 'T'), cnt(a, 'Z'), cnt(a, 'D')))
print('  missing: %d   changed (not on the lists): %d   added footprints: %s   added tracks+vias: %d, zones: %d' % (len(missing), len(bad), sorted(added), sum(1 for k in b if k not in a and k[0] == 'T'), sum(1 for k in b if k not in a and k[0] == 'Z')))
for k in (missing + bad)[:20]: print('   !', k, a[k], b.get(k))
head = subprocess.run([sys.executable, '-B', os.path.abspath(__file__), '--head', sys.argv[3], sys.argv[2], sys.argv[4]], capture_output=True, text=True, env=os.environ)
print('\n'.join(l for l in head.stdout.splitlines() if l.startswith('  ')) or head.stderr[-800:])
ok = not missing and not bad and added == NEW and head.returncode == 0 and {n: y for n, x, y in j1 if n in ('12', '32', '33')} == {'12': 'MOTOR_IN2', '32': 'GPIO12', '33': 'MOTOR_IN1'}
print('  LOCK', 'PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)
