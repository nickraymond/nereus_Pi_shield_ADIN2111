"""Step 24: final pass on the small designators (Nick, this session's chat, 2026-11-11: "as long as there are no
other technical changes please refine the placement of the small component silk screen"; earlier, on the summary
doc: "adjust the silkscreen so that they do not overlap and it's [clear] what they belong to").

- The designators in step24_designators.json move to the places found by step24_plan.py: free of pads, other
  silkscreen and fiducial openings, and nearer to their own part than to any other.
- NUDGE holds the small moves set by hand for texts the planner could not place by its box rules, each checked
  with DRC on a scratch copy.
- Silkscreen only: no copper, part or outline changes.
"""
import json
import os
import sys
import pcbnew
import boardio

FACE = "Menlo"
MM = pcbnew.FromMM
mm = pcbnew.ToMM
PLAN = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "step24_designators.json")))
# reference designators moved by hand: ref -> (dx, dy)
NUDGE = {"D8": (0.17, 0.0),    # to the middle of the 1.40 mm between D8's and D9's outlines
         "U2": (0.0, 0.06)}    # 0.13 mm under U2's corner marks
# board-level texts moved by hand: (layer name, text, x, y) -> (dx, dy)
TEXTS = {("Top Overlay", "VBUS OUT", 120.5, 117.5): (0.0, 0.12), ("Bottom Overlay", "VBUS OUT", 120.5, 117.5): (0.0, 0.12)}   # 0.14 mm under their box line

b = boardio.load()
fp = boardio.footprints(b)
box = lambda o: [round(mm(v), 2) for v in (o.GetBoundingBox().GetX(), o.GetBoundingBox().GetY(), o.GetBoundingBox().GetRight(), o.GetBoundingBox().GetBottom())]
first = sorted(PLAN)[0]
if box(fp[first].Reference()) != PLAN[first]["from_box"]:
    sys.exit("step 24 already applied (%s is not where the plan found it); nothing done" % first)
for ref, p in PLAN.items():
    assert box(fp[ref].Reference()) == p["from_box"], (ref, box(fp[ref].Reference()), p["from_box"])
at = lambda d: (b.GetLayerName(d.GetLayer()), d.GetText(), round(mm(d.GetPosition().x), 2), round(mm(d.GetPosition().y), 2))
texts = {at(d): d for d in b.GetDrawings() if d.GetClass() == "PCB_TEXT"}
assert all(k in texts for k in TEXTS), [k for k in TEXTS if k not in texts]
faces = open(boardio.BOARD).read().count('(face "%s")' % FACE)

for ref, p in PLAN.items():
    fp[ref].Reference().Move(pcbnew.VECTOR2I(MM(p["move"][0]), MM(p["move"][1])))
for ref, (dx, dy) in NUDGE.items():
    fp[ref].Reference().Move(pcbnew.VECTOR2I(MM(dx), MM(dy)))
for k, (dx, dy) in TEXTS.items():
    texts[k].Move(pcbnew.VECTOR2I(MM(dx), MM(dy)))

boardio.save(b)
kept = open(boardio.BOARD).read().count('(face "%s")' % FACE)
assert kept == faces, (faces, kept)
print("  %d designators moved by plan: %s" % (len(PLAN), ", ".join("%s (%+.2f, %+.2f)" % (r, PLAN[r]["move"][0], PLAN[r]["move"][1]) for r in sorted(PLAN))))
print("  %d designators and %d texts nudged by hand" % (len(NUDGE), len(TEXTS)))
