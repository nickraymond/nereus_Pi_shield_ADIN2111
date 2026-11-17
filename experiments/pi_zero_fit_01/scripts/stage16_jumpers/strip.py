"""Clear strip below JP3 / JP4: from their courtyards' south edge to the board edge (y 39.5), x of the two courtyards; lists every bottom pad
and every via (tented on this board) and bottom track inside it. Usage: <KiCad python> strip.py <board>"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage3_routing'))
import s3lib, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); cy = []
for r in ('JP3', 'JP4'):
    f = b.FindFootprintByReference(r); bb = f.GetCourtyard(pcbnew.B_CrtYd).BBox(); x0, y0 = s3lib.N(bb.GetPosition()); x1, y1 = s3lib.N(bb.GetEnd()); cy.append((r, x0, y0, x1, y1))
    print('  %s courtyard x %.2f..%.2f y %.2f..%.2f; strip below it to the edge (39.5): %.2f mm' % (r, x0, x1, y0, y1, 39.5 - y1))
X0, X1, Y0 = min(c[1] for c in cy), max(c[3] for c in cy), max(c[4] for c in cy)
for f in b.GetFootprints():
    for p in f.Pads():
        bb = p.GetBoundingBox(); x0, y0 = s3lib.N(bb.GetPosition()); x1, y1 = s3lib.N(bb.GetEnd())
        if x1 > X0 and x0 < X1 and y1 > Y0 and p.IsOnLayer(pcbnew.B_Cu): print('  ! bottom pad in the strip:', f.GetReference(), p.GetNumber(), (x0, y0, x1, y1))
for t in b.GetTracks():
    a, c = s3lib.N(t.GetStart()), s3lib.N(t.GetEnd()); r = pcbnew.ToMM(t.GetWidth(pcbnew.F_Cu) if t.GetClass() == 'PCB_VIA' else t.GetWidth()) / 2
    if max(a[1], c[1]) + r > Y0 and min(a[0], c[0]) - r < X1 and max(a[0], c[0]) + r > X0 and (t.GetClass() == 'PCB_VIA' or t.GetLayer() == pcbnew.B_Cu):
        print('    in the strip (mask-covered): %s %s %s-%s, reaches y %.2f' % ('via (tented)' if t.GetClass() == 'PCB_VIA' else 'track', s3lib.sn(t.GetNetname()), a, c, max(a[1], c[1]) + r))
