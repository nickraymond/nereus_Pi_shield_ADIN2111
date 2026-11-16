"""Stage 12, job 2 (re-review N2): the second via at F1 pad 1 moves clear of the pad. New-frame mm.
Usage: <KiCad python> job2_f1.py <board> [log.json]        env F1VIA = uuid of the via that goes;  PLAN=1: pre-check only, nothing saved

F1 (bottom) pad 1, 5V_LIFEPO4: 1.25 x 1.75 mm at (4.20, 16.60), copper y 15.725 .. 17.475, mask opening 0.025 mm larger. Two vias feed the 2.0 mm
Internal 2 track from it: (4.267, 15.887), hole inside the pad (stays), and (4.267, 17.687), hole edge 0.062 mm south of the pad's copper.
BOTH are vias of the frozen JLC board (their ids are in Nereus_Pi_Shield_Adin2111/ and in the stage-2c board d30920b); stage 6 did not add the
second one, it widened the track between them. So this job moves a carried via: the lock check lists it as "removed on instruction".
New site (4.267, 18.00), the same column 0.313 mm further south: hole edge 0.375 mm from the pad's copper, 0.35 mm from its mask opening.
The column is the only one: on the top layer the via stands between L6's two pads (x 2.97 .. 5.47), and south of it the 1.0 mm
Net-(J4-Pin_1) track on the bottom (north edge y 18.50) stops it at y 18.07 (0.13 mm) - built at 18.00 (0.20 mm).
Connection to the pad on the bottom: 1.0 mm from inside the pad to (4.267, 17.80) and 0.6 mm on to the via's centre (the 1.0 mm end cap ends
flush with the via's pad at y 18.30). The Internal 2 track is 2.0 mm wide round (4.267, 17.687): the new via stands inside its copper."""
import sys, os, subprocess, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage3_routing'))
import s3lib, pcbnew
OLD, NEWV, NET, B = (4.267, 17.687), (4.267, 18.0), '5V_LIFEPO4', '6 Bottom Layer'
if sys.argv[1] == '--pre':
    b = pcbnew.LoadBoard(sys.argv[2]); kill = [t for t in b.GetTracks() if t.m_Uuid.AsString() == os.environ['F1VIA']]
    assert len(kill) == 1 and kill[0].GetClass() == 'PCB_VIA' and s3lib.sn(kill[0].GetNetname()) == NET and max(abs(a - c) for a, c in zip(s3lib.N(kill[0].GetPosition()), OLD)) < 0.001, kill
    print('   removing the via %s at %s, %s (an item of the frozen board and of the stage-2c board)' % (os.environ['F1VIA'][:8], OLD, NET)); b.Remove(kill[0]); pcbnew.SaveBoard(sys.argv[2], b); sys.exit(0)
PATH = sys.argv[1]; PLAN = bool(os.environ.get('PLAN'))
if not PLAN:
    out = subprocess.run([sys.executable, '-B', os.path.abspath(__file__), '--pre', PATH], capture_output=True, text=True, env=os.environ); print(out.stdout.rstrip())
    if out.returncode: raise SystemExit('pre failed: ' + out.stderr[-800:])
r = s3lib.Router(PATH, '12 job 2'); C = 0.13
r.via(NET, NEWV, 0.6, 0.3, clr=C, note='second via of the F1 end, 0.313 mm south of the frozen board\'s')
r.track(NET, B, [(4.267, 16.6), (4.267, 17.8)], 1.0, clr=C, note='F1 pad 1 to the via')
r.track(NET, B, [(4.267, 17.8), NEWV], 0.6, clr=C, note='to the via\'s centre')
nb = r.report_bad()
# the new hole against every pad's copper and mask opening on the two outer layers
best = []
for f in r.b.GetFootprints():
    for p in f.Pads():
        if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH: continue
        bb = p.GetBoundingBox(); x0, y0 = s3lib.N(bb.GetPosition()); x1, y1 = s3lib.N(bb.GetEnd()); me = s3lib.mm(p.GetSolderMaskExpansion(pcbnew.B_Cu if f.IsFlipped() else pcbnew.F_Cu))
        d = math.hypot(max(x0 - NEWV[0], 0, NEWV[0] - x1), max(y0 - NEWV[1], 0, NEWV[1] - y1)) - 0.15; best.append((d - me, d, '%s pad %s (%s)' % (f.GetReference(), p.GetNumber(), 'bottom' if f.IsFlipped() else 'top')))
best.sort(); print('   new via hole (0.3 mm) at %s: nearest pads, hole edge to mask opening / to copper (pads as their boxes): %s' % (NEWV, '; '.join('%s %.3f / %.3f mm' % (n, a, c) for a, c, n in best[:3])))
if PLAN: print('   PLAN: pre-check hits %d, nothing saved' % nb); sys.exit(1 if nb else 0)
r.finish(PATH, sys.argv[2] if len(sys.argv) > 2 else None); r.summary()
sys.exit(1 if nb else 0)
