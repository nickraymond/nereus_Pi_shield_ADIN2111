"""Step 15: R15 and R16 get Sofar's footprint back (review finding M-S5; Nick's comment in the summary doc,
2026-11-11: "lets put back the sofar footprint").

R15 (bottom) and R16 (top) are the mote's CRCW08057R50FKEAHP, in the mote's places with the mote's tracks, but
this board carried KiCad's stock `Resistor_SMD:R_0805_2012Metric` (pads 1.02 x 1.40 mm, pitch 1.82) where the
mote has `Vault:CRCW08057R50FKEAHP-Footprint-1` (pads 0.85 x 1.35 mm, pitch 1.65). The gap between the pads is
0.80 mm in both.

- Board: each footprint keeps its place, side, turn, designator text, fields and link to its symbol; its pads,
  graphics and 3D model are replaced by those of the library footprint in `mote.pretty` (the copy extracted
  from the mote board). Pad nets are kept. No track or via changes: the tracks are the mote's and end where
  the mote's pads are.
- Schematic (PoDL sheet): the Footprint field of R15 and R16 becomes `Vault:CRCW08057R50FKEAHP-Footprint-1`.
  Nothing else in the schematic changes.
"""
import os
import sys
import pcbnew
import boardio
from boardio import mm

LIB = os.path.join(os.path.dirname(os.path.abspath(boardio.BOARD)), "mote.pretty")
NAME = "CRCW08057R50FKEAHP-Footprint-1"
OLD_ID, NEW_ID = "Resistor_SMD:R_0805_2012Metric", "Vault:" + NAME
SCH = os.path.join(os.path.dirname(os.path.abspath(boardio.BOARD)), "BM_Mote_1_PoDL.kicad_sch")
FACE = "Menlo"
# pad centres on the mote board (KiCAD_reference_designs/20250409_BM_Mote_000639-AB), read with pcbnew
WANT = {"R15": {"1": (152.076, 99.304), "2": (150.426, 99.304)}, "R16": {"1": (150.901, 118.879), "2": (150.901, 120.529)}}

b = boardio.load()
fp = boardio.footprints(b)
ids = {r: fp[r].GetFPIDAsString() for r in WANT}
if all(i == NEW_ID for i in ids.values()):
    sys.exit("step 15 already applied (R15 and R16 carry Sofar's footprint); nothing done")
assert all(i == OLD_ID for i in ids.values()), ids
faces = open(boardio.BOARD).read().count('(face "%s")' % FACE)
sch = open(SCH, encoding="utf-8").read()
old_field = '(property "Footprint" "%s"' % OLD_ID
assert sch.count(old_field) == 2, sch.count(old_field)

dead = []
for ref in WANT:
    old = fp[ref]
    new = pcbnew.FootprintLoad(LIB, NAME)
    assert new is not None, LIB
    new.SetParent(b)
    new.SetPosition(old.GetPosition())
    if old.IsFlipped():
        new.Flip(new.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    for rot in (0, 90, 180, 270):
        new.SetOrientationDegrees(rot)
        got = {p.GetNumber(): (mm(p.GetPosition().x), mm(p.GetPosition().y)) for p in new.Pads()}
        if all(abs(got[n][0] - x) < 0.005 and abs(got[n][1] - y) < 0.005 for n, (x, y) in WANT[ref].items()):
            break
    else:
        raise AssertionError("%s: no turn puts Sofar's pads at %s (last tried %s)" % (ref, WANT[ref], got))
    assert abs(new.GetOrientationDegrees() - old.GetOrientationDegrees()) % 360 < 0.01, (ref, new.GetOrientationDegrees(), old.GetOrientationDegrees())
    nets = {p.GetNumber(): p.GetNet() for p in old.Pads()}
    dead += [(old, item) for item in list(old.Pads()) + list(old.GraphicalItems())]
    new_pads, new_gfx = list(new.Pads()), list(new.GraphicalItems())
    for p in new_pads:
        q = p.Duplicate().Cast()
        q.SetNet(nets[q.GetNumber()])
        old.Add(q)
    for g in new_gfx:
        old.Add(g.Duplicate().Cast())
    old.SetFPID(pcbnew.LIB_ID("Vault", NAME))
    old.Models().clear()
    for m in new.Models():
        old.Models().push_back(m)
    print("  %s: pads %s, nets %s" % (ref, {p.GetNumber(): (round(mm(p.GetPosition().x), 3), round(mm(p.GetPosition().y), 3)) for p in new_pads},
                                    {n: net.GetNetname().split("/")[-1] for n, net in nets.items()}))
# removals last: after a Remove, pcbnew's Python bindings can no longer list items
for old, item in dead:
    old.Remove(item)
boardio.save(b)
kept = open(boardio.BOARD).read().count('(face "%s")' % FACE)
assert kept == faces, (faces, kept)
open(SCH, "w", encoding="utf-8").write(sch.replace(old_field, '(property "Footprint" "%s"' % NEW_ID))
print("  R15 and R16: footprint %s -> %s on the board and in the PoDL sheet" % (OLD_ID, NEW_ID))
boardio.report(["R15", "R16"])
