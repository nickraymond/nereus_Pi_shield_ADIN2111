"""Stage 12, job 1 (re-review N1, N5): the pad row J15..J19 gets more distance from header J1's pads. New-frame mm.
Usage: <KiCad python> job1_row.py <board> <stage-2c board> <stage-11 silk report.json> <silk report out.json> [log.json]

Chosen: round pads 1.7 -> 1.5 mm (1.0 mm hole, ring 0.25 mm all round) and the row 0.10 mm south (y 6.70 -> 6.80).
  - gap to J1's pads 0.23 -> 0.43 mm (1.93 + 0.10 between the rows, less 0.85 + 0.75).
  - a 1.5 mm circle at y 6.80 lies inside the old 1.7 mm circle at y 6.70 (0.10 + 0.75 = 0.85): on the outer layers no copper comes closer to
    anything south, east or west than it is today, so no outer-layer lane moves; only the track ends on the pads follow them.
  - with the hole at y 6.70 and a ring of 0.25 mm the best gap is 0.33 mm (oval or offset pads included), so the holes have to move; a 1.7 mm row
    0.20 mm south gives the same 0.43 mm but its copper reaches 0.20 mm further south: I2C0_SDA (top, lane y 7.8) would be at -0.05 mm and the
    Internal 1 / Internal 2 lanes at y 7.8 at 0.30 mm with no margin, i.e. three more lane groups to move.
Forced by the holes' 0.10 mm (inner layers, hole to copper 0.30 mm):
  Internal 1  I2C3_SCL lane y 7.60 -> 7.75 under J15 (hole to copper 0.300 -> 0.35 mm, N5); I2C3_SDA 8.00 -> 8.15 and CFG0_STRAP 8.40 -> 8.55 keep
              their 0.2 mm gaps to it. The three 45 degree steps at x 19..20.4 start 0.10 mm further east (J15 pad 4's hole).
              CFG0_STRAP's step at J16 pad 1 0.10 mm further west (that hole to copper would be 0.32 mm, 0.39 with the step moved).
  Internal 2  VBUS 1.5 mm lane y 8.30 -> 8.40 under J15 (hole to copper stays 0.35 mm).
Track ends on the pads (same lanes, 0.10 mm longer): GPIO14 / 15 / 19 / 20 / 21, PI_5V, PI_3V3 (bottom), GPIO17 (top), GPIO7 (Internal 1), GPIO12 (Internal 2).
Silkscreen: the 30 pad names and the row title "GPIO" stay where they are: the pads' south edge is where it was (y 7.55), so every name is as far
from its pad as approved. LABELS=1 moves the 31 texts 0.10 mm south with the holes; tried: "21" then comes 0.055 mm from the box line at y 9.0
on both sides (4 new silk_overlap items), so it is not built.
Plane fills: Sofar's no-net fill "NoConnect_Right" on the PWR plane loses a 0.17 mm2 tip at (53.2..53.7, 5.75..6.28), north-west of J19 pad 1: the
hole's antipad closes the neck it hung on (2 pieces, same area). With the row only 0.06 mm south the tip stays on, but the gap to J1 is 0.39 mm."""
import sys, os, json, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage3_routing'))
import s3lib, pcbnew
T, B, I1, I2 = 'Top Layer', '6 Bottom Layer', 'Internal 1', 'Internal 2'
ROW = {'J15': (10.91, 4), 'J16': (26.15, 2), 'J17': (33.77, 2), 'J18': (41.39, 4), 'J19': (54.09, 3)}; Y0, DYR, PADD = 6.70, float(os.environ.get('DYR', '0.10')), 1.5; Y = round(Y0 + DYR, 4)
YV = round(5.43 + DYR, 4)
def pre(path, rep_in, rep_out):
    """child process: the five footprints 0.10 mm south, pads 1.5 mm; the row's labels by the same offset"""
    b = pcbnew.LoadBoard(path); n = 0
    for ref, (x1, cnt) in ROW.items():
        f = b.FindFootprintByReference(ref); p0 = s3lib.N(f.GetPosition()); f.SetPosition(s3lib.V(p0[0], p0[1] + DYR))
        for p in f.Pads():
            assert s3lib.mm(p.GetSize(pcbnew.F_Cu).x) == 1.7 and s3lib.mm(p.GetDrillSize().x) == 1.0 and p.GetShape(pcbnew.F_Cu) == pcbnew.PAD_SHAPE_CIRCLE, (ref, p.GetNumber())
            p.SetSize(pcbnew.F_Cu, pcbnew.VECTOR2I(pcbnew.FromMM(PADD), pcbnew.FromMM(PADD))); c = s3lib.N(p.GetPosition()); assert abs(c[1] - Y) < 1e-4, c; n += 1
    rep = json.load(open(rep_in)); want = [l for l in rep['labels'] if l[0].startswith(tuple(ROW)) and ' pad ' in l[0] or l[0] == 'pad row title']; moved = 0
    if os.environ.get('LABELS', '0') == '1':
        lay = {'top': pcbnew.F_SilkS, 'bottom': pcbnew.B_SilkS}
        for d in b.GetDrawings():
            if d.GetClass() != 'PCB_TEXT' or d.GetLayer() not in lay.values(): continue
            q = s3lib.N(d.GetPosition())
            for l in want:
                if l[1] == d.GetText() and lay[l[7]] == d.GetLayer() and abs(q[0] - l[2]) < 0.006 and abs(q[1] - l[3]) < 0.006:
                    d.SetPosition(s3lib.V(q[0], q[1] + DYR)); l[3] = round(l[3] + DYR, 2); moved += 1; break
        assert moved == len(want) == 31, (moved, len(want))
    json.dump(rep, open(rep_out, 'w'), indent=0)
    pcbnew.SaveBoard(path, b); print('   %d pads of %s: 1.7 -> %.1f mm round, y %.2f -> %.2f; %d row labels moved %.2f mm south' % (n, ', '.join(ROW), PADD, Y0, Y, moved, DYR))
if sys.argv[1] == '--pre': pre(*sys.argv[2:5]); sys.exit(0)
PATH, BASE, REP_IN, REP_OUT = sys.argv[1:5]
out = subprocess.run([sys.executable, '-B', os.path.abspath(__file__), '--pre', PATH, REP_IN, REP_OUT], capture_output=True, text=True); print(out.stdout.rstrip())
if out.returncode: raise SystemExit('pre failed: ' + out.stderr[-1200:])
S = lambda net, layer, *pts: [(net, layer, (a[0], a[1], c[0], c[1]), 'seg') for a, c in zip(pts, pts[1:])]
old = {  # the pieces that go (exact segments, all our own), and what replaces them
 ('GPIO14', B, 0.2): ([(14.72, 3.5), (14.72, 5.43), (15.99, Y0)], [(14.72, 3.5), (14.72, YV), (15.99, Y)]),
 ('GPIO15', B, 0.2): ([(19.8, 3.5), (19.8, 5.43), (18.53, Y0)], [(19.8, 3.5), (19.8, YV), (18.53, Y)]),
 ('GPIO19', B, 0.2): ([(51.55, 4.77), (53.48, Y0), (54.09, Y0)], [(51.55, 4.77), (round(53.48 + DYR, 4), Y), (54.09, Y)]),
 ('GPIO20', B, 0.2): ([(55.36, 3.5), (55.36, 5.43), (56.63, Y0)], [(55.36, 3.5), (55.36, YV), (56.63, Y)]),
 ('GPIO21', B, 0.2): ([(57.9, 3.5), (57.9, 5.43), (59.17, Y0)], [(57.9, 3.5), (57.9, YV), (59.17, Y)]),
 ('PI_5V', B, 0.5): ([(10.91, Y0), (12.18, Y0)], [(10.91, Y), (12.18, Y)]),
 ('PI_3V3', B, 0.5): ([(28.69, 4.77), (28.69, Y0), (26.15, Y0)], [(28.69, 4.77), (28.69, Y), (26.15, Y)]),
 ('GPIO17', T, 0.2): ([(37.58, 1.4), (37.58, 5.43), (36.31, Y0)], [(37.58, 1.4), (37.58, YV), (36.31, Y)]),
 ('GPIO7', I1, 0.2): ([(42.66, 4.0), (42.66, 5.43), (43.93, Y0)], [(42.66, 4.0), (42.66, YV), (43.93, Y)]),
 ('GPIO12', I2, 0.2): ([(42.66, 4.0), (42.66, 5.43), (41.39, Y0)], [(42.66, 4.0), (42.66, YV), (41.39, Y)]),
 ('I2C3_SCL', I1, 0.2): ([(23.01, 6.65), (19.95, 6.65), (19.0, 7.6), (10.43, 7.6), (9.83, 8.2)], [(23.01, 6.65), (20.05, 6.65), (18.95, 7.75), (10.28, 7.75), (9.83, 8.2)]),
 ('I2C3_SDA', I1, 0.2): ([(23.87, 7.05), (20.116, 7.05), (19.166, 8.0), (10.79, 8.0), (10.19, 8.6)], [(23.87, 7.05), (20.216, 7.05), (19.116, 8.15), (10.64, 8.15), (10.19, 8.6)]),
 ('CFG0_STRAP', I1, 0.2): ([(41.61, 8.6), (26.65, 8.6), (25.5, 7.45), (20.28, 7.45), (19.33, 8.4), (12.2, 8.4), (11.6, 9.0)], [(41.61, 8.6), (26.55, 8.6), (25.4, 7.45), (20.38, 7.45), (19.28, 8.55), (12.05, 8.55), (11.6, 9.0)]),
 ('VBUS', I2, 1.5): ([(10.726, 9.3), (11.726, 8.3), (19.8, 8.3)], [(10.726, 9.3), (11.626, 8.4), (19.7, 8.4)]),
 ('VBUS', I2, 1.0): ([(19.8, 8.3), (21.0, 7.1)], [(19.7, 8.4), (21.0, 7.1)]),
}
rm = []
for (net, layer, w), (o, n) in old.items(): rm += S(net, layer, *o)
s3lib.prestep(PATH, BASE, removes=rm)
r = s3lib.Router(PATH, '12 job 1'); C = 0.13
INNER = {(I2, 'J18.1'), (I1, 'J18.2')}      # the row's pads have copper on the outer layers only, and on an inner layer where a track ends on them (stage 5)
for L in (I1, I2, 'GND Plane', 'PWR Plane'):
    r.geo.L[L] = [e for e in r.geo.L[L] if not (e[4].startswith('pad J1') and e[4].split()[1].split('.')[0] in ROW and (L, e[4].split()[1]) not in INNER)]
for (net, layer, w), (o, n) in old.items(): r.track(net, layer, n, w, clr=C)
nb = r.report_bad()
r.finish(PATH, sys.argv[5] if len(sys.argv) > 5 else None); r.summary()
sys.exit(1 if nb else 0)
