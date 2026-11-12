"""Step 9h planner input: silkscreen texts, footprints (pads, courtyard, own silkscreen) and vias as json.
Run with KiCad's python: dump.py <board.kicad_pcb> <out.json>."""
import sys, json, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); mm = pcbnew.ToMM
def bb(o):
    r = o.GetBoundingBox(); return [round(mm(r.GetLeft()),2), round(mm(r.GetTop()),2), round(mm(r.GetRight()),2), round(mm(r.GetBottom()),2)]
out = {"texts": [], "fps": [], "silk": []}
for d in b.GetDrawings():
    ln = d.GetLayerName()
    if d.GetClass() == "PCB_TEXT" and "Silk" in pcbnew.LayerName(d.GetLayer()) or (d.GetClass()=="PCB_TEXT" and d.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS)):
        p = d.GetPosition(); out["texts"].append({"t": d.GetText(), "side": "T" if d.GetLayer()==pcbnew.F_SilkS else "B", "x": round(mm(p.x),2), "y": round(mm(p.y),2),
            "h": mm(d.GetTextSize().y), "w": mm(d.GetTextSize().x), "ang": d.GetTextAngleDegrees(), "hj": d.GetHorizJustify(), "bb": bb(d)})
    elif d.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS):
        out["silk"].append({"cls": d.GetClass(), "side": "T" if d.GetLayer()==pcbnew.F_SilkS else "B", "bb": bb(d)})
for f in b.GetFootprints():
    r = f.Reference(); p = f.GetPosition(); rp = r.GetPosition()
    cy = None
    try:
        c = f.GetCourtyard(pcbnew.B_CrtYd if f.IsFlipped() else pcbnew.F_CrtYd)
        if c.OutlineCount(): 
            q = c.BBox(); cy = [round(mm(q.GetLeft()),2), round(mm(q.GetTop()),2), round(mm(q.GetRight()),2), round(mm(q.GetBottom()),2)]
    except Exception as e: pass
    pads = []
    for pad in f.Pads():
        q = pad.GetBoundingBox(); th = pad.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH)
        pads.append([round(mm(q.GetLeft()),2), round(mm(q.GetTop()),2), round(mm(q.GetRight()),2), round(mm(q.GetBottom()),2), 1 if th else 0])
    sk = []
    for g in f.GraphicalItems():
        if g.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS):
            sk.append({"cls": g.GetClass(), "side": "T" if g.GetLayer()==pcbnew.F_SilkS else "B", "bb": bb(g), "t": g.GetText() if g.GetClass()=="PCB_TEXT" else None})
    out["fps"].append({"ref": f.GetReference(), "val": f.GetValue(), "side": "B" if f.IsFlipped() else "T", "x": round(mm(p.x),2), "y": round(mm(p.y),2), "rot": f.GetOrientationDegrees(),
        "ref_vis": r.IsVisible(), "ref_layer": pcbnew.LayerName(r.GetLayer()), "rx": round(mm(rp.x),2), "ry": round(mm(rp.y),2), "rh": mm(r.GetTextSize().y), "rang": r.GetTextAngleDegrees(),
        "cy": cy, "pads": pads, "silk": sk, "bb": bb(f)})
vias = []
for t in b.GetTracks():
    if t.Type() == pcbnew.PCB_VIA_T:
        p = t.GetPosition(); vias.append([round(mm(p.x),2), round(mm(p.y),2), mm(t.GetWidth(pcbnew.F_Cu)), mm(t.GetDrill())])
out["vias"] = vias
json.dump(out, open(sys.argv[2], "w"))
print(len(out["texts"]), "texts", len(out["fps"]), "fps", len(out["silk"]), "board silk", len(vias), "vias")
