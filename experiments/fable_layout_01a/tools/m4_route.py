#!/usr/bin/env python3
"""M4 (brief 1.a: milestone M2): planes, the remaining routing, zone fill. Applied by tools/build_all.sh after m3_copy.py.

Order (OPTIONS §2): planes → the bus feeds insert → inductor by hand (BRIEF §6) → the two ADIN pairs as coupled pairs
(router.route_pair, Top + Internal 1, the mote's length limits) → the bus data legs → the 5 V links at the strip's
north end → VBUS_OUT → the ADIN pocket's planned nets (SPI, ~{INT}, ~{RST}, ADIN_PWR on their corridors) → the rails
into the pocket (1V8, 3V3) → the LED nets north → the load switch's signals → everything else short-first → stitching
vias → plane leftovers → zone fill. Every net is routed at its class width and clearance or reported open: there are
no fallback classes (BRIEF §5); fine-pitch pads leave through ≤ 1 mm 0.15 mm escapes (router.escapes). Writes
out/m4/routing.json with what was routed and how.
"""
import json
import math
import time

import pcbnew

import geom
import router
from geom import MM, mm, V

TOP = "/Top-Level Schematic/"
NETS = {}        # short name -> full board net name (filled in main: global labels have no sheet prefix)
F, I1, I3, B = pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In3_Cu, pcbnew.B_Cu


def N(short):
    return NETS[short]


PAIRS = {    # port: (P net, N net, U1 pins (P, N), T pads (P, N), length limit per net (mote), pins' outward direction, pads' inward direction)
    1: ("BM1_DATA_P", "BM1_DATA_N", ("U1", "28", "27"), ("T1", "1", "2"), 9.5, (0, -1), (1, 0)),
    2: ("BM2_DATA_P", "BM2_DATA_N", ("U1", "5", "4"), ("T2", "1", "2"), 21.3, (0, 1), (1, 0)),
}
# corridor preferences (OPTIONS §2.3): {layer: cost multiplier}; a layer not listed costs 1.0
PREF_I3 = {I3: 1.0, I1: 1.5, F: 2.5, B: 2.5}
PREF_I1 = {I1: 1.0, I3: 1.5, F: 2.5, B: 2.5}
PREF_TOP = {F: 1.0, I1: 1.5, I3: 1.5, B: 1.5}
PREF_BOT = {B: 1.0, I3: 1.4, I1: 1.5, F: 2.0}
log = {"planes": {}, "manual": [], "pairs": [], "stitch": [], "routed": [], "failed": [], "notes": []}


def poly_from_rects(rects):
    ps = pcbnew.SHAPE_POLY_SET()
    for r in rects:
        ps.BooleanAdd(router_rect(r))
    ps.Simplify()
    return ps


def router_rect(r):
    ps = pcbnew.SHAPE_POLY_SET()
    ch = pcbnew.SHAPE_LINE_CHAIN()
    for x, y in ((r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])):
        ch.Append(V(x, y))
    ch.SetClosed(True)
    ps.AddOutline(ch)
    return ps


def add_zone(board, layer, net_name, poly, name, priority, min_thick=0.25, clearance=0.25, solid=False):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    if net_name:
        z.SetNet(board.FindNet(net_name))
    z.SetAssignedPriority(priority)
    z.SetMinThickness(MM(min_thick))
    z.SetLocalClearance(MM(clearance))
    z.SetThermalReliefGap(MM(0.254))
    z.SetThermalReliefSpokeWidth(MM(0.254))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL if solid else pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetZoneName(name)
    for i in range(poly.OutlineCount()):
        z.Outline().AddOutline(poly.Outline(i))
        for k in range(poly.HoleCount(i)):
            z.Outline().AddHole(poly.Hole(i, k), i)
    board.Add(z)
    return z


def planes(board):
    """Create the plane zones (once: tools/m3b_planes.py adds them before the pre-route trim; a second call only
    refills) and return {net: (outline, layer, fill)} so the stitching step can test 'inside'."""
    if not any(z.GetZoneName().startswith("GND plane (In2)") for z in board.Zones()):
        make_planes(board)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    polys = {}
    wanted = {("GND", pcbnew.In2_Cu), ("VBUS", pcbnew.In4_Cu), (N("P_IN"), pcbnew.In4_Cu), ("3V3", pcbnew.In4_Cu), (N("5V_PI"), pcbnew.B_Cu),
              (N("ADIN_AVDD"), pcbnew.In4_Cu), (N("ADIN_VDDIO"), pcbnew.In4_Cu)}
    for z in board.Zones():
        if z.GetIsRuleArea() or not z.GetNetname():
            continue
        if True:        # every filled zone of a net joins its clusters (Sofar's copied island pours too); the stitching
            layer = z.GetLayer()      # via spots are searched in the union of the fills
            outline = pcbnew.SHAPE_POLY_SET(z.Outline())
            raw = pcbnew.SHAPE_POLY_SET(z.GetFilledPolysList(layer))
            fill = pcbnew.SHAPE_POLY_SET(raw)
            fill.Deflate(MM(0.15), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, MM(0.01))
            if z.GetNetname() in polys:       # several zones of one net: union (outline, layer of the first, fills)
                polys[z.GetNetname()][0].BooleanAdd(outline)
                polys[z.GetNetname()][2].BooleanAdd(fill)
            else:
                polys[z.GetNetname()] = [outline, layer, fill, None]
    for net_name in polys:
        polys[net_name][3] = island_table(board, net_name)
    return polys


def make_planes(board):
    o = geom.OUTLINE
    outline = pcbnew.SHAPE_POLY_SET()
    board.GetBoardPolygonOutlines(outline)
    body = pcbnew.SHAPE_POLY_SET(outline)
    body.Deflate(MM(geom.EDGE_CLEARANCE), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, MM(0.01))
    # GND plane with one slot past each inductor: the island (inductor + its inserts, west) joins the rest of the plane
    # only on the far side from the inserts (east); slots 0.5 mm wide along the island's band-side edge (as 01).
    gnd = pcbnew.SHAPE_POLY_SET(body)
    slots = [(o["x0"], 26.2, 22.7, 26.7),      # port 2 island south edge (above U1's pins, y ≥ 28.2)
             (o["x0"], 6.5, 22.7, 7.0),         # port 2 island north edge (north band stays with the main plane)
             (o["x0"], 39.0, 22.7, 39.5),       # port 1 island north edge, south of the port-2 pair's corridor at y ≈ 37
             (o["x0"], 54.0, 22.7, 54.5)]       # port 1 island south edge
    for s in slots:
        gnd.BooleanSubtract(router_rect(s))
    gnd.Simplify()
    add_zone(board, pcbnew.In2_Cu, "GND", gnd, "GND plane (In2): island per inductor, slots per the mote", 0, 0.25, 0.25)
    log["planes"]["GND"] = {"layer": "In2", "slots": slots, "note": "islands x -7.5..22.7, y 7-26.2 (port 2) and 39.5-54 (port 1), open to the east"}
    # PWR plane In4: VBUS everywhere but the P_IN island under port 2's centre, the 3V3 island at the 3.3 V buck's
    # output (moved with the cell: x 33.4-38, y 24-38), the copied ADIN islands (priority 7) and Sofar's two no-net islands
    vbus = poly_from_rects([(23.2, 0.5, 38.0, 64.5), (o["x0"], 26.0, 23.2, 64.5), (16.8, 8.0, 23.2, 26.0)])
    vbus.BooleanIntersection(body)
    p_in = poly_from_rects([(11.0, 8.0, 16.6, 25.7)])     # R8 straddles the P_IN / VBUS boundary at x ≈ 16.6
    v3 = poly_from_rects([(33.4, 24.0, 38.0, 38.0)])
    vbus.BooleanSubtract(poly_from_rects([(33.1, 23.7, 38.3, 38.3)]))
    vbus.Simplify()
    nc2 = poly_from_rects([(3.5, 13.5, 9.5, 20.0)])
    nc1 = poly_from_rects([(3.5, 45.0, 9.5, 51.5)])
    add_zone(board, pcbnew.In4_Cu, "VBUS", vbus, "VBUS plane (In4)", 0, 0.25, 0.25)
    add_zone(board, pcbnew.In4_Cu, N("P_IN"), p_in, "P_IN island (In4) under port 2 east", 5, 0.25, 0.25)
    add_zone(board, pcbnew.In4_Cu, "3V3", v3, "3V3 island (In4) at the 3.3 V buck output", 5, 0.25, 0.25)
    add_zone(board, pcbnew.In4_Cu, None, nc2, "NoConnect_P2 (In4, no net: Sofar Q10)", 6, 0.25, 0.25)
    add_zone(board, pcbnew.In4_Cu, None, nc1, "NoConnect_P1 (In4, no net: Sofar Q10)", 6, 0.25, 0.25)
    log["planes"]["In4"] = {"VBUS": "strip x 23.2-38 full height + west half y 26-64.5 (ADIN islands cut it, priority 7)",
                            "P_IN": [11.0, 8.0, 16.6, 25.7], "VBUS east of P_IN": [16.8, 8.0, 23.2, 26.0], "3V3": [33.4, 24.0, 38.0, 38.0],
                            "NoConnect": [[3.5, 13.5, 9.5, 20.0], [3.5, 45.0, 9.5, 51.5]]}
    # 5 V to the Pi: a bottom-side pour under JP1 / L6 for the output caps (BRIEF §6: ≥ 1.0 mm or a pour); the links
    # L6 → JP1 → J1 pins 2/4 are 1.0 mm top-layer tracks (OPTIONS Q3)
    pi5 = poly_from_rects([(29.7, 7.5, 38.0, 24.0)])
    add_zone(board, pcbnew.B_Cu, N("5V_PI"), pi5, "5V_PI pour (B.Cu) under JP1 / L6 / U10", 3, solid=True)
    log["planes"]["5V_PI"] = [29.7, 7.5, 38.0, 24.0]
    # bottom-side GND pour over the whole board, as the mote's bottom layer (it is what joins Sofar's decoupling caps
    # under U1 and the 1.8 V buck to GND there); the insert pull-backs and the M3 holes' rule areas cut it
    gndb = pcbnew.SHAPE_POLY_SET(body)
    for f in board.GetFootprints():          # the fiducials' mask apertures hold no pour (DRC mask bridge)
        if f.GetReference().startswith("FID") and f.IsFlipped():
            c = geom.xy(f.GetPosition())
            ring = pcbnew.SHAPE_POLY_SET()
            ch = pcbnew.SHAPE_LINE_CHAIN()
            for k in range(36):
                ch.Append(V(c[0] + 1.2 * math.cos(math.radians(10 * k)), c[1] + 1.2 * math.sin(math.radians(10 * k))))
            ch.SetClosed(True)
            ring.AddOutline(ch)
            gndb.BooleanSubtract(ring)
    gndb.Simplify()
    add_zone(board, pcbnew.B_Cu, "GND", gndb, "GND pour (B.Cu), as the mote's bottom layer", 0, 0.25, 0.25, solid=True)   # the mote's GND pours: solid pad connections
    log["planes"]["GND_B"] = "bottom pour, whole board, priority 0 (the 5V_PI pour is priority 3)"


def bus_feeds(g):
    """Insert ring → inductor bus pad, 1.5 mm wide on Top (BRIEF §6: ≥ 1.0 mm, short and wide)."""
    feeds = [("MP3", "BM2_P", (1.5, 12.0), (10.0, 12.49)), ("MP4", "BM2_N", (1.5, 21.4), (10.0, 21.01)),
             ("MP1", "BM1_P", (1.5, 43.6), (10.0, 39.99)), ("MP2", "BM1_N", (1.5, 53.0), (10.0, 48.5))]
    for ref, net, a, b in feeds:
        name = N(net)
        mid = (a[0] + 2.5, a[1])
        g.add_track(name, a, mid, pcbnew.F_Cu, 1.5)
        g.add_track(name, mid, b, pcbnew.F_Cu, 1.5)
        log["manual"].append({"net": net, "from": ref, "path": [a, mid, b], "width": 1.5, "layer": "Top"})


def plane_connected(cluster, plane):
    """A via / through pad whose copper overlaps one of the net's filled islands, or an SMD pad / track that lies on an
    island of its own layer — an island counting only when it reaches the net's other copper (an inner plane always
    does; an outer-layer pour island needs a via or a through pad of the net in it)."""
    fills = plane[3]            # {layer: [(island polygon, connected)]}
    for it in cluster:
        cls = it.GetClass()
        if cls == "PCB_VIA" or (cls == "PAD" and it.GetDrillSize().x > 0):
            for layer, islands in fills.items():
                for isl, ok in islands:
                    if ok and isl.Collide(it.GetPosition(), MM(0.2)):
                        return True
        elif cls == "PAD":
            for layer, islands in fills.items():
                if it.IsOnLayer(layer):
                    for isl, ok in islands:
                        if ok and isl.Collide(it.GetPosition(), MM(0.1)):
                            return True
        elif cls == "PCB_TRACK":
            for isl, ok in fills.get(it.GetLayer(), []):
                if ok and (isl.Collide(it.GetStart(), MM(0.05)) or isl.Collide(it.GetEnd(), MM(0.05))):
                    return True
    return False


def island_table(board, net_name):
    """{layer: [(island polygon, connected)]} of a net's zones; connected = an inner-plane island, or one holding a
    via / through pad of the net."""
    vias = [t.GetPosition() for t in board.GetTracks() if t.GetClass() == "PCB_VIA" and t.GetNetname() == net_name]
    pth = [p.GetPosition() for f in board.GetFootprints() for p in f.Pads() if p.GetNetname() == net_name and p.GetDrillSize().x > 0]
    out = {}
    for z in board.Zones():
        if z.GetIsRuleArea() or z.GetNetname() != net_name:
            continue
        layer = z.GetLayer()
        fp = z.GetFilledPolysList(layer)
        for i in range(fp.OutlineCount()):
            isl = pcbnew.SHAPE_POLY_SET()
            isl.AddOutline(fp.Outline(i))
            for h in range(fp.HoleCount(i)):
                isl.AddHole(fp.Hole(i, h), 0)
            ok = layer in (pcbnew.In2_Cu, pcbnew.In4_Cu) or any(isl.Collide(q, MM(0.1)) for q in vias + pth)
            out.setdefault(layer, []).append((isl, ok))
    return out


def pad_of(board, ref, num):
    fps = geom.fp_by_ref(board)
    return next(p for p in fps[ref].Pads() if p.GetNumber() == num)


def route_pairs(g, board):
    """Each ADIN pair as a coupled pair (router.route_pair / commit_pair): the virtual track starts 0.6 mm outside
    U1's two pins and ends 0.6 mm in front of the T pads; Top + Internal 1; one swap via where the pin and pad
    order demand it (pair_parity)."""
    for port, (pn, nn, (uref, up, un), (tref, tp, tn), limit, dir_out, dir_in) in PAIRS.items():
        P, Nn = N(pn), N(nn)
        pins = (geom.xy(pad_of(board, uref, up).GetPosition()), geom.xy(pad_of(board, uref, un).GetPosition()))
        pads = (geom.xy(pad_of(board, tref, tp).GetPosition()), geom.xy(pad_of(board, tref, tn).GetPosition()))
        pin_mid = ((pins[0][0] + pins[1][0]) / 2, (pins[0][1] + pins[1][1]) / 2)
        pad_mid = ((pads[0][0] + pads[1][0]) / 2, (pads[0][1] + pads[1][1]) / 2)
        S = (pin_mid[0] + 0.5 * dir_out[0], pin_mid[1] + 0.5 * dir_out[1])     # 0.1 mm past the pins' ends
        E = (pad_mid[0] - 0.2 * dir_in[0], pad_mid[1] - 0.2 * dir_in[1])       # on the pads' own copper
        parity = router.Grid.pair_parity(pins, pads, dir_out, dir_in)
        net = g.netcode[P]           # == g.netcode[Nn]: the pair is one net to the grid (Grid merge)
        # the swap figure makes the far track longer: try each swing side and keep the one whose longer net is shorter
        best = None
        for sides in ((1,), (-1,)):
            path, swaps = g.route_pair(net, {(F,) + router.cell(*S)}, {(F,) + router.cell(*E)}, parity, layers=[F, I1], max_nodes=1500000, via_cost=8.0, sides=sides)
            if path is None:
                continue
            Lp = len(path) * router.PITCH + (0.5 if swaps else 0.0)
            if best is None or Lp < best[0]:
                best = (Lp, path, swaps)
        if best is None:
            log["failed"].append({"net": pn, "why": f"pair port {port}: no path for the virtual track (parity {parity})"})
            log["pairs"].append({"port": port, "ok": False})
            continue
        _, path, swaps = best
        stats = g.commit_pair((P, Nn), path, pins, pads, swaps)
        log["notes"].append(f"pair port {port}: parity {parity}, swap figures at {sorted((router.pos(*c), sd) for c, sd in swaps.items())}")
        log["notes"].append(f"pair port {port}: {stats}")
        for name in (P, Nn):
            total = sum(mm(t.GetLength()) for t in board.GetTracks() if t.GetNetname() == name and t.GetClass() != "PCB_VIA")
            vias = sum(1 for t in board.GetTracks() if t.GetNetname() == name and t.GetClass() == "PCB_VIA")
            log["pairs"].append({"net": name.rsplit("/", 1)[-1], "port": port, "total_mm": round(total, 2), "limit_mm": limit, "vias": vias,
                                 "ok": total <= limit, "parity": parity})


def commit_with_stubs(g, net_name, path, cls, s_esc, t_esc):
    """Commit a path; if it starts / ends on an escape endpoint, lay that pad's 0.15 mm stub too."""
    segs, vias, length = g.commit(net_name, path, cls)
    for end, esc in ((path[0], s_esc), (path[-1], t_esc)):
        if end in esc:
            p, l = esc[end]
            g.add_track(net_name, p, router.pos(end[1], end[2]), l, 0.15)
            length += geom.dist(p, router.pos(end[1], end[2]))
    return segs, vias, length


def route_net(g, board, net_name, cls=None, layers=None, max_nodes=600000, plane_poly=None, via_cost=12.0, layer_cost=None, pair_only=None):
    """Join the net's clusters by tracks at the class width and clearance (no fallback): nearest pairs first, other
    pairings on failure; fine-pitch pads get escapes. Clusters already on the net's plane count as one. Returns the
    new track length, or None if a link could not be routed (logged in 'failed')."""
    cls = cls or router.net_class(net_name)
    clusters = router.net_clusters(board, net_name)
    if plane_poly is not None:
        on_plane = [c for c in clusters if plane_connected(c, plane_poly)]
        if on_plane:
            merged = [it for c in on_plane for it in c]
            clusters = [merged] + [c for c in clusters if not plane_connected(c, plane_poly)]
    clusters.sort(key=lambda c: -len(c))
    net = g.netcode[net_name]
    total = 0.0
    tried = set()          # (id(a), id(b)) pairs that found no path: a failed link does not stop the net's other links
    while len(clusters) > 1:
        pairs = sorted(((geom.dist(router.centroid(clusters[i]), router.centroid(clusters[j])), i, j)
                        for i in range(len(clusters)) for j in range(i + 1, len(clusters))
                        if (id(clusters[i]), id(clusters[j])) not in tried), key=lambda t: t[0])
        if not pairs:
            break
        _, ai, bi = pairs[0]
        a, b2 = clusters[ai], clusters[bi]
        s_cells = router.cluster_cells(g, a, layers)
        s_esc = router.cluster_escapes(g, a, cls, net, layers)
        t_cells = router.cluster_cells(g, b2, layers)
        t_esc = router.cluster_escapes(g, b2, cls, net, layers)
        path = None
        if (s_cells or s_esc) and (t_cells or t_esc):
            path = g.route(net, s_cells | set(s_esc), t_cells | set(t_esc), cls, layers=layers, max_nodes=max_nodes, via_cost=via_cost,
                           soft=router.pad_cells_of(g, b2, layers), layer_cost=layer_cost)
        if path is None:
            tried.add((id(a), id(b2)))
            continue
        segs, vias, length = commit_with_stubs(g, net_name, path, cls, s_esc, t_esc)
        total += length
        merged = a + b2
        clusters = [c for k, c in enumerate(clusters) if k not in (ai, bi)] + [merged]
    if len(clusters) > 1:
        log["failed"].append({"net": net_name, "why": "no path at the class width / clearance", "class": cls, "open_links": len(clusters) - 1,
                              "clusters": [sorted({it.GetParentFootprint().GetReference() + "." + it.GetNumber() for it in c if it.GetClass() == "PAD"})[:4] for c in clusters]})
        return None
    return total


def routed(short, L, cls):
    log["routed"].append({"net": short, "class": cls, "length_new_mm": None if L is None else round(L, 1)})


def gnd_links(g, board):
    """GND pads of one footprint within 1.0 mm of each other (U11's pins and its thermal pad, BGA balls): a straight
    0.15 mm link on the pad's layer when the line is clear (a pad-field link, BRIEF §5)."""
    n = 0
    for f in board.GetFootprints():
        pads = [p for p in f.Pads() if p.GetNetname() == "GND" and p.GetDrillSize().x == 0]
        others = [p for p in f.Pads() if p.GetNetname() != "GND"]
        for i, a in enumerate(pads):
            for b2 in pads[i + 1:]:
                la = [l for l in router.ROUTE_LAYERS if a.IsOnLayer(l) and b2.IsOnLayer(l)]
                if not la:
                    continue
                l = la[0]
                sa, sb = a.GetEffectiveShape(l), b2.GetEffectiveShape(l)
                if mm(sa.GetClearance(sb)) > 0.6:
                    continue
                pa, pb = geom.xy(a.GetPosition()), geom.xy(b2.GetPosition())
                # the link runs from the smaller pad's centre toward the other pad's centre and stops once inside it
                if a.GetBoundingBox().GetArea() > b2.GetBoundingBox().GetArea():
                    a, b2, sa, sb, pa, pb = b2, a, sb, sa, pb, pa
                end = pb
                for k in range(1, 41):
                    q = (pa[0] + (pb[0] - pa[0]) * k / 40, pa[1] + (pb[1] - pa[1]) * k / 40)
                    if sb.Collide(V(*q), 0):
                        end = q
                        break
                seg = pcbnew.SHAPE_SEGMENT(V(*pa), V(*end), MM(0.15))
                ok = all(not seg.Collide(o.GetEffectiveShape(l), MM(0.15) - 1) for o in others if o.IsOnLayer(l))
                if ok:
                    g.add_track("GND", pa, end, l, 0.15)
                    n += 1
    log["notes"].append(f"{n} intra-footprint GND links (0.15 mm)")


def prestitch(g, board, plane, max_r=1.5, net_name="GND", skip_pocket=True):
    """A via next to every single-pad cluster of a plane net before the signals are routed (≤ 1.2 mm away, inside
    the plane's filled copper), at the net's class width (escapes for fine pads)."""
    poly, layer, fill = plane[:3]
    net = g.netcode[net_name]
    pcls = "gnd" if net_name == "GND" else router.net_class(net_name)
    width, clear, vdia, vdrill = router.CLASSES[pcls]
    rv = g.radius_for(vdia, clear)
    n = 0
    for cluster in router.net_clusters(board, net_name):
        if plane_connected(cluster, plane) or len(cluster) != 1 or cluster[0].GetClass() != "PAD":
            continue
        pad = cluster[0]
        p = geom.xy(pad.GetPosition())
        if skip_pocket and p[0] < 7.0 and 25.0 < p[1] < 40.0:
            continue          # the ADIN pocket: U1's escapes need every free cell there; stitched after the signals
        if pad.m_Uuid.AsString() in g.exclude_ids:
            continue
        s_cells = g.pad_cells(pad)
        s_esc = g.escapes(pad, pcls, net)
        for spot in g.find_via_spots(net, p, rv, max_r=max_r, inside=fill, count=4, xr=g.xradii(net, vdia, clear)):
            cx, cy = router.cell(*spot)
            goals = {(l, cx, cy) for l in router.ROUTE_LAYERS}
            path = g.route(net, s_cells | set(s_esc), goals, pcls, max_nodes=20000)
            if path is None:
                continue
            commit_with_stubs(g, net_name, path, pcls, s_esc, {})
            g.add_via(net_name, spot, vdia, vdrill)
            log["stitch"].append({"net": net_name.rsplit("/", 1)[-1], "via": [round(spot[0], 2), round(spot[1], 2)], "pre": True})
            n += 1
            break
    log["notes"].append(f"{n} {net_name.rsplit('/', 1)[-1]} pads pre-stitched (via within {max_r} mm) before the signals")


def stitch(g, board, polys):
    """Every cluster of a plane net gets a via into its plane unless it already touches it."""
    for net_name, plane in polys.items():
        if net_name not in g.netcode:
            continue
        plane[3] = island_table(board, net_name)
        fill = plane[2]
        net = g.netcode[net_name]
        cls = "gnd" if net_name == "GND" else router.net_class(net_name)
        width, clear, vdia, vdrill = router.CLASSES[cls]
        rv = g.radius_for(vdia, clear)
        for cluster in router.net_clusters(board, net_name):
            if plane_connected(cluster, plane):
                continue
            pts = []
            for it in cluster:
                if it.m_Uuid.AsString() in g.exclude_ids:
                    continue
                if it.GetClass() == "PAD":
                    pts.append(geom.xy(it.GetPosition()))
                elif it.GetClass() == "PCB_TRACK":
                    pts.append(geom.xy(it.GetEnd()))
            spots = []
            for p in pts:
                for sp in g.find_via_spots(net, p, rv, max_r=4.0, inside=fill, count=12, xr=g.xradii(net, vdia, clear)):
                    spots.append((geom.dist(sp, p), sp))
            if not spots:
                log["failed"].append({"net": net_name, "why": "no via spot in the plane within 4 mm", "near": pts[:3]})
                continue
            spots.sort()
            s_cells = router.cluster_cells(g, cluster)
            s_esc = router.cluster_escapes(g, cluster, cls, net)
            done = False
            for _, spot in spots[:16]:
                cx, cy = router.cell(*spot)
                goals = {(l, cx, cy) for l in router.ROUTE_LAYERS}
                path = g.route(net, s_cells | set(s_esc), goals, cls, max_nodes=200000)
                if path is None:
                    continue
                commit_with_stubs(g, net_name, path, cls, s_esc, {})
                g.add_via(net_name, spot, vdia, vdrill)
                done = True
                break
            if not done:
                log["failed"].append({"net": net_name, "why": "no path to any of the stitching via spots", "near": pts[:3]})
                continue
            log["stitch"].append({"net": net_name.rsplit("/", 1)[-1], "via": [round(spot[0], 2), round(spot[1], 2)]})


def zone_stitch(g, board, filler):
    """Every filled island of every zone gets a via into the net's other copper when it has none: a bottom-pour
    island under U1 to the GND plane, Sofar's copied Top output pour to the bottom 5V_PI pour. The via spot is the
    island's cell nearest its centroid where a via of the net's class fits; the island is left as it is when none fits
    (reported)."""
    n = 0
    for z in list(board.Zones()):
        if z.GetIsRuleArea() or not z.GetNetname():
            continue
        net_name = z.GetNetname()
        net = g.netcode.get(net_name)
        if net is None:
            continue
        cls = "gnd" if net_name == "GND" else router.net_class(net_name)
        width, clear, vdia, vdrill = router.CLASSES[cls]
        rv = g.radius_for(vdia, clear)
        layer = z.GetLayer()
        fp = z.GetFilledPolysList(layer)
        vias = [t for t in board.GetTracks() if t.GetClass() == "PCB_VIA" and t.GetNetname() == net_name]
        pth = [p for f in board.GetFootprints() for p in f.Pads() if p.GetNetname() == net_name and p.GetDrillSize().x > 0]
        for i in range(fp.OutlineCount()):
            isl = pcbnew.SHAPE_POLY_SET()
            isl.AddOutline(fp.Outline(i))
            for h in range(fp.HoleCount(i)):
                isl.AddHole(fp.Hole(i, h), 0)
            if any(isl.Collide(v.GetPosition(), MM(0.1)) for v in vias) or any(isl.Collide(p.GetPosition(), MM(0.1)) for p in pth):
                continue
            if layer in (pcbnew.In2_Cu, pcbnew.In4_Cu) and i == 0 and fp.OutlineCount() == 1:
                continue
            bb = isl.BBox()
            cen = ((mm(bb.GetLeft()) + mm(bb.GetRight())) / 2, (mm(bb.GetTop()) + mm(bb.GetBottom())) / 2)
            inner = pcbnew.SHAPE_POLY_SET(isl)
            inner.Deflate(MM(vdia / 2 + 0.05), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, MM(0.01))
            spot = g.find_via_spot(net, cen, rv, max_r=max(2.0, (mm(bb.GetWidth()) + mm(bb.GetHeight())) / 2), inside=inner, xr=g.xradii(net, vdia, clear))
            if spot is None:
                log["failed"].append({"net": net_name, "why": f"zone island on {board.GetLayerName(layer)} near {tuple(round(c, 1) for c in cen)} has no via and none fits"})
                continue
            g.add_via(net_name, spot, vdia, vdrill)
            log["stitch"].append({"net": net_name.rsplit("/", 1)[-1], "via": [round(spot[0], 2), round(spot[1], 2)], "zone": z.GetZoneName()[:40]})
            n += 1
    if n:
        filler.Fill(board.Zones())
    log["notes"].append(f"{n} zone-island vias (zone_stitch)")


def main():
    t0 = time.time()
    board = geom.load()
    for i in range(board.GetNetInfo().GetNetCount()):
        ni = board.GetNetInfo().GetNetItem(i)
        if ni and ni.GetNetname():
            NETS[ni.GetNetname().rsplit("/", 1)[-1]] = ni.GetNetname()
    polys = planes(board)
    g = router.Grid(board, merge={N(nn): N(pn) for pn, nn, *_ in PAIRS.values()})
    log["notes"].append(f"grid {router.W}x{router.H} cells at {router.PITCH} mm built in {time.time() - t0:.0f} s")
    # The Kelvin sense traces (U4.1-R8.2 on P_IN, U4.2-R8.1 on VBUS, Sofar's 0.2032 mm Bottom tracks, copied whole) and
    # U4's two sense pads: no route starts or ends on them, no stitching via lands beside them (QE S7.b R2-F1)
    fps0 = geom.fp_by_ref(board)
    for p in fps0["U4"].Pads():
        if p.GetNumber() in ("1", "2"):
            g.exclude_ids.add(p.m_Uuid.AsString())
    u4 = geom.xy(fps0["U4"].GetPosition())
    nk = 0
    for t in board.GetTracks():
        if (t.GetClass() == "PCB_TRACK" and t.GetLayer() == pcbnew.B_Cu and abs(mm(t.GetWidth()) - 0.2032) < 0.001
                and t.GetNetname() in ("VBUS", N("P_IN")) and geom.dist(geom.xy(t.GetStart()), u4) < 7.5 and geom.dist(geom.xy(t.GetEnd()), u4) < 7.5):
            g.exclude_ids.add(t.m_Uuid.AsString())
            nk += 1
    log["notes"].append(f"Kelvin sense traces protected: {nk} tracks + U4 pads 1/2 excluded from routing starts/ends and stitching")
    bus_feeds(g)
    # 1. the ADIN pairs, coupled, Top + Internal 1
    route_pairs(g, board)
    # 2. the bus data legs (0.2 mm, 0.35 from everything incl. the opposite leg), Internal 1 preferred
    for net in ("BM1_P", "BM1_N", "BM2_P", "BM2_N"):
        L = route_net(g, board, N(net), "busleg", layer_cost=PREF_I1, max_nodes=1500000)
        routed(net, L, "busleg (data leg, 0.2 mm; 0.35 from every other net incl. the opposite leg)")
    # 3. the 5 V path at the strip's north end: L6 -> JP1 (5V_PI; the bottom pour joins the output caps) and JP1 -> J1 pins 2/4
    L = route_net(g, board, N("5V_PI"), "pi5v", plane_poly=polys.get(N("5V_PI")), layer_cost=PREF_TOP, max_nodes=800000)
    routed("5V_PI", L, "pi5v")
    L = route_net(g, board, N("PI_5V"), "pi5v", layer_cost=PREF_TOP, max_nodes=800000)
    routed("PI_5V", L, "pi5v")
    # 4. the load switch's signals (their escapes leave U11's 0.5 mm pitch rows first), then the payload output:
    #    U11 pin 10 -> D3/C50 (bottom) -> J5 pin 1 / TP36, Internal 2 west of U11 (south of J1's last pins)
    for short in ("ISET", "Net-(U11-UVLO)", "~{PAYLOAD_FAULT}", "PAYLOAD_EN"):
        L = route_net(g, board, N(short), max_nodes=800000)
        routed(short, L, router.net_class(N(short)))
    L = route_net(g, board, N("VBUS_OUT"), "payload", layer_cost=PREF_I3, max_nodes=1500000, via_cost=6.0)
    routed("VBUS_OUT", L, "payload")
    # 4b. GND pads of one footprint joined; lonely plane-net pads given their via before the signals crowd them
    gnd_links(g, board)
    prestitch(g, board, polys["GND"])
    for pn in ("VBUS", N("P_IN"), "3V3", N("5V_PI")):
        if pn in polys and pn in g.netcode:
            prestitch(g, board, polys[pn], net_name=pn)
    # 5. the ADIN pocket's planned nets (OPTIONS §2.3): SPI + ~{INT} + ~{CS} east on Internal 2 under U1 to J1; ~{RST} on
    #    Internal 1/2 from U1's east side; ADIN_PWR from U2/U3 on Internal 2
    for short, pref in (("~{ADIN_INT}", {I3: 1.0, I1: 1.1, F: 2.5, B: 2.5}), ("ADIN_MOSI", PREF_I3), ("ADIN_MISO", PREF_I3), ("ADIN_SCK", PREF_I3), ("~{ADIN_CS}", PREF_I3),
                        ("~{ADIN_RST}", PREF_I1)):
        L = route_net(g, board, N(short), layer_cost=pref, max_nodes=1500000, via_cost=6.0)
        routed(short, L, router.net_class(N(short)) + " (pocket corridor)")
    # 6. the rails into the pocket's south: 3V3 to U3 first (the longest way, from the island), then 1V8 (B18 -> U2) and
    #    ADIN_PWR (U2/U3 -> R43 / TP8 / J1 pin 16): the pocket's south exit holds one track per layer
    L = route_net(g, board, "3V3", plane_poly=polys.get("3V3"), layer_cost={I3: 1.0, I1: 1.2, B: 1.5, F: 2.5}, max_nodes=2500000, via_cost=6.0)
    routed("3V3", L, "rail (plane + pocket)")
    L = route_net(g, board, N("1V8"), layer_cost=PREF_I3, max_nodes=1500000, via_cost=6.0)
    routed("1V8", L, "rail")
    L = route_net(g, board, N("ADIN_PWR"), layer_cost=PREF_BOT, max_nodes=1500000, via_cost=6.0)
    routed("ADIN_PWR", L, "signal (pocket corridor)")
    # 7. the LED block at the north edge: ~{ADIN_P2_LED1} by the west edge lane, ~{ADIN_P1_LED1} and ADIN_VDDIO north
    #    between the L2 envelope and J1 (OPTIONS Q6)
    for short, pref in (("~{ADIN_P2_LED1}", PREF_I3), ("~{ADIN_P1_LED1}", PREF_I3)):
        L = route_net(g, board, N(short), layer_cost=pref, max_nodes=2000000)
        routed(short, L, "signal (LED, north)")
    L = route_net(g, board, N("ADIN_VDDIO"), plane_poly=polys.get(N("ADIN_VDDIO")), layer_cost=PREF_I3, max_nodes=2000000)
    routed("ADIN_VDDIO", L, "rail (island + LED block)")
    L = route_net(g, board, N("ADIN_LED_VDD"), layer_cost=PREF_BOT, max_nodes=400000)
    routed("ADIN_LED_VDD", L, "rail (LED block)")
    # 8. the load switch's signals and the I2C pull-ups
    for short in ("I2C1_SDA", "I2C1_SCL"):
        L = route_net(g, board, N(short), max_nodes=800000)
        routed(short, L, router.net_class(N(short)))
    # 9. the rest short-first
    done = {N(s) for s in ("BM1_DATA_P", "BM1_DATA_N", "BM2_DATA_P", "BM2_DATA_N", "5V_PI", "PI_5V", "VBUS_OUT", "BM1_P", "BM1_N", "BM2_P", "BM2_N",
                           "ADIN_MOSI", "ADIN_MISO", "ADIN_SCK", "~{ADIN_CS}", "~{ADIN_INT}", "~{ADIN_RST}", "ADIN_PWR", "1V8", "3V3",
                           "~{ADIN_P2_LED1}", "~{ADIN_P1_LED1}", "ADIN_VDDIO", "ADIN_LED_VDD", "PAYLOAD_EN", "~{PAYLOAD_FAULT}", "ISET",
                           "Net-(U11-UVLO)", "I2C1_SDA", "I2C1_SCL")}
    nets = []
    for i in range(board.GetNetInfo().GetNetCount()):
        ni = board.GetNetInfo().GetNetItem(i)
        if ni and ni.GetNetname() and not ni.GetNetname().startswith("unconnected-") and ni.GetNetname() not in done and ni.GetNetname() not in polys:
            nets.append(ni.GetNetname())

    def span(n):
        cl = router.net_clusters(board, n)
        if len(cl) < 2:
            return -1
        cs = [router.centroid(c) for c in cl]
        return max(geom.dist(a, b) for a in cs for b in cs)
    order = sorted(((span(n), n) for n in nets), key=lambda t: t[0])
    for sp, net in order:
        if sp < 0:
            continue
        L = route_net(g, board, net)
        routed(net.rsplit("/", 1)[-1], L, router.net_class(net))
    # 10. stitching vias for every plane-net cluster, then the planes' leftovers by track
    stitch(g, board, polys)
    for net, plane in polys.items():
        if net in g.netcode:
            L = route_net(g, board, net, plane_poly=plane, max_nodes=1200000)
            routed(net.rsplit("/", 1)[-1], L, router.net_class(net) + " (plane leftovers)")
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    zone_stitch(g, board, filler)
    # a pour split into islands by other copper: join the islands with tracks at the pour net's class, then refill
    for z in board.Zones():
        if z.GetIsRuleArea() or not z.GetNetname() or z.GetLayer() not in router.ROUTE_LAYERS:
            continue
        fp = z.GetFilledPolysList(z.GetLayer())
        if fp.OutlineCount() <= 1:
            continue
        net = g.netcode[z.GetNetname()]
        pcls = router.net_class(z.GetNetname())
        islands = []
        for i in range(fp.OutlineCount()):
            o = fp.Outline(i)
            cells = set()
            for k in range(o.PointCount()):
                q = o.CPoint(k)
                cx, cy = router.cell(mm(q.x), mm(q.y))
                if 0 <= cx < router.W and 0 <= cy < router.H:
                    cells.add((z.GetLayer(), cx, cy))
            islands.append(cells)
        islands.sort(key=len, reverse=True)
        for isl in islands[1:]:
            path = g.route(net, isl, islands[0], pcls, max_nodes=600000)
            if path:
                g.commit(z.GetNetname(), path, pcls)
                log["notes"].append(f"{z.GetZoneName()}: islands joined with a {pcls} track")
            else:
                log["failed"].append({"net": z.GetNetname(), "why": "pour islands could not be joined at the class width"})
        filler.Fill(board.Zones())
    geom.save(board)
    (geom.OUT / "m4").mkdir(parents=True, exist_ok=True)
    log["notes"].append(f"total {time.time() - t0:.0f} s")
    json.dump(log, open(geom.OUT / "m4" / "routing.json", "w"), indent=1)
    print("M4: routed", len(log["routed"]), "nets; pairs", [(p.get("net"), p.get("total_mm"), p["ok"]) for p in log["pairs"]],
          "; stitch vias", len(log["stitch"]), "; failed", len(log["failed"]), sorted({f["net"].rsplit("/", 1)[-1] for f in log["failed"]}))


if __name__ == "__main__":
    main()
