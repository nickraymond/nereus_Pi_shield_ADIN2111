"""Stage 8, job 2: the board's footprints carry the schematic's fields; the nine parts' fields follow the schematic (stage 2b's
apply(): fields, nothing else changes; place, side, turn and pad nets are asserted unchanged).
Usage: <KiCad python> job2_sync.py <board> <netlist>"""
import sys, os, importlib.util, pcbnew
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'stage2b_board_sync'))
spec = importlib.util.spec_from_file_location('sync2b', os.path.join(HERE, '..', 'stage2b_board_sync', 's3lib.py')); L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
REFS = ('U12', 'U13', 'C60', 'C64', 'R48', 'J7', 'J9', 'J10', 'J8')
b = pcbnew.LoadBoard(sys.argv[1]); comps = L.load_netlist(sys.argv[2]); fps = L.by_ref(b)
for r in REFS:
    f = fps[r]; before = (f.GetPosition(), f.GetOrientationDegrees(), f.IsFlipped(), sorted((p.GetNumber(), p.GetNetname()) for p in f.Pads())); d = L.diff_one(f, comps[r])
    assert d and all(k == 'field' for k, _ in d), (r, d)
    L.apply(b, f, r, comps[r])
    assert before == (f.GetPosition(), f.GetOrientationDegrees(), f.IsFlipped(), sorted((p.GetNumber(), p.GetNetname()) for p in f.Pads())) and not L.diff_one(f, comps[r]), r
    print('  %-4s %s' % (r, '; '.join(t for _, t in d)))
rest = [(r, [x for x in L.diff_one(fps[r], comps[r]) if x[0] != 'pin']) for r in sorted(fps) if r in comps]
print('  other differences board / netlist (not touched):', [x for x in rest if x[1]] or 'none')
pcbnew.SaveBoard(sys.argv[1], b)
