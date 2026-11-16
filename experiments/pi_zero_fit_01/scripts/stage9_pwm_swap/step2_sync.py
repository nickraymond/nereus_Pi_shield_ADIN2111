"""Stage 9: board follows the schematic of step1_schematic.py. New-frame mm.
  <KiCad python> step2_sync.py --rip <board> <stage-2c board>   first, in its own process: the copper that goes. Only tracks / vias that are NOT in the
        stage-2c board (our own) are touched: MOTOR_IN1 and MOTOR_IN2 on Internal 2 (whole), MOTOR_IN1's 1.27 mm on Internal 1 and its two
        swap vias (14.1, 26.8) / (13.2, 25.9). The vias at U12, (3.7, 38.2) MOTOR_IN1 and (7.0, 38.0) MOTOR_IN2, and the bottom pieces at U12 / TP40 stay.
  <KiCad python> step2_sync.py <board> <netlist>                  J1 takes pad nets and fields from the netlist (same place).
Nothing is routed here."""
import sys, os, re, importlib.util, pcbnew
HERE = os.path.dirname(os.path.abspath(__file__))
if sys.argv[1] == '--rip':
    sys.path.insert(0, os.path.join(HERE, '..', 'stage3_routing')); import s3lib
    base = set(re.findall(r'\(uuid "([0-9a-f-]{36})"\)', open(sys.argv[3]).read())); b = pcbnew.LoadBoard(sys.argv[2]); kill = []; cnt = {}; kept = []
    SWAP = ((14.1, 26.8), (13.2, 25.9)); KEEP = {('MOTOR_IN1', (3.7, 38.2)), ('MOTOR_IN2', (7.0, 38.0))}
    for t in b.GetTracks():                      # one GetTracks() call; nothing is queried after the first Remove()
        n = s3lib.sn(t.GetNetname())
        if n not in ('MOTOR_IN1', 'MOTOR_IN2'): continue
        assert t.m_Uuid.AsString() not in base, ('an item of the stage-2c board is on this net', n)
        if t.GetClass() == 'PCB_VIA':
            p = tuple(round(v, 2) for v in s3lib.N(t.GetPosition()))
            if (n, p) in KEEP: kept.append((n, p)); continue
            assert n == 'MOTOR_IN1' and p in SWAP, ('a via this script does not know', n, p)
        elif t.GetLayerName() == '6 Bottom Layer': continue
        else: assert t.GetLayerName() == 'Internal 2' or (n == 'MOTOR_IN1' and t.GetLayerName() == 'Internal 1'), (n, t.GetLayerName())
        k = (n, 'via' if t.GetClass() == 'PCB_VIA' else t.GetLayerName()); cnt[k] = cnt.get(k, 0) + (1 if k[1] == 'via' else s3lib.mm(t.GetLength())); kill.append(t)
    assert set(kept) == KEEP, kept
    for k in sorted(cnt): print('  removed %-10s %-14s %s' % (k[0], k[1], '%d' % cnt[k] if k[1] == 'via' else '%.2f mm' % cnt[k]))
    for t in kill: b.Remove(t)
    pcbnew.SaveBoard(sys.argv[2], b); sys.exit(0)
sys.path.insert(0, os.path.join(HERE, '..', 'stage2b_board_sync'))
spec = importlib.util.spec_from_file_location('sync2b', os.path.join(HERE, '..', 'stage2b_board_sync', 's3lib.py')); L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
b = pcbnew.LoadBoard(sys.argv[1]); comps = L.load_netlist(sys.argv[2]); fps = L.by_ref(b)
f = fps['J1']; pos, rot = f.GetPosition(), f.GetOrientationDegrees(); d = L.diff_one(f, comps['J1'])
L.apply(b, f, 'J1', comps['J1']); assert (f.GetPosition(), f.GetOrientationDegrees()) == (pos, rot) and not L.diff_one(f, comps['J1'])
print('  J1: %s' % '; '.join(t for k, t in d))
rest = [(r, [x for x in L.diff_one(fps[r], comps[r]) if x[0] != 'pin']) for r in sorted(fps) if r in comps]
print('  other differences board / netlist (not touched):', [x for x in rest if x[1]] or 'none')
pcbnew.SaveBoard(sys.argv[1], b)
