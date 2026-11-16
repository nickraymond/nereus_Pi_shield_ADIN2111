"""Stage 3 phase F: BM1 trunks redone (design session's decision after phase A's deviation). Usage: <KiCad python> phaseF.py <in> <out> [log.json]

Phase A ran both BM1 trunks between L1's pads at 1.2 mm because J5's pads blocked the east side. Here:
  J5 (payload wire pads) moves north in the east strip, (61.9, 18.6) -> (61.9, 10.6); the fiducial pair FID4 / FID2 moves out of
  its way, (62.6, 9.0) -> (62.6, 7.7).
  BM1_N  the frozen board's 2.0 mm path under L1, 1:1 as far as (52.231, 22.964), then 45 deg to x 54.125 and south to J10 pads 1-2.
  BM1_P  2.0 mm out of L1 pad 3 to the east, south at x 59.75 (0.2 mm off L1 pad 4), then 45 deg south-west between Sofar's GND
         polygon corner (58.43, 23.01) and the south-east screw keep-out (r 3.0 at (61.5, 26.5)): the gap is 1.65 mm, so the
         trunk necks to 1.4 mm there (centre line x + y = 82.67), then 2.0 mm again to J10 pads 3-4.
  The 0.2 mm link from Sofar's data-tap via (52.406, 18.614) to the trunk at L1 pad 3 stays as phase A drew it.
Removes only phase A's BM1 copper (checked against the board of commit d30920b, path in $S3_BASE).
"""
import sys, os, s3lib
T = 'Top Layer'
import shutil
if sys.argv[1] != sys.argv[2]: shutil.copy(sys.argv[1], sys.argv[2])
s3lib.prestep(sys.argv[2], os.environ['S3_BASE'], removes=[('BM1_N', T), ('BM1_P', T)], moves=[('J5', (61.9, 10.6)), ('FID4', (62.6, 7.7)), ('FID2', (62.6, 7.7))])
r = s3lib.Router(sys.argv[2], 'F')
K = 82.67                                   # neck centre line x + y = K
r.track('BM1_N', T, [(47.777, 17.699), (49.367, 17.699), (52.231, 20.564), (52.231, 22.964), (54.125, 24.858), (54.125, 33.9)], 2.0, clr=0.19, note='frozen path under L1')
r.track('BM1_P', T, [(56.286, 17.699), (58.75, 17.699), (59.75, 18.699), (59.75, 22.8)], 2.0, clr=0.2, note='east of L1')
r.track('BM1_P', T, [(59.75, 22.8), (59.75, K - 59.75), (57.82, K - 57.82)], 1.4, clr=0.15, note='neck past the SE screw keep-out')
r.track('BM1_P', T, [(57.82, K - 57.82), (56.625, K - 56.625), (56.625, 33.9)], 2.0, clr=0.2)
r.track('BM1_P', T, [(52.406, 18.614), (54.286, 18.614)], 0.2, note="data tap via to L1 pad 3 (as phase A)")
n = r.report_bad()
r.finish(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None); r.summary()
sys.exit(1 if n else 0)
