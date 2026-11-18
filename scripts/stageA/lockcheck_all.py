"""Lock check for the routing stages: nothing that was on the board before the stage has changed.

KiCad's Python: lockcheck_all.py <board before the stage> <board after> [--allow <uuid> ...]
Matched by uuid. Compared: footprints (position, turn, face, every pad's position, size box and net), tracks and vias
(ends, width, layer, net), graphic items on every layer (layer, box), zones and rule areas (layers, net, name,
priority, rule-area flag, every outline vertex). Zone FILLS are not compared: they are recomputed after each stage.
Items of the old board that are missing or different fail the check unless their uuid is allowed. New items are
counted by kind. Written new; same idea as verify_lock in the Pi Zero work's s3lib.py."""
import sys, collections
import pcbnew
a = pcbnew.LoadBoard(sys.argv[1]); n = pcbnew.LoadBoard(sys.argv[2])
allow = set(sys.argv[4:]) if len(sys.argv) > 3 and sys.argv[3] == "--allow" else set()
def bx(q): return (q.GetLeft(), q.GetTop(), q.GetRight(), q.GetBottom())
def sig_fp(f): return ("fp", f.GetReference(), f.GetPosition().x, f.GetPosition().y, round(f.GetOrientationDegrees(), 3), f.GetLayer(),
                       tuple(sorted((p.GetNumber(), p.GetPosition().x, p.GetPosition().y, bx(p.GetBoundingBox()), p.GetNetname()) for p in f.Pads())))
def sig_tr(t):
    if t.Type() == pcbnew.PCB_VIA_T: return ("via", t.GetPosition().x, t.GetPosition().y, t.GetDrill(), t.TopLayer(), t.BottomLayer(), t.GetNetname())
    return ("trk", t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y, t.GetWidth(), t.GetLayer(), t.GetNetname())
def sig_dr(d): return ("dr", d.GetClass(), d.GetLayer(), bx(d.GetBoundingBox()))
def sig_z(z):
    o = z.Outline(); return ("zone", tuple(z.GetLayerSet().Seq()), z.GetNetname(), z.GetZoneName(), z.GetAssignedPriority(), z.GetIsRuleArea(),
                             tuple((o.CVertex(i).x, o.CVertex(i).y) for i in range(o.TotalVertices())))
def items(b):
    d = {}
    for f in b.GetFootprints(): d[f.m_Uuid.AsString()] = sig_fp(f)
    for t in b.GetTracks(): d[t.m_Uuid.AsString()] = sig_tr(t)
    for g in b.GetDrawings(): d[g.m_Uuid.AsString()] = sig_dr(g)
    for z in b.Zones(): d[z.m_Uuid.AsString()] = sig_z(z)
    return d
A, N = items(a), items(n)
kept = collections.Counter(); bad = []
for u, s in A.items():
    if u in allow: continue
    if u not in N: bad.append(("missing", s[:8]))
    elif N[u] != s: bad.append(("changed", s[:8]))
    else: kept[s[0]] += 1
added = collections.Counter(s[0] for u, s in N.items() if u not in A)
print("unchanged: " + ", ".join("%d %s" % (kept[k], k) for k in ("fp", "trk", "via", "dr", "zone")))
print("new: " + (", ".join("%d %s" % (v, k) for k, v in sorted(added.items())) or "nothing"))
for k, s in bad[:25]: print("   ! %s: %s" % (k, s))
print("LOCK CHECK %s (%d old items missing or changed, %d allowed)" % ("PASS" if not bad else "FAIL", len(bad), len(allow)))
sys.exit(1 if bad else 0)
