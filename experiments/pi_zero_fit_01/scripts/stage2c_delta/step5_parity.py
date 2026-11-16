"""Step 5: every remaining difference between board and netlist: pad nets (J1 pins that lost their nets), pin names and
types, fields; footprints the schematic no longer has are removed; nets nothing uses any more are removed.
Locked mote footprints are never touched: a difference on one of them is reported, and stops the script if it is a net.
Usage: <KiCad python> step5_nets.py <board in> <netlist> <board out>"""
import sys
from s3lib import *
b = pcbnew.LoadBoard(sys.argv[1]); comps = load_netlist(sys.argv[2]); fps = by_ref(b); lock = locked_refs(b)
print('  locked mote footprints:', len(lock))
gone = [fps[r] for r in sorted(fps) if r not in comps and not fps[r].GetAttributes() & pcbnew.FP_BOARD_ONLY]
assert not [r for r in comps if r not in fps], 'parts still missing on the board'
for r in sorted(fps):
    if r not in comps: continue
    d = diff_one(fps[r], comps[r])
    if not d: continue
    if r in lock:
        assert all(k == 'pin' for k, _ in d), ('locked footprint needs a real change', r, d)
        print('  %s (locked, NOT changed): %s' % (r, '; '.join(t for _, t in d))); continue
    f = fps[r]; pos, rot, side = f.GetPosition(), f.GetOrientationDegrees(), f.IsFlipped()
    apply(b, f, r, comps[r]); assert (f.GetPosition(), f.GetOrientationDegrees(), f.IsFlipped()) == (pos, rot, side)
    print('  %s: %s' % (r, '; '.join('%s %s' % (k, t) for k, t in d)))
print('  footprints removed (not in the schematic):', [f.GetReference() for f in gone] or 'none')
# nets nothing uses: collect first, remove last (wrappers go stale after Remove)
used = {p.GetNetname() for f in b.GetFootprints() for p in f.Pads()} | {t.GetNetname() for t in b.GetTracks()} | {z.GetNetname() for z in b.Zones()}
dead = [n for name, n in b.GetNetInfo().NetsByName().items() if str(name) and str(name) not in used]
print('  nets removed (no pad, track or fill uses them):', sorted(n.GetNetname() for n in dead) or 'none')
for x in gone + dead: b.Remove(x)
pcbnew.SaveBoard(sys.argv[3], b); print('saved', sys.argv[3])
