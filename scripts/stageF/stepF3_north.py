"""Routing stage F, part 3: SDA, SCL and the N6's 3V3 across the north row: from U13 to the QWIIC connector J3, with
the 3V3 branch to R49 and the pot connector J8.

KiCad's Python: stepF3_north.py <board .kicad_pcb (a copy outside git)>
Frame: X' = KiCad x - 100, y = 100 - KiCad y (mm). Positions read from the board at commit edfa070 and from parts 1
and 2 (2026-11-18). T = top, I2 = Internal 2. New vias 0.45 / 0.20 mm.
- Three parallel lines on Internal 2, from south to north SCL (0.2 mm), SDA (0.2 mm), N6 3V3 (0.4 mm), 0.2 mm or more
  apart. SCL and SDA leave part 1's vias under U13; the 3V3 line starts at a new via at (3.72, 44.35) south of C65
  pad 1 and passes north of U13. The order is fixed by that: I2C comes into U13 from the south, 3V3 crosses from
  U13's west side to its east side, so 3V3 is the north line. Running round J3's east end turns that order into
  J3's pin order (3V3 pin 2, SDA pin 3, SCL pin 4, south to north).
- East at y 45.7 / 46.1 / 46.65; north-east at 45 degrees from X' 12.5..12.9; east at y 48.8 / 49.2 / 49.75, north
  of Sofar's P_IN vias at (16.507, 44.683..47.083) and GND vias at (23.2..23.9, 47.5..48.2), under J9 and the BM2 bus
  tracks with the GND plane between; north-east again from X' 27.6..28.0; north at X' 28.75 / 29.3 / 29.85 to one via
  each east of J3's pins; top west into pins 2, 3, 4. The 3V3 via lies on part 2's top track.
- 3V3 branch: a via at (12.3, 46.65) on the 3V3 line; top from R49 pad 1 east and north at X' 12.3 to J8 pin 1
  (0.3 mm), 0.75 mm east of the pot wiper's track.
- Top from the via at (3.72, 44.35) into C65 pad 1."""
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
expect({("U13", "8"): (5.27, 45.19), ("C65", "1"): (3.72, 45.19), ("R49", "1"): (11.283, 43.932), ("J8", "1"): (12.745, 52.195),
        ("J3", "2"): (27.32, 52.745), ("J3", "3"): (27.32, 53.745), ("J3", "4"): (27.32, 54.745)})
expect_via(SDA, 6.3, 44.69); expect_via(SCL, 6.85, 45.2); expect_via(V3, 32.73, 52.745)
# the diagonals: west bend y - x = 32.8 (SCL), 33.366 (SDA), 34.144 (3V3); east bend y - x = 20.8, 21.366, 22.144
path(SCL, I2, 0.2, [(6.85, 45.2), (7.35, 45.7), (12.9, 45.7), (16.0, 48.8), (28.0, 48.8), (29.85, 50.65), (29.85, 54.745)]); via(SCL, 29.85, 54.745)
path(SDA, I2, 0.2, [(6.3, 44.69), (6.3, 45.7), (6.7, 46.1), (12.734, 46.1), (15.834, 49.2), (27.834, 49.2), (29.3, 50.666), (29.3, 53.745)]); via(SDA, 29.3, 53.745)
via(V3, 3.72, 44.35)
path(V3, I2, 0.4, [(3.72, 44.35), (3.72, 45.6), (4.77, 46.65), (12.506, 46.65), (15.606, 49.75), (27.606, 49.75), (28.75, 50.894), (28.75, 52.745)]); via(V3, 28.75, 52.745)
via(V3, 12.3, 46.65)
path(SCL, T, 0.2, [(29.85, 54.745), (27.32, 54.745)])
path(SDA, T, 0.2, [(29.3, 53.745), (27.32, 53.745)])
path(V3, T, 0.3, [(11.283, 43.932), (12.0, 43.932), (12.3, 44.232), (12.3, 51.75), (12.745, 52.195)])
path(V3, T, 0.3, [(3.72, 44.35), (3.72, 45.19)])
done()
