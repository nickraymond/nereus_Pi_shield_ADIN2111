"""Stage 4, step 2: board follows the schematic of step 1 (the method of stage 2b / 2c: footprints from the libraries, nets and fields
from the netlist; nothing is routed here). New-frame mm. Usage: <KiCad python> step2_sync.py <board in> <netlist> <board out>

Sites were searched on all six layers first (a 1.7 mm pad with a 1.0 mm hole against every other net's copper, the screw keep-outs,
the edge rule and the part bodies of both sides); these are the places that are clear without moving any part but FID5 / FID6:
  J11 west   (15.30, 9.60) + (17.84, 9.60)   GPIO14, GPIO15   south of their header pins, between the PI_5V track and Sofar's ground via
  J12 north-east (57.70, 7.40) + (57.70, 9.94)   GPIO18, GPIO19   between the header's east end and J5
  J13 east   (62.60, 17.85) + (62.60, 20.39)  GPIO17, GPIO20   between J5 and the south-east screw
  J14 south-east (62.20, 32.90 / 35.44 / 37.98)  GND x 3      east of J10; FID5 / FID6 move from (62.2, 33.0) to (62.2, 30.6) for it
Test points (Vault:PCB_TP_1.5mm, the footprint of TP38): TP40 MOTOR_IN1, TP41 MOTOR_OUT1, TP43 I2C0_SCL on the bottom, TP42 MOTOR_OUT2 on the top.
"""
import sys, os, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'stage2b_board_sync'))
spec = importlib.util.spec_from_file_location('sync2b', os.path.join(HERE, '..', 'stage2b_board_sync', 's3lib.py')); L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
import pcbnew
L.PROJ = os.path.dirname(os.path.abspath(sys.argv[1]))
V, N, mm = L.V, L.N, L.mm
b = pcbnew.LoadBoard(sys.argv[1]); comps = L.load_netlist(sys.argv[2]); fps = L.by_ref(b)
# ref: (anchor pad, its place, second pad, its place, side)
PLACE = {
    'J11': ('1', (15.30, 9.60), '2', (17.84, 9.60), 'top'), 'J12': ('1', (57.70, 7.40), '2', (57.70, 9.94), 'top'),
    'J13': ('1', (62.60, 17.85), '2', (62.60, 20.39), 'top'), 'J14': ('1', (62.20, 32.90), '3', (62.20, 37.98), 'top'),
    'TP40': ('1', (2.20, 37.85), None, None, 'bottom'), 'TP41': ('1', (2.50, 35.50), None, None, 'bottom'),
    'TP42': ('1', (8.35, 31.605), None, None, 'top'), 'TP43': ('1', (31.13, 33.27), None, None, 'bottom'),
}
missing = sorted(r for r in comps if r not in fps)
assert missing == sorted(PLACE), ('the parts to add are not the parts this script places', missing)
for r, (p1, at1, p2, at2, side) in PLACE.items():
    f = L.lib_footprint(comps[r]['fpid']); b.Add(f); f.SetPosition(V(*at1))
    if side == 'bottom': f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    pad = lambda n: [q for q in f.Pads() if q.GetNumber() == n][0]
    d = pad(p1).GetPosition() - f.GetPosition(); assert d.x == 0 and d.y == 0, (r, 'anchor pad is not at the footprint origin')
    if p2:
        for rot in (0, 90, 180, 270):
            f.SetOrientationDegrees(rot); q = N(pad(p2).GetPosition())
            if abs(q[0] - at2[0]) < 0.005 and abs(q[1] - at2[1]) < 0.005: break
        else: raise SystemExit('%s: no turn puts pad %s at %s' % (r, p2, at2))
    L.apply(b, f, r, comps[r]); assert not L.diff_one(f, comps[r]), (r, L.diff_one(f, comps[r]))
    print('  %-5s %-52s %s %3.0f deg  %s' % (r, L.fpid_str(f), side, f.GetOrientationDegrees(),
          '  '.join('%s %s (%.2f, %.2f) %.1f mm pad, %.1f mm hole' % (q.GetNumber(), q.GetNetname().split('/')[-1], *N(q.GetPosition()), mm(q.GetBoundingBox().GetWidth()), mm(q.GetDrillSize().x)) for q in f.Pads())))
# J1: the six pins that now carry GPIO nets (J1 is our own part; position untouched)
f = fps['J1']; pos, rot = f.GetPosition(), f.GetOrientationDegrees(); d = L.diff_one(f, comps['J1'])
L.apply(b, f, 'J1', comps['J1']); assert (f.GetPosition(), f.GetOrientationDegrees()) == (pos, rot) and not L.diff_one(f, comps['J1'])
print('  J1:', '; '.join(t for k, t in d))
for r in ('FID5', 'FID6'):
    f = fps[r]; old = N(f.GetPosition()); assert old == (62.2, 33.0), (r, old); f.SetPosition(V(62.2, 30.6)); print('  moved %s %s -> (62.2, 30.6)' % (r, old))
rest = [(r, L.diff_one(fps[r], comps[r])) for r in sorted(fps) if r in comps and r != 'J1']
rest = [(r, [x for x in d if x[0] != 'pin']) for r, d in rest]; rest = [x for x in rest if x[1]]
print('  other differences board / netlist (not touched):', rest or 'none')
used = {p.GetNetname() for f in b.GetFootprints() for p in f.Pads()} | {t.GetNetname() for t in b.GetTracks()} | {z.GetNetname() for z in b.Zones()}
dead = [n for name, n in b.GetNetInfo().NetsByName().items() if str(name) and str(name) not in used]
print('  nets removed (nothing uses them):', sorted(n.GetNetname() for n in dead) or 'none')
for x in dead: b.Remove(x)
pcbnew.SaveBoard(sys.argv[3], b); print('saved', sys.argv[3])
