"""Routing stage G, part 4: the two SPI configuration straps and the strap resistor R2 are moved away from the crystal
(Nick, routing session's chat, 2026-11-18: "Can we move the straps way from being under the crystal, even if there are
planes between to prevent noise ... we can route them a bit farther away to keep the crystal clean.").

KiCad's Python: stepG4_straps_clear_crystal.py <board .kicad_pcb (a copy outside git)>
Frame: X' = KiCad x - 100, y = 100 - KiCad y (mm). Positions read from the board of commit 2c6d93b on 2026-11-18.
The crystal Y1 (bottom layer) has its body box at X' 8.93..11.98, y 13.58..16.51; its load capacitors C8 and C7 reach
X' 7.76..12.96, y 14.15..16.32. Before this step: CFG0_STRAP ran on Internal 2 at y 15.77 straight under Y1, C8 and C7;
R2 stood on top at (9.3, 16.4), over the crystal's XTAL_I pad, with CFG1_STRAP on top at y 15.56 and the pin 19 net on
top at y 16.1 leading to it.
- CFG0_STRAP, Internal 2: from its via at (5.9, 15.56) south at X' 5.9, east at y 11.2 (2.4 mm south of the crystal's
  box, 0.6 mm north of ADIN_PWR), 45 degrees north-east between the three VBUS vias at X' 16.1 and U1's via row at
  y 14.83, east at y 14.12, 45 degrees north-east between Sofar's ~ADIN_INT via and the ADIN_PWR via, and into the old
  line at y 17.7. Its bottom part, both vias and the top stub at R9 stay.
- R2 moves to (6.6, 15.4), turned upright: pad 2 (CFG1_STRAP) at y 15.0, pad 1 (pin 19 net) at y 15.8. Both lines stay
  on the top layer at X' 6.6, 1.3 mm west of C8's pads and 2.3 mm west of Y1's pads; nothing of the straps is left
  over or under the crystal's box.
Tracks of stage G that this step replaces are removed; their uuids go to <board>.removed for the lock check, and the
run needs ALLOW_REF=R2."""
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
expect({("R2", "1"): (8.9, 16.4), ("R2", "2"): (9.7, 16.4), ("Y1", "3"): (9.569, 15.62), ("C8", "1"): (8.307, 15.585)})
expect_via("CFG0_STRAP", 5.9, 15.56); expect_via("CFG1_STRAP", 6.6, 10.48); expect_via("Net-(U1A-P1_LED_0{slash}SPI_CFG1)", 6.6, 17.3)
expect_via("~{ADIN_INT}", 20.502, 16.762); expect_via("ADIN_PWR", 21.0, 15.728); expect_via("VBUS", 16.107, 13.233); expect_via("GND", 8.207, 11.933)
C0, C1, P19 = "CFG0_STRAP", "CFG1_STRAP", "Net-(U1A-P1_LED_0{slash}SPI_CFG1)"
# 1. this session's tracks that are replaced
OLD = [(C0, I2, [(5.9, 15.56), (6.11, 15.77), (18.0, 15.77), (19.22, 16.99), (19.909, 16.99), (20.619, 17.7), (26.85, 17.7)]),
       (C1, T, [(6.6, 10.48), (6.6, 15.26), (6.9, 15.56), (9.06, 15.56), (9.7, 16.2), (9.7, 16.4)]),
       (P19, T, [(6.6, 16.3), (6.8, 16.1), (8.6, 16.1), (8.9, 16.4)])]
gone = []
def xy(p): return (mm(p.x) - 100, 100 - mm(p.y))
for n, layer, pts in OLD:
    for a_, c_ in zip(pts, pts[1:]):
        hit = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T and t.GetLayer() == layer and t.GetNetname().endswith(n)
               and sorted([xy(t.GetStart()), xy(t.GetEnd())]) == sorted([a_, c_]) or
               (t.Type() == pcbnew.PCB_TRACE_T and t.GetLayer() == layer and t.GetNetname().endswith(n)
                and all(abs(u - v) < 0.002 for p, q in zip(sorted([xy(t.GetStart()), xy(t.GetEnd())]), sorted([a_, c_])) for u, v in zip(p, q)))]
        assert len(hit) == 1, ("old segment not found once", n, a_, c_, len(hit))
        gone.append(hit[0])
uu = [t.m_Uuid.AsString() for t in gone]
for t in gone: b.Remove(t)
open(sys.argv[1] + ".removed", "w").write(" ".join(uu))
# 2. R2 upright at (6.6, 15.4), pad 1 north
r2 = b.FindFootprintByReference("R2"); r2.SetPosition(V(6.6, 15.4))
for ang in (90, 270):
    r2.SetOrientationDegrees(ang)
    pp = {p.GetNumber(): xy(p.GetPosition()) for p in r2.Pads()}
    if pp["1"][1] > pp["2"][1]: break
expect({("R2", "1"): (6.6, 15.8), ("R2", "2"): (6.6, 15.0)})
# 3. the new lines
path(C0, I2, 0.2, [(5.9, 15.56), (5.9, 11.5), (6.2, 11.2), (13.1, 11.2), (16.02, 14.12), (18.62, 14.12), (22.2, 17.7), (26.85, 17.7)])
path(C1, T, 0.2, [(6.6, 10.48), (6.6, 15.0)])
path(P19, T, 0.2, [(6.6, 16.3), (6.6, 15.8)])
print("removed %d of this session's track segments; R2 moved to (6.6, 15.4), orientation %.0f deg" % (len(uu), r2.GetOrientationDegrees()))
done()
