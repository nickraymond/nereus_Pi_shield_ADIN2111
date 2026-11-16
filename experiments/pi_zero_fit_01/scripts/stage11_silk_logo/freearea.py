"""Obstacles for new silkscreen on the bottom side, and the clear rectangles among them (new-frame mm, board - (113.47, 89.34)).
Obstacles: pads on the bottom and through-hole pads, mask openings (+ 0.15 mm, JLC pad to silkscreen); via holes (+ 0.1 mm, every via, tented or
not); bottom silkscreen graphics and texts (their boxes + 0.15 mm), Sofar's locked texts among them; bottom-side part bodies (pads, silkscreen,
fab outline; + 0.1 mm); 0.5 mm from the outline."""
import pcbnew
DX, DY = 113.47, 89.34; mm = pcbnew.ToMM; Bs = pcbnew.B_SilkS
def rect(bb, g=0.0): return (mm(bb.GetLeft()) - DX - g, mm(bb.GetTop()) - DY - g, mm(bb.GetRight()) - DX + g, mm(bb.GetBottom()) - DY + g)
def obstacles(b, skip=()):
    R = []; C = []
    for f in b.GetFootprints():
        body = []; bot = f.IsFlipped()
        for p in f.Pads():
            th = p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH)
            if th or bot: R.append(('pad ' + f.GetReference(), rect(p.GetBoundingBox(), 0.15)))
            if bot: body.append(rect(p.GetBoundingBox()))
        for g in f.GraphicalItems():
            L = g.GetLayer()
            if g.GetClass() == 'PCB_SHAPE':
                if L == pcbnew.B_Mask: R.append(('mask ' + f.GetReference(), rect(g.GetBoundingBox(), 0.15)))
                if L == Bs: R.append(('silk ' + f.GetReference(), rect(g.GetBoundingBox(), 0.15)))
                if bot and L in (Bs, pcbnew.B_Fab): body.append(rect(g.GetBoundingBox()))
            elif g.GetClass() == 'PCB_TEXT' and L == Bs and g.IsVisible(): R.append(('text ' + f.GetReference(), rect(g.GetBoundingBox(), 0.15)))
        for t in (f.Reference(), f.Value()):
            if t.IsVisible() and t.GetLayer() == Bs: R.append(('text ' + f.GetReference(), rect(t.GetBoundingBox(), 0.15)))
        if body and not f.GetReference().startswith(('TP', 'FID', 'H', 'J1')):
            R.append(('body ' + f.GetReference(), (min(r[0] for r in body) - .1, min(r[1] for r in body) - .1, max(r[2] for r in body) + .1, max(r[3] for r in body) + .1)))
    for d in b.GetDrawings():
        if d.GetLayer() == Bs and d.m_Uuid.AsString() not in skip: R.append(('board silk', rect(d.GetBoundingBox(), 0.15)))
    for t in b.GetTracks():
        if t.GetClass() == 'PCB_VIA': C.append((mm(t.GetPosition().x) - DX, mm(t.GetPosition().y) - DY, mm(t.GetDrill()) / 2 + 0.1))
    return R, C
def raster(R, C, win, st=0.05):
    """occupancy grid of the window (x0, y0, x1, y1): True = blocked"""
    x0, y0, x1, y1 = win; nx, ny = int(round((x1 - x0) / st)), int(round((y1 - y0) / st)); g = [[False] * nx for _ in range(ny)]
    for _, (a, c, e, f) in R:
        for j in range(max(0, int((c - y0) / st)), min(ny, int((f - y0) / st) + 1)):
            row = g[j]
            for i in range(max(0, int((a - x0) / st)), min(nx, int((e - x0) / st) + 1)): row[i] = True
    for cx, cy, r in C:
        for j in range(max(0, int((cy - r - y0) / st)), min(ny, int((cy + r - y0) / st) + 1)):
            for i in range(max(0, int((cx - r - x0) / st)), min(nx, int((cx + r - x0) / st) + 1)):
                px = min(max(cx, x0 + i * st), x0 + (i + 1) * st); py = min(max(cy, y0 + j * st), y0 + (j + 1) * st)
                if (px - cx) ** 2 + (py - cy) ** 2 < r * r: g[j][i] = True
    return g, st
def maxrects(g, st, win):
    """every maximal clear rectangle (x0, y0, x1, y1), by the histogram method"""
    ny, nx = len(g), len(g[0]); h = [0] * nx; out = set()
    for j in range(ny):
        for i in range(nx): h[i] = 0 if g[j][i] else h[i] + 1
        stack = []
        for i in range(nx + 1):
            cur = h[i] if i < nx else 0; start = i
            while stack and stack[-1][1] > cur:
                s, hh = stack.pop(); start = s
                if j == ny - 1 or any(g[j + 1][k] for k in range(s, i)): out.add((s, j - hh + 1, i, j + 1))
            if cur and (not stack or stack[-1][1] < cur): stack.append((start, cur))
    return [(win[0] + a * st, win[1] + c * st, win[0] + e * st, win[1] + f * st) for a, c, e, f in out]
