#!/usr/bin/env python3
"""M4: planes, the remaining routing, zone fill. Applied by tools/build_all.sh after m3_copy.py.

Order: planes defined (GND on In2 with the two inductor slots; the PWR plane In4 split into VBUS, P_IN, a 3V3 island,
the copied ADIN islands and Sofar's two no-net islands) → the bus feeds insert → inductor drawn by hand (BRIEF §6) →
the ADIN data pairs (Top + Internal 1 only) → stitching vias from every plane-net cluster into its plane → every other
net by the grid router (tools/router.py) → zone fill. Writes out/m4/routing.json with what was routed and how.
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
RIPUP_ROUNDS = 0       # rip-up rounds tried (they thrashed: the pocket's exits are the real limit; see LOG M4)
HAND_LINKS = True       # two hand-laid 0.15 mm links after the pairs (see hand_links)


def N(short):
    return NETS[short]


PAIR_LIMITS_SHORT = {"BM1_DATA_N": 9.5, "BM1_DATA_P": 9.5, "BM2_DATA_P": 21.3, "BM2_DATA_N": 21.3}   # inner pin first
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


def add_zone(board, layer, net_name, poly, name, priority, min_thick=0.25, clearance=0.25):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    if net_name:
        z.SetNet(board.FindNet(net_name))
    z.SetAssignedPriority(priority)
    z.SetMinThickness(MM(min_thick))
    z.SetLocalClearance(MM(clearance))
    z.SetThermalReliefGap(MM(0.254))
    z.SetThermalReliefSpokeWidth(MM(0.254))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetZoneName(name)
    for i in range(poly.OutlineCount()):
        z.Outline().AddOutline(poly.Outline(i))
        for k in range(poly.HoleCount(i)):
            z.Outline().AddHole(poly.Hole(i, k), i)
    board.Add(z)
    return z


def planes(board):
    """Return {net: polygon} of the plane zones so the stitching step can test 'inside'."""
    o = geom.OUTLINE
    outline = pcbnew.SHAPE_POLY_SET()
    board.GetBoardPolygonOutlines(outline)
    body = pcbnew.SHAPE_POLY_SET(outline)
    body.Deflate(MM(geom.EDGE_CLEARANCE), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, MM(0.01))
    # GND plane with one slot past each inductor: the island (inductor + its inserts, west) joins the rest of the plane
    # only on the far side from the inserts (east); slots 0.5 mm wide along the island's band-side edge.
    gnd = pcbnew.SHAPE_POLY_SET(body)
    slots = [(o["x0"], 26.2, 22.7, 26.7),      # port 2 island south edge (above U1's pins, y ≥ 28.2)
             (o["x0"], 6.5, 22.7, 7.0),         # port 2 island north edge (north band stays with the main plane)
             (o["x0"], 39.0, 22.7, 39.5),       # port 1 island north edge, south of the port-2 pair's crossing at y ≈ 38
             (o["x0"], 54.0, 22.7, 54.5)]       # port 1 island south edge
    for s in slots:
        gnd.BooleanSubtract(router_rect(s))
    gnd.Simplify()
    add_zone(board, pcbnew.In2_Cu, "GND", gnd, "GND plane (In2): island per inductor, slots per the mote", 0, 0.25, 0.25)
    log["planes"]["GND"] = {"layer": "In2", "slots": slots, "note": "islands x -7.5..22.7, y 7-26.2 (port 2) and 39.5-54 (port 1), open to the east"}
    # PWR plane In4
    vbus = poly_from_rects([(23.2, 0.5, 38.0, 64.5), (o["x0"], 26.0, 23.2, 64.5), (16.8, 8.0, 23.2, 26.0)])
    vbus.BooleanIntersection(body)
    p_in = poly_from_rects([(11.0, 8.0, 16.6, 25.7)])     # R8 straddles the P_IN / VBUS boundary at x ≈ 16.6
    v3 = poly_from_rects([(33.4, 8.0, 38.0, 23.0)])
    vbus.BooleanSubtract(poly_from_rects([(33.1, 7.7, 38.3, 23.3)]))
    vbus.Simplify()
    nc2 = poly_from_rects([(3.5, 13.5, 9.5, 20.0)])
    nc1 = poly_from_rects([(3.5, 45.0, 9.5, 51.5)])
    add_zone(board, pcbnew.In4_Cu, "VBUS", vbus, "VBUS plane (In4)", 0, 0.25, 0.25)
    add_zone(board, pcbnew.In4_Cu, N("P_IN"), p_in, "P_IN island (In4) under port 2 east", 5, 0.25, 0.25)
    add_zone(board, pcbnew.In4_Cu, "3V3", v3, "3V3 island (In4) at the 3.3 V buck output", 5, 0.25, 0.25)
    add_zone(board, pcbnew.In4_Cu, None, nc2, "NoConnect_P2 (In4, no net: Sofar Q10)", 6, 0.25, 0.25)
    add_zone(board, pcbnew.In4_Cu, None, nc1, "NoConnect_P1 (In4, no net: Sofar Q10)", 6, 0.25, 0.25)
    log["planes"]["In4"] = {"VBUS": "strip x 23.2-38 full height + west half y 26-64.5 (ADIN islands cut it, priority 7)",
                            "P_IN": [11.0, 8.0, 16.6, 25.7], "VBUS east of P_IN": [16.8, 8.0, 23.2, 26.0], "3V3": [33.4, 8.0, 38.0, 23.0],
                            "NoConnect": [[3.5, 13.5, 9.5, 20.0], [3.5, 45.0, 9.5, 51.5]]}
    # the copied ADIN islands keep Sofar's priority 7: VBUS (0) flows around them
    # 5 V to the Pi as a bottom-side pour (BRIEF §6: ≥ 1.0 mm or a pour) from L6's output to JP1 beside J1
    pi5 = poly_from_rects([(29.7, 7.5, 38.0, 26.5)])
    add_zone(board, pcbnew.B_Cu, N("5V_PI"), pi5, "5V_PI pour (B.Cu) L6 -> JP1", 3)
    log["planes"]["5V_PI"] = [29.7, 7.5, 38.0, 26.5]
    # The stitching tests "inside the plane" against the FILLED copper (QE S7.b F1: vias in a sliver or in a cleared
    # spot around other copper reached no plane), deflated 0.15 mm so the via's copper lands well inside the fill.
    # The planes sit on In2 / In4 where nothing else is routed, so this fill stays valid while the signals are laid.
    # polys[net] = (outline, layer, fill): "already connected" is tested against the OUTLINE (a pad inside it joins the
    # plane through its thermal spokes), via spots against the FILL (deflated 0.15 mm so the via lands in solid copper).
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    polys = {}
    wanted = {("GND", pcbnew.In2_Cu), ("VBUS", pcbnew.In4_Cu), (N("P_IN"), pcbnew.In4_Cu), ("3V3", pcbnew.In4_Cu), (N("5V_PI"), pcbnew.B_Cu),
              (N("ADIN_AVDD"), pcbnew.In4_Cu), (N("ADIN_VDDIO"), pcbnew.In4_Cu)}
    for z in board.Zones():
        if z.GetIsRuleArea() or not z.GetNetname():
            continue
        if (z.GetNetname(), z.GetLayer()) in wanted:       # the planes and islands above (not Sofar's copied Top pours)
            layer = z.GetLayer()
            outline = pcbnew.SHAPE_POLY_SET(z.Outline())
            fill = pcbnew.SHAPE_POLY_SET(z.GetFilledPolysList(layer))
            fill.Deflate(MM(0.15), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, MM(0.01))
            if z.GetNetname() in polys:       # several zones of one net: union
                polys[z.GetNetname()][0].BooleanAdd(outline)
                polys[z.GetNetname()][2].BooleanAdd(fill)
            else:
                polys[z.GetNetname()] = (outline, layer, fill)
    return polys


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
    """A via or through pad inside the plane, or copper on the plane's own layer inside it (bottom pour)."""
    poly, layer = plane[0], plane[1]
    for it in cluster:
        cls = it.GetClass()
        if cls == "PCB_VIA" or (cls == "PAD" and it.GetDrillSize().x > 0):
            if poly.Contains(it.GetPosition()):
                return True
        elif cls == "PAD" and it.IsOnLayer(layer) and poly.Contains(it.GetPosition()):
            return True
        elif cls == "PCB_TRACK" and it.GetLayer() == layer and poly.Contains(it.GetStart()) and poly.Contains(it.GetEnd()):
            return True
    return False


def hand_links(g, board):
    """Two links the grid router cannot find (0.15 mm, BRIEF's fan-out width), laid after the pairs:
    U3's 3V3 out of the ADIN pocket on Internal 2, threaded between Sofar's copied vias (≥ 0.15 mm from each, ≥ 4.8 mm
    from MP1), and U11 pin 7 → R34 (ISET) past U11's pin 6."""
    # U3's 3V3 leaves the pocket from Sofar's copied via west of U3 (at (-5.5, 38.65); QE S7.b F4: the old lookup
    # radius missed it, so the escape was never laid). The router finds the lane east to x = 2.5 on Internal 2 while
    # the pocket is still empty; the plane leftovers step joins it to the 3V3 island later.
    v3 = next((t for t in board.GetTracks() if t.GetClass() == "PCB_VIA" and t.GetNetname() == "3V3" and geom.dist(geom.xy(t.GetPosition()), (-5.5, 38.65)) < 0.6), None)
    if v3 is not None:
        a = geom.xy(v3.GetPosition())
        net = g.netcode["3V3"]
        start = {(pcbnew.In3_Cu,) + router.cell(*a)}
        goal = {(pcbnew.In3_Cu,) + router.cell(2.5, y) for y in (37.5, 38.0, 38.5)}
        path = g.route(net, start, goal, "thin", layers=[pcbnew.In3_Cu], max_nodes=200000, via_ok=False)
        if path is None:
            path = g.route(net, start, goal, "thin", max_nodes=400000)
        if path is not None:
            nt, nv, L = g.commit("3V3", path, "thin")
            log["manual"].append({"net": "3V3", "from": a, "to": [2.5, 38.0], "width": 0.15, "layer": "Internal 2 (router, thin class)", "length_mm": round(L, 2), "why": "U3's 3V3 out of the ADIN pocket before the pocket's signals"})
        else:
            log["failed"].append({"net": "3V3", "why": "no lane out of the pocket for U3's 3V3 escape (hand link)", "near": [a]})
    else:
        log["failed"].append({"net": "3V3", "why": "U3's 3V3 via near (-5.5, 38.65) not found", "near": []})
    fps = geom.fp_by_ref(board)
    p7 = next(p for p in fps["U11"].Pads() if p.GetNumber() == "7")
    p2 = next(p for p in fps["R34"].Pads() if p.GetNumber() == "2")
    a, b2 = geom.xy(p7.GetPosition()), geom.xy(p2.GetPosition())
    pts = [a, (34.5, a[1]), (34.5, 56.2), b2]
    for s, e in zip(pts, pts[1:]):
        g.add_track(N("ISET"), s, e, pcbnew.F_Cu, 0.15)
    log["manual"].append({"net": "ISET", "path": pts, "width": 0.15, "layer": "Top", "why": "U11 pin 7 to R34 past pin 6"})
    # U11 pin 1 (VBUS, the top pin of the west column): straight north into a via on the VBUS plane
    p1 = next(p for p in fps["U11"].Pads() if p.GetNumber() == "1")
    a = geom.xy(p1.GetPosition())
    g.add_track("VBUS", a, (a[0], 52.55), pcbnew.F_Cu, 0.15)
    g.add_via("VBUS", (a[0], 52.55), 0.45, 0.2)
    log["manual"].append({"net": "VBUS", "path": [a, (a[0], 52.55)], "width": 0.15, "layer": "Top", "why": "U11 pin 1 into the VBUS plane north of the pin"})


def route_net(g, board, net_name, cls=None, layers=None, max_nodes=400000, plane_poly=None, via_cost=12.0, bus_exempt_ok=False):
    """Join the net's clusters by tracks: nearest pairs first, other pairings on failure, the brief's 0.15 mm
    fan-out class as a last resort. Clusters already on the net's plane count as one."""
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
    while len(clusters) > 1:
        a = clusters[0]
        ca = router.centroid(a)
        order = sorted(range(1, len(clusters)), key=lambda i: geom.dist(ca, router.centroid(clusters[i])))
        joined = False
        fallbacks = {"signal": ("thin",), "rail": ("thin",), "data": ("thin",), "power": ("power_n", "power_t"),
                     "payload": ("power", "power_n", "power_t", "thin"), "pi5v": ("power", "power_n", "thin"), "bus": ("power",)}
        # "thin" (0.15 / 0.15) as the last resort of a power-class net is below the brief's 0.25 clearance: every such
        # link is reported by check_rules.py (REPORT §6 #11)
        for attempt_cls in (cls,) + fallbacks.get(cls, ()):
            s = router.cluster_cells(g, a, layers)
            for bi in order[:3]:
                t = router.cluster_cells(g, clusters[bi], layers)
                if not s or not t:
                    continue
                path = g.route(net, s, t, attempt_cls, layers=layers, max_nodes=max_nodes if attempt_cls == cls else max(max_nodes, 1500000), via_cost=via_cost)
                if path is None:
                    continue
                segs, vias, length = g.commit(net_name, path, attempt_cls)
                total += length
                if attempt_cls != cls:
                    log["notes"].append(f"{net_name.rsplit('/', 1)[-1]}: a link routed with the {attempt_cls} class ({router.CLASSES[attempt_cls][0]} mm)")
                clusters[0] = a + clusters[bi]
                del clusters[bi]
                joined = True
                break
            if joined:
                break
        if not joined and bus_exempt_ok and not g.bus_exempt:
            g.bus_exempt = True
            try:
                L = route_net(g, board, net_name, cls, layers, max_nodes, plane_poly, via_cost, bus_exempt_ok=False)
            finally:
                g.bus_exempt = False
            if L is not None:
                log["notes"].append(f"{net_name.rsplit('/', 1)[-1]}: routed at the Default 0.15 mm from bus copper (no lane at 0.35; DRC exclusion with reason, REPORT §6)")
                return total + L
            return None
        if not joined:
            log["failed"].append({"net": net_name, "why": "no path", "clusters": len(clusters)})
            return None
    return total


def gnd_links(g, board):
    """GND pads of one footprint within 1.0 mm of each other (U11's pins and its thermal pad, BGA balls): a straight
    0.15 mm link on the pad's layer when the line is clear. Done before the signals so no via has to sit beside them."""
    net = g.netcode["GND"]
    n = 0
    for f in board.GetFootprints():
        pads = [p for p in f.Pads() if p.GetNetname() == "GND" and p.GetDrillSize().x == 0]
        for i, a in enumerate(pads):
            for b2 in pads[i + 1:]:
                la = [l for l in router.ROUTE_LAYERS if a.IsOnLayer(l) and b2.IsOnLayer(l)]
                pa, pb = geom.xy(a.GetPosition()), geom.xy(b2.GetPosition())
                if not la or geom.dist(pa, pb) > 1.0:
                    continue
                steps = max(2, int(geom.dist(pa, pb) / 0.05))
                ok = True
                for k in range(steps + 1):
                    x, y = pa[0] + (pb[0] - pa[0]) * k / steps, pa[1] + (pb[1] - pa[1]) * k / steps
                    cx, cy = router.cell(x, y)
                    v = g.occ[la[0]][cy * router.W + cx]
                    if v not in (0, net):
                        ok = False
                        break
                if ok:
                    g.add_track("GND", pa, pb, la[0], 0.15)
                    n += 1
    log["notes"].append(f"{n} intra-footprint GND links (0.15 mm)")


def prestitch(g, board, plane, max_r=1.2, net_name="GND"):
    """A via next to every single-pad cluster of a plane net before the signals are routed (≤ 1.2 mm away, inside
    the plane's filled copper). GND uses the rail via (0.5/0.25), the power nets their class via."""
    poly, layer, fill = plane
    net = g.netcode[net_name]
    pcls = "rail" if net_name == "GND" else router.net_class(net_name)
    width, clear, vdia, vdrill = router.CLASSES[pcls]
    rv = g.radius_for(vdia, clear)
    n = 0
    for cluster in router.net_clusters(board, net_name):
        if plane_connected(cluster, plane) or len(cluster) != 1 or cluster[0].GetClass() != "PAD":
            continue
        pad = cluster[0]
        p = geom.xy(pad.GetPosition())
        if p[0] < 7.0 and 25.0 < p[1] < 40.0:
            continue          # the ADIN pocket: U1's SPI escapes need every free cell there; stitched after the signals
        if pad.m_Uuid.AsString() in g.exclude_ids:
            continue
        for spot in g.find_via_spots(net, p, rv, max_r=max_r, inside=fill, count=4, xr=g.xradii(net, vdia, clear)):
            cx, cy = router.cell(*spot)
            goals = {(l, cx, cy) for l in router.ROUTE_LAYERS}
            path = None
            for tcls in ((pcls, "power_n", "power_t") if pcls != "rail" else ("thin",)):
                path = g.route(net, g.pad_cells(pad), goals, tcls, max_nodes=20000)
                if path is not None:
                    break
            if path is None:
                continue
            g.commit(net_name, path, tcls)
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
        fill = plane[2]
        net = g.netcode[net_name]
        cls0 = router.net_class(net_name)
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
            spots, cls = [], cls0
            for cls in (cls0, "power_n", "power_t", "thin") if cls0 in ("power", "pi5v", "payload", "bus") else (cls0, "thin"):
                width, clear, vdia, vdrill = router.CLASSES[cls]
                rv = g.radius_for(vdia, clear)
                for p in pts:
                    for sp in g.find_via_spots(net, p, rv, max_r=4.0, inside=fill, count=12, xr=g.xradii(net, vdia, clear)):
                        spots.append((geom.dist(sp, p), sp))
                if spots:
                    break
            if not spots:
                log["failed"].append({"net": net_name, "why": "no via spot in the plane within 3 mm", "near": pts[:3]})
                continue
            spots.sort()
            done = False
            for _, spot in spots[:16]:
                cx, cy = router.cell(*spot)
                goals = {(l, cx, cy) for l in router.ROUTE_LAYERS}
                path = None
                for pcls in (cls, "power_n", "power_t", "thin") if cls in ("power", "pi5v", "payload", "bus") else (cls, "thin"):
                    path = g.route(net, router.cluster_cells(g, cluster), goals, pcls, max_nodes=200000)
                    if path is not None:
                        break
                if path is None:
                    continue
                g.commit(net_name, path, pcls)
                g.add_via(net_name, spot, vdia, vdrill)
                if pcls != cls0:
                    log["notes"].append(f"{net_name.rsplit('/', 1)[-1]}: stitched with the {pcls} class")
                done = True
                break
            if not done:
                log["failed"].append({"net": net_name, "why": "no path to any of the stitching via spots", "near": pts[:3]})
                continue
            log["stitch"].append({"net": net_name.rsplit("/", 1)[-1], "via": [round(spot[0], 2), round(spot[1], 2)]})


def main():
    t0 = time.time()
    board = geom.load()
    for i in range(board.GetNetInfo().GetNetCount()):
        ni = board.GetNetInfo().GetNetItem(i)
        if ni and ni.GetNetname():
            NETS[ni.GetNetname().rsplit("/", 1)[-1]] = ni.GetNetname()
    PAIR_LIMITS = {N(k): v for k, v in PAIR_LIMITS_SHORT.items()}
    polys = planes(board)
    g = router.Grid(board)
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
    # PI_5V: JP1 → J1 pins 2/4 (5V_PI itself is the bottom pour + stitching vias)
    L = route_net(g, board, N("PI_5V"), "pi5v")
    log["routed"].append({"net": "PI_5V", "class": "pi5v", "length_new_mm": None if L is None else round(L, 1)})
    # data pairs on Top + Internal 1 only, with the mote's length limits (copied stubs count)
    for net, limit in PAIR_LIMITS.items():
        L = route_net(g, board, net, "data", layers=[pcbnew.F_Cu, pcbnew.In1_Cu], via_cost=4.0, max_nodes=1500000)
        total = sum(mm(t.GetLength()) for t in board.GetTracks() if t.GetNetname() == net and t.GetClass() != "PCB_VIA")
        log["pairs"].append({"net": net.rsplit("/", 1)[-1], "new_mm": None if L is None else round(L, 2), "total_mm": round(total, 2), "limit_mm": limit, "ok": L is not None and total <= limit})
    if HAND_LINKS:
        hand_links(g, board)
    # 1V8 from the 1.8 V buck (B18, beside J1) to U2 in the ADIN pocket: its lane crosses the port-1 leg area, so it
    # goes before the legs; last resort: the Default 0.15 mm from bus copper (declared, DRC exclusion with reason)
    L = route_net(g, board, N("1V8"), bus_exempt_ok=True)
    log["routed"].append({"net": "1V8", "class": router.net_class(N("1V8")), "length_new_mm": None if L is None else round(L, 1)})
    # bus data legs (inductor cluster → T1/T2 pins 6/7, 0.2 mm as the mote) and the payload path
    for net in (N("BM1_P"), N("BM1_N"), N("BM2_P"), N("BM2_N")):
        L = route_net(g, board, net, "signal")
        log["routed"].append({"net": net.rsplit("/", 1)[-1], "class": "signal (data leg; 0.35 from non-bus copper by the kind map)", "length_new_mm": None if L is None else round(L, 1)})
    L = route_net(g, board, N("VBUS_OUT"), "payload")
    log["routed"].append({"net": "VBUS_OUT", "class": "payload", "length_new_mm": None if L is None else round(L, 1)})
    # GND pads of one footprint joined; lonely GND pads given their via now; then the signals, then the rest of the stitching
    gnd_links(g, board)
    prestitch(g, board, polys["GND"])
    for pn in ("VBUS", N("P_IN"), "3V3", N("5V_PI")):
        if pn in polys and pn in g.netcode:
            prestitch(g, board, polys[pn], net_name=pn)
    done = set(PAIR_LIMITS) | {N(s) for s in ("5V_PI", "PI_5V", "VBUS_OUT", "BM1_P", "BM1_N", "BM2_P", "BM2_N")}
    nets = []
    for i in range(board.GetNetInfo().GetNetCount()):
        ni = board.GetNetInfo().GetNetItem(i)
        if ni and ni.GetNetname() and not ni.GetNetname().startswith("unconnected-") and ni.GetNetname() not in done and ni.GetNetname() not in polys:
            nets.append(ni.GetNetname())
    # the ADIN pocket has few exits (the west-edge lane, the north and south strips, under U1): its nets go first,
    # then U11's west-side pins, which share one 1.9 mm corridor beside J1's pin tails
    # 1V8 first: its only lane from the 1.8 V buck (B18) to U1 runs between L1's bus copper (0.35 mm rule) and J1
    for short in ("PAYLOAD_EN", "~{PAYLOAD_FAULT}", "Net-(U11-UVLO)", "ISET"):
        net = N(short)
        if net in nets or net in polys:
            if net in nets:
                nets.remove(net)
            L = route_net(g, board, net, plane_poly=polys.get(net))
            log["routed"].append({"net": short, "class": router.net_class(net), "length_new_mm": None if L is None else round(L, 1)})
    # short nets first
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
        log["routed"].append({"net": net.rsplit("/", 1)[-1], "class": router.net_class(net), "length_new_mm": None if L is None else round(L, 1)})
    # rip-up and retry: a net with no path gets the nets crowding its area removed, the grid rebuilt, itself routed
    # first and the ripped nets after it (up to three rounds)
    for rnd in range(RIPUP_ROUNDS):
        failed = [f["net"] for f in log["failed"] if f["why"] == "no path"]
        if not failed:
            break
        log["failed"] = [f for f in log["failed"] if f["why"] != "no path"]
        rip = set()
        for fnet in failed:
            # only the hard end: the failing net's smallest cluster (its pad fan-out), not the whole net
            cls_ = sorted(router.net_clusters(board, fnet), key=len)
            boxes = []
            for c in cls_[:2]:
                xs = [mm(i.GetPosition().x) for i in c]
                ys = [mm(i.GetPosition().y) for i in c]
                boxes.append((min(xs) - 2.0, min(ys) - 2.0, max(xs) + 2.0, max(ys) + 2.0))
            for onet, items in g.made.items():
                if onet == fnet or onet in ("GND",) or onet in PAIR_LIMITS or any(onet.endswith(s) for s in ("BM1_P", "BM1_N", "BM2_P", "BM2_N")):
                    continue
                for it in items:
                    q = geom.xy(it.GetPosition())
                    if any(b[0] <= q[0] <= b[2] and b[1] <= q[1] <= b[3] for b in boxes):
                        rip.add(onet)
                        break
        for onet in rip:
            for it in g.made.pop(onet, []):
                board.Remove(it)
        log["notes"].append(f"rip-up round {rnd + 1}: {[n.rsplit('/', 1)[-1] for n in failed]} failed; ripped {[n.rsplit('/', 1)[-1] for n in rip]}")
        made_before = g.made
        g = router.Grid(board)
        g.made = {k: v for k, v in made_before.items()}
        for net in failed + sorted(rip):
            L = route_net(g, board, net, plane_poly=polys.get(net), max_nodes=800000)
            log["routed"].append({"net": net.rsplit("/", 1)[-1], "class": router.net_class(net) + f" (retry {rnd + 1})", "length_new_mm": None if L is None else round(L, 1)})
    stitch(g, board, polys)
    # plane nets' leftovers (clusters the stitching could not reach): tracks to the plane-connected super-cluster
    for net, plane in polys.items():
        if net in g.netcode:
            L = route_net(g, board, net, plane_poly=plane, max_nodes=1200000)
            log["routed"].append({"net": net.rsplit("/", 1)[-1], "class": router.net_class(net) + " (plane leftovers)", "length_new_mm": None if L is None else round(L, 1)})
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    # a pour split into islands by other copper: join the islands with tracks, then refill
    for z in board.Zones():
        if z.GetIsRuleArea() or not z.GetNetname() or z.GetLayer() not in router.ROUTE_LAYERS:
            continue
        fp = z.GetFilledPolysList(z.GetLayer())
        if fp.OutlineCount() <= 1:
            continue
        net = g.netcode[z.GetNetname()]
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
            path = None
            for pcls in ("pi5v", "power", "power_n"):
                path = g.route(net, isl, islands[0], pcls, max_nodes=600000)
                if path:
                    g.commit(z.GetNetname(), path, pcls)
                    log["notes"].append(f"{z.GetZoneName()}: islands joined with a {pcls} track")
                    break
            if path is None:
                log["failed"].append({"net": z.GetNetname(), "why": "pour islands could not be joined"})
        filler.Fill(board.Zones())
    geom.save(board)
    (geom.OUT / "m4").mkdir(parents=True, exist_ok=True)
    log["notes"].append(f"total {time.time() - t0:.0f} s")
    json.dump(log, open(geom.OUT / "m4" / "routing.json", "w"), indent=1)
    print("M4: routed", len(log["routed"]), "nets; pairs", [(p["net"], p["total_mm"], p["ok"]) for p in log["pairs"]],
          "; stitch vias", len(log["stitch"]), "; failed", len(log["failed"]), sorted({f["net"].rsplit("/", 1)[-1] for f in log["failed"]}))


if __name__ == "__main__":
    main()
