"""Rough-layout scratch board for a mock, for a STEP export. Works ONLY on a scratch copy outside the repository.
Usage: <KiCad python> n6_rough_board.py <scratch .kicad_pcb (in/out)> <Sofar reference .kicad_pcb> <D|F|G|H>
What it does: turns Sofar's mote block (81 footprints and his tracks / vias) a quarter turn as one rigid group, places
the 5 V converter, motor driver and ADC groups, top-entry JST connectors, pin headers on the N6-facing side, mounting
holes (F) and a rectangular outline. Everything else of ours is removed, and all zones are removed: this is a
mechanical mock, not a design. Frame: KiCad x = 100 + X', KiCad y = 100 - y (X', y as in n6_mocks.py); the drill
origin is the N6's corner at the USB end on the VIN side."""
import sys, pcbnew
path, refpath, mock = sys.argv[1:4]
assert "NereusData" in path, "scratch copies only"
mm, MM = pcbnew.ToMM, pcbnew.FromMM
K = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/"
OX = OY = 100.0
XOFF = 32.13 if mock == "D" else 33.03; YOFF = 1.0
HOLE = 2.7
RAD = 0.0 if mock == "D" else 3.0          # corner radius of the outline (Nick: radius on the larger board)
b = pcbnew.LoadBoard(path); r = pcbnew.LoadBoard(refpath)
V = lambda x, y: pcbnew.VECTOR2I(MM(x), MM(y))
fps = {f.GetReference(): f for f in b.GetFootprints()}
rf = {f.GetReference(): f for f in r.GetFootprints()}
core = [f for n, f in fps.items() if n in rf and f.GetPosition() == rf[n].GetPosition() and f.GetLayer() == rf[n].GetLayer()
        and abs(f.GetOrientationDegrees() - rf[n].GetOrientationDegrees()) < 0.1]
assert len(core) == 81, len(core)
def tkey(t):
    if t.Type() == pcbnew.PCB_VIA_T: return ("v", t.GetPosition().x, t.GetPosition().y)
    p = sorted([(t.GetStart().x, t.GetStart().y), (t.GetEnd().x, t.GetEnd().y)]); return ("t", t.GetLayer(), p[0], p[1], t.GetWidth())
refkeys = {tkey(t) for t in r.GetTracks()}
tracks = list(b.GetTracks()); coretr = [t for t in tracks if tkey(t) in refkeys]; othertr = [t for t in tracks if tkey(t) not in refkeys]
def cbox(f):
    cy = f.GetCourtyard(pcbnew.F_CrtYd if f.GetLayer() == pcbnew.F_Cu else pcbnew.B_CrtYd)
    q = cy.BBox() if cy.OutlineCount() else f.GetBoundingBox(False)
    return [mm(q.GetLeft()), mm(q.GetTop()), mm(q.GetRight()), mm(q.GetBottom())]
def gbox(fl):
    bs = [cbox(f) for f in fl]; return [min(q[0] for q in bs), min(q[1] for q in bs), max(q[2] for q in bs), max(q[3] for q in bs)]
def place(fl, X0, y0, rot=0, extra=()):
    """Move a rigid group so that its courtyard box has its lower-left corner at (X', y) = (X0, y0), after turning it rot degrees."""
    if rot:
        g = gbox(fl); c = V((g[0] + g[2]) / 2, (g[1] + g[3]) / 2)
        for o in list(fl) + list(extra): o.Rotate(c, pcbnew.EDA_ANGLE(rot, pcbnew.DEGREES_T))
    g = gbox(fl); d = V(OX + X0 - g[0], OY - y0 - g[3])
    for o in list(fl) + list(extra): o.Move(d)
    g = gbox(fl); return "X' %.2f..%.2f, y %.2f..%.2f" % (g[0] - OX, g[2] - OX, OY - g[3], OY - g[1])
# 1. the mote block: quarter turn, L1 end at the USB end, the ADIN's SPI side towards the P0..P3 column (higher X')
for ang in (-90, 90):
    g = gbox(core); c = V((g[0] + g[2]) / 2, (g[1] + g[3]) / 2)
    for o in core + coretr: o.Rotate(c, pcbnew.EDA_ANGLE(ang, pcbnew.DEGREES_T))
    u1 = fps["U1"]; spi = [p for p in u1.Pads() if "ADIN_SCK" in p.GetNetname()][0]
    ok = fps["L1"].GetPosition().y > fps["L2"].GetPosition().y and spi.GetPosition().x > u1.GetPosition().x
    if ok: break
    for o in core + coretr: o.Rotate(c, pcbnew.EDA_ANGLE(-ang, pcbnew.DEGREES_T))
assert ok, "no quarter turn gives L1 at the USB end with SPI towards P0..P3"
g = gbox(core); d = V(OX + XOFF - 2.22 - g[2], OY - YOFF - g[3])     # block frame: courtyards start 2.22 mm inside the copper edge
for o in core + coretr: o.Move(d)
g = gbox(core); print("mote block turned %d deg: X' %.2f..%.2f, y %.2f..%.2f" % (ang, g[0] - OX, g[2] - OX, OY - g[3], OY - g[1]))
# 2. our groups
G = lambda s: [fps[n] for n in s.split()]
conv, motor, adc = G("U10 L6 C53 C54 C55 C56 C57 C58 R37 R38 R39 R40"), G("U12 C60 C61 C62 C63 C64 C66 R48"), G("U13 C65 C67 R49 R50 R51")
def lib(libname, name, ref, val, bottom=False):
    f = pcbnew.FootprintLoad(K + libname + ".pretty", name); f.SetReference(ref); f.SetValue(val); b.Add(f)
    f.SetPosition(V(OX, OY))
    if bottom: f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    return f
GH4, GH3, SH4 = "JST_GH_BM04B-GHS-TBT_1x04-1MP_P1.25mm_Vertical", "JST_GH_BM03B-GHS-TBT_1x03-1MP_P1.25mm_Vertical", "JST_SH_BM04B-SRSS-TB_1x04-1MP_P1.00mm_Vertical"
def conn(name, ref, val, X0, y0, rot=0): print(val, place([lib("Connector_JST", name, ref, val)], X0, y0, rot))
def header(ref, Xc, smd):
    f = lib("Connector_PinHeader_2.54mm", "PinHeader_2x08_P2.54mm_Vertical" + ("_SMD" if smd else ""), ref, "N6 header, pins soldered to the N6", bottom=True)
    ps = [p.GetPosition() for p in f.Pads()]; cx = sum(p.x for p in ps) / len(ps); cy = sum(p.y for p in ps) / len(ps)
    f.Move(pcbnew.VECTOR2I(int(MM(OX + Xc) - cx), int(MM(OY - 10.48) - cy)))
    xs = sorted({round(mm(p.GetPosition().x) - OX, 2) for p in f.Pads()}); print(ref, "pad columns X'", xs)
if mock == "D":
    W0, E, S0, N0 = 0.0, 35.56, -12.0, 48.5
    print("5 V", place(conv, 10.2, -11.2, 90)); print("motor (N6-facing side, under the MOTOR connector's edge)", place(motor, 23.2, -10.6)); print("ADC", place(adc, 26.8, 42.3))
    conn(GH4, "J10", "BM1", 0.3, -11.7); conn(GH4, "J7", "MOTOR", 28.67, -10.6, 90); conn(GH3, "J8", "POT", 27.05, 41.6)
    conn(GH4, "J9", "BM2", 1.6, 41.6); conn(SH4, "J3", "QWIIC", 0.6, 28.0, 90)
    header("J21", 2.83, False); header("J22", 32.73, False); holes = []
elif mock == "G":
    # Nick, 2026-11-17: narrower F. Connectors on the west wall, 3 mm between connector bodies ("2-3mm between
    # connectors"; the land patterns are then 1.26 mm apart); motor driver, POT and ADC on the south wall. With that
    # pitch the 5 V converter also fits on the west wall, between QWIIC and BM2, clear of the header pads.
    W0, E, S0, N0 = -3.0, 37.1, -7.5, 48.5
    print("motor (N6-facing side)", place(motor, 3.0, -7.2, 90)); print("ADC (N6-facing side)", place(adc, 23.0, -6.5))
    conn(GH3, "J8", "POT", 14.0, -7.2)
    y = -1.6
    for name, ref, val, h in ((GH4, "J7", "MOTOR", 6.69), (GH4, "J10", "BM1", 6.69), (SH4, "J3", "QWIIC", 5.29)):
        conn(name, ref, val, -2.65, y); y += h + 1.26
    print("5 V", place(conv, -2.8, 21.2)); conn(GH4, "J9", "BM2", -2.65, 36.17)
    header("J21", 2.83, True); header("J22", 32.73, True)
    holes = [(W0 + 3, S0 + 3), (E - 3, S0 + 3), (W0 + 3, N0 - 3), (E - 3, N0 - 3)]
elif mock == "H":
    # Nick, 2026-11-17, after his CAD check of mock G: the N6 sits in the shield's south-east corner (its P0-side edge
    # flush with the shield's east edge, a short strip past the USB end for the screws), 2.1 mm mounting holes.
    # East header through-hole (surface-mount pads would overhang the N6's edge by 1.3 mm), west header surface-mount.
    # Everything of ours on the west wall: BM1, MOTOR, POT, QWIIC, 5 V converter, BM2 (3 mm between connector bodies);
    # motor driver and ADC on the N6-facing side of the same strip.
    W0, E, S0, N0 = -3.0, 35.56, -4.6, 55.7
    HOLE = 2.1
    y = 0.2
    for name, ref, val, h in ((GH4, "J10", "BM1", 6.69), (GH4, "J7", "MOTOR", 6.69), (GH3, "J8", "POT", 6.69), (SH4, "J3", "QWIIC", 5.29)):
        conn(name, ref, val, -2.65, y); y += h + 1.26
    print("5 V", place(conv, -2.8, y)); conn(GH4, "J9", "BM2", -2.65, y + 12.6 + 1.26)
    print("motor (N6-facing side)", place(motor, -2.7, 21.2, 90)); print("ADC (N6-facing side)", place(adc, -2.7, 28.3))
    header("J21", 2.83, True); header("J22", 32.73, False)
    holes = [(W0 + 2.3, -2.3), (E - 2.3, -2.3), (W0 + 2.3, N0 - 2.3), (E - 2.3, N0 - 2.3)]
else:
    W0, E, S0, N0 = -3.2, 43.3, -6.0, 48.5
    print("5 V", place(conv, -2.8, 7.6)); print("motor (N6-facing side)", place(motor, 33.7, 26.5)); print("ADC (N6-facing side, under BM2)", place(adc, 33.7, 36.2))
    conn(GH4, "J10", "BM1", 33.5, 0.3); conn(GH3, "J8", "POT", 33.5, 7.2); conn(SH4, "J3", "QWIIC", 33.5, 14.1)
    conn(GH4, "J7", "MOTOR", 33.5, 19.6); conn(GH4, "J9", "BM2", 33.5, 35.5)
    header("J21", 2.83, True); header("J22", 32.73, True)
    holes = [(W0 + 3, S0 + 3), (E - 3, S0 + 3), (W0 + 3, N0 - 3), (E - 3, N0 - 3)]
for i, (X, y) in enumerate(holes):
    if HOLE == 2.1:
        f = lib("MountingHole", "MountingHole_2.2mm_M2", "H%d" % (i + 1), "2.1 mm hole")
        for pd in f.Pads():
            pd.SetDrillSize(V(2.1, 2.1))
            try: pd.SetSize(pcbnew.F_Cu, V(2.1, 2.1))
            except TypeError: pd.SetSize(V(2.1, 2.1))
            print("hole drill", mm(pd.GetDrillSize().x))
    else: f = lib("MountingHole", "MountingHole_2.7mm_M2.5", "H%d" % (i + 1), "2.7 mm hole (size to confirm)")
    f.SetPosition(V(OX + X, OY - y))
# 3. outline and origin
old_edges = [d for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts]
def edge(kind, a, c=None, e=None):
    s = pcbnew.PCB_SHAPE(b); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(0.1))
    if kind == "line": s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(V(*a)); s.SetEnd(V(*e))
    else: s.SetShape(pcbnew.SHAPE_T_ARC); s.SetCenter(V(*c)); s.SetStart(V(*a)); s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T))
    b.Add(s)
x0, x1, y0, y1, R = OX + W0, OX + E, OY - N0, OY - S0, RAD     # KiCad frame: y0 = camera-end edge, y1 = USB-end edge
edge("line", (x0 + R, y0), e=(x1 - R, y0)); edge("line", (x1, y0 + R), e=(x1, y1 - R))
edge("line", (x1 - R, y1), e=(x0 + R, y1)); edge("line", (x0, y1 - R), e=(x0, y0 + R))
if R:   # quarter arcs, each drawn clockwise on screen from its start point
    edge("arc", (x1 - R, y0), c=(x1 - R, y0 + R)); edge("arc", (x1, y1 - R), c=(x1 - R, y1 - R))
    edge("arc", (x0 + R, y1), c=(x0 + R, y1 - R)); edge("arc", (x0, y0 + R), c=(x0 + R, y0 + R))
b.GetDesignSettings().SetAuxOrigin(V(OX, OY))
print("outline %.2f x %.2f mm" % (E - W0, N0 - S0))
# 4. removals last (pcbnew objects go stale after Remove: nothing is queried afterwards)
keep = {f.GetReference() for f in core + conv + motor + adc} | {"J21", "J22", "H1", "H2", "H3", "H4"}
gone = [f for n, f in fps.items() if n not in keep]
print("removed footprints:", " ".join(sorted(f.GetReference() for f in gone)))
zones = list(b.Zones())
for o in gone + othertr + zones + old_edges: b.Remove(o)
pcbnew.SaveBoard(path, b); print("saved", path)
