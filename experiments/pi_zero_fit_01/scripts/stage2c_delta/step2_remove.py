"""Stage 2c, step 2: take off the board the footprints whose library footprint changed in the schematic (they come back
from the library in step 3). Nothing else is touched. Saved right after the removals (pcbnew wrappers go stale after Remove).
Usage: <KiCad python> step2_remove.py <board in> <netlist> <board out>"""
import sys
from s3lib import *
GROUPS = {'U12', 'C60', 'C61', 'C62', 'C63', 'C64', 'C66', 'R48', 'U13', 'C65', 'C67', 'R49', 'R50', 'R51'}
b = pcbnew.LoadBoard(sys.argv[1]); comps = load_netlist(sys.argv[2]); fps = by_ref(b)
assert not [r for r in fps if r not in comps and not fps[r].GetAttributes() & pcbnew.FP_BOARD_ONLY], 'a footprint the schematic no longer has'
swap = sorted(r for r in fps if r in comps and fpid_str(fps[r]) != comps[r]['fpid'])
assert set(swap) <= GROUPS, ('footprint change outside the two new groups', swap)
for r in swap: print('  %-4s %s -> %s' % (r, fpid_str(fps[r]), comps[r]['fpid']))
for f in [fps[r] for r in swap]: b.Remove(f)
pcbnew.SaveBoard(sys.argv[3], b); print('  removed %d footprints; saved' % len(swap))
