"""Step 6: refill all zones and save. Usage: <KiCad python> step6_fill.py <board in> <board out>"""
import sys
from s3lib import *
b = pcbnew.LoadBoard(sys.argv[1])
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
print('  refilled %d zones (%d of them rule areas)' % (len(b.Zones()), sum(1 for z in b.Zones() if z.GetIsRuleArea())))
pcbnew.SaveBoard(sys.argv[2], b); print('saved', sys.argv[2])
