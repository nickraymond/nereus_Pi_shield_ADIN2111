"""Read-only: new tracks and vias (not in the base board, by uuid) against copper of other nets on the same layer:
pairs nearer than the limits given. clearcheck.py <base board> <new board>"""
import sys, pcbnew
a = pcbnew.LoadBoard(sys.argv[1]); b = pcbnew.LoadBoard(sys.argv[2]); mm = pcbnew.ToMM; FM = pcbnew.FromMM
old = {t.m_Uuid.AsString() for t in a.GetTracks()}
new = [t for t in b.GetTracks() if t.m_Uuid.AsString() not in old]
CU = list(b.GetEnabledLayers().CuStack())
def F(p): return "(%.2f, %.2f)" % (mm(p.x) - 100, 100 - mm(p.y))
def lay(t): return CU if t.Type() == pcbnew.PCB_VIA_T else [t.GetLayer()]
others = []
for f in b.GetFootprints():
    for p in f.Pads(): others.append((p, "%s pad %s %s" % (f.GetReference(), p.GetNumber(), p.GetNetname().split("/")[-1] or "no net"), [l for l in CU if p.IsOnLayer(l)]))
for t in b.GetTracks(): others.append((t, "%s %s %s" % ("via" if t.Type() == pcbnew.PCB_VIA_T else "track", t.GetNetname().split("/")[-1], F(t.GetPosition())), lay(t)))
res = {}
for t in new:
    for l in lay(t):
        s = t.GetEffectiveShape(l)
        for o, name, ls in others:
            if l not in ls or o is t or o.GetNetname() == t.GetNetname(): continue
            if o.m_Uuid.AsString() == t.m_Uuid.AsString(): continue
            so = o.GetEffectiveShape(l)
            for lim in (0.127, 0.15, 0.2, 0.25):
                if s.Collide(so, FM(lim)):
                    k = ("%s %s %s" % ("via" if t.Type() == pcbnew.PCB_VIA_T else "track %.2f" % mm(t.GetWidth()), t.GetNetname().split("/")[-1], F(t.GetPosition())), name, b.GetLayerName(l)); res[k] = min(res.get(k, 9), lim); break
print("new items: %d. Other-net copper nearer than 0.25 mm (zone fills not included):" % len(new))
for (n, name, l), lim in sorted(res.items(), key=lambda kv: kv[1]): print("   under %.3f mm: %-34s to %-40s on %s" % (lim, n, name, l))
if not res: print("   none")
