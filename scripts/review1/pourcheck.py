"""Read-only: every filled piece of our GND pours ("N6 GND ...") on the outer and Internal 1 layers: which GND vias and
through-hole GND pads lie in it, and which surface GND pads. A piece with no via and no through-hole pad is tied to
ground through nothing: its pads are open. pourcheck.py <board> [--sites <zone name> <piece index> <via dia>]
With --sites: grid points (0.1 mm) inside that piece where a through GND via of that size keeps 0.2 mm from all
other-net copper on every copper layer."""
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); mm = pcbnew.ToMM; FM = pcbnew.FromMM
CU = list(b.GetEnabledLayers().CuStack())
def F(p): return "(%.2f, %.2f)" % (mm(p.x) - 100, 100 - mm(p.y))
vias = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() == "GND"]
pads = [(f.GetReference(), p) for f in b.GetFootprints() for p in f.Pads() if p.GetNetname() == "GND"]
bad = 0; pieces = {}
for z in b.Zones():
    if not z.GetZoneName().startswith("N6 GND") or z.GetIsRuleArea(): continue
    for l in z.GetLayerSet().Seq():
        f = z.GetFilledPolysList(l)
        for i in range(f.OutlineCount()):
            one = pcbnew.SHAPE_POLY_SET(); one.AddOutline(f.Outline(i))
            for h in range(f.HoleCount(i)): one.AddHole(f.Hole(i, h))
            q = one.BBox()
            v = [t for t in vias if one.Collide(t.GetPosition(), FM(0.31))]
            th = [(r, p) for r, p in pads if p.HasHole() and one.Collide(p.GetPosition(), FM(1.0))]
            sm = [(r, p) for r, p in pads if not p.HasHole() and p.IsOnLayer(l) and one.Collide(p.GetPosition(), FM(0.05))]
            tied = bool(v or th); bad += (not tied)
            pieces[(z.GetZoneName(), l, i, z.m_Uuid.AsString())] = one
            print("%-17s %-14s piece %d  X' %6.2f..%6.2f y %6.2f..%6.2f  %6.1f mm2  GND vias %d, through-hole GND pads %d, surface GND pads: %s%s" % (
                z.GetZoneName(), b.GetLayerName(l), i, mm(q.GetLeft()) - 100, mm(q.GetRight()) - 100, 100 - mm(q.GetBottom()), 100 - mm(q.GetTop()), one.Area() / 1e12,
                len(v), len(th), ", ".join("%s.%s" % (r, p.GetNumber()) for r, p in sm) or "none", "" if tied else "   <== NOT TIED TO GROUND"))
print("pieces not tied to ground: %d" % bad)
if "--sites" in sys.argv:
    k = sys.argv.index("--sites"); name, idx, dia = sys.argv[k + 1], int(sys.argv[k + 2]), float(sys.argv[k + 3])
    oth = []
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.GetNetname() != "GND": oth.append((p, [l for l in CU if p.IsOnLayer(l)] if not p.HasHole() else CU))
    for t in b.GetTracks():
        if t.GetNetname() != "GND": oth.append((t, CU if t.Type() == pcbnew.PCB_VIA_T else [t.GetLayer()]))
    for d in b.GetDrawings():
        if d.GetLayer() in CU: oth.append((d, [d.GetLayer()]))
    for (zn, l, i, u), one in pieces.items():
        if zn != name or i != idx: continue
        q = one.BBox(); good = []
        x = q.GetLeft()
        while x <= q.GetRight():
            y = q.GetTop()
            while y <= q.GetBottom():
                pt = pcbnew.VECTOR2I(x, y)
                if one.Contains(pt, -1, FM(0.0)):
                    c = pcbnew.SHAPE_CIRCLE(pt, FM(dia / 2))
                    if not any(o.GetEffectiveShape(ly).Collide(c, FM(0.2)) for o, ls in oth for ly in ls): good.append((round(mm(x) - 100, 2), round(100 - mm(y), 2)))
                y += FM(0.1)
            x += FM(0.1)
        print("free GND via sites (dia %.2f) in '%s' piece %d on %s: %d" % (dia, name, idx, b.GetLayerName(l), len(good)))
        rows = {}
        for gx, gy in good: rows.setdefault(gy, []).append(gx)
        for gy in sorted(rows, reverse=True): print("   y %.2f: X' %s" % (gy, " ".join("%.1f" % v for v in sorted(rows[gy]))))
