"""Development aid (not part of the build): a path HINT for one net.  <KiCad python> hint.py <board> then python on stdin.

A grid search (0.1 mm, 8 directions, heavy cost on bends and vias) over the same geometry model the pre-check uses. Its output is
a suggestion only: every path that goes on the board is written by hand into a phase script as a few 0 / 45 / 90 degree segments,
checked by the pre-check and then by kicad-cli DRC.
   hint(net, start, goal, layers='TB12', w=0.2, clr=0.15, box=None, via=8, start_layers=None, goal_layers=None)
start / goal: (x, y) new-frame mm, exact. layers: T top, B bottom, 1 Internal 1, 2 Internal 2. Prints the polylines and vias.
"""
import sys, math, heapq, s3lib
r = s3lib.Router(sys.argv[1], 'hint'); g = r.geo
LN = {'T': 'Top Layer', 'B': '6 Bottom Layer', '1': 'Internal 1', '2': 'Internal 2'}
Hs = 0.1
KEEP = 3.0     # screw keep-out rule areas are r 3.0 on every copper layer
def _mark(blk, nx, ny, ox, oy, x0, y0, x1, y1, fn, R):
    i0 = max(0, int(math.floor((x0 - R - ox) / Hs))); i1 = min(nx - 1, int(math.ceil((x1 + R - ox) / Hs)))
    j0 = max(0, int(math.floor((y0 - R - oy) / Hs))); j1 = min(ny - 1, int(math.ceil((y1 + R - oy) / Hs)))
    for j in range(j0, j1 + 1):
        y = oy + j * Hs; row = j * nx
        for i in range(i0, i1 + 1):
            if not blk[row + i] and fn(ox + i * Hs, y) < R: blk[row + i] = 1
def _cap(blk, nx, ny, ox, oy, a, b, rad, R):
    L = math.hypot(b[0] - a[0], b[1] - a[1]); n = max(1, int(L / 1.0))
    for k in range(n):
        p = (a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n); q = (a[0] + (b[0] - a[0]) * (k + 1) / n, a[1] + (b[1] - a[1]) * (k + 1) / n)
        _mark(blk, nx, ny, ox, oy, min(p[0], q[0]) - rad, min(p[1], q[1]) - rad, max(p[0], q[0]) + rad, max(p[1], q[1]) + rad,
              lambda x, y, p=p, q=q: s3lib._pt_seg(x, y, p[0], p[1], q[0], q[1]) - rad, R)
def blocked(layer, net, R, ox, oy, nx, ny, zones=True, bx=None):
    """bytearray: 1 where a track centre of half-width+clearance R may not be (other nets' copper, holes, keep-outs, edge)."""
    blk = bytearray(nx * ny)
    X0, Y0, X1, Y1 = bx
    for kind, n2, bb, data, desc in g.L[layer]:
        if n2 == net and net: continue
        if bb[0] - R > X1 or bb[2] + R < X0 or bb[1] - R > Y1 or bb[3] + R < Y0: continue
        if kind == 'cap': _cap(blk, nx, ny, ox, oy, data[0], data[1], data[2], R)
        elif kind == 'rect':
            x0, y0, x1, y1 = data
            _mark(blk, nx, ny, ox, oy, x0, y0, x1, y1, lambda x, y: math.hypot(max(x0 - x, 0, x - x1), max(y0 - y, 0, y - y1)), R)
        else:
            if not zones: continue
            for ring in data:
                for a, b in zip(ring, ring[1:] + ring[:1]):
                    if max(a[0], b[0]) + R < X0 or min(a[0], b[0]) - R > X1 or max(a[1], b[1]) + R < Y0 or min(a[1], b[1]) - R > Y1: continue
                    _cap(blk, nx, ny, ox, oy, a, b, 0.0, R)
            j0 = max(0, int((bb[1] - oy) / Hs)); j1 = min(ny - 1, int((bb[3] - oy) / Hs) + 1)
            for j in range(j0, j1 + 1):                                  # interior: scanline, even-odd over all rings
                y = oy + j * Hs + 1e-7; xs = []
                for ring in data:
                    for a, b in zip(ring, ring[1:] + ring[:1]):
                        if (a[1] > y) != (b[1] > y): xs.append(a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]))
                xs.sort()
                for k in range(0, len(xs) - 1, 2):
                    i0 = max(0, int(math.ceil((xs[k] - ox) / Hs))); i1 = min(nx - 1, int((xs[k + 1] - ox) / Hs))
                    for i in range(i0, i1 + 1): blk[j * nx + i] = 1
    for hx, hy, hr, need, n2, desc in g.holes:
        if n2 == net and net: continue
        e = hr + need               # hole edge to copper edge >= need; the copper half-width is R - 0.15 or so
        _mark(blk, nx, ny, ox, oy, hx - e, hy - e, hx + e, hy + e, lambda x, y, hx=hx, hy=hy, e=hr + need: math.hypot(x - hx, y - hy) - e + 0.15, R)
    for hx, hy in s3lib.HOLES:
        _mark(blk, nx, ny, ox, oy, hx - KEEP, hy - KEEP, hx + KEEP, hy + KEEP, lambda x, y, hx=hx, hy=hy: math.hypot(x - hx, y - hy) - KEEP - 0.15 + 0.02, R)
    for j in range(ny):
        y = oy + j * Hs
        for i in range(nx):
            x = ox + i * Hs
            if (x < 3.2 or x > 61.8 or y < 3.2 or y > 36.3 or x < R + 0.4 or y < R + 0.4) and s3lib.edge_margin((x, y)) < R - 0.15 + s3lib.EDGE: blk[j * nx + i] = 1
    return blk
DIRS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
def hint(net, start, goal, layers='TB12', w=0.2, clr=0.15, box=None, via=8.0, start_layers=None, goal_layers=None, bend=0.6, show=True, avoid=(), align=True):
    """avoid: [(x0, y0, x1, y1, layers)] extra no-go boxes. align: the goal is moved (<= 0.05 mm) onto the grid of the start."""
    if align: goal = (round(start[0] + round((goal[0] - start[0]) / Hs) * Hs, 4), round(start[1] + round((goal[1] - start[1]) / Hs) * Hs, 4))
    X0, Y0, X1, Y1 = box or (min(start[0], goal[0]) - 6, min(start[1], goal[1]) - 6, max(start[0], goal[0]) + 6, max(start[1], goal[1]) + 6)
    X0, Y0, X1, Y1 = max(X0, 0), max(Y0, 0), min(X1, 65), min(Y1, 39.5)
    ox = start[0] - round((start[0] - X0) / Hs) * Hs; oy = start[1] - round((start[1] - Y0) / Hs) * Hs
    nx = int((X1 - ox) / Hs) + 1; ny = int((Y1 - oy) / Hs) + 1; R = w / 2 + clr; ls = [LN[c] for c in layers]
    blk = [blocked(l, net, R, ox, oy, nx, ny, bx=(X0, Y0, X1, Y1)) for l in ls]
    for (a0, b0, a1, b1, lay) in avoid:
        for li, c in enumerate(layers):
            if c in lay: _mark(blk[li], nx, ny, ox, oy, a0, b0, a1, b1, lambda x, y: -1.0 if a0 <= x <= a1 and b0 <= y <= b1 else 1.0, 0.0)
    vb = None
    if len(ls) > 1:
        vb = bytearray(nx * ny)
        for l in g.L:
            b2 = blocked(l, net, 0.3 + clr, ox, oy, nx, ny, zones=l not in s3lib.PLANES, bx=(X0, Y0, X1, Y1))
            for k in range(nx * ny):
                if b2[k]: vb[k] = 1
        for l in ('Top Layer', '6 Bottom Layer'):                       # no via in or against a pad of the net itself
            for kind, n2, bb, data, desc in g.L[l]:
                if n2 == net and desc.startswith('pad ') and kind == 'rect':
                    x0, y0, x1, y1 = data; _mark(vb, nx, ny, ox, oy, x0, y0, x1, y1, lambda x, y, x0=x0, y0=y0, x1=x1, y1=y1: math.hypot(max(x0 - x, 0, x - x1), max(y0 - y, 0, y - y1)), 0.42)
        for hx, hy, hr, need, n2, desc in g.holes:                      # hole to hole 0.25 (project rule 0.2; pad holes 0.45)
            e = hr + 0.15 + (0.45 if 'pad' in desc else 0.25)
            _mark(vb, nx, ny, ox, oy, hx - e, hy - e, hx + e, hy + e, lambda x, y, hx=hx, hy=hy, e=e: math.hypot(x - hx, y - hy) - e, 0.0)
    si, sj = int(round((start[0] - ox) / Hs)), int(round((start[1] - oy) / Hs)); gi, gj = int(round((goal[0] - ox) / Hs)), int(round((goal[1] - oy) / Hs))
    sl = [ls.index(LN[c]) for c in (start_layers or layers)]; gl = set(ls.index(LN[c]) for c in (goal_layers or layers))
    NL = len(ls); S = lambda l, i, j, d: ((l * ny + j) * nx + i) * 9 + d
    pq = []; best = {}; prev = {}
    for l in sl:
        s = S(l, si, sj, 8); best[s] = 0.0; heapq.heappush(pq, (0.0, 0.0, l, si, sj, 8))
    h = lambda i, j: (max(abs(i - gi), abs(j - gj)) + 0.4142 * min(abs(i - gi), abs(j - gj))) * Hs
    end = None; n = 0
    while pq:
        f, c, l, i, j, d = heapq.heappop(pq); s = S(l, i, j, d)
        if best.get(s, 1e9) < c - 1e-9: continue
        n += 1
        if i == gi and j == gj and l in gl: end = (l, i, j, d); break
        if n > 3000000: break
        for d2, (dx, dy) in enumerate(DIRS):
            if d != 8:
                t = min((d2 - d) % 8, (d - d2) % 8)
                if t > 2: continue
                pen = 0.0 if t == 0 else bend if t == 1 else 4 * bend
            else: pen = 0.0
            i2, j2 = i + dx, j + dy
            if not (0 <= i2 < nx and 0 <= j2 < ny) or blk[l][j2 * nx + i2]: continue
            if dx and dy and (blk[l][j * nx + i2] and blk[l][j2 * nx + i]): continue
            c2 = c + (Hs if not (dx and dy) else Hs * 1.41421) + pen; s2 = S(l, i2, j2, d2)
            if c2 < best.get(s2, 1e9) - 1e-9: best[s2] = c2; prev[s2] = (l, i, j, d); heapq.heappush(pq, (c2 + h(i2, j2), c2, l, i2, j2, d2))
        if vb is not None and not vb[j * nx + i]:
            for l2 in range(NL):
                if l2 == l: continue
                c2 = c + via; s2 = S(l2, i, j, 8)
                if c2 < best.get(s2, 1e9) - 1e-9: best[s2] = c2; prev[s2] = (l, i, j, d); heapq.heappush(pq, (c2 + h(i, j), c2, l2, i, j, 8))
    if not end:
        print('HINT %s: NO PATH (%d states) start blocked %s goal blocked %s' % (net, n, [blk[l][sj * nx + si] for l in range(NL)], [blk[l][gj * nx + gi] for l in range(NL)])); return None
    path = []; st = end
    while st is not None: path.append(st); st = prev.get(S(*st))
    path.reverse(); out = []; cur = None
    for l, i, j, d in path:
        p = (round(ox + i * Hs, 4), round(oy + j * Hs, 4))
        if cur is None or cur[0] != l: cur = [l, [p]]; out.append(cur)
        elif cur[1][-1] != p: cur[1].append(p)
    res = []
    for l, pts in out:
        sp = [pts[0]]
        for a, b in zip(pts[1:], pts[2:] + [None]):
            if b is None: sp.append(a); break
            u = (a[0] - sp[-1][0], a[1] - sp[-1][1]); v = (b[0] - a[0], b[1] - a[1])
            if abs(u[0] * v[1] - u[1] * v[0]) > 1e-9 or u[0] * v[0] + u[1] * v[1] < 0: sp.append(a)
        res.append((ls[l], sp))
    if (round(res[-1][1][-1][0], 4), round(res[-1][1][-1][1], 4)) != (round(goal[0], 4), round(goal[1], 4)): res = _snap(res, goal)
    if res is None: print('HINT %s: could not snap the end onto %s' % (net, goal)); return None
    tot = sum(s3lib.length(p) for _, p in res)
    if show:
        print('HINT %s w%.2f: %.1f mm, %d vias, %d corners (%d states)' % (net, w, tot, len(res) - 1, sum(len(p) - 2 for _, p in res if len(p) > 1), n))
        for l, sp in res: print('   %-14s %s' % (l, sp))
    return res
def _snap(res, goal):
    """the search ends on the grid node nearest the goal; move the last corners so the path ends exactly on it, all segments still 0/45/90."""
    l, pts = res[-1]; pts = [list(p) for p in pts]; d = (goal[0] - pts[-1][0], goal[1] - pts[-1][1])
    if len(pts) < 2: return None
    segs = [(k, (pts[k + 1][0] - pts[k][0], pts[k + 1][1] - pts[k][1])) for k in range(len(pts) - 1)]
    k2, u2 = segs[-1]; n2 = math.hypot(*u2); u2 = (u2[0] / n2, u2[1] / n2)
    for k1, u1 in reversed(segs[:-1]):
        n1 = math.hypot(*u1); u1 = (u1[0] / n1, u1[1] / n1); det = u1[0] * u2[1] - u1[1] * u2[0]
        if abs(det) < 1e-6: continue
        a = (d[0] * u2[1] - d[1] * u2[0]) / det; b = (u1[0] * d[1] - u1[1] * d[0]) / det
        for k in range(k1 + 1, len(pts)): pts[k][0] += a * u1[0]; pts[k][1] += a * u1[1]
        for k in range(k2 + 1, len(pts)): pts[k][0] += b * u2[0]; pts[k][1] += b * u2[1]
        return res[:-1] + [(l, [(round(x, 4), round(y, 4)) for x, y in pts])]
    if abs(d[0] * u2[1] - d[1] * u2[0]) < 1e-6: return res[:-1] + [(l, [tuple(p) for p in pts[:-1]] + [(round(goal[0], 4), round(goal[1], 4))])]
    return None
EMIT = []
def keep(net, res, w=0.2, clr=0.15, note=''):
    """add a hinted (or hand-written) path to the model so that later hints see it; collect the script lines."""
    if not res: return
    SH = {'Top Layer': 'T', '6 Bottom Layer': 'B', 'Internal 1': 'I1', 'Internal 2': 'I2'}
    for k, (l, pts) in enumerate(res):
        l = LN.get(l, l)
        if k and res[k - 1][1][-1] == pts[0]:
            hh = g.via(pts[0], 0.6, 0.3, net, clr)
            if hh: print('   !! via', pts[0], hh[:3])
            g.add_via(net, pts[0], 0.6, 0.3); EMIT.append("r.via(%r, %r)" % (net, tuple(pts[0])))
        if len(pts) > 1:
            hh = g.path(l, pts, w, net, clr)
            if hh: print('   !!', l, hh[:3])
            for a, b in zip(pts, pts[1:]): g.add_track(l, net, a, b, w)
            EMIT.append("r.track(%r, %s, %r, %s%s)" % (net, SH[l], [tuple(p) for p in pts], w, (", note=%r" % note) if note else ''))
def H(net, start, goal, layers='B', w=0.2, clr=0.15, note='', sl='B', gl='B', **kw):
    res = hint(net, start, goal, layers, w, clr, start_layers=sl if sl in layers else None, goal_layers=gl if gl in layers else None, **kw); keep(net, res, w, clr, note); return res
def emit(path):
    open(path, 'a').write('\n'.join(EMIT) + '\n'); print('emitted', len(EMIT))
def chk(layer, pts, w, net, clr=0.15):
    hh = g.path(LN.get(layer, layer), pts, w, net, clr); print('chk %s %s w%.2f %s: %s' % (layer, net, w, pts if len(pts) < 5 else (pts[0], pts[-1]), hh[:6] if hh else 'clear'))
def chkv(p, net, d=0.6, drill=0.3, clr=0.15):
    hh = g.via(p, d, drill, net, clr); print('via %s %s: %s' % (net, p, hh[:6] if hh else 'clear'))
def win(layer, x0, y0, x1, y1): g.window(LN.get(layer, layer), x0, y0, x1, y1)
def K(net, layer, pts, w=0.2, clr=0.13, note=''): keep(net, [(layer, pts)], w, clr, note)
def KV(net, p, clr=0.13):
    hh = g.via(p, 0.6, 0.3, net, clr)
    if hh: print('   !! via', net, p, hh[:3])
    g.add_via(net, p, 0.6, 0.3); EMIT.append("r.via(%r, %r)" % (net, tuple(p)))
class _R:      # so that the body of a phase script can be replayed here: r.track(...), r.via(...)
    def track(self, net, layer, pts, w, clr=0.13, note='', **kw): keep(net, [(layer, pts)], w, clr, note)
    def via(self, net, p, clr=0.13, **kw): KV(net, p, clr)
T, B, I1, I2 = 'Top Layer', '6 Bottom Layer', 'Internal 1', 'Internal 2'; C = 0.13
def replay(path):
    global r; r = _R(); exec(open(path).read().split('# ---- body ----')[1].split('# ---- end ----')[0], globals()); del EMIT[:]
exec(sys.stdin.read())
