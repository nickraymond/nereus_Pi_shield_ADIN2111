"""Routing stage G, repair: Sofar's top track from his BM1_P via at (20.057, 7.458) south into L1 pad 3 is put back.

KiCad's Python: stepG0_bm1p_restore.py <board .kicad_pcb (a copy outside git)>
Frame: X' = KiCad x - 100, y = 100 - KiCad y (mm).
The via carries BM1_P on Internal 2 from the data transformer T1 pin 6 to the bus. On the starting board (commit
325599c, Sofar's layout unchanged) a 0.2 mm top track joined the via to L1 pad 3: KiCad (165.876, 107.954) to
(167.756, 107.954) there, which is (20.057, 7.458) to (20.057, 5.578) in today's frame (the block was turned a quarter
turn: X' = 128.011 - old y, y = 173.334 - old x, checked on two vias). Stage 0c dropped it with the old bus tracks, so
T1 pin 6 has had no connection to the bus since then; DRC showed it as one unconnected item. This step adds the same
track again: same ends, same width, same layer. Nothing else."""
import sys, math
import pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); FM = pcbnew.FromMM; mm = pcbnew.ToMM
T, B, I1, I2 = (b.GetLayerID(n) for n in ("Top Layer", "6 Bottom Layer", "Internal 1", "Internal 2")); assert min(T, B, I1, I2) >= 0
def net(suffix):
    c = [n for name, n in b.GetNetsByName().items() if str(name) == suffix or str(name).endswith("/" + suffix)]
    assert len(c) == 1 and c[0].GetNetCode() > 0, (suffix, len(c)); return c[0]
def V(x, y): return pcbnew.VECTOR2I(FM(100 + x), FM(100 - y))
count = {"track": 0, "via": 0}; total = {}
def path(n, layer, w, pts):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        dx, dy = abs(x1 - x0), abs(y1 - y0); assert dx < 1e-6 or dy < 1e-6 or abs(dx - dy) < 1e-6, ("not straight or 45 deg", n, (x0, y0), (x1, y1))
        t = pcbnew.PCB_TRACK(b); t.SetStart(V(x0, y0)); t.SetEnd(V(x1, y1)); t.SetWidth(FM(w)); t.SetLayer(layer); t.SetNet(net(n)); b.Add(t)
        count["track"] += 1; total[n] = total.get(n, 0) + math.hypot(x1 - x0, y1 - y0)
def via(n, x, y, d=0.45, h=0.2):
    v = pcbnew.PCB_VIA(b); v.SetPosition(V(x, y)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(T, B)
    v.SetWidth(pcbnew.F_Cu, FM(d)); v.SetDrill(FM(h)); v.SetNet(net(n)); b.Add(v); count["via"] += 1
def expect(pads):
    for (r, num), (ex, ey) in pads.items():
        p = [q for q in b.FindFootprintByReference(r).Pads() if q.GetNumber() == num][0]
        x, y = mm(p.GetPosition().x) - 100, 100 - mm(p.GetPosition().y)
        assert abs(x - ex) < 0.01 and abs(y - ey) < 0.01, ("pad moved", r, num, (x, y), (ex, ey))
def expect_via(n, x, y):
    assert any(t.Type() == pcbnew.PCB_VIA_T and t.GetNetname().endswith(n) and abs(mm(t.GetPosition().x) - 100 - x) < 0.005 and abs(100 - mm(t.GetPosition().y) - y) < 0.005 for t in b.GetTracks()), ("via not found", n, x, y)
def done():
    pcbnew.SaveBoard(sys.argv[1], b)
    for n in sorted(total): print("  %-14s %.1f mm of new track" % (n, total[n]))
    print("added %d track segments and %d vias" % (count["track"], count["via"]))
expect({("L1", "3"): (20.971, 3.578), ("T1", "6"): (11.207, 9.743)})
expect_via("BM1_P", 20.057, 7.458)
p = [q for q in b.FindFootprintByReference("L1").Pads() if q.GetNumber() == "3"][0]
assert p.GetBoundingBox().Contains(V(20.057, 5.578)), "the track's south end is not inside L1 pad 3"
path("BM1_P", T, 0.2, [(20.057, 7.458), (20.057, 5.578)])
done()
