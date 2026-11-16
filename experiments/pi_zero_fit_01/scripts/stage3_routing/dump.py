"""Dump a board to JSON in new-frame mm (pads, tracks, vias, zones). Usage: <KiCad python> dump.py <board> <out.json> [dx dy]"""
import pcbnew, sys, json
DX, DY = (float(sys.argv[3]), float(sys.argv[4])) if len(sys.argv) > 4 else (113.47, 89.34)
mm = pcbnew.ToMM
b = pcbnew.LoadBoard(sys.argv[1])
P = lambda p: [round(mm(p.x) - DX, 3), round(mm(p.y) - DY, 3)]
sn = lambda n: n.split('/')[-1]
out = {'fps': [], 'tracks': [], 'vias': [], 'zones': []}
for f in b.GetFootprints():
    pads = []
    for p in f.Pads():
        bb = p.GetBoundingBox()
        pads.append({'n': p.GetNumber(), 'net': sn(p.GetNetname()), 'pos': P(p.GetPosition()), 'bb': P(bb.GetPosition()) + P(bb.GetEnd()),
                     'th': p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH), 'drill': mm(p.GetDrillSize().x),
                     'layers': [b.GetLayerName(l) for l in p.GetLayerSet().CuStack()]})
    f.BuildCourtyardCaches()
    cy = f.GetCourtyard(pcbnew.B_CrtYd if f.IsFlipped() else pcbnew.F_CrtYd).BBox()
    out['fps'].append({'ref': f.GetReference(), 'val': f.GetValue(), 'bot': f.IsFlipped(), 'pos': P(f.GetPosition()), 'locked': f.IsLocked(),
                       'cy': P(cy.GetPosition()) + P(cy.GetEnd()), 'pads': pads})
for t in b.GetTracks():
    if t.GetClass() == 'PCB_VIA':
        out['vias'].append({'net': sn(t.GetNetname()), 'pos': P(t.GetStart()), 'd': mm(t.GetWidth(pcbnew.F_Cu)), 'drill': mm(t.GetDrillValue()), 'id': t.m_Uuid.AsString()})
    else:
        out['tracks'].append({'net': sn(t.GetNetname()), 'L': t.GetLayerName(), 'a': P(t.GetStart()), 'b': P(t.GetEnd()), 'w': mm(t.GetWidth()), 'cls': t.GetClass(), 'id': t.m_Uuid.AsString()})
for z in b.Zones():
    bb = z.GetBoundingBox(); o = z.Outline()
    pts = [P(o.CVertex(i)) for i in range(o.TotalVertices())] if o.TotalVertices() < 60 else None
    out['zones'].append({'net': sn(z.GetNetname()), 'name': z.GetZoneName(), 'layers': [b.GetLayerName(l) for l in z.GetLayerSet().Seq()], 'bb': P(bb.GetPosition()) + P(bb.GetEnd()),
                         'rule': z.GetIsRuleArea(), 'prio': z.GetAssignedPriority(), 'pts': pts, 'nv': o.TotalVertices(),
                         'clr': mm(z.GetLocalClearance().value()) if hasattr(z.GetLocalClearance(), 'value') and z.GetLocalClearance().has_value() else None,
                         'minw': mm(z.GetMinThickness()), 'conn': z.GetPadConnection(),
                         'ko': [z.GetDoNotAllowTracks(), z.GetDoNotAllowVias(), z.GetDoNotAllowZoneFills(), z.GetDoNotAllowPads()] if z.GetIsRuleArea() else None})
json.dump(out, open(sys.argv[2], 'w'))
print(len(out['fps']), 'fps', len(out['tracks']), 'tracks', len(out['vias']), 'vias', len(out['zones']), 'zones')
