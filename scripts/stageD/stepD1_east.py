"""Routing stage D, part 1: the east channel. SPI from Sofar's stub ends through the series resistors R53..R56 to the
N6's P0..P3, the CS pull-up's CS side, the interrupt line to P6, the I2C lines to their pull-ups and P4 / P5, and R43.
Reset and ADIN_PWR to the west header are part 2. R52 pad 1 (ADIN_VDDIO), R9 pad 1 (CFG0_STRAP) and the N6 3V3 side
of R26 / R27 are stages G and F and are NOT in this script.

KiCad's Python: stepD1_east.py <board .kicad_pcb (a copy outside git)>
Frame: X' = KiCad x - 100, y = 100 - KiCad y (mm). Positions read from the board after the J21 move with
scripts/stageA/window.py (2026-11-18). T = top, B = bottom, I1 / I2 = Internal 1 / 2. New vias here are 0.45 / 0.20 mm,
the size of Sofar's own vias in this channel (his stub ends are 0.5 mm apart).
Where Sofar's lines end (his copper, unchanged): on top at X' 28.382 MISO (y 15.083), SCL (14.083), SDA (13.583),
INT (12.583); through vias for CS (26.157, 16.083) and SCK (26.625, 15.583); MOSI on Internal 1 at (26.508, 14.596).
Header J22: signals on the outer column X' 34.0, unconnected pins on the inner column X' 31.46. One track per gap
between two inner pads, on the gap's centre line (0.32 mm to each pad), then 45 degrees into the pin.
- MISO: top, stub to R9 pad 2, on to R54 pad 1. N6 side: gap y 18.10 to P1.
- MOSI: Internal 1 from the stub end to one new via beside R53 pad 1. N6 side: y 20.55 (above row 1) to P0.
- SCK: Internal 2 from Sofar's via to one new via south-west of R55 pad 1. N6 side: gap y 13.02 to P2.
- CS: Internal 2 from Sofar's via, west round the MISO via, to one new via west of R56 pad 1 / R52 pad 2, which are
  joined on top. N6 side: gap y 10.48 to P3.
- SCL: one via east of the stub end, bottom, south at X' 29.6 past R26 pad 1 (0.6 mm branch), gap y 7.94 to P4.
- SDA: one via south-east of the stub end, bottom, south at X' 28.3 to R27 pad 1, gap y 5.40 to P5.
- INT: top, south at X' 28.382 from the stub end, gap y 2.86 to P6.
- R43 (100 k from ADIN_PWR to GND): pad 2 to Sofar's GND via beside it; pad 1 on the bottom to test pad TP8.
No SPI track is on the bottom layer. No GND via is added beside the new SPI vias: top, Internal 1 and Internal 2 all
have the GND plane as their nearest plane here, so no line changes its reference plane, and a via that touches only
the GND plane would be reported as dangling (the routing plan asked for one; recorded as a deviation)."""
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
# what this script relies on must be where it was read (0.01 mm), else stop
PADS = {("R53", "1"): (29.6, 19.671), ("R53", "2"): (29.6, 20.529), ("R54", "1"): (29.6, 17.171), ("R54", "2"): (29.6, 18.029),
        ("R55", "1"): (29.6, 12.971), ("R55", "2"): (29.6, 13.829), ("R56", "1"): (29.6, 10.871), ("R56", "2"): (29.6, 11.729),
        ("R52", "2"): (29.6, 9.679), ("R9", "2"): (28.78, 15.083), ("R26", "1"): (29.0, 8.8), ("R27", "1"): (29.0, 6.3),
        ("R43", "1"): (30.334, 21.8), ("R43", "2"): (31.066, 21.8), ("TP8", "1"): (25.457, 11.283),
        ("J22", "1"): (34.0, 19.37), ("J22", "3"): (34.0, 16.83), ("J22", "5"): (34.0, 14.29), ("J22", "7"): (34.0, 11.75),
        ("J22", "9"): (34.0, 9.21), ("J22", "11"): (34.0, 6.67), ("J22", "13"): (34.0, 4.13)}
for (r, num), (ex, ey) in PADS.items():
    p = [q for q in b.FindFootprintByReference(r).Pads() if q.GetNumber() == num][0]
    x, y = mm(p.GetPosition().x) - 100, 100 - mm(p.GetPosition().y)
    assert abs(x - ex) < 0.01 and abs(y - ey) < 0.01, ("pad moved", r, num, (x, y), (ex, ey))
def has_end(n, layer, x, y):
    for t in b.GetTracks():
        if t.GetNet().GetNetCode() != net(n).GetNetCode(): continue
        if t.Type() == pcbnew.PCB_VIA_T:
            if layer is None and abs(mm(t.GetPosition().x) - 100 - x) < 0.01 and abs(100 - mm(t.GetPosition().y) - y) < 0.01: return True
        elif layer is not None and t.GetLayer() == layer:
            for e in (t.GetStart(), t.GetEnd()):
                if abs(mm(e.x) - 100 - x) < 0.01 and abs(100 - mm(e.y) - y) < 0.01: return True
    return False
for n, layer, x, y in (("ADIN_MISO", T, 28.382, 15.083), ("I2C0_SCL", T, 28.382, 14.083), ("I2C0_SDA", T, 28.382, 13.583), ("~{ADIN_INT}", T, 28.382, 12.583),
                       ("ADIN_MOSI", I1, 26.508, 14.596), ("~{ADIN_CS}", None, 26.157, 16.083), ("ADIN_SCK", None, 26.625, 15.583), ("GND", None, 31.732, 21.058)):
    assert has_end(n, layer, x, y), ("Sofar's stub end not found", n, x, y)
W = 0.2
# MISO
path("ADIN_MISO", T, W, [(28.382, 15.083), (29.25, 15.083), (29.6, 15.433), (29.6, 17.171)])
path("N6_MISO", T, W, [(29.6, 18.1), (32.73, 18.1), (34.0, 16.83)])
# MOSI
path("ADIN_MOSI", I1, W, [(26.508, 14.596), (27.676, 14.596), (28.75, 15.67), (28.75, 19.671)]); via("ADIN_MOSI", 28.75, 19.671)
path("ADIN_MOSI", T, W, [(28.75, 19.671), (29.6, 19.671)])
path("N6_MOSI", T, W, [(29.6, 20.55), (32.82, 20.55), (34.0, 19.37)])
# SCK
path("ADIN_SCK", I2, W, [(26.625, 15.583), (27.4, 14.808), (27.4, 13.55), (28.6, 12.35), (29.0, 12.35)]); via("ADIN_SCK", 29.0, 12.35)
path("ADIN_SCK", T, W, [(29.0, 12.35), (29.5, 12.85)])
path("N6_SCK", T, W, [(29.6, 13.829), (30.1, 13.829), (30.25, 13.679), (30.25, 13.17), (30.4, 13.02), (32.73, 13.02), (34.0, 14.29)])
# CS
path("~{ADIN_CS}", I2, W, [(26.157, 16.083), (25.6, 15.526), (25.6, 13.9), (27.0, 12.5), (27.0, 11.6), (28.35, 10.25), (28.95, 10.25)]); via("~{ADIN_CS}", 28.95, 10.25)
path("~{ADIN_CS}", T, W, [(28.95, 10.25), (29.6, 10.25)])
path("~{ADIN_CS}", T, W, [(29.6, 9.679), (29.6, 10.871)])
path("~{N6_CS}", T, W, [(29.6, 11.729), (30.1, 11.729), (30.25, 11.579), (30.25, 10.63), (30.4, 10.48), (32.73, 10.48), (34.0, 11.75)])
# SCL
path("I2C0_SCL", T, W, [(28.382, 14.083), (28.85, 14.083)]); via("I2C0_SCL", 28.85, 14.083)
path("I2C0_SCL", B, W, [(28.85, 14.083), (29.6, 13.333), (29.6, 8.8), (30.46, 7.94), (32.73, 7.94), (34.0, 9.21)])
path("I2C0_SCL", B, W, [(29.6, 8.8), (29.0, 8.8)])
# SDA
path("I2C0_SDA", T, W, [(28.382, 13.583), (28.65, 13.315)]); via("I2C0_SDA", 28.65, 13.315)
path("I2C0_SDA", B, W, [(28.65, 13.315), (28.3, 12.965), (28.3, 6.7), (28.7, 6.3), (29.0, 6.3), (29.9, 5.4), (32.73, 5.4), (34.0, 6.67)])
# INT
path("~{ADIN_INT}", T, W, [(28.382, 12.583), (28.382, 3.706), (29.228, 2.86), (32.73, 2.86), (34.0, 4.13)])
# R43
path("GND", B, W, [(31.732, 21.058), (31.066, 21.724)])
path("ADIN_PWR", B, W, [(30.334, 21.8), (30.0, 21.466), (30.0, 14.7), (28.0, 14.7), (26.0, 12.7), (26.0, 11.9)])
pcbnew.SaveBoard(sys.argv[1], b)
for n in sorted(total): print("  %-14s %.1f mm of new track" % (n, total[n]))
print("added %d track segments and %d vias" % (count["track"], count["via"]))
