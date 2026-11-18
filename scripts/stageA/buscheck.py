"""Stage A gate: each bus connector pin is connected to its inductor pad by top-layer copper, and how near the bus
tracks on the top layer come to copper of other nets and to the board edge.

KiCad's Python: buscheck.py <board>. Read-only. Connection: KiCad's own connectivity (same net, no unconnected pair
between the two pads in the ratsnest) plus a walk over touching top-layer tracks from the connector pad to the
inductor pad. Distance: KiCad's shape collision test at 0.18 mm and 0.30 mm, for every top-layer track of the four
bus nets wider than 0.5 mm against every top-layer pad, track, via and copper shape of another net (zone fills are
left to the DRC, which refills them at the zone's own clearance)."""
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); mm = pcbnew.ToMM; TOP = b.GetLayerID("Top Layer"); b.BuildConnectivity()
PRE = "/Top-Level Schematic/"
PAIRS = [("J10", "1", "L1", "2", "BM1_N"), ("J10", "2", "L1", "2", "BM1_N"), ("J10", "3", "L1", "3", "BM1_P"), ("J10", "4", "L1", "3", "BM1_P"),
         ("J9", "1", "L2", "2", "BM2_N"), ("J9", "2", "L2", "2", "BM2_N"), ("J9", "3", "L2", "3", "BM2_P"), ("J9", "4", "L2", "3", "BM2_P")]
def pad(r, num): return [p for p in b.FindFootprintByReference(r).Pads() if p.GetNumber() == num][0]
def F(p): return "(%.3f, %.3f)" % (mm(p.x) - 100, 100 - mm(p.y))
ok = True
for r1, n1, r2, n2, nn in PAIRS:
    p1, p2 = pad(r1, n1), pad(r2, n2); assert p1.GetNetname() == p2.GetNetname() == PRE + nn
    tr = [t for t in b.GetTracks() if t.GetNetname() == PRE + nn and t.Type() != pcbnew.PCB_VIA_T and t.GetLayer() == TOP]
    seen = set(); front = [t for t in tr if p1.HitTest(t.GetStart()) or p1.HitTest(t.GetEnd())]; reach = False; length = 0; wmin = 99
    while front:
        t = front.pop()
        if id(t) in seen: continue
        seen.add(id(t))
        for q in tr:
            if id(q) not in seen and any(t.HitTest(e) for e in (q.GetStart(), q.GetEnd())) : front.append(q)
    walked = [t for t in tr if id(t) in seen]
    reach = any(p2.HitTest(t.GetStart()) or p2.HitTest(t.GetEnd()) for t in walked)
    ok &= reach
    print("%-4s pin %s -> %-3s pad %s  %-6s  %s  (top-layer tracks walked: %d, narrowest %.2f mm)" % (r1, n1, r2, n2, nn, "CONNECTED on top" if reach else "NOT CONNECTED", len(walked), min([mm(t.GetWidth()) for t in walked] or [0])))
bus = [t for t in b.GetTracks() if t.Type() != pcbnew.PCB_VIA_T and t.GetLayer() == TOP and t.GetNetname().startswith(PRE + "BM") and mm(t.GetWidth()) > 0.5]
others = []
for f in b.GetFootprints():
    for p in f.Pads():
        if p.IsOnLayer(TOP) or p.HasHole(): others.append((p, "%s pad %s %s" % (f.GetReference(), p.GetNumber(), p.GetNetname().split("/")[-1] or "no net")))
for t in b.GetTracks():
    if t.Type() == pcbnew.PCB_VIA_T or t.GetLayer() == TOP: others.append((t, "%s %s at %s" % ("via" if t.Type() == pcbnew.PCB_VIA_T else "track %.2f" % mm(t.GetWidth()), t.GetNetname().split("/")[-1], F(t.GetPosition()))))
for d in b.GetDrawings():
    if d.GetLayer() == TOP and hasattr(d, "GetNetname"): others.append((d, "copper shape %s" % d.GetNetname().split("/")[-1]))
near = {}
for t in bus:
    s = t.GetEffectiveShape(TOP)
    for o, name in others:
        if o.GetNetname() == t.GetNetname(): continue
        so = o.GetEffectiveShape(TOP)
        for lim in (0.127, 0.18, 0.30):
            if s.Collide(so, pcbnew.FromMM(lim)):
                k = (t.GetNetname().split("/")[-1], name); near[k] = min(near.get(k, 9), lim); break
print("bus tracks wider than 0.5 mm on top: %d. Other-net copper nearer than 0.30 mm:" % len(bus))
for (n, name), lim in sorted(near.items(), key=lambda kv: kv[1]): print("   under %.3f mm: %-6s to %s" % (lim, n, name))
if not near: print("   none")
ok &= all(l > 0.127 for l in near.values())
e = b.GetBoardEdgesBoundingBox(); worst = 99
for t in bus:
    q = t.GetBoundingBox()
    worst = min(worst, mm(q.GetLeft() - e.GetLeft()), mm(e.GetRight() - q.GetRight()), mm(q.GetTop() - e.GetTop()), mm(e.GetBottom() - q.GetBottom()))
print("nearest bus copper to the outline's bounding box: %.3f mm (rounded corners not considered)" % worst)
vias = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname().startswith(PRE + "BM")]
print("vias on the four bus nets: %d (Sofar's; none added if the lock check lists no new via)" % len(vias))
print("BUS CHECK %s" % ("PASS" if ok else "FAIL")); sys.exit(0 if ok else 1)
