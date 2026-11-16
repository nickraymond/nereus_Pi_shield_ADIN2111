"""Stage 6, step 1: the electrical review's findings (REVIEW_ELECTRICAL.md, written against 397fdfd), re-measured on 76d258b.
Usage: <KiCad python> step1_review.py <board> <board out> [log.json]     env S3_BASE = the stage-2c board (d30920b)

 1  MOTOR_IN1 (Internal 2) leaves the U1 / Y1 area: from J1 pin 32 through the gap x 47.74 (was 45.2), x 48.45 past Sofar's 3V3 via
    (48.98, 12.11), then x 49.1 beside MOTOR_IN2 (x 49.5), and its own diagonal (x + y = 77.4) to the old lane y 38.05.
    ~PAYLOAD_FAULT takes the gap x 45.2 instead. MOTOR_IN2's diagonal moves south-east (x + y = 79.2, the other side of Sofar's GND via
    (47.93, 30.46)): one lane only fits between that via and the BM1_DATA vias (47.02, 28.86 / 29.51).
 2  MOTOR_nSLEEP (Internal 1): straight at x 55.36 to y 34.3, in the 0.5 mm gap between the BM1_N and BM1_P trunks (was x 56.25, under BM1_P).
    I2C3_SCL / I2C3_SDA (Internal 1): x 8.03 / 8.36 for y 17.6..25.9, west of the BM2_N trunk (copper x 8.53..10.53); was x 9.83 / 10.19.
 3  R9 (4.7 k strap on ADIN_MISO) back to the top layer beside J1 / U1: pad 2 on the ADIN_MISO track at (44.781, 9.89), as on the frozen
    board (44.78, 9.89). The 53.8 mm Internal 1 branch of ADIN_MISO goes; the static net CFG0_STRAP is the long one now (to JP4).
    R47 / R2 stay (see the log).
 4  5V_LIFEPO4: Internal 2 0.8 -> 2.0 mm, two vias at each end (the via in F1 pad 1 at (4.267, 15.887) is now used; new via (11.3, 23.05)).
 7  VBUS to the converter: Internal 2 1.0 -> 1.5 mm west of J15 pad 4 and east of J16 pad 1; 1.0 mm stays between x 20 and 25.5.
 9  ADIN_TIMER (Internal 1): x 9.3 for y 9.3..15.9 (was x 7.85 beside the switch node), then x 7.70.
11  C49 to U11 pin 1: the Internal 1 link 0.2 -> 0.5 mm (no bottom-layer path exists, see the log).
12  Two dangling stubs of the converter copper removed (uuids in DROP; the lock check lists them).
"""
import sys, os, json, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage3_routing'))
import s3lib, pcbnew
T, B, I1, I2 = 'Top Layer', '6 Bottom Layer', 'Internal 1', 'Internal 2'
DROP = {'89214ad6-26b4-421d-8de0-e5b3b5f7cfb4': '5V_PI top 0.18 mm stub (1.221, 14.511)-(1.346, 14.386)',
        '1745e174-32ff-4215-9962-73b7e474f208': 'VBUS bottom 0.70 mm stub (11.221, 10.194)-(10.726, 10.688)'}
R9_POS, R9_PAD2 = (44.381, 9.89), (44.781, 9.89)

def pre(path):
    """child process: R9 to the top layer, and the two listed stubs of the input board removed (nothing is queried after the first Remove)."""
    b = pcbnew.LoadBoard(path); f = b.FindFootprintByReference('R9'); old = s3lib.N(f.GetPosition())
    f.SetPosition(s3lib.V(*R9_POS))
    if f.IsFlipped(): f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    for k in range(4):
        p = [s3lib.N(q.GetPosition()) for q in f.Pads() if q.GetNumber() == '2'][0]
        if abs(p[0] - R9_PAD2[0]) < 0.02 and abs(p[1] - R9_PAD2[1]) < 0.02: break
        f.SetOrientationDegrees(f.GetOrientationDegrees() + 90)
    else: raise SystemExit('R9: pad 2 not at %s' % (R9_PAD2,))
    rt = f.Reference(); rt.SetPosition(s3lib.V(R9_POS[0] - 1.9, R9_POS[1] + 1.0)); rt.SetTextAngleDegrees(0)
    print('   R9 %s bottom -> %s top, %.0f deg, pad 2 at %s' % (old, R9_POS, f.GetOrientationDegrees(), p))
    kill = [t for t in b.GetTracks() if t.m_Uuid.AsString() in DROP]
    for t in kill: print('   dropping input item %s: %s' % (t.m_Uuid.AsString()[:8], DROP[t.m_Uuid.AsString()]))
    if len(kill) != len(DROP): raise SystemExit('DROP: %d of %d found' % (len(kill), len(DROP)))
    for t in kill: b.Remove(t)
    pcbnew.SaveBoard(path, b)
if len(sys.argv) > 2 and sys.argv[1] == '--pre': pre(sys.argv[2]); sys.exit(0)

out = subprocess.run([sys.executable, __file__, '--pre', sys.argv[1]], capture_output=True, text=True); print(out.stdout.strip())
if out.returncode: raise SystemExit('pre failed: ' + out.stderr[-800:])
rm = [('MOTOR_IN1', I2, (34.1, 2, 47, 38.1)), ('~{PAYLOAD_FAULT}', I2, (46.4, 4.7, 47.8, 8.3)), ('MOTOR_IN2', I2, (49.5, 28.1, 39.0, 38.6), 'seg'),
      ('MOTOR_nSLEEP', I1, (55.36, 22.31, 56.25, 23.2), 'seg'), ('MOTOR_nSLEEP', I1, (56.25, 23.2, 56.25, 38.24), 'seg'),
      ('ADIN_MISO', '*', (9, 3, 34, 37.5)),
      ('CFG0_STRAP', B, (9.3, 37.9, 10.5, 37.9), 'seg'), ('CFG0_STRAP', B, (10.5, 37.9, 11.0, 38.4), 'seg'),
      ('ADIN_TIMER', I1, (7.0, 7.0, 7.85, 7.85), 'seg'), ('ADIN_TIMER', I1, (7.85, 7.85, 7.85, 33.8), 'seg'), ('ADIN_TIMER', I1, (7.85, 33.8, 9.15, 35.1), 'seg'),
      ('I2C3_SCL', I1, (9.83, 8.2, 9.83, 37.29), 'seg'), ('I2C3_SDA', I1, (10.19, 8.6, 10.19, 37.14), 'seg'),
      ('5V_LIFEPO4', I2), ('VBUS', I2, (10, 7, 30.1, 12.8)),
      ('VBUS', I1, (44.5, 37.45, 50.4, 37.45), 'seg'), ('VBUS', I1, (50.4, 37.45, 50.7, 37.75), 'seg')]
s3lib.prestep(sys.argv[1], os.environ['S3_BASE'], removes=rm)
r = s3lib.Router(sys.argv[1], '6 review'); C = 0.13
ROW = ('J15', 'J16', 'J17', 'J18', 'J19'); INNER = {(I2, 'J18.1'), (I1, 'J18.2')}      # the row's pads have copper on the outer layers only (stage 5)
for L in (I1, I2, 'GND Plane', 'PWR Plane'):
    r.geo.L[L] = [e for e in r.geo.L[L] if not (e[4].startswith('pad J1') and e[4].split()[1].split('.')[0] in ROW and (L, e[4].split()[1]) not in INNER)]
# ---- 1  motor inputs
r.track('~{PAYLOAD_FAULT}', I2, [(46.47, 4.77), (45.2, 6.04), (45.2, 7.04), (46.45, 8.29)], 0.2, clr=C, note='gap x 45.2 (was 47.74)')
r.track('MOTOR_IN1', I2, [(46.47, 2.23), (47.74, 3.5), (47.74, 7.0), (48.45, 7.71), (48.45, 12.7), (49.1, 13.35), (49.1, 28.3), (39.35, 38.05), (34.2, 38.05)], 0.2, clr=C)
r.track('MOTOR_IN2', I2, [(49.5, 28.1), (49.5, 29.7), (40.6, 38.6), (39.0, 38.6)], 0.2, clr=C)
# ---- 2  lanes off the trunks
r.track('MOTOR_nSLEEP', I1, [(55.36, 22.31), (55.36, 34.3), (56.25, 35.19), (56.25, 38.24)], 0.2, clr=C)
r.track('I2C3_SCL', I1, [(9.83, 8.2), (9.83, 15.84), (8.03, 17.64), (8.03, 25.9), (9.83, 27.7), (9.83, 37.29)], 0.2, clr=C)
r.track('I2C3_SDA', I1, [(10.19, 8.6), (10.19, 15.95), (8.36, 17.78), (8.36, 25.4), (10.19, 27.23), (10.19, 37.14)], 0.2, clr=C)
# ---- 9  ADIN_TIMER away from the switch node
r.track('ADIN_TIMER', I1, [(7.0, 7.0), (9.3, 9.3), (9.3, 15.9), (7.7, 17.5), (7.7, 33.65), (9.15, 35.1)], 0.2, clr=C)
# ---- 3  R9 beside U1; CFG0_STRAP is the long net
r.track('CFG0_STRAP', T, [(43.981, 9.89), (42.9, 9.89)], 0.2, clr=C); r.via('CFG0_STRAP', (42.9, 9.89), clr=C)
r.track('CFG0_STRAP', I1, [(42.9, 9.89), (41.61, 8.6), (26.65, 8.6), (25.5, 7.45), (20.28, 7.45), (19.33, 8.4), (12.2, 8.4), (11.6, 9.0), (11.6, 12.0), (10.75, 12.85), (10.75, 32.25), (11.5, 33.0), (11.5, 35.2)], 0.2, clr=C)
r.via('CFG0_STRAP', (11.5, 35.2), clr=C, note='the old ADIN_MISO via site')
r.track('CFG0_STRAP', B, [(11.5, 35.2), (10.85, 35.85), (10.85, 38.25), (11.0, 38.4)], 0.2, clr=C)
# ---- 4  5V_LIFEPO4
r.track('5V_LIFEPO4', I2, [(4.267, 15.887), (4.267, 17.687), (8.0, 17.687), (11.3, 20.987), (11.3, 23.9)], 2.0, clr=C)
r.via('5V_LIFEPO4', (11.3, 23.05), clr=C); r.track('5V_LIFEPO4', B, [(11.3, 23.05), (11.3, 23.9)], 0.8, clr=C)
# ---- 7  VBUS feed
r.track('VBUS', I2, [(10.726, 10.688), (10.726, 9.3), (11.726, 8.3), (19.8, 8.3)], 1.5, clr=C)
r.track('VBUS', I2, [(19.8, 8.3), (21.0, 7.1), (24.2, 7.1), (25.55, 8.45)], 1.0, clr=C, note='neck: Sofar GND vias (22.28, 8.32), (23.73, 8.06) and the row holes')
r.track('VBUS', I2, [(25.55, 8.45), (28.95, 8.45), (29.75, 9.25), (29.75, 12.764)], 1.5, clr=C, note='x 29.75: PI_3V3 (ours, x 30.79) is 0.19 mm east of it')
r.track('VBUS', I2, [(29.75, 12.764), (29.981, 12.764)], 1.0, clr=C, note="into Sofar's via")
# ---- 11  C49 link
r.track('VBUS', I1, [(44.5, 37.45), (50.4, 37.45), (50.7, 37.75)], 0.5, clr=C)
n = r.report_bad()
r.finish(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None); r.summary()
sys.exit(1 if n else 0)
