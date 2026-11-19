"""Stage 0, step 0c (STAGE0_PLAN.md): bring the board in line with the stage 0 schematic and place it per mock P.

Run by run_0c.sh on a COPY of the project outside git (pcbnew.SaveBoard rewrites the .kicad_pro next to the board);
only the .kicad_pcb is copied back. KiCad's own Python:
  step0c_board.py <work .kicad_pcb (in/out)> <Sofar reference .kicad_pcb> <schematic netlist> <footprint lib dir of the project>

Where the code comes from: the frame, cbox / gbox / place, header(), the block's quarter turn, the outline and the
two BM1 tracks are taken from scripts/n6_rough_board.py (mock "P"), which is a mock builder (it drops zones, our
routing and small parts and uses library footprints without nets). New here: Sofar's zones, rule areas and drawings
turn with the block; footprints, fields, paths and pad nets follow the schematic netlist; the small parts are placed;
nothing is removed before everything else is done (pcbnew objects go stale after Remove).
Frame: KiCad x = 100 + X', KiCad y = 100 - y; the origin is the N6's corner at the USB end on the VIN side.
"""
import math, re, sys, collections
import pcbnew
sys.dont_write_bytecode = True
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import netparse
from n6_pinmap import HEADERS

path, refpath, netpath, projdir = sys.argv[1:5]
assert "NereusData" in path, "work on the copy outside git only"
mm, MM = pcbnew.ToMM, pcbnew.FromMM
OX = OY = 100.0
XOFF, YOFF = 32.13, 1.0
W0, E, S0, N0, RAD = -6.6, 35.56, -1.4, 60.6, 3.0
STOCK = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/"
LIBS = {"Vault": projdir + "/mote.pretty", "nereus": projdir + "/nereus.pretty", "urchin": projdir + "/urchin.pretty"}
def P(*a): print(*a); sys.stdout.flush()
V = lambda x, y: pcbnew.VECTOR2I(MM(x), MM(y))
XY = lambda p: (round(mm(p.x) - OX, 3), round(OY - mm(p.y), 3))
ANG = lambda a: pcbnew.EDA_ANGLE(a, pcbnew.DEGREES_T)

b = pcbnew.LoadBoard(path); r = pcbnew.LoadBoard(refpath)
F_CU, B_CU = pcbnew.F_Cu, pcbnew.B_Cu

# ------------------------------------------------------------------ the schematic netlist (source of truth)
root = netparse.sexpr(open(netpath, encoding="utf-8").read())
find, val = netparse.find, netparse.val
COMP = {}
for c in find(find(root, "components")[0], "comp"):
    fields = {}
    for fs in find(c, "fields"):
        for f in find(fs, "field"): fields[val(f, "name")] = f[2] if len(f) > 2 else ""
    props = {val(p, "name"): val(p, "value") for p in find(c, "property")}
    sp = find(c, "sheetpath")[0]
    COMP[val(c, "ref")] = dict(value=val(c, "value"), footprint=val(c, "footprint"), description=val(c, "description"), fields=fields, props=props,
                               sheet=val(sp, "names"), path=val(sp, "tstamps") + val(c, "tstamps"), pins={})
NETS = {}
for n in find(find(root, "nets")[0], "net"):
    for x in find(n, "node"):
        COMP[val(x, "ref")]["pins"][val(x, "pin")] = val(n, "name"); NETS.setdefault(val(n, "name"), []).append(val(x, "ref") + "." + val(x, "pin"))
P("netlist: %d parts, %d nets" % (len(COMP), len(NETS)))

# ------------------------------------------------------------------ 1. what is whose (nothing is changed yet)
fps = list(b.GetFootprints())
rf = {f.GetReference(): f for f in r.GetFootprints()}
core = [f for f in fps if f.GetReference() in rf and f.GetPosition() == rf[f.GetReference()].GetPosition() and f.GetLayer() == rf[f.GetReference()].GetLayer()
        and abs(f.GetOrientationDegrees() - rf[f.GetReference()].GetOrientationDegrees()) < 0.1]
assert len(core) == 81, len(core)
coreset = {f.m_Uuid.AsString() for f in core}
byref = {}
for f in fps: byref.setdefault(f.GetReference(), []).append(f)
assert all(len(v) == 1 for v in byref.values()), "duplicate references on the starting board"
byref = {k: v[0] for k, v in byref.items()}
def tkey(t):
    if t.Type() == pcbnew.PCB_VIA_T: return ("v", t.GetPosition().x, t.GetPosition().y)
    p = sorted([(t.GetStart().x, t.GetStart().y), (t.GetEnd().x, t.GetEnd().y)]); return ("t", t.GetLayer(), p[0], p[1], t.GetWidth())
refkeys = {tkey(t) for t in r.GetTracks()}
tracks = list(b.GetTracks())
coretr = [t for t in tracks if tkey(t) in refkeys]; othertr = [t for t in tracks if tkey(t) not in refkeys]
assert len(coretr) == 1055 and sum(1 for t in coretr if t.Type() == pcbnew.PCB_VIA_T) == 185, len(coretr)
def zsig(z):
    o = z.Outline(); return (tuple(z.GetLayerSet().Seq()), z.GetIsRuleArea(), tuple((o.CVertex(i).x, o.CVertex(i).y) for i in range(o.TotalVertices())))
rz = {zsig(z) for z in r.Zones()}
zones = list(b.Zones())
corez = [z for z in zones if zsig(z) in rz]; ourz = [z for z in zones if zsig(z) not in rz]
assert all(z.GetZoneName().startswith("S3") or "U10" in z.GetZoneName() for z in ourz), [z.GetZoneName() for z in ourz]
assert not any(z.GetZoneName().startswith("S3") or "U10" in z.GetZoneName() for z in corez)
def dk(d):
    q = d.GetBoundingBox(); return (d.GetLayer(), d.GetClass(), q.GetLeft(), q.GetTop(), q.GetRight(), q.GetBottom())
rd = {dk(d) for d in r.GetDrawings()}
def sane(d):
    q = d.GetBoundingBox(); return all(abs(mm(v)) < 400 for v in (q.GetLeft(), q.GetTop(), q.GetRight(), q.GetBottom()))
draws = list(b.GetDrawings())
corecu = [d for d in draws if pcbnew.IsCopperLayer(d.GetLayer())]
assert len(corecu) == 17 and all(dk(d) in rd for d in corecu)
coredoc = [d for d in draws if not pcbnew.IsCopperLayer(d.GetLayer()) and dk(d) in rd and sane(d)]       # Sofar's own drawings (not copper): turn with the block
strays = [d for d in draws if not pcbnew.IsCopperLayer(d.GetLayer()) and dk(d) in rd and not sane(d)]   # his, with out-of-range coordinates: left alone
olddraw = [d for d in draws if not pcbnew.IsCopperLayer(d.GetLayer()) and dk(d) not in rd]              # ours: outline, silkscreen, reference outlines
P("Sofar's block: %d footprints, %d tracks + %d vias, %d copper shapes, %d zones (%d rule areas), %d drawings on %s" % (
    len(core), len(coretr) - 185, 185, len(corecu), len(corez), sum(1 for z in corez if z.GetIsRuleArea()), len(coredoc),
    dict(collections.Counter(b.GetLayerName(d.GetLayer()) for d in coredoc))))
P("ours on the starting board: %d footprints, %d tracks and vias, %d zones %s, %d drawings %s; %d of Sofar's drawings with out-of-range coordinates left as they are" % (
    len(fps) - 81, len(othertr), len(ourz), sorted(z.GetZoneName() for z in ourz), len(olddraw), dict(collections.Counter(b.GetLayerName(d.GetLayer()) for d in olddraw)), len(strays)))
groups = list(b.Groups())

# ------------------------------------------------------------------ helpers from the mock builder
def cbox(f):
    cy = f.GetCourtyard(pcbnew.F_CrtYd if f.GetLayer() == F_CU else pcbnew.B_CrtYd)
    q = cy.BBox() if cy.OutlineCount() else f.GetBoundingBox(False)
    return [mm(q.GetLeft()), mm(q.GetTop()), mm(q.GetRight()), mm(q.GetBottom())]
def gbox(fl):
    bs = [cbox(f) for f in fl]; return [min(q[0] for q in bs), min(q[1] for q in bs), max(q[2] for q in bs), max(q[3] for q in bs)]
def place(fl, X0, y0, rot=0):
    if rot:
        g = gbox(fl); c = V((g[0] + g[2]) / 2, (g[1] + g[3]) / 2)
        for o in fl: o.Rotate(c, ANG(rot))
    g = gbox(fl); d = V(OX + X0 - g[0], OY - y0 - g[3])
    for o in fl: o.Move(d)
    g = gbox(fl); return "X' %.2f..%.2f, y %.2f..%.2f" % (g[0] - OX, g[2] - OX, OY - g[3], OY - g[1])
def box(f):      # courtyard box in the mock frame: (X'0, y0, X'1, y1)
    q = cbox(f); return (q[0] - OX, OY - q[3], q[2] - OX, OY - q[1])

# ------------------------------------------------------------------ 2. the block's quarter turn, as ONE rigid group
ride = [byref["R9"], byref["R43"]]      # ours, kept where the Pi board has them relative to the block (ROUTING_PLAN_P section 5, row 6)
rigid = core + coretr + corecu + corez + coredoc + ride
ok = False
for ang in (-90, 90):
    g = gbox(core); c = V((g[0] + g[2]) / 2, (g[1] + g[3]) / 2)
    for o in rigid: o.Rotate(c, ANG(ang))
    u1 = byref["U1"]; spi = [p for p in u1.Pads() if "ADIN_SCK" in p.GetNetname()][0]
    ok = byref["L1"].GetPosition().y > byref["L2"].GetPosition().y and spi.GetPosition().x > u1.GetPosition().x
    if ok: break
    for o in rigid: o.Rotate(c, ANG(-ang))
assert ok, "no quarter turn gives L1 at the USB end with SPI towards P0..P3"
g = gbox(core); d = V(OX + XOFF - 2.22 - g[2], OY - YOFF - g[3])
for o in rigid: o.Move(d)
g = gbox(core)
P("block turned %d deg about (%.4f, %.4f), then moved (%.4f, %.4f): courtyards X' %.2f..%.2f, y %.2f..%.2f; U1 at %s, L1 at %s, L2 at %s" % (
    ang, mm(c.x), mm(c.y), mm(d.x), mm(d.y), g[0] - OX, g[2] - OX, OY - g[3], OY - g[1], XY(u1.GetPosition()), XY(byref["L1"].GetPosition()), XY(byref["L2"].GetPosition())))

# ------------------------------------------------------------------ 3. footprints that go, stay, or are new (by object)
gone_core = [byref[n] for n in ("R35", "C50", "R11", "TP19", "TP35")]
assert all(f.m_Uuid.AsString() in coreset for f in gone_core) and not any(f.GetReference() in COMP for f in gone_core)
REPLACE = ("J3", "J7", "J8", "J9", "J10")       # same reference, new (top-entry) footprint: the old object goes
gone = [f for f in fps if f.GetReference() not in COMP or f.GetReference() in REPLACE]
keep = [f for f in fps if f not in gone]
for f in keep:
    assert f.GetFPIDAsString() == COMP[f.GetReference()]["footprint"], (f.GetReference(), f.GetFPIDAsString(), COMP[f.GetReference()]["footprint"])
NEW = {}
def libload(lib_id):
    nick, name = lib_id.split(":", 1)
    f = pcbnew.FootprintLoad(LIBS.get(nick, STOCK + nick + ".pretty"), name); assert f is not None, lib_id
    f.SetFPID(pcbnew.LIB_ID(nick, name)); return f
def add(ref, like=None):
    """A new footprint for schematic part `ref`: from the library named in the netlist, or a copy of the existing footprint `like`
    (same library footprint, already on this board) so that its fields, layers and attributes are those of its twin."""
    c = COMP[ref]
    if like:
        src = byref[like]; assert src.GetFPIDAsString() == c["footprint"], (ref, like)
        f = pcbnew.Cast_to_FOOTPRINT(src.Duplicate(False))
        if f.IsFlipped(): f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        f.SetOrientationDegrees(0)
    else:
        f = libload(c["footprint"])
    b.Add(f); f.SetPosition(V(OX, OY)); f.SetReference(ref); NEW[ref] = f
    return f
for ref in ("J21", "J22") + REPLACE: add(ref)
for ref, like in (("R52", "R7"), ("R53", "R38"), ("R54", "R38"), ("R55", "R38"), ("R56", "R38"), ("C68", "C2"), ("TP44", "TP43"), ("TP45", "TP43")):
    add(ref, like)
final = {f.GetReference(): f for f in keep}; final.update(NEW)
assert set(final) == set(COMP), (sorted(set(COMP) - set(final)), sorted(set(final) - set(COMP)))

# fields, schematic link and attributes of the new footprints; pad nets of every footprint
def sync(f, c, ref):
    f.SetValue(c["value"]); f.SetPath(pcbnew.KIID_PATH(c["path"]))
    f.SetSheetname(c["props"].get("Sheetname", c["sheet"])); f.SetSheetfile(c["props"].get("Sheetfile", ""))
    want = dict(c["fields"]); want.pop("Footprint", None)
    want["Datasheet"] = want.get("Datasheet", ""); want["Description"] = c["description"]
    have = {x.GetName(): x for x in f.GetFields()}
    for name, x in have.items():
        if name in ("Reference", "Value"): continue
        if name in want: x.SetText(want[name])
        elif name not in ("Footprint", "KiLib_Generator"): f.Remove(x)
    for name, v in want.items():
        if name not in have and name not in ("Reference", "Value"):
            x = pcbnew.PCB_FIELD(f, pcbnew.FIELD_T_USER, name); x.SetText(v); x.SetVisible(False); x.SetLayer(pcbnew.F_Fab if not f.IsFlipped() else pcbnew.B_Fab)
            x.SetPosition(f.GetPosition()); f.Add(x)
    a = f.GetAttributes()
    for flag, key in ((pcbnew.FP_EXCLUDE_FROM_BOM, "exclude_from_bom"), (pcbnew.FP_DNP, "dnp"), (pcbnew.FP_EXCLUDE_FROM_POS_FILES, "exclude_from_pos_files")):
        a = (a | flag) if key in c["props"] else (a & ~flag) if key != "exclude_from_pos_files" else a
    f.SetAttributes(a)
for ref, f in NEW.items(): sync(f, COMP[ref], ref)
def net(name):
    n = b.FindNet(name)
    if n is None:
        n = pcbnew.NETINFO_ITEM(b, name); b.Add(n)
    return n
changed, coremis = [], []
for ref, f in sorted(final.items()):
    for p in f.Pads():
        want = COMP[ref]["pins"].get(p.GetNumber(), "")
        if p.GetNetname() == want: continue
        if f.m_Uuid.AsString() in coreset: coremis.append((ref, p.GetNumber(), p.GetNetname(), want)); continue
        if ref not in NEW: changed.append("%s.%s %s -> %s" % (ref, p.GetNumber(), p.GetNetname().split("/")[-1] or "(none)", want.split("/")[-1] or "(none)"))
        if want: p.SetNet(net(want))
        else: p.SetNetCode(0)
P("pad nets changed on kept footprints of ours (%d): %s" % (len(changed), "; ".join(changed)))
P("pad nets of Sofar's kept footprints that differ from the netlist (must be none): %s" % coremis)
assert not coremis

# ------------------------------------------------------------------ 4. placement per mock P
def conn(ref, X0, y0, rot=0): P("  %-4s %s" % (ref, place([NEW[ref]], X0, y0, rot)))
def header(ref, Xc):
    f = NEW[ref]; f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    ps = [p.GetPosition() for p in f.Pads()]; cx = sum(p.x for p in ps) / len(ps); cy = sum(p.y for p in ps) / len(ps)
    f.Move(pcbnew.VECTOR2I(int(MM(OX + Xc) - cx), int(MM(OY - 10.48) - cy)))
G = lambda s: [final[n] for n in s.split()]
def overlaps(fl):
    return {tuple(sorted((a.GetReference(), c2.GetReference()))) for i, a in enumerate(fl) for c2 in fl[i + 1:] if a.GetLayer() == c2.GetLayer() and hit(box(a), box(c2))}
def hit(a, c2): return a[0] < c2[2] and c2[0] < a[2] and a[1] < c2[3] and c2[1] < a[3]
INHERITED = overlaps([f for f in keep if f.m_Uuid.AsString() not in coreset])
conv, motor, adc = G("U10 L6 C53 C54 C55 C56 C57 C58 R37 R38 R39 R40"), G("U12 C60 C61 C62 C63 C64 C66 R48"), G("U13 C65 C67 R49 R50 R51")
P("placement as mock P (courtyard boxes):")
conn("J7", -0.5, 49.3, 90); conn("J8", 7.45, 49.3, 90); conn("J9", 15.4, 49.3, 90); conn("J3", 23.35, 49.3, 90); conn("J10", 5.9, -1.1, 270)
P("  5 V converter group", place(conv, -4.05, 24.0)); P("  motor driver group (N6-facing side)", place(motor, -6.3, 38.5, 90))
c0 = adc[0].GetPosition()
for f in adc: f.Flip(c0, pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
P("  ADC group (top face)", place(adc, 3.3, 42.2))
P("  JP3 (N6-facing side)", place([final["JP3"]], -6.2, 9.0)); P("  JP4 (N6-facing side)", place([final["JP4"]], -6.2, 12.6))
header("J21", 2.83); header("J22", 32.73)
HOLES = {"H1": (-3.6, 1.6), "H2": (-3.6, 57.6), "H3": (32.56, 57.6)}
for ref, (X, y) in HOLES.items(): final[ref].SetPosition(V(OX + X, OY - y))

# the two BM1 tracks, exactly as the mock draws them
j10 = NEW["J10"]; pin = {pd.GetNumber(): XY(pd.GetPosition()) for pd in j10.Pads() if pd.GetNumber() in "1234"}
P("  BM1 pins (X', y):", pin, {k: COMP["J10"]["pins"][k].split("/")[-1] for k in sorted(pin)})
newtr = []
def trk(netname, pts, w):
    for a, c2 in zip(pts, pts[1:]):
        s = pcbnew.PCB_TRACK(b); s.SetNet(net("/Top-Level Schematic/" + netname)); s.SetLayer(F_CU); s.SetWidth(MM(w))
        s.SetStart(V(OX + a[0], OY - a[1])); s.SetEnd(V(OX + c2[0], OY - c2[1])); b.Add(s); newtr.append(s)
xp = pin["3"][0] + 0.55
for k in pin: pin[k] = (xp, pin[k][1])
yn = (pin["1"][1] + pin["2"][1]) / 2; yp = (pin["3"][1] + pin["4"][1]) / 2
trk("BM1_N", [pin["1"], pin["2"]], 0.6)
trk("BM1_N", [(xp, yn), (12.2, yn), (12.2 + (5.7 - yn), 5.7), (13.8, 5.7), (15.7, 7.6), (18.1, 7.6)], 2.0)
trk("BM1_N", [(18.1, 7.6), (19.9, 9.4)], 1.6)
trk("BM1_N", [(19.9, 9.4), (21.0, 10.5), (21.0, 12.1)], 2.0)
trk("BM1_P", [pin["3"], pin["4"]], 0.6)
trk("BM1_P", [(xp, yp), (13.8 - (yp - 2.0), yp), (13.8, 2.0)], 2.0)
trk("BM1_P", [(13.8, 2.0), (15.7, 0.1)], 1.4); trk("BM1_P", [(15.7, 0.1), (20.0, 0.1), (21.0, 1.1), (21.0, 3.6)], 2.0)

# ------------------------------------------------------------------ small parts: free places, found by search
placed = set(f.m_Uuid.AsString() for f in core + ride + conv + motor + adc + [final["JP3"], final["JP4"], final["H1"], final["H2"], final["H3"]]
             + [NEW[n] for n in ("J21", "J22") + REPLACE]) - {f.m_Uuid.AsString() for f in gone}
def padbox(p, grow=0.0):
    q = p.GetBoundingBox(); return (mm(q.GetLeft()) - OX - grow, OY - mm(q.GetBottom()) - grow, mm(q.GetRight()) - OX + grow, OY - mm(q.GetTop()) + grow)
def hit(a, c2): return a[0] < c2[2] and c2[0] < a[2] and a[1] < c2[3] and c2[1] < a[3]
def inside(q, m=0.5):   # box inside the rounded outline, m from the edge
    if q[0] < W0 + m or q[2] > E - m or q[1] < S0 + m or q[3] > N0 - m: return False
    for cx, cy, sx, sy in ((W0 + RAD, S0 + RAD, -1, -1), (E - RAD, S0 + RAD, 1, -1), (W0 + RAD, N0 - RAD, -1, 1), (E - RAD, N0 - RAD, 1, 1)):
        px, py = (q[0] if sx < 0 else q[2]), (q[1] if sy < 0 else q[3])
        if (px - cx) * sx > 0 and (py - cy) * sy > 0 and math.hypot(px - cx, py - cy) > RAD - m: return False
    return True
HEADPADS = [padbox(p, 0.3) for h in ("J21", "J22") for p in NEW[h].Pads()]
CONNPADS = [padbox(p, 0.2) for h in REPLACE for p in NEW[h].Pads()]
def copper(face):     # (kind, geometry) of copper on that outer layer that a new pad must stay clear of
    out = []
    for t in coretr + newtr:
        if t.Type() == pcbnew.PCB_VIA_T:
            x, y = XY(t.GetPosition()); out.append(("c", x, y, mm(t.GetWidth(face)) / 2))
        elif t.GetLayer() == face:
            out.append(("s", XY(t.GetStart()), XY(t.GetEnd()), mm(t.GetWidth()) / 2))
    for z in corez:
        if not z.GetIsRuleArea() and face in z.GetLayerSet().Seq():
            q = z.Outline().BBox(); out.append(("b", (mm(q.GetLeft()) - OX, OY - mm(q.GetBottom()), mm(q.GetRight()) - OX, OY - mm(q.GetTop()))))
    for d0 in corecu:
        if d0.GetLayer() == face:
            q = d0.GetBoundingBox(); out.append(("b", (mm(q.GetLeft()) - OX, OY - mm(q.GetBottom()), mm(q.GetRight()) - OX, OY - mm(q.GetTop()))))
    return out
COPPER = {F_CU: copper(F_CU), B_CU: copper(B_CU)}
def obox(o):
    if o[0] == "b": return o[1]
    if o[0] == "c": return (o[1] - o[3], o[2] - o[3], o[1] + o[3], o[2] + o[3])
    return (min(o[1][0], o[2][0]) - o[3], min(o[1][1], o[2][1]) - o[3], max(o[1][0], o[2][0]) + o[3], max(o[1][1], o[2][1]) + o[3])
COPPER = {k: [(obox(o), o) for o in v] for k, v in COPPER.items()}
def clear_of_copper(q, face, cl=0.25):
    g = (q[0] - cl, q[1] - cl, q[2] + cl, q[3] + cl)
    for ob, o in COPPER[face]:
        if not hit(g, ob): continue
        if o[0] == "b":
            if hit(q, (o[1][0] - cl, o[1][1] - cl, o[1][2] + cl, o[1][3] + cl)): return False
        elif o[0] == "c":
            dx = max(q[0] - o[1], 0, o[1] - q[2]); dy = max(q[1] - o[2], 0, o[2] - q[3])
            if math.hypot(dx, dy) < o[3] + cl: return False
        else:
            (x1, y1), (x2, y2), hw = o[1], o[2], o[3]
            n = max(1, int(math.hypot(x2 - x1, y2 - y1) / 0.1))
            for i in range(n + 1):
                x, y = x1 + (x2 - x1) * i / n, y1 + (y2 - y1) * i / n
                if math.hypot(max(q[0] - x, 0, x - q[2]), max(q[1] - y, 0, y - q[3])) < hw + cl: return False
    return True
def occupied(face):
    # the headers' courtyard (their plastic) counts on the N6-facing side only; on the top face their pad field does; holes count on both
    out = [box(f) for f in final.values() if f.m_Uuid.AsString() in placed and (f.GetLayer() == face or f.GetReference() in HOLES)]
    return out + HEADPADS + (CONNPADS if face == B_CU else [])
def spot(ref, face, near, region, rot=None, gap=0.15, step=0.1):
    """Put footprint `ref` on `face` at the free place nearest to `near` inside `region` (X'0, y0, X'1, y1): its courtyard clear of every
    other courtyard on that face by `gap`, 0.5 mm inside the outline, not on a header's pad field, not on the opposite face of a
    connector's pads, its pads 0.25 mm clear of Sofar's outer-layer copper and of the BM1 tracks."""
    f = final[ref]; placed.discard(f.m_Uuid.AsString())
    if (f.GetLayer() == B_CU) != (face == B_CU): f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    best = None
    for rr in ([rot] if rot is not None else [0, 90]):
        f.SetOrientationDegrees(rr); f.SetPosition(V(OX, OY))
        q0 = box(f); pads0 = [padbox(p) for p in f.Pads()]
        occ = occupied(face)
        xs = [region[0] + i * step for i in range(int((region[2] - region[0]) / step) + 1)]; ys = [region[1] + i * step for i in range(int((region[3] - region[1]) / step) + 1)]
        cand = sorted(((math.hypot(x - near[0], y - near[1]), x, y) for x in xs for y in ys))
        for dist, x, y in cand:
            if best and dist >= best[0]: break
            q = (q0[0] + x, q0[1] + y, q0[2] + x, q0[3] + y)
            if not inside(q): continue
            g = (q[0] - gap, q[1] - gap, q[2] + gap, q[3] + gap)
            if any(hit(g, o) for o in occ): continue
            if not all(clear_of_copper((p[0] + x, p[1] + y, p[2] + x, p[3] + y), face) for p in pads0): continue
            best = (dist, x, y, rr); break
    assert best, "no free place for %s near %s in %s" % (ref, near, region)
    f.SetOrientationDegrees(best[3]); f.SetPosition(V(OX + best[1], OY - best[2])); placed.add(f.m_Uuid.AsString())
    return "%s at (%.2f, %.2f), %.1f mm from the aim %s" % (ref, best[1], best[2], best[0], near)
WHERE = []
def put(ref, face, near, region, why, rot=None, gap=0.15):
    if ref.startswith(("TP", "FID")): rot = 0
    faces = face if isinstance(face, tuple) else (face,)       # several faces: the one with the nearer free place wins
    if len(faces) > 1:
        dist = {}
        for fc in faces:
            try: dist[fc] = float(re.search(r"\), ([\d.]+) mm from", spot(ref, fc, near, region, rot, gap)).group(1))
            except AssertionError: pass
        faces = (min(dist, key=dist.get),)
    WHERE.append((ref, why, spot(ref, faces[0], near, region, rot, gap) + (", N6-facing side" if faces[0] == B_CU else ", top face")))
    return XY(final[ref].GetPosition())
EAST = (28.4, 0.6, 31.0, 21.5)        # east channel between the block and the east header's inner column
WING = (-6.1, 4.0, 0.4, 21.5)         # west wing beside the west header
WINGN = (-6.1, 21.0, 9.5, 49.0)       # wing and block edge above the west header
pv = {n: XY([p for p in NEW["J22"].Pads() if p.GetNumber() == n][0].GetPosition()) for n in ("1", "3", "5", "7", "9", "11")}
u10 = XY(final["U10"].GetPosition()); u13 = XY(final["U13"].GetPosition()); c65 = XY(final["C65"].GetPosition())
node19 = (10.79, 19.34)               # Sofar's via on U1 pin 19's net (ROUTING_PLAN_P, section 5 row 6)
# R9 keeps its place at MISO's stub, (28.78, 15.48), in the same channel: the series resistors go north and south of it
put("R53", F_CU, (29.55, pv["1"][1] + 0.7), EAST, "MOSI series, beside P0, top face, east channel")
put("R54", F_CU, (29.55, pv["3"][1] + 0.8), EAST, "MISO series, beside P1, just north of R9 at Sofar's MISO stub end")
put("R55", F_CU, (29.55, pv["5"][1] - 0.9), EAST, "SCK series, beside P2, just south of R9")
put("R56", F_CU, (29.55, pv["7"][1] - 0.3), EAST, "CS series, beside P3")
put("R52", F_CU, (29.55, pv["7"][1] - 2.2), EAST, "CS pull-up, next to R56 on its ADIN side")
put("R26", B_CU, (29.55, pv["9"][1]), EAST, "SCL pull-up beside P4, N6-facing side")
put("R27", B_CU, (29.55, pv["11"][1]), EAST, "SDA pull-up beside P5, N6-facing side")
ridepos = XY(final["R43"].GetPosition())
put("R43", B_CU, ridepos, (5.0, 0.6, 31.0, 30.0), "ADIN_PWR pull-down: its Pi-board place relative to the block is under the east header's body, so the nearest free place")
r2 = put("R2", (B_CU, F_CU), node19, (5.0, 10.0, 28.0, 30.0), "CFG1 strap resistor, nearest free place to U1 pin 19's via (10.79, 19.34)")
r47 = put("R47", (B_CU, F_CU), node19, (5.0, 10.0, 28.0, 30.0), "ADIN_TIMER resistor, nearest free place to U1 pin 19's via")
put("R37", F_CU, (u10[0], u10[1] + 3.0), (-6.1, 21.5, 5.0, 40.0), "feedback divider, top face north of U10 (C53 stays under U10)")
put("R38", F_CU, (u10[0], u10[1] + 3.0), (-6.1, 21.5, 5.0, 40.0), "feedback divider, top face north of U10")
put("C68", F_CU, c65, WINGN, "1 uF beside C65 at U13")
put("JP2", F_CU, (-4.45, 8.0), WING, "LED jumper, top face of the west wing beside the header")
for led, res, y in (("D8", "R44", 19.6), ("D9", "R45", 16.2), ("D10", "R46", 12.8)):
    put(led, F_CU, (-5.2, y), WING, "LED, top face of the west wing")
    put(res, F_CU, (-3.7, y), WING, "its series resistor beside it")
c56 = XY(final["C56"].GetPosition())
put("TP38", B_CU, c56, (-6.1, 23.6, 0.6, 37.0), "5V_PI test point, N6-facing side under the converter's output capacitors", gap=0.3)
put("TP24", B_CU, (-5.0, 36.3), (-6.1, 23.6, 0.6, 38.0), "GND test point, N6-facing side under the converter", gap=0.3)
m0 = XY(final["U12"].GetPosition())
put("TP40", B_CU, (m0[0] + 3.0, m0[1] - 3.0), WINGN, "MOTOR_IN1 test point at the motor driver", gap=0.3)
put("TP41", B_CU, (m0[0] + 3.0, m0[1]), WINGN, "MOTOR_OUT1 test point at the motor driver", gap=0.3)
put("TP42", F_CU, (m0[0] + 3.0, m0[1] + 3.0), WINGN, "MOTOR_OUT2 test point, top face", gap=0.3)
put("TP43", B_CU, (u13[0], u13[1]), WINGN, "I2C0_SCL test point at U13, N6-facing side", gap=0.3)
put("TP44", B_CU, (u13[0], u13[1] - 2.5), WINGN, "ADC ALERT test point at U13, N6-facing side", gap=0.3)
put("TP45", (B_CU, F_CU), r47, (5.0, 8.0, 28.0, 32.0), "ADIN_TIMER test point at R47", gap=0.3)
for ref, face, near in (("FID3", F_CU, (-5.0, 22.0)), ("FID4", F_CU, (33.6, 46.5)), ("FID5", F_CU, (33.6, 24.0)),
                        ("FID1", B_CU, (-4.6, 5.6)), ("FID2", B_CU, (33.6, 46.5)), ("FID6", B_CU, (33.6, 24.0))):
    put(ref, face, near, (W0, S0, -2.9, N0) if near[0] < 0 else (30.6, S0, E, N0), "fiducial (west wing / east strip)", gap=0.3)
left = sorted(ref for ref, f in final.items() if f.m_Uuid.AsString() not in placed)
assert not left, "not placed: %s" % left

# ------------------------------------------------------------------ outline, origin, silkscreen
def edge(kind, a, c2=None, e=None):
    s = pcbnew.PCB_SHAPE(b); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(0.1))
    if kind == "line": s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(V(*a)); s.SetEnd(V(*e))
    else: s.SetShape(pcbnew.SHAPE_T_ARC); s.SetCenter(V(*c2)); s.SetStart(V(*a)); s.SetArcAngleAndEnd(ANG(90))
    b.Add(s)
x0, x1, y0, y1 = OX + W0, OX + E, OY - N0, OY - S0
edge("line", (x0 + RAD, y0), e=(x1 - RAD, y0)); edge("line", (x1, y0 + RAD), e=(x1, y1 - RAD))
edge("line", (x1 - RAD, y1), e=(x0 + RAD, y1)); edge("line", (x0, y1 - RAD), e=(x0, y0 + RAD))
edge("arc", (x1 - RAD, y0), c2=(x1 - RAD, y0 + RAD)); edge("arc", (x1, y1 - RAD), c2=(x1 - RAD, y1 - RAD))
edge("arc", (x0 + RAD, y1), c2=(x0 + RAD, y1 - RAD)); edge("arc", (x0, y0 + RAD), c2=(x0 + RAD, y0 + RAD))
b.GetDesignSettings().SetAuxOrigin(V(OX, OY)); b.GetDesignSettings().SetGridOrigin(V(OX, OY))
P("outline %.2f x %.2f mm, corner radius %.1f; drill / place origin at the N6's corner" % (E - W0, N0 - S0, RAD))
LABELS = [("MOTOR", 2.8, 59.6, 0, "F"), ("POT", 10.8, 59.6, 0, "F"), ("BM2", 18.7, 59.6, 0, "F"), ("QWIIC", 26.0, 59.6, 0, "F"),
          ("BM1", 8.7, 9.6, 0, "F"), ("5V REG", -2.6, 23.0, 0, "F"), ("ADC", 1.6, 45.0, 90, "F"),
          ("MOTOR DRV", -1.6, 46.0, 0, "B"), ("SPI CFG", -3.4, 7.8, 0, "B"), ("CFG1", -3.4, 16.3, 0, "B"), ("CFG0", -3.4, 17.9, 0, "B"),
          ("0 | 1", -3.2, 19.5, 0, "B"), ("0/0 =", -3.2, 21.0, 0, "B"), ("OA+CRC", -3.2, 22.5, 0, "B")]
for txt, tx, ty, rot, side in LABELS:
    s = pcbnew.PCB_TEXT(b); s.SetText(txt); s.SetLayer(pcbnew.F_SilkS if side == "F" else pcbnew.B_SilkS); s.SetMirrored(side == "B")
    s.SetTextSize(pcbnew.VECTOR2I(MM(1.0), MM(1.0))); s.SetTextThickness(MM(0.15)); s.SetPosition(V(OX + tx, OY - ty))
    if rot: s.SetTextAngle(ANG(rot))
    b.Add(s)
    q = s.GetBoundingBox(); q = (mm(q.GetLeft()) - OX, OY - mm(q.GetBottom()), mm(q.GetRight()) - OX, OY - mm(q.GetTop()))
    sx = max(0.0, W0 + 0.3 - q[0]) - max(0.0, q[2] - (E - 0.3))
    if sx: s.Move(V(sx, 0)); P("  silkscreen name %r moved %.2f mm in X' to keep 0.3 mm to the outline" % (txt, sx))
    if q[3] > N0 - 0.3 or q[1] < S0 + 0.3: P("  silkscreen name %r is %.2f mm inside the north edge (as in the mock)" % (txt, N0 - q[3]))
for ref in ("J21", "J22") + REPLACE: NEW[ref].Reference().SetVisible(False)      # functional names instead (Nick, mock N / P)

# ------------------------------------------------------------------ reports
P("J21 / J22 pads (pad, N6 signal per n6_pinmap.py, net on the pad, X', y):")
for h in ("J21", "J22"):
    for p in sorted(NEW[h].Pads(), key=lambda p: int(p.GetNumber())):
        sig, want = HEADERS[h][int(p.GetNumber())]; x, y = XY(p.GetPosition())
        got = p.GetNetname(); okn = (got.startswith("unconnected-(") if want is None else got in (want, "/Top-Level Schematic/" + want))
        P("  PAD %s %2s %-8s %-28s %6.2f %6.2f %s %s" % (h, p.GetNumber(), sig, got.split("/")[-1], x, y, NEW[h].GetLayerName(), "ok" if okn else "NET MISMATCH"))
P("where our parts are (reference, face, X', y, turn, note):")
for ref, f in sorted(final.items(), key=lambda kv: [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", kv[0])]):
    if f.m_Uuid.AsString() in coreset: continue
    x, y = XY(f.GetPosition()); why = [w for w in WHERE if w[0] == ref]
    P("  PART %-5s %-3s %7.2f %7.2f %6.1f  %s" % (ref, "N6" if f.IsFlipped() else "top", x, y, f.GetOrientationDegrees(), why[0][1] if why else "mock P position" if ref not in ("R9", "R43") else "as on the Pi board relative to the block"))
for w in WHERE: P("  SPOT", w[2], "|", w[1])
# courtyard overlaps and edge distance, all footprints of the result
fl = list(final.values()); n_ov = 0
for i, a in enumerate(fl):
    for c2 in fl[i + 1:]:
        if a.GetLayer() == c2.GetLayer() and hit(box(a), box(c2)) and not (a.m_Uuid.AsString() in coreset and c2.m_Uuid.AsString() in coreset):
            n_ov += 1; old = tuple(sorted((a.GetReference(), c2.GetReference()))) in INHERITED
            P("  %s: %s / %s" % ("courtyard boxes overlap as on the starting board (same rigid group)" if old else "COURTYARD BOXES OVERLAP (same face)", a.GetReference(), c2.GetReference()))
for f in fl:
    if not inside(box(f), 0.5) and f.GetReference() not in HOLES: P("  courtyard box under 0.5 mm from the edge: %s %s" % (f.GetReference(), [round(v, 2) for v in box(f)]))
    for p in f.Pads():
        if f.m_Uuid.AsString() not in coreset and not inside(padbox(p), 0.5) and f.GetReference() not in HOLES: P("  PAD under 0.5 mm from the edge: %s.%s" % (f.GetReference(), p.GetNumber()))
for z in corez:
    q = z.Outline().BBox(); q = (mm(q.GetLeft()) - OX, OY - mm(q.GetBottom()), mm(q.GetRight()) - OX, OY - mm(q.GetTop()))
    out = not (q[0] >= W0 and q[2] <= E and q[1] >= S0 and q[3] <= N0); over = sum(1 for hp in HEADPADS if hit(q, hp))
    if (out or over) and (not z.GetIsRuleArea() or z.GetZoneName()):
        P("  ZONE of Sofar's %r net %r on %s: box X' %.2f..%.2f, y %.2f..%.2f%s%s" % (z.GetZoneName(), z.GetNetname().split("/")[-1], ",".join(b.GetLayerName(l) for l in z.GetLayerSet().Seq()),
          q[0], q[2], q[1], q[3], "; reaches outside the outline" if out else "", "; its box covers %d header pads" % over if over else ""))
ra = [z for z in corez if z.GetIsRuleArea() and not z.GetZoneName()]
def zq(z):
    q = z.Outline().BBox(); return (mm(q.GetLeft()) - OX, OY - mm(q.GetBottom()), mm(q.GetRight()) - OX, OY - mm(q.GetTop()))
P("  unnamed rule areas of Sofar's: %d; of these %d reach outside the outline and %d have a box over a header pad" % (
    len(ra), sum(1 for z in ra if not (zq(z)[0] >= W0 and zq(z)[2] <= E and zq(z)[1] >= S0 and zq(z)[3] <= N0)), sum(1 for z in ra if any(hit(zq(z), hp) for hp in HEADPADS))))
dead = sorted({t.GetNetname() for t in coretr if t.GetNetname() and t.GetNetname() not in NETS})
P("nets that stay on the board only because Sofar's copper carries them (no pad left): %s" % [(n.split("/")[-1], sum(1 for t in coretr if t.GetNetname() == n)) for n in dead])

# ------------------------------------------------------------------ removals last, then save
ngone = sorted(f.GetReference() for f in gone)
for g0 in groups:
    g0.RemoveAll()
used = {p.GetNetCode() for f in final.values() for p in f.Pads()} | {t.GetNetCode() for t in coretr + newtr} | {z.GetNetCode() for z in corez}
deadnets = [n for n in b.GetNetsByNetcode().values() if n.GetNetCode() > 0 and n.GetNetCode() not in used]
deadnames = sorted(n.GetNetname().split("/")[-1] for n in deadnets)
for o in groups + gone + othertr + ourz + olddraw: b.Remove(o)
for n in deadnets: b.Remove(n)
P("nets removed from the board (%d): %s" % (len(deadnames), " ".join(deadnames)))
P("removed: %d footprints (%s); %d tracks and vias of ours; %d zones of ours; %d drawings of ours; %d groups" % (len(ngone), " ".join(ngone), len(othertr), len(ourz), len(olddraw), len(groups)))
pcbnew.SaveBoard(path, b); P("saved", path)
