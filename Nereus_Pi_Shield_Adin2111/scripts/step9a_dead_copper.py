"""Step 9a: remove dead copper left from the mote: track segments that end in the open and join nothing.

The list in step9a_dead_copper.json (net, layer, start, end; 58 segments, 46.8 mm) was found on a scratch copy:
run DRC, remove every track it reports as "Track has unconnected end", repeat until none is left (4 rounds).
All 58 led to parts the shield does not have (mezzanine connector, STM32). The open-connection count stayed 0
in every round. Vias are left alone.
"""
import json
import os
import sys
import pcbnew
import boardio
from boardio import mm

b = boardio.load()
tracks = [t for t in b.GetTracks() if t.Type() != pcbnew.PCB_VIA_T]
rows = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "step9a_dead_copper.json")))
left = list(tracks)
dead = []
for net, layer, x1, y1, x2, y2 in rows:
    for t in left:
        if (t.GetNetname() == net and b.GetLayerName(t.GetLayer()) == layer
                and abs(mm(t.GetStart().x) - x1) < 0.001 and abs(mm(t.GetStart().y) - y1) < 0.001
                and abs(mm(t.GetEnd().x) - x2) < 0.001 and abs(mm(t.GetEnd().y) - y2) < 0.001):
            dead.append(t)
            left.remove(t)
            break
if not dead:
    sys.exit("step 9a already applied (none of the listed segments is on the board); nothing done")
assert len(dead) == len(rows) == 58, (len(dead), len(rows))
total = sum(mm(t.GetLength()) for t in dead)
for t in dead:
    b.Remove(t)
boardio.save(b)
print("  removed %d dead segments, %.1f mm" % (len(dead), total))
