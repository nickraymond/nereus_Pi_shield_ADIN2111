"""Unit test of the pair router emission (router.commit_pair): on a blank board, each net continuous from pin to
pad, P/N and obstacle clearance ≥ 0.15 mm, through turns, both swap sides, a straight via pair, a turn right after a
swap, a turn right after a straight via pair, and the pads' straight approach (session 2: the opposite pad is modelled
as copper of its net, so a track crossing it fails the clearance check: QE round 1 F1). Then the real-board case: both
ADIN pairs routed by m4_route.route_pairs on the M3 snapshot (out/m3/snapshot.kicad_pcb; else the committed board with
the pair nets' copper stripped), checked for continuity, P-N clearance, clearance to every other net (0.15; 0.35 to
the bus nets) and the mote's length limits.
  $PY tools/test_pair.py            (run from experiments/fable_layout_01a/; --quick skips the real-board case)
"""
import sys, math
sys.path.insert(0, 'tools')
import pcbnew, geom, router
from geom import MM, mm

def make_board():
    b = pcbnew.BOARD(); b.SetCopperLayerCount(6)
    for name in ('P', 'N', 'X'):
        b.Add(pcbnew.NETINFO_ITEM(b, name))
    return b

FAILS = []


def pad_copper(b, net, p, u, length=1.2, width=0.41):
    """A transformer pad modelled as a track of its net: `length` along u (centred on p), `width` wide."""
    t = pcbnew.PCB_TRACK(b)
    t.SetStart(pcbnew.VECTOR2I(MM(p[0] - u[0] * length / 2), MM(p[1] - u[1] * length / 2)))
    t.SetEnd(pcbnew.VECTOR2I(MM(p[0] + u[0] * length / 2), MM(p[1] + u[1] * length / 2)))
    t.SetWidth(MM(width)); t.SetLayer(pcbnew.F_Cu); t.SetNet(b.FindNet(net)); b.Add(t)


def test(name, path_cells, swaps, pins, pads, extra=None, dir_in=None, start_vias=None):
    b = make_board()
    if extra: extra(b)
    g = router.Grid(b, merge={'N': 'P'})
    path = [(l, *router.cell(x, y)) for l, x, y in path_cells]
    stats = g.commit_pair(('P', 'N'), path, pins, pads, swaps={router.cell(*c): sd for c, sd in swaps.items()}, dir_in=dir_in, dir_out=(0, -1) if dir_in else None, start_vias=start_vias)
    # connectivity: each net's items must form one cluster containing the pin end and the pad end
    ok = True
    for net, pin, pad in (('P', pins[0], pads[0]), ('N', pins[1], pads[1])):
        cl = router.net_clusters(b, net)
        hit = [c for c in cl if any(it.GetClass()=='PCB_TRACK' and (geom.dist(geom.xy(it.GetStart()), pin) < 1e-3 or geom.dist(geom.xy(it.GetEnd()), pin) < 1e-3) for it in c)]
        at_pad = hit and any(it.GetClass()=='PCB_TRACK' and (geom.dist(geom.xy(it.GetStart()), pad) < 1e-3 or geom.dist(geom.xy(it.GetEnd()), pad) < 1e-3) for it in hit[0])
        if len(cl) != 1 or not at_pad:
            ok = False; print(f"  {name}: {net} clusters {len(cl)} sizes {[len(c) for c in cl]} pad reached {bool(at_pad)}")
    # clearance P vs N on every layer, and vs the X obstacle
    worst = 9
    items = {n: [t for t in b.GetTracks() if t.GetNetname() == n] for n in ('P', 'N', 'X')}
    for a in items['P']:
        for c in items['N'] + items['X']:
            for l in geom.CU:
                la = geom.CU if a.GetClass()=='PCB_VIA' else [a.GetLayer()]
                lc = geom.CU if c.GetClass()=='PCB_VIA' else [c.GetLayer()]
                if l in la and l in lc:
                    d = mm(a.GetEffectiveShape(l).GetClearance(c.GetEffectiveShape(l)))
                    if d < 0.149: print('   COLLISION', b.GetLayerName(l)[:4], a.GetClass()[4:], tuple(round(v,3) for v in geom.xy(a.GetStart() if a.GetClass()!='PCB_VIA' else a.GetPosition())), tuple(round(v,3) for v in geom.xy(a.GetEnd() if a.GetClass()!='PCB_VIA' else a.GetPosition())), 'vs', c.GetClass()[4:], tuple(round(v,3) for v in geom.xy(c.GetStart() if c.GetClass()!='PCB_VIA' else c.GetPosition())), tuple(round(v,3) for v in geom.xy(c.GetEnd() if c.GetClass()!='PCB_VIA' else c.GetPosition())), round(d,3))
                    worst = min(worst, d)
    for a in items['N']:
        for c in items['X']:
            for l in geom.CU:
                la = geom.CU if a.GetClass()=='PCB_VIA' else [a.GetLayer()]
                lc = geom.CU if c.GetClass()=='PCB_VIA' else [c.GetLayer()]
                if l in la and l in lc:
                    worst = min(worst, mm(a.GetEffectiveShape(l).GetClearance(c.GetEffectiveShape(l))))
    good = ok and worst >= 0.149
    if not good:
        FAILS.append(name)
    print(f"{name}: {'OK' if good else 'FAIL'}  min P-N/obstacle clearance {worst:.3f}  stats {stats}")
    return b

F, I1 = pcbnew.F_Cu, pcbnew.In1_Cu
# 1. east 3 mm, swap (side +1) at x 12, continue east to 15, turn north to y 7, end; pins west of S, pads below the end
cells = [(F, 10 + 0.1*k, 10.0) for k in range(0, 21)] + [(I1, 12.0 + 0.1*k, 10.0) for k in range(0, 31)] + [(I1, 15.0, 10.0 - 0.1*k) for k in range(1, 31)]
test('swap +1 then turn', cells, {(12.0, 10.0): 1}, ((9.4, 9.8), (9.4, 10.2)), ((15.2, 6.4), (14.8, 6.4)))
test('swap -1 then turn', cells, {(12.0, 10.0): -1}, ((9.4, 9.8), (9.4, 10.2)), ((15.2, 6.4), (14.8, 6.4)))
# 2. diagonal travel with a swap, then a straight via pair back to Top
cells = [(F, 10 + 0.1*k, 20 - 0.1*k) for k in range(0, 21)] + [(I1, 12 + 0.1*k, 18 - 0.1*k) for k in range(0, 21)] + [(F, 14 + 0.1*k, 16 - 0.1*k) for k in range(0, 21)]
test('diagonal swap + straight pair', cells, {(12.0, 18.0): 1}, ((9.40, 20.25), (9.75, 20.60)), ((16.44, 14.02), (15.98, 13.56)))
test('diagonal swap side -1', cells, {(12.0, 18.0): -1}, ((9.40, 20.25), (9.75, 20.60)), ((16.44, 14.02), (15.98, 13.56)))
# 3. no via at all, with a turn
cells = [(F, 10 + 0.1*k, 30.0) for k in range(0, 21)] + [(F, 12.0, 30.0 - 0.1*k) for k in range(1, 21)]
test('plain turn', cells, {}, ((9.4, 29.8), (9.4, 30.2)), ((11.8, 27.4), (12.2, 27.4)))

# 5. swap, then a turn right after the 0.9 mm straight run (the duplicate-vertex case), then a straight pair, then end
cells = [(F, 10 + 0.1*k, 40.0) for k in range(0, 21)] + [(I1, 12.0 + 0.1*k, 40.0) for k in range(0, 11)] + [(I1, 13.0, 40.0 - 0.1*k) for k in range(1, 21)] + [(F, 13.0, 38.0 - 0.1*k) for k in range(0, 21)]
test('swap then immediate turn + straight pair', cells, {(12.0, 40.0): 1}, ((9.4, 39.8), (9.4, 40.2)), ((13.325, 35.4), (12.675, 35.4)))
test('swap -1 then immediate turn + straight pair', cells, {(12.0, 40.0): -1}, ((9.4, 39.8), (9.4, 40.2)), ((13.325, 35.4), (12.675, 35.4)))

# 6. a straight via pair, then an immediate 90° turn; and then an immediate 45° turn (session 2: STRAIGHT_RUN = 3 cells after the vias)
cells = [(F, 10 + 0.1*k, 50.0) for k in range(0, 21)] + [(I1, 12.0 + 0.1*k, 50.0) for k in range(0, 4)] + [(I1, 12.3, 50.0 - 0.1*k) for k in range(1, 21)]
test('straight pair then 90° turn', cells, {}, ((9.4, 49.8), (9.4, 50.2)), ((12.1, 47.4), (12.5, 47.4)))
cells = [(F, 10 + 0.1*k, 60.0) for k in range(0, 21)] + [(I1, 12.0 + 0.1*k, 60.0) for k in range(0, 4)] + [(I1, 12.3 + 0.1*k, 60.0 - 0.1*k) for k in range(1, 21)]
test('straight pair then 45° turn', cells, {}, ((9.4, 59.8), (9.4, 60.2)), ((14.07, 57.77), (14.53, 58.23)))     # the run heads north-east (y down): P stays left = north-west of the end
# 7. the pads' approach (dir_in): the path ends at A' = pad_mid - 1.4 along dir_in (as m4_route.route_pairs sets the
#    goal), arriving straight, from the side, and diagonally, on Top or on Internal 1 (then the via pair sits at A =
#    A' + 0.3 beside the approach); the pads 0.65 mm apart are copper of their nets (1.2 x 0.41 as Sofar's), so a
#    track over the opposite pad is a P-N collision. Pin order P west / N east leaving north, pads N north / P south
#    entered eastward: parity 1, so one swap on the way (the real port-1 case).
pads = ((14.0, 30.75), (14.0, 30.1))                      # P south, N north; pad_mid (14.0, 30.425); A' = (12.6, 30.425)
def tpads(b):
    pad_copper(b, 'P', pads[0], (1, 0)); pad_copper(b, 'N', pads[1], (1, 0))
pre = [(F, 5.0, 33.5 - 0.1*k) for k in range(0, 21)] + [(I1, 5.0, 31.5 - 0.1*k) for k in range(0, 11)]     # north, swap at (5.0, 31.5)
# straight in on Internal 1 (east along y 30.4 into A'): the via pair at A
cells = pre + [(I1, 5.0 + 0.1*k, 30.4) for k in range(1, 77)]
test('approach: straight in on In1, swap +1', cells, {(5.0, 31.5): 1}, ((4.8, 34.0), (5.2, 34.0)), pads, tpads, dir_in=(1, 0))
test('approach: straight in on In1, swap -1', cells, {(5.0, 31.5): -1}, ((4.8, 34.0), (5.2, 34.0)), pads, tpads, dir_in=(1, 0))
# straight in on Top (a second swap on the way puts it back on Top; parity 0 then: pads swapped)
cells = pre + [(I1, 5.0 + 0.1*k, 30.4) for k in range(1, 41)] + [(F, 9.0 + 0.1*k, 30.4) for k in range(0, 37)]
test('approach: straight in on Top (two swaps)', cells, {(5.0, 31.5): 1, (9.0, 30.4): 1}, ((4.8, 34.0), (5.2, 34.0)), (pads[1], pads[0]), lambda b: (pad_copper(b, 'N', pads[0], (1, 0)), pad_copper(b, 'P', pads[1], (1, 0))), dir_in=(1, 0))
# from the north on Internal 1: north to y 28.4, east to x 12.6, south into A' (a 90° turn at A')
cells = [(F, 5.0, 33.5 - 0.1*k) for k in range(0, 21)] + [(I1, 5.0, 31.5 - 0.1*k) for k in range(0, 32)] + [(I1, 5.0 + 0.1*k, 28.4) for k in range(1, 77)] + [(I1, 12.6, 28.4 + 0.1*k) for k in range(1, 21)]
test('approach: from the north on In1 (90° at A\')', cells, {(5.0, 31.5): 1}, ((4.8, 34.0), (5.2, 34.0)), pads, tpads, dir_in=(1, 0))
# the same on Top (the second swap on the east leg)
cells = [(F, 5.0, 33.5 - 0.1*k) for k in range(0, 21)] + [(I1, 5.0, 31.5 - 0.1*k) for k in range(0, 32)] + [(I1, 5.0 + 0.1*k, 28.4) for k in range(1, 31)] + [(F, 8.0 + 0.1*k, 28.4) for k in range(0, 47)] + [(F, 12.6, 28.4 + 0.1*k) for k in range(1, 21)]
test('approach: from the north on Top (90° at A\')', cells, {(5.0, 31.5): 1, (8.0, 28.4): -1}, ((4.8, 34.0), (5.2, 34.0)), (pads[1], pads[0]), lambda b: (pad_copper(b, 'N', pads[0], (1, 0)), pad_copper(b, 'P', pads[1], (1, 0))), dir_in=(1, 0))
# diagonally into A' on Internal 1 (45° at A')
cells = [(F, 5.0, 33.5 - 0.1*k) for k in range(0, 21)] + [(I1, 5.0, 31.5 - 0.1*k) for k in range(0, 32)] + [(I1, 5.0 + 0.1*k, 28.4) for k in range(1, 57)] + [(I1, 10.6 + 0.1*k, 28.4 + 0.1*k) for k in range(1, 21)]
test('approach: diagonal into A\' on In1 (45°)', cells, {(5.0, 31.5): 1}, ((4.8, 34.0), (5.2, 34.0)), pads, tpads, dir_in=(1, 0))
cells = [(F, 5.0, 33.5 - 0.1*k) for k in range(0, 21)] + [(I1, 5.0, 31.5 - 0.1*k) for k in range(0, 32)] + [(I1, 5.0 + 0.1*k, 28.4) for k in range(1, 31)] + [(F, 8.0 + 0.1*k, 28.4) for k in range(0, 27)] + [(F, 10.6 + 0.1*k, 28.4 + 0.1*k) for k in range(1, 21)]
test('approach: diagonal into A\' on Top (45°)', cells, {(5.0, 31.5): 1, (8.0, 28.4): -1}, ((4.8, 34.0), (5.2, 34.0)), (pads[1], pads[0]), lambda b: (pad_copper(b, 'N', pads[0], (1, 0)), pad_copper(b, 'P', pads[1], (1, 0))), dir_in=(1, 0))

# 7b. the pins' staggered vias (dir_out, start_vias): P's via 0.75 north of its pin, N's 1.2; the path starts on Internal 1
#     at S2 = pin_mid + 1.5 north; one swap; arrives on Top at A'
cells = [(I1, 5.0, 32.5 - 0.1*k) for k in range(0, 11)] + [(F, 5.0, 31.5 - 0.1*k) for k in range(0, 32)] + [(F, 5.0 + 0.1*k, 28.4) for k in range(1, 77)] + [(F, 12.6, 28.4 + 0.1*k) for k in range(1, 21)]
test('staggered start vias, swap, Top approach', cells, {(5.0, 31.5): 1}, ((4.75, 34.0), (5.25, 34.0)), pads, tpads, dir_in=(1, 0), start_vias={'P': (4.75, 33.25), 'N': (5.25, 32.8)})   # U1's 0.5 mm pin pitch
test('staggered start vias (N near), swap, Top approach', cells, {(5.0, 31.5): 1}, ((4.75, 34.0), (5.25, 34.0)), pads, tpads, dir_in=(1, 0), start_vias={'P': (4.75, 32.8), 'N': (5.25, 33.25)})
# 8. the real board: both ports routed by m4_route.route_pairs on the M3 snapshot (the pipeline's own input), else the
#    committed board with the pair nets' copper removed (a harder case: every other net is already there)
if '--quick' not in sys.argv:
    import time
    import m4_route
    src = geom.OUT / 'm3' / 'snapshot.kicad_pcb'
    stripped = False
    if not src.exists():
        src, stripped = geom.BOARD, True
    board = pcbnew.LoadBoard(str(src))
    pair_nets = {'/Top-Level Schematic/' + n for n in ('BM1_DATA_P', 'BM1_DATA_N', 'BM2_DATA_P', 'BM2_DATA_N')}
    if stripped:
        for t in [t for t in board.GetTracks() if t.GetNetname() in pair_nets]:
            board.Remove(t)
    print(f"real board: {src.name}{' (pair copper stripped)' if stripped else ''}")
    for i in range(board.GetNetInfo().GetNetCount()):
        ni = board.GetNetInfo().GetNetItem(i)
        if ni and ni.GetNetname():
            m4_route.NETS[ni.GetNetname().rsplit('/', 1)[-1]] = ni.GetNetname()
    t0 = time.time()
    g = router.Grid(board, merge={m4_route.N(nn): m4_route.N(pn) for pn, nn, *_ in m4_route.PAIRS.values()})
    m4_route.route_pairs(g, board)
    for n in m4_route.log['notes']:
        print('  ', n)
    for f_ in m4_route.log['failed']:
        print('   FAILED', f_)
    # every pair item vs every other-net item on a shared layer: 0.15 (the Default class), 0.35 to a bus net's copper
    items = []
    for f in board.GetFootprints():
        for p in f.Pads():
            if p.GetNetname():
                items.append((p.GetNetname(), p))
    for t in board.GetTracks():
        items.append((t.GetNetname(), t))
    ours = [(n, it) for n, it in items if n in pair_nets and it.GetClass() != 'PAD']
    others = [(n, it) for n, it in items if n not in pair_nets]
    worst, bad = 9.0, []
    for n, a in ours:
        bb = a.GetBoundingBox(); bb.Inflate(MM(0.4))
        for on, b_ in others:
            if not bb.Intersects(b_.GetBoundingBox()):
                continue
            need = 0.35 if router.net_class(on) == 'bus' and b_.GetClass() != 'PAD' or (router.net_class(on) == 'bus' and b_.GetClass() == 'PAD' and b_.GetParentFootprint().GetReference() not in ('T1', 'T2')) else 0.15
            for l in router.item_layers(a) & router.item_layers(b_):
                sb = b_.GetEffectiveShape(l)
                if b_.GetClass() == 'PCB_ARC':          # SHAPE::GetClearance returns 0 for an arc in 9.0.6; Collide works
                    sb = pcbnew.SHAPE_POLY_SET(); b_.TransformShapeToPolygon(sb, l, 0, MM(0.02), pcbnew.ERROR_INSIDE)
                    dd = need if not a.GetEffectiveShape(l).Collide(sb, MM(need) - 1) else 0.0
                else:
                    dd = mm(a.GetEffectiveShape(l).GetClearance(sb))
                worst = min(worst, dd)
                if dd < need - 0.001:
                    pa = geom.xy(a.GetPosition())
                    bad.append(f"{n.rsplit('/', 1)[-1]} vs {on.rsplit('/', 1)[-1]} ({b_.GetClass()}) on {board.GetLayerName(l)} at ({pa[0]:.2f}, {pa[1]:.2f}): {dd:.3f} < {need}")
    pairs_ok = all(p.get('ok') for p in m4_route.log['pairs'])
    for p in m4_route.log['pairs']:
        print('  ', p)
    for b_ in bad[:20]:
        print('   CLEARANCE', b_)
    good = pairs_ok and not bad and not m4_route.log['failed']
    if not good:
        FAILS.append('real board')
    print(f"real board: {'OK' if good else 'FAIL'}  min clearance to other nets {worst:.3f}  ({time.time() - t0:.0f} s)")

print('ALL OK' if not FAILS else f'FAILED: {FAILS}')
sys.exit(1 if FAILS else 0)
