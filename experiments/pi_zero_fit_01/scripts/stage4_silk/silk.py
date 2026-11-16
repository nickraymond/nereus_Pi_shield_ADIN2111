"""Stage 4 silkscreen clean-up, for a SCRATCH COPY of the board folder (never the committed board).
Usage: <KiCad python> silk.py <scratch board.kicad_pcb> <mote board.kicad_pcb> [report.json]

Rules (Nick's standing style, DESIGN D39 of the frozen board, read 2026-11-16):
  font      Menlo Bold (slashed zero), as every visible text of the frozen board. pcbnew's Python cannot set a face, so the face is
            written into the saved file's font blocks afterwards (D39 did the same); KiCad rebuilds the outlines when it loads the file.
  sizes     function names 1.3 x 1.05 mm (1.15 or 1.0 where the place is short); designators, pin and pad labels 1.0 x 0.75 mm, 0.15 mm line: JLC's minimums,
            docs/design-review/jlc_rules_2026-11.md lines 24-25 (min_text_height 1.0 mm, min_text_thickness 0.15 mm) and line 23
            (pad to silkscreen 0.15 mm); the same values are in the .kicad_pro (min_text_height, min_text_thickness, min_silk_clearance).
  locked    footprints that sit where Sofar's mote has them (81) are not touched: no text moved, resized or hidden.
  ours      every other footprint: designator re-placed by a small planner (horizontal first, off pads, bodies, other texts, edge);
            hidden if no place within reach (listed in the report). FID / H designators hidden, as on the frozen board.
New-frame mm (board - (113.47, 89.34)).
"""
import sys, os, re, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage3_routing'))
import s3lib, pcbnew
from s3lib import V, N, mm, IU
PATH, MOTE = sys.argv[1], sys.argv[2]
DH = float(os.environ.get('DES_H', '1.0')); DW = 0.75 if DH >= 1.0 else 0.7      # designator size; DES_H=0.8 is the frozen board's (under JLC's 1.0 mm)
DRY = os.environ.get('DRY') == '1'
mp = {f.GetReference(): (f.GetPosition().x, f.GetPosition().y) for f in pcbnew.LoadBoard(MOTE).GetFootprints()}
b = pcbnew.LoadBoard(PATH)
F, B = pcbnew.F_SilkS, pcbnew.B_SilkS
OFF = (IU(113.47), IU(89.34))
fps = {f.GetReference(): f for f in b.GetFootprints()}
# the mote sits in this board shifted by a constant: locked = same reference, same relative place as U1
du = (fps['U1'].GetPosition().x - mp['U1'][0], fps['U1'].GetPosition().y - mp['U1'][1])
locked = {r for r, f in fps.items() if r in mp and abs(f.GetPosition().x - mp[r][0] - du[0]) < 1000 and abs(f.GetPosition().y - mp[r][1] - du[1]) < 1000}
print('locked (Sofar) footprints: %d; ours: %d' % (len(locked), len(fps) - len(locked)))
mine = []                                     # uuids of texts that get the Menlo face
rect = lambda bb, g=0.0: (mm(bb.GetLeft()) - 113.47 - g, mm(bb.GetTop()) - 89.34 - g, mm(bb.GetRight()) - 113.47 + g, mm(bb.GetBottom()) - 89.34 + g)
obst = {F: [], B: []}; circ = {F: [], B: []}
for r, f in fps.items():
    side = B if f.IsFlipped() else F
    for p in f.Pads():
        th = p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH)
        for s in ((F, B) if th else (side,)): obst[s].append(rect(p.GetBoundingBox(), 0.15))     # JLC pad to silkscreen 0.15 mm
    if r.startswith('H') and r[1:].isdigit():            # mounting holes: a circle, the footprint's courtyard (screw head / stand-off), on both sides
        x, y = N(f.GetPosition()); rr = mm(f.GetBoundingBox(False).GetWidth()) / 2 + 0.1; circ[F].append((x, y, rr)); circ[B].append((x, y, rr))
    elif r != 'J1' and r not in ('J5', 'J11', 'J12', 'J13', 'J14') and not r.startswith(('TP', 'FID')): obst[side].append(rect(f.GetBoundingBox(False), 0.1))   # bare pad rows, wire pads and test points: pads only
    if r.startswith('FID'): x, y = N(f.GetPosition()); circ[side].append((x, y, 1.1))          # fiducial: its 2 mm mask opening + 0.1
    if r in locked:
        for t in [f.Reference(), f.Value()] + [g for g in f.GraphicalItems() if g.GetClass() == 'PCB_TEXT']:
            if t.IsVisible() and t.GetLayer() in (F, B): obst[t.GetLayer()].append(rect(t.GetBoundingBox(), 0.1))
# vias are not obstacles here (they are under solder mask on this board's plots); kicad-cli's silk_over_copper is the judge afterwards
for d in b.GetDrawings():
    if d.GetLayer() in (F, B): obst[d.GetLayer()].append(rect(d.GetBoundingBox(), 0.1))
hit = lambda a, c: not (a[2] <= c[0] or c[2] <= a[0] or a[3] <= c[1] or c[3] <= a[1])
def tsize(s, h, w, ang=0):
    """Box KiCad gives a Menlo Bold text (measured on the scratch board with pcbnew: width 0.842 x size-x per character, height 1.633 x size-y;
    kicad-cli's silk_overlap works on this box, not on the ink)."""
    L = 0.842 * w * len(s) + 0.06; H = 1.633 * h + 0.06; return (L, H) if ang == 0 else (H, L)
def free(side, x, y, s, h, w, ang=0, hole_r=None):
    """the text's box if it is clear of every obstacle and 0.5 mm inside the outline, else None. hole_r: use this radius for the
    mounting holes instead of their courtyard (only for J4's polarity marks, see section 3)."""
    tw, th = tsize(s, h, w, ang); r = (x - tw / 2, y - th / 2, x + tw / 2, y + th / 2)
    if min(s3lib.edge_margin(q) for q in ((r[0], r[1]), (r[2], r[1]), (r[0], r[3]), (r[2], r[3]))) < 0.5: return None
    blk = [o for o in obst[side] if hit(r, o)]
    for cx, cy, cr in circ[side]:
        rr = hole_r if (hole_r and cr > 2) else cr
        if (max(r[0] - cx, 0, cx - r[2]) ** 2 + max(r[1] - cy, 0, cy - r[3]) ** 2) ** 0.5 < rr: blk.append((cx, cy, rr))
    if blk and os.environ.get('DBG') and s in os.environ['DBG'].split(','): print('   DBG %s (%.2f, %.2f) blocked by' % (s, x, y), [tuple(round(v, 2) for v in o) for o in blk][:4])
    return None if blk else r
def style(t, h, w, ang, side):
    t.SetTextSize(pcbnew.VECTOR2I(IU(w), IU(h))); t.SetTextThickness(IU(0.15)); t.SetTextAngleDegrees(ang)
    t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER); t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER); t.SetMirrored(side == B); t.SetLayer(side); t.SetVisible(True)
done, skipped = [], []
def label(s, x, y, h=1.0, w=0.75, ang=0, side=F, must=False, what='', hole_r=None):
    r = free(side, x, y, s, h, w, ang, hole_r)
    if r is None and not must: skipped.append('%s "%s" at (%.2f, %.2f)' % (what, s, x, y)); return False
    t = pcbnew.PCB_TEXT(b); t.SetText(s); t.SetPosition(V(x, y)); style(t, h, w, ang, side); b.Add(t)
    mine.append(t.m_Uuid.AsString()); tw, th = tsize(s, h, w, ang); obst[side].append((x - tw / 2, y - th / 2, x + tw / 2, y + th / 2)); done.append((what, s, x, y)); return True
def box(x0, y0, x1, y1, side=F):
    for a, c in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        g = pcbnew.PCB_SHAPE(b); g.SetShape(pcbnew.SHAPE_T_SEGMENT); g.SetStart(V(*a)); g.SetEnd(V(*c)); g.SetWidth(IU(0.2)); g.SetLayer(side); b.Add(g)
    for o in ((x0 - .15, y0 - .15, x1 + .15, y0 + .15), (x0 - .15, y1 - .15, x1 + .15, y1 + .15), (x0 - .15, y0, x0 + .15, y1), (x1 - .15, y0, x1 + .15, y1)): obst[side].append(o)
pad = lambda ref, n: N([p for p in fps[ref].Pads() if p.GetNumber() == n][0].GetPosition())
padbb = lambda ref, n: rect([p for p in fps[ref].Pads() if p.GetNumber() == n][0].GetBoundingBox())

# ---- 0. our own footprints: old texts off, pin-header outlines of the pad rows off (they are bare pads; J14's hung over the edge)
kill = []
for r, f in fps.items():
    if r in locked: continue
    for g in f.GraphicalItems():
        if g.GetLayer() in (F, B) and (g.GetClass() == 'PCB_TEXT' and r in ('J4', 'J5') or r in ('J11', 'J12', 'J13', 'J14')): kill.append((f, g))
    f.Reference().SetVisible(False); f.Value().SetVisible(False) if f.Value().GetLayer() in (F, B) else None
for f, g in kill: f.Remove(g)
print('removed from our footprints: %d silkscreen items (J4 / J5 texts, J11..J14 outlines)' % len(kill))

# ---- 1. function names north of the south-wall connectors; the designator centred under the name; pin names beside the designator
mine_ref = set()
def first(cands, s, h, w, what, side=F, ang=0, hole_r=None):
    for x, y in cands:
        if free(side, x, y, s, h, w, ang, hole_r): return label(s, x, y, h, w, ang, side, what=what, hole_r=hole_r)
    skipped.append('%s "%s": no clear place' % (what, s)); return False
def conn(ref, name, pins=(), alt=None):
    """name large over the designator where two rows fit; else the name alone at 1.0 mm in the one row (the designator then goes to the planner).
    pins: (text at the pin-1 end, text at the other end), set left and right of the centre text in the same row."""
    xs = [pad(ref, n)[0] for n in ('1', '2', '3', '4') if any(q.GetNumber() == n for q in fps[ref].Pads())]; cx = (min(xs) + max(xs)) / 2
    row = rect(fps[ref].GetBoundingBox(False))[1] - 0.1 - tsize('X', 1.0, 0.75)[1] / 2 - 0.03; mid = None
    for h, w in ((1.3, 1.05), (1.15, 0.95)):
        y1 = row - tsize('X', 1.0, 0.75)[1] / 2 - tsize('X', h, w)[1] / 2 - 0.05
        for dx in (0, 0.4, -0.4, 0.8, -0.8, 1.2, -1.2):
            if not mid and free(F, cx + dx, y1, name, h, w) and free(F, cx, row, ref, 1.0, 0.75):
                label(name, cx + dx, y1, h, w, what=ref + ' function'); label(ref, cx, row, what=ref + ' designator'); mine_ref.add(ref); mid = (cx, ref, 0.75)
    DXS = [0] + [sg * k * 0.05 for k in range(1, 31) for sg in (1, -1)]; west_first = pad(ref, '1')[0] < cx
    def flank(x0, nm, w, pp, gap=0.15):          # places of the pin names left / right of a centre text at x0
        half = tsize(nm, 1.0, w)[0] / 2
        return [(s_, x0 + sg * (half + gap + tsize(s_, 1.0, 0.75)[0] / 2)) for s_, sg in zip(pp, (-1, 1) if west_first else (1, -1)) if s_]
    if not mid:                                  # one row: first with the pin names (full, then the short forms), then the name alone
        for pp in [pins] + ([alt] if alt else []) + [()]:
            for w in (0.95, 0.75, 0.6):
                for dx in DXS:
                    if not mid and free(F, cx + dx, row, name, 1.0, w) and all(free(F, x_, row, s_, 1.0, 0.75) for s_, x_ in flank(cx + dx, name, w, pp)):
                        label(name, cx + dx, row, 1.0, w, what=ref + ' function, one row at 1.0 x %.2f mm (no room for two rows)' % w); mid = (cx + dx, name, w)
                        for s_, x_ in flank(cx + dx, name, w, pp): label(s_, x_, row, what=ref + ' pin name')
                        if pp != pins: skipped.append('%s pin names %s: no room, %s' % (ref, pins, 'short forms %s used' % (pp,) if pp else 'none set'))
                        return
    if not mid: skipped.append('%s function "%s": no clear place north of the connector' % (ref, name)); return
    for (s_, xa), (_, xb), (_, xc) in zip(flank(mid[0], mid[1], mid[2], pins, 0.35), flank(mid[0], mid[1], mid[2], pins, 0.25), flank(mid[0], mid[1], mid[2], pins, 0.15)):
        first([(xa, row), (xb, row), (xc, row)], s_, 1.0, 0.75, ref + ' pin name')
conn('J7', 'MOTOR', ('O1', 'O2'))       # pins 1 + 2 MOTOR_OUT1, 3 + 4 MOTOR_OUT2
conn('J9', 'BM2', ('N', 'P'))           # pins 1 + 2 BM2_N, 3 + 4 BM2_P
conn('J8', 'POT', ('3V3', 'GND'), alt=('+', 'GND'))       # pin 1 3V3, pin 2 the wiper, pin 3 GND; '+' = 3V3 where '3V3' has no room
conn('J3', 'QWIIC', ('1', ''))          # 1.0 mm pitch: no room for four names; '1' marks pin 1 (GND; then PI_3V3, I2C3_SDA, I2C3_SCL)
conn('J10', 'BM1', ('N', 'P'))          # pins 1 + 2 BM1_N, 3 + 4 BM1_P
# ---- 2. LEDs as on the frozen board ('ADIN' over the centre LED, 'BM2' 'PWR' 'BM1' in a row at the LEDs): D10 = port 2, D8 = power, D9 = port 1 by their nets
nets = {r: sorted(s3lib.sn(q.GetNetname()) for q in fps[r].Pads()) for r in ('D10', 'D8', 'D9')}; print('LED nets:', nets)
assert any('P2_LED' in n for n in nets['D10']) and any('P1_LED' in n for n in nets['D9']) and 'GND' in nets['D8']
lx, ly = N(fps['D8'].GetPosition())
first([(lx, ly - 2.45), (lx, ly - 2.6), (lx, ly - 2.8)], 'ADIN', 1.0, 0.75, 'LED')
for r, s_ in (('D10', 'BM2'), ('D8', 'PWR'), ('D9', 'BM1')): first([(N(fps[r].GetPosition())[0], ly + d) for d in (2.45, 2.55, 2.65)], s_, 1.0, 0.8, 'LED ' + r)
# ---- 3. power outputs. J4 carries its box in the footprint already; J5 gets one. Polarity at the +5 V / VBUS pad.
j4 = [padbb('J4', '1'), padbb('J4', '2')]; print('J4 pads:', {n: (pad('J4', n), s3lib.sn([q for q in fps['J4'].Pads() if q.GetNumber() == n][0].GetNetname())) for n in '12'})
yb = rect(fps['J4'].GetBoundingBox(False))[3] + 0.1; th_ = tsize('+', 1.0, 1.0)[1] / 2
# The only place at the +5 V pad is south of the box, beside the H4 screw: these two marks are checked against the hole (1.35 mm + 0.2), not
# against H4's courtyard, and can lie under a screw head or stand-off there. The committed board's '+' sat in the same corner.
first([(pad('J4', '1')[0] - d, yb + th_ + 0.02) for d in (0, 0.2, 0.4, 0.6)], '+', 1.0, 1.0, 'J4 polarity (inside H4 courtyard)', hole_r=1.55)
first([(pad('J4', '2')[0] + d, yb + th_ + 0.02) for d in (0.3, 0.5, 0.7, 0.9, 1.1)], 'GND', 1.0, 0.75, 'J4 polarity (inside H4 courtyard)', hole_r=1.55)
for h, w in ((1.3, 0.95), (1.15, 0.9)):
    done_ = False
    for x, y in ((8.93, 21.6), (8.93, 22.0), (8.93, 22.7), (9.2, 22.7), (8.93, 23.0)):
        if free(F, x, y, '5V AUX', h, w) and free(F, x, y + 2.0, 'J4', 1.0, 0.75): label('5V AUX', x, y, h, w, what='J4 function'); label('J4', x, y + 2.0, what='J4 designator'); mine_ref.add('J4'); done_ = True; break
    if done_: break
else: skipped.append('J4 function "5V AUX": no clear place')
j5 = [padbb('J5', '1'), padbb('J5', '2')]; print('J5 pads:', {n: (pad('J5', n), s3lib.sn([q for q in fps['J5'].Pads() if q.GetNumber() == n][0].GetNetname())) for n in '12'})
bx = (min(r[0] for r in j5) - 0.2, min(r[1] for r in j5) - 0.2, max(r[2] for r in j5) + 0.2, max(r[3] for r in j5) + 0.2); box(*bx)
first([(61.9, bx[3] + 0.17 + tsize('X', 1.0, 0.68)[1] / 2 + d) for d in (0, 0.02)], 'VBUS OUT', 1.0, 0.68, 'J5 function (1.0 mm: 1.9 mm between J5 and J13)')
first([(x_, bx[1] - 0.17 - tsize('+', 1.0, 1.0)[1] / 2 - d) for d in (0, 0.1) for x_ in (60.5, 60.3)], '+', 1.0, 1.0, 'J5 polarity'); mine_ref.add('J5')
# ---- 4. GPIO / GND pads: the GPIO number at each pad, on the top; on the bottom as well where the top has no place
for ref, n, s_, cands in (('J11', '1', '14', ((0, -1.9), (0, 1.9))), ('J11', '2', '15', ((0, -1.9), (0, 1.9))), ('J12', '1', '18', ((-1.75, 0), (1.75, 0))), ('J12', '2', '19', ((-1.75, 0), (1.75, 0))),
                           ('J13', '1', '17', ((-1.75, 0), (1.75, 0))), ('J13', '2', '20', ((-1.75, 0), (1.75, 0))), ('J14', '2', 'GND', ((-2.1, 0), (-2.3, 0), (-2.1, -2.54), (-2.1, 2.54)))):
    x, y = pad(ref, n)
    if not any(free(F, x + dx, y + dy, s_, 1.0, 0.75) for dx, dy in cands): first([(x + dx, y + dy) for dx, dy in cands], s_, 1.0, 0.75, ref + ' pad (bottom side; no place on the top)', side=B)
    else: first([(x + dx, y + dy) for dx, dy in cands], s_, 1.0, 0.75, ref + ' pad')
    mine_ref.add(ref)                                    # the pad names stand for the designator; J11..J14 designators are tried again by the planner below
mine_ref -= {'J11', 'J12', 'J13', 'J14'}
# ---- 5. test points: short net name beside the pad (it replaces the designator); else the designator, by the planner
for ref, s_ in (('TP40', 'IN1'), ('TP41', 'OUT1'), ('TP42', 'OUT2'), ('TP43', 'SCL0')):
    f = fps[ref]; side = B if f.IsFlipped() else F; x, y = N(f.GetPosition()); tw, th = tsize(s_, 1.0, 0.75)
    if first([(x, y - 0.95 - th / 2), (x, y + 0.95 + th / 2), (x + 0.95 + tw / 2, y), (x - 0.95 - tw / 2, y), (x + 0.6, y - 0.95 - th / 2), (x - 0.6, y - 0.95 - th / 2)], s_, 1.0, 0.75, ref + ' net name', side=side): mine_ref.add(ref)
# ---- 6. designators of our other parts
hidden = []; hidden_on_purpose = []
for r in sorted(fps, key=lambda r: (fps[r].GetBoundingBox(False).GetWidth() * fps[r].GetBoundingBox(False).GetHeight(), r), reverse=True):
    f = fps[r]
    if r in locked or r in mine_ref: continue
    t = f.Reference(); side = B if f.IsFlipped() else F
    if r in ('D8', 'D9', 'D10'): hidden_on_purpose.append(r); continue      # the LEDs carry their function names; no place for three designators beside them
    if r.startswith(('FID', 'H')) or r == 'J1': 
        if r == 'J1': t.SetVisible(True)      # J1's designator is left exactly as it was
        continue
    x0, y0, x1, y1 = rect(f.GetBoundingBox(False)); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; best = None
    for g in (0.3, 0.7, 1.2, 1.9, 2.8):
        for ang in (0, 90):
            tw, th = tsize(r, DH, DW, ang)
            for sh in (0, 0.7, -0.7, 1.5, -1.5):
                for x, y in ((cx + sh, y0 - th / 2 - g), (cx + sh, y1 + th / 2 + g), (x1 + tw / 2 + g, cy + sh), (x0 - tw / 2 - g, cy + sh)):
                    if free(side, x, y, r, DH, DW, ang): best = (x, y, ang); break
                if best: break
            if best: break
        if best: break
    if not best: hidden.append(r); continue
    x, y, ang = best; t.SetPosition(V(x, y)); style(t, DH, DW, ang, side); mine.append(t.m_Uuid.AsString())
    tw, th = tsize(r, DH, DW, ang); obst[side].append((x - tw / 2, y - th / 2, x + tw / 2, y + th / 2))
nshown = sum(1 for r, f in fps.items() if r not in locked and f.Reference().IsVisible()) + len([r for r in mine_ref if not r.startswith('TP') and r != 'J5'])
print('our designators shown: %d (as board texts for the labelled connectors); hidden for want of a clear place: %d %s; hidden on purpose: %s + FID / H' % (nshown, len(hidden), hidden, hidden_on_purpose))
print('labels placed: %d; left out: %d' % (len(done), len(skipped)))
for s in skipped: print('   left out:', s)
if DRY: sys.exit(0)
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
if len(sys.argv) > 3: json.dump({'locked': sorted(locked), 'hidden': hidden, 'hidden_on_purpose': hidden_on_purpose, 'skipped': skipped, 'labels': done}, open(sys.argv[3], 'w'), indent=0)
