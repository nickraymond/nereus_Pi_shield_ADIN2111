"""Stage 7 silkscreen proposal, for a SCRATCH COPY of the board folder (never the committed board).
Usage: <KiCad python> silk.py <scratch board.kicad_pcb> <mote board.kicad_pcb> <frozen board.kicad_pcb> <report.json>

Rules (Nick's style, DESIGN D39 of the frozen board; review of the stage-4 proposal):
  font      Menlo Bold (slashed zero). pcbnew's Python cannot set a face: it is written into the saved file's font blocks afterwards.
  sizes     function names 1.5 x 1.1 mm where there is room, down to 1.0 x 0.7; pad-row, LED and polarity labels 1.0 mm high (JLC's minimum,
            docs/design-review/jlc_rules_2026-11.md line 24; line width 0.15 mm, line 25; pad to silkscreen 0.15 mm, line 23);
            designators, pin names, test-point names and jumper end marks 0.8 x 0.75 / 0.7 mm: the frozen board's designator size (D39 (4)),
            under JLC's 1.0 mm.
  locked    the 81 footprints that sit where Sofar's mote has them are not touched (no text moved, resized or hidden).
  obstacles for a text's INK (measured on the frozen board's Menlo outlines: 1.06 x height, from 0.63 h above the anchor to 0.44 h below;
            width 0.842 x size-x per character less 0.16 x size-x): pads and mask openings + 0.15 mm, via holes + 0.1 mm (every via,
            tented or not), part bodies (pads, silkscreen and fab outlines) + 0.1 mm, mounting-hole courtyards, fiducial openings, 0.5 mm
            from the outline. For a text's KiCad BOX (1.633 x height, 0.842 x size-x per character; kicad-cli's silk_overlap works on it):
            every other silkscreen text.
New-frame mm (board - (113.47, 89.34)).
"""
import sys, os, re, json, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage3_routing'))
import s3lib, pcbnew
from s3lib import V, N, mm, IU, sn
PATH, MOTE, FROZEN, REPORT = sys.argv[1:5]
DH, DW = 0.8, 0.75                    # designators (frozen board: 0.8 x 0.75, read from its Reference texts below)
PH, PW = 0.8, 0.7                     # pin names, test-point names, end marks
DBG = os.environ.get('DBG', '').split(',')
mp = {f.GetReference(): (f.GetPosition().x, f.GetPosition().y) for f in pcbnew.LoadBoard(MOTE).GetFootprints()}
fz = pcbnew.LoadBoard(FROZEN); F, B = pcbnew.F_SilkS, pcbnew.B_SilkS
fzf = {f.GetReference(): f for f in fz.GetFootprints()}
import collections
print('frozen board designator sizes (h x w, visible):', dict(collections.Counter((mm(f.Reference().GetTextSize().y), mm(f.Reference().GetTextSize().x)) for f in fz.GetFootprints() if f.Reference().IsVisible())))
fzt = {}
for d in fz.GetDrawings():
    if d.GetClass() == 'PCB_TEXT' and d.GetLayer() in (F, B): fzt.setdefault((d.GetText(), d.GetLayer()), []).append(d)
def frozen_off(text, ref, layer=F, pick=0):
    """offset of a frozen-board text from a frozen-board footprint, and its size (h, w)"""
    d = sorted(fzt[(text, layer)], key=lambda d: abs(d.GetPosition().x - fzf[ref].GetPosition().x) + abs(d.GetPosition().y - fzf[ref].GetPosition().y))[pick]
    return (mm(d.GetPosition().x - fzf[ref].GetPosition().x), mm(d.GetPosition().y - fzf[ref].GetPosition().y), mm(d.GetTextSize().y), mm(d.GetTextSize().x))
b = pcbnew.LoadBoard(PATH)
fps = {f.GetReference(): f for f in b.GetFootprints()}
du = (fps['U1'].GetPosition().x - mp['U1'][0], fps['U1'].GetPosition().y - mp['U1'][1])
locked = {r for r, f in fps.items() if r in mp and abs(f.GetPosition().x - mp[r][0] - du[0]) < 1000 and abs(f.GetPosition().y - mp[r][1] - du[1]) < 1000}
print('locked (Sofar) footprints: %d; ours: %d' % (len(locked), len(fps) - len(locked)))
ds = b.GetDesignSettings(); vias = [t for t in b.GetTracks() if t.GetClass() == 'PCB_VIA']
TM = {pcbnew.TENTING_MODE_FROM_BOARD: 'from board', pcbnew.TENTING_MODE_TENTED: 'tented', pcbnew.TENTING_MODE_NOT_TENTED: 'not tented'}
tent = dict(collections.Counter((TM[v.GetFrontTentingMode()], TM[v.GetBackTentingMode()]) for v in vias))
print('via tenting: board setup front %s back %s; %d vias, per-via (front, back): %s' % (ds.m_TentViasFront, ds.m_TentViasBack, len(vias), tent))
side_of = lambda f: B if f.IsFlipped() else F
rect = lambda bb, g=0.0: (mm(bb.GetLeft()) - 113.47 - g, mm(bb.GetTop()) - 89.34 - g, mm(bb.GetRight()) - 113.47 + g, mm(bb.GetBottom()) - 89.34 + g)
hit = lambda a, c: not (a[2] <= c[0] or c[2] <= a[0] or a[3] <= c[1] or c[3] <= a[1])
def union(rs): return (min(r[0] for r in rs), min(r[1] for r in rs), max(r[2] for r in rs), max(r[3] for r in rs))
# text against text by ink + 0.17 mm (kicad-cli measures the glyphs against the silk clearance, 0.15 mm); INKTT=0: by KiCad box
INKTT = os.environ.get('INKTT', '1') == '1'; TINK = {F: [], B: []}; PADS = {F: [], B: []}; SILKG = {F: [], B: []}; LINE = {F: [], B: []}; DBGN = collections.Counter(); WHY = collections.Counter(); BODY = {F: [], B: []}; CIRC = {F: [], B: []}; TEXT = {F: [], B: []}; body_of = {}
MASK = {F: pcbnew.F_Mask, B: pcbnew.B_Mask}; FAB = {F: pcbnew.F_Fab, B: pcbnew.B_Fab}
PADS_ONLY = lambda r: r in ('J1', 'J4', 'J5', 'J15', 'J16', 'J17', 'J18', 'J19') or r.startswith(('TP', 'FID', 'H'))
for r, f in fps.items():
    side = side_of(f); mine_b = []
    for p in f.Pads():
        th = p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH)
        for s in ((F, B) if th else (side,)): PADS[s].append(rect(p.GetBoundingBox(), 0.15))
        mine_b.append(rect(p.GetBoundingBox()))
    for g in f.GraphicalItems():
        if g.GetClass() != 'PCB_SHAPE': continue
        for s in (F, B):
            if g.GetLayer() == MASK[s]: PADS[s].append(rect(g.GetBoundingBox(), 0.15))
        if g.GetLayer() in (F, B): SILKG[g.GetLayer()].append(rect(g.GetBoundingBox(), 0.02))
        if g.GetLayer() in (side, FAB[side]) or b.GetLayerName(g.GetLayer()) == 'Mechanical 12': mine_b.append(rect(g.GetBoundingBox()))
    if r == 'J1': BODY[B].append((6.98, 0.84, 58.02, 6.16)); body_of[r] = (B, (6.98, 0.84, 58.02, 6.16))       # the header's outline on the bottom
    elif r.startswith('H') and r[1:].isdigit():            # mounting holes: the footprint's courtyard circle (screw head / stand-off), both sides
        x, y = N(f.GetPosition()); rr = mm(f.GetBoundingBox(False).GetWidth()) / 2 + 0.1; CIRC[F].append((x, y, rr)); CIRC[B].append((x, y, rr))
    elif r.startswith('FID'): x, y = N(f.GetPosition()); CIRC[side].append((x, y, 1.1))          # fiducial: its 2 mm mask opening + 0.1
    elif not PADS_ONLY(r): u = union(mine_b); BODY[side].append((u[0] - .1, u[1] - .1, u[2] + .1, u[3] + .1)); body_of[r] = (side, u)
    if r in locked:
        for t in [f.Reference(), f.Value()] + [g for g in f.GraphicalItems() if g.GetClass() == 'PCB_TEXT']:
            if t.IsVisible() and t.GetLayer() in (F, B): TEXT[t.GetLayer()].append(rect(t.GetBoundingBox(), 0.2))       # Sofar's texts: 0.2 mm round their box, so that ours do not run on from them
HOLE = [(N(v.GetPosition())[0], N(v.GetPosition())[1], mm(v.GetDrill()) / 2 + 0.1) for v in vias]
for d in b.GetDrawings():
    if d.GetLayer() in (F, B): TEXT[d.GetLayer()].append(rect(d.GetBoundingBox(), 0.1))
BOT = [False]          # set by free(): on the bottom (mirrored) a turned text's ink is taken symmetric
def boxes(s, x, y, h, w, ang=0):
    """(ink box, KiCad box) of a centred Menlo Bold text"""
    L = 0.842 * w * len(s); li = L - 0.16 * w
    if ang == 0: return (x - li / 2, y - 0.63 * h, x + li / 2, y + 0.44 * h), (x - L / 2 - .03, y - 0.8165 * h - .03, x + L / 2 + .03, y + 0.8165 * h + .03)
    wl, wr = (0.63, 0.44) if ang == 90 and not BOT[0] else (0.44, 0.63) if ang == 270 and not BOT[0] else (0.63, 0.63)
    return (x - wl * h, y - li / 2, x + wr * h, y + li / 2), (x - 0.8165 * h - .03, y - L / 2 - .03, x + 0.8165 * h + .03, y + L / 2 + .03)
def cdist(r, cx, cy): return math.hypot(max(r[0] - cx, 0, cx - r[2]), max(r[1] - cy, 0, cy - r[3]))
def free(side, x, y, s, h, w, ang=0, hole_r=None, own=None, relax=()):
    """None if blocked, else (ink, box). own: this footprint's body is no obstacle. relax: obstacle classes to skip ('via', 'body')."""
    BOT[0] = side == B; ink, bx = boxes(s, x, y, h, w, ang); BOT[0] = False; blk = []
    if min(s3lib.edge_margin(q) for q in ((ink[0], ink[1]), (ink[2], ink[1]), (ink[0], ink[3]), (ink[2], ink[3]))) < 0.5: blk.append('edge')
    blk += [('pad', o) for o in PADS[side] if hit(ink, o)]
    if 'body' not in relax: blk += [('body', o) for o in BODY[side] if hit(ink, o) and not (own and body_of.get(own) and body_of[own][0] == side and all(abs(a - c) < 0.11 for a, c in zip(o, body_of[own][1])))]
    blk += [('text', o) for o in TEXT[side] if hit(bx, o)] + [('text', o) for o in TINK[side] if hit(ink, o)] + [('line', o) for o in LINE[side] if hit(ink, o)] + [('silk', o) for o in SILKG[side] if hit((ink[0] - .14, ink[1] - .14, ink[2] + .14, ink[3] + .14), o)]
    if 'via' not in relax: blk += [('via', o) for o in HOLE if cdist(ink, o[0], o[1]) < o[2]]
    for cx, cy, cr in CIRC[side]:
        rr = hole_r if (hole_r and cr > 2) else cr
        if cdist(ink, cx, cy) < rr: blk.append(('circle', (cx, cy, rr)))
    DBGN[s] += 1
    for k in blk: WHY[k if isinstance(k, str) else k[0]] += 1
    if blk and s in DBG and DBGN[s] < int(os.environ.get('DBGMAX', '6')): print('   DBG %s (%.2f, %.2f) h%.1f a%d blocked by' % (s, x, y, h, ang), [(k if isinstance(k, str) else (k[0], tuple(round(v, 2) for v in k[1]))) for k in blk][:4])
    return None if blk else (ink, bx)
def addtext(side, s, x, y, h, w, ang):
    BOT[0] = side == B; ink, bx = boxes(s, x, y, h, w, ang); BOT[0] = False
    if INKTT: TINK[side].append((ink[0] - .17, ink[1] - .17, ink[2] + .17, ink[3] + .17))
    else: TEXT[side].append(bx)
mine = []; done = []; skipped = []; netrows = []
def style(t, h, w, ang, side):
    t.SetTextSize(pcbnew.VECTOR2I(IU(w), IU(h))); t.SetTextThickness(IU(0.15)); t.SetTextAngleDegrees(ang)
    t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER); t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER); t.SetMirrored(side == B); t.SetLayer(side); t.SetVisible(True)
def netcheck(what, s, chk):
    """chk: (ref, pad number, regex the pad's net must match). Every function / pin / net label goes through here."""
    if not chk: return
    ref, n, rx = chk; nets = sorted({sn(p.GetNetname()) for p in fps[ref].Pads() if p.GetNumber() in str(n).split('+')})
    ok = bool(nets) and all(re.fullmatch(rx, x) for x in nets); netrows.append((what, s, '%s pad %s' % (ref, n), ' / '.join(nets), 'OK' if ok else 'MISMATCH'))
    assert ok, (what, s, chk, nets)
def place(what, s, x, y, h, w, ang, side):
    t = pcbnew.PCB_TEXT(b); t.SetText(s); t.SetPosition(V(x, y)); style(t, h, w, ang, side); b.Add(t)
    mine.append(t.m_Uuid.AsString()); addtext(side, s, x, y, h, w, ang); done.append((what, s, round(x, 2), round(y, 2), h, w, ang, 'top' if side == F else 'bottom'))
def put(what, s, cands, sizes=((1.0, 0.75),), ang=0, side=F, chk=None, **kw):
    """first clear candidate at the first size that has one"""
    netcheck(what, s, chk)
    for h, w in sizes:
        for x, y in cands:
            if free(side, x, y, s, h, w, ang, **kw): place(what, s, x, y, h, w, ang, side); return (x, y, h, w)
    skipped.append('%s "%s" (%s)' % (what, s, 'top' if side == F else 'bottom')); return None
def seg(a, c, side, wd=0.2):
    g = pcbnew.PCB_SHAPE(b); g.SetShape(pcbnew.SHAPE_T_SEGMENT); g.SetStart(V(*a)); g.SetEnd(V(*c)); g.SetWidth(IU(wd)); g.SetLayer(side); b.Add(g)
    LINE[side].append((min(a[0], c[0]) - .2, min(a[1], c[1]) - .2, max(a[0], c[0]) + .2, max(a[1], c[1]) + .2))
def box(x0, y0, x1, y1, side):
    for a, c in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))): seg(a, c, side)
pad = lambda ref, n: N([p for p in fps[ref].Pads() if p.GetNumber() == n][0].GetPosition())
padbb = lambda ref, n: rect([p for p in fps[ref].Pads() if p.GetNumber() == n][0].GetBoundingBox())
grid = lambda x, y, dxs, dys: [(x + dx, y + dy) for dy in dys for dx in dxs]
SW = lambda k, st=0.1: [0] + [sg * i * st for i in range(1, k + 1) for sg in (1, -1)]           # 0, +st, -st, +2 st, ...

# ---- 0. our own footprints: old texts off (J4's '+' / 'GND' footprint texts, U12's '*' on TP40's pad); designators re-placed in section 9
kill = []; mine_ref = set()
for r, f in fps.items():
    if r in locked: continue
    for g in f.GraphicalItems():
        if g.GetLayer() in (F, B) and g.GetClass() == 'PCB_TEXT' and r in ('J4', 'J5', 'U12'): kill.append((f, g, g.GetText(), N(g.GetPosition())))
    f.Reference().SetVisible(False)
    if f.Value().GetLayer() in (F, B): f.Value().SetVisible(False)
for f, g, s_, p_ in kill: f.Remove(g)
print('removed footprint texts:', [(f.GetReference(), s_, p_) for f, g, s_, p_ in kill])
j4box = union([rect(g.GetBoundingBox()) for g in fps['J4'].GraphicalItems() if g.GetLayer() == F and g.GetClass() == 'PCB_SHAPE']); print('J4 box (footprint, top): %s' % (tuple(round(v, 2) for v in j4box),))

# ---- 1. LEDs, copied from the frozen board: same texts, same offsets from the same LEDs, same size. Which LED is which port: by net, and the
#         port's way to its connector is traced in netcheck.py (U1 pin names -> transformer -> BM connector).
for r, s_, rx in (('D8', 'ADIN', r'GND|Net-\(D8-A\)'), ('D10', 'BM2', r'~\{ADIN_P2_LED1\}|Net-\(D10-A\)'), ('D8', 'PWR', r'GND|Net-\(D8-A\)'), ('D9', 'BM1', r'~\{ADIN_P1_LED1\}|Net-\(D9-A\)')):
    fr = {'D10': 'D10', 'D8': 'D8', 'D9': 'D9'}[r]; frz = {'BM2': 'D10', 'BM1': 'D9'}.get(s_, 'D8')
    ox, oy, h, w = frozen_off(s_, frz); x, y = N(fps[r].GetPosition())
    # the frozen board's port names follow its own LED nets; here the name follows THIS board's net at the LED, so check the frozen LED too
    print('LED label "%s": frozen offset (%.2f, %.2f) from %s, size %.1f x %.1f; frozen %s nets %s' % (s_, ox, oy, frz, h, w, frz, sorted(sn(p.GetNetname()) for p in fzf[frz].Pads())))
    got = put('LED ' + r, s_, [(x + ox, y + oy + sg * d) for d in (0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3) for sg in ((1,) if oy > 0 else (-1,))], ((h, w),), chk=(r, '1+2', rx))
    print('   placed at offset (%.2f, %.2f)' % (got[0] - x, got[1] - y) if got else '   LED label blocked')
for r in ('D8', 'D9', 'D10'):                 # LED designators: where the frozen board has them (same offsets), frozen size
    t = fps[r].Reference(); ft = fzf[r].Reference(); x, y = N(fps[r].GetPosition())
    ox, oy = mm(ft.GetPosition().x - fzf[r].GetPosition().x), mm(ft.GetPosition().y - fzf[r].GetPosition().y); ang = ft.GetTextAngleDegrees()
    t.SetPosition(V(x + ox, y + oy)); style(t, DH, DW, ang, F); mine.append(t.m_Uuid.AsString()); addtext(F, r, x + ox, y + oy, DH, DW, ang); mine_ref.add(r)

# ---- 2. south-wall connectors: function name large, designator small centred under it, pin names tiny just north of the pads
def conn(ref, name, pins, rx, name_dx=SW(12), des_alt=(), PH=PH, PW=PW, pin_dx=(0, 0.1, -0.1, 0.2, -0.2, 0.3, -0.3, 0.45, -0.45, 0.6, -0.6), name_at=None, name_sizes=((1.5, 1.1), (1.3, 1.0), (1.15, 0.9), (1.0, 0.75))):
    """pins: [(text, pad numbers 'a+b', regex, angle)]"""
    f = fps[ref]; top = body_of[ref][1][1]; xs = [pad(ref, p.GetNumber())[0] for p in f.Pads() if p.GetNumber().isdigit()]; cx = (min(xs) + max(xs)) / 2
    yp = top - 0.12 - 0.44 * PH; rowtop = yp - 0.8165 * PH - 0.06; ok_pins = 0
    for s_, nums, prx, ang in pins:
        px = sum(pad(ref, n)[0] for n in nums.split('+')) / len(nums.split('+'))
        if ang == 0: c = [(px + dx, yp - dy) for dy in (0, 0.1, 0.2, 0.3, 0.4) for dx in pin_dx]
        else:                  # turned names: the whole row at one height, the lowest at which every name is clear
            L = 0.842 * PW * len(s_); pxs = [sum(pad(ref, n)[0] for n in q[1].split('+')) / len(q[1].split('+')) for q in pins]
            dyc = next((dy for dy in (0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2) if all(any(free(F, qx + dx, top - 0.1 - L / 2 - dy, q[0], PH, PW, 90, own=ref) for dx in pin_dx) for q, qx in zip(pins, pxs))), 0)
            c = [(px + dx, top - 0.1 - L / 2 - dyc) for dx in pin_dx]; rowtop = min(rowtop, top - 0.1 - L - dyc - 0.2)
        if put(ref + ' pin name', s_, c, ((PH, PW),), ang=ang, chk=(ref, nums, prx), own=ref): ok_pins += 1
    yd = rowtop - 0.8165 * DH
    if name_at:            # explicit places: (name places, designator offset from the name)
        netcheck(ref + ' function', name, (ref, '+'.join(sorted({p.GetNumber() for p in f.Pads() if p.GetNumber().isdigit()})), rx))
        for h, w in name_sizes:
            for x, y in name_at[0]:
                for ddx, ddy in name_at[1]:
                    if free(F, x, y, name, h, w) and free(F, x + ddx, y + ddy, ref, DH, DW):
                        place(ref + ' function', name, x, y, h, w, 0, F); place(ref + ' designator', ref, x + ddx, y + ddy, DH, DW, 0, F); mine_ref.add(ref); return
        skipped.append('%s function "%s"' % (ref, name)); return
    for h, w in name_sizes:                       # name over designator, same centre line
        yn = yd - 0.8165 * DH - 0.8165 * h - 0.08
        for dy in (0, 0.15, 0.3, 0.5, 0.8, 1.2):
            for dx in name_dx:
                if free(F, cx + dx, yn - dy, name, h, w) and free(F, cx + dx, yd - dy, ref, DH, DW):
                    netcheck(ref + ' function', name, (ref, '+'.join(sorted({p.GetNumber() for p in f.Pads() if p.GetNumber().isdigit()})), rx))
                    place(ref + ' function', name, cx + dx, yn - dy, h, w, 0, F); place(ref + ' designator', ref, cx + dx, yd - dy, DH, DW, 0, F); mine_ref.add(ref); return
    # no room for the pair: the name alone, the designator at one of the alternative places
    netcheck(ref + ' function', name, (ref, '+'.join(sorted({p.GetNumber() for p in f.Pads() if p.GetNumber().isdigit()})), rx))
    got = None
    for h, w in name_sizes:
        for dy in (0, 0.15, 0.3, 0.5, 0.8, 1.2, 1.6):
            for dx in name_dx:
                if not got and free(F, cx + dx, rowtop - 0.8165 * h - 0.05 - dy, name, h, w): got = (cx + dx, rowtop - 0.8165 * h - 0.05 - dy, h, w)
    if got: place(ref + ' function (designator not under it: no room)', name, got[0], got[1], got[2], got[3], 0, F)
    else: skipped.append('%s function "%s"' % (ref, name))
    for x, y, ang in des_alt:
        if free(F, x, y, ref, DH, DW, ang, own=ref): place(ref + ' designator', ref, x, y, DH, DW, ang, F); mine_ref.add(ref); return
# J7: six tented vias stand where the large name would go (y 28.25 .. 32.0): MOTOR at 1.0 mm between the via rows, J7 beside it in the same row
conn('J7', 'MOTOR', [('O1', '1+2', 'MOTOR_OUT1', 0), ('O2', '3+4', 'MOTOR_OUT2', 0)], 'MOTOR_OUT[12]', des_alt=[(9.0 + dx, 31.14 + dy, 0) for dy in (0, -0.1, 0.1, -0.2) for dx in (0, 0.1, -0.1, 0.2, 0.3)])
conn('J9', 'BM2', [('N', '1+2', 'BM2_N', 0), ('P', '3+4', 'BM2_P', 0)], 'BM2_[NP]')
conn('J10', 'BM1', [('N', '1+2', 'BM1_N', 0), ('P', '3+4', 'BM1_P', 0)], 'BM1_[NP]')
# J8: 1.25 mm pitch, three different nets, and six tented vias north of it ((23.59, 31.98), (26.69, 32.6) right north of pin 3, (27.73, 31.41), ...):
# names turned 90 over each pin do not clear the via holes. One row in pin order at 0.7 mm: 3V3 west of pin 1, WIP over pin 2, GND east of pin 3.
t8 = body_of['J8'][1][1]; yr8 = t8 - 0.15 - 0.31
for s_, n, rx, x0 in (('3V3', '1', '3V3', 23.5), ('WIP', '2', 'POT_WIPER', pad('J8', '2')[0]), ('GND', '3', 'GND', 27.8)):
    put('J8 pin name (row in pin order)', s_, grid(x0, yr8, (0, 0.05, -0.05, 0.1, -0.1), (0, -0.05, -0.1)), ((0.7, 0.7),), chk=('J8', n, rx), own='J8')
put('J8 function', 'POT', grid(25.9, 31.15, (0, 0.1, -0.1, 0.2), (0, -0.05, 0.05, -0.1, -0.15)), ((1.15, 0.9), (1.0, 0.75)), chk=('J8', '1+2+3', '3V3|POT_WIPER|GND'))
for x, y in grid(21.45, 32.6, (0, -0.1, 0.1, 0.2, 0.3), (0, 0.05, -0.1, -0.2)):           # the designator: no clear place under or beside the name; at the connector's west corner
    if free(F, x, y, 'J8', DH, DW, own='J8'): place('J8 designator (not under the name: no room)', 'J8', x, y, DH, DW, 0, F); mine_ref.add('J8'); break
# J3: 1.0 mm pitch. Full names do not fit (turned 90 they reach T1's designator); one letter per pin: G GND, 3 PI_3V3, D I2C3_SDA, C I2C3_SCL
conn('J3', 'QWIIC', [('G', '1', 'GND', 0), ('3', '2', 'PI_3V3', 0), ('D', '3', 'I2C3_SDA', 0), ('C', '4', 'I2C3_SCL', 0)], 'GND|PI_3V3|I2C3_SD[AL]|I2C3_SCL',
     name_sizes=((1.3, 0.8), (1.15, 0.8), (1.0, 0.75)), name_at=(grid(49.2, 31.9, SW(4, 0.05), (-0.3, -0.25, -0.2, -0.35, -0.4, -0.1, 0, -0.5, -0.7)), grid(0.7, 2.15, (0, -0.1, 0.1, -0.2, 0.2, -0.4, -0.7), (0, 0.1, -0.1, -0.2, -0.3, 0.2))))

# ---- 3. power outputs: boxed on both sides, name, designator under the name, '+' / 'GND' at the pads on both sides
print('J4 pads:', {n: (pad('J4', n), sn([q for q in fps['J4'].Pads() if q.GetNumber() == n][0].GetNetname())) for n in '12'}, ' F1:', {p.GetNumber(): sn(p.GetNetname()) for p in fps['F1'].Pads()})
jb = union([padbb('J4', '1'), padbb('J4', '2')]); jb4 = (jb[0] - 0.35, jb[1] - 0.3, jb[2] + 0.35, jb[3] + 0.3); box(*jb4, side=B)      # the top box is in the footprint
for g in fps['J4'].GraphicalItems():
    if g.GetLayer() == F and g.GetClass() == 'PCB_SHAPE': LINE[F].append(rect(g.GetBoundingBox(), 0.35))
for side in (F, B):
    yb = max(j4box[3], jb4[3]) + 0.25
    # between J4 and the H4 screw: checked against the hole + 0.5 mm (r 1.85), not H4's courtyard (r 2.6): a screw head or stand-off can cover them
    put('J4 polarity', '+', grid(pad('J4', '1')[0], yb + 0.63, SW(6), (0, 0.1, 0.2)), ((1.0, 1.0), (0.8, 0.8)), side=side, chk=('J4', '1', r'Net-\(J4-Pin_1\)'), hole_r=1.85)
    put('J4 polarity', 'GND', grid(pad('J4', '2')[0], yb + 0.63, [0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4], (0, 0.1, 0.2)), ((1.0, 0.75), (0.8, 0.7)), side=side, chk=('J4', '2', 'GND'), hole_r=1.85)
for h, w in ((1.3, 0.9), (1.15, 0.85), (1.0, 0.75)):
    ok = False
    for x, y in grid(8.95, 21.3, SW(6), (0, 0.2, 0.4, -0.2, 0.6, 0.8, 1.0)):
        yd = y + 0.8165 * h + 0.8165 * DH + 0.08
        if free(F, x, y, '5V AUX', h, w) and free(F, x, yd, 'J4', DH, DW):
            netcheck('J4 function', '5V AUX', ('F1', '1+2', r'5V_LIFEPO4|Net-\(J4-Pin_1\)')); place('J4 function', '5V AUX', x, y, h, w, 0, F); place('J4 designator', 'J4', x, yd, DH, DW, 0, F); mine_ref.add('J4'); ok = True; break
    if ok: break
else: skipped.append('J4 function "5V AUX" (top)')
put('J4 function', '5V AUX', grid(9.0, 19.6, SW(8), (0, 0.2, -0.2, 0.4, -0.4, -0.6)), ((1.0, 0.75),), side=B)
j5 = union([padbb('J5', '1'), padbb('J5', '2')]); bx5 = (j5[0] - 0.35, j5[1] - 0.3, j5[2] + 0.35, j5[3] + 0.3)
print('J5 pads:', {n: (pad('J5', n), sn([q for q in fps['J5'].Pads() if q.GetNumber() == n][0].GetNetname())) for n in '12'}, ' box', tuple(round(v, 2) for v in bx5))
for side in (F, B):
    box(*bx5, side=side)
    put('J5 polarity', '+', grid(bx5[0] - 0.75, pad('J5', '1')[1], (0, -0.1, -0.2, -0.3), SW(5)), ((1.0, 1.0), (0.8, 0.8)), side=side, chk=('J5', '1', 'VBUS_OUT'))
    g_ = put('J5 polarity', 'GND', grid(61.9, bx5[3] + 0.3 + 0.63, SW(4), (0, 0.1, 0.2, 0.3)), ((1.0, 0.75),), side=side, chk=('J5', '2', 'GND'))
    y0 = (g_[1] if g_ else bx5[3]) + 0.8165 + 0.1
    for h, w in ((1.3, 0.7), (1.15, 0.7), (1.0, 0.68)):
        ok = False
        for x, y in grid(61.9, y0 + 0.8165 * h, SW(3), (0, 0.15, 0.3, 0.5, 0.8)):
            yd = y + 0.8165 * h + 0.8165 * DH + 0.08
            if free(side, x, y, 'VBUS OUT', h, w) and (side == B or free(F, x, yd, 'J5', DH, DW)):
                netcheck('J5 function', 'VBUS OUT', ('J5', '1', 'VBUS_OUT')); place('J5 function', 'VBUS OUT', x, y, h, w, 0, side)
                if side == F: place('J5 designator', 'J5', x, yd, DH, DW, 0, F); mine_ref.add('J5')
                ok = True; break
        if ok: break
    else: skipped.append('J5 function "VBUS OUT" (%s)' % ('top' if side == F else 'bottom'))

# ---- 4. the pad row under J1: every pad named on the top and on the bottom; row title
ROW = [('J15', '1', '5V', 'PI_5V'), ('J15', '2', 'GND', 'GND'), ('J15', '3', '14', 'GPIO14'), ('J15', '4', '15', 'GPIO15'), ('J16', '1', '3V3', 'PI_3V3'), ('J16', '2', '3V3', 'PI_3V3'),
       ('J17', '1', 'GND', 'GND'), ('J17', '2', '17', 'GPIO17'), ('J18', '1', '18', 'GPIO18'), ('J18', '2', '7', 'GPIO7'), ('J18', '3', 'GND', 'GND'), ('J18', '4', 'GND', 'GND'),
       ('J19', '1', '19', 'GPIO19'), ('J19', '2', '20', 'GPIO20'), ('J19', '3', '21', 'GPIO21')]
rowres = {}
for side in (F, B):
    for ref, n, s_, rx in ROW:
        x, y = pad(ref, n); yb = padbb(ref, n)[3] + 0.15
        c = [(x + dx, yb + 0.63 * 1.0 + dy) for dy in (0, 0.1, 0.2, 0.3, 0.45, 0.6, 0.8, 1.0, 1.2) for dx in (0, 0.15, -0.15, 0.3, -0.3, 0.45, -0.45, 0.6, -0.6)]
        rowres[(ref, n, side)] = put('%s pad %s' % (ref, n), s_, c, ((1.0, 0.75), (0.8, 0.7)), side=side, chk=(ref, n, rx))
    yr = [v[1] for k, v in rowres.items() if k[2] == side and v and k[1:] in (('4', side), ('1', side)) and k[0] in ('J15', 'J16')]
    put('pad row title', 'GPIO', [(22.34, 6.7), (22.34, 6.8), (22.34, 6.6), (22.2, 6.7), (22.5, 6.7)] + [(x0 + dx, y + dy) for y in yr[:1] for x0 in (22.34,) for dy in (0, 0.2, 0.4) for dx in SW(4)], ((1.0, 0.75), (0.8, 0.7)), side=side)
mine_ref |= {'J15', 'J16', 'J17', 'J18', 'J19'}       # the pad names stand for the five group designators (hidden on purpose)

# ---- 5. jumpers: the frozen board's function names (read from it), name over designator; 0 / 1 at the strap ends by net
FZN = {}
for jp in ('JP1', 'JP2', 'JP3', 'JP4'):
    best = min(((abs(d.GetPosition().x - fzf[jp].GetPosition().x) + abs(d.GetPosition().y - fzf[jp].GetPosition().y), k[0]) for k, v in fzt.items() for d in v if k[1] == F and d.GetTextSize().y >= IU(1.3)))
    FZN[jp] = best[1]
print('frozen board jumper names (nearest top-side text):', FZN, '; its 0 / 1 marks at JP3:', sorted((round(mm(d.GetPosition().x - fzf['JP3'].GetPosition().x), 2), k[0]) for k, v in fzt.items() for d in v if k[0] in '01' and k[1] == F and abs(d.GetPosition().y - fzf['JP3'].GetPosition().y) < 1e5 and abs(d.GetPosition().x - fzf['JP3'].GetPosition().x) < 4e6),
      'frozen JP3 pads:', {p.GetNumber(): (round(mm(p.GetPosition().x - fzf['JP3'].GetPosition().x), 2), sn(p.GetNetname())) for p in fzf['JP3'].Pads()})
def stack(ref, name, cx, ybot, rx, pads, sizes=((1.5, 1.0), (1.3, 0.95), (1.15, 0.85), (1.0, 0.75)), dxs=SW(8), dys=(0, 0.15, 0.3, 0.5, 0.8, 1.2), below=False):
    """name over designator, the pair above ybot (or, below=True, starting under ybot)"""
    for h, w in sizes:
        for dy in dys:
            for dx in dxs:
                if below: yn = ybot + 0.63 * h + 0.1 + dy; yd = yn + 0.8165 * h + 0.8165 * DH + 0.08
                else: yd = ybot - 0.12 - 0.44 * DH - dy; yn = yd - 0.8165 * DH - 0.8165 * h - 0.08
                if free(B, cx + dx, yn, name, h, w) and free(B, cx + dx, yd, ref, DH, DW):
                    netcheck(ref + ' function', name, (ref, pads, rx)); place(ref + ' function', name, cx + dx, yn, h, w, 0, B); place(ref + ' designator', ref, cx + dx, yd, DH, DW, 0, B); mine_ref.add(ref); return yn - 0.8165 * h
    skipped.append('%s function "%s" (bottom)' % (ref, name)); return None
# JP3 / JP4 end marks first (they are the tightest): 1 = the end on ADIN_VDDIO, 0 = the end on GND (frozen board, D42)
for ref in ('JP3', 'JP4'):
    for p in fps[ref].Pads():
        net = sn(p.GetNetname())
        if net not in ('ADIN_VDDIO', 'GND') or p.GetSize().y > IU(1.0): continue
        x, y = N(p.GetPosition()); outw = x < N(fps[ref].GetPosition())[0]; e = body_of[ref][1][0] if outw else body_of[ref][1][2]; sg = -1 if outw else 1
        if (ref, p.GetNumber()) == ('JP4', '1'): netcheck('JP4 end mark (shared with JP3: both ends on GND)', '0', ('JP4', '1', 'GND')); continue
        if (ref, p.GetNumber()) == ('JP3', '3'): e = (body_of['JP3'][1][2] + body_of['JP4'][1][0]) / 2 - 0.4
        c = [(e + sg * (0.4 + d), y + dy) for d in (0, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7) for dy in (0, 0.2, -0.2, 0.4, 0.6)]
        put('%s end mark' % ref, '1' if net == 'ADIN_VDDIO' else '0', c, ((0.8, 0.65),), side=B, chk=(ref, p.GetNumber(), 'ADIN_VDDIO' if net == 'ADIN_VDDIO' else 'GND'), relax=('body',))
stack('JP2', FZN['JP2'], N(fps['JP2'].GetPosition())[0], body_of['JP2'][1][1], 'ADIN_LED_VDD|ADIN_VDDIO', '1+2')
top3 = stack('JP3', FZN['JP3'], N(fps['JP3'].GetPosition())[0], body_of['JP3'][1][1], 'CFG1_STRAP', '2')
# JP4 has JP2 north of it, JP3 west, R49 / R50 east and the board edge south: its name and designator go on top of JP3's pair, as a second pair
if top3: stack('JP4', FZN['JP4'], N(fps['JP3'].GetPosition())[0], top3 - 0.25, 'CFG0_STRAP', '2')
else: skipped.append('JP4 function')
# JP1: vias at (11.3, 23.05 / 23.9) and C26 leave one place for the name; the designator under it, moved west so that it does not read as C26's
n1 = put('JP1 function', FZN['JP1'], grid(13.35, 23.13, (0, 0.05, 0.1, 0.15, 0.2, 0.3), (0, 0.05, 0.1, -0.05)), ((1.0, 0.7),), side=B, chk=('JP1', '2', '5V_PI'))
for x, y in grid(12.25, (n1[1] if n1 else 23.13) + 0.8165 + 0.8165 * DH + 0.08, (0, 0.05, 0.1, 0.2, 0.3, 0.5), (0, 0.1, -0.1, 0.2)):
    if free(B, x, y, 'JP1', DH, DW): place('JP1 designator', 'JP1', x, y, DH, DW, 0, B); mine_ref.add('JP1'); break
for sg, e in ((-1, body_of['JP1'][1][0]),):          # both end names on JP1's west side (east of it they run into JP1's designator: 'JP1AUX')
    ca = [(e + sg * (0.85 + d), pad('JP1', '1')[1] + dy) for d in (0, 0.1, 0.2, 0.3) for dy in SW(3)]; cb = [(e + sg * (1.15 + d), pad('JP1', '3')[1] + dy) for d in (0, 0.1, 0.2, 0.3) for dy in SW(3)]
    if any(free(B, x, y, 'PI', PH, PW) for x, y in ca) and any(free(B, x, y, 'AUX', PH, PW) for x, y in cb):
        put('JP1 end name', 'PI', ca, ((PH, PW),), side=B, chk=('JP1', '1', 'PI_5V')); put('JP1 end name (5V_LIFEPO4 -> F1 -> J4)', 'AUX', cb, ((PH, PW),), side=B, chk=('JP1', '3', '5V_LIFEPO4')); break
else: skipped.append('JP1 end names "PI" / "AUX" (bottom)')

# ---- 6. U12's pin-1 mark (it sat on TP40's pad): a '*' at pin 1, clear of pads
p1 = pad('U12', '1'); put('U12 pin 1 mark', '*', grid(p1[0] - 0.8, p1[1] - 0.1, (0, 0.05, -0.05, 0.1), (0, -0.1, -0.2, -0.3, -0.5, -0.7, 0.1)), ((0.8, 0.8),), side=B, chk=('U12', '1', 'MOTOR_IN1'), relax=('body',))

# ---- 7. test points: short net name at each (ours replace nothing; Sofar's designators stay where they are)
TPN = {'TP40': ('IN1', 'MOTOR_IN1'), 'TP41': ('OUT1', 'MOTOR_OUT1'), 'TP42': ('OUT2', 'MOTOR_OUT2'), 'TP43': ('SCL0', 'I2C0_SCL'), 'TP1': ('AVDD', 'ADIN_AVDD'), 'TP2': ('VDDIO', 'ADIN_VDDIO'),
       'TP13': ('BM2N', 'BM2_N'), 'TP7': ('BM2P', 'BM2_P'), 'TP5': ('BM1N', 'BM1_N'), 'TP3': ('BM1P', 'BM1_P'), 'TP19': ('PL_EN', 'PAYLOAD_EN'), 'TP35': ('PL_FLT', r'~\{PAYLOAD_FAULT\}'),
       'TP20': ('3V3', '3V3'), 'TP21': ('1V8', '1V8'), 'TP22': ('VBUS', 'VBUS'), 'TP23': ('GND', 'GND'), 'TP24': ('GND', 'GND'), 'TP38': ('5V_PI', '5V_PI'), 'TP8': ('A_PWR', 'ADIN_PWR')}
assert set(TPN) == {r for r in fps if r.startswith('TP')}, sorted({r for r in fps if r.startswith('TP')} ^ set(TPN))
tp_named = {}
for ref in ('TP40', 'TP41', 'TP42', 'TP43') + tuple(sorted(set(TPN) - {'TP40', 'TP41', 'TP42', 'TP43'})):
    s_, rx = TPN[ref]; f = fps[ref]; side = side_of(f); x, y = N(f.GetPosition()); L = 0.842 * PW * len(s_); c = []
    for g in (0, 0.15, 0.3, 0.5):
        c += [(x + sh, y - 0.9 - 0.44 * PH - g) for sh in (0, 0.3, -0.3, 0.6, -0.6)] + [(x + sh, y + 0.9 + 0.63 * PH + g) for sh in (0, 0.3, -0.3, 0.6, -0.6)]
        c += [(x + 0.95 + L / 2 + g, y + sh) for sh in (0, 0.3, -0.3)] + [(x - 0.95 - L / 2 - g, y + sh) for sh in (0, 0.3, -0.3)]
    tp_named[ref] = bool(put(ref + ' net name', s_, c, ((PH, PW),), side=side, chk=(ref, '1', rx)))
    if not tp_named[ref] and len(s_) > 3:      # turned 90
        cc = [(x + 0.9 + 0.63 * PH + g, y + sh) for g in (0, 0.2, 0.4) for sh in (0, 0.4, -0.4)] + [(x - 0.9 - 0.63 * PH - g, y + sh) for g in (0, 0.2, 0.4) for sh in (0, 0.4, -0.4)]
        skipped.pop(); tp_named[ref] = bool(put(ref + ' net name', s_, cc, ((PH, PW),), ang=90, side=side))

# ---- 8. J1: its designator at the header's west end on the top (pin 1 end), turned, away from the pad row
p_ = pad('J1', '1')
for x, y, ang, side in ((6.75, 3.5, 90, F), (6.8, 3.5, 90, F), (6.7, 3.3, 90, F), (22.34, 8.9, 0, B), (22.34, 9.3, 0, B), (31.2, 8.9, 0, B)):
    if free(side, x, y, 'J1', DH, DW, ang):
        t = fps['J1'].Reference(); t.SetPosition(V(x, y)); style(t, DH, DW, ang, side); mine.append(t.m_Uuid.AsString()); addtext(side, 'J1', x, y, DH, DW, ang); mine_ref.add('J1'); print('J1 designator at (%.2f, %.2f) %s, angle %d' % (x, y, 'top' if side == F else 'bottom', ang)); break

# ---- 9. designators of our other parts: 0.8 x 0.75; one rule for all: north, south, east, west of the part at growing distance, horizontal
#         first, then turned 90; a place is taken only if the text is nearer to its own part than to any other part on that side.
RELAX = tuple(os.environ.get('RELAX', '').split(',')); why = {}; hidden = []; hidden_on_purpose = sorted(r for r in fps if r.startswith(('FID', 'H'))) + ['J15', 'J16', 'J17', 'J18', 'J19']; placed_des = {}
def rdist(a, c): return math.hypot(max(a[0] - c[2], 0, c[0] - a[2]), max(a[1] - c[3], 0, c[1] - a[3]))
order = sorted((r for r in fps if r not in locked and r not in mine_ref and not r.startswith(('FID', 'H'))),
               key=lambda r: (fps[r].GetBoundingBox(False).GetWidth() * fps[r].GetBoundingBox(False).GetHeight(), r))
order = [r for r in order if r[0] == 'U'] + [r for r in order if not r.startswith('TP') and r[0] != 'U'] + [r for r in order if r.startswith('TP')]      # ICs first, test points (they carry a net name) last
for r in order:
    f = fps[r]; t = f.Reference(); side = side_of(f); WHY.clear()
    x0, y0, x1, y1 = body_of[r][1] if r in body_of else rect(f.GetBoundingBox(False)); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; best = None
    others = [o for o in BODY[side] if not all(abs(a - c) < 0.11 for a, c in zip(o, (x0, y0, x1, y1)))]
    for ang in (0, 90):
        for g in (0.15, 0.3, 0.5, 0.8, 1.2, 1.7, 2.3, 3.0):
            ink0 = boxes(r, 0, 0, DH, DW, ang)[0]; up, dn, hw = -ink0[1], ink0[3], ink0[2]
            for sh in (0, 0.4, -0.4, 0.8, -0.8, 1.2, -1.2, 1.8, -1.8):
                for x, y in ((cx + sh, y0 - dn - g), (cx + sh, y1 + up + g), (x1 + hw + g, cy + sh), (x0 - hw - g, cy + sh)):
                    fr = free(side, x, y, r, DH, DW, ang, own=r, relax=RELAX)
                    if not fr: continue
                    d_own = rdist(fr[0], (x0, y0, x1, y1))
                    if any(rdist(fr[0], (o[0] + .1, o[1] + .1, o[2] - .1, o[3] - .1)) < d_own - 0.05 for o in others): WHY['nearer to another part'] += 1; continue
                    best = (x, y, ang, g); break
                if best: break
            if best: break
        if best: break
    if not best: hidden.append(r); why[r] = dict(WHY); continue
    x, y, ang, g = best; t.SetPosition(V(x, y)); style(t, DH, DW, ang, side); mine.append(t.m_Uuid.AsString()); addtext(side, r, x, y, DH, DW, ang); placed_des[r] = (round(x, 2), round(y, 2), ang, g)
print('our designators: %d placed by the rule (%d turned 90, %d further than 0.8 mm from the part), %d with their function label; hidden for want of a clear place: %d %s; hidden on purpose: %s'
      % (len(placed_des), sum(1 for v in placed_des.values() if v[2]), sum(1 for v in placed_des.values() if v[3] > 0.8), len(mine_ref - {'J15', 'J16', 'J17', 'J18', 'J19'}), len(hidden), hidden, hidden_on_purpose))
for r in hidden: print('   hidden %s: candidates blocked by %s' % (r, why[r]))
print('labels placed: %d; left out: %d' % (len(done), len(skipped)))
for s in skipped: print('   left out:', s)
print('net check: %d labels, %d OK' % (len(netrows), sum(1 for r in netrows if r[4] == 'OK')))
pcbnew.SaveBoard(PATH, b)
# ---- the face: written into the font blocks of exactly the texts above
txt = open(PATH, encoding='utf-8').read(); n = 0
for u in dict.fromkeys(mine):
    i = txt.find('(uuid "%s")' % u); assert i > 0, u
    s0 = max(txt.rfind('\n\t(gr_text ', 0, i), txt.rfind('\n\t\t(property "Reference"', 0, i)); j = txt.find('(font\n', s0)
    k = txt.find(')\n', txt.find('(thickness', j)) + 2
    blk = txt[j:k]; assert j > 0 and j - s0 < 600, (u, j - s0)
    if 'face' in blk: continue
    ind = blk[blk.rfind('\n', 0, blk.find('(size')) + 1:blk.find('(size')]
    blk = blk.replace('(font\n', '(font\n%s(face "Menlo")\n' % ind, 1) + '%s(bold yes)\n' % ind if '(bold yes)' not in txt[j:k + 40] else blk.replace('(font\n', '(font\n%s(face "Menlo")\n' % ind, 1)
    txt = txt[:j] + blk + txt[k:]; n += 1
assert txt.count('(') == txt.count(')'); open(PATH, 'w', encoding='utf-8').write(txt)
print('Menlo Bold written into %d text blocks' % n)
json.dump({'locked': sorted(locked), 'hidden': hidden, 'hidden_on_purpose': hidden_on_purpose, 'skipped': skipped, 'labels': done, 'net_check': netrows, 'designators': placed_des,
           'via_tenting': {'board_front': bool(ds.m_TentViasFront), 'board_back': bool(ds.m_TentViasBack), 'per_via': {str(k): v for k, v in tent.items()}}}, open(REPORT, 'w'), indent=0)
