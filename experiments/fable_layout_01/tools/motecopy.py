"""Copy blocks of Sofar's mote copper onto the shield board, rigidly (translate + rotate by multiples of 90°).

A block (see blocks.json) names the mote footprints it carries, a selection rule for the copper around them, and one
transform:  p' = R(rot) · (p − src) + dst   (src, dst in mm; rot in degrees, KiCad's Rotate convention).
`select()` is the single source of truth for "which mote items belong to a block": copy (M2/M3) and blockcheck (M3/M5)
both call it, so what is checked is exactly what was copied.

Nets are mapped from the mote to the shield **by pad** (BRIEF §5): for every (ref, pad) the two boards share, the
mote's net name maps to the shield's. A block with a `ref_map` (e.g. the 5 V buck copied from the 3.3 V cell) maps
nets through its own pads first (U5.3 → U10.3 …).
"""
import json
import math

import pcbnew

import geom
from geom import MM, mm, V, deg

KINDS = ("track", "arc", "via", "zone")


class Transform:
    def __init__(self, src, dst, rot=0.0):
        self.src, self.dst, self.rot = tuple(src), tuple(dst), float(rot)

    def apply_item(self, item):
        """Move a duplicated KiCad item from the mote frame into the board frame (in place)."""
        item.Move(pcbnew.VECTOR2I(MM(self.dst[0] - self.src[0]), MM(self.dst[1] - self.src[1])))
        if self.rot:
            item.Rotate(V(*self.dst), deg(self.rot))

    def apply_xy(self, p):
        a = math.radians(self.rot)
        x, y = p[0] - self.src[0], p[1] - self.src[1]
        # KiCad's Rotate(+angle) turns counter-clockwise on screen, i.e. clockwise in y-down maths: (x,y) -> (x cos + y sin, -x sin + y cos)
        return (x * math.cos(a) + y * math.sin(a) + self.dst[0], -x * math.sin(a) + y * math.cos(a) + self.dst[1])

    def as_dict(self):
        return {"src": list(self.src), "dst": list(self.dst), "rot": self.rot}


def pad_nets(board):
    out = {}
    for f in board.GetFootprints():
        for p in f.Pads():
            if p.GetNumber():
                out[(f.GetReference(), p.GetNumber())] = p.GetNetname()
    return out


class Mote:
    def __init__(self, board):
        self.board = board
        self.mote = pcbnew.LoadBoard(str(geom.MOTE))
        self.mote_fp = {f.GetReference(): f for f in self.mote.GetFootprints()}
        self.mote_pads = pad_nets(self.mote)
        self.board_pads = pad_nets(board)
        # global net map, by shared pads
        votes = {}
        for key, mnet in self.mote_pads.items():
            if key in self.board_pads and mnet:
                votes.setdefault(mnet, {}).setdefault(self.board_pads[key], 0)
                votes[mnet][self.board_pads[key]] += 1
        self.net_map, self.net_conflicts = {}, {}
        for mnet, c in votes.items():
            best = max(c, key=c.get)
            self.net_map[mnet] = best
            if len(c) > 1:
                self.net_conflicts[mnet] = c

    # ---- selection ------------------------------------------------------------------------------------------
    def select(self, block):
        """Return the mote items of a block: {"footprints": [...], "copper": [(item, clip_rect)], "zones": [(z, clip_rect)]}.

        Footprints by ref. Copper (tracks / arcs / vias) by kind, on a block net (the nets touching the block's pads,
        unless `nets` is given), inside the block's region: a list of rects [x0, y0, x1, y1] in mote mm, each
        optionally {"rect": [...], "layers": [...]} to take only those layers there; or `radius` around the anchor.
        A track with one end inside a rect is clipped to that rect (clip_rect set); arcs are taken whole when fully
        inside; a zone is taken when its outline overlaps a rect that allows its layer, clipped to that rect unless it
        lies wholly inside. Vias on `exclude_vias_on` nets are skipped (they belong to a block sharing the area).
        """
        refs = block["refs"]
        fps = [self.mote_fp[r] for r in refs]
        kinds = block.get("kinds", list(KINDS))
        if block.get("nets"):
            nets = set(block["nets"])
        else:
            nets = {p.GetNetname() for f in fps for p in f.Pads() if p.GetNetname()}
        anchor = tuple(block["src"])
        radius = block.get("radius")
        rects = []
        for r in block.get("region", []):
            if isinstance(r, dict):
                rects.append((r["rect"], {self.mote.GetLayerID(n) for n in r["layers"]}))
            else:
                rects.append((r, None))
        no_vias = set(block.get("exclude_vias_on", []))

        def rect_of(p, layer):
            x, y = mm(p.x), mm(p.y)
            if radius is not None:
                return (None,) if math.hypot(x - anchor[0], y - anchor[1]) <= radius else None
            for rect, layers in rects:
                if layers is not None and layer is not None and layer not in layers:
                    continue
                if rect[0] <= x <= rect[2] and rect[1] <= y <= rect[3]:
                    return (rect,)
            return None

        copper = []
        for t in self.mote.GetTracks():
            if t.GetNetname() not in nets:
                continue
            cls = t.GetClass()
            if cls == "PCB_VIA" and "via" in kinds:
                if t.GetNetname() not in no_vias and rect_of(t.GetPosition(), None):
                    copper.append((t, None))
            elif cls == "PCB_ARC" and "arc" in kinds:
                lay = t.GetLayer()
                if rect_of(t.GetStart(), lay) and rect_of(t.GetEnd(), lay) and rect_of(t.GetMid(), lay):
                    copper.append((t, None))
            elif cls == "PCB_TRACK" and "track" in kinds:
                lay = t.GetLayer()
                a, b = rect_of(t.GetStart(), lay), rect_of(t.GetEnd(), lay)
                if a and b:
                    copper.append((t, None))
                elif a or b:
                    rect = (a or b)[0]
                    if rect is not None:
                        copper.append((t, rect))
        zones = []
        clip_nets = set(block.get("clip_zone_nets", []))
        zrects = block.get("zone_region")          # optional zone-only rects (no layer filter) for whole-inside tests

        def zone_inside(q, zl):
            if zrects:
                x, y = mm(q.x), mm(q.y)
                return any(r[0] <= x <= r[2] and r[1] <= y <= r[3] for r in zrects)
            return rect_of(q, zl)
        if "zone" in kinds and rects:
            for z in self.mote.Zones():
                if z.GetIsRuleArea() or z.GetNetname() not in nets:
                    continue
                zl = z.GetLayer()
                o = z.Outline().Outline(0)
                pts = [o.CPoint(i) for i in range(o.PointCount())]
                if pts and all(zone_inside(q, zl) for q in pts):
                    zones.append((z, None))             # an island pour wholly inside the block: copy whole
                elif z.GetNetname() in clip_nets:
                    bb = z.GetBoundingBox()
                    zr = (mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom()))
                    for rect, layers in rects:
                        if (layers is None or zl in layers) and geom.rect_overlap(zr, rect):
                            zones.append((z, rect))
                            break
                # anything else (the big GND / power planes) is M4's: planes are rebuilt on the new geometry
        return {"footprints": fps, "copper": copper, "zones": zones, "nets": sorted(nets)}

    # ---- nets -------------------------------------------------------------------------------------------------
    def block_net_map(self, block):
        """Mote net -> shield net for this block: through ref_map'd pads first, then the global map."""
        local = {}
        ref_map = block.get("ref_map", {})
        for r in block["refs"]:
            d = ref_map.get(r, r)
            for (ref, pad), mnet in self.mote_pads.items():
                if ref == r and mnet and (d, pad) in self.board_pads:
                    local.setdefault(mnet, self.board_pads[(d, pad)])
        out = dict(self.net_map)
        out.update(local)
        out.update(block.get("net_map", {}))
        return out

    # ---- copying ----------------------------------------------------------------------------------------------
    def net_item(self, name):
        ni = self.board.FindNet(name)
        if ni is None:
            raise KeyError(f"net {name!r} is not on the board")
        return ni

    def place_footprints(self, block, T):
        """Move the board's footprints (same refs, or ref_map) to where the mote's are, transformed; side as the mote.

        Proven by pads: every pad centre must land where the mote's pad lands after the transform (≤ 0.001 mm).
        """
        bfp = geom.fp_by_ref(self.board)
        ref_map = block.get("ref_map", {})
        placed = []
        for r in block["refs"]:
            src, dst_ref = self.mote_fp[r], ref_map.get(r, r)
            fp = bfp[dst_ref]
            if fp.IsFlipped() != src.IsFlipped():
                fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
            x, y = T.apply_xy(geom.xy(src.GetPosition()))
            fp.SetPosition(V(x, y))
            fp.SetOrientationDegrees(src.GetOrientationDegrees() + T.rot)
            want = {p.GetNumber(): T.apply_xy(geom.xy(p.GetPosition())) for p in src.Pads() if p.GetNumber()}
            got = {p.GetNumber(): geom.xy(p.GetPosition()) for p in fp.Pads() if p.GetNumber()}
            bad = [n for n in want if n in got and geom.dist(want[n], got[n]) > 0.001]
            if bad:
                raise SystemExit(f"{dst_ref}: pads {bad} do not land on the mote's {r} pads after the transform "
                                 f"(want {want[bad[0]]}, got {got[bad[0]]}); flip/orientation convention?")
            placed.append(dst_ref)
        return placed

    def copy_copper(self, block, T, sel=None):
        """Add the block's tracks / arcs / vias / zones to the board, transformed and re-netted. Returns counts."""
        sel = sel or self.select(block)
        nmap = self.block_net_map(block)
        n = {"track": 0, "arc": 0, "via": 0, "zone": 0, "skipped_net": 0, "clipped": 0}
        for item, rect in sel["copper"]:
            net = nmap.get(item.GetNetname())
            if net is None:
                n["skipped_net"] += 1
                continue
            cls = item.GetClass()
            if cls == "PCB_VIA":
                new = pcbnew.PCB_VIA(self.board)
                new.SetPosition(item.GetPosition())
                new.SetViaType(pcbnew.VIATYPE_THROUGH)
                new.SetWidth(item.GetWidth(pcbnew.F_Cu))
                new.SetDrill(item.GetDrillValue())
                new.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
                n["via"] += 1
            elif cls == "PCB_ARC":
                new = pcbnew.PCB_ARC(self.board)
                new.SetStart(item.GetStart())
                new.SetMid(item.GetMid())
                new.SetEnd(item.GetEnd())
                new.SetWidth(item.GetWidth())
                new.SetLayer(item.GetLayer())
                n["arc"] += 1
            else:
                new = pcbnew.PCB_TRACK(self.board)
                s, e = item.GetStart(), item.GetEnd()
                if rect is not None:
                    s, e = clip_segment(s, e, rect)
                    n["clipped"] += 1
                new.SetStart(s)
                new.SetEnd(e)
                new.SetWidth(item.GetWidth())
                new.SetLayer(item.GetLayer())
                n["track"] += 1
            new.SetNet(self.net_item(net))
            T.apply_item(new)
            self.board.Add(new)
        for z, rect in sel["zones"]:
            net = nmap.get(z.GetNetname())
            if net is None:
                n["skipped_net"] += 1
                continue
            new = pcbnew.ZONE(self.board)
            new.SetLayerSet(z.GetLayerSet())
            new.SetNet(self.net_item(net))
            new.SetAssignedPriority(z.GetAssignedPriority())
            new.SetMinThickness(z.GetMinThickness())
            new.SetLocalClearance(z.GetLocalClearance())
            new.SetThermalReliefGap(z.GetThermalReliefGap())
            new.SetThermalReliefSpokeWidth(z.GetThermalReliefSpokeWidth())
            new.SetPadConnection(z.GetPadConnection())
            new.SetZoneName(z.GetZoneName())
            outline = pcbnew.SHAPE_POLY_SET(z.Outline())
            if rect is not None:
                outline.BooleanIntersection(rect_poly(rect))
                outline.Fracture()
                n["clipped"] += 1
            for i in range(outline.OutlineCount()):       # copy the contours: the zone owns its own outline object
                new.Outline().AddOutline(outline.Outline(i))
            T.apply_item(new)
            self.board.Add(new)
            n["zone"] += 1
        return n


def clip_segment(s, e, rect):
    """Clip the segment s-e (VECTOR2I) to the rect (mm); the inside end stays, the other end moves to the boundary."""
    x0, y0, x1, y1 = (MM(v) for v in rect)

    def inside(p):
        return x0 <= p.x <= x1 and y0 <= p.y <= y1
    if inside(s) and not inside(e):
        s, e = e, s   # now s is outside
        swap = True
    else:
        swap = False
    # Liang–Barsky from the inside point e towards s
    dx, dy = s.x - e.x, s.y - e.y
    tmax = 1.0
    for p, q in ((-dx, e.x - x0), (dx, x1 - e.x), (-dy, e.y - y0), (dy, y1 - e.y)):
        if p > 0:
            tmax = min(tmax, q / p)
    clipped = pcbnew.VECTOR2I(int(round(e.x + dx * tmax)), int(round(e.y + dy * tmax)))
    return (e, clipped) if swap else (clipped, e)


def rect_poly(rect):
    ps = pcbnew.SHAPE_POLY_SET()
    ch = pcbnew.SHAPE_LINE_CHAIN()
    for x, y in ((rect[0], rect[1]), (rect[2], rect[1]), (rect[2], rect[3]), (rect[0], rect[3])):
        ch.Append(pcbnew.VECTOR2I(MM(x), MM(y)))
    ch.SetClosed(True)
    ps.AddOutline(ch)
    return ps


def load_blocks(path=geom.EXP / "blocks.json"):
    return json.load(open(path))


def transform_of(block):
    return Transform(block["src"], block["dst"], block.get("rot", 0))
