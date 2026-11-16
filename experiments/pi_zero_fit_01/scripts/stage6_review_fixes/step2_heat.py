"""Stage 6, step 2: heat spreading for the 5 V converter (Nick, 2026-11-16: "Yes, build it"; drawing: stage5_proposals/converter_heat_proposal_*.png).
Usage: <KiCad python> step2_heat.py <board> <board out> [log.json]     env S3_BASE = the stage-2c board

 (a) a GND zone on the bottom layer under the converter (OUTLINE below); solid connections,
     clearance 0.3, min width 0.25, islands removed (the frozen board's settings for its own zones). It flows round C53, R37, R38 and the tracks.
 (b) extra GND vias (0.6 / 0.3): VIAS below. The drawing's third site (11.4, 12.3) is not built: see the log.
No part and no existing copper of the converter group is touched; this script only adds.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage3_routing'))
import s3lib, pcbnew
B = '6 Bottom Layer'
# The drawing's outline was (0.9, 8.6) (2.0, 7.5) (10.7, 7.5) (10.7, 15.3) (0.9, 15.3). Two changes, both to reach GND vias that are already there:
# the north edge is 0.3 mm further north (y 7.2; the fill stops 0.3 mm short of the 5V_PI track at y 6.886 by itself): with y 7.5 the strip beside
# R38 pad 2 was under the 0.25 mm minimum width and the via (8.901, 7.459) hung on a separate 0.13 mm2 piece; and a tab (10.7..12.0, 13.9..15.3)
# onto Sofar's GND copper shape with its three vias (11.706, 15.114), (12.331, 14.764), (12.331, 15.464).
OUTLINE = [(0.9, 8.6), (2.3, 7.2), (10.7, 7.2), (10.7, 13.9), (12.0, 13.9), (12.0, 15.3), (0.9, 15.3)]
VIAS = [(float(a), float(b)) for a, b in (v.split(',') for v in os.environ.get('S6_VIAS', '4.55,11.6 4.4,12.75').split())]
r = s3lib.Router(sys.argv[1], '6 heat'); C = 0.13
for p in VIAS: r.via('GND', p, clr=C, note='converter heat')
z = r.zone('GND', B, OUTLINE, 'GND converter heat spreader (stage 6)', prio=1, clr=0.3, minw=0.25, solid=True)
n = r.report_bad()
r.finish(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
ps = z.GetFilledPolysList(z.GetLayer()); mm = s3lib.mm
areas = [round(ps.Outline(i).Area() / 1e12 - sum(ps.Hole(i, h).Area() for h in range(ps.HoleCount(i))) / 1e12, 2) for i in range(ps.OutlineCount())]
tied = sorted(s3lib.N(t.GetStart()) for t in r.b.GetTracks() if t.GetClass() == 'PCB_VIA' and s3lib.sn(t.GetNetname()) == 'GND' and ps.Contains(t.GetStart()))
other = sorted((s3lib.sn(t.GetNetname()), s3lib.N(t.GetStart())) for t in r.b.GetTracks() if t.GetClass() == 'PCB_VIA' and s3lib.sn(t.GetNetname()) != 'GND' and z.Outline().Contains(t.GetStart()))
pads = sorted('%s.%s' % (f.GetReference(), p.GetNumber()) for f in r.b.GetFootprints() for p in f.Pads() if s3lib.sn(p.GetNetname()) == 'GND' and p.IsOnLayer(z.GetLayer()) and ps.Contains(p.GetPosition()))
print('   heat spreader: pieces %d, areas %s mm2 (outline %.1f mm2); GND vias in the fill: %d %s; GND pads in the fill: %s' % (len(areas), areas, z.Outline().Area() / 1e12, len(tied), tied, pads))
print('   vias of other nets inside the outline (the fill keeps 0.3 mm from them): %s' % other)
sys.exit(1 if n else 0)
