"""Stage B gate. KiCad's Python: planecheck.py <board after the stage, zones filled> [<board before>]. Read-only.
1. Per zone of ours ("N6 ..."): filled area and number of filled pieces.
2. GND on the GND plane: number of separate copper pieces (all GND zones of that layer merged), against the board before.
3. The N6 header pins without a net: nearest zone fill on any copper layer (must not touch).
4. N6 3V3 and the mote's 3V3: no zone of either net overlaps the other's pads.
5. The two slots of Sofar's GND plane: is there GND-plane copper across each slot mouth between his outline's end and the board edge."""
import sys, pcbnew
mm = pcbnew.ToMM; FM = pcbnew.FromMM
def load(p):
    b = pcbnew.LoadBoard(p); return b
b = load(sys.argv[1]); old = load(sys.argv[2]) if len(sys.argv) > 2 else None
CU = [l for l in b.GetEnabledLayers().CuStack()]
def fills(bd, layer, net):
    s = pcbnew.SHAPE_POLY_SET()
    for z in bd.Zones():
        if not z.GetIsRuleArea() and z.GetNetname() == net and z.IsOnLayer(layer) and z.IsFilled(): s.BooleanAdd(pcbnew.SHAPE_POLY_SET(z.GetFilledPolysList(layer)))
    s.Simplify(); return s
print("1. our zones")
for z in b.Zones():
    if z.GetZoneName().startswith("N6 "):
        for l in z.GetLayerSet().Seq():
            f = z.GetFilledPolysList(l); print("   %-17s %-14s %-6s filled %7.1f mm2 in %d piece(s)" % (z.GetZoneName(), b.GetLayerName(l), z.GetNetname().split("/")[-1], f.Area() / 1e12, f.OutlineCount()))
gl = b.GetLayerID("GND Plane")
g = fills(b, gl, "GND"); print("2. GND on the GND plane: %d piece(s), %.1f mm2" % (g.OutlineCount(), g.Area() / 1e12) + ("" if not old else "   (before: %d piece(s), %.1f mm2)" % (fills(old, old.GetLayerID("GND Plane"), "GND").OutlineCount(), fills(old, old.GetLayerID("GND Plane"), "GND").Area() / 1e12)))
for i in range(g.OutlineCount()):
    q = g.Outline(i).BBox(); print("      piece %d: X' %.2f..%.2f y %.2f..%.2f" % (i, mm(q.GetLeft()) - 100, mm(q.GetRight()) - 100, 100 - mm(q.GetBottom()), 100 - mm(q.GetTop())))
print("3. header pins without a net against zone fills")
worst = 99; n = 0
allfill = {}
for l in CU:
    s = pcbnew.SHAPE_POLY_SET()
    for z in b.Zones():
        if not z.GetIsRuleArea() and z.IsOnLayer(l) and z.IsFilled(): s.BooleanAdd(pcbnew.SHAPE_POLY_SET(z.GetFilledPolysList(l)))
    allfill[l] = s
for r in ("J21", "J22"):
    for p in b.FindFootprintByReference(r).Pads():
        if p.GetNetname().startswith("unconnected-") or p.GetNetname() == "":
            n += 1
            for l in CU:
                hole = p.GetEffectiveHoleShape()
                for lim in (0.0, 0.1, 0.2, 0.25, 0.3):
                    if allfill[l].Collide(hole, FM(lim)):
                        worst = min(worst, lim); break
print("   %d pins; zone copper nearer to a pin's HOLE than: %s" % (n, "none within 0.30 mm" if worst == 99 else "%.2f mm" % worst))
print("4. 3V3 nets")
for net in ("3V3", "/Top-Level Schematic/N6_3V3"):
    zs = [z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == net]
    print("   %-8s zones: %d" % (net.split("/")[-1], len(zs)))
print("5. slot mouths on the GND plane")
for name, x0, x1, y in (("south", 33.7, 35.0, 6.86), ("north", 34.7, 35.0, 41.83)):
    probe = pcbnew.SHAPE_POLY_SET(); probe.NewOutline()
    for px, py in ((x0, y - 0.05), (x1, y - 0.05), (x1, y + 0.05), (x0, y + 0.05)): probe.Append(pcbnew.VECTOR2I(FM(100 + px), FM(100 - py)))
    probe.BooleanIntersection(g); print("   %s slot, X' %.1f..%.1f at y %.2f: %s" % (name, x0, x1, y, "COPPER ACROSS (%.3f mm2)" % (probe.Area() / 1e12) if probe.Area() > 0 else "open (no copper)"))
