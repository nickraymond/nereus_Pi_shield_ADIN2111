"""Step 2: link the bare connector footprints J7-J10 to their schematic symbols and give their pads the netlist's nets.
Usage: <KiCad python> step2_link_connectors.py <board in> <netlist> <board out>"""
import sys
from s3lib import *
b = pcbnew.LoadBoard(sys.argv[1]); comps = load_netlist(sys.argv[2]); fps = by_ref(b)
for r in ('J7', 'J8', 'J9', 'J10'):
    f = fps[r]; pos, rot, side = f.GetPosition(), f.GetOrientationDegrees(), f.IsFlipped()
    print('  %s: %d differences before' % (r, len(diff_one(f, comps[r]))))
    apply(b, f, r, comps[r])
    assert (f.GetPosition(), f.GetOrientationDegrees(), f.IsFlipped()) == (pos, rot, side)
    left = diff_one(f, comps[r]); assert not left, left
    print('  %s %-10s %s at %s: %s' % (r, f.GetValue(), fpid_str(f), N(pos), ', '.join('%s=%s' % (p.GetNumber(), p.GetNetname().split('/')[-1] or '(no net)') for p in f.Pads())))
pcbnew.SaveBoard(sys.argv[3], b); print('saved', sys.argv[3])
