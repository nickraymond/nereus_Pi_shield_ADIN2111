"""Step 1: diff the board against the schematic netlist. Read-only. Usage: <KiCad python> step1_diff.py <board> <netlist>"""
import sys, collections
from s3lib import *
b = pcbnew.LoadBoard(sys.argv[1]); comps = load_netlist(sys.argv[2]); fps = by_ref(b)
print('board: %d footprints, %d tracks/vias, %d zones   netlist: %d parts' % (len(fps), len(b.GetTracks()), len(b.Zones()), len(comps)))
dele = sorted(r for r in fps if r not in comps); add = sorted(r for r in comps if r not in fps)
print('\nA. On the board, not in the schematic (to delete): %d' % len(dele))
for r in dele: print('   %-6s %-24s %s  at %s %s  board-only=%s' % (r, fps[r].GetValue()[:24], fpid_str(fps[r]), N(fps[r].GetPosition()), 'bottom' if fps[r].IsFlipped() else 'top', bool(fps[r].GetAttributes() & pcbnew.FP_BOARD_ONLY)))
print('\nB. In the schematic, not on the board (to add): %d' % len(add))
for r in add: print('   %-6s %-16s %s' % (r, comps[r]['value'], comps[r]['fpid']))
print('\nC. On both, with differences:')
cnt = collections.Counter(); nfp = 0
for r in sorted(fps):
    if r not in comps: continue
    d = diff_one(fps[r], comps[r])
    if d:
        nfp += 1; print('   ' + r)
        for k, t in d: cnt[k] += 1; print('      %-9s %s' % (k, t))
print('\n   footprints with differences: %d;  by kind: %s' % (nfp, dict(cnt)))
used = {n for c in comps.values() for n, _, _ in c['pads'].values()}
bn = {n.GetNetname() for n in b.GetNetInfo().NetsByName().values() if n.GetNetname()}
print('\nD. Nets on the board that the schematic no longer has: %s' % sorted(bn - used))
print('   Nets in the schematic that the board does not have yet: %s' % sorted(used - bn))
