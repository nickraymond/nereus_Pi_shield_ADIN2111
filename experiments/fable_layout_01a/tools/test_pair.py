"""Unit test of the pair router emission (router.commit_pair) on a blank board: each net continuous from pin to pad,
P/N and obstacle clearance ≥ 0.15 mm, through turns, both swap sides, a straight via pair and a turn right after a swap.
  $PY tools/test_pair.py        (run from experiments/fable_layout_01a/)
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

def test(name, path_cells, swaps, pins, pads, extra=None):
    b = make_board()
    if extra: extra(b)
    g = router.Grid(b, merge={'N': 'P'})
    path = [(l, *router.cell(x, y)) for l, x, y in path_cells]
    stats = g.commit_pair(('P', 'N'), path, pins, pads, swaps={router.cell(*c): sd for c, sd in swaps.items()})
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
    print(f"{name}: {'OK' if ok and worst >= 0.149 else 'FAIL'}  min P-N/obstacle clearance {worst:.3f}  stats {stats}")
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
