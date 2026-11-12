"""Step 3 of the routing plan: the bus pairs at the inserts.

The four bus nets were already connected after step 0 (insert labels) and step 1b (inserts mirrored). What was
left were errors, 125 of the 151 on the board, all at the inserts, plus one short:

1. Insert footprint, unplated hole. The import from Altium gave the 4.4 mm hole a pad stack with size 0 on the
   inner layers ("pad must have a positive size") and a 5.5 mm net-less copper disc on the bottom, which the
   seven ring vias of the bus net run into. The hole becomes a plain unplated hole (4.4 mm, no copper). The
   bus copper stays on the footprint's ring pad (pad 1, r 2.2 to 3.69 mm), which already covers that area.
2. FID1 and FID3 move 0.2 mm west, to (123.70, 128.60): after the inserts moved west in step 1b the fiducial's
   mask opening (2.25 mm) ran into MP4's, which KiCad reports as a solder-mask bridge between nets. The gap
   between the two openings is now 0.15 mm.
3. Two scoped rules in the .kicad_dru: the insert's hole may touch its own ring pad (JLC trims 0.2 mm of copper
   around an unplated hole), and needs 0.2 mm to other copper (JLC: unplated hole to track 0.2 mm; the top arc is
   0.23 mm from the hole, as on Sofar's mote).
4. Each 2 mm trunk ended on the ring's centre line, so its round end reached 0.17 mm into the hole. The trunks
   now end 3.45 mm from the insert centre: the end cap stays 0.25 mm off the hole and still overlaps the arc.
5. The BM2_P trunk's vertical run moves from x 129.58 to x 129.10: it touched Sofar's GND via at (130.90, 115.00).

Run with KiCad's python. The pad-stack change is a text edit made before the board is loaded.
"""
import math
import os
import re
import sys
import pcbnew
import boardio
from boardio import mm

MM = pcbnew.FromMM
DRU = os.path.join(os.path.dirname(boardio.BOARD), "Nereus_Pi_Shield_Adin2111.kicad_dru")
INSERTS = ("MP1", "MP2", "MP3", "MP4")
END_R = 3.45                       # trunk end centre to insert centre: 2.2 hole + 0.25 clearance + 1.0 half width

# ---- 1. plain unplated hole (text edit)
text = open(boardio.BOARD).read()
pat = re.compile(
    r'(\(pad "" np_thru_hole circle\s*\(at 0 0 [\-\d.]+\)\s*\(size 4\.4 4\.4\)\s*\(drill 4\.4\)\s*'
    r'\(layers "\*\.Cu" "\*\.Mask"\)\s*\(uuid "[^"]+"\))\s*\(padstack\s*\(mode front_inner_back\)\s*'
    r'\(layer "Inner"\s*\(shape circle\)\s*\(size 0 0\)\s*\(zone_connect -1\)\s*\)\s*'
    r'\(layer "B\.Cu"\s*\(shape circle\)\s*\(size 5\.5 5\.5\)\s*\(zone_connect -1\)\s*\)\s*\)')
text, n = pat.subn(lambda m: m.group(1), text)
if n == 0:
    sys.exit("step 3 already applied (the insert holes have no custom pad stack); nothing done")
assert n == 4, n
open(boardio.BOARD, "w").write(text)

# ---- 3. scoped rules
dru = open(DRU).read()
assert "Insert hole" not in dru
open(DRU, "w").write(dru.rstrip("\n") + '''

   (rule "Insert hole to other copper"
     (condition "A.Type == 'Pad' && A.Pad_Type == 'NPTH, mechanical' && A.memberOfFootprint('MP?')")
     (constraint hole_clearance (min 0.2mm)))
   (rule "Insert hole to its own ring pad"
     (condition "A.Type == 'Pad' && A.Pad_Type == 'NPTH, mechanical' && A.memberOfFootprint('MP?') && B.Type == 'Pad' && B.memberOfFootprint('MP?')")
     (constraint hole_clearance (min 0mm)))
''')

b = boardio.load()
fp = boardio.footprints(b)
tracks = list(b.GetTracks())
sn = lambda t: t.GetNetname().split("/")[-1]
xy = lambda p: (mm(p.x), mm(p.y))
vec = lambda x, y: pcbnew.VECTOR2I(MM(x), MM(y))
top = b.GetLayerID("Top Layer")

# ---- 2. fiducials clear of MP4's mask opening
for r in ("FID1", "FID3"):
    assert boardio.pos(fp[r]) == (123.9, 128.6), boardio.pos(fp[r])
    boardio.move_to(fp[r], 123.70, 128.60)

def trunk_segments(net):
    return [t for t in tracks if t.Type() == pcbnew.PCB_TRACE_T and t.GetLayer() == top and sn(t) == net and abs(mm(t.GetWidth()) - 2.0) < 0.01]

def move_vertex(net, old, new):
    hits = 0
    for t in trunk_segments(net):
        if math.hypot(xy(t.GetStart())[0] - old[0], xy(t.GetStart())[1] - old[1]) < 0.02:
            t.SetStart(vec(*new)); hits += 1
        if math.hypot(xy(t.GetEnd())[0] - old[0], xy(t.GetEnd())[1] - old[1]) < 0.02:
            t.SetEnd(vec(*new)); hits += 1
    return hits

report = []
# ---- 5. BM2_P vertical run off the GND via
NEW_X = 129.10
c3 = boardio.pos(fp["MP3"])
last = [t for t in trunk_segments("BM2_P") if math.hypot(xy(t.GetEnd())[0] - c3[0], xy(t.GetEnd())[1] - c3[1]) < 3.9]
assert len(last) == 1
ex, ey = xy(last[0].GetEnd())
corner_low = xy(last[0].GetStart())
assert abs(corner_low[0] - 129.58) < 0.02, corner_low
assert move_vertex("BM2_P", corner_low, (NEW_X, ey - (ex - NEW_X))) == 2
assert move_vertex("BM2_P", (129.58, 113.75), (NEW_X, 113.75 + (129.58 - NEW_X))) == 2
report.append("  BM2_P vertical run: x 129.58 -> %.2f" % NEW_X)

# ---- 4. trunk ends 3.45 mm from the insert centre
for r in INSERTS:
    net = [p.GetNetname().split("/")[-1] for p in fp[r].Pads() if p.GetNumber() == "1"][0]
    cx, cy = boardio.pos(fp[r])
    ends = [t for t in trunk_segments(net) if math.hypot(xy(t.GetEnd())[0] - cx, xy(t.GetEnd())[1] - cy) < 3.9]
    assert len(ends) == 1, (r, len(ends))
    t = ends[0]
    (sx, sy), (ex, ey) = xy(t.GetStart()), xy(t.GetEnd())
    ux, uy = sx - ex, sy - ey
    n = math.hypot(ux, uy); ux, uy = ux / n, uy / n                 # from the end back towards the start
    # |E + k u - C| = END_R, smallest k >= 0
    dx, dy = ex - cx, ey - cy
    bq = dx * ux + dy * uy
    cq = dx * dx + dy * dy - END_R * END_R
    k = -bq + math.sqrt(bq * bq - cq)
    assert 0 <= k < 1.5, (r, k)
    t.SetEnd(vec(ex + k * ux, ey + k * uy))
    report.append("  %s %s: trunk end pulled back %.2f mm, now %.2f mm from the insert centre" % (r, net, k, END_R))

boardio.save(b)
print("\n".join(report))
boardio.report(list(INSERTS))
