"""Step 24 planner: new places for the designators that stand too close to an outline or read as another part's.

Usage: step24_plan.py <board> <out.json> REF [REF ...]      (read only on the board; writes the JSON)

For each named designator, in the order given, it searches the places within REACH mm of the part (0.1 mm grid,
same text angle as today) and keeps the best one that is free:
  - GAP_PAD from every pad on that side (its own part's too) and from every fiducial opening,
  - GAP_SILK from every other silkscreen line and text on that side (boxes; rectangles count as their four edges),
  - not on another part's body (the box around its pads), EDGE from the board edge.
Best = nearest to its own part, with a penalty when another part is as near as its own, and a small penalty for
distance moved. A designator already in a free place moves only when the gain is clear. Boxes are the texts'
bounding boxes, which are larger than the drawn letters, so the real gaps are larger than the limits.
"""
import json
import sys
import pcbnew

GAP_PAD, GAP_SILK, EDGE, REACH = 0.20, 0.16, 0.50, 2.6
b = pcbnew.LoadBoard(sys.argv[1])
out, wanted = sys.argv[2], sys.argv[3:]
mm = pcbnew.ToMM
eb = b.GetBoardEdgesBoundingBox()
EX0, EY0, EX1, EY1 = mm(eb.GetX()), mm(eb.GetY()), mm(eb.GetRight()), mm(eb.GetBottom())
SIDES = {"top": (pcbnew.F_Cu, b.GetLayerID("F.SilkS")), "bottom": (pcbnew.B_Cu, b.GetLayerID("B.SilkS"))}


def box(o):
    r = o.GetBoundingBox()
    return (mm(r.GetX()), mm(r.GetY()), mm(r.GetRight()), mm(r.GetBottom()))


def gap(a, c):
    dx = max(c[0] - a[2], a[0] - c[2], 0)
    dy = max(c[1] - a[3], a[1] - c[3], 0)
    return (dx * dx + dy * dy) ** 0.5


def union(bs):
    return (min(x[0] for x in bs), min(x[1] for x in bs), max(x[2] for x in bs), max(x[3] for x in bs))


fps = {f.GetReference(): f for f in b.GetFootprints()}
pads = {"top": [], "bottom": []}      # (box, gap, owner)
silk = {"top": [], "bottom": []}      # (box, owner key)
body = {"top": {}, "bottom": {}}
for ref, f in fps.items():
    for s, (cu, sl) in SIDES.items():
        mine = []
        for p in f.Pads():
            if p.IsOnLayer(cu):
                pb = box(p)
                m = mm(p.GetLocalSolderMaskMargin() or 0) if ref.startswith("FID") else 0
                pads[s].append(((pb[0] - m, pb[1] - m, pb[2] + m, pb[3] + m), GAP_PAD, ref))
                mine.append(pb)
        if mine:
            body[s][ref] = union(mine)
        for g in f.GraphicalItems():
            if g.GetLayer() == sl:
                silk[s].append((box(g), "g:" + ref))
        for fld in f.GetFields():
            if fld.GetLayer() == sl and fld.IsVisible():
                silk[s].append((box(fld), "ref:" + ref if fld == f.Reference() or fld.GetText() == ref else "f:" + ref))
for d in b.GetDrawings():
    for s, (_, sl) in SIDES.items():
        if d.GetLayer() != sl:
            continue
        x0, y0, x1, y1 = box(d)
        if d.GetClass() == "PCB_SHAPE" and d.GetShape() == pcbnew.SHAPE_T_RECT:
            for e in ((x0, y0, x1, y0 + 0.2), (x0, y1 - 0.2, x1, y1), (x0, y0, x0 + 0.2, y1), (x1 - 0.2, y0, x1, y1)):
                silk[s].append((e, "board"))
        else:
            silk[s].append(((x0, y0, x1, y1), "board"))

plan = {}
for ref in wanted:
    f = fps[ref]
    r = f.Reference()
    s = "bottom" if r.GetLayer() == SIDES["bottom"][1] else "top"
    assert r.IsVisible() and r.GetLayer() == SIDES[s][1], ref
    tb = box(r)
    w, h = tb[2] - tb[0], tb[3] - tb[1]
    cx, cy = (tb[0] + tb[2]) / 2, (tb[1] + tb[3]) / 2
    own = body[s][ref]
    others = [(o, bb) for o, bb in body[s].items() if o != ref]
    key = "ref:" + ref

    def cost(x, y):
        t = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
        if t[0] < EX0 + EDGE or t[2] > EX1 - EDGE or t[1] < EY0 + EDGE or t[3] > EY1 - EDGE:
            return None
        if any(gap(t, pb) < g for pb, g, _ in pads[s]):
            return None
        if any(gap(t, sb) < GAP_SILK for sb, k in silk[s] if k != key):
            return None
        og = gap(t, own)
        near = min(gap(t, bb) for _, bb in others)
        if near <= 0:
            return None
        return og + (1.0 if near < og + 0.15 else 0.0) + 0.05 * ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5

    now = cost(cx, cy)
    best = (now if now is not None else 99.0, cx, cy)
    n = int(REACH / 0.1)
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            x, y = cx + i * 0.1, cy + j * 0.1
            c = cost(x, y)
            if c is not None and c < best[0] - 1e-9:
                best = (c, x, y)
    move = (round(best[1] - cx, 2), round(best[2] - cy, 2))
    if move != (0.0, 0.0) and (now is None or best[0] < now - 0.3):
        plan[ref] = {"side": s, "move": list(move), "from_box": [round(v, 2) for v in tb], "cost": [None if now is None else round(now, 2), round(best[0], 2)]}
        nb = (best[1] - w / 2, best[2] - h / 2, best[1] + w / 2, best[2] + h / 2)
        silk[s] = [(sb, k) for sb, k in silk[s] if k != key] + [(nb, key)]
        print("  %-5s %-6s move (%+.2f, %+.2f)  cost %s -> %.2f" % (ref, s, move[0], move[1], "blocked" if now is None else "%.2f" % now, best[0]))
    else:
        print("  %-5s %-6s stays (%s)" % (ref, s, "no free place found" if now is None and best[0] >= 99 else "no clearly better place"))
json.dump(plan, open(out, "w"), indent=1, sort_keys=True)
print("%d of %d designators get a new place" % (len(plan), len(wanted)))
