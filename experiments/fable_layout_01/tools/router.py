"""A small grid router for the experiment (pure Python, no numpy: KiCad's bundled Python has none).

Model: 0.1 mm cells over the board frame; four routing layers (Top, Internal 1, Internal 2, Bottom; the GND and PWR
planes carry no tracks); through vias only. Every piece of copper on the board is stamped into per-layer occupancy
maps with its net code, then dilated by (half width + clearance) of each routing class into "blocked unless my net"
maps, so A* only asks O(1) per cell. Pads with no net, the board edge margin, hole keep-outs and the insert pull-backs
(blocked for every net but the insert's) are stamped as blocked for all. Routed copper is stamped back before the next
net. Widths, clearances and via sizes come from the class table (BRIEF §6).
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
    "power_n": (0.3, 0.25, 0.5, 0.25),    # power-class fallbacks: narrower, the brief's 0.25 clearance kept
    "power_t": (0.2, 0.25, 0.45, 0.2),
    "power":  (0.5, 0.25, 0.6, 0.3),
    "pi5v":   (1.0, 0.25, 0.6, 0.3),
    "payload": (0.6, 0.25, 0.5, 0.25),
    "rail":   (0.3, 0.15, 0.5, 0.25),
    "signal": (0.2, 0.15, 0.45, 0.2),
    "data":   (0.2, 0.15, 0.45, 0.2),
    "thin":   (0.15, 0.15, 0.45, 0.2),
}


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


class Grid:
    def __init__(self, board):
        self.board = board
        self.occ = {l: [0] * (W * H) for l in ALL_LAYERS}
        self.radii = [3, 4, 5, 6, 7, 10]  # cells: thin, signal track, small via, power track / 0.5 via, power via, bus
        self.dil = {r: {l: [0] * (W * H) for l in ALL_LAYERS} for r in self.radii}
        # Cross-class clearance (QE S7.b R2-F2): the brief's clearance is a property of BOTH items. dilk[r][layer] holds a
        # bitmask of the kinds of copper within r cells: 1 = bus-net copper, 2 = power-class copper (power / pi5v /
        # payload nets), 4 = anything that is not a bus net. A non-bus route keeps bit 1 clear within its 0.35 mm
        # radius and bit 2 within its 0.25 mm radius; a bus route keeps bit 4 clear within its 0.35 mm radius.
        self.kradii = [4, 5, 6, 7, 8, 9, 10]
        self.dilk = {r: {l: [0] * (W * H) for l in ALL_LAYERS} for r in self.kradii}
        self.disks = {r: disk(r, strict=True) for r in sorted(set(self.radii) | set(self.kradii))}
        self.made = {}           # net name -> board items this grid created (for rip-up)
        self.hole = [0] * (W * H)   # cells where a new via centre would put its drill < 0.25 mm from an existing hole
        self.exclude_ids = set()    # uuids of items no route may start from or end on (the Kelvin sense traces)
        self.bus_exempt = False     # last resort for one net: keep the Default 0.15 from bus copper (declared + excluded)
        self.netcode = {}
        for i in range(board.GetNetInfo().GetNetCount()):
            ni = board.GetNetInfo().GetNetItem(i)
            if ni:
                self.netcode[ni.GetNetname()] = ni.GetNetCode()
        self.bus_codes = {code for name, code in self.netcode.items() if net_class(name) == "bus"}
        self.kind = {code: (1 if net_class(name) == "bus" else (2 | 4 if net_class(name) in ("power", "pi5v", "payload") else 4))
                     for name, code in self.netcode.items()}
        self._stamp_board()

    # ---- stamping ---------------------------------------------------------------------------------------------
    def _mark(self, layer, cx, cy, net):
        if 0 <= cx < W and 0 <= cy < H:
            i = cy * W + cx
            o = self.occ[layer]
            if o[i] == 0:
                o[i] = net
            elif o[i] != net:
                o[i] = BLOCK
            for r in self.radii:
                d = self.dil[r][layer]
                for dx, dy in self.disks[r]:
                    x, y = cx + dx, cy + dy
                    if 0 <= x < W and 0 <= y < H:
                        j = y * W + x
                        if d[j] == 0:
                            d[j] = net
                        elif d[j] != net:
                            d[j] = BLOCK
            bit = self.kind.get(net, 4)
            for r in self.kradii:
                d = self.dilk[r][layer]
                for dx, dy in self.disks[r]:
                    x, y = cx + dx, cy + dy
                    if 0 <= x < W and 0 <= y < H:
                        d[y * W + x] |= bit

    INFLATE = 0.071     # half a cell diagonal: pre-existing (off-grid) copper is stamped this much larger so that every
                        # boundary point has a stamped cell within reach; the router's own tracks and vias are on-grid

    HOLE_GAP = 0.25     # KiCad's hole-to-hole minimum; a new via's drill is at most 0.3 mm
    NEW_DRILL = 0.3

    def stamp_hole(self, x, y, drill):
        """Forbid new via centres closer than drill/2 + 0.15 + 0.25 (+ half a cell) to this hole (same net too)."""
        cx, cy = cell(x, y)
        r = int(math.ceil((drill / 2 + self.NEW_DRILL / 2 + self.HOLE_GAP + 0.07) / PITCH))
        for dx, dy in disk(r, strict=True):
            X, Y = cx + dx, cy + dy
            if 0 <= X < W and 0 <= Y < H:
                self.hole[Y * W + X] = 1

    def stamp_disk(self, layers, x, y, radius, net, inflate=0.0):
        radius += inflate
        cx, cy = cell(x, y)
        rc = int(math.ceil(radius / PITCH))
        for dx, dy in disk(rc):
            px, py = pos(cx + dx, cy + dy)
            if (px - x) ** 2 + (py - y) ** 2 <= radius * radius + 1e-9:
                for l in layers:
                    self._mark(l, cx + dx, cy + dy, net)

    def stamp_segment(self, layer, a, b, width, net, inflate=0.0):
        hw = width / 2 + inflate
        x0, y0 = min(a[0], b[0]) - hw, min(a[1], b[1]) - hw
        x1, y1 = max(a[0], b[0]) + hw, max(a[1], b[1]) + hw
        c0, c1 = cell(x0, y0), cell(x1, y1)
        ax, ay, bx, by = a[0], a[1], b[0], b[1]
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        for cy in range(c0[1], c1[1] + 1):
            for cx in range(c0[0], c1[0] + 1):
                px, py = pos(cx, cy)
                if L2 == 0:
                    t = 0
                else:
                    t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L2))
                qx, qy = ax + t * dx, ay + t * dy
                if (px - qx) ** 2 + (py - qy) ** 2 <= hw * hw + 1e-9:
                    self._mark(layer, cx, cy, net)

    def stamp_poly(self, layers, poly, net, inflate=0.0):
        """poly: SHAPE_POLY_SET in board coordinates."""
        bb = poly.BBox()
        c0 = cell(mm(bb.GetLeft()) - inflate, mm(bb.GetTop()) - inflate)
        c1 = cell(mm(bb.GetRight()) + inflate, mm(bb.GetBottom()) + inflate)
        clr = MM(inflate)
        for cy in range(c0[1], c1[1] + 1):
            for cx in range(c0[0], c1[0] + 1):
                px, py = pos(cx, cy)
                if poly.Collide(V(px, py), clr) if inflate else poly.Contains(V(px, py)):
                    for l in layers:
                        self._mark(l, cx, cy, net)

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
                for l in layers:
                    poly = p.GetEffectivePolygon(l, pcbnew.ERROR_INSIDE)
                    self.stamp_poly([l], poly, net, self.INFLATE)
                if p.GetDrillSize().x > 0:
                    self.stamp_disk(ALL_LAYERS, mm(p.GetPosition().x), mm(p.GetPosition().y),
                                    mm(max(p.GetDrillSize().x, p.GetDrillSize().y)) / 2 + 0.25, net if net else BLOCK, self.INFLATE)
                    self.stamp_hole(mm(p.GetPosition().x), mm(p.GetPosition().y), mm(max(p.GetDrillSize().x, p.GetDrillSize().y)))
        # footprint rule areas (the M3 housing holes' keep-outs): nothing of ours goes there
        for f in b.GetFootprints():
            for z in f.Zones():
                if z.GetIsRuleArea():
                    layers = [l for l in z.GetLayerSet().Seq() if l in ALL_LAYERS] or ALL_LAYERS
                    self.stamp_poly(ALL_LAYERS, pcbnew.SHAPE_POLY_SET(z.Outline()), BLOCK)
        # footprint copper graphics (the net-tie bridges of JP1/JP2): blocked for every net
        for f in b.GetFootprints():
            for s in f.GraphicalItems():
                if s.GetClass() == "PCB_SHAPE" and s.GetLayer() in ALL_LAYERS:
                    poly = pcbnew.SHAPE_POLY_SET()
                    s.TransformShapeToPolygon(poly, s.GetLayer(), 0, MM(0.01), pcbnew.ERROR_INSIDE)
                    self.stamp_poly([s.GetLayer()], poly, BLOCK, self.INFLATE)
        # tracks, arcs, vias
        for t in b.GetTracks():
            net = self.netcode.get(t.GetNetname(), BLOCK)
            cls = t.GetClass()
            if cls == "PCB_VIA":
                self.stamp_disk(ALL_LAYERS, mm(t.GetPosition().x), mm(t.GetPosition().y), mm(t.GetWidth(pcbnew.F_Cu)) / 2, net, self.INFLATE)
                self.stamp_hole(mm(t.GetPosition().x), mm(t.GetPosition().y), mm(t.GetDrillValue()))
            elif cls == "PCB_ARC":
                poly = pcbnew.SHAPE_POLY_SET()
                t.TransformShapeToPolygon(poly, t.GetLayer(), 0, MM(0.01), pcbnew.ERROR_INSIDE)
                self.stamp_poly([t.GetLayer()], poly, net, self.INFLATE)
            else:
                self.stamp_segment(t.GetLayer(), geom.xy(t.GetStart()), geom.xy(t.GetEnd()), mm(t.GetWidth()), net, self.INFLATE)
        # zones: copied island pours (their outlines) and rule areas
        for z in b.Zones():
            layers = [l for l in z.GetLayerSet().Seq() if l in ALL_LAYERS]
            if z.GetIsRuleArea():
                name = z.GetZoneName()
                net = 0
                for ref, n in geom.INSERT_NET.items():
                    if ref in name:
                        net = self.netcode.get("/Top-Level Schematic/" + n, BLOCK)
                if net:
                    self.stamp_poly(layers, pcbnew.SHAPE_POLY_SET(z.Outline()), net, self.INFLATE)
            # filled zones (planes, island pours) are not obstacles: the fill keeps clearance around other copper
        # keep outer-layer copper away from the standoff / housing holes (BRIEF §3: nothing within r 3.0 / 3.5)
        for ref, (x, y) in geom.PI_HOLES.items():
            self.stamp_disk([pcbnew.F_Cu, pcbnew.B_Cu], x, y, 3.0, BLOCK)
        for ref, (x, y) in geom.HOUSING_HOLES.items():
            self.stamp_disk([pcbnew.F_Cu, pcbnew.B_Cu], x, y, 3.5, BLOCK)

    # ---- queries ----------------------------------------------------------------------------------------------
    def kradius(self, width, clearance):
        r = int(math.ceil((width / 2 + clearance + 0.07) / PITCH))
        return min(x for x in self.kradii if x >= r)

    def xradii(self, net, width, clearance):
        """[(bit, radius)] the cross-class checks for a new item of this net / width / class clearance."""
        if net in self.bus_codes:
            return [(4, self.kradius(width, 0.35))]
        out = [] if self.bus_exempt else [(1, self.kradius(width, 0.35))]
        if clearance < 0.25:
            out.append((2, self.kradius(width, 0.25)))
        return out

    def free(self, layer, cx, cy, r, net, hw_cells=2, xr=()):
        i = cy * W + cx
        if self.edge[i] <= hw_cells:          # copper would reach within the edge clearance
            return False
        v = self.dil[r][layer][i]
        if not (v == 0 or v == net):
            return False
        for bit, rk in xr:
            if self.dilk[rk][layer][i] & bit:
                return False
        return True

    def via_free(self, cx, cy, r, net, hw_cells=3, xr=()):
        if self.edge[cy * W + cx] <= hw_cells or self.hole[cy * W + cx]:
            return False
        i = cy * W + cx
        for l in ALL_LAYERS:
            v = self.dil[r][l][i]
            if v != 0 and v != net:
                return False
            for bit, rk in xr:
                if self.dilk[rk][l][i] & bit:
                    return False
        return True

    def radius_for(self, width, clearance):
        # + 0.07 mm: copper can reach up to half a cell diagonal beyond the last stamped cell centre
        r = int(math.ceil((width / 2 + clearance + 0.07) / PITCH))
        return min(x for x in self.radii if x >= r)

    # ---- A* ---------------------------------------------------------------------------------------------------
    def route(self, net, starts, goals, cls, layers=None, max_nodes=400000, via_cost=12.0, via_ok=True, soft=()):
        """starts/goals: {(layer, cx, cy)} sets. Returns a path [(layer, cx, cy), ...] or None.
        soft: goal cells that may be entered by an orthogonal step without the clearance test — the destination
        PAD's own copper (a bus leg enters T1/T2 pad 6 although pad 7 sits 0.24 mm away, Sofar's geometry)."""
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
        goal_cells = {}
        for l, cx, cy in goals:
            goal_cells.setdefault((cx, cy), set()).add(l)
        gx = [c[0] for c in goal_cells]
        gy = [c[1] for c in goal_cells]
        gcx, gcy = sum(gx) / len(gx), sum(gy) / len(gy)
        gminx, gmaxx, gminy, gmaxy = min(gx), max(gx), min(gy), max(gy)

        def h(cx, cy):
            dx = max(gminx - cx, 0, cx - gmaxx)
            dy = max(gminy - cy, 0, cy - gmaxy)
            return math.hypot(dx, dy)
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
                ng = g + c
                if ng < best.get(nxt, 1e18):
                    best[nxt] = ng
                    parent[nxt] = cur
                    heapq.heappush(open_heap, (ng + h(nx, ny), ng, nxt))
            if via_ok and self.via_free(cx, cy, rv, net, hwv, xrv):
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

    # ---- emitting copper --------------------------------------------------------------------------------------
    def commit(self, net_name, path, cls):
        """Turn a path into tracks and vias on the board and stamp them. Returns (tracks, vias, length_mm)."""
        width, clear, vdia, vdrill = CLASSES[cls]
        net = self.netcode[net_name]
        ni = self.board.FindNet(net_name)
        made = self.made.setdefault(net_name, [])
        segs, vias = [], []
        i = 0
        while i < len(path):
            j = i
            while j + 1 < len(path) and path[j + 1][0] == path[i][0]:
                j += 1
            run = path[i:j + 1]
            # compress collinear cells
            pts = [run[0]]
            for k in range(1, len(run)):
                if k + 1 < len(run):
                    d1 = (run[k][1] - run[k - 1][1], run[k][2] - run[k - 1][2])
                    d2 = (run[k + 1][1] - run[k][1], run[k + 1][2] - run[k][2])
                    if d1 == d2:
                        continue
                pts.append(run[k])
            for a, b in zip(pts, pts[1:]):
                segs.append((a[0], pos(a[1], a[2]), pos(b[1], b[2])))
            if j + 1 < len(path):
                vias.append(pos(path[j][1], path[j][2]))
            i = j + 1
        length = 0.0
        for layer, a, b in segs:
            t = pcbnew.PCB_TRACK(self.board)
            t.SetStart(V(*a))
            t.SetEnd(V(*b))
            t.SetWidth(MM(width))
            t.SetLayer(layer)
            t.SetNet(ni)
            self.board.Add(t)
            made.append(t)
            self.stamp_segment(layer, a, b, width, net)
            length += geom.dist(a, b)
        for p in vias:
            v = pcbnew.PCB_VIA(self.board)
            v.SetPosition(V(*p))
            v.SetViaType(pcbnew.VIATYPE_THROUGH)
            v.SetWidth(MM(vdia))
            v.SetDrill(MM(vdrill))
            v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
            v.SetNet(ni)
            self.board.Add(v)
            made.append(v)
            self.stamp_disk(ALL_LAYERS, p[0], p[1], vdia / 2, net)
            self.stamp_hole(p[0], p[1], vdrill)
        return len(segs), len(vias), length

    def add_track(self, net_name, a, b, layer, width):
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
        return t

    def add_via(self, net_name, p, dia, drill):
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
        return v

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

    def find_via_spots(self, net, near, r_cells, max_r=2.0, inside=None, count=6, xr=()):
        """Up to `count` cells nearest to `near` (mm) where a via of dilation radius r_cells fits for `net`,
        optionally inside a polygon; spaced ≥ 0.5 mm apart so they are real alternatives."""
        cx0, cy0 = cell(*near)
        cands = []
        rr = int(max_r / PITCH)
        for dy in range(-rr, rr + 1):
            for dx in range(-rr, rr + 1):
                cx, cy = cx0 + dx, cy0 + dy
                if not (0 <= cx < W and 0 <= cy < H):
                    continue
                if not self.via_free(cx, cy, r_cells, net, 3, xr):
                    continue
                if inside is not None and not inside.Contains(V(*pos(cx, cy))):
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

    def find_via_spot(self, net, near, r_cells, max_r=2.0, inside=None, xr=()):
        s = self.find_via_spots(net, near, r_cells, max_r, inside, 1, xr)
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


def centroid(items):
    xs = [mm(i.GetPosition().x) for i in items]
    ys = [mm(i.GetPosition().y) for i in items]
    return sum(xs) / len(xs), sum(ys) / len(ys)
