"""Stage 8, job 3: board follows the schematic of job3_schematic.py. New-frame mm.
  <KiCad python> job3_sync.py --rip <board> <stage-2c board>   first, in its own process: the copper that goes. Only tracks / vias that are NOT in the
        stage-2c board (our own, stages 3..6) are touched: GPIO18 whole (J1 pin 12 - J18 pad 1, Internal 2); MOTOR_IN1 and MOTOR_IN2 on Internal 2
        (the runs past U1 / Y1 and along the south strip); their vias (3.7, 38.2) / (7.0, 38.0) and bottom pieces at U12 / TP40 stay.
  <KiCad python> job3_sync.py <board> <netlist>                  J1 and J18 take pad nets and fields from the netlist (same place); unused nets go.
Nothing is routed here."""
import sys, os, re, importlib.util, pcbnew
HERE = os.path.dirname(os.path.abspath(__file__))
if sys.argv[1] == '--rip':
    sys.path.insert(0, os.path.join(HERE, '..', 'stage3_routing')); import s3lib
    base = set(re.findall(r'\(uuid "([0-9a-f-]{36})"\)', open(sys.argv[3]).read())); b = pcbnew.LoadBoard(sys.argv[2]); kill = []; cnt = {}
    for t in b.GetTracks():                      # one GetTracks() call; nothing is queried after the first Remove()
        n = s3lib.sn(t.GetNetname())
        if n not in ('GPIO18', 'MOTOR_IN1', 'MOTOR_IN2'): continue
        assert t.m_Uuid.AsString() not in base, ('an item of the stage-2c board is on this net', n)
        if n != 'GPIO18' and (t.GetClass() == 'PCB_VIA' or t.GetLayerName() != 'Internal 2'): continue      # the vias and bottom pieces at U12 / TP40 stay
        k = (n, 'via' if t.GetClass() == 'PCB_VIA' else t.GetLayerName()); cnt[k] = cnt.get(k, 0) + (0 if k[1] == 'via' else s3lib.mm(t.GetLength())); kill.append(t)
    for k in sorted(cnt): print('  removed %-10s %-14s %s' % (k[0], k[1], '' if k[1] == 'via' else '%.2f mm' % cnt[k]))
    for t in kill: b.Remove(t)
    pcbnew.SaveBoard(sys.argv[2], b); sys.exit(0)
sys.path.insert(0, os.path.join(HERE, '..', 'stage2b_board_sync'))
spec = importlib.util.spec_from_file_location('sync2b', os.path.join(HERE, '..', 'stage2b_board_sync', 's3lib.py')); L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
b = pcbnew.LoadBoard(sys.argv[1]); comps = L.load_netlist(sys.argv[2]); fps = L.by_ref(b)
for r in ('J1', 'J18'):
    f = fps[r]; pos, rot = f.GetPosition(), f.GetOrientationDegrees(); d = L.diff_one(f, comps[r])
    L.apply(b, f, r, comps[r]); assert (f.GetPosition(), f.GetOrientationDegrees()) == (pos, rot) and not L.diff_one(f, comps[r])
    print('  %s: %s' % (r, '; '.join(t for k, t in d)))
rest = [(r, [x for x in L.diff_one(fps[r], comps[r]) if x[0] != 'pin']) for r in sorted(fps) if r in comps]
print('  other differences board / netlist (not touched):', [x for x in rest if x[1]] or 'none')
used = {p.GetNetname() for f in b.GetFootprints() for p in f.Pads()} | {t.GetNetname() for t in b.GetTracks()} | {z.GetNetname() for z in b.Zones()}
dead = [n for name, n in b.GetNetInfo().NetsByName().items() if str(name) and str(name) not in used]
print('  nets removed (nothing uses them):', sorted(n.GetNetname() for n in dead) or 'none')
for x in dead: b.Remove(x)
pcbnew.SaveBoard(sys.argv[1], b)
