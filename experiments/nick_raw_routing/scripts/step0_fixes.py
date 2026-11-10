"""Step 0 of the routing plan: fixes before any routing. No copper is added or removed.

1. The 44 circles and the caption text on Edge.Cuts (from the Pi outline import) go to User.Drawings.
   KiCad treated the circles as cut-outs at every J1 pin and at H1-H4.
2. MP1 trades places with MP2, and MP3 with MP4, so each insert pad's net matches the bus copper
   already at that spot (Nick, 2026-11-10: "use option 1").
3. MTG1-MTG4 (M3 holes from the mote, outside the outline) are removed. Their symbols are set to
   "not on board" in BM_Mote_1_Master.kicad_sch by hand, in the same commit.
4. J5 (payload out) moves onto the board at the west edge, opening west. FID1 and FID3 make room.
5. TP38 (5V_PI test point) moves onto the board beside C58.
6. The "GND north strip" zone gets priority 1; it overlapped the mote's GND plane at priority 0.
"""
import sys
import pcbnew
import boardio
from boardio import mm, move_to, pos

b = boardio.load()
fp = boardio.footprints(b)

if "MTG1" not in fp:
    sys.exit("step 0 already applied (MTG1 is gone); nothing done")

# 1. Edge.Cuts: keep the 4 lines and 4 arcs of the outline, move the rest
moved = 0
for d in list(b.GetDrawings()):
    if d.GetLayer() != pcbnew.Edge_Cuts:
        continue
    is_circle = d.Type() == pcbnew.PCB_SHAPE_T and d.GetShape() == pcbnew.SHAPE_T_CIRCLE
    is_text = d.Type() == pcbnew.PCB_TEXT_T
    if is_circle or is_text:
        d.SetLayer(pcbnew.Dwgs_User)
        moved += 1
assert moved == 45, moved
left = [d for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts]
assert len(left) == 8, len(left)

# 2. inserts: exchange positions within each pair (same part, same rotation)
for a, c in (("MP1", "MP2"), ("MP3", "MP4")):
    assert fp[a].GetOrientationDegrees() == fp[c].GetOrientationDegrees()
    pa, pc = pos(fp[a]), pos(fp[c])
    move_to(fp[a], *pc)
    move_to(fp[c], *pa)

# 3. MTG1-MTG4
for r in ("MTG1", "MTG2", "MTG3", "MTG4"):
    assert all(p.GetNetname().startswith("unconnected-") for p in fp[r].Pads()), r
    b.Remove(fp[r])

# 4. J5 to the west edge, same rotation (signal pads east, opening west); fiducials out of its way
assert fp["J5"].GetOrientationDegrees() == -90
move_to(fp["J5"], 119.50, 122.20)
for r in ("FID1", "FID3"):
    assert pos(fp[r]) == (117.9011, 124.1036), pos(fp[r])
    move_to(fp[r], 118.50, 112.00)

# 5. TP38 beside C58 (5V_PI)
move_to(fp["TP38"], 136.65, 84.85)

# 6. zone priority
strips = [z for z in b.Zones() if z.GetZoneName() == "GND north strip (Pi header)"]
assert len(strips) == 1
strips[0].SetAssignedPriority(1)

boardio.save(b)
b = boardio.load()
fp = boardio.footprints(b)
print("Edge.Cuts items:", sum(1 for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts))
for r in ("MP1", "MP2", "MP3", "MP4", "J5", "FID1", "FID3", "TP38"):
    print(" ", r, pos(fp[r]), [p.GetNetname().split("/")[-1] for p in fp[r].Pads() if p.GetNumber() == "1"][:1])
print("footprints:", len(fp))
