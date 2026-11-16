"""Pi Zero fit experiment, stage 1: board geometry and placement only (no routing, no schematic change).

Usage: <KiCad python> build_stage1.py <source board> <Sofar mote board> <output board>
Frame: the mote keeps Sofar's absolute coordinates; the new 65 x 39.5 mm outline is drawn around it at
x 113.47..178.47, y 89.34..128.84 (so "new frame" = old - (113.47, 89.34)).
New connectors are placed as library footprints with no nets (their schematic symbols come in stage 2).
"""
import pcbnew, sys, math
mm, IU = pcbnew.ToMM, pcbnew.FromMM
SRC, MOTE, OUT = sys.argv[1:4]
DX, DY, W, H, RAD = 113.47, 89.34, 65.0, 39.5, 3.0
LIB = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/'
V = lambda x, y: pcbnew.VECTOR2I(IU(x + DX), IU(y + DY))          # new-frame mm -> board point
N = lambda p: (round(mm(p.x) - DX, 2), round(mm(p.y) - DY, 2))    # board point -> new-frame mm
b, m = pcbnew.LoadBoard(SRC), pcbnew.LoadBoard(MOTE)
def key(t): return (t.GetClass(), t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y,
                    t.GetLayer() if t.GetClass() != 'PCB_VIA' else -1)
mk = {key(t) for t in m.GetTracks()}
mref = {f.GetReference(): f for f in m.GetFootprints()}
NOT_CORE = {'D3', 'C49', 'TP24'}
core = {f.GetReference() for f in b.GetFootprints() if f.GetReference() in mref and f.GetReference() not in NOT_CORE
        and f.GetPosition() == mref[f.GetReference()].GetPosition()}
print('locked core footprints:', len(core))
fp = {f.GetReference(): f for f in list(b.GetFootprints())}   # taken before any removal (later wrappers go stale)

# 1. copper: keep Sofar's tracks/vias, drop ours; keep Sofar's zones and copper shapes, drop ours
cu = set(b.GetEnabledLayers().CuStack())
def zk(z):
    bx = z.GetBoundingBox(); return (tuple(z.GetLayerSet().CuStack()), bx.GetLeft() // 100000, bx.GetTop() // 100000,
                                     bx.GetRight() // 100000, bx.GetBottom() // 100000, z.GetIsRuleArea())
def dk(d):
    bx = d.GetBoundingBox(); return (d.GetLayer(), bx.GetLeft() // 1000, bx.GetTop() // 1000, bx.GetRight() // 1000, bx.GetBottom() // 1000)
mz = {zk(z) for z in m.Zones()}
md = {dk(d) for d in m.GetDrawings() if d.GetLayer() in cu}
rm = [t for t in b.GetTracks() if key(t) not in mk]
rm += [z for z in b.Zones() if zk(z) not in mz]
SILK = {pcbnew.F_SilkS, pcbnew.B_SilkS, pcbnew.Edge_Cuts, pcbnew.F_Fab, pcbnew.B_Fab, pcbnew.Dwgs_User, pcbnew.Cmts_User}
for d in b.GetDrawings():
    L = d.GetLayer()
    if L in SILK or d.GetClass().startswith('PCB_DIM') or (L in cu and dk(d) not in md): rm.append(d)
print('to remove: our tracks/zones/board graphics =', len(rm))   # applied at the end: pcbnew wrappers go stale after Remove

# 2. footprints that leave the board
GONE = {'MP1', 'MP2', 'MP3', 'MP4', 'J2', 'J4', 'J5', 'J6', 'F1', 'TP36'}
for r in GONE: rm.append(fp.pop(r))

def put(ref, x, y, rot=None, bottom=None):
    f = fp[ref]
    if bottom is not None and f.IsFlipped() != bottom: f.Flip(f.GetPosition(), False)
    if rot is not None: f.SetOrientationDegrees(rot)
    f.SetPosition(V(x, y))

# 3. header and holes
j1 = fp['J1']; p1 = [p for p in j1.Pads() if p.GetNumber() == '1'][0].GetPosition()
j1.Move(pcbnew.VECTOR2I(V(8.37, 4.77).x - p1.x, V(8.37, 4.77).y - p1.y))
for ref, (x, y) in zip(('H1', 'H2', 'H3', 'H4'), ((3.5, 3.5), (61.5, 3.5), (61.5, 26.5), (3.5, 26.5))): put(ref, x, y)

# 4. Sofar copper that now touches a J1 pad (Nick approved removing it, 2026-11-15): report and remove
gone = []
pads = [(p.GetPosition(), p.GetSize().x / 2, p.GetNumber()) for p in j1.Pads()]
for t in list(b.GetTracks()):
    if key(t) not in mk: continue
    for pos, r, num in pads:
        seg = pcbnew.SEG(t.GetStart(), t.GetEnd())
        w = t.GetWidth(pcbnew.F_Cu) if t.GetClass() == 'PCB_VIA' else t.GetWidth()
        gap = mm(seg.Distance(pos) - r - w // 2)
        if gap < 0.2:
            gone.append((t.GetClass(), t.GetNetname().split('/')[-1], t.GetLayerName(), N(t.GetStart()), N(t.GetEnd()), 'pin ' + num, round(gap, 2)))
            rm.append(t); break
for g in gone: print('  removed Sofar item at J1:', g)

# 5. the 5 V converter group: rigid, turned so L6 ends up south-west, at the west end, top side
G5 = ['U10', 'L6', 'C53', 'C54', 'C55', 'C56', 'C57', 'C58', 'R37', 'R38', 'R39', 'R40', 'TP38']
def gbox(refs):          # (left, top, right, bottom) of the pads, board units
    q = [p.GetBoundingBox() for r in refs for p in fp[r].Pads()]
    return (min(x.GetLeft() for x in q), min(x.GetTop() for x in q), max(x.GetRight() for x in q), max(x.GetBottom() for x in q))
g = gbox(G5[:-1]); c = pcbnew.VECTOR2I((g[0] + g[2]) // 2, (g[1] + g[3]) // 2)
for r in G5: fp[r].Rotate(c, pcbnew.EDA_ANGLE(float(sys.argv[4]) if len(sys.argv) > 4 else 90.0, pcbnew.DEGREES_T))
bb = gbox(G5[:-1]); tgt = V(0.55, 7.15)
for r in G5: fp[r].Move(pcbnew.VECTOR2I(tgt.x - bb[0], tgt.y - bb[1]))
bb = gbox(G5[:-1]); print('5 V group pads box (new frame): x %.2f..%.2f y %.2f..%.2f' % (mm(bb[0]) - DX, mm(bb[2]) - DX, mm(bb[1]) - DY, mm(bb[3]) - DY), ' L6 at', N(fp['L6'].GetPosition()), ' U10 at', N(fp['U10'].GetPosition()))

# 6. south row, top side (side-entry, cable leaves south). Courtyard bottom sits 0.3 mm inside the edge.
def add(lib, name, ref, value, x_left, rot=0.0):
    f = pcbnew.FootprintLoad(LIB + lib + '.pretty', name); f.SetReference(ref); f.SetValue(value); b.Add(f)
    f.SetOrientationDegrees(rot); f.BuildCourtyardCaches(); cb = f.GetCourtyard(pcbnew.F_CrtYd).BBox()
    f.Move(pcbnew.VECTOR2I(V(x_left, 0).x - cb.GetLeft(), V(0, H - 0.3).y - cb.GetBottom()))
    cb = f.GetBoundingBox(False); fp[ref] = f
    f.BuildCourtyardCaches(); cb = f.GetCourtyard(pcbnew.F_CrtYd).BBox()
    print('  %-5s %-34s courtyard x %.2f..%.2f  y %.2f..%.2f' % (ref, name[:34], *N(cb.GetPosition()), *N(cb.GetEnd()))[:200])
    return f
GH4, GH3 = 'JST_GH_SM04B-GHS-TB_1x04-1MP_P1.25mm_Horizontal', 'JST_GH_SM03B-GHS-TB_1x03-1MP_P1.25mm_Horizontal'
ROT = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
add('Connector_JST', GH4, 'J7', 'MOTOR', 1.70, ROT)
add('Connector_JST', GH4, 'J9', 'BM2', 11.45, ROT)
add('Connector_JST', GH3, 'J8', 'POT', 21.30, ROT)
add('Connector_JST', GH4, 'J10', 'BM1', 50.60, ROT)
# Qwiic: the board's own J3 (JST SH side entry) moves into the row
j3 = fp['J3']; j3.SetOrientationDegrees(float(sys.argv[6]) if len(sys.argv) > 6 else 0.0); j3.BuildCourtyardCaches()
cb = j3.GetBoundingBox(False)
j3.Move(pcbnew.VECTOR2I(V(41.6, 0).x - cb.GetLeft(), V(0, H - 0.3).y - cb.GetBottom()))
print('  J3 (Qwiic) box', N(j3.GetBoundingBox(False).GetPosition()), N(j3.GetBoundingBox(False).GetEnd()))
# LEDs (top) with their resistors under them (bottom); order west to east: BM2 (D10), ADIN (D8), BM1 (D9)
for (d, r), x in zip((('D10', 'R46'), ('D8', 'R44'), ('D9', 'R45')), (32.3, 35.3, 38.3)):
    put(d, x, 35.6, bottom=False); put(r, x, 35.6, bottom=True)

# 7. bottom side under the south row (x 2..8 and 22..28.5 stay free for the motor driver and the ADC, stage 2)
for ref, (x, y) in zip(('JP1', 'JP2', 'JP3', 'JP4'), ((13.0, 34.3), (18.0, 34.3), (13.0, 37.4), (18.0, 37.4))):   # cut jumpers, 2 x 2
    put(ref, x, y, rot=0, bottom=True)
put('R2', 9.3, 34.0, bottom=True); put('R47', 9.3, 35.7, bottom=True); put('R9', 9.3, 37.5, bottom=True)       # strap resistors by the jumpers
put('R26', 29.6, 34.2, bottom=True); put('R27', 29.6, 36.0, bottom=True)        # I2C1 pull-ups (ADC side)
put('R10', 40.3, 34.2, bottom=True); put('R24', 40.3, 36.0, bottom=True)        # I2C3 pull-ups (Qwiic)
put('R43', 39.6, 8.0, bottom=True)                                             # ADIN_PWR pull-down, in the channel
put('TP38', 5.0, 21.2, bottom=True)                                            # 5V_PI test point, under the converter
# payload load switch, re-laid on one side (bottom), x 41.5..55.5
put('D3', 43.0, 35.8, bottom=True); put('U11', 47.5, 36.0, rot=0, bottom=True); put('C49', 50.8, 36.0, bottom=True)
put('C59', 52.8, 34.2, bottom=True); put('R34', 52.8, 36.0, bottom=True); put('R36', 52.8, 37.7, bottom=True)
put('R41', 54.7, 36.0, bottom=True); put('R42', 54.7, 37.7, bottom=True); put('TP24', 55.0, 34.0, bottom=True)
# fiducials: three corners, both sides
for (t_, b_), (x, y) in zip((('FID3', 'FID1'), ('FID4', 'FID2'), ('FID5', 'FID6')), ((8.2, 22.6), (62.6, 9.0), (62.2, 33.0))):
    put(t_, x, y); put(b_, x, y)

# 8. outline 65 x 39.5, 3 mm corners
def line(a, c):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(V(*a)); s.SetEnd(V(*c)); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(IU(0.1)); b.Add(s)
def arc(cx, cy, a0):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_ARC); s.SetCenter(V(cx, cy))
    s.SetStart(V(cx + RAD * math.cos(math.radians(a0)), cy + RAD * math.sin(math.radians(a0))))
    s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(90.0, pcbnew.DEGREES_T)); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(IU(0.1)); b.Add(s)
line((RAD, 0), (W - RAD, 0)); line((W, RAD), (W, H - RAD)); line((W - RAD, H), (RAD, H)); line((0, H - RAD), (0, RAD))
arc(RAD, RAD, 180); arc(W - RAD, RAD, 270); arc(W - RAD, H - RAD, 0); arc(RAD, H - RAD, 90)

left = sorted(r for r in fp if r not in core)
print('non-core footprints on the board:', len(left))
for x in rm: b.Remove(x)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(OUT, b); print('saved', OUT)
