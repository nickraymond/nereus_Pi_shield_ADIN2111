"""Stage 3 phase M (fourth session): clean-up of stage 3's own copper. No net changes its route. Usage: <KiCad python> phaseM.py <in> <out> [log.json]

By hand (each one a removed piece and its replacement):
  strap net, bottom at R2: the link from R47 met the R2 track at 45 deg (an acute corner); now straight north onto it, a T at 90 deg.
  ADIN_TIMER, Internal 1 at J1 pin 36: the lane overshot the pin and came back at 45 deg (acute); now it leaves the lane 135 deg before the pin.
  5V_PI, bottom at the bulk rail: the 1.0 mm trunk ended in a diagonal plus a 0.07 mm link lying on top of it; now the trunk runs straight onto the rail.
  MOTOR_IN2, Internal 2: two collinear pieces along y 38.6 merged.
  PI_3V3 (top, at J1 pin 17; Internal 2 at the via (30.3, 35.5)) and MOTOR_IN1 (Internal 2 at J1 pin 32): ends that stopped 0.02..0.04 mm beside the
  pad / via centre now end on it. PI_3V3's Internal 2 branch to the Qwiic pull-ups left that via at 45 deg to the feed (acute); it is now a T at 90 deg
  on the feed at y 34.0, one straight piece to the via (36.6, 34.0).
By rule: every end of a stage-3 track that stops inside a pad of its own net 0.08 mm or more off the pad's centre, with nothing else connected at that
  end, gets a piece on to the centre (straight, or 45 deg then straight; the piece stays inside the pad). Where that piece is in line with the
  track's last segment and as wide, the last segment is replaced by one longer segment instead (removed in a second child step after the save). Not touched, on purpose (KEEP): ends in
  the long bus / inductor / thermal pads where the track is meant to stop at the pad's edge.
"""
import sys, os, math, s3lib
T, B, I1, I2 = 'Top Layer', '6 Bottom Layer', 'Internal 1', 'Internal 2'
ST = 'Net-(U1A-P1_LED_0{slash}SPI_CFG1)'; seg = lambda net, layer, a, b: (net, layer, (a[0], a[1], b[0], b[1]), 'seg')
s3lib.prestep(sys.argv[1], os.environ['S3_BASE'], removes=[
    seg(ST, B, (9.775, 34.875), (9.3, 34.4)), seg(ST, B, (9.775, 35.9), (9.775, 34.875)), seg(ST, B, (9.3, 34.4), (10.25, 34.4)),
    seg('ADIN_TIMER', I1, (7.85, 0.85), (52.93, 0.85)), seg('ADIN_TIMER', I1, (52.93, 0.85), (51.55, 2.23)),
    seg('5V_PI', B, (7.15, 20.2), (7.15, 29.6)), seg('5V_PI', B, (7.15, 29.6), (6.6, 30.15)), seg('5V_PI', B, (6.6, 30.15), (6.65, 30.1)), seg('5V_PI', B, (4.4, 30.1), (7.5, 30.1)),
    seg('MOTOR_IN2', I2, (7.5, 38.6), (8.1, 38.6)), seg('MOTOR_IN2', I2, (8.1, 38.6), (39.0, 38.6)),
    seg('PI_3V3', T, (9.47, 3.67), (27.57, 3.67)), seg('PI_3V3', T, (27.57, 3.67), (28.67, 4.77)),
    seg('PI_3V3', I2, (35.19, 28.97), (30.29, 33.87)), seg('PI_3V3', I2, (30.29, 33.87), (30.29, 35.47)), seg('PI_3V3', I2, (30.3, 35.5), (31.8, 34.0)), seg('PI_3V3', I2, (31.8, 34.0), (36.6, 34.0)),
    seg('MOTOR_IN1', I2, (45.3, 12.75), (45.3, 3.45)), seg('MOTOR_IN1', I2, (45.3, 3.45), (46.5, 2.25))])
r = s3lib.Router(sys.argv[1], 'M'); C = 0.13
# ---- body ----
r.track(ST, B, [(9.775, 35.9), (9.775, 34.4)], 0.2, clr=C); r.track(ST, B, [(9.3, 34.4), (9.775, 34.4)], 0.2, clr=C); r.track(ST, B, [(9.775, 34.4), (10.25, 34.4)], 0.2, clr=C)
r.track('ADIN_TIMER', I1, [(7.85, 0.85), (50.17, 0.85), (51.55, 2.23)], 0.2, clr=C)
r.track('5V_PI', B, [(7.15, 20.2), (7.15, 30.1)], 1.0, clr=C); r.track('5V_PI', B, [(4.4, 30.1), (7.15, 30.1)], 1.0, clr=C); r.track('5V_PI', B, [(7.15, 30.1), (7.5, 30.1)], 1.0, clr=C)
r.track('MOTOR_IN2', I2, [(7.5, 38.6), (39.0, 38.6)], 0.2)
r.track('PI_3V3', T, [(9.47, 3.67), (27.59, 3.67), (28.69, 4.77)], 0.2, clr=C)
r.track('PI_3V3', I2, [(35.19, 28.97), (30.3, 33.86), (30.3, 34.0)], 0.2, clr=C); r.track('PI_3V3', I2, [(30.3, 34.0), (30.3, 35.5)], 0.2, clr=C); r.track('PI_3V3', I2, [(30.3, 34.0), (36.6, 34.0)], 0.2, clr=C)
r.track('MOTOR_IN1', I2, [(45.3, 12.75), (45.3, 3.4), (46.47, 2.23)], 0.2, clr=C)
# ---- end ----
# --- by rule: ends inside own-net pads, off-centre
KEEP = ('L6.2', 'L1.3', 'U11.11', 'J9.1', 'J9.2', 'J9.3', 'J9.4', 'J10.1', 'J10.2', 'J10.3', 'J10.4')
base = s3lib.base_uuids(os.environ['S3_BASE']); b = r.b; N = s3lib.N; key = lambda p: (round(p[0], 3), round(p[1], 3))
tracks = [(t.m_Uuid.AsString(), s3lib.sn(t.GetNetname()), t.GetLayerName(), N(t.GetStart()), N(t.GetEnd()), s3lib.mm(t.GetWidth())) for t in b.GetTracks() if t.GetClass() != 'PCB_VIA']
vias = set((s3lib.sn(t.GetNetname()), key(N(t.GetStart()))) for t in b.GetTracks() if t.GetClass() == 'PCB_VIA')
pads = []
for f in b.GetFootprints():
    for p in f.Pads():
        bb = p.GetBoundingBox(); x0, y0 = N(bb.GetPosition()); x1, y1 = N(bb.GetEnd())
        pads.append((f.GetReference() + '.' + p.GetNumber(), s3lib.sn(p.GetNetname()), N(p.GetPosition()), (x0, y0, x1, y1), [b.GetLayerName(l) for l in p.GetLayerSet().CuStack()]))
cnt = {}
for u, net, layer, a, bb_, w in tracks:
    for e in (a, bb_): cnt[(net, layer, key(e))] = cnt.get((net, layer, key(e)), 0) + 1
def on_other(p, net, layer, me):
    for u, n2, l2, a, c, w in tracks:
        if u == me or n2 != net or l2 != layer: continue
        if s3lib._pt_seg(p[0], p[1], a[0], a[1], c[0], c[1]) < 0.02 and key(a) != key(p) and key(c) != key(p): return True
    return False
fixed = []; left = []; post = []
for u, net, layer, a, c, w in tracks:
    if u in base: continue
    for e, o in ((a, c), (c, a)):
        if cnt[(net, layer, key(e))] > 1 or (net, key(e)) in vias or on_other(e, net, layer, u): continue
        for name, pnet, pc, bb, pl in pads:
            if pnet != net or layer not in pl or not (bb[0] - 1e-3 <= e[0] <= bb[2] + 1e-3 and bb[1] - 1e-3 <= e[1] <= bb[3] + 1e-3): continue
            off = math.hypot(e[0] - pc[0], e[1] - pc[1])
            if off < 0.0115: break
            if off < 0.08 or name in KEEP: left.append((name, net, layer, e, round(off, 3))); break
            tx = e[0] if abs(e[0] - pc[0]) < 0.03 else pc[0]; ty = e[1] if abs(e[1] - pc[1]) < 0.03 else pc[1]
            dx, dy = tx - e[0], ty - e[1]; m = min(abs(dx), abs(dy))
            pts = [e] if m < 1e-6 or abs(abs(dx) - abs(dy)) < 1e-6 else [e, (round(e[0] + math.copysign(m, dx), 4), round(e[1] + math.copysign(m, dy), 4))]
            pts.append((round(tx, 4), round(ty, 4)))
            if not all(bb[0] - 1e-3 <= q[0] <= bb[2] + 1e-3 and bb[1] - 1e-3 <= q[1] <= bb[3] + 1e-3 for q in pts): left.append((name, net, layer, e, round(off, 3))); break
            ww = min(w, max(0.2, round(min(bb[2] - bb[0], bb[3] - bb[1]), 2)))       # never wider than the pad is narrow
            if len(pts) == 2 and abs(ww - w) < 1e-6 and abs((o[0] - e[0]) * (pts[1][1] - e[1]) - (o[1] - e[1]) * (pts[1][0] - e[0])) < 1e-6 and (o[0] - e[0]) * (pts[1][0] - e[0]) + (o[1] - e[1]) * (pts[1][1] - e[1]) < 0:
                post.append(seg(net, layer, o, e)); pts = [o, pts[1]]        # in line: one longer segment replaces the last one
            r.track(net, layer, pts, ww, clr=C, note='to the centre of ' + name, allow=('copper graphic in JP1',) if name.startswith('JP1.') else ())   # JP1's own bridge between pads 1 and 2; fixed.append((name, net, layer, e, round(off, 3), pts[1:], ww)); break
for x in fixed: print('   to pad centre: %-8s %-28s %-15s end %s was %.3f mm off; added %s, %.2f mm wide' % x)
for x in left: print('   left as it is: %-8s %-28s %-15s end %s, %.3f mm off the centre' % x)
print('pad-centre rule: %d ends extended, %d left (under 0.08 mm, or in KEEP %s)' % (len(fixed), len(left), ', '.join(KEEP)))
n = r.report_bad()
r.finish(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None); r.summary()
print('second step: %d last segments replaced by the longer ones' % len(post))
if post: s3lib.prestep(sys.argv[2], os.environ['S3_BASE'], removes=post)
sys.exit(1 if n else 0)
