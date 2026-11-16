"""Stage 4 silkscreen clean-up, for a SCRATCH COPY of the board folder (never the committed board).
Usage: <KiCad python> silk.py <scratch board.kicad_pcb> <mote board.kicad_pcb> [report.json]

Rules (Nick's standing style, DESIGN D39 of the frozen board, read 2026-11-16):
  font      Menlo Bold (slashed zero), as every visible text of the frozen board. pcbnew's Python cannot set a face, so the face is
            written into the saved file's font blocks afterwards (D39 did the same); KiCad rebuilds the outlines when it loads the file.
  sizes     function names 1.4 x 1.1 mm; designators, pin and pad labels 1.0 x 0.75 mm, 0.15 mm line: JLC's minimums,
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
obst = {F: [], B: []}
for r, f in fps.items():
    side = B if f.IsFlipped() else F
    for p in f.Pads():
        th = p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH)
        for s in ((F, B) if th else (side,)): obst[s].append(rect(p.GetBoundingBox(), 0.2))
    if r != 'J1' and r not in ('J5', 'J11', 'J12', 'J13', 'J14') and not r.startswith('TP'): obst[side].append(rect(f.GetBoundingBox(False), 0.1))   # bare pad rows, wire pads and test points: pads only
    if r.startswith('FID'): x, y = N(f.GetPosition()); obst[side].append((x - 1.1, y - 1.1, x + 1.1, y + 1.1))
    if r in locked:
        for t in [f.Reference(), f.Value()] + [g for g in f.GraphicalItems() if g.GetClass() == 'PCB_TEXT']:
            if t.IsVisible() and t.GetLayer() in (F, B): obst[t.GetLayer()].append(rect(t.GetBoundingBox(), 0.1))
# vias are not obstacles here (they are under solder mask on this board's plots); kicad-cli's silk_over_copper is the judge afterwards
hit = lambda a, c: not (a[2] <= c[0] or c[2] <= a[0] or a[3] <= c[1] or c[3] <= a[1])
def tsize(s, h, w, ang=0):
    L = 0.8 * w * len(s) + 0.15; return (L, h + 0.1) if ang == 0 else (h + 0.1, L)       # Menlo: 0.79 x width per character, measured on the frozen board's 'BM2'
def free(side, x, y, s, h, w, ang=0):
    tw, th = tsize(s, h, w, ang); r = (x - tw / 2, y - th / 2, x + tw / 2, y + th / 2)
    if min(s3lib.edge_margin(p) for p in ((r[0], r[1]), (r[2], r[1]), (r[0], r[3]), (r[2], r[3]))) < 0.6: return None
    return None if any(hit(r, o) for o in obst[side]) else r
def style(t, h, w, ang, side):
    t.SetTextSize(pcbnew.VECTOR2I(IU(w), IU(h))); t.SetTextThickness(IU(0.15)); t.SetTextAngleDegrees(ang)
    t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER); t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER); t.SetMirrored(side == B); t.SetLayer(side); t.SetVisible(True)
done, skipped = [], []
def label(s, x, y, h=1.0, w=0.75, ang=0, side=F, must=False, what=''):
    r = free(side, x, y, s, h, w, ang)
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

# ---- 1. function names north of the south-wall connectors, designator under it, pin names beside the designator
ROW1, ROW2 = 30.75, 32.05
def conn(ref, name, pins=()):
    xs = [pad(ref, n)[0] for n in ('1', '2', '3', '4') if any(p.GetNumber() == n for p in fps[ref].Pads())]; cx = (min(xs) + max(xs)) / 2
    label(name, cx, ROW1, 1.4, 1.1, must=True, what=ref + ' function'); label(ref, cx, ROW2, must=True, what=ref + ' designator'); mine_ref.add(ref)
    for s, x in pins: label(s, x, ROW2, what=ref + ' pin')
mine_ref = set()
p = lambda r, n: pad(r, n)[0]
print('pin 1 x of J7 %.2f J9 %.2f J8 %.2f J3 %.2f J10 %.2f; pin nets: %s' % (p('J7', '1'), p('J9', '1'), p('J8', '1'), p('J3', '1'), p('J10', '1'),
      {r: {q.GetNumber(): s3lib.sn(q.GetNetname()) for q in fps[r].Pads() if q.GetNumber() != 'MP'} for r in ('J7', 'J9', 'J8', 'J3', 'J10')}))
sgn = lambda r, a, c: -1 if p(r, a) < p(r, c) else 1
conn('J7', 'MOTOR', (('O1', (p('J7', '1') + p('J7', '2')) / 2 + sgn('J7', '1', '4') * 1.45), ('O2', (p('J7', '3') + p('J7', '4')) / 2 - sgn('J7', '1', '4') * 1.45)))
conn('J9', 'BM2', (('N', (p('J9', '1') + p('J9', '2')) / 2 + sgn('J9', '1', '4') * 0.9), ('P', (p('J9', '3') + p('J9', '4')) / 2 - sgn('J9', '1', '4') * 0.9)))
conn('J8', 'POT', (('3V3', p('J8', '1') + sgn('J8', '1', '3') * 1.15), ('GND', p('J8', '3') - sgn('J8', '1', '3') * 1.15)))
conn('J3', 'QWIIC', (('1', p('J3', '1') + sgn('J3', '1', '4') * 0.9),))
conn('J10', 'BM1', (('N', (p('J10', '1') + p('J10', '2')) / 2 + sgn('J10', '1', '4') * 0.9), ('P', (p('J10', '3') + p('J10', '4')) / 2 - sgn('J10', '1', '4') * 0.9)))
# ---- 2. LEDs as on the frozen board: ADIN above the centre one, BM2 | PWR | BM1 under them (D10 = port 2, D8 = power, D9 = port 1 by their nets)
nets = {r: sorted(s3lib.sn(q.GetNetname()) for q in fps[r].Pads()) for r in ('D10', 'D8', 'D9')}; print('LED nets:', nets)
assert any('P2_LED' in n for n in nets['D10']) and any('P1_LED' in n for n in nets['D9']) and 'GND' in nets['D8']
ly = N(fps['D8'].GetPosition())[1]
label('ADIN', N(fps['D8'].GetPosition())[0], ly - 2.35, must=True, what='LED')
for r, s in (('D10', 'BM2'), ('D8', 'PWR'), ('D9', 'BM1')): label(s, N(fps[r].GetPosition())[0], ly + 2.3, 1.0, 0.8, must=True, what='LED ' + r)
# ---- 3. power outputs: boxed, polarity at the pads
j4 = [padbb('J4', '1'), padbb('J4', '2')]; print('J4 pads:', {n: (pad('J4', n), s3lib.sn([q for q in fps['J4'].Pads() if q.GetNumber() == n][0].GetNetname())) for n in '12'})
box(min(r[0] for r in j4) - 0.35, min(r[1] for r in j4) - 0.35, max(r[2] for r in j4) + 0.35, max(r[3] for r in j4) + 0.35)
label('+', pad('J4', '1')[0], max(r[3] for r in j4) + 1.1, 1.2, 1.2, must=True, what='J4'); label('GND', pad('J4', '2')[0] + 0.5, max(r[3] for r in j4) + 1.1, must=True, what='J4')
label('5V AUX', 9.1, 20.9, 1.4, 1.0, must=True, what='J4 function'); label('J4', 9.1, 22.2, must=True, what='J4 designator'); mine_ref.add('J4')
j5 = [padbb('J5', '1'), padbb('J5', '2')]; print('J5 pads:', {n: (pad('J5', n), s3lib.sn([q for q in fps['J5'].Pads() if q.GetNumber() == n][0].GetNetname())) for n in '12'})
box(min(r[0] for r in j5) - 0.3, min(r[1] for r in j5) - 0.3, max(r[2] for r in j5) + 0.3, max(r[3] for r in j5) + 0.3)
label('VBUS OUT', 61.9, max(r[3] for r in j5) + 0.95, 1.0, 0.68, what='J5 function'); label('+', 60.45, min(r[1] for r in j5) - 1.0, 1.2, 1.2, what='J5 polarity'); mine_ref.add('J5')
# ---- 4. GPIO / GND pads: the GPIO number at each pad
for ref, n, s, dx, dy, ang in (('J11', '1', '14', 0, -1.55, 0), ('J11', '2', '15', 0, -1.55, 0), ('J12', '1', '18', -1.65, 0, 0), ('J12', '2', '19', -1.65, 0, 0),
                               ('J13', '1', '17', -1.65, 0, 0), ('J13', '2', '20', -1.65, 0, 0), ('J14', '2', 'GND', 1.5, 0, 90)):
    x, y = pad(ref, n); label(s, x + dx, y + dy, ang=ang, what=ref + ' pad')
label('GPIO', pad('J11', '1')[0] + 1.27, pad('J11', '1')[1] + 1.55, what='J11 function')
# ---- 5. test points: short net name beside the pad
for ref, s in (('TP40', 'IN1'), ('TP41', 'OUT1'), ('TP42', 'OUT2'), ('TP43', 'SCL0')):
    f = fps[ref]; side = B if f.IsFlipped() else F; x, y = N(f.GetPosition())
    for dx, dy in ((0, -1.5), (0, 1.5), (1.4 + 0.3 * len(s), 0), (-1.4 - 0.3 * len(s), 0)):
        if free(side, x + dx, y + dy, s, 1.0, 0.75): label(s, x + dx, y + dy, side=side, what=ref + ' net'); break
    else: skipped.append('%s net name "%s": no room' % (ref, s))
    mine_ref.add(ref)                                   # the net name replaces the designator on the silkscreen
# ---- 6. designators of our other parts
hidden = []
for r in sorted(fps, key=lambda r: (fps[r].GetBoundingBox(False).GetWidth() * fps[r].GetBoundingBox(False).GetHeight(), r), reverse=True):
    f = fps[r]
    if r in locked or r in mine_ref: continue
    t = f.Reference(); side = B if f.IsFlipped() else F
    if r.startswith(('FID', 'H')) or r == 'J1': 
        if r == 'J1': t.SetVisible(True)      # J1's designator is left exactly as it was
        continue
    x0, y0, x1, y1 = rect(f.GetBoundingBox(False)); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; best = None
    for g in (0.3, 0.7, 1.2, 1.9, 2.8):
        for ang in (0, 90):
            tw, th = tsize(r, 1.0, 0.75, ang)
            for sh in (0, 0.7, -0.7, 1.5, -1.5):
                for x, y in ((cx + sh, y0 - th / 2 - g), (cx + sh, y1 + th / 2 + g), (x1 + tw / 2 + g, cy + sh), (x0 - tw / 2 - g, cy + sh)):
                    if free(side, x, y, r, 1.0, 0.75, ang): best = (x, y, ang); break
                if best: break
            if best: break
        if best: break
    if not best: hidden.append(r); continue
    x, y, ang = best; t.SetPosition(V(x, y)); style(t, 1.0, 0.75, ang, side); mine.append(t.m_Uuid.AsString())
    tw, th = tsize(r, 1.0, 0.75, ang); obst[side].append((x - tw / 2, y - th / 2, x + tw / 2, y + th / 2))
print('designators placed: %d; hidden for want of a clear place: %d %s' % (len([1 for r in fps if r not in locked]) - len(hidden), len(hidden), hidden))
print('labels placed: %d; left out: %d' % (len(done), len(skipped)))
for s in skipped: print('   left out:', s)
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
if len(sys.argv) > 3: json.dump({'locked': sorted(locked), 'hidden': hidden, 'skipped': skipped, 'labels': done}, open(sys.argv[3], 'w'), indent=0)
