"""Lock check. Usage: <KiCad python> verify_locks.py <board in (stage 1)> <board out>
 1. the 81 mote footprints: position, turn, side, every pad (position, size, net) and every graphic identical to the input board;
 2. tracks, vias: identical multiset (ends, width, layer, net, drill); zones: identical outlines, layers, nets, priority;
 3. every other footprint that was on the input board: position, turn, side, pads identical (pad nets listed where changed)."""
import sys, collections
from s3lib import *
a, c = pcbnew.LoadBoard(sys.argv[1]), pcbnew.LoadBoard(sys.argv[2])
m = {f.GetReference(): f for f in pcbnew.LoadBoard(MOTE).GetFootprints()}
def geo(f, nets=True):
    pads = sorted((p.GetNumber(), p.GetPosition().x, p.GetPosition().y, p.GetSize(pcbnew.F_Cu).x, p.GetSize(pcbnew.F_Cu).y, p.GetDrillSize().x,
                   p.GetOrientationDegrees(), tuple(p.GetLayerSet().Seq()), p.GetNetname() if nets else '') for p in f.Pads())
    gr = sorted((g.GetClass(), g.GetLayer(), g.GetBoundingBox().GetLeft(), g.GetBoundingBox().GetTop(), g.GetBoundingBox().GetRight(), g.GetBoundingBox().GetBottom()) for g in f.GraphicalItems())
    return (f.GetPosition().x, f.GetPosition().y, f.GetOrientationDegrees(), f.IsFlipped(), f.GetFPID().GetUniStringLibItemName(), tuple(pads)), tuple(gr)
fa, fc = by_ref(a), by_ref(c)
lock = sorted(r for r in fa if r in m and fa[r].GetPosition() == m[r].GetPosition())
bad = [r for r in lock if r not in fc or geo(fa[r]) != geo(fc[r]) or fpid_str(fa[r]) != fpid_str(fc[r]) or fc[r].GetPosition() != m[r].GetPosition() or fa[r].GetValue() != fc[r].GetValue()
       or [(p.GetPinFunction(), p.GetPinType()) for p in fa[r].Pads()] != [(p.GetPinFunction(), p.GetPinType()) for p in fc[r].Pads()]
       or [(x.GetName(), x.GetText()) for x in fa[r].GetFields()] != [(x.GetName(), x.GetText()) for x in fc[r].GetFields()]]
print('1. locked mote footprints: %d; changed: %d %s' % (len(lock), len(bad), bad))
def tk(t):
    v = t.GetClass() == 'PCB_VIA'
    return (t.GetClass(), t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y, t.GetWidth(pcbnew.F_Cu) if v else t.GetWidth(), -1 if v else t.GetLayer(), t.GetNetname(), t.GetDrill() if v else 0,
            (t.TopLayer(), t.BottomLayer()) if v else 0)
ta, tc = collections.Counter(tk(t) for t in a.GetTracks()), collections.Counter(tk(t) for t in c.GetTracks())
nv = lambda b: sum(1 for t in b.GetTracks() if t.GetClass() == 'PCB_VIA')
print('2. tracks + vias: in %d (vias %d), out %d (vias %d); identical: %s' % (len(a.GetTracks()), nv(a), len(c.GetTracks()), nv(c), ta == tc))
def zk(z):
    o = z.Outline(); pts = tuple((o.CVertex(i).x, o.CVertex(i).y) for i in range(o.TotalVertices()))
    return (tuple(z.GetLayerSet().Seq()), z.GetNetname(), z.GetIsRuleArea(), z.GetAssignedPriority(), z.GetZoneName(), pts)
za, zc = collections.Counter(zk(z) for z in a.Zones()), collections.Counter(zk(z) for z in c.Zones())
print('   zones: in %d, out %d; outlines / layers / nets / priority identical: %s' % (len(a.Zones()), len(c.Zones()), za == zc))
moved, netch, grch = [], [], []
for r in sorted(fa):
    if r in lock: continue
    if r not in fc: moved.append(r + ' (removed)'); continue
    if geo(fa[r], False)[0] != geo(fc[r], False)[0]: moved.append(r)
    if geo(fa[r])[0] != geo(fc[r])[0] and geo(fa[r], False)[0] == geo(fc[r], False)[0]: netch.append(r)
    if geo(fa[r])[1] != geo(fc[r])[1]: grch.append(r)
print('3. other footprints from the input board: %d; moved / turned / flipped / pad geometry or footprint name changed: %s' % (len(fa) - len(lock), moved or 'none'))
print('   pad nets changed on: %s;  graphics changed on: %s' % (netch or 'none', grch or 'none'))
print('   library nickname added to the footprint ID on: %s' % ([r for r in sorted(fa) if r in fc and fpid_str(fa[r]) != fpid_str(fc[r])] or 'none'))
print('   new footprints: %s' % sorted(r for r in fc if r not in fa))
print('   footprints: in %d, out %d' % (len(fa), len(fc)))
ok = not bad and ta == tc and za == zc and len(lock) == 81
print('LOCK CHECK:', 'PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)
