"""Stage 21: top-entry (vertical) JST connectors on the south wall. New-frame mm.
Usage: <KiCad python> job21.py <board> [log.json]        PLAN=1: pre-check only, nothing saved

Fit (fit21.py, measured on 4676018): the vertical footprints put the signal pads on the SOUTH side of the body and the mounting
pads on the north side, so the new pads land where the side-entry bodies covered the board. Under those bodies sit vias of other
nets; only J9 fits. J7, J8, J3, J10 stay side-entry (blockers in fit21.py's output and the stage report).

J9 (BM2): JST_GH_BM04B-GHS-TBT, rotation 0 (pin 1 west, as the side-entry part), y 36.15 (courtyard 3.345 below the centre:
39.495, inside the 39.5 edge; pads end 38.95, 0.55 from the edge), x 16.375 = old x + 0.15: at the old x the west mounting pad
touches the CFG0_STRAP via at (11.7, 33.6) (0.0 mm); +0.15 gives 0.15 mm copper / 0.30 mm hole clearance.
Child step (--pre, own process: pcbnew's objects are stale after Remove()): J9 replaced (fields, path, label positions copied; pad
nets by number; mounting pads no net, as today); the two BM2 trunk end segments that ran to the old pads removed; the board text
'J9' moved north only as far as needed to clear the new west mounting pad by 0.15 mm (the project's pad-to-silk rule).
Parent step: the trunks to the new pads, 2.0 mm; BM2_N necks to 1.4 mm for 3.2 mm to pass between the new west mounting pad and
the GND via at (15.5, 35.45) (stage-3 phase F used the same 1.4 mm neck on BM1_P)."""
import sys, os, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage3_routing'))
import s3lib, pcbnew
LIB = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Connector_JST.pretty'
SWAP = {'J9': ('JST_GH_BM04B-GHS-TBT_1x04-1MP_P1.25mm_Vertical', (16.375, 36.15), 'BM04B-GHS')}
KILL = [('749c0c06', 'BM2_N', (14.975, 33.9)), ('5622de3e', 'BM2_P', (17.475, 33.9))]   # uuid prefix, net, end at the old pads
SILK_CLR = 0.15
FIELDS = {'PLANNED MPN': 'BM04B-GHS-TBT', 'PLANNED LCSC': '', 'PLANNED NOTE': 'top-entry variant: LCSC number not looked up', 'SOURCING': ''}
if sys.argv[1] == '--pre':
    b = pcbnew.LoadBoard(sys.argv[2])
    for ref, (name, pos, val) in SWAP.items():
        old = b.FindFootprintByReference(ref); new = pcbnew.FootprintLoad(LIB, name)
        new.SetFPID(pcbnew.LIB_ID('Connector_JST', name)); b.Add(new)
        new.SetPosition(s3lib.V(*pos)); new.SetOrientationDegrees(0)
        new.SetPath(old.GetPath()); new.SetSheetname(old.GetSheetname()); new.SetSheetfile(old.GetSheetfile()); new.SetAttributes(old.GetAttributes())
        for fl in old.GetFields():
            nm = fl.GetName()
            if nm == 'Reference': new.SetReference(fl.GetText())
            elif nm == 'Value': new.SetValue(val)
            else: new.SetField(nm, fl.GetText())
            nf = new.GetField(nm); nf.SetAttributes(fl); nf.SetLayer(fl.GetLayer()); nf.SetVisible(fl.IsVisible())
            nf.SetPosition(fl.GetPosition() if nm == 'Reference' else pcbnew.VECTOR2I(new.GetPosition().x + fl.GetPosition().x - old.GetPosition().x, new.GetPosition().y + fl.GetPosition().y - old.GetPosition().y))
        for nm, v in FIELDS.items(): new.GetField(nm).SetText(v)     # the schematic's new values (sch21.py), parity
        nets = {p.GetNumber(): p.GetNet() for p in old.Pads() if p.GetNumber() != 'MP'}
        for p in new.Pads():
            if p.GetNumber() in nets: p.SetNet(nets[p.GetNumber()])
        print('   %s %s %s -> %s %s %s; pads %s' % (ref, old.GetFPIDAsString().split(':')[1], s3lib.N(old.GetPosition()), name, s3lib.N(new.GetPosition()), new.GetOrientationDegrees(),
              ', '.join('%s %s %s' % (p.GetNumber(), s3lib.N(p.GetPosition()), s3lib.sn(p.GetNetname()) or '-') for p in new.Pads())))
        mps = []
        for p in new.Pads():
            if p.GetNumber() == 'MP':
                bb = p.GetBoundingBox(); x0, y0 = s3lib.N(bb.GetPosition()); x1, y1 = s3lib.N(bb.GetEnd()); mps.append((x0, y0, x1, y1))
        b.Remove(old)
        for d in b.GetDrawings():
            if d.GetClass() != 'PCB_TEXT' or d.GetLayer() != pcbnew.F_SilkS or d.GetText() != ref: continue
            ps = pcbnew.SHAPE_POLY_SET(); d.TransformShapeToPolySet(ps, pcbnew.F_SilkS, 0, pcbnew.FromMM(0.005), pcbnew.ERROR_INSIDE)
            bb = ps.BBox(); x0, y0 = s3lib.N(bb.GetPosition()); x1, y1 = s3lib.N(bb.GetEnd())
            need = 0.0
            for a in mps:
                if x0 < a[2] + SILK_CLR and a[0] - SILK_CLR < x1 and y0 < a[3] + SILK_CLR and a[1] - SILK_CLR < y1: need = max(need, y1 - (a[1] - SILK_CLR))
            need = round(need + 0.005, 2)
            if need: d.Move(pcbnew.VECTOR2I(0, -pcbnew.FromMM(need)))
            print('   board text %r strokes (%.3f, %.3f)..(%.3f, %.3f): %s' % (d.GetText(), x0, y0, x1, y1, ('moved %.2f mm north' % need) if need else 'clear, stays'))
    kill = []
    for t in b.GetTracks():
        u = t.m_Uuid.AsString()
        for k in KILL:
            if u.startswith(k[0]):
                p = s3lib.N(t.GetStart()); q = s3lib.N(t.GetEnd())
                assert s3lib.sn(t.GetNetname()) == k[1] and any(max(abs(a - c) for a, c in zip(z, k[2])) < 0.002 for z in (p, q)), (k, p, q)
                kill.append(t); print('   removing %s %s %s-%s w %.2f %s' % (k[0], k[1], p, q, s3lib.mm(t.GetWidth()), t.GetLayerName()))
    assert len(kill) == len(KILL), (len(kill), len(KILL))
    for t in kill: b.Remove(t)
    pcbnew.SaveBoard(sys.argv[2], b); sys.exit(0)
PATH = sys.argv[1]; PLAN = bool(os.environ.get('PLAN'))
out = subprocess.run([sys.executable, '-B', os.path.abspath(__file__), '--pre', PATH], capture_output=True, text=True); print(out.stdout.rstrip())
if out.returncode: raise SystemExit('pre failed: ' + out.stderr[-1500:])
r = s3lib.Router(PATH, '21 top entry'); C = 0.15; T = 'Top Layer'
r.track('BM2_P', T, [(17.475, 29.3), (17.475, 37.9)], 2.0, clr=C, note='trunk to J9 pads 3 / 4, as before but 4.0 mm longer')
r.track('BM2_N', T, [(14.975, 30.335), (14.975, 33.0)], 2.0, clr=C, note='trunk, as before to y 33.0')
r.track('BM2_N', T, [(14.975, 33.0), (14.3, 33.675), (14.3, 36.2), (15.0, 36.9)], 1.4, clr=C, note='1.4 mm neck between the J9 west mounting pad and the GND via (15.5, 35.45)')
r.track('BM2_N', T, [(15.0, 36.9), (15.0, 37.9)], 2.0, clr=C, note='to J9 pads 1 / 2')
nb = r.report_bad()
if PLAN: print('   PLAN: pre-check hits %d, nothing saved' % nb); sys.exit(1 if nb else 0)
r.finish(PATH, sys.argv[2] if len(sys.argv) > 2 else None); r.summary(); sys.exit(1 if nb else 0)
