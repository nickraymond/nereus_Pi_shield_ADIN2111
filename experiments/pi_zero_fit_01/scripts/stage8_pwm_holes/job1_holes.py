"""Stage 8, job 1: the four mounting holes H1..H4 take the Raspberry Pi's hole size, 2.75 mm (was 2.70 mm).
Source in the repo: Nereus_Pi_Shield_Adin2111/Pi_Zero_outline.dxf, layer MOUNT_HOLES, four CIRCLE entities of radius 1.375 at
(3.5, 3.5), (61.5, 3.5), (3.5, 26.5), (61.5, 26.5) (this script reads them and stops if they differ from the board).
Only the pad of each footprint changes: size 2.70 -> 2.75 and drill 2.70 -> 2.75, still np_thru_hole (not plated), same place.
The footprint keeps its library name (MountingHole_2.7mm_M2.5_ISO7380); DRC lists the four as lib_footprint_mismatch.
Usage: <KiCad python> job1_holes.py <board> <Pi_Zero_outline.dxf>"""
import sys, os, pcbnew
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage3_routing'))
import s3lib
D = 2.75
t = [x.strip() for x in open(sys.argv[2], errors='replace').read().replace('\r', '').split('\n')]; dxf = {}
for i in range(len(t) - 1):
    if t[i] == '0' and t[i + 1] == 'CIRCLE':
        d = {}; j = i + 2
        while j < len(t) - 1 and t[j] != '0': d[t[j]] = t[j + 1]; j += 2
        if d.get('8') == 'MOUNT_HOLES': dxf[(float(d['10']), float(d['20']))] = float(d['40'])
print('  DXF MOUNT_HOLES circles (centre: radius):', dxf)
assert len(dxf) == 4 and all(abs(2 * r - D) < 1e-9 for r in dxf.values()), dxf
b = pcbnew.LoadBoard(sys.argv[1]); n = 0
for f in sorted(b.GetFootprints(), key=lambda f: f.GetReference()):
    if f.GetReference() not in ('H1', 'H2', 'H3', 'H4'): continue
    (p,) = list(f.Pads()); c = s3lib.N(p.GetPosition())
    assert p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH and (c[0], c[1]) in dxf, (f.GetReference(), c)      # the DXF's four centres are symmetric in y (3.5 / 26.5)
    old = (s3lib.mm(p.GetSize(pcbnew.F_Cu).x), s3lib.mm(p.GetDrillSize().x))
    p.SetSize(pcbnew.F_Cu, pcbnew.VECTOR2I(s3lib.IU(D), s3lib.IU(D))); p.SetDrillSize(pcbnew.VECTOR2I(s3lib.IU(D), s3lib.IU(D))); n += 1
    print('  %s (%.2f, %.2f): pad / drill %.2f / %.2f -> %.2f / %.2f mm, %s' % (f.GetReference(), c[0], c[1], old[0], old[1], s3lib.mm(p.GetSize(pcbnew.F_Cu).x), s3lib.mm(p.GetDrillSize().x),
          'not plated' if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH else 'PLATED'))
assert n == 4
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(sys.argv[1], b)
