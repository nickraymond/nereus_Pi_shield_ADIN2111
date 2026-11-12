"""Step 22: fiducials as JLC asks for them: 1 mm dots in 2 mm openings, 3.5 mm or more from the board edge
(review finding M-S3; Nick's comments on the summary doc, 2026-11-11: "is there a better place to put [fiducials]
or should we make them larger to aid in manufacturability? We have space, the mote did not", then on the proposal:
"approved make it happen").

FID1-FID6 were Sofar's 0.75 mm dots in 2.25 mm openings, three per side at the same three places, 1.65 / 3.55 /
2.65 mm from the edge. JLC's help page (read 2026-11-11 by the previous session) asks for 1 mm dots, 2 mm
openings and 3.35 mm from the edge.

- Each pad grows to 1.00 mm; its solder-mask margin goes from 0.75 to 0.50 mm (opening 2.00 mm). No paste, as before.
- New places, top and bottom dot of a pair on the same spot, found by searching for places where both sides are
  free (1.3 mm to copper, 1.2 mm to silkscreen and part outlines, 1.5 mm to holes, measured from the centre):
    south-west pair FID1 / FID3   (123.70, 128.60) -> (123.40, 127.90)   0.8 mm
    east pair       FID5 / FID6   (178.70, 122.00) -> (177.50, 122.90)   1.5 mm
    north-west pair FID2 / FID4   (117.90,  83.60) -> (125.90,  92.00)  11.6 mm
  Nothing nearer is free for the north-west pair: the 5V_PI track, JP1 and H1's keep-out fill the corner on top,
  the notes behind JP1 on the bottom. Its new place is the open spot between L6, the AUX OUT box and C55.
- No copper, part or text changes.
"""
import sys
import pcbnew
import boardio
from boardio import mm

MM = pcbnew.FromMM
DOT, MARGIN = 1.00, 0.50
MOVES = {"FID1": ((123.70, 128.60), (123.40, 127.90)), "FID3": ((123.70, 128.60), (123.40, 127.90)),
         "FID5": ((178.70, 122.00), (177.50, 122.90)), "FID6": ((178.70, 122.00), (177.50, 122.90)),
         "FID2": ((117.90, 83.60), (125.90, 92.00)), "FID4": ((117.90, 83.60), (125.90, 92.00))}

b = boardio.load()
fp = boardio.footprints(b)
pads = {r: fp[r].Pads()[0] for r in MOVES}
layer = lambda r: pcbnew.B_Cu if fp[r].IsFlipped() else pcbnew.F_Cu
if all(abs(mm(pads[r].GetSize(layer(r)).x) - DOT) < 0.001 for r in MOVES):
    sys.exit("step 22 already applied (the fiducials are 1 mm dots); nothing done")
at = lambda p: (round(mm(p.GetPosition().x), 2), round(mm(p.GetPosition().y), 2))
for r, (old, new) in MOVES.items():
    p = pads[r]
    assert len(fp[r].Pads()) == 1 and at(p) == (old[0], old[1]), (r, at(p))
    assert abs(mm(p.GetSize(layer(r)).x) - 0.75) < 0.001 and abs(mm(p.GetLocalSolderMaskMargin()) - 0.75) < 0.001, r
    assert p.GetShape(layer(r)) == pcbnew.PAD_SHAPE_CIRCLE, r
for r, (old, new) in MOVES.items():
    fp[r].Move(pcbnew.VECTOR2I(MM(new[0] - old[0]), MM(new[1] - old[1])))   # the pad is not at the footprint's origin
    p = pads[r]
    assert at(p) == (new[0], new[1]), (r, at(p))
    p.SetSize(layer(r), pcbnew.VECTOR2I(MM(DOT), MM(DOT)))
    p.SetLocalSolderMaskMargin(MM(MARGIN))
boardio.save(b)
print("  6 fiducials: dot 0.75 -> %.2f mm, mask opening 2.25 -> %.2f mm" % (DOT, DOT + 2 * MARGIN))
for r in sorted(MOVES):
    print("  %s %s -> %s" % (r, MOVES[r][0], MOVES[r][1]))
