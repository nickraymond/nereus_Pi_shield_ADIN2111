"""Routing stage F, part 2: the N6's 3V3 in the east and south: the join of the two header 3V3 pins, the trunk north
between the east header's pad columns, the pull-ups R26 / R27, and QWIIC J3 pin 2.

KiCad's Python: stepF2_3v3_east.py <board .kicad_pcb (a copy outside git)>
Frame: X' = KiCad x - 100, y = 100 - KiCad y (mm). Positions read from the board at commit edfa070 (2026-11-18).
T = top, B = bottom, I2 = Internal 2. All Internal 2 track is 0.4 mm (the plan's width for this net).
- Join of J21 pin 15 and J22 pin 15: Internal 2, one straight line at y 0.2 along the south edge, 45 degrees into each
  pin, 31 mm, no via. The only other things on Internal 2 in that strip are Sofar's GND vias at (16.057, 1.833..3.333)
  and BM1_P vias at (22.507, 2.233..3.733), 1.1 mm or more north of the line.
- Trunk: Internal 2 from J22 pin 15 north-west into the gap between the header's two pad columns, then north at
  X' 32.73 (the gap's centre line; 0.57 mm from every pin hole) to y 52.745, one via (0.6 / 0.3 mm), then top west at
  y 52.745 into J3 pin 2. Part 3's lines reach J3 on Internal 2 from the south, west of this via; that is why the last
  4.6 mm are on top.
- Pull-ups: one via (0.45 / 0.20 mm) at (29.0, 7.94) between R27 pad 2 and R26 pad 1, bottom into R27 pad 2 (which
  is joined to R26 pad 2 since e3c8688), Internal 2 east at y 7.94 between the header's rows into the trunk (0.3 mm).
  On the bottom the pair is shut in by SDA, SCL and the header pads, so it needs the via."""
import sys, math
import pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); FM = pcbnew.FromMM; mm = pcbnew.ToMM
T, B, I2 = (b.GetLayerID(n) for n in ("Top Layer", "6 Bottom Layer", "Internal 2")); assert min(T, B, I2) >= 0
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
SDA, SCL, V3 = "I2C0_SDA", "I2C0_SCL", "N6_3V3"
expect({("J21", "15"): (4.14, 1.59), ("J22", "15"): (34.0, 1.59), ("J22", "16"): (31.46, 1.59), ("J22", "10"): (31.46, 9.21), ("J22", "12"): (31.46, 6.67),
        ("R27", "2"): (29.0, 7.1), ("R26", "1"): (29.0, 8.8), ("J3", "2"): (27.32, 52.745)})
path(V3, I2, 0.4, [(4.14, 1.59), (5.53, 0.2), (32.61, 0.2), (34.0, 1.59)])
path(V3, I2, 0.4, [(34.0, 1.59), (32.73, 2.86), (32.73, 52.745)]); via(V3, 32.73, 52.745, 0.6, 0.3)
path(V3, T, 0.4, [(32.73, 52.745), (27.32, 52.745)])
via(V3, 29.0, 7.94)
path(V3, B, 0.2, [(29.0, 7.1), (29.0, 7.94)])
path(V3, I2, 0.3, [(29.0, 7.94), (32.73, 7.94)])
done()
