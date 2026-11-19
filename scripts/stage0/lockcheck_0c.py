"""Lock check for step 0c: every item of Sofar's block has the same position relative to the block as on the starting board.

KiCad's Python: lockcheck_0c.py <starting .kicad_pcb> <result .kicad_pcb> <Sofar reference .kicad_pcb> [--outlines-only]
--outlines-only: skip the comparison of zone FILLS (used on the refilled board: the fills are recomputed by KiCad
against the new outline and the header pads; outlines, nets, layers and priorities are still compared).
Written new; the idea (compare by uuid against the input board) is that of snapshot / verify_lock in
experiments/pi_zero_fit_01/scripts/stage3_routing/s3lib.py on development. Here the block has been turned, so ONE
rigid transform (a quarter turn and a shift, taken from two footprints, U1 and L1) is applied to the starting board's
coordinates and must reproduce, to the nanometre, every footprint (position, turn, face, every pad's position, size
box and net), every track and via (ends, width, layer, net), every copper shape, every zone and rule area of Sofar's
(layers, net, name, priority, every outline vertex and the filled area) on the result. Items are matched by uuid.
Sofar's items are found on the starting board by comparison with his reference board, as in step0c_board.py."""
import sys, collections
import pcbnew
a = pcbnew.LoadBoard(sys.argv[1]); n = pcbnew.LoadBoard(sys.argv[2]); r = pcbnew.LoadBoard(sys.argv[3])
GONE = ("R35", "C50", "R11", "TP19", "TP35")      # removed from the schematic in step 0a: these five leave the board
def P(*x): print(*x); sys.stdout.flush()
rf = {f.GetReference(): f for f in r.GetFootprints()}
core = [f for f in a.GetFootprints() if f.GetReference() in rf and f.GetPosition() == rf[f.GetReference()].GetPosition() and f.GetLayer() == rf[f.GetReference()].GetLayer()
        and abs(f.GetOrientationDegrees() - rf[f.GetReference()].GetOrientationDegrees()) < 0.1]
def tkey(t):
    if t.Type() == pcbnew.PCB_VIA_T: return ("v", t.GetPosition().x, t.GetPosition().y)
    p = sorted([(t.GetStart().x, t.GetStart().y), (t.GetEnd().x, t.GetEnd().y)]); return ("t", t.GetLayer(), p[0], p[1], t.GetWidth())
refkeys = {tkey(t) for t in r.GetTracks()}
coretr = [t for t in a.GetTracks() if tkey(t) in refkeys]
def zsig(z):
    o = z.Outline(); return (tuple(z.GetLayerSet().Seq()), z.GetIsRuleArea(), tuple((o.CVertex(i).x, o.CVertex(i).y) for i in range(o.TotalVertices())))
rz = {zsig(z) for z in r.Zones()}
corez = [z for z in a.Zones() if zsig(z) in rz]
corecu = [d for d in a.GetDrawings() if pcbnew.IsCopperLayer(d.GetLayer())]
N = {}
for f in n.GetFootprints(): N[f.m_Uuid.AsString()] = f
for t in n.GetTracks(): N[t.m_Uuid.AsString()] = t
for z in n.Zones(): N[z.m_Uuid.AsString()] = z
for d in n.GetDrawings(): N[d.m_Uuid.AsString()] = d
# the transform, from U1 and L1: p' = R(p - p0) + q0 with R a quarter turn
fa = {f.GetReference(): f for f in core}
u, l = fa["U1"], fa["L1"]; u2, l2 = N[u.m_Uuid.AsString()], N[l.m_Uuid.AsString()]
dx, dy = l.GetPosition().x - u.GetPosition().x, l.GetPosition().y - u.GetPosition().y
ex, ey = l2.GetPosition().x - u2.GetPosition().x, l2.GetPosition().y - u2.GetPosition().y
ROT = [k for k, (m00, m01, m10, m11) in {90: (0, -1, 1, 0), -90: (0, 1, -1, 0), 0: (1, 0, 0, 1), 180: (-1, 0, 0, -1)}.items() if (m00 * dx + m01 * dy, m10 * dx + m11 * dy) == (ex, ey)]
assert len(ROT) == 1, ROT
M = {90: (0, -1, 1, 0), -90: (0, 1, -1, 0), 0: (1, 0, 0, 1), 180: (-1, 0, 0, -1)}[ROT[0]]
def T(p):
    x, y = p.x - u.GetPosition().x, p.y - u.GetPosition().y
    return (M[0] * x + M[1] * y + u2.GetPosition().x, M[2] * x + M[3] * y + u2.GetPosition().y)
def TB(q):
    c = [T(pcbnew.VECTOR2I(x, y)) for x in (q.GetLeft(), q.GetRight()) for y in (q.GetTop(), q.GetBottom())]
    return (min(p[0] for p in c), min(p[1] for p in c), max(p[0] for p in c), max(p[1] for p in c))
def B(q): return (q.GetLeft(), q.GetTop(), q.GetRight(), q.GetBottom())
turn = (u2.GetOrientationDegrees() - u.GetOrientationDegrees()) % 360
P("transform from U1 and L1: screen turn matrix %s (U1's own angle %.1f -> %.1f deg), U1 (%.4f, %.4f) -> (%.4f, %.4f) mm" % (
    M, u.GetOrientationDegrees(), u2.GetOrientationDegrees(), pcbnew.ToMM(u.GetPosition().x), pcbnew.ToMM(u.GetPosition().y), pcbnew.ToMM(u2.GetPosition().x), pcbnew.ToMM(u2.GetPosition().y)))
bad = collections.Counter(); cnt = collections.Counter(); shown = [0]
def fail(kind, what):
    bad[kind] += 1
    if shown[0] < 25: shown[0] += 1; P("   ! %s: %s" % (kind, what))
left_on_purpose = []
for f in core:
    g = N.get(f.m_Uuid.AsString())
    if f.GetReference() in GONE:
        if g is not None: fail("footprint", f.GetReference() + " should have left the board")
        else: left_on_purpose.append(f.GetReference())
        continue
    cnt["footprints"] += 1
    if g is None: fail("footprint", f.GetReference() + " missing"); continue
    okf = (g.GetPosition().x, g.GetPosition().y) == T(f.GetPosition()) and abs(((g.GetOrientationDegrees() - f.GetOrientationDegrees()) - turn + 180) % 360 - 180) < 0.001 \
        and g.GetLayer() == f.GetLayer() and g.GetReference() == f.GetReference() and g.GetFPIDAsString() == f.GetFPIDAsString() and g.GetValue() == f.GetValue()
    pa = sorted((p.GetNumber(), T(p.GetPosition()), TB(p.GetBoundingBox()), p.GetNetname()) for p in f.Pads())
    pb = sorted((p.GetNumber(), (p.GetPosition().x, p.GetPosition().y), B(p.GetBoundingBox()), p.GetNetname()) for p in g.Pads())
    cnt["pads"] += len(pa)
    if not okf or pa != pb: fail("footprint", "%s moved differently or a pad changed" % f.GetReference())
for t in coretr:
    g = N.get(t.m_Uuid.AsString()); via = t.Type() == pcbnew.PCB_VIA_T; cnt["vias" if via else "tracks"] += 1
    if g is None: fail("track", "missing " + t.m_Uuid.AsString()); continue
    if via: same = (g.GetPosition().x, g.GetPosition().y) == T(t.GetPosition()) and g.GetWidth(pcbnew.F_Cu) == t.GetWidth(pcbnew.F_Cu) and g.GetDrillValue() == t.GetDrillValue() and g.GetNetname() == t.GetNetname() and tuple(g.GetLayerSet().Seq()) == tuple(t.GetLayerSet().Seq())
    else: same = (g.GetStart().x, g.GetStart().y) == T(t.GetStart()) and (g.GetEnd().x, g.GetEnd().y) == T(t.GetEnd()) and g.GetWidth() == t.GetWidth() and g.GetLayer() == t.GetLayer() and g.GetNetname() == t.GetNetname() and g.GetClass() == t.GetClass()
    if not same: fail("track", "changed " + t.m_Uuid.AsString())
for d in corecu:
    g = N.get(d.m_Uuid.AsString()); cnt["copper shapes"] += 1
    if g is None or g.GetLayer() != d.GetLayer() or B(g.GetBoundingBox()) != TB(d.GetBoundingBox()) or g.GetClass() != d.GetClass(): fail("shape", d.m_Uuid.AsString())
for z in corez:
    g = N.get(z.m_Uuid.AsString()); cnt["rule areas" if z.GetIsRuleArea() else "zones"] += 1
    if g is None: fail("zone", "missing %r %s" % (z.GetZoneName(), z.GetNetname())); continue
    oa, ob = z.Outline(), g.Outline(); cnt["zone outline vertices"] += oa.TotalVertices()
    va = [T(oa.CVertex(i)) for i in range(oa.TotalVertices())]; vb = [(ob.CVertex(i).x, ob.CVertex(i).y) for i in range(ob.TotalVertices())]
    same = va == vb and tuple(g.GetLayerSet().Seq()) == tuple(z.GetLayerSet().Seq()) and g.GetNetname() == z.GetNetname() and g.GetZoneName() == z.GetZoneName() \
        and g.GetAssignedPriority() == z.GetAssignedPriority() and g.GetIsRuleArea() == z.GetIsRuleArea() and g.IsFilled() == z.IsFilled()
    if same and z.IsFilled() and "--outlines-only" not in sys.argv:      # fills are derived data: after a refill only the outlines are compared
        for ly in z.GetLayerSet().Seq():
            pa2, pb2 = z.GetFilledPolysList(ly), g.GetFilledPolysList(ly)
            same = same and pa2.TotalVertices() == pb2.TotalVertices() and TB(pa2.BBox()) == B(pb2.BBox()) and abs(pa2.Area() - pb2.Area()) < 1e6
            cnt["fill vertices"] += pa2.TotalVertices()
    if not same: fail("zone", "changed %r %s on %s" % (z.GetZoneName(), z.GetNetname(), [a.GetLayerName(x) for x in z.GetLayerSet().Seq()]))
P("checked, all with the one transform: " + ", ".join("%d %s" % (v, k) for k, v in cnt.items()))
P("left the board as instructed (removed from the schematic in step 0a): " + " ".join(sorted(left_on_purpose)))
P("differences: %d %s" % (sum(bad.values()), dict(bad)))
P("LOCK", "PASS" if not bad and len(left_on_purpose) == 5 and cnt["footprints"] == 76 and cnt["tracks"] == 870 and cnt["vias"] == 185 and cnt["copper shapes"] == 17 and cnt["zones"] + cnt["rule areas"] == 170 else "FAIL")
sys.exit(1 if bad else 0)
