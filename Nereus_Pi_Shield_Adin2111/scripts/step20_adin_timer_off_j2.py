"""Step 20: ADIN_TIMER leaves the breakout header; J2 pin 22 goes to ground (Nick's comments on the summary doc,
2026-11-11: "The Adin_timer pin should only go to the primary Pi Header, not the aux header with the I/O breakouts
since this is critical for Adin time alignment. That means another schematic change"; "Tie it to GND").

ADIN_TIMER was on J1 pin 36 (GPIO16), J2 pin 22 and R47. Its bottom track ran through J2 pin 22's pad.

Schematic (Master sheet): the global label ADIN_TIMER at J2 pin 22 is removed; pin 22's wire runs on to the GND
symbol #PWR085 of pin 18, which moves one grid step down to y 336.55 so that both pins end on it.

Board:
- J2 pad 22 takes the net GND. It stands in the zone "GND north strip (Pi header)" on the GND Plane, which joins
  it with thermal spokes at the refill, as J2's other ground pins.
- ADIN_TIMER's bottom track no longer touches the pad: from (174.72, 83.00) it goes on east to (176.19, 83.00),
  turns to (176.99, 83.80) and runs down the gap between pins 22 and 24 to join its old lane at (176.99, 86.37),
  0.32 mm from each pad. Three segments out (4.31 mm), three in (5.17 mm).
- The pin's name on the silkscreen, "TM" on both sides, becomes "GND".
The zones are refilled by the DRC run that follows this script (kicad-cli pcb drc --refill-zones --save-board).
"""
import os
import re
import sys
import pcbnew
import boardio
from boardio import add_track, mm

FACE = "Menlo"
SCH = os.path.join(os.path.dirname(os.path.abspath(boardio.BOARD)), "Nereus_Pi_Shield_Adin2111_TopLevel.kicad_sch")
OUT = [((175.72, 84.00), (174.72, 83.00)), ((176.99, 86.37), (175.72, 85.10)), ((175.72, 85.10), (175.72, 84.00))]
NEW = [(174.72, 83.00), (176.19, 83.00), (176.99, 83.80), (176.99, 86.37)]

b = boardio.load()
fp = boardio.footprints(b)
pad = [p for p in fp["J2"].Pads() if p.GetNumber() == "22"][0]
if pad.GetNetname().split("/")[-1] == "GND":
    sys.exit("step 20 already applied (J2 pad 22 is on GND); nothing done")
assert pad.GetNetname().split("/")[-1] == "ADIN_TIMER", pad.GetNetname()
assert abs(mm(pad.GetPosition().x) - 175.72) < 0.01 and abs(mm(pad.GetPosition().y) - 85.10) < 0.01

# ---- schematic first: if its text is not what this step was written against, nothing is touched
sch = open(SCH, encoding="utf-8").read()
label = re.search(r'\n\t\(global_label "ADIN_TIMER"\n\t\t\(shape input\)\n\t\t\(at 501\.65 336\.55 0\)\n.*?\n\t\)(?=\n\t\()', sch, re.S)
assert label and label.group(0).count("(global_label") == 1, "the ADIN_TIMER label at J2 pin 22 was not found"
W22 = "(xy 497.84 336.55) (xy 501.65 336.55)"
W18 = "(xy 520.7 331.47) (xy 520.7 334.01)"
assert sch.count(W22) == 1 and sch.count(W18) == 1, (sch.count(W22), sch.count(W18))
pwr = re.search(r'\n\t\(symbol\n\t\t\(lib_id "BM_Mote_000639-AB-altium-import:GND_POWER_GROUND"\)\n\t\t\(at 520\.7 334\.01 0\)\n.*?\n\t\)(?=\n\t\()', sch, re.S)
assert pwr and '(property "Reference" "#PWR085"' in pwr.group(0) and pwr.group(0).count("\n\t(symbol") == 1, "#PWR085 was not found at (520.7, 334.01)"
assert sch.count("ADIN_TIMER") == 2, sch.count("ADIN_TIMER")


def down(m):
    return "(at %s %s %s)" % (m.group(1), ("%.2f" % (float(m.group(2)) + 2.54)).rstrip("0").rstrip("."), m.group(3))


moved = re.sub(r"\(at ([\d.\-]+) ([\d.\-]+) (\d+)\)", down, pwr.group(0))
new = sch.replace(pwr.group(0), moved).replace(label.group(0), "")
new = new.replace(W22, "(xy 497.84 336.55) (xy 520.7 336.55)").replace(W18, "(xy 520.7 331.47) (xy 520.7 336.55)")
assert new.count("ADIN_TIMER") == 1 and new.count("(at 520.7 336.55 0)") >= 1 and new.count("(xy 520.7 336.55)") == 2

# ---- board
tracks = list(b.GetTracks())
bot = b.GetLayerID("6 Bottom Layer")
old = []
for a, c in OUT:
    hits = [t for t in tracks if t.Type() == pcbnew.PCB_TRACE_T and t.GetLayer() == bot and t.GetNetname().split("/")[-1] == "ADIN_TIMER"
            and {(round(mm(t.GetStart().x), 2), round(mm(t.GetStart().y), 2)), (round(mm(t.GetEnd().x), 2), round(mm(t.GetEnd().y), 2))} == {a, c}]
    assert len(hits) == 1, (a, c, len(hits))
    old.append(hits[0])
texts = [d for d in b.GetDrawings() if d.GetClass() == "PCB_TEXT" and d.GetText() == "TM"]
where = sorted((b.GetLayerName(d.GetLayer()), round(mm(d.GetPosition().x), 2), round(mm(d.GetPosition().y), 2)) for d in texts)
assert where == [("Bottom Overlay", 175.72, 83.4), ("Top Overlay", 175.72, 82.5)], where
faces = open(boardio.BOARD).read().count('(face "%s")' % FACE)

pad.SetNet(boardio.net_of(b, "GND"))
length = add_track(b, "ADIN_TIMER", "6 Bottom Layer", NEW, 0.2)
for d in texts:
    d.SetText("GND")
for t in old:
    b.Remove(t)

open(SCH, "w", encoding="utf-8").write(new)
boardio.save(b)
kept = open(boardio.BOARD).read().count('(face "%s")' % FACE)
assert kept == faces, (faces, kept)
print("  schematic: ADIN_TIMER label off J2 pin 22; pin 22 wired to #PWR085 (GND), moved to (520.7, 336.55)")
print("  board: J2 pad 22 on GND; ADIN_TIMER re-laid around the pad, %.2f mm in for 4.31 mm out; 'TM' -> 'GND' on both sides" % length)
