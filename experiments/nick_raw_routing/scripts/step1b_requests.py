"""Step 1b: Nick's four requests of 2026-11-10 for the holes, the LEDs, the inserts and J4.

1. Inserts on one line and mirrored about the board's centreline (x 148.80): MP4, MP3, MP2, MP1 at
   x 128.70, 138.30, 159.30, 168.90, all at y 127.45. Each insert's copper ring (arc and seven vias) moves
   with it and is now concentric with the insert; the last 45-degree run of each 2 mm bus trunk follows,
   and the corner on the vertical run slides to keep it at 45 degrees. The +/- silkscreen marks move 0.8 mm
   west with the inserts.
2. LEDs D9, D8, D10 at x 145.80, 148.80, 151.80 (3.0 mm apart, D8 on the centreline), y 128.60, which is
   3.5 mm from the south edge. R45, R44, R46 sit under them on the bottom.
3. J4 is no longer a JST PH connector: it becomes the same two wire pads as J5, pad 1 (to F1) at
   (119.00, 92.10), pad 2 GND 3.81 mm south. The symbol changes in the same commit (Master sheet).
4. A copper keep-out of radius 3.0 mm around each mounting hole H1-H4 on all six copper layers: no track,
   via or zone fill. The radius is the HOLE_KEEPOUT circle of the project's Pi_HAT_outline.dxf.
"""
import math
import os
import sys
import pcbnew
import boardio
from boardio import mm, move_to, pos

MM = pcbnew.FromMM
NAME = "WirePads_1x02_P3.81mm_Oval4.2x2.6mm_Drill1.3mm"
LIB = os.path.join(boardio.HERE, "..", "nereus.pretty")
Y_ROW = 127.45
TARGET_X = {"MP4": 128.70, "MP3": 138.30, "MP2": 159.30, "MP1": 168.90}
# net of the ring: (x of the trunk's vertical run, the trunk's end on the ring, vertices between corner and end)
TRUNK = {
    "BM2_N": (123.00, (128.32, 124.72), []),
    "BM2_P": (129.58, (136.22, 126.50), []),
    "BM1_N": (167.70, (162.20, 125.36), [(166.40, 121.16)]),
    "BM1_P": (174.30, (171.11, 124.70), []),
}
CORNER_Y = {"BM2_N": 119.40, "BM2_P": 119.86, "BM1_N": 119.86, "BM1_P": 121.50}
LEDS = {"D9": 145.80, "D8": 148.80, "D10": 151.80}
LED_R = {"D9": "R45", "D8": "R44", "D10": "R46"}
LED_Y = 128.60
KEEPOUT_R = 3.0

b = boardio.load()
fp = boardio.footprints(b)
if fp["J4"].GetFPID().GetLibItemName().wx_str() == NAME:
    sys.exit("step 1b already applied (J4 is the wire-pad footprint); nothing done")
tracks = list(b.GetTracks())
sn = lambda t: t.GetNetname().split("/")[-1]
xy = lambda p: (mm(p.x), mm(p.y))
vec = lambda x, y: pcbnew.VECTOR2I(MM(x), MM(y))

# ---- 1. inserts, rings and trunk ends
top = b.GetLayerID("Top Layer")
arcs = [t for t in tracks if t.Type() == pcbnew.PCB_ARC_T and sn(t) in TRUNK]
assert len(arcs) == 5, len(arcs)
report = []
for net, (xv, end, mids) in TRUNK.items():
    mine = [a for a in arcs if sn(a) == net]
    cx, cy = xy(mine[0].GetCenter())
    ref = min(TARGET_X, key=lambda r: math.hypot(pos(fp[r])[0] - cx, pos(fp[r])[1] - cy))
    assert math.hypot(pos(fp[ref])[0] - cx, pos(fp[ref])[1] - cy) < 0.2, (net, ref)
    assert [p.GetNetname().split("/")[-1] for p in fp[ref].Pads() if p.GetNumber() == "1"] == [net], (net, ref)
    dx, dy = TARGET_X[ref] - cx, Y_ROW - cy
    shift = pcbnew.VECTOR2I(MM(dx), MM(dy))
    vias = [t for t in tracks if t.Type() == pcbnew.PCB_VIA_T and sn(t) == net
            and math.hypot(xy(t.GetPosition())[0] - cx, xy(t.GetPosition())[1] - cy) < 3.9]
    assert len(vias) == 7, (net, len(vias))
    for t in mine + vias:
        t.Move(shift)
    # trunk: end and in-between vertices translate; the corner slides along the vertical run to keep 45 degrees
    new_end = (end[0] + dx, end[1] + dy)
    new_corner = (xv, new_end[1] - abs(new_end[0] - xv))
    moves = {end: new_end, (xv, CORNER_Y[net]): new_corner}
    for m in mids:
        moves[m] = (m[0] + dx, m[1] + dy)
    hits = 0
    for t in tracks:
        if t.Type() != pcbnew.PCB_TRACE_T or t.GetLayer() != top or sn(t) != net:
            continue
        for old, new in moves.items():
            if math.hypot(xy(t.GetStart())[0] - old[0], xy(t.GetStart())[1] - old[1]) < 0.012:
                t.SetStart(vec(*new)); hits += 1
            if math.hypot(xy(t.GetEnd())[0] - old[0], xy(t.GetEnd())[1] - old[1]) < 0.012:
                t.SetEnd(vec(*new)); hits += 1
    assert hits == 2 * len(moves) - 1, (net, hits)          # every vertex joins two segments, the end only one
    move_to(fp[ref], TARGET_X[ref], Y_ROW)
    report.append("  %s %s: ring moved (%.3f, %.3f); trunk corner y %.2f -> %.2f" % (ref, net, dx, dy, CORNER_Y[net], new_corner[1]))
marks = [d for d in b.GetDrawings() if d.Type() == pcbnew.PCB_TEXTBOX_T and d.GetText() in ("+", "-") and mm(d.GetPosition().y) > 125]
assert len(marks) == 8, len(marks)
for d in marks:
    d.Move(pcbnew.VECTOR2I(MM(-0.80), 0))

# ---- 2. LEDs and their resistors
for led, x in LEDS.items():
    move_to(fp[led], x, LED_Y)
    move_to(fp[LED_R[led]], x, LED_Y)

# ---- 3. J4 as wire pads
old = fp["J4"]
new = pcbnew.FootprintLoad(LIB, NAME)
new.SetFPID(pcbnew.LIB_ID("nereus", NAME))
new.SetReference("J4")
new.SetValue("Wire pads")
new.SetPath(old.GetPath())
new.SetSheetname(old.GetSheetname())
new.SetSheetfile(old.GetSheetfile())
nets = {p.GetNumber(): p.GetNet() for p in old.Pads()}
assert sorted(n.GetNetname().split("/")[-1] for n in nets.values()) == ["GND", "Net-(J4-Pin_1)"]
for p in new.Pads():
    p.SetNet(nets[p.GetNumber()])
FIELDS = {
    "Description": "5 V in: two through-hole wire pads (4.2 x 2.6 mm oval, 1.3 mm hole), leads soldered directly, "
                   "no connector. Pin 1 to F1, pin 2 GND. Was JST S2B-PH until 2026-11-10",
    "Planned MPN": "", "Planned LCSC": "", "Planned MFR": "",
}
for name, value in FIELDS.items():
    new.SetField(name, value)
for f in new.GetFields():
    if f.GetName() in FIELDS:
        f.SetVisible(False)
move_to(new, 119.00, 92.10)
b.Add(new)
b.Remove(old)

# ---- 4. copper keep-outs around the mounting holes
copper = pcbnew.LSET()
for name in ("Top Layer", "Internal 1", "GND Plane", "Internal 2", "PWR Plane", "6 Bottom Layer"):
    copper.AddLayer(b.GetLayerID(name))
for ref in ("H1", "H2", "H3", "H4"):
    cx, cy = pos(fp[ref])
    z = pcbnew.ZONE(b)
    z.SetIsRuleArea(True)
    z.SetZoneName("%s screw keep-out" % ref)
    z.SetLayerSet(copper)
    z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True)
    z.SetDoNotAllowZoneFills(True)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(False)
    o = z.Outline()
    o.NewOutline()
    for i in range(72):
        a = 2 * math.pi * i / 72
        o.Append(MM(cx + KEEPOUT_R * math.cos(a)), MM(cy + KEEPOUT_R * math.sin(a)))
    b.Add(z)

boardio.save(b)
print("\n".join(report))
boardio.report(["MP4", "MP3", "MP2", "MP1", "D9", "D8", "D10", "R45", "R44", "R46", "J4"])
