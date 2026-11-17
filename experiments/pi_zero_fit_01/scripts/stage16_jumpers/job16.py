"""Stage 16: JP2 / JP3 / JP4 (bottom) 2.0 mm north so that the owner can put labels below them. New-frame mm.
Usage: <KiCad python> job16.py <board> [log.json]        PLAN=1: pre-check only, nothing saved (the child step still runs on a copy you give it)

Child step (--pre, own process: pcbnew's objects are stale after Remove()): the three footprints 2.0 mm north (pads, outline, own texts with
them); the 17 tracks / vias of the jumper links listed in KILL removed (each checked by uuid prefix, net and position); board texts on the
bottom silkscreen moved 2.0 mm north only if their drawn strokes would sit on a jumper pad's mask opening (pad + 0.025 mm).
Parent step: the new links, pre-checked against every copper layer (tracks 0.13 mm, vias 0.15 mm = hole edge 0.30 mm to other copper)."""
import sys, os, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage3_routing'))
import s3lib, pcbnew
DYM = -2.0; JPS = ('JP2', 'JP3', 'JP4'); B, I1 = '6 Bottom Layer', 'Internal 1'; TR = 36.139   # the Internal 1 ADIN_VDDIO trunk's y
KILL = [  # uuid prefix, net, (x, y) of start / via
 ('40c20d07', 'CFG0_STRAP', (11.5, 35.2)), ('f9e60f95', 'CFG0_STRAP', (11.5, 35.2)), ('d43c191b', 'CFG0_STRAP', (11.5, 33.0)), ('9e4eba03', 'CFG0_STRAP', (18.0, 37.8)),
 ('d13b8b12', 'CFG1_STRAP', (13.0, 33.4)), ('4dea72a6', 'GND', (14.3, 37.4)), ('6581825e', 'GND', (15.5, 37.4)),
 ('6cb15335', 'ADIN_VDDIO', (11.5, TR)), ('9f2aff15', 'ADIN_VDDIO', (16.55, TR)), ('324dcad4', 'ADIN_VDDIO', (18.95, TR)),
 ('45403483', 'ADIN_VDDIO', (11.5, TR)), ('e2d0ad10', 'ADIN_VDDIO', (11.5, 36.9)), ('c1da4ad0', 'ADIN_VDDIO', (11.7, 37.1)), ('a88ac4e3', 'ADIN_VDDIO', (16.55, TR)),
 ('0d6191d7', 'ADIN_VDDIO', (18.95, TR)), ('c7f794f8', 'ADIN_VDDIO', (19.3, 36.489)), ('ad78f28b', 'ADIN_LED_VDD', (20.1, 34.9))]
if sys.argv[1] == '--pre':
    b = pcbnew.LoadBoard(sys.argv[2]); mm = pcbnew.ToMM; dy = pcbnew.FromMM(DYM)
    for r in JPS:
        f = b.FindFootprintByReference(r); o = s3lib.N(f.GetPosition()); f.SetPosition(pcbnew.VECTOR2I(f.GetPosition().x, f.GetPosition().y + dy))
        print('   %s %s -> %s' % (r, o, s3lib.N(f.GetPosition())))
    pads = []
    for r in JPS:
        for p in b.FindFootprintByReference(r).Pads():
            bb = p.GetBoundingBox(); x0, y0 = s3lib.N(bb.GetPosition()); x1, y1 = s3lib.N(bb.GetEnd()); m = 0.025; pads.append((x0 - m, y0 - m, x1 + m, y1 + m, '%s.%s' % (r, p.GetNumber())))
    for d in b.GetDrawings():
        if d.GetClass() != 'PCB_TEXT' or d.GetLayer() != pcbnew.B_SilkS: continue
        x0, y0 = s3lib.N(d.GetBoundingBox().GetPosition())
        if not (8 < x0 < 22 and 26 < y0 < 39.5): continue
        ps = pcbnew.SHAPE_POLY_SET(); d.TransformShapeToPolySet(ps, pcbnew.B_SilkS, 0, pcbnew.FromMM(0.005), pcbnew.ERROR_INSIDE)
        hit = []
        for a in pads:
            box = pcbnew.SHAPE_POLY_SET(); box.NewOutline()
            for x, y in ((a[0], a[1]), (a[2], a[1]), (a[2], a[3]), (a[0], a[3])): v = s3lib.V(x, y); box.Append(v.x, v.y)
            ib = pcbnew.SHAPE_POLY_SET(ps); ib.BooleanIntersection(box)
            if ib.OutlineCount(): hit.append(a[4])
        bb = ps.BBox(); e = (s3lib.N(bb.GetPosition()), s3lib.N(bb.GetEnd()))
        if hit: d.Move(pcbnew.VECTOR2I(0, dy))
        print('   board text %-5r strokes %s..%s: %s' % (d.GetText(), e[0], e[1], ('on ' + ', '.join(hit) + ' -> 2.0 mm north') if hit else 'clear of the jumper pads, stays'))
    kill = []
    for t in b.GetTracks():
        u = t.m_Uuid.AsString()
        for k in KILL:
            if u.startswith(k[0]):
                p = s3lib.N(t.GetStart()); q = s3lib.N(t.GetEnd())
                assert s3lib.sn(t.GetNetname()) == k[1] and any(max(abs(a - c) for a, c in zip(z, k[2])) < 0.002 for z in (p, q)), (k, p, q)
                kill.append(t); print('   removing %s %s %s %s-%s %s' % (k[0], t.GetClass()[4:], k[1], p, q, '' if t.GetClass() == 'PCB_VIA' else t.GetLayerName()))
    assert len(kill) == len(KILL), (len(kill), len(KILL))
    for t in kill: b.Remove(t)
    pcbnew.SaveBoard(sys.argv[2], b); sys.exit(0)
PATH = sys.argv[1]; PLAN = bool(os.environ.get('PLAN'))
out = subprocess.run([sys.executable, '-B', os.path.abspath(__file__), '--pre', PATH], capture_output=True, text=True); print(out.stdout.rstrip())
if out.returncode: raise SystemExit('pre failed: ' + out.stderr[-1500:])
r = s3lib.Router(PATH, '16 jumpers'); C, CV = 0.13, 0.15; W = 0.2
# ADIN_VDDIO: JP3 pad 1 and JP4 pad 3 from the Internal 1 trunk through vias 0.66 mm further south (clear of the pads by 0.35 mm);
# JP2 pad 1 (its old via now sits under JP4) from a new via west of JP2, the only spot where the top layer is free of the BM2 trunks and J9
r.track('ADIN_VDDIO', I1, [(11.5, TR), (11.5, 36.8)], W, clr=C, note='trunk end to the moved JP3 via')
r.via('ADIN_VDDIO', (11.5, 36.8), clr=CV, note='JP3 pad 1 via, was (11.5, 36.139)')
r.track('ADIN_VDDIO', B, [(11.5, 36.8), (11.7, 36.6), (11.7, 35.4)], W, clr=C, note='to JP3 pad 1')
r.track('ADIN_VDDIO', I1, [(18.95, TR), (18.95, 36.8)], W, clr=C, note='trunk to the moved JP4 via')
r.via('ADIN_VDDIO', (18.95, 36.8), clr=CV, note='JP4 pad 3 via, was (18.95, 36.139)')
r.track('ADIN_VDDIO', B, [(18.95, 36.8), (19.3, 36.45), (19.3, 35.4)], W, clr=C, note='to JP4 pad 3')
r.via('ADIN_VDDIO', (13.3, 32.3), clr=CV, note='JP2 pad 1 via, was (16.55, 36.139)')
r.track('ADIN_VDDIO', I1, [(13.3, 32.3), (13.3, TR)], W, clr=C, note='JP2 via down to the trunk')
r.track('ADIN_VDDIO', B, [(13.3, 32.3), (16.55, 32.3)], W, clr=C, note='to JP2 pad 1')
# ADIN_LED_VDD: JP2 pad 2 to the existing x 20.1 run
r.track('ADIN_LED_VDD', B, [(20.1, 34.9), (20.1, 32.95), (19.45, 32.3)], W, clr=C, note='JP2 pad 2')
# CFG0_STRAP: its via left the place of JP3 pad 1; new via north of JP3, bottom jog between R2 / SPI_CFG1's via and JP3 pad 1; JP4 end shortened
r.track('CFG0_STRAP', I1, [(11.5, 33.0), (11.5, 33.4), (11.7, 33.6)], W, clr=C, note='Internal 1 to the new via')
r.via('CFG0_STRAP', (11.7, 33.6), clr=CV, note='was (11.5, 35.2)')
r.track('CFG0_STRAP', B, [(11.7, 33.6), (11.7, 33.76), (10.85, 34.61), (10.85, 35.85)], W, clr=C, note='to the existing x 10.85 run')
r.track('CFG0_STRAP', B, [(18.0, 37.8), (18.0, 35.4)], W, clr=C, note='to JP4 pad 2')
# CFG1_STRAP and GND: the jumper ends follow the pads
r.track('CFG1_STRAP', B, [(13.0, 33.4), (13.0, 35.4)], W, clr=C, note='to JP3 pad 2')
r.track('GND', B, [(14.3, 35.4), (15.5, 35.4), (16.7, 35.4)], W, clr=C, note='JP3 pad 3 - via (15.5, 35.45) - JP4 pad 1')
nb = r.report_bad()
if PLAN: print('   PLAN: pre-check hits %d, nothing saved' % nb); sys.exit(1 if nb else 0)
r.finish(PATH, sys.argv[2] if len(sys.argv) > 2 else None); r.summary(); sys.exit(1 if nb else 0)
