"""Stage 3 phase A: the four bus trunks, top layer. Usage: <KiCad python> phaseA.py <in board> <out board> [log.json]

Port 2 (J9, under L2): Sofar's / the frozen board's geometry.
  BM2_P  Sofar's 2.0 mm stub ends at (18.181, 22.339); from there the frozen board's diagonal to x 15.63 (it has to pass west of
         Sofar's GND via at (17.38, 25.69)), south, then back east under J9 pads 3-4.
  BM2_N  the frozen board's path west of L2: pad 2 -> (11.471, 17.224) -> (9.531, 19.164) -> south, then a diagonal parallel
         to BM2_P's (2.5 mm pitch) to J9 pads 1-2.
Port 1 (J10, under L1): both trunks pass between L1's pads at 1.2 mm (4.01 mm between the pads; 0.35 mm between the two
  trunks), not round the east: J5's pads now leave only 1.27 mm between L1 pad 4 and J5 pad 2, see the report.
  They widen to 2.0 mm for the run south to J10.
Each trunk ends at y 33.9 over its two ganged pads (pads y 33.255..34.955, pair 1.85 mm wide).
"""
import sys, s3lib
r = s3lib.Router(sys.argv[1], 'A'); T = 'Top Layer'
# --- port 2
r.track('BM2_P', T, [(18.181, 22.339), (15.63, 24.89), (15.63, 27.455), (17.475, 29.3), (17.475, 33.9)], 2.0, clr=0.2, note='from Sofar stub end; frozen diagonal 1:1')
r.track('BM2_N', T, [(13.955, 17.224), (11.471, 17.224), (9.531, 19.164), (9.531, 24.891), (14.975, 30.335), (14.975, 33.9)], 2.0, clr=0.2, note='frozen path west of L2 1:1 to y 24.9')
# --- port 1
r.track('BM1_N', T, [(47.777, 17.699), (49.299, 17.699), (51.65, 20.05), (51.65, 24.62), (54.125, 27.095), (54.125, 28.5)], 1.2, clr=0.2, note='between L1 pads, neck 1.2 mm')
r.track('BM1_N', T, [(54.125, 28.5), (54.125, 33.9)], 2.0, clr=0.2)
r.track('BM1_P', T, [(56.286, 17.699), (55.201, 17.699), (53.2, 19.7), (53.2, 23.95), (56.625, 27.375), (56.625, 28.5)], 1.2, clr=0.2, note='between L1 pads, neck 1.2 mm')
r.track('BM1_P', T, [(56.625, 28.5), (56.625, 33.9)], 2.0, clr=0.2)
r.track('BM1_P', T, [(52.406, 18.614), (54.286, 18.614)], 0.2, note="data tap via to the trunk (the frozen board's 0.2 mm link, shortened)")
n = r.report_bad()
r.finish(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None); r.summary()
sys.exit(1 if n else 0)
