"""Stage 11, job 2: the Bristlemouth logo and the board name on the bottom silkscreen, between TP8's "A_PWR" and TP35.
Usage: <KiCad python> logo.py <board.kicad_pcb> <frozen board.kicad_pcb> <report.json>      (PLAN=1: search and print only)

- Logo: the two filled polygons of the frozen board's top silkscreen (east strip, x > 173.5; Sofar's mote logo, there turned and 1.15 x). They are
  copied, turned back upright (the orientation of the mote file, checked below against the mote's own polygons if given as argv[4]), mirrored
  left-right for the bottom side and scaled by one factor.
- Texts: the frozen board's two strings, read from it ("Pi Shield", "ADIN2111 Rev0"), Menlo Bold, the frozen board's height ratio and its
  width-to-height ratio per line unless WR is set; mirrored. The second line is never under 1.0 mm (JLC, docs/design-review/jlc_rules_2026-11.md).
- Place: freearea.py's obstacles on a 0.05 mm grid, GAP mm further off. The logo is tested by its own shape (its drawn area, not its box), each
  text line by its ink box (stage 7's Menlo measure: 1.06 x height, 0.63 h above the anchor; 0.842 x width per character less 0.16 x width).
  Arrangements: logo left of the name, right of it, above it (as seen from the bottom, header at the top); logo and name are placed each for
  itself, SEP mm apart. The largest logo wins, then the largest text.
New-frame mm; seen from the bottom, left is larger x."""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import freearea, pcbnew
PATH, FROZEN, REPORT = sys.argv[1:4]; mm = pcbnew.ToMM; IU = pcbnew.FromMM; DX, DY = freearea.DX, freearea.DY; Bs = pcbnew.B_SilkS
GAP = float(os.environ.get('GAP', '0.15')); ST = 0.05; WIN = (24.0, 6.0, 49.0, 19.0)
fz = pcbnew.LoadBoard(FROZEN)
polys = []
for d in fz.GetDrawings():
    if d.GetClass() == 'PCB_SHAPE' and d.GetLayer() == pcbnew.F_SilkS and d.GetShape() == pcbnew.SHAPE_T_POLY and mm(d.GetBoundingBox().GetLeft()) > 173.5:
        ps = d.GetPolyShape(); assert ps.OutlineCount() == 1 and ps.HoleCount(0) == 0 and d.GetWidth() == 0; o = ps.Outline(0)
        polys.append([(mm(o.CPoint(i).x), mm(o.CPoint(i).y)) for i in range(o.PointCount())])
assert sorted(len(p) for p in polys) == [221, 3560], [len(p) for p in polys]
names = {d.GetText(): d for d in fz.GetDrawings() if d.GetClass() == 'PCB_TEXT' and d.GetLayer() == pcbnew.F_SilkS and mm(d.GetBoundingBox().GetLeft()) > 173.5 and d.GetTextAngleDegrees() == 270}
assert len(names) == 2, list(names)
T1, T2 = sorted(names, key=lambda s: -names[s].GetTextSize().y); F1, F2 = names[T1], names[T2]
print('frozen board: logo polygons %s points; texts %r %.2f x %.2f mm (h x w), %r %.2f x %.2f mm, font %s bold %s, line %.2f mm' % (sorted(len(p) for p in polys), T1, mm(F1.GetTextSize().y), mm(F1.GetTextSize().x),
      T2, mm(F2.GetTextSize().y), mm(F2.GetTextSize().x), F1.GetFontName(), F1.IsBold(), mm(F1.GetTextThickness())))
# upright: the frozen logo is the mote's turned by a quarter turn; (x, y) -> (y, -x) or (-y, x). The mote's own file decides which.
xs = [x for p in polys for x, y in p]; ys = [y for p in polys for x, y in p]; cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
def norm(pl):
    ax = [x for p in pl for x, y in p]; ay = [y for p in pl for x, y in p]; a, c = (min(ax) + max(ax)) / 2, (min(ay) + max(ay)) / 2
    return [[(x - a, y - c) for x, y in p] for p in pl], (max(ax) - min(ax), max(ay) - min(ay))
turns = {'a': lambda x, y: (y, -x), 'b': lambda x, y: (-y, x)}; up = None
if len(sys.argv) > 4:
    mt = pcbnew.LoadBoard(sys.argv[4]); mp = []
    for d in mt.GetDrawings():
        if d.GetClass() == 'PCB_SHAPE' and d.GetLayer() == pcbnew.F_SilkS and d.GetShape() == pcbnew.SHAPE_T_POLY:
            o = d.GetPolyShape().Outline(0); mp.append([(mm(o.CPoint(i).x), mm(o.CPoint(i).y)) for i in range(o.PointCount())])
    mn, msz = norm(sorted(mp, key=len)); k0 = (max(xs) - min(xs)) / msz[1]
    for k, fn in turns.items():
        cand, _ = norm([[fn(x, y) for x, y in p] for p in sorted(polys, key=len)])
        err = max(math.hypot(a[0] / k0 - m[0], a[1] / k0 - m[1]) for pc, pm in zip(cand, mn) for a, m in zip(pc, pm)) if all(len(a) == len(m) for a, m in zip(cand, mn)) else 9
        print('   turn %s: largest point distance from the mote logo (after 1 / %.4f): %.4f mm' % (k, k0, err))
        if err < 0.01: up = k
    assert up, 'the frozen logo is not the mote logo turned by a quarter turn'
    print('mote logo %.3f x %.3f mm; frozen logo %.3f x %.3f mm = the mote logo x %.4f, quarter turn "%s"' % (msz[0], msz[1], max(xs) - min(xs), max(ys) - min(ys), k0, up))
else: up = os.environ['TURN']
native, nsz = norm([[turns[up](x, y) for x, y in p] for p in polys])         # upright, at the frozen board's size, centred on (0, 0)
k0 = float(os.environ.get('K0', '1.15')); native = [[(x / k0, y / k0) for x, y in p] for p in native]; LW, LH = nsz[0] / k0, nsz[1] / k0     # mote size
bottom = [[(-x, y) for x, y in p] for p in native]                            # mirrored left-right: reads right from the bottom
def inside(p, x, y):
    c = False; n = len(p)
    for i in range(n):
        (x1, y1), (x2, y2) = p[i], p[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1): c = not c
    return c
def spans(p, y):
    xs_ = sorted(x1 + (y - y1) * (x2 - x1) / (y2 - y1) for (x1, y1), (x2, y2) in zip(p, p[1:] + p[:1]) if (y1 > y) != (y2 > y)); return list(zip(xs_[::2], xs_[1::2]))
big = max(bottom, key=len); eye = min(bottom, key=len)
# line widths of the logo at mote size: the spine (horizontal cuts through the upright bar), the lower bar (vertical cuts), the eye
tr = [(y, x) for x, y in big]
spine = sorted(max(b_ - a for a, b_ in spans(big, y)[-1:]) for y in [LH * (-0.3 + 0.05 * i) for i in range(8)]); bar = sorted(spans(tr, x)[-1][1] - spans(tr, x)[-1][0] for x in [LW * (0.05 * i) for i in range(5)])
eyed = max(x for x, y in eye) - min(x for x, y in eye)
print('logo at mote size: %.3f x %.3f mm; spine %.3f mm wide (median of 8 cuts), lowest bar %.3f mm (median of 5 cuts), eye %.3f mm across' % (LW, LH, spine[4], bar[2], eyed))
STROKE = min(spine[4], bar[2])
b = pcbnew.LoadBoard(PATH)
old = [d for d in b.GetDrawings() if d.GetLayer() == Bs and (d.GetClass() == 'PCB_TEXT' and d.GetText() in (T1, T2) or d.GetClass() == 'PCB_SHAPE' and d.GetShape() == pcbnew.SHAPE_T_POLY)]
assert not old, 'the board already has the name or a silkscreen polygon on the bottom'
R, C = freearea.obstacles(b); R = [(n, (r[0] - GAP, r[1] - GAP, r[2] + GAP, r[3] + GAP)) for n, r in R]; C = [(x, y, r + GAP) for x, y, r in C]
g, _ = freearea.raster(R, C, WIN); NX, NY = len(g[0]), len(g)
occ = [sum(1 << (NX - 1 - i) for i, v in enumerate(row) if v) | (-1 << NX) for row in g]       # bit i: column i counted from the larger-x side (left, seen from the bottom); all blocked beyond the window
def grow(o):
    """the occupancy grown by one cell in every direction"""
    h = [r | (r << 1) | (r >> 1) for r in o]; return [h[j] | h[max(j - 1, 0)] | h[min(j + 1, len(h) - 1)] for j in range(len(h))]
def logomask(s):
    """rows of bits of the logo at scale s, cell (0, 0) = its box's top-left corner as seen from the bottom"""
    if s in LM: return LM[s]
    w, h = LW * s, LH * s; rows = []
    for j in range(int(math.ceil(h / ST))):
        m = 0
        for p in native:           # seen from the bottom the mirrored logo reads as the upright one
            for yy in (j * ST, (j + 1) * ST - 1e-6, (j + .5) * ST):
                for a, c in spans([(x * s + w / 2, y * s + h / 2) for x, y in p], yy):
                    for i in range(max(0, int(a / ST)), int(c / ST) + 1): m |= 1 << i
        rows.append(m)
    LM[s] = (rows, w, h); return LM[s]
LM = {}
def rectmask(parts):
    """parts: [(x0, y0, x1, y1)] in mm from the group's top-left -> rows of bits"""
    H = max(p[3] for p in parts); rows = [0] * int(math.ceil(H / ST))
    for a, c, e, f in parts:
        for j in range(int(c / ST), min(len(rows), int(math.ceil(f / ST)))):
            for i in range(int(a / ST), int(math.ceil(e / ST))): rows[j] |= 1 << i
    return rows
def runs(r):
    out = []; i = 0
    while r >> i:
        if (r >> i) & 1:
            a = i
            while (r >> i) & 1: i += 1
            out.append((a, i))
        else: i += 1
    return out
def fits(rows, width, o=None):
    """every place (i, j) of the group's top-left cell at which no cell of the mask is blocked"""
    o = o or occ; out = []; rr = [runs(r) for r in rows]
    for j in range(NY - len(rows) + 1):
        blk = 0
        for k, rs in enumerate(rr):
            for a, c in rs:
                cur = o[j + k] >> a; n = 1; L = c - a
                while n < L: st_ = min(n, L - n); cur |= cur >> st_; n += st_
                blk |= cur
        out += [(i, j) for i in range(NX) if not (blk >> i) & 1]
    return out
R1 = mm(F1.GetTextSize().x) / mm(F1.GetTextSize().y); R2 = mm(F2.GetTextSize().x) / mm(F2.GetTextSize().y); HR = mm(F2.GetTextSize().y) / mm(F1.GetTextSize().y)
WR = float(os.environ.get('WR', '1.0'))                # width factor on the frozen board's letter widths
def textblock(h1):
    """the two lines, centred on each other: (mask rows, width, height, centres [(x, y, h, w)]) in mm from the block's top-left"""
    h2 = h1 * HR; w1, w2 = round(h1 * R1 * WR, 3), round(h2 * R2 * WR, 3); l1 = 0.842 * w1 * len(T1) - 0.16 * w1; l2 = 0.842 * w2 * len(T2) - 0.16 * w2; tw = max(l1, l2)
    lg = 0.25 * h1; th = 1.06 * h1 + lg + 1.06 * h2; c1 = (tw / 2, 0.63 * h1, h1, w1); c2 = (tw / 2, 1.06 * h1 + lg + 0.63 * h2, h2, w2)
    return rectmask([(tw / 2 - l1 / 2, 0, tw / 2 + l1 / 2, 1.06 * h1), (tw / 2 - l2 / 2, 1.06 * h1 + lg, tw / 2 + l2 / 2, th)]), tw, th, (c1, c2)
SEP = (0.5, 2.0)          # distance logo to name, mm: least, most
def pairs(arr, tf, tw, th, lf, lw, lh):
    """(cost, text place, logo place) for every pair of places that makes the arrangement; cells. The logo and the name are placed each for itself:
    beside each other their middles are at most a quarter of the taller one apart in height; above, the logo's middle is over the name."""
    out = []; c = lambda v: v / ST
    for ti, tj in tf:
        for li, lj in lf:
            if arr == 'logo above':
                gap = tj - (lj + c(lh)); off = abs((li + c(lw) / 2) - (ti + c(tw) / 2)); lim = c(tw) / 2 - c(lw) / 2
            else:
                gap = (ti - (li + c(lw))) if arr == 'logo left' else (li - (ti + c(tw))); off = abs((lj + c(lh) / 2) - (tj + c(th) / 2)); lim = max(c(lh), c(th)) / 4
            if c(SEP[0]) <= gap <= c(SEP[1]) and off <= max(lim, 0): out.append((gap + off, (ti, tj), (li, lj)))
    return out
H1MIN = 1.0 / HR; best = None; tried = {}; SMAX = float(os.environ.get('SMAX', '2.0'))
trows, tw, th, tc = textblock(H1MIN); tf = fits(trows, tw)
print('the name at its smallest (%.3f / 1.0 mm high, letter widths x %.2f of the frozen board\'s): block %.2f x %.2f mm, %d clear places' % (H1MIN, WR, tw, th, len(tf)))
for arr in ('logo left', 'logo right', 'logo above'):
    s = SMAX; got = None
    while s > 0.3 and not got:
        lrows, lw, lh = logomask(s); pr = pairs(arr, tf, tw, th, fits(lrows, lw), lw, lh)
        if pr: got = (s, len(pr))
        else: s = round(s - 0.02, 2)
    tried[arr] = got and got[0]
    print('arrangement "%s": largest logo with the name at its smallest: %s' % (arr, ('scale %.2f of the mote size (logo %.2f x %.2f mm), %d pairs of places' % (got[0], LW * got[0], LH * got[0], got[1])) if got else 'does not fit'))
    if got and (not best or got[0] > best[1]): best = (arr, got[0])
assert best, 'no arrangement fits; try WR (narrower letters) or GAP'
arr, s = best; h1 = H1MIN; lrows, lw, lh = logomask(s); lf = fits(lrows, lw)
while True:                                             # the largest name that still fits with that logo
    q = textblock(round(h1 + 0.025, 3)); pr2 = pairs(arr, fits(q[0], q[1]), q[1], q[2], lf, lw, lh)
    if not pr2: break
    h1 = round(h1 + 0.025, 3)
trows, tw, th, tc = textblock(h1); pr = sorted(pairs(arr, fits(trows, tw), tw, th, lf, lw, lh)); cost, (ti, tj), (li, lj) = pr[0]
X = lambda i_, u=0.0: WIN[2] - i_ * ST - u; Y = lambda j_, v=0.0: WIN[1] + j_ * ST + v       # seen from the bottom x runs right to left: column i is counted from the window's larger-x side
lbox = [X(li, lw), Y(lj), X(li), Y(lj, lh)]; tbox = [X(ti, tw), Y(tj), X(ti), Y(tj, th)]; gbox = [min(lbox[0], tbox[0]), min(lbox[1], tbox[1]), max(lbox[2], tbox[2]), max(lbox[3], tbox[3])]
print('chosen: "%s", logo scale %.2f of the mote size (frozen board: %.2f): logo %.2f x %.2f mm at x %.2f..%.2f, y %.2f..%.2f; texts %.3f and %.3f mm high, block %.2f x %.2f mm at x %.2f..%.2f, y %.2f..%.2f; %d pairs of places; all of it x %.2f..%.2f, y %.2f..%.2f (%.2f x %.2f mm); kept clear: the rule distances + %.2f mm'
      % (arr, s, k0, lw, lh, lbox[0], lbox[2], lbox[1], lbox[3], tc[0][2], tc[1][2], tw, th, tbox[0], tbox[2], tbox[1], tbox[3], len(pr), gbox[0], gbox[2], gbox[1], gbox[3], gbox[2] - gbox[0], gbox[3] - gbox[1], GAP))
print('finest logo line at this scale: %.3f mm (JLC minimum silkscreen line 0.15 mm); eye %.3f mm across' % (STROKE * s, eyed * s))
rep = {'arrangement': arr, 'tried': tried, 'logo_scale_of_mote': s, 'logo_mm': [lw, lh], 'logo_box': lbox, 'text_box': tbox, 'group_box': gbox, 'letter_width_factor': WR, 'gap_beyond_rule_mm': GAP,
       'texts': [{'text': t, 'x': X(ti, c[0]), 'y': Y(tj, c[1]), 'h': c[2], 'w': c[3]} for t, c in zip((T1, T2), tc)], 'finest_line_mm': STROKE * s, 'eye_mm': eyed * s}
json.dump(rep, open(REPORT, 'w'), indent=1)
if os.environ.get('PLAN'): sys.exit(0)
grp = pcbnew.PCB_GROUP(b); grp.SetName('Bristlemouth logo and board name'); b.Add(grp); mine = []
lcx, lcy = (lbox[0] + lbox[2]) / 2, (lbox[1] + lbox[3]) / 2
for p in bottom:                # mirrored left-right (x -> -x) about the logo's centre: as seen from the bottom it reads as the mote's logo
    sh = pcbnew.PCB_SHAPE(b); sh.SetShape(pcbnew.SHAPE_T_POLY); sh.SetLayer(Bs); sh.SetWidth(0); sh.SetFilled(True)
    sh.SetPolyPoints([pcbnew.VECTOR2I(IU(DX + lcx + x * s), IU(DY + lcy + y * s)) for x, y in p]); b.Add(sh); grp.AddItem(sh)
for q in rep['texts']:
    t = pcbnew.PCB_TEXT(b); t.SetText(q['text']); t.SetLayer(Bs); t.SetTextSize(pcbnew.VECTOR2I(IU(q['w']), IU(q['h']))); t.SetTextThickness(IU(0.15)); t.SetBold(True)
    t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER); t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER); t.SetMirrored(True); t.SetPosition(pcbnew.VECTOR2I(IU(DX + q['x']), IU(DY + q['y']))); b.Add(t); grp.AddItem(t); mine.append(t.m_Uuid.AsString())
pcbnew.SaveBoard(PATH, b)
txt = open(PATH, encoding='utf-8').read(); n = 0          # the face, as stage 7 does it
for u in mine:
    i = txt.find('(uuid "%s")' % u); s0 = txt.rfind('\n\t(gr_text ', 0, i); j = txt.find('(font\n', s0); assert 0 < j - s0 < 600
    ind = txt[txt.rfind('\n', 0, txt.find('(size', j)) + 1:txt.find('(size', j)]; k = txt.find(')\n', txt.find('(thickness', j)) + 2; blk = txt[j:k]; assert 'face' not in blk
    blk = blk.replace('(font\n', '(font\n%s(face "Menlo")\n' % ind, 1)
    if '(bold yes)' not in txt[j:k + 40]: blk += '%s(bold yes)\n' % ind
    txt = txt[:j] + blk + txt[k:]; n += 1
assert txt.count('(') == txt.count(')'); open(PATH, 'w', encoding='utf-8').write(txt)
print('added: 2 filled polygons (%d + %d points), 2 texts (Menlo Bold written into %d text blocks), one group' % (len(bottom[0]), len(bottom[1]), n))
