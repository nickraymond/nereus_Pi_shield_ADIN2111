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


PAIRS = {    # port: (P net, N net, U1 pins (P, N), T pads (P, N), length limit per net (mote)); the pins' outward direction and
    1: ("BM1_DATA_P", "BM1_DATA_N", ("U1", "28", "27"), ("T1", "1", "2"), 9.5),      # the pads' inward direction are read from
    2: ("BM2_DATA_P", "BM2_DATA_N", ("U1", "5", "4"), ("T2", "1", "2"), 21.3),      # the placement (axis_dir)
}


def axis_dir(frm, to):
    """The axis-aligned unit vector from `frm` to `to` (the larger component wins)."""
    dx, dy = to[0] - frm[0], to[1] - frm[1]
    if abs(dx) >= abs(dy):
        return (1 if dx > 0 else -1, 0)
    return (0, 1 if dy > 0 else -1)
# corridor preferences (OPTIONS §2.3): {layer: cost multiplier}; a layer not listed costs 1.0
PREF_I3 = {I3: 1.0, I1: 1.5, F: 2.5, B: 2.5}
PREF_I1 = {I1: 1.0, I3: 1.5, F: 2.5, B: 2.5}
PREF_TOP = {F: 1.0, I1: 1.5, I3: 1.5, B: 1.5}
PREF_BOT = {B: 1.0, I3: 1.4, I1: 1.5, F: 2.0}
log = {"planes": {}, "manual": [], "pairs": [], "stitch": [], "routed": [], "failed": [], "notes": []}
ADIN_AREA = None   # (x0, y0, x1, y1) of the ADIN block's parts, set in main
PLANE_CLR = 0.3    # inner planes keep 0.3 from other copper and holes: JLCPCB's inner PTH hole-to-copper 0.3 (DFM.md row 12; was 0.25)


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
    if layer in (pcbnew.F_Cu, pcbnew.B_Cu) and hasattr(pcbnew, "ISLAND_REMOVAL_MODE_ALWAYS"):
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)     # an outer-pour island with no via is dropped by the fill (REPORT §6 #1)
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
    e2, e1 = geom.ENVELOPES["L2"], geom.ENVELOPES["L1"]
    slots = [(o["x0"], e2[3] + 1.7, 22.7, e2[3] + 2.2),      # port 2 island south edge (y 26.2–26.7: north of the band)
             (o["x0"], e2[1] - 2.5, 22.7, e2[1] - 2.0),      # port 2 island north edge (north band stays with the main plane)
             (o["x0"], e1[1] + 2.5, 22.7, e1[1] + 3.0),      # port 1 island north edge (y 42.0–42.5: south of the band and the port-1 pair)
             (o["x0"], e1[3] + 2.0, 22.7, e1[3] + 2.5)]      # port 1 island south edge
    for s in slots:
        gnd.BooleanSubtract(router_rect(s))
    gnd.Simplify()
    add_zone(board, pcbnew.In2_Cu, "GND", gnd, "GND plane (In2): island per inductor, slots per the mote", 0, 0.25, PLANE_CLR)
    log["planes"]["GND"] = {"layer": "In2", "slots": slots, "note": "islands x -7.5..22.7 around each inductor + its inserts, open to the east"}
    # PWR plane In4: VBUS everywhere but the P_IN island under port 2's centre, the 3V3 island at the 3.3 V buck's
    # output (moved with the cell: x 33.4-38, y 24-38), the copied ADIN islands (priority 7) and Sofar's two no-net islands
    x1, y1 = o["x1"] - 0.5, o["y1"] - 0.5
    vbus = poly_from_rects([(23.2, 0.5, x1, y1), (o["x0"], 26.0, 23.2, y1), (16.8, 8.0, 23.2, 26.0)])
    vbus.BooleanIntersection(body)
    p_in = poly_from_rects([(11.0, 8.0, 16.6, 25.7)])     # R8 straddles the P_IN / VBUS boundary at x ≈ 16.6
    v3 = poly_from_rects([(33.4, 24.0, x1, 38.0)])
    vbus.BooleanSubtract(poly_from_rects([(33.1, 23.7, x1 + 0.3, 38.3)]))
    vbus.Simplify()
    nc2 = poly_from_rects([(3.5, e2[1] + 4.5, 9.5, e2[1] + 11.0)])
    nc1 = poly_from_rects([(3.5, e1[1] + 5.5, 9.5, e1[1] + 12.0)])
    add_zone(board, pcbnew.In4_Cu, "VBUS", vbus, "VBUS plane (In4)", 0, 0.25, PLANE_CLR)
    add_zone(board, pcbnew.In4_Cu, N("P_IN"), p_in, "P_IN island (In4) under port 2 east", 5, 0.25, PLANE_CLR)
    add_zone(board, pcbnew.In4_Cu, "3V3", v3, "3V3 island (In4) at the 3.3 V buck output", 5, 0.25, PLANE_CLR)
    add_zone(board, pcbnew.In4_Cu, None, nc2, "NoConnect_P2 (In4, no net: Sofar Q10)", 6, 0.25, PLANE_CLR)
    add_zone(board, pcbnew.In4_Cu, None, nc1, "NoConnect_P1 (In4, no net: Sofar Q10)", 6, 0.25, PLANE_CLR)
    log["planes"]["In4"] = {"VBUS": "strip x 23.2-38 full height + west half y 26-64.5 (ADIN islands cut it, priority 7)",
                            "P_IN": [11.0, 8.0, 16.6, 25.7], "VBUS east of P_IN": [16.8, 8.0, 23.2, 26.0], "3V3": [33.4, 24.0, x1, 38.0],
                            "NoConnect": [[3.5, 13.5, 9.5, 20.0], [3.5, 45.0, 9.5, 51.5]]}
    # 5 V to the Pi: a bottom-side pour under JP1 / L6 for the output caps (BRIEF §6: ≥ 1.0 mm or a pour); the links
    # L6 → JP1 → J1 pins 2/4 are 1.0 mm top-layer tracks (OPTIONS Q3)
    # (the pour reaches under the 5 V cell's bottom-side dividers R37-R40 / C53 / C54 at y 21-24, which split it into
    # islands; session 2: each island gets a via into the copied Top output pour where that covers it (zone_stitch,
    # other_layer_copper) instead of a 1.0 mm track; the divider's tap R37.1 is one of those islands)
    pi5 = poly_from_rects([(29.7, 7.5, x1, 24.0)])
    add_zone(board, pcbnew.B_Cu, N("5V_PI"), pi5, "5V_PI pour (B.Cu) under JP1 / L6 / U10", 3, solid=True)
    # and the same rectangle on Internal 2, as the mote carries the buck's output on a plane island (3V3 on In4): the
    # bottom pour's islands (the dividers R37-R40 cut it) each get a via into this patch (zone_stitch), and the patch
    # keeps 0.25 mm from the few Internal 2 tracks that cross the strip's north end
    add_zone(board, pcbnew.In3_Cu, N("5V_PI"), poly_from_rects([(29.7, 7.5, x1, 24.0)]), "5V_PI patch (In3) under the 5 V cell", 3, 0.25, 0.25)
    log["planes"]["5V_PI"] = {"B.Cu pour": [29.7, 7.5, x1, 24.0], "In3 patch": [29.7, 7.5, x1, 24.0]}
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


def bus_feeds(g, board):
    """Insert ring → inductor bus pad, 1.5 mm wide on Top (BRIEF §6: ≥ 1.0 mm, short and wide). From 3.31 mm east of the
    insert's centre (inside Sofar's arc, r 2.43–3.63; the track's round end then stays 0.36 mm from the Ø4.4 hole: JLCPCB
    NPTH-to-track 0.2, board 0.25, DFM.md row 13) to the inductor's pad of that net, with one bend 2.5 mm out."""
    pads = {}
    for ref in ("L1", "L2"):
        for p in geom.fp_by_ref(board)[ref].Pads():
            if p.GetNetname().rsplit("/", 1)[-1] in geom.INSERT_NET.values():
                pads[p.GetNetname().rsplit("/", 1)[-1]] = geom.xy(p.GetPosition())
    for ref, (ix, iy) in geom.INSERTS.items():
        net = geom.INSERT_NET[ref]
        name = N(net)
        a = (ix + 3.31, iy)
        b = pads[net]
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


PAIR_START_RUN = 0.5     # mm of straight virtual track leaving the pins beyond the 0.5 mm pin stub (the tracks leave the pins straight)
PAIR_PAD_RUN = 0.6       # mm from a T pad's centre to its near edge (the pads are 1.2 mm long): the pitch is reached there
PAIR_STAGGER = 0.33      # least distance between the pins' two vias along the exit direction: with the 0.5 mm pin pitch the centres are 0.6 apart (0.45 vias, 0.15 gap)
PAIR_MARGIN = 0.3        # session 2.b (QE round 2 N2): a pair is kept under the mote's length by at least this much when any candidate manages it


def pair_check(board, P, Nn, pins_pads):
    """The emitted pair, checked on the board (trust the artifact): each net one cluster from its pin to its pad,
    and every P item ≥ 0.15 mm from every N item on each shared layer (pads of one footprint excepted: Sofar's T pads
    are 0.24 mm apart). Returns (ok, [problems])."""
    probs = []
    cl = {}
    for name in (P, Nn):
        cl[name] = router.net_clusters(board, name)
        if len(cl[name]) != 1:
            probs.append(f"{name.rsplit('/', 1)[-1]}: {len(cl[name])} clusters (sizes {[len(c) for c in cl[name]]})")
    ip = [it for c in cl[P] for it in c]
    inn = [it for c in cl[Nn] for it in c]
    worst = 9.0
    for a in ip:
        for b in inn:
            if a.GetClass() == "PAD" and b.GetClass() == "PAD":
                continue
            common = router.item_layers(a) & router.item_layers(b)
            for l in common:
                dd = mm(a.GetEffectiveShape(l).GetClearance(b.GetEffectiveShape(l)))
                if dd < worst:
                    worst = dd
                if dd < 0.149:
                    pa = geom.xy(a.GetPosition())
                    probs.append(f"{a.GetClass()[4:] or 'PAD'} {P.rsplit('/', 1)[-1]} vs {b.GetClass()[4:] or 'PAD'} {Nn.rsplit('/', 1)[-1]} on {board.GetLayerName(l)} at ({pa[0]:.2f}, {pa[1]:.2f}): {dd:.3f} mm")
    return (not probs), probs, worst


def route_pairs(g, board):
    """Each ADIN pair as a coupled pair (router.route_pair / commit_pair): the virtual track leaves U1's two pins
    straight (0.5 mm pin stub + PAIR_START_RUN), is routed on Top + Internal 1 to the approach point A' 1.4 mm in
    front of the T pads (on either layer: a path still on Internal 1 there gets its via pair beside the approach), and
    from A' runs straight into the pads, spreading to their pitch (commit_pair, dir_in).
    The pads' approach lane and the pins' stub are forbidden cells, so the path cannot cross them. One swap via where
    the pin and pad order demand it (pair_parity). The emitted copper is checked on the board (pair_check) and taken
    off again if it fails; the other swing side is tried next, then the pair is reported open."""
    fps_ = geom.fp_by_ref(board)
    for port, (pn, nn, (uref, up, un), (tref, tp, tn), limit) in PAIRS.items():
        P, Nn = N(pn), N(nn)
        pins = (geom.xy(pad_of(board, uref, up).GetPosition()), geom.xy(pad_of(board, uref, un).GetPosition()))
        pads = (geom.xy(pad_of(board, tref, tp).GetPosition()), geom.xy(pad_of(board, tref, tn).GetPosition()))
        pin_mid = ((pins[0][0] + pins[1][0]) / 2, (pins[0][1] + pins[1][1]) / 2)
        pad_mid = ((pads[0][0] + pads[1][0]) / 2, (pads[0][1] + pads[1][1]) / 2)
        dir_out = axis_dir(geom.xy(fps_[uref].GetPosition()), pin_mid)       # out of U1 through the pins
        dir_in = axis_dir(pad_mid, geom.xy(fps_[tref].GetPosition()))        # into the transformer through its data pads
        log["notes"].append(f"pair port {port}: pins out {dir_out}, pads in {dir_in}")
        S = (pin_mid[0] + 0.5 * dir_out[0], pin_mid[1] + 0.5 * dir_out[1])                     # 0.1 mm past the pins' ends
        S1 = (S[0] + PAIR_START_RUN * dir_out[0], S[1] + PAIR_START_RUN * dir_out[1])          # a Top start: the A* starts here
        # the approach: A' (the A* goal, on Top or Internal 1) → 0.3 mm straight → A (the via pair when the path is on
        # Internal 1) → the splay → B (the pads' near edge) → the pad centres (router.commit_pair)
        parity = router.Grid.pair_parity(pins, pads, dir_out, dir_in)
        net = g.netcode[P]           # == g.netcode[Nn]: the pair is one net to the grid (Grid merge)
        # either end may hold a via pair beside the stub / the approach (vias at ±0.325, checked on every layer here,
        # since commit_pair places them blind): then the A* may start / end on Internal 1 there and the swap is the only
        # figure it places on the way. Port 1 (session 2): the end pair would land in the crystal's bottom pad, so the
        # pair starts with vias at the pins (as Sofar's mote) and arrives at T1 on Top.
        width, clear, vdia, vdrill = router.CLASSES["pair"]
        rv1 = g.radius_for(router.PAIR_VIA, clear)
        hwv1 = int(math.ceil(router.PAIR_VIA / 2 / router.PITCH))
        xrv1 = g.xradii(net, router.PAIR_VIA, clear)
        rt = g.radius_for(width, clear)
        hwt = int(math.ceil(width / 2 / router.PITCH))
        xrt = g.xradii(net, width, clear)

        def via_pair_ok(c, u):
            n_ = (u[1], -u[0])
            return all(g.via_free(*router.cell(c[0] + sg * 0.325 * n_[0], c[1] + sg * 0.325 * n_[1]), rv1, net, hwv1, xrv1, router.PAIR_VIA, clear, router.PAIR_VIA_DRILL) for sg in (1, -1))

        n_out = (dir_out[1], -dir_out[0])
        # start variants: (label, start cells, forbidden lane, cells to prepend to the path, start vias)
        variants = [("Top", {(F,) + router.cell(*S1)}, router.Grid.lane_cells(pin_mid, (S1[0] - 0.15 * dir_out[0], S1[1] - 0.15 * dir_out[1]), 0.9),
                     router.Grid.straight_cells(F, S, S1)[:-1], None)]
        # the pins' vias, staggered along dir_out (two 0.45 vias need 0.6 mm between centres; the pins are 0.5 apart):
        # one net's via at L_near from its pin, the other's at L_near + PAIR_STAGGER; each stub straight out of its pin, each
        # Internal 1 leg straight on to S2 = the far via + 0.3 mm; everything checked exactly, then S2's cell for the A*
        pin_of = {P: pins[0], Nn: pins[1]}
        found_start = None

        def via_ok(name, L):
            v = (pin_of[name][0] + L * dir_out[0], pin_of[name][1] + L * dir_out[1])
            return g.via_free(*router.cell(*v), rv1, net, hwv1, xrv1, router.PAIR_VIA, clear, router.PAIR_VIA_DRILL) and g.seg_free_exact(F, pin_of[name], v, router.PAIR_W, net, clear)
        for L_near in (0.8, 1.0, 1.3):
            for far_net in (P, Nn):
                near_net_ = Nn if far_net == P else P
                if not via_ok(near_net_, L_near):
                    continue
                # the far via: the first free spot ≥ PAIR_STAGGER beyond the near one (0.05 mm steps, ≤ 0.6 further)
                L_far = next((L for L in (L_near + PAIR_STAGGER + 0.05 * k for k in range(0, 7)) if via_ok(far_net, L)), None)
                if L_far is None:
                    continue
                sv = {near_net_: (pin_of[near_net_][0] + L_near * dir_out[0], pin_of[near_net_][1] + L_near * dir_out[1]),
                      far_net: (pin_of[far_net][0] + L_far * dir_out[0], pin_of[far_net][1] + L_far * dir_out[1])}
                S2 = (pin_mid[0] + (L_far + router.STRAIGHT_RUN * router.PITCH) * dir_out[0], pin_mid[1] + (L_far + router.STRAIGHT_RUN * router.PITCH) * dir_out[1])
                ok = True
                for name in (P, Nn):
                    v = sv[name]
                    along = (S2[0] - v[0]) * dir_out[0] + (S2[1] - v[1]) * dir_out[1]
                    q = (v[0] + along * dir_out[0], v[1] + along * dir_out[1])
                    ok = ok and g.seg_free_exact(I1, v, q, router.PAIR_W, net, clear)
                c2 = router.cell(*S2)
                ok = ok and g.free(I1, c2[0], c2[1], rt, net, hwt, xrt)
                if ok:
                    found_start = (L_near, L_far, far_net, sv, S2)
                    break
            if found_start:
                break
        if found_start:
            # the legs narrow to ±0.2 at S2 and run straight 0.3 mm more to S3, where the A* starts (a turn at S2 ran the
            # outer track 0.1 mm past the other net's leg end)
            L_near, L_far, far_net, sv, S2 = found_start
            S3 = (S2[0] + router.STRAIGHT_RUN * router.PITCH * dir_out[0], S2[1] + router.STRAIGHT_RUN * router.PITCH * dir_out[1])
            c3 = router.cell(*S3)
            if all(g.free(I1, cx, cy, rt, net, hwt, xrt) for _, cx, cy in router.Grid.straight_cells(I1, S2, S3)):
                variants.append((f"In1, vias at {L_near} / {L_far:.2f} mm from the pins ({far_net.rsplit('/', 1)[-1]} far)", {(I1,) + c3},
                                 router.Grid.lane_cells(pin_mid, (S3[0] - 0.15 * dir_out[0], S3[1] - 0.15 * dir_out[1]), 0.9),
                                 router.Grid.straight_cells(I1, S2, S3)[:-1], sv))
        # session 2.b (trial 8): a START SWAP. The pair leaves the pins straight (0.5 mm stub + 0.3 mm), makes its one swap
        # figure right there in the open (centre 1.7 mm out, ±0.9 along, swing ±0.6 beside; the neighbouring pins' pads end
        # 0.45 mm out), runs 1.2 mm straight on Internal 1 and only then hands over to the A*, which must place no figure
        # (parity 0). With the mote's compact U1 / T geometry (the pads 2–4 mm away at 45–60°) the mid-route swap figure
        # found its 2 mm of straight run only behind the pads (trials 5–7); here it has it by construction.
        for side in (1, -1):
            c0 = (S[0] + 1.2 * dir_out[0], S[1] + 1.2 * dir_out[1])
            c1 = (c0[0] + 1.2 * dir_out[0], c0[1] + 1.2 * dir_out[1])
            pre = router.Grid.straight_cells(F, S, c0) + [(I1,) + router.cell(*c0)] + router.Grid.straight_cells(I1, c0, c1)[1:]
            variants.append((f"start swap (side {side})", {pre[-1]}, router.Grid.lane_cells(pin_mid, (c1[0] - 0.15 * dir_out[0], c1[1] - 0.15 * dir_out[1]), 0.9),
                             pre[:-1], None, {router.cell(*c0): side}))
        # the approach: with an end via pair (at A = B − splay, beside the approach) the A* goal A' is 0.3 mm before A on
        # either layer; without one (the vias would not fit) the goal is A itself, on Top
        A = (pad_mid[0] - (PAIR_PAD_RUN + router.PAD_SPLAY) * dir_in[0], pad_mid[1] - (PAIR_PAD_RUN + router.PAD_SPLAY) * dir_in[1])
        end_vias = via_pair_ok(A, dir_in)
        if end_vias:
            A = (A[0] - router.STRAIGHT_RUN * router.PITCH * dir_in[0], A[1] - router.STRAIGHT_RUN * router.PITCH * dir_in[1])
        beyond = (pad_mid[0] + 1.5 * dir_in[0], pad_mid[1] + 1.5 * dir_in[1])
        a1 = (A[0] + 0.15 * dir_in[0], A[1] + 0.15 * dir_in[1])
        lane_end = router.Grid.lane_cells(a1, beyond, 0.9)           # the approach lane is forbidden to the A*
        # session 2.b (trial 5): the half-plane behind the pads is forbidden too (trial 6 also forbade the half-plane behind the
        # pins, which left port 2 no path at all). With
        # the mote's own U1 / T1 geometry (pins 2.2 mm west and 3.9 mm north of the pads, both facing east) the A* found
        # its 2 mm of straight run for the swap figure by going past the pads and turning back, and the two offset tracks
        # crossed at the U-turn (every candidate failed the board check). Sofar enters the pads from the body side with
        # vias; our emitter enters along the lane, so the path must stay on the pins' side of the pads.
        behind = set()
        for cx in range(router.W):
            for cy in range(router.H):
                x, y = router.pos(cx, cy)
                if (x - pad_mid[0]) * dir_in[0] + (y - pad_mid[1]) * dir_in[1] > 0.3:
                    behind.add((cx, cy))
        lane_end |= behind
        goals = {(F,) + router.cell(*A)} | ({(I1,) + router.cell(*A)} if end_vias else set())
        log["notes"].append(f"pair port {port}: start variants {[v[0] for v in variants]}; via pair at the pads' approach {'fits' if len(goals) > 1 else 'does not fit'}")
        # the swap figure makes the far track longer: try each start variant and swing side, shortest first, and keep
        # the first whose copper passes the board check
        cands = []
        for variant in variants:
            label, starts, lane_start, prefix, sv = variant[:5]
            pre_swaps = variant[5] if len(variant) > 5 else {}
            need = (parity + len(pre_swaps)) % 2
            for sides in ((1,), (-1,)):
                path, swaps = g.route_pair(net, starts, goals, need, layers=[F, I1], max_nodes=1500000, via_cost=8.0, sides=sides, forbid=lane_end | lane_start)
                if path is None:
                    continue
                swaps = {**pre_swaps, **swaps}
                Lp = (len(prefix) + len(path)) * router.PITCH + (0.5 if swaps else 0.0) + (0.0 if path[-1][0] == F else 0.3) + (0.0 if sv is None else 1.2)
                cands.append((Lp, f"{label}, swing {sides[0]}", prefix + path, swaps, sv))
                if pre_swaps:
                    break          # the A* places no figure here: the swing side is the prefix's
        if not cands:
            log["failed"].append({"net": pn, "why": f"pair port {port}: no path for the virtual track (parity {parity})"})
            log["pairs"].append({"port": port, "ok": False})
            continue
        # every candidate is emitted, checked on the board and measured, then taken off again; the one with the shortest
        # longer net among those that pass is emitted for good (the virtual path length does not tell which net gets
        # the far via / the outer corners)
        scored = []
        for Lp, side, full, swaps, sv in cands:
            stats = g.commit_pair((P, Nn), full, pins, pads, swaps, dir_in=dir_in, pad_run=PAIR_PAD_RUN, dir_out=dir_out, start_vias=sv)
            ok, probs, worst = pair_check(board, P, Nn, (pins, pads))
            Lmax = max(stats[P][2], stats[Nn][2])
            n_rm = g.remove_made([P, Nn])
            if ok:
                scored.append((Lmax, side, full, swaps, sv))
                log["notes"].append(f"pair port {port}: candidate {side}: passes the board check, P {stats[P][2]:.2f} / N {stats[Nn][2]:.2f} mm, min P-N clearance {worst:.3f}")
            else:
                log["notes"].append(f"pair port {port}: candidate {side} FAILED the board check ({probs[:3]}); {n_rm} items removed")
        if not scored:
            log["failed"].append({"net": pn, "why": f"pair port {port}: every candidate path failed the board check (parity {parity})"})
            log["pairs"].append({"port": port, "ok": False})
            continue
        scored.sort(key=lambda c: c[0])
        within = [c for c in scored if c[0] <= limit - PAIR_MARGIN]
        if scored[0][0] > limit - PAIR_MARGIN:
            log["notes"].append(f"pair port {port}: no candidate keeps the {PAIR_MARGIN} mm margin under the {limit} mm limit (best {scored[0][0]:.2f})")
        Lmax, side, full, swaps, sv = (within or scored)[0]
        stats = g.commit_pair((P, Nn), full, pins, pads, swaps, dir_in=dir_in, pad_run=PAIR_PAD_RUN, dir_out=dir_out, start_vias=sv)
        ok, probs, worst = pair_check(board, P, Nn, (pins, pads))
        log["notes"].append(f"pair port {port}: parity {parity}, {side}, starts on {board.GetLayerName(full[0][0])}, ends on {board.GetLayerName(full[-1][0])}, swap figures at {sorted((router.pos(*c), sd) for c, sd in swaps.items())}; board check {'ok' if ok else 'FAILED'}, min P-N clearance {worst:.3f} mm")
        log["notes"].append(f"pair port {port}: {stats}")
        for name in (P, Nn):
            total = sum(mm(t.GetLength()) for t in board.GetTracks() if t.GetNetname() == name and t.GetClass() != "PCB_VIA")
            vias = sum(1 for t in board.GetTracks() if t.GetNetname() == name and t.GetClass() == "PCB_VIA")
            log["pairs"].append({"net": name.rsplit("/", 1)[-1], "port": port, "total_mm": round(total, 2), "limit_mm": limit, "vias": vias,
                                 "ok": total <= limit, "parity": parity})


# where each regulator's fan-out via may go: anywhere but the two pairs' exit lanes (±1.5 mm beside each port's pin pair,
# 4 mm out from U1 along the pins' direction): the pairs leave U1 straight through those lanes (route_pairs) and route
# around whatever vias sit elsewhere. Session 2's pocket layout sent U2's vias to the exit's south-west corner by hand;
# trial 2 of the centre layout forbade the whole band along U1's port edges and left 3 of 4 balls without a spot.
def fanout_allowed(board, ref):
    fps = geom.fp_by_ref(board)
    u1 = geom.xy(fps["U1"].GetPosition())
    lanes = []
    for port, (pn, nn, (uref, up, un), *_rest) in PAIRS.items():
        a, b = geom.xy(pad_of(board, uref, up).GetPosition()), geom.xy(pad_of(board, uref, un).GetPosition())
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        lanes.append((mid, axis_dir(u1, mid)))

    def ok(x, y):
        for mid, (dx, dy) in lanes:
            along = (x - mid[0]) * dx + (y - mid[1]) * dy
            lat = abs((x - mid[0]) * dy - (y - mid[1]) * dx)
            if -0.5 <= along <= 4.0 and lat <= 1.5:
                return False
        return True
    return ok


FANOUT_REACH = {"U2": 2.6}


def fanout(g, board, refs=("U2", "U3"), max_r=1.7):
    """BGA fan-out first (session 2): every non-GND ball of these bottom-side regulators gets its via (within max_r,
    the net's class) before the pairs and the pocket's nets are routed. REPORT §6 #3 / the first M2 run of session 2:
    U2's 1V8 ball ended sealed on the bottom (U3's fan-out vias west, the 3V3 track south, the port-2 pair above) with
    no via spot left, so 1V8 and ADIN_PWR stayed open. The via is placed south / east / west of the ball, never north
    (the pair's lane along U1's south edge)."""
    n = 0
    fps = geom.fp_by_ref(board)
    for ref in refs:
        for pad in fps[ref].Pads():
            name = pad.GetNetname()
            if not name or name == "GND":
                continue
            cluster = next(c for c in router.net_clusters(board, name) if any(it.GetClass() == "PAD" and it.m_Uuid.AsString() == pad.m_Uuid.AsString() for it in c))
            if any(it.GetClass() == "PCB_VIA" or (it.GetClass() == "PAD" and it.GetDrillSize().x > 0) for it in cluster):
                continue          # Sofar's copper already takes this ball to a via
            cls = router.net_class(name)
            width, clear, vdia, vdrill = router.CLASSES[cls]
            net = g.netcode[name]
            rv = g.radius_for(vdia, clear)
            p = geom.xy(pad.GetPosition())
            side = [pcbnew.B_Cu if fps[ref].IsFlipped() else F]       # the fan-out stays on the ball's own layer: the via at
            s_cells = router.cluster_cells(g, cluster, side)             # its far end is its only via (the first try let the
            s_esc = router.cluster_escapes(g, cluster, cls, net, side)   # route hop to Top at the ball and cross the pair's lane)
            done = False
            for spot in g.find_via_spots(net, p, rv, max_r=FANOUT_REACH.get(ref, max_r), count=8, xr=g.xradii(net, vdia, clear), dia=vdia, clr=clear, drill=vdrill,
                                         also=fanout_allowed(board, ref)):
                cx, cy = router.cell(*spot)
                path = g.route(net, s_cells | set(s_esc), {(side[0], cx, cy)}, cls, layers=side, via_ok=False, max_nodes=80000)
                if path is None:
                    continue
                commit_with_stubs(g, name, path, cls, s_esc, {})
                g.add_via(name, spot, vdia, vdrill)
                log["stitch"].append({"net": name.rsplit("/", 1)[-1], "via": [round(spot[0], 2), round(spot[1], 2)], "fanout": f"{ref}.{pad.GetNumber()}"})
                n += 1
                done = True
                break
            if not done:
                log["notes"].append(f"fan-out: no via spot within {max_r} mm of {ref}.{pad.GetNumber()} ({name.rsplit('/', 1)[-1]})")
    log["notes"].append(f"{n} regulator balls fanned out to vias before the pairs ({', '.join(refs)})")


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


SMALL_PAD = 1.0      # mm: a plane-net pad narrower than this (0402 / 0603 dividers, decoupling) links to its via with a 0.2 mm stub


def small_stub_class(pad, pcls):
    """BRIEF §6: 'R8/U4 sense legs and small decoupling stubs keep the mote's 0.2 mm'. A power-class net's stitching link from a
    pad narrower than SMALL_PAD runs at the rail class (0.2 mm); since no via may sit in a solder pad any more (QE round 3 F1),
    a 0.5 mm track from an 0402 pad in the strip's crowded bottom finds no room (R41.1 was open)."""
    if pcls not in ("power", "pi5v", "payload"):
        return pcls
    try:
        sz = pad.GetSize(pcbnew.F_Cu)
    except TypeError:
        sz = pad.GetSize()
    return "rail" if pad.GetDrillSize().x == 0 and min(mm(sz.x), mm(sz.y)) < SMALL_PAD else pcls


def prestitch(g, board, plane, max_r=1.5, net_name="GND", skip_pocket=True, only_ref=None):
    """A via next to every single-pad cluster of a plane net before the signals are routed (≤ 1.2 mm away, inside
    the plane's filled copper), at the net's class width (escapes for fine pads). only_ref: this footprint's pads only."""
    poly, layer, fill = plane[:3]
    net = g.netcode[net_name]
    pcls0 = "gnd" if net_name == "GND" else router.net_class(net_name)
    n = 0
    for cluster in router.net_clusters(board, net_name):
        if plane_connected(cluster, plane) or len(cluster) != 1 or cluster[0].GetClass() != "PAD":
            continue
        pad = cluster[0]
        pcls = small_stub_class(pad, pcls0)
        width, clear, vdia, vdrill = router.CLASSES[pcls]
        rv = g.radius_for(vdia, clear)
        if only_ref is not None and pad.GetParentFootprint().GetReference() != only_ref:
            continue
        p = geom.xy(pad.GetPosition())
        if skip_pocket and ADIN_AREA and ADIN_AREA[0] <= p[0] <= ADIN_AREA[2] and ADIN_AREA[1] <= p[1] <= ADIN_AREA[3]:
            continue          # the ADIN block's area: U1's escapes need every free cell there; stitched after the signals
        if pad.m_Uuid.AsString() in g.exclude_ids:
            continue
        s_cells = g.pad_cells(pad)
        s_esc = g.escapes(pad, pcls, net)
        for spot in g.find_via_spots(net, p, rv, max_r=max_r, inside=fill, count=4, xr=g.xradii(net, vdia, clear), dia=vdia, clr=clear, drill=vdrill):
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
    log["notes"].append(f"{n} {net_name.rsplit('/', 1)[-1]} pads pre-stitched (via within {max_r} mm) before the signals" + (f" ({only_ref} only)" if only_ref else ""))


def stitch(g, board, polys):
    """Every cluster of a plane net gets a via into its plane unless it already touches it."""
    for net_name, plane in polys.items():
        if net_name not in g.netcode:
            continue
        plane[3] = island_table(board, net_name)
        fill = plane[2]
        net = g.netcode[net_name]
        cls0 = "gnd" if net_name == "GND" else router.net_class(net_name)
        for cluster in router.net_clusters(board, net_name):
            if plane_connected(cluster, plane):
                continue
            cls = cls0
            pads_ = [it for it in cluster if it.GetClass() == "PAD"]
            if pads_ and all(small_stub_class(p_, cls0) == "rail" for p_ in pads_):
                cls = "rail"
            width, clear, vdia, vdrill = router.CLASSES[cls]
            rv = g.radius_for(vdia, clear)
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
                for sp in g.find_via_spots(net, p, rv, max_r=4.0, inside=fill, count=12, xr=g.xradii(net, vdia, clear), dia=vdia, clr=clear, drill=vdrill):
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


def other_layer_copper(board, net_name, layer):
    """A test (x, y) -> bool: does the net have copper on a layer other than `layer` at that point (a filled zone
    island of the net, or a track / via / through pad of the net within its own copper, 0.05 mm margin)?"""
    fills = []
    for z in board.Zones():
        if z.GetIsRuleArea() or z.GetNetname() != net_name or z.GetLayer() == layer:
            continue
        fp = z.GetFilledPolysList(z.GetLayer())
        if fp.OutlineCount():
            fills.append(pcbnew.SHAPE_POLY_SET(fp))
    items = [t for t in board.GetTracks() if t.GetNetname() == net_name and (t.GetClass() == "PCB_VIA" or t.GetLayer() != layer)]
    pads = [p for f in board.GetFootprints() for p in f.Pads() if p.GetNetname() == net_name and (p.GetDrillSize().x > 0 or any(p.IsOnLayer(l) for l in geom.CU if l != layer))]

    def test(x, y):
        q = V(x, y)
        if any(fl.Contains(q) for fl in fills):
            return True
        for it in items:
            l = next(iter(router.item_layers(it) - {layer}), None)
            if l is not None and it.GetEffectiveShape(l).Collide(q, MM(0.05)):
                return True
        for p in pads:
            l = next((l for l in geom.CU if l != layer and (p.GetDrillSize().x > 0 or p.IsOnLayer(l))), None)
            if l is not None and p.GetEffectiveShape(l).Collide(q, MM(0.05)):
                return True
        return False
    return test


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
            # the via is only useful where the net has copper on another layer to reach (session 2, REPORT §6 #5: a
            # 5V_PI island via with nothing on any other layer was dangling)
            others = other_layer_copper(board, net_name, layer)
            spot = g.find_via_spot(net, cen, rv, max_r=max(2.0, (mm(bb.GetWidth()) + mm(bb.GetHeight())) / 2), inside=inner, xr=g.xradii(net, vdia, clear),
                                   dia=vdia, clr=clear, also=others, drill=vdrill)
            if spot is None:
                log["failed"].append({"net": net_name, "why": f"zone island on {board.GetLayerName(layer)} near {tuple(round(c, 1) for c in cen)} has no via and none fits over the net's copper on another layer"})
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
    global ADIN_AREA
    blocks = {b["name"]: b for b in json.load(open(geom.EXP / "blocks.json"))["blocks"]}
    fpsA = geom.fp_by_ref(board)
    cys = [geom.courtyard_bbox(fpsA[r]) for r in blocks["ADIN"]["placed"]]
    ADIN_AREA = (min(c[0] for c in cys) - 1.0, min(c[1] for c in cys) - 1.0, max(c[2] for c in cys) + 1.0, max(c[3] for c in cys) + 1.0)
    log["notes"].append(f"ADIN block area (prestitch skipped inside): {tuple(round(v, 1) for v in ADIN_AREA)}")
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
    bus_feeds(g, board)
    # 0. SPI first (session 2.b, Nick: the SPI is how the Pi talks to the ADIN; it goes straight from U1 to J1's SPI pins on
    #    a reserved Internal 2 lane, routed before anything else can take the room, never along a board edge; no length
    #    matching, LESSONS §5). Internal 2 at cost 1.0, Internal 1 at 1.5, the outer layers forbidden for these nets.
    for short in ("ADIN_SCK", "ADIN_MOSI", "ADIN_MISO", "~{ADIN_CS}"):
        L = route_net(g, board, N(short), layers=[F, I3, I1], layer_cost={I3: 1.0, I1: 1.5, F: 3.0}, max_nodes=1500000, via_cost=6.0)
        routed(short, L, "signal (SPI lane, Internal 2, first)")
    # 0b. the regulators' balls get their vias next (fanout)
    fanout(g, board)
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
    # 4. the load switch: its VBUS input pin gets its plane via first (session 2, REPORT §6 #3: after the row's signals
    #    the 0.5 mm escape of U11 pin 1 had no path to the plane), then its signals (their escapes leave U11's 0.5 mm
    #    pitch rows first), then the payload output: U11 pin 10 -> D3/C50 (bottom) -> J5 pin 1 / TP36, Internal 2 west
    #    of U11 (south of J1's last pins)
    prestitch(g, board, polys["VBUS"], net_name="VBUS", only_ref="U11")
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
    for short, pref in (("~{ADIN_INT}", {I3: 1.0, I1: 1.1, F: 2.5, B: 2.5}), ("~{ADIN_RST}", PREF_I1)):
        L = route_net(g, board, N(short), layer_cost=pref, max_nodes=1500000, via_cost=6.0)
        routed(short, L, router.net_class(N(short)) + " (pocket corridor)")
    # 6. the rails into the pocket's south: 3V3 to U3 first (the longest way, from the island), then 1V8 (B18 -> U2) and
    #    ADIN_PWR (U2/U3 -> R43 / TP8 / J1 pin 16): the pocket's south exit holds one track per layer
    # (session 2: the bottom layer costs 2.0 for these so they stay off the bottom around U2 / U3, whose balls leave
    # on the bottom to their fan-out vias; the first M2 run of session 2 had 3V3 seal U2's balls in on the bottom)
    L = route_net(g, board, "3V3", plane_poly=polys.get("3V3"), layer_cost={I3: 1.0, I1: 1.2, B: 2.0, F: 2.5}, max_nodes=2500000, via_cost=6.0)
    routed("3V3", L, "rail (plane + pocket)")
    L = route_net(g, board, N("1V8"), layer_cost=PREF_I3, max_nodes=1500000, via_cost=6.0)
    routed("1V8", L, "rail")
    L = route_net(g, board, N("ADIN_PWR"), layer_cost=PREF_I3, max_nodes=1500000, via_cost=6.0)
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
        width, clear, vdia, vdrill = router.CLASSES[pcls]
        rt = g.radius_for(width, clear)
        hwt = int(math.ceil(width / 2 / router.PITCH))
        xrt = g.xradii(net, width, clear)
        vias = [t.GetPosition() for t in board.GetTracks() if t.GetClass() == "PCB_VIA" and t.GetNetname() == z.GetNetname()]
        pth = [p.GetPosition() for f in board.GetFootprints() for p in f.Pads() if p.GetNetname() == z.GetNetname() and p.GetDrillSize().x > 0]
        islands = []
        for i in range(fp.OutlineCount()):
            isl = pcbnew.SHAPE_POLY_SET()
            isl.AddOutline(fp.Outline(i))
            if any(isl.Collide(q, MM(0.1)) for q in vias + pth):
                continue          # this island reaches the net's other copper through a via / through pad: nothing to join
            o = fp.Outline(i)
            cells = set()
            for k in range(o.PointCount()):
                q = o.CPoint(k)
                cx, cy = router.cell(mm(q.x), mm(q.y))
                # a start / goal cell on the fill's edge must itself be free for the track (session 2: a GND island-join
                # track started 0.1 mm from a 1V8 track, which the fill keeps 0.25 from but a track must keep 0.15 from)
                if 0 <= cx < router.W and 0 <= cy < router.H and g.free(z.GetLayer(), cx, cy, rt, net, hwt, xrt):
                    cells.add((z.GetLayer(), cx, cy))
            if cells:
                islands.append(cells)
        if len(islands) < 2:
            continue
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
