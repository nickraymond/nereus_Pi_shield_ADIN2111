"""Stage 5, step 2: board follows the schematic of step 1 (method of stage 2b / 2c / 4: footprints from the libraries, nets and
fields from the netlist; nothing is routed here). New-frame mm.
Usage: <KiCad python> step2_sync.py <board> <netlist> <board out>            (adds the row, applies the netlist)
       <KiCad python> step2_sync.py --remove <board>                          (first, in its own process: J11..J14 go)

The row: y 6.70, on J1's pin columns (x = 8.37 + 2.54 k), 1.93 mm south of J1's southern pin row. Sites measured against the fixed
copper only (scan.py / sites16.py in the NereusData folder): 15 columns are clean for a 1.7 mm pad / 1.0 mm hole.
  J15 1x04  x 10.91 13.45 15.99 18.53   PI_5V GND GPIO14 GPIO15
  J16 1x02  x 26.15 28.69               PI_3V3 PI_3V3
  J17 1x02  x 33.77 36.31               GND GPIO17
  J18 1x04  x 41.39 43.93 46.47 49.01   GPIO18 GPIO7 GND GND
  J19 1x03  x 54.09 56.63 59.17         GPIO19 GPIO20 GPIO21
Not used: column 31.23 (a GND pad there would merge with Sofar's GND via at (32.231, 6.864): via centre 1.01 mm from the pad centre,
its 0.2 mm hole 0.06 mm from the pad's copper edge); columns 21.07 / 23.61 (VBUS, 1.0 mm on Internal 2, has to pass north of Sofar's
vias at (22.28, 8.32) and (23.73, 8.06) there); 38.85 (R43 and Sofar's GND via); 51.55 (Sofar's GND and ADIN_PWR vias).
Bare solder holes, not parts. Each stock footprint is changed on the board in these ways only (DRC reports them as
lib_footprint_mismatch, a warning type the board already has): no silkscreen, fabrication outline or courtyard (the stock ones are
the header's body; no part is fitted), no 3D model, reference hidden, pad 1 round like the others, attributes "exclude from BOM" and
"exclude from position files", and the pads keep copper only on the outer layers and on inner layers where they connect.
"""
import sys, os, importlib.util, pcbnew
HERE = os.path.dirname(os.path.abspath(__file__))
OLD = ('J11', 'J12', 'J13', 'J14')
if sys.argv[1] == '--remove':
    b = pcbnew.LoadBoard(sys.argv[2]); kill = [f for f in b.GetFootprints() if f.GetReference() in OLD]
    names = sorted(f.GetReference() for f in kill); assert names == sorted(OLD), names
    for f in kill: b.Remove(f)
    pcbnew.SaveBoard(sys.argv[2], b); print('  removed footprints', names); sys.exit(0)
sys.path.insert(0, os.path.join(HERE, '..', 'stage2b_board_sync'))
spec = importlib.util.spec_from_file_location('sync2b', os.path.join(HERE, '..', 'stage2b_board_sync', 's3lib.py')); L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
L.PROJ = os.path.dirname(os.path.abspath(sys.argv[1]))
V, N, mm, IU = L.V, L.N, L.mm, pcbnew.FromMM
ROW_Y = 6.70
def stripped(fpid):
    """the stock footprint without its outline graphics (silkscreen, fabrication, courtyard) and 3D model: the library file is
    copied to a temporary folder with those blocks cut out as text, and loaded from there (removing items from a loaded footprint
    upsets pcbnew's Python layer, LOG.md stage 3)."""
    import tempfile, re
    lib, name = fpid.split(':'); src = open(L.STOCK + lib + '.pretty/' + name + '.kicad_mod', encoding='utf-8').read()
    out = []; i = 0; cut = 0
    for m in re.finditer(r'\n\t\((fp_line|fp_rect|fp_poly|fp_circle|fp_arc|model)\b', src):
        if m.start() < i: continue
        depth = 0; j = m.start() + 2
        while True:
            ch = src[j]
            if ch == '"':
                j += 1
                while src[j] != '"': j += 2 if src[j] == '\\' else 1
            elif ch == '(': depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0: break
            j += 1
        blk = src[m.start():j + 1]
        if m.group(1) == 'model' or re.search(r'\(layer "F\.(SilkS|Fab|CrtYd)"\)', blk): out.append(src[i:m.start()]); i = j + 1; cut += 1
    out.append(src[i:]); d = tempfile.mkdtemp(suffix='.pretty'); open(os.path.join(d, name + '.kicad_mod'), 'w', encoding='utf-8').write(''.join(out))
    f = pcbnew.FootprintLoad(d, name); f.SetFPID(pcbnew.LIB_ID(lib, name)); print('  %s: %d outline / model blocks left out' % (name, cut))
    return f
PLACE = {'J15': (10.91, 4), 'J16': (26.15, 2), 'J17': (33.77, 2), 'J18': (41.39, 4), 'J19': (54.09, 3)}     # x of pad 1, number of pads
b = pcbnew.LoadBoard(sys.argv[1]); comps = L.load_netlist(sys.argv[2]); fps = L.by_ref(b)
missing = sorted(r for r in comps if r not in fps); extra = sorted(r for r in fps if r not in comps and fps[r].GetPath().AsString())
assert missing == sorted(PLACE), ('the parts to add are not the parts this script places', missing)
assert not [r for r in OLD if r in fps], 'J11..J14 are still on the board'
for r, (x1, n) in PLACE.items():
    f = stripped(comps[r]['fpid'])
    f.SetAttributes(pcbnew.FP_THROUGH_HOLE | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES)
    f.Reference().SetVisible(False)
    for q in f.Pads():
        q.SetShape(pcbnew.F_Cu, pcbnew.PAD_SHAPE_CIRCLE); q.SetUnconnectedLayerMode(pcbnew.UNCONNECTED_LAYER_MODE_REMOVE_EXCEPT_START_AND_END)
    b.Add(f); f.SetPosition(V(x1, ROW_Y))
    pad = lambda k: [q for q in f.Pads() if q.GetNumber() == k][0]
    last = (round(x1 + 2.54 * (n - 1), 4), ROW_Y)
    for rot in (0, 90, 180, 270):
        f.SetOrientationDegrees(rot); q = N(pad(str(n)).GetPosition())
        if abs(q[0] - last[0]) < 0.005 and abs(q[1] - last[1]) < 0.005: break
    else: raise SystemExit('%s: no turn puts pad %d at %s' % (r, n, last))
    L.apply(b, f, r, comps[r]); assert not L.diff_one(f, comps[r]), (r, L.diff_one(f, comps[r]))
    print('  %-4s %-52s top %3.0f deg' % (r, L.fpid_str(f), f.GetOrientationDegrees()))
    for q in f.Pads(): print('        pad %s %-7s (%.2f, %.2f)  %.1f mm pad, %.1f mm hole' % (q.GetNumber(), q.GetNetname().split('/')[-1], *N(q.GetPosition()), mm(q.GetBoundingBox().GetWidth()), mm(q.GetDrillSize().x)))
for r in ('J1', 'TP40', 'TP41', 'TP42', 'TP43'):      # J1: pad nets; the test points: the new symbols' links (same nets, same place)
    f = fps[r]; pos, rot = f.GetPosition(), f.GetOrientationDegrees(); d = L.diff_one(f, comps[r])
    L.apply(b, f, r, comps[r]); assert (f.GetPosition(), f.GetOrientationDegrees()) == (pos, rot) and not L.diff_one(f, comps[r])
    print('  %s: %s' % (r, '; '.join(t for k, t in d if k != 'path') or 'symbol link only'))
rest = [(r, [x for x in L.diff_one(fps[r], comps[r]) if x[0] != 'pin']) for r in sorted(fps) if r in comps]
print('  other differences board / netlist (not touched):', [x for x in rest if x[1]] or 'none')
used = {p.GetNetname() for f in b.GetFootprints() for p in f.Pads()} | {t.GetNetname() for t in b.GetTracks()} | {z.GetNetname() for z in b.Zones()}
dead = [n for name, n in b.GetNetInfo().NetsByName().items() if str(name) and str(name) not in used]
print('  nets removed (nothing uses them):', sorted(n.GetNetname() for n in dead) or 'none')
for x in dead: b.Remove(x)
pcbnew.SaveBoard(sys.argv[3], b); print('saved', sys.argv[3])
