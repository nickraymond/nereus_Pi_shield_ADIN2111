"""A small grid router for the experiment (pure Python, no numpy: KiCad's bundled Python has none).

Model: 0.1 mm cells over the board frame; four routing layers (Top, Internal 1, Internal 2, Bottom; the GND and PWR
planes carry no tracks); through vias only. Every piece of copper on the board is written into per-layer maps by its
EXACT distance from each cell centre: `occ` (the cell centre is inside the copper) and, for each dilation radius r
(cells), `dil[r]` = "a new item whose half width + clearance is up to ρ_r = 0.1·r − 0.07 mm may not centre here unless
it is on the same net". Experiment 01 stamped copper as inflated cells and dilated them by integer disks, which
over-blocked by ≈ 0.2 mm and kept 0.2 mm tracks from threading between U1's thermal vias; this version computes the
distance to the real shape (circles, segments, rounded rectangles, polygons) and marks each map directly, so the
grid is exact to the cell pitch. Pads with no net, the board edge margin, hole keep-outs and the insert pull-backs
(blocked for every net but the insert's) are blocked for all. Routed copper is stamped back before the next net.
Widths, clearances and via sizes come from the class table (BRIEF §6).

New in 1.a (OPTIONS §2): `route_pair` / `commit_pair` route an ADIN pair as one virtual track and emit two offset
tracks with the mote's geometry; `escapes` gives fine-pitch pads a ≤ 1 mm 0.15 mm stub to the first cell where the
class width fits (BRIEF §5 fan-out allowance); `route` takes a per-layer cost (corridor preference); there are no
fallback classes.
"""
import heapq
import math

import pcbnew

import geom
from geom import MM, mm, V

PITCH = 0.1
X0, Y0 = geom.OUTLINE["x0"], geom.OUTLINE["y0"]
W = int(round((geom.OUTLINE["x1"] - X0) / PITCH)) + 1
H = int(round((geom.OUTLINE["y1"] - Y0) / PITCH)) + 1
ROUTE_LAYERS = [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In3_Cu, pcbnew.B_Cu]
ALL_LAYERS = geom.CU
BLOCK = -1

# class -> (track width, clearance, via diameter, via drill)
CLASSES = {
    "bus":    (1.0, 0.35, 0.6, 0.3),
    "busleg": (0.2, 0.35, 0.45, 0.2),     # the bus nets' 0.2 mm data legs: new bus copper keeps 0.35 from the other leg too (QE R3-F2)
    "power":  (0.5, 0.25, 0.6, 0.3),
    "pi5v":   (1.0, 0.25, 0.6, 0.3),
    "payload": (0.6, 0.25, 0.5, 0.25),
    "rail":   (0.2, 0.15, 0.45, 0.2),     # 3V3 / 1V8 / VDDIO / AVDD / LED_VDD: the brief's "everything else" width
    "signal": (0.2, 0.15, 0.45, 0.2),
    "data":   (0.2, 0.15, 0.45, 0.2),
    "thin":   (0.15, 0.15, 0.45, 0.2),    # pad-field escapes only (BRIEF §5)
    "gnd":    (0.2, 0.15, 0.45, 0.2),     # GND stitching: a 0.2 mm link and a 0.45 via into the plane (signal sizes)
    # an ADIN pair as one virtual track: two 0.2 mm tracks at 0.4 mm pitch (the mote's 0.2 mm gap) = 0.6 mm wide; a layer
    # change is a swap via (two 0.45/0.2 vias 0.6 mm apart along the track, the tracks swapping sides) inside an r 1.05 disk
    "pair":   (0.6, 0.15, 2.1, 0.2),
}
PAIR_W, PAIR_PITCH, PAIR_VIA, PAIR_VIA_DRILL = 0.2, 0.4, 0.45, 0.2
FINE_PAD = 0.35          # mm: pads narrower than this (BGA balls, 0.5 mm pitch pins) may leave by a 0.15 mm escape (BRIEF §5)
# The swap via figure, in (along, lateral) coordinates of the via centre c (along = the travel direction u, lateral =
# +1 to the left). The "near" track (the one on side s) dives at c - 0.3u; the "far" track swings out to lateral -0.5s,
# passes the near via and dives at c + 0.3u; on the new layer the near track leaves on the far side and the far track on
# the near side (the swap). Every segment keeps >= 0.175 mm from the other net's via; the figure spans +-0.9 along,
# -0.6 ... +0.3 lateral (times s), so it needs room on one side only, and either side may be used (s = +-1).
SWAP_NEAR_A = [(-0.8, 0.2), (-0.3, 0.0)]                                   # layer A, near track (lateral x s)
SWAP_FAR_A = [(-0.8, -0.2), (-0.6, -0.5), (0.0, -0.5), (0.3, 0.0)]        # layer A, far track
SWAP_NEAR_B = [(-0.3, 0.0), (0.0, -0.5), (0.6, -0.5), (0.8, -0.2)]         # layer B, near track leaves on the far side
SWAP_FAR_B = [(0.3, 0.0), (0.8, 0.2)]                                      # layer B, far track leaves on the near side
SWAP_RUN = 10                                                              # straight cells before and after: the figure spans 0.8 mm and a 90° turn right after it keeps its inner corner 0.2 mm behind the turn
STRAIGHT_RUN = 3                                                           # straight cells before and after a straight via pair (two 0.45 vias at ±0.325)
EXIT_STRAIGHT = 2                                                          # further same-direction steps after any figure's run before the path may turn
PAD_SPLAY = 0.2                                                            # mm of straight approach over which the pair spreads from ±0.2 to the transformer pads' pitch (0.125 mm lateral: 32°)


def net_class(name):
    n = name.rsplit("/", 1)[-1]
    if n in ("BM1_P", "BM1_N", "BM2_P", "BM2_N"):
        return "bus"
    if n in ("VBUS", "P_IN"):
        return "power"
    if n in ("5V_PI", "PI_5V"):
        return "pi5v"
    if n == "VBUS_OUT":
        return "payload"
    if n in ("3V3", "1V8", "ADIN_AVDD", "ADIN_VDDIO", "GND", "ADIN_LED_VDD"):
        return "rail"
    if "DATA" in n:
        return "data"
    return "signal"


def cell(x, y):
    return int(round((x - X0) / PITCH)), int(round((y - Y0) / PITCH))


def pos(cx, cy):
    return X0 + cx * PITCH, Y0 + cy * PITCH


def disk(r_cells, strict=False):
    out = []
    for dx in range(-r_cells, r_cells + 1):
        for dy in range(-r_cells, r_cells + 1):
            d2 = dx * dx + dy * dy
            if (d2 < r_cells * r_cells) if strict else (d2 <= r_cells * r_cells + 0.25):
                out.append((dx, dy))
    return out


def seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / L2
    t = 0.0 if t < 0 else (1.0 if t > 1 else t)
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def poly_dist(px, py, rings):
    """Signed distance from a point to a polygon given as rings of (x, y): negative inside (even-odd)."""
    best = 1e9
    inside = False
    for ring in rings:
        n = len(ring)
        for i in range(n):
            ax, ay = ring[i]
            bx, by = ring[(i + 1) % n]
            d = seg_dist(px, py, ax, ay, bx, by)
            if d < best:
                best = d
            if (ay > py) != (by > py):
                x = ax + (py - ay) * (bx - ax) / (by - ay)
                if x > px:
                    inside = not inside
    return -best if inside else best


class Grid:
    # dilation radii in cells: a new item with half width + clearance ≤ ρ_r = 0.1 r − 0.07 uses map r (see radius_for)
    RADII = [3, 4, 5, 6, 7, 10, 13]
    # cross-class maps (net-coded like dil, so a net's own copper never blocks it): bus copper seen by non-bus routes at
    # 0.35, power-class copper seen by signal-class routes at 0.25, non-bus copper seen by bus routes at 0.35
    BRADII = [5, 6, 7, 8, 10, 15]
    PRADII = [4, 5, 6, 7, 14]
    NRADII = [5, 7, 8, 10]
    HOLE_GAP = 0.25     # KiCad's hole-to-hole minimum; a new via's drill is at most 0.3 mm
    NEW_DRILL = 0.3

    def __init__(self, board, merge=None):
        """merge: {net name: other net name} stamped and routed as ONE net (an ADIN pair's N as its P): the per-cell
        maps hold one net code, so a cell near both pins of a pair would otherwise read BLOCK and the pair could not
        start between its own pins. The two nets have no other copper, so nothing else routes against them alone."""
        self.board = board
        self.occ = {l: [0] * (W * H) for l in ALL_LAYERS}
        self.radii = list(self.RADII)
        self.rho = {r: 0.1 * r - 0.07 for r in self.radii}
        self.dil = {r: {l: [0] * (W * H) for l in ALL_LAYERS} for r in self.radii}
        # Cross-class clearance (QE S7.b R2-F2): the brief's clearance is a property of BOTH items. dilk[r][layer] holds a
        # bitmask of the kinds of copper within ρ_r of the cell: 1 = bus-net copper, 2 = power-class copper (power / pi5v /
        # payload nets), 4 = anything that is not a bus net. A non-bus route keeps bit 1 clear within its 0.35 mm
        # radius and bit 2 within its 0.25 mm radius; a bus route keeps bit 4 clear within its 0.35 mm radius.
        self.xmaps = {}
        for name, radii in (("bus", self.BRADII), ("pwr", self.PRADII), ("nonbus", self.NRADII)):
            self.xmaps[name] = {r: {l: [0] * (W * H) for l in ALL_LAYERS} for r in radii}
        self.xrho = {r: 0.1 * r - 0.07 for r in set(self.BRADII) | set(self.PRADII) | set(self.NRADII)}
        self.made = {}           # net name -> board items this grid created
        self.hole = [0] * (W * H)   # cells where a new via centre would put its drill < 0.25 mm from an existing hole
        self.exclude_ids = set()    # uuids of items no route may start from or end on (the Kelvin sense traces)
        self.same = set()           # extra net codes treated as "own net" during one route (a pair's second net)
        self.netcode = {}
        for i in range(board.GetNetInfo().GetNetCount()):
            ni = board.GetNetInfo().GetNetItem(i)
            if ni:
                self.netcode[ni.GetNetname()] = ni.GetNetCode()
        for a, b2 in (merge or {}).items():
            self.netcode[a] = self.netcode[b2]
        self.bus_codes = {code for name, code in self.netcode.items() if net_class(name) == "bus"}
        self.kind = {code: (1 if net_class(name) == "bus" else (2 | 4 if net_class(name) in ("power", "pi5v", "payload") else 4))
                     for name, code in self.netcode.items()}
        self.maxrho = max(self.rho.values())
        self._stamp_board()

    # ---- stamping (exact distances) ------------------------------------------------------------------------
    def _mark_dist(self, layers, cx, cy, d, net, kind=None):
        """Mark one cell at distance d (mm, ≤ 0 inside) from an item of `net` on `layers`; kind = the cross-class
        bits to set (default: the net's own kind; 0 for a keep-out that is not copper)."""
        if not (0 <= cx < W and 0 <= cy < H):
            return
        i = cy * W + cx
        bit = (self.kind.get(net, 4) if net != BLOCK else 7) if kind is None else kind
        for l in layers:
            if d <= 1e-9:
                o = self.occ[l]
                if o[i] == 0:
                    o[i] = net
                elif o[i] != net:
                    o[i] = BLOCK
            for r in self.radii:
                if d < self.rho[r]:
                    dd = self.dil[r][l]
                    if dd[i] == 0:
                        dd[i] = net
                    elif dd[i] != net:
                        dd[i] = BLOCK
            for name, b in (("bus", 1), ("pwr", 2), ("nonbus", 4)):
                if not bit & b:
                    continue
                for r, mp in self.xmaps[name].items():
                    if d < self.xrho[r]:
                        dd = mp[l]
                        if dd[i] == 0:
                            dd[i] = net
                        elif dd[i] != net:
                            dd[i] = BLOCK

    def _cells_in(self, x0, y0, x1, y1):
        c0, c1 = cell(x0 - self.maxrho, y0 - self.maxrho), cell(x1 + self.maxrho, y1 + self.maxrho)
        for cy in range(max(c0[1], 0), min(c1[1], H - 1) + 1):
            for cx in range(max(c0[0], 0), min(c1[0], W - 1) + 1):
                yield cx, cy

    def stamp_hole(self, x, y, drill):
        """Forbid new via centres closer than drill/2 + 0.15 + 0.25 (+ half a cell) to this hole (same net too)."""
        cx, cy = cell(x, y)
        r = int(math.ceil((drill / 2 + self.NEW_DRILL / 2 + self.HOLE_GAP + 0.07) / PITCH))
        for dx, dy in disk(r, strict=True):
            X, Y = cx + dx, cy + dy
            if 0 <= X < W and 0 <= Y < H:
                self.hole[Y * W + X] = 1

    def stamp_disk(self, layers, x, y, radius, net, inflate=0.0, kind=None):
        for cx, cy in self._cells_in(x - radius, y - radius, x + radius, y + radius):
            px, py = pos(cx, cy)
            self._mark_dist(layers, cx, cy, math.hypot(px - x, py - y) - radius, net, kind)

    def stamp_segment(self, layer, a, b, width, net, inflate=0.0):
        hw = width / 2
        for cx, cy in self._cells_in(min(a[0], b[0]) - hw, min(a[1], b[1]) - hw, max(a[0], b[0]) + hw, max(a[1], b[1]) + hw):
            px, py = pos(cx, cy)
            self._mark_dist([layer], cx, cy, seg_dist(px, py, a[0], a[1], b[0], b[1]) - hw, net)

    def stamp_rings(self, layers, rings, net):
        xs = [p[0] for r in rings for p in r]
        ys = [p[1] for r in rings for p in r]
        if not xs:
            return
        for cx, cy in self._cells_in(min(xs), min(ys), max(xs), max(ys)):
            px, py = pos(cx, cy)
            self._mark_dist(layers, cx, cy, poly_dist(px, py, rings), net)

    @staticmethod
    def poly_rings(poly, hole_rings=True):
        rings = []
        for i in range(poly.OutlineCount()):
            o = poly.Outline(i)
            rings.append([(mm(o.CPoint(k).x), mm(o.CPoint(k).y)) for k in range(o.PointCount())])
            if hole_rings:
                for h in range(poly.HoleCount(i)):
                    hh = poly.Hole(i, h)
                    rings.append([(mm(hh.CPoint(k).x), mm(hh.CPoint(k).y)) for k in range(hh.PointCount())])
        return rings

    def stamp_poly(self, layers, poly, net, inflate=0.0):
        self.stamp_rings(layers, self.poly_rings(poly), net)

    def stamp_pad(self, pad, layers, net):
        """Exact distance for the common pad shapes (rect, rounded rect, oval, circle); polygon otherwise."""
        try:                       # KiCad 9 padstacks take a layer
            shape, size = pad.GetShape(pcbnew.F_Cu), pad.GetSize(pcbnew.F_Cu)
        except TypeError:
            shape, size = pad.GetShape(), pad.GetSize()
        w, h = mm(size.x), mm(size.y)
        x, y = mm(pad.GetPosition().x), mm(pad.GetPosition().y)
        ang = math.radians(pad.GetOrientationDegrees())
        ca, sa = math.cos(ang), math.sin(ang)
        if shape == pcbnew.PAD_SHAPE_CIRCLE:
            self.stamp_disk(layers, x, y, w / 2, net)
            return
        if shape in (pcbnew.PAD_SHAPE_RECT, pcbnew.PAD_SHAPE_ROUNDRECT, pcbnew.PAD_SHAPE_OVAL):
            if shape == pcbnew.PAD_SHAPE_ROUNDRECT:
                try:
                    rc = mm(pad.GetRoundRectCornerRadius(pcbnew.F_Cu))
                except TypeError:
                    rc = mm(pad.GetRoundRectCornerRadius())
            elif shape == pcbnew.PAD_SHAPE_OVAL:
                rc = min(w, h) / 2
            else:
                rc = 0.0
            hx, hy = w / 2 - rc, h / 2 - rc
            R = math.hypot(w, h) / 2
            for cx, cy in self._cells_in(x - R, y - R, x + R, y + R):
                px, py = pos(cx, cy)
                # into the pad frame (KiCad rotates counter-clockwise on screen by +orientation)
                dx, dy = px - x, py - y
                lx = dx * ca - dy * sa
                ly = dx * sa + dy * ca
                qx, qy = max(abs(lx) - hx, 0.0), max(abs(ly) - hy, 0.0)
                d = math.hypot(qx, qy) - rc
                if qx == 0 and qy == 0:
                    d = -min(hx - abs(lx), hy - abs(ly)) - rc
                self._mark_dist(layers, cx, cy, d, net)
            return
        poly = pad.GetEffectivePolygon(layers[0], pcbnew.ERROR_INSIDE)
        self.stamp_rings(layers, self.poly_rings(poly), net)

    def _stamp_board(self):
        b = self.board
        # board edge: a distance-to-outside map (cells), checked against each class's half width in free() / via_free()
        o = geom.OUTLINE
        m = geom.EDGE_CLEARANCE
        x0, x1, y0, y1, r = o["x0"] + m, o["x1"] - m, o["y0"] + m, o["y1"] - m, o["r"] - m
        self.edge = [99] * (W * H)
        outside = []
        for cy in range(H):
            for cx in range(W):
                px, py = pos(cx, cy)
                ok = x0 <= px <= x1 and y0 <= py <= y1
                if ok and r > 0:
                    qx = x0 + r if px < x0 + r else (x1 - r if px > x1 - r else None)
                    qy = y0 + r if py < y0 + r else (y1 - r if py > y1 - r else None)
                    if qx is not None and qy is not None and (px - qx) ** 2 + (py - qy) ** 2 > r * r:
                        ok = False
                if not ok:
                    i = cy * W + cx
                    self.edge[i] = 0
                    for l in ALL_LAYERS:
                        self.occ[l][i] = BLOCK
                        for rr in self.radii:
                            self.dil[rr][l][i] = BLOCK
                    outside.append((cx, cy))
        ring = [(cx, cy) for cx, cy in outside if any(0 <= cx + dx < W and 0 <= cy + dy < H and self.edge[(cy + dy) * W + cx + dx] == 99
                                                      for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        for cx, cy in ring:
            for dx, dy in disk(12):
                x, y = cx + dx, cy + dy
                if 0 <= x < W and 0 <= y < H:
                    d = int(math.ceil(math.hypot(dx, dy)))
                    j = y * W + x
                    if d < self.edge[j]:
                        self.edge[j] = d
        # pads
        for f in b.GetFootprints():
            for p in f.Pads():
                net = self.netcode.get(p.GetNetname(), 0) if p.GetNetname() else BLOCK
                layers = [l for l in ALL_LAYERS if p.IsOnLayer(l)]
                if p.GetDrillSize().x > 0:
                    layers = ALL_LAYERS
                if layers:
                    self.stamp_pad(p, layers, net)
                if p.GetDrillSize().x > 0:
                    self.stamp_disk(ALL_LAYERS, mm(p.GetPosition().x), mm(p.GetPosition().y),
                                    mm(max(p.GetDrillSize().x, p.GetDrillSize().y)) / 2 + 0.25, net if net else BLOCK)
                    self.stamp_hole(mm(p.GetPosition().x), mm(p.GetPosition().y), mm(max(p.GetDrillSize().x, p.GetDrillSize().y)))
        # footprint rule areas (Sofar's Hole_M3: r 3.9 no tracks / no vias on the outer layers, r 3 no pour): tracks are
        # blocked on the area's own copper layers where it forbids them; a no-pour-only area is the zone filler's business
        for f in b.GetFootprints():
            for z in f.Zones():
                if z.GetIsRuleArea() and (z.GetDoNotAllowTracks() or z.GetDoNotAllowVias()):
                    layers = [l for l in z.GetLayerSet().Seq() if l in ALL_LAYERS]
                    self.stamp_poly(layers, pcbnew.SHAPE_POLY_SET(z.Outline()), BLOCK)
        # fiducials: their solder-mask aperture (a circle on F/B.Mask) must hold no other copper (DRC mask bridge)
        for f in b.GetFootprints():
            for g_ in f.GraphicalItems():
                if g_.GetClass() == "PCB_SHAPE" and g_.GetShape() == pcbnew.SHAPE_T_CIRCLE and g_.GetLayer() in (pcbnew.F_Mask, pcbnew.B_Mask):
                    cu = pcbnew.F_Cu if g_.GetLayer() == pcbnew.F_Mask else pcbnew.B_Cu
                    c = geom.xy(g_.GetCenter())
                    self.stamp_disk([cu], c[0], c[1], mm(g_.GetRadius()), BLOCK)
        # footprint copper graphics (the net-tie bridges of JP1/JP2): blocked for every net
        for f in b.GetFootprints():
            for s in f.GraphicalItems():
                if s.GetClass() == "PCB_SHAPE" and s.GetLayer() in ALL_LAYERS:
                    poly = pcbnew.SHAPE_POLY_SET()
                    s.TransformShapeToPolygon(poly, s.GetLayer(), 0, MM(0.01), pcbnew.ERROR_INSIDE)
                    self.stamp_poly([s.GetLayer()], poly, BLOCK)
        # tracks, arcs, vias
        for t in b.GetTracks():
            net = self.netcode.get(t.GetNetname(), BLOCK)
            cls = t.GetClass()
            if cls == "PCB_VIA":
                self.stamp_disk(ALL_LAYERS, mm(t.GetPosition().x), mm(t.GetPosition().y), mm(t.GetWidth(pcbnew.F_Cu)) / 2, net)
                self.stamp_hole(mm(t.GetPosition().x), mm(t.GetPosition().y), mm(t.GetDrillValue()))
            elif cls == "PCB_ARC":
                poly = pcbnew.SHAPE_POLY_SET()
                t.TransformShapeToPolygon(poly, t.GetLayer(), 0, MM(0.02), pcbnew.ERROR_INSIDE)
                self.stamp_poly([t.GetLayer()], poly, net)
            else:
                self.stamp_segment(t.GetLayer(), geom.xy(t.GetStart()), geom.xy(t.GetEnd()), mm(t.GetWidth()), net)
        # zones: the insert pull-backs (circles r 4.8, blocked for every net but the insert's) and copied island pours
        for z in b.Zones():
            layers = [l for l in z.GetLayerSet().Seq() if l in ALL_LAYERS]
            if z.GetIsRuleArea():
                name = z.GetZoneName()
                for ref, n in geom.INSERT_NET.items():
                    if ref in name:
                        net = self.netcode.get("/Top-Level Schematic/" + n, BLOCK)
                        x, y = geom.INSERTS[ref]
                        # the pull-back is a keep-out, not copper: no clearance to it (the maps add half width + 0.15 +
                        # the cell margin, so the disk is drawn 0.15 smaller) and no cross-class 0.35 on top of the 4.8 mm
                        self.stamp_disk(layers, x, y, geom.INSERT_KEEPOUT_R - 0.15, net, kind=0)
            # filled zones (planes, island pours) are not obstacles: the fill keeps clearance around other copper
        # keep outer-layer copper away from the standoff / housing holes (BRIEF §3: nothing within r 3.0 / 3.5)
        for ref, (x, y) in geom.PI_HOLES.items():
            self.stamp_disk([pcbnew.F_Cu, pcbnew.B_Cu], x, y, 3.0, BLOCK)
        for ref, (x, y) in geom.HOUSING_HOLES.items():
            self.stamp_disk([pcbnew.F_Cu, pcbnew.B_Cu], x, y, 3.5, BLOCK)

    # ---- queries ----------------------------------------------------------------------------------------------
    def kradius(self, name, width, clearance):
        r = int(math.ceil((width / 2 + clearance + 0.07) / PITCH))
        return min(x for x in self.xmaps[name] if x >= r)

    def xradii(self, net, width, clearance):
        """[(map, radius)] the cross-class checks for a new item of this net / width / class clearance."""
        if net in self.bus_codes:
            return [(self.xmaps["nonbus"], self.kradius("nonbus", width, 0.35))]
        out = [(self.xmaps["bus"], self.kradius("bus", width, 0.35))]
        if clearance < 0.25:
            out.append((self.xmaps["pwr"], self.kradius("pwr", width, 0.25)))
        return out

    def free(self, layer, cx, cy, r, net, hw_cells=2, xr=()):
        i = cy * W + cx
        if self.edge[i] <= hw_cells:          # copper would reach within the edge clearance
            return False
        v = self.dil[r][layer][i]
        if not (v == 0 or v == net or v in self.same):
            return False
        for mp, rk in xr:
            v = mp[rk][layer][i]
            if not (v == 0 or v == net or v in self.same):
                return False
        return True

    def via_free(self, cx, cy, r, net, hw_cells=3, xr=(), dia=None, clr=None, drill=None):
        """dia / clr: the via's real diameter and class clearance for the exact near-miss check (session 2, REPORT §6
        #2: the check used to derive a diameter from the map radius, 0.03 mm under the class's 0.45, and let a 3V3
        via sit 0.14 mm from R21's pad). drill: the via's real drill; the hole map assumes NEW_DRILL (0.3) plus the
        cell margin, so a cell it blocks is re-checked exactly with the real drill when it is given."""
        if self.edge[cy * W + cx] <= hw_cells:
            return False
        if self.hole[cy * W + cx] and (drill is None or not self.hole_free_exact(cx, cy, drill)):
            return False
        i = cy * W + cx
        near_miss = False
        for l in ALL_LAYERS:
            v = self.dil[r][l][i]
            if not (v == 0 or v == net or v in self.same):
                # blocked on the map: when the next smaller map is free, the real geometry decides (the maps carry a
                # 0.07 mm cell margin and round up to 0.1 mm; a via has few candidates, so an exact check is cheap)
                r1 = max((x for x in self.radii if x < r), default=None)
                v1 = self.dil[r1][l][i] if r1 is not None else BLOCK
                if r1 is None or not (v1 == 0 or v1 == net or v1 in self.same):
                    return False
                near_miss = True
            for mp, rk in xr:
                v = mp[rk][l][i]
                if not (v == 0 or v == net or v in self.same):
                    return False
        if near_miss:
            return self.via_free_exact(cx, cy, r, net, dia, clr)
        return True

    def hole_free_exact(self, cx, cy, drill):
        """Hole-to-hole: the new drill's edge ≥ HOLE_GAP from every existing drill's edge (pads and vias), exactly."""
        if not hasattr(self, "_items"):
            self.via_free_exact(0, 0, self.radii[0], 0)        # builds the item list
        x, y = pos(cx, cy)
        reach = drill / 2 + self.HOLE_GAP + 3.0
        for code, layers, item, bb in self._items:
            cls = item.GetClass()
            if cls == "PCB_VIA":
                d_other = mm(item.GetDrillValue())
                px, py = mm(item.GetPosition().x), mm(item.GetPosition().y)
            elif cls == "PAD" and item.GetDrillSize().x > 0:
                d_other = mm(max(item.GetDrillSize().x, item.GetDrillSize().y))
                px, py = mm(item.GetPosition().x), mm(item.GetPosition().y)
            else:
                continue
            if abs(px - x) > reach or abs(py - y) > reach:
                continue
            if math.hypot(px - x, py - y) - d_other / 2 - drill / 2 < self.HOLE_GAP - 1e-6:
                return False
        return True

    def via_free_exact(self, cx, cy, r, net, dia=None, clr=None):
        """Exact clearance of a via at the cell to every other-net copper item within reach, with pcbnew's shapes:
        diameter `dia` and clearance `clr` when given (the class's), else derived from the map radius r (diameter ≈
        2·(ρ_r − 0.15), clearance ρ_r − dia/2 − 0.07)."""
        if not hasattr(self, "_items"):
            self._items = []
            for f in self.board.GetFootprints():
                for p in f.Pads():
                    code = self.netcode.get(p.GetNetname(), 0) if p.GetNetname() else BLOCK
                    layers = ALL_LAYERS if p.GetDrillSize().x > 0 else [l for l in ALL_LAYERS if p.IsOnLayer(l)]
                    if not layers:
                        continue
                    bb = p.GetBoundingBox()
                    self._items.append((code, layers, p, (mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom()))))
            for t in self.board.GetTracks():
                code = self.netcode.get(t.GetNetname(), BLOCK)
                layers = ALL_LAYERS if t.GetClass() == "PCB_VIA" else [t.GetLayer()]
                bb = t.GetBoundingBox()
                self._items.append((code, layers, t, (mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom()))))
        x, y = pos(cx, cy)
        rho = self.rho[r]
        if net == 0:
            return True
        if dia is None:
            dia = 2 * (rho - 0.15 - 0.07)      # the via diameter this map radius stands for (radius_for rounds up)
        if clr is None:
            clr = rho - dia / 2 - 0.07
        for ref, (ix, iy) in geom.INSERTS.items():      # the insert pull-backs are not items: no other-net copper within r 4.8
            if net != self.netcode.get("/Top-Level Schematic/" + geom.INSERT_NET[ref]) and math.hypot(x - ix, y - iy) - dia / 2 < geom.INSERT_KEEPOUT_R + 0.01:
                return False
        reach = rho + 0.3
        circle = pcbnew.SHAPE_CIRCLE(V(x, y), MM(dia / 2))
        for code, layers, item, bb in self._items:
            if code == net or code in self.same:
                continue
            if bb[0] > x + reach or bb[2] < x - reach or bb[1] > y + reach or bb[3] < y - reach:
                continue
            l = layers[0]
            if item.GetClass() == "PCB_VIA" or (item.GetClass() == "PAD" and item.GetDrillSize().x > 0):
                shape = item.GetEffectiveShape(l)
            else:
                shape = item.GetEffectiveShape(l)
            if shape.Collide(circle, MM(clr) - 1):
                return False
        return True

    def seg_free_exact(self, layer, a, b, width, net, clr):
        """Exact clearance of a track segment a-b (mm) of `width` on `layer` to every other-net copper item, with
        pcbnew's shapes (for fixed geometry such as a pair's pin stubs, where the maps' 0.07 mm cell margin is
        needlessly conservative)."""
        if not hasattr(self, "_items"):
            self.via_free_exact(0, 0, self.radii[0], net)       # builds the item list
        shape = pcbnew.SHAPE_SEGMENT(V(*a), V(*b), MM(width))
        x0, y0 = min(a[0], b[0]) - width - clr, min(a[1], b[1]) - width - clr
        x1, y1 = max(a[0], b[0]) + width + clr, max(a[1], b[1]) + width + clr
        for code, layers, item, bb in self._items:
            if code == net or code in self.same or layer not in layers:
                continue
            if bb[0] > x1 or bb[2] < x0 or bb[1] > y1 or bb[3] < y0:
                continue
            if item.GetEffectiveShape(layer).Collide(shape, MM(clr) - 1):
                return False
        for ref, (ix, iy) in geom.INSERTS.items():
            if net != self.netcode.get("/Top-Level Schematic/" + geom.INSERT_NET[ref]) and seg_dist(ix, iy, a[0], a[1], b[0], b[1]) - width / 2 < geom.INSERT_KEEPOUT_R + 0.01:
                return False
        return True

    def radius_for(self, width, clearance):
        # map r covers half width + clearance up to 0.1 r − 0.07 (the 0.07 absorbs the cell quantisation)
        r = int(math.ceil((width / 2 + clearance + 0.07) / PITCH))
        return min(x for x in self.radii if x >= r)

    # ---- A* ---------------------------------------------------------------------------------------------------
    def route(self, net, starts, goals, cls, layers=None, max_nodes=400000, via_cost=12.0, via_ok=True, soft=(), layer_cost=None):
        """starts/goals: {(layer, cx, cy)} sets. Returns a path [(layer, cx, cy), ...] or None.
        soft: goal cells that may be entered by an orthogonal step without the clearance test — the destination
        PAD's own copper (a bus leg enters T1/T2 pad 6 although pad 7 sits 0.24 mm away, Sofar's geometry).
        layer_cost: {layer: multiplier} for the step cost (corridor preference; 1.0 default)."""
        soft_cells = {}
        for l, cx, cy in soft:
            soft_cells.setdefault((cx, cy), set()).add(l)
        width, clear, vdia, vdrill = CLASSES[cls]
        rt = self.radius_for(width, clear)
        rv = self.radius_for(vdia, clear)
        hwt = int(math.ceil(width / 2 / PITCH))
        hwv = int(math.ceil(vdia / 2 / PITCH))
        xrt = self.xradii(net, width, clear)
        xrv = self.xradii(net, vdia, clear)
        layers = layers or ROUTE_LAYERS
        lc = {l: (layer_cost or {}).get(l, 1.0) for l in layers}
        hmin = min(lc.values())
        goal_cells = {}
        for l, cx, cy in goals:
            goal_cells.setdefault((cx, cy), set()).add(l)
        gx = [c[0] for c in goal_cells]
        gy = [c[1] for c in goal_cells]
        gminx, gmaxx, gminy, gmaxy = min(gx), max(gx), min(gy), max(gy)

        def h(cx, cy):
            dx = max(gminx - cx, 0, cx - gmaxx)
            dy = max(gminy - cy, 0, cy - gmaxy)
            return math.hypot(dx, dy) * hmin
        open_heap = []
        best = {}
        parent = {}
        for s in starts:
            if s[0] in layers:
                best[s] = 0.0
                heapq.heappush(open_heap, (h(s[1], s[2]), 0.0, s))
        steps = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0)]
        if cls != "thin":      # a 0.15 mm track next to a via keeps 0.15 mm only when it moves orthogonally
            steps += [(1, 1, 1.4142), (1, -1, 1.4142), (-1, 1, 1.4142), (-1, -1, 1.4142)]
        n = 0
        while open_heap:
            f, g, cur = heapq.heappop(open_heap)
            if g > best.get(cur, 1e18):
                continue
            l, cx, cy = cur
            if (cx, cy) in goal_cells and l in goal_cells[(cx, cy)]:
                path = [cur]
                while cur in parent:
                    cur = parent[cur]
                    path.append(cur)
                return path[::-1]
            n += 1
            if n > max_nodes:
                return None
            for dx, dy, c in steps:
                nx, ny = cx + dx, cy + dy
                if not (0 <= nx < W and 0 <= ny < H):
                    continue
                is_soft = not (dx and dy) and (nx, ny) in soft_cells and l in soft_cells[(nx, ny)]
                if not is_soft and not self.free(l, nx, ny, rt, net, hwt, xrt):
                    continue
                if dx and dy and not (self.free(l, cx + dx, cy, rt, net, hwt, xrt) and self.free(l, cx, cy + dy, rt, net, hwt, xrt)):
                    continue
                nxt = (l, nx, ny)
                ng = g + c * lc[l]
                if ng < best.get(nxt, 1e18):
                    best[nxt] = ng
                    parent[nxt] = cur
                    heapq.heappush(open_heap, (ng + h(nx, ny), ng, nxt))
            if via_ok and self.via_free(cx, cy, rv, net, hwv, xrv, vdia, clear, vdrill):
                for l2 in layers:
                    if l2 == l:
                        continue
                    nxt = (l2, cx, cy)
                    ng = g + via_cost
                    if ng < best.get(nxt, 1e18):
                        best[nxt] = ng
                        parent[nxt] = cur
                        heapq.heappush(open_heap, (ng + h(cx, cy), ng, nxt))
        return None

    def route_pair(self, net, starts, goals, parity, layers=None, max_nodes=1500000, via_cost=8.0, end_guard=7, sides=(1, -1), forbid=()):
        """A* for a pair's virtual track (class 'pair'). A layer change is a macro step: a straight run of n cells
        on the old layer, the via(s), a straight run of n cells on the new layer (n = SWAP_RUN for a swap via, whose
        figure spans ±0.9 mm; STRAIGHT_RUN for a straight via pair), all of it checked free. Two consecutive figures
        are therefore ≥ (n_after + n_before) cells apart on one straight line and cannot overlap: 1.3 mm between a
        straight pair and a swap, which keeps 0.175 mm between the swap's swing and the pair's vias. (Session 1 kept
        a spacing counter in the A* state instead; a cell could be revisited with another counter value, so the path
        looped back over itself to satisfy the spacing and the two tracks crossed: QE round 1 F1 / REPORT §6 #1.)
        A swap via exchanges the two tracks' sides; the number of swaps must have the given parity (commit_pair).
        No via lies within `end_guard` cells of the start / goal cells. `forbid`: cells no step or run may enter (the
        pads' approach lane and the pins' stub, so the path cannot cross them). Returns (path, swap_cells) or
        (None, None)."""
        width, clear, vdia, vdrill = CLASSES["pair"]
        rt = self.radius_for(width, clear)
        wide = PAIR_PITCH + 0.25 + PAIR_VIA                               # two 0.45 vias at ±0.325: 1.1 mm across
        rv_str = self.radius_for(wide, clear)
        hwt = int(math.ceil(width / 2 / PITCH))
        xrt = self.xradii(net, width, clear)
        xrv_str = self.xradii(net, wide, clear)
        hwv_str = int(math.ceil(wide / 2 / PITCH))
        layers = layers or [pcbnew.F_Cu, pcbnew.In1_Cu]
        forbid = set(forbid)
        goal_cells = {}
        for l, cx, cy in goals:
            goal_cells.setdefault((cx, cy), set()).add(l)
        gx = [c[0] for c in goal_cells]
        gy = [c[1] for c in goal_cells]
        gminx, gmaxx, gminy, gmaxy = min(gx), max(gx), min(gy), max(gy)
        ends = [(cx, cy) for _, cx, cy in starts] + list(goal_cells)

        def near_end(cx, cy):
            return any(abs(cx - ex) <= end_guard and abs(cy - ey) <= end_guard for ex, ey in ends)

        def h(cx, cy):
            dx = max(gminx - cx, 0, cx - gmaxx)
            dy = max(gminy - cy, 0, cy - gmaxy)
            return math.hypot(dx, dy)

        def run_free(l, cx, cy, dx, dy, n):
            for k in range(1, n + 1):
                x, y = cx + k * dx, cy + k * dy
                if not (0 <= x < W and 0 <= y < H) or (x, y) in forbid or not self.free(l, x, y, rt, net, hwt, xrt):
                    return False
                if dx and dy and not (self.free(l, x - dx, y, rt, net, hwt, xrt) and self.free(l, x, y - dy, rt, net, hwt, xrt)):
                    return False
            return True
        rt1 = self.radius_for(PAIR_W, clear)                 # one 0.2 mm track of the figure
        hwt1 = int(math.ceil(PAIR_W / 2 / PITCH))
        xrt1 = self.xradii(net, PAIR_W, clear)
        rv1 = self.radius_for(PAIR_VIA, clear)
        hwv1 = int(math.ceil(PAIR_VIA / 2 / PITCH))
        xrv1 = self.xradii(net, PAIR_VIA, clear)

        def swap_free(la, lb, cx, cy, dx, dy, side):
            """The swap figure at cell (cx, cy) with travel direction (dx, dy), its swing on `side` (+1 left): the two
            vias and every track segment of the figure checked cell by cell at the 0.2 mm track's radius."""
            d = math.hypot(dx, dy)
            ux, uy = dx / d, dy / d
            nx, ny = uy * side, -ux * side
            x0, y0 = pos(cx, cy)

            def at(along, lat):
                return (x0 + along * ux + lat * nx, y0 + along * uy + lat * ny)
            for along in (-0.3, 0.3):
                vx, vy = cell(*at(along, 0.0))
                if not self.via_free(vx, vy, rv1, net, hwv1, xrv1, PAIR_VIA, clear, PAIR_VIA_DRILL):
                    return False
            for layer, figs in ((la, (SWAP_NEAR_A, SWAP_FAR_A)), (lb, (SWAP_NEAR_B, SWAP_FAR_B))):
                for fig in figs:
                    for (a0, l0), (a1, l1) in zip(fig, fig[1:]):
                        p0, p1 = at(a0, l0), at(a1, l1)
                        n_ = max(1, int(geom.dist(p0, p1) / (PITCH / 2)))
                        for k in range(n_ + 1):
                            qx, qy = cell(p0[0] + (p1[0] - p0[0]) * k / n_, p0[1] + (p1[1] - p0[1]) * k / n_)
                            if not (0 <= qx < W and 0 <= qy < H) or (qx, qy) in forbid or not self.free(layer, qx, qy, rt1, net, hwt1, xrt1):
                                return False
            return True
        steps = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0), (1, 1, 1.4142), (1, -1, 1.4142), (-1, 1, 1.4142), (-1, -1, 1.4142)]
        macros = ((False, STRAIGHT_RUN, 0),) + tuple((True, SWAP_RUN, sd) for sd in sides)
        open_heap, best, parent = [], {}, {}
        tick = 0          # heap tiebreak: the state tuples hold None / tuples and must never be compared
        # state: (layer, cx, cy, swap parity, exit): exit = (dx, dy, k), the direction of the macro this cell was reached
        # by and the number of same-direction steps still owed, else None. The EXIT_STRAIGHT steps after a figure's run
        # continue straight and place no figure, then the first free step may not turn back past 90°: a path that turned
        # 90° right after a figure put the next figure's vias 0.48 mm from the last one's, and one that turned back ran
        # over the figure it had just left (the defects behind QE round 1 F1 / REPORT §6 #1).
        for s in starts:
            if s[0] in layers:
                st = (s[0], s[1], s[2], 0, None)
                best[st] = 0.0
                heapq.heappush(open_heap, (h(s[1], s[2]), 0.0, tick, st))
                tick += 1
        n = 0
        found = None
        while open_heap:
            f, g, _, cur = heapq.heappop(open_heap)
            if g > best.get(cur, 1e18):
                continue
            l, cx, cy, par, ex = cur
            if (cx, cy) in goal_cells and l in goal_cells[(cx, cy)] and par == parity:
                found = cur
                break
            n += 1
            if n > max_nodes:
                return None, None
            for dx, dy, c in steps:
                if ex is not None:
                    if ex[2] > 0 and (dx, dy) != (ex[0], ex[1]):
                        continue
                    if ex[2] == 0 and dx * ex[0] + dy * ex[1] < 0:
                        continue
                nx, ny = cx + dx, cy + dy
                if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in forbid:
                    continue
                if not self.free(l, nx, ny, rt, net, hwt, xrt):
                    continue
                if dx and dy and not (self.free(l, cx + dx, cy, rt, net, hwt, xrt) and self.free(l, cx, cy + dy, rt, net, hwt, xrt)):
                    continue
                nxt = (l, nx, ny, par, (ex[0], ex[1], ex[2] - 1) if (ex is not None and ex[2] > 0) else None)
                ng = g + c
                if ng < best.get(nxt, 1e18):
                    best[nxt] = ng
                    parent[nxt] = (cur, None)
                    tick += 1
                    heapq.heappush(open_heap, (ng + h(nx, ny), ng, tick, nxt))
                # a layer change nn cells ahead in this direction, straight through, and nn straight cells after it
                # (not while straight steps are still owed after the last one)
                if ex is not None and ex[2] > 0:
                    continue
                for swap, nn, side in macros:
                    vx, vy = cx + nn * dx, cy + nn * dy
                    if not (0 <= vx < W and 0 <= vy < H) or near_end(vx, vy):
                        continue
                    if not swap and not self.via_free(vx, vy, rv_str, net, hwv_str, xrv_str, wide, clear, PAIR_VIA_DRILL):
                        continue
                    if not run_free(l, cx, cy, dx, dy, nn):
                        continue
                    for l2 in layers:
                        if l2 == l or not run_free(l2, vx, vy, dx, dy, nn):
                            continue
                        if swap and not swap_free(l, l2, vx, vy, dx, dy, side):
                            continue
                        qx, qy = vx + nn * dx, vy + nn * dy
                        nxt = (l2, qx, qy, (1 - par) if swap else par, (dx, dy, EXIT_STRAIGHT))
                        ng = g + 2 * nn * c + via_cost
                        if ng < best.get(nxt, 1e18):
                            best[nxt] = ng
                            parent[nxt] = (cur, (dx, dy, nn, swap, l2, side))
                            tick += 1
                            heapq.heappush(open_heap, (ng + h(qx, qy), ng, tick, nxt))
        if found is None:
            return None, None
        path, swaps = [], {}
        cur = found
        while True:
            l, cx, cy, par, ex = cur
            if cur not in parent:
                path.append((l, cx, cy))
                break
            prev, macro = parent[cur]
            if macro is None:
                path.append((l, cx, cy))
            else:
                dx, dy, nn, swap, l2, side = macro
                pl = prev[0]
                vx, vy = prev[1] + nn * dx, prev[2] + nn * dy
                # cells after the via (new layer), the via cell on both layers, cells before it (old layer), newest first
                for k in range(nn, 0, -1):
                    path.append((l2, vx + k * dx, vy + k * dy))
                path.append((l2, vx, vy))
                path.append((pl, vx, vy))
                for k in range(1, nn):                 # newest first: the cell next to the via comes first
                    path.append((pl, vx - k * dx, vy - k * dy))
                if swap:
                    swaps[(vx, vy)] = side
            cur = prev
        return path[::-1], swaps

    @staticmethod
    def straight_cells(layer, a, b):
        """The cells of a straight run from point a to point b (mm) on one layer, a included, as path entries."""
        ca, cb = cell(*a), cell(*b)
        n = max(abs(cb[0] - ca[0]), abs(cb[1] - ca[1]))
        out = []
        for k in range(n + 1):
            out.append((layer, ca[0] + round((cb[0] - ca[0]) * k / n) if n else ca[0], ca[1] + round((cb[1] - ca[1]) * k / n) if n else ca[1]))
        return out

    @staticmethod
    def lane_cells(a, b, half_width):
        """Cells of the rectangle from a to b (mm) and `half_width` to either side (square ends: the cell at a or b
        itself is inside, the cells beyond them are not), as a set of (cx, cy): a forbidden lane."""
        x0, y0 = min(a[0], b[0]) - half_width, min(a[1], b[1]) - half_width
        x1, y1 = max(a[0], b[0]) + half_width, max(a[1], b[1]) + half_width
        c0, c1 = cell(x0, y0), cell(x1, y1)
        L = geom.dist(a, b)
        ux, uy = ((b[0] - a[0]) / L, (b[1] - a[1]) / L) if L > 1e-9 else (1.0, 0.0)
        out = set()
        for cy in range(c0[1], c1[1] + 1):
            for cx in range(c0[0], c1[0] + 1):
                px, py = pos(cx, cy)
                along = (px - a[0]) * ux + (py - a[1]) * uy
                lat = abs((px - a[0]) * uy - (py - a[1]) * ux)
                if -1e-6 <= along <= L + 1e-6 and lat <= half_width + 1e-6:
                    out.add((cx, cy))
        return out

    # ---- emitting copper --------------------------------------------------------------------------------------
    def _new_track(self, net_name, a, b, layer, width):
        if geom.dist(a, b) < 1e-6:
            return None
        ni = self.board.FindNet(net_name)
        t = pcbnew.PCB_TRACK(self.board)
        t.SetStart(V(*a))
        t.SetEnd(V(*b))
        t.SetWidth(MM(width))
        t.SetLayer(layer)
        t.SetNet(ni)
        self.board.Add(t)
        self.made.setdefault(net_name, []).append(t)
        self.stamp_segment(layer, a, b, width, self.netcode[net_name])
        if hasattr(self, "_items"):
            self._items.append((self.netcode[net_name], [layer], t, (min(a[0], b[0]) - width, min(a[1], b[1]) - width, max(a[0], b[0]) + width, max(a[1], b[1]) + width)))
        return t

    def _new_via(self, net_name, p, dia, drill):
        ni = self.board.FindNet(net_name)
        v = pcbnew.PCB_VIA(self.board)
        v.SetPosition(V(*p))
        v.SetViaType(pcbnew.VIATYPE_THROUGH)
        v.SetWidth(MM(dia))
        v.SetDrill(MM(drill))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetNet(ni)
        self.board.Add(v)
        self.made.setdefault(net_name, []).append(v)
        self.stamp_disk(ALL_LAYERS, p[0], p[1], dia / 2, self.netcode[net_name])
        self.stamp_hole(p[0], p[1], drill)
        if hasattr(self, "_items"):
            self._items.append((self.netcode[net_name], ALL_LAYERS, v, (p[0] - dia / 2, p[1] - dia / 2, p[0] + dia / 2, p[1] + dia / 2)))
        return v

    @staticmethod
    def polyline(path):
        """[(layer, (x, y)), ...] vertices of a cell path with collinear runs merged; a via = two vertices at one point."""
        out = []
        i = 0
        while i < len(path):
            j = i
            while j + 1 < len(path) and path[j + 1][0] == path[i][0]:
                j += 1
            run = path[i:j + 1]
            pts = [run[0]]
            for k in range(1, len(run)):
                if k + 1 < len(run):
                    d1 = (run[k][1] - run[k - 1][1], run[k][2] - run[k - 1][2])
                    d2 = (run[k + 1][1] - run[k][1], run[k + 1][2] - run[k][2])
                    if d1 == d2:
                        continue
                pts.append(run[k])
            out.append([(p[0], pos(p[1], p[2])) for p in pts])
            i = j + 1
        return out

    def commit(self, net_name, path, cls):
        """Turn a path into tracks and vias on the board and stamp them. Returns (tracks, vias, length_mm)."""
        width, clear, vdia, vdrill = CLASSES[cls]
        runs = self.polyline(path)
        segs, vias, length = 0, 0, 0.0
        for k, run in enumerate(runs):
            for (l, a), (_, b2) in zip(run, run[1:]):
                if self._new_track(net_name, a, b2, l, width) is not None:
                    segs += 1
                    length += geom.dist(a, b2)
            if k + 1 < len(runs):
                self._new_via(net_name, run[-1][1], vdia, vdrill)
                vias += 1
        return segs, vias, length

    def add_track(self, net_name, a, b, layer, width):
        return self._new_track(net_name, a, b, layer, width)

    def add_via(self, net_name, p, dia, drill):
        return self._new_via(net_name, p, dia, drill)

    @staticmethod
    def _left(u):
        """Left normal of a unit direction on a y-down map (facing south, left is east)."""
        return (u[1], -u[0])

    @staticmethod
    def _unit(a, b):
        d = geom.dist(a, b)
        return ((b[0] - a[0]) / d, (b[1] - a[1]) / d) if d > 1e-9 else (0.0, 0.0)

    def commit_pair(self, nets, path, pins, pads, swaps=None, dir_in=None, pad_run=0.6, splay=PAD_SPLAY, dir_out=None, start_vias=None):
        """Emit a pair from a virtual-track path (route_pair): two 0.2 mm tracks at ±0.2 mm of the centre line (the
        mote's geometry) plus the hand stubs from the two pins to the first vertex and, at the end, the approach to
        the two pads; at a layer change either a straight via pair (two vias beside the track, sides kept) or the swap
        figure (SWAP_* tables; the tracks exchange sides). nets = (P, N) names; pins / pads = ((xP, yP), (xN, yN)).
        dir_in: the pads' entry direction (unit vector). With it, the path's last vertex A' is where the approach
        begins: from A' the two tracks run straight along dir_in, spreading from ±0.2 mm to the pads' own pitch over
        `splay` mm, and reach the pitch `pad_run` mm before the pad centres (the pads' near edge), so neither track
        passes over the other net's pad (QE round 1 F1: the former approach ran the last segment from the path's end
        straight to the pad centres, which crossed the opposite pad when the path arrived diagonally). A path that
        ends on Internal 1 gets its via pair at A = B − splay, beside the approach (so the only figure the A* places
        on the way is the swap). Without dir_in the old behaviour (last vertex → pad centres) is kept for the
        blank-board tests. dir_out + start_vias ({net: (x, y)}): a path whose first cell is not on Top starts with
        a via per net straight out of its pin (the Top stub from the pin centre along dir_out to the via; the vias
        staggered along dir_out as Sofar's mote leaves U1, since two 0.45 mm vias do not fit side by side at the 0.5
        mm pin pitch), the Internal 1 legs running on at the pins' own pitch to the path's first vertex S2 and
        narrowing to ±0.2 there, so the only figure placed on the way is the swap.
        Returns {net: (tracks, vias, length_mm)}."""
        P, N = nets
        swaps = swaps or {}
        runs = self.polyline(path)
        pin_mid = ((pins[0][0] + pins[1][0]) / 2, (pins[0][1] + pins[1][1]) / 2)
        pad_mid = ((pads[0][0] + pads[1][0]) / 2, (pads[0][1] + pads[1][1]) / 2)
        u0 = self._unit(pin_mid, runs[0][0][1])
        n0 = self._left(u0)
        p_left = ((pins[0][0] - pins[1][0]) * n0[0] + (pins[0][1] - pins[1][1]) * n0[1]) > 0
        d = PAIR_PITCH / 2
        stats = {P: [0, 0, 0.0], N: [0, 0, 0.0]}

        def emit(net, a, b, layer):
            t = self._new_track(net, a, b, layer, PAIR_W)
            if t is not None:
                stats[net][0] += 1
                stats[net][2] += geom.dist(a, b)

        def dedupe(vs):
            out = []
            for v in vs:
                if not out or geom.dist(out[-1], v) > 1e-6:
                    out.append(v)
            return out

        def miter(p, n1, n2, sgn):
            k = 1 + n1[0] * n2[0] + n1[1] * n2[1]
            if k < 0.3:                                  # a reversal: fall back to the second normal
                return (p[0] + sgn * d * n2[0], p[1] + sgn * d * n2[1])
            return (p[0] + sgn * d * (n1[0] + n2[0]) / k, p[1] + sgn * d * (n1[1] + n2[1]) / k)

        def offsets(verts, sgn, u_in=None, u_out=None):
            """Offset polyline at sgn·d (miter); u_in / u_out: the travel direction before the first / after the last
            vertex when known (a swap or via pair there, or the pads' approach), else the end vertices use their
            single normal."""
            m = len(verts)
            out = []
            for i in range(m):
                n_prev = self._left(u_in) if (i == 0 and u_in) else (self._left(self._unit(verts[i - 1], verts[i])) if i > 0 else None)
                n_next = self._left(u_out) if (i == m - 1 and u_out) else (self._left(self._unit(verts[i], verts[i + 1])) if i < m - 1 else None)
                if n_prev is None:
                    n_prev = n_next
                if n_next is None:
                    n_next = n_prev
                out.append(miter(verts[i], n_prev, n_next, sgn))
            return out
        left_net, right_net = (P, N) if p_left else (N, P)
        pin_of = {P: pins[0], N: pins[1]}
        pad_of = {P: pads[0], N: pads[1]}
        entry = None          # (left point, right point, direction) the current run starts from (a via pair / swap exit)
        start_vias = start_vias if (dir_out is not None and runs[0][0][0] != pcbnew.F_Cu) else None
        if start_vias:
            S2 = runs[0][0][1]
            q = {}
            for net_ in (left_net, right_net):
                v = start_vias[net_]
                emit(net_, pin_of[net_], v, pcbnew.F_Cu)                 # the Top stub, straight out of the pin
                self._new_via(net_, v, PAIR_VIA, PAIR_VIA_DRILL)
                stats[net_][1] += 1
                along = (S2[0] - v[0]) * dir_out[0] + (S2[1] - v[1]) * dir_out[1]
                q[net_] = (v[0] + along * dir_out[0], v[1] + along * dir_out[1])      # the pin's lateral, at S2's along
                emit(net_, v, q[net_], runs[0][0][0])                     # the Internal 1 leg, still at the pins' pitch
            entry = (q[left_net], q[right_net], dir_out)
        for k, run in enumerate(runs):
            layer = run[0][0]
            verts = dedupe([q for _, q in run])
            if k == 0 and not start_vias:
                verts = dedupe([pin_mid] + verts)
            last = k + 1 == len(runs)
            u_in = entry[2] if entry else None
            if last:
                if dir_in is None:
                    verts = dedupe(verts + [pad_mid])
                    lo = offsets(verts, +1, u_in)
                    ro = offsets(verts, -1, u_in)
                    lo[-1], ro[-1] = pad_of[left_net], pad_of[right_net]
                else:
                    # the approach: ±0.2 through the path's last vertex A' (mitered with the entry direction), then
                    # straight along dir_in: on Top, ±0.2 to A = B − splay, the splay to the pads' pitch by B =
                    # pad_run before the centres, then straight into the pads. When the path ends on another layer,
                    # a via pair at A (beside the approach, ±0.325, as a straight via pair) takes it to Top and the
                    # Top tracks run from the vias straight into the pads (the pads' pitch 0.65 = the vias' 0.65).
                    lo = offsets(verts, +1, u_in, dir_in)
                    ro = offsets(verts, -1, u_in, dir_in)
                    n_in = self._left(dir_in)
                    B = (pad_mid[0] - pad_run * dir_in[0], pad_mid[1] - pad_run * dir_in[1])
                    A = (B[0] - splay * dir_in[0], B[1] - splay * dir_in[1])
                    if layer == pcbnew.F_Cu:
                        last_v = verts[-1]
                        ahead = (A[0] - last_v[0]) * dir_in[0] + (A[1] - last_v[1]) * dir_in[1]
                        for arr, net_, sg in ((lo, left_net, +1), (ro, right_net, -1)):
                            pd = pad_of[net_]
                            if ahead > 0.05:          # A lies ahead of the path's end: a straight ±0.2 run to it first
                                arr.append((A[0] + sg * d * n_in[0], A[1] + sg * d * n_in[1]))
                            arr += [(B[0] + pd[0] - pad_mid[0], B[1] + pd[1] - pad_mid[1]), pd]
                    else:
                        end_vias = []
                        for arr, net_, sg in ((lo, left_net, +1), (ro, right_net, -1)):
                            v = (A[0] + sg * 0.325 * n_in[0], A[1] + sg * 0.325 * n_in[1])
                            arr.append(v)
                            end_vias.append((net_, v, pad_of[net_]))
                u_next = None
            else:
                c = verts[-1]
                u = self._unit(verts[-2], c) if len(verts) > 1 else u_in
                nrm = self._left(u)
                swap = cell(*c) in swaps
                if swap:
                    verts = dedupe(verts[:-1] + [(c[0] - 0.8 * u[0], c[1] - 0.8 * u[1])])
                lo = offsets(verts, +1, u_in, u)
                ro = offsets(verts, -1, u_in, u)
                u_next = u
            if k == 0 and not start_vias:
                lo[0], ro[0] = pin_of[left_net], pin_of[right_net]
            if entry:
                lo, ro = [entry[0]] + lo, [entry[1]] + ro
            if not last and not swap:
                # a straight via pair at c: the two vias beside the track at ±0.325 mm; the run after it starts there
                vl = (c[0] + 0.325 * nrm[0], c[1] + 0.325 * nrm[1])
                vr = (c[0] - 0.325 * nrm[0], c[1] - 0.325 * nrm[1])
                lo, ro = lo + [vl], ro + [vr]
            elif not last:
                lo, ro = lo + [(c[0] - 0.8 * u[0] + d * nrm[0], c[1] - 0.8 * u[1] + d * nrm[1])], ro + [(c[0] - 0.8 * u[0] - d * nrm[0], c[1] - 0.8 * u[1] - d * nrm[1])]
            for a, b2 in zip(lo, lo[1:]):
                emit(left_net, a, b2, layer)
            for a, b2 in zip(ro, ro[1:]):
                emit(right_net, a, b2, layer)
            if last:
                if dir_in is not None and layer != pcbnew.F_Cu:
                    for net_, v, pd in end_vias:
                        self._new_via(net_, v, PAIR_VIA, PAIR_VIA_DRILL)
                        stats[net_][1] += 1
                        emit(net_, v, (B[0] + pd[0] - pad_mid[0], B[1] + pd[1] - pad_mid[1]), pcbnew.F_Cu)
                        emit(net_, (B[0] + pd[0] - pad_mid[0], B[1] + pd[1] - pad_mid[1]), pd, pcbnew.F_Cu)
                break
            layer_b = runs[k + 1][0][0]
            if not swap:
                self._new_via(left_net, vl, PAIR_VIA, PAIR_VIA_DRILL)
                self._new_via(right_net, vr, PAIR_VIA, PAIR_VIA_DRILL)
                stats[left_net][1] += 1
                stats[right_net][1] += 1
                entry = (vl, vr, u)
                runs[k + 1] = [(layer_b, c)] + runs[k + 1][1:]
                continue
            side = swaps[cell(*c)]
            near_net, far_net = (left_net, right_net) if side > 0 else (right_net, left_net)

            def at(along, lat):
                lat *= side
                return (c[0] + along * u[0] + lat * nrm[0], c[1] + along * u[1] + lat * nrm[1])
            for net_, fig, lay in ((near_net, SWAP_NEAR_A, layer), (far_net, SWAP_FAR_A, layer), (near_net, SWAP_NEAR_B, layer_b), (far_net, SWAP_FAR_B, layer_b)):
                for (a0, l0), (a1, l1) in zip(fig, fig[1:]):
                    emit(net_, at(a0, l0), at(a1, l1), lay)
            self._new_via(near_net, at(-0.3, 0.0), PAIR_VIA, PAIR_VIA_DRILL)
            self._new_via(far_net, at(0.3, 0.0), PAIR_VIA, PAIR_VIA_DRILL)
            stats[near_net][1] += 1
            stats[far_net][1] += 1
            left_net, right_net = right_net, left_net
            # the next run starts at the figure's exit: the new left net leaves at +0.2 of the left normal
            entry = ((c[0] + 0.8 * u[0] + d * nrm[0], c[1] + 0.8 * u[1] + d * nrm[1]),
                     (c[0] + 0.8 * u[0] - d * nrm[0], c[1] + 0.8 * u[1] - d * nrm[1]), u)
            runs[k + 1] = [(layer_b, (c[0] + 0.8 * u[0], c[1] + 0.8 * u[1]))] + runs[k + 1][1:]
        return {n: tuple(v) for n, v in stats.items()}

    def remove_made(self, net_names):
        """Take a net's emitted items off the board again (a pair whose self-check failed). The grid's maps keep
        their stamps (they read as the net's own copper, so a retry of the same net is not blocked by them)."""
        gone = []
        for name in net_names:
            for it in self.made.pop(name, []):
                self.board.Remove(it)
                gone.append(id(it))
        if hasattr(self, "_items"):
            gone = set(gone)
            self._items = [it for it in self._items if id(it[2]) not in gone]
        return len(gone)

    @staticmethod
    def pair_parity(pins, pads, first_dir, last_dir):
        """0 if P keeps its side from the pins to the pads, 1 if it must cross (one swap via)."""
        def left(u):
            return (u[1], -u[0])
        n0, n1 = left(first_dir), left(last_dir)
        p0 = (pins[0][0] - pins[1][0]) * n0[0] + (pins[0][1] - pins[1][1]) * n0[1] > 0
        p1 = (pads[0][0] - pads[1][0]) * n1[0] + (pads[0][1] - pads[1][1]) * n1[1] > 0
        return 0 if p0 == p1 else 1

    def pad_cells(self, pad, layers_only=None):
        """Cells inside a pad on its copper layers (through-hole pads: every routing layer)."""
        out = set()
        layers = ALL_LAYERS if pad.GetDrillSize().x > 0 else [l for l in ALL_LAYERS if pad.IsOnLayer(l)]
        layers = [l for l in layers if l in (layers_only or ROUTE_LAYERS)]
        if not layers:
            return out
        poly = pad.GetEffectivePolygon(layers[0], pcbnew.ERROR_INSIDE)
        bb = poly.BBox()
        c0 = cell(mm(bb.GetLeft()), mm(bb.GetTop()))
        c1 = cell(mm(bb.GetRight()), mm(bb.GetBottom()))
        for cy in range(c0[1], c1[1] + 1):
            for cx in range(c0[0], c1[0] + 1):
                px, py = pos(cx, cy)
                if poly.Contains(V(px, py)):
                    for l in layers:
                        out.add((l, cx, cy))
        return out

    def escapes(self, pad, cls, net, max_len=1.0, layers_only=None):
        """Pad-field escapes (BRIEF §5): straight 0.15 mm stubs of ≤ max_len mm from the pad centre in the four
        directions to the first cell where the class width fits. {(layer, cx, cy): (pad centre, layer)}."""
        width, clear, vdia, vdrill = CLASSES[cls]
        rt = self.radius_for(width, clear)
        hwt = int(math.ceil(width / 2 / PITCH))
        xrt = self.xradii(net, width, clear)
        r3 = self.radius_for(0.15, 0.15)
        xr3 = self.xradii(net, 0.15, 0.15)
        layers = ALL_LAYERS if pad.GetDrillSize().x > 0 else [l for l in ALL_LAYERS if pad.IsOnLayer(l)]
        layers = [l for l in layers if l in (layers_only or ROUTE_LAYERS)]
        try:
            size = pad.GetSize(pcbnew.F_Cu)
        except TypeError:
            size = pad.GetSize()
        if min(mm(size.x), mm(size.y)) > FINE_PAD:
            return {}             # a pad this big starts its class-width track itself (BRIEF §5: escapes are for pad fields)
        p = geom.xy(pad.GetPosition())
        c0 = cell(*p)
        out = {}
        for l in layers:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                for k in range(1, int(round(max_len / PITCH)) + 1):
                    cx, cy = c0[0] + k * dx, c0[1] + k * dy
                    if not (0 <= cx < W and 0 <= cy < H):
                        break
                    if not self.free(l, cx, cy, r3, net, 1, xr3):
                        break
                    if self.free(l, cx, cy, rt, net, hwt, xrt) and self.occ[l][cy * W + cx] != net:
                        out[(l, cx, cy)] = (p, l)       # the first cell outside the pad's own copper where the class width fits
                        break                           # (session 2: a cell inside own copper, e.g. Sofar's 0.1 mm stub at
        return out                                      # U2's balls, used to end the scan with no escape at all)

    def find_via_spots(self, net, near, r_cells, max_r=2.0, inside=None, count=6, xr=(), dia=None, clr=None, also=None, drill=None):
        """Up to `count` cells nearest to `near` (mm) where a via of dilation radius r_cells (diameter dia, clearance
        clr for the exact check) fits for `net`, optionally inside a polygon and passing `also(x, y)`; spaced ≥ 0.5 mm
        apart so they are real alternatives."""
        cx0, cy0 = cell(*near)
        cands = []
        rr = int(max_r / PITCH)
        for dy in range(-rr, rr + 1):
            for dx in range(-rr, rr + 1):
                cx, cy = cx0 + dx, cy0 + dy
                if not (0 <= cx < W and 0 <= cy < H):
                    continue
                if not self.via_free(cx, cy, r_cells, net, 3, xr, dia, clr, drill):
                    continue
                if inside is not None and not inside.Contains(V(*pos(cx, cy))):
                    continue
                if also is not None and not also(*pos(cx, cy)):
                    continue
                cands.append((dx * dx + dy * dy, cx, cy))
        cands.sort()
        out = []
        for d, cx, cy in cands:
            p = pos(cx, cy)
            if all(geom.dist(p, q) >= 0.5 for q in out):
                out.append(p)
            if len(out) >= count:
                break
        return out

    def find_via_spot(self, net, near, r_cells, max_r=2.0, inside=None, xr=(), dia=None, clr=None, also=None, drill=None):
        s = self.find_via_spots(net, near, r_cells, max_r, inside, 1, xr, dia, clr, also, drill)
        return s[0] if s else None


# ---- connectivity by geometry (the Python ratsnest API is not iterable in 9.0.6) ------------------------------------
def item_layers(item):
    if item.GetClass() == "PCB_VIA" or (item.GetClass() == "PAD" and item.GetDrillSize().x > 0):
        return set(ALL_LAYERS)
    if item.GetClass() == "PAD":
        return {l for l in ALL_LAYERS if item.IsOnLayer(l)}
    return {item.GetLayer()}


def touches(a, b):
    la, lb = item_layers(a), item_layers(b)
    common = la & lb
    if not common:
        return False
    l = next(iter(common))
    return a.GetEffectiveShape(l).Collide(b.GetEffectiveShape(l), 0)


def net_clusters(board, net_name, kinds=("PAD", "PCB_TRACK", "PCB_ARC", "PCB_VIA")):
    """Group a net's pads, tracks, arcs and vias into connected clusters (lists of items) by touching geometry."""
    items = []
    for f in board.GetFootprints():
        for p in f.Pads():
            if p.GetNetname() == net_name and "PAD" in kinds:
                items.append(p)
    for t in board.GetTracks():
        if t.GetNetname() == net_name and t.GetClass() in kinds:
            items.append(t)
    parent = list(range(len(items)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    boxes = [i.GetBoundingBox() for i in items]
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if find(i) == find(j):
                continue
            if not boxes[i].Intersects(boxes[j]):
                continue
            if touches(items[i], items[j]):
                parent[find(i)] = find(j)
    groups = {}
    for i, it in enumerate(items):
        groups.setdefault(find(i), []).append(it)
    return list(groups.values())


def pad_cells_of(grid, items, layers=None):
    """Cells of the cluster's PADS only (the soft goals of Grid.route)."""
    cells = set()
    for it in items:
        if it.GetClass() == "PAD" and it.m_Uuid.AsString() not in grid.exclude_ids:
            cells |= grid.pad_cells(it, layers or ROUTE_LAYERS)
    return cells


def cluster_cells(grid, items, layers=None):
    """Routable cells covered by a cluster's items (pads, track centrelines, vias)."""
    cells = set()
    layers = layers or ROUTE_LAYERS
    for it in items:
        if it.m_Uuid.AsString() in grid.exclude_ids:
            continue
        cls = it.GetClass()
        if cls == "PAD":
            cells |= grid.pad_cells(it, layers)
        elif cls == "PCB_VIA":
            cx, cy = cell(mm(it.GetPosition().x), mm(it.GetPosition().y))
            for l in layers:
                cells.add((l, cx, cy))
        elif cls == "PCB_TRACK":
            if it.GetLayer() not in layers:
                continue
            a, b = geom.xy(it.GetStart()), geom.xy(it.GetEnd())
            n = max(1, int(geom.dist(a, b) / PITCH))
            for k in range(n + 1):
                x, y = a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n
                cx, cy = cell(x, y)
                cells.add((it.GetLayer(), cx, cy))
    return cells


def cluster_escapes(grid, items, cls, net, layers=None):
    """Escape endpoints of every pad in the cluster (see Grid.escapes)."""
    out = {}
    for it in items:
        if it.GetClass() == "PAD" and it.m_Uuid.AsString() not in grid.exclude_ids:
            out.update(grid.escapes(it, cls, net, layers_only=layers))
    return out


def centroid(items):
    xs = [mm(i.GetPosition().x) for i in items]
    ys = [mm(i.GetPosition().y) for i in items]
    return sum(xs) / len(xs), sum(ys) / len(ys)
