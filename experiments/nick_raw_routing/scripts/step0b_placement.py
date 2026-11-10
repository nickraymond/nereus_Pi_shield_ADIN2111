"""Step 0b: placement changes Nick asked for on 2026-11-10. No track or via is added or removed.

1. J6 one pitch west, to x 142.40, as on Nick's reload_old_mote (7cc5f04). The gap to J2 for the SPI nets
   grows from 3.7 mm to 6.2 mm.
2. FID1 and FID3 to (123.90, 128.60), as on Nick's reload_old_mote.
3. TP38 to (133.56, 82.65), above the 5V_PI track between J1 pins 7 and 9: J6's new west pad took its
   step 0 spot.
4. J5 is no longer a JST GH connector. It becomes two through-hole wire pads
   (nereus:WirePads_1x02_P3.81mm_Oval4.2x2.6mm_Drill1.3mm), pad 1 VBUS_OUT at (119.00, 120.20),
   pad 2 GND 3.81 mm south of it, long axis towards the west edge. The schematic symbol's footprint,
   value and BOM flags change in the same commit (Master sheet).
"""
import os
import sys
import pcbnew
import boardio
from boardio import move_to, pos

NAME = "WirePads_1x02_P3.81mm_Oval4.2x2.6mm_Drill1.3mm"
LIB = os.path.join(boardio.HERE, "..", "nereus.pretty")

b = boardio.load()
fp = boardio.footprints(b)
old = fp["J5"]
if old.GetFPID().GetLibItemName().wx_str() == NAME:
    sys.exit("step 0b already applied (J5 is the wire-pad footprint); nothing done")

assert pos(fp["J6"]) == (144.9411, 85.1036), pos(fp["J6"])
move_to(fp["J6"], 144.9411 - 2.54, 85.1036)
for r in ("FID1", "FID3"):
    move_to(fp[r], 123.90, 128.60)
move_to(fp["TP38"], 133.56, 82.65)

new = pcbnew.FootprintLoad(LIB, NAME)
assert new is not None
new.SetFPID(pcbnew.LIB_ID("nereus", NAME))
new.SetReference("J5")
new.SetValue("Wire pads")
new.SetPath(old.GetPath())
new.SetSheetname(old.GetSheetname())
new.SetSheetfile(old.GetSheetfile())
nets = {p.GetNumber(): p.GetNet() for p in old.Pads() if p.GetNumber() in ("1", "2")}
assert {n.GetNetname().split("/")[-1] for n in nets.values()} == {"VBUS_OUT", "GND"}
for p in new.Pads():
    p.SetNet(nets[p.GetNumber()])
# the symbol's fields, as on the Master sheet (the schematic-parity check compares them)
FIELDS = {
    "Description": "Payload power out: two through-hole wire pads (4.2 x 2.6 mm oval, 1.3 mm hole), leads soldered "
                   "directly, no connector. Pin 1 VBUS_OUT, pin 2 GND. Was JST SM02B-GHS-TB until 2026-11-10",
    "MANUFACTURER": "", "LCSC": "", "SOURCING": "No part: wire pads",
    "PLANNED MPN": "", "PLANNED MFR": "", "PLANNED LCSC": "", "PLANNED NOTE": "No part to buy",
}
for name, value in FIELDS.items():
    new.SetField(name, value)
for f in new.GetFields():
    if f.GetName() in FIELDS:
        f.SetVisible(False)
move_to(new, 119.00, 120.20)
b.Add(new)
b.Remove(old)

boardio.save(b)
boardio.report(["J5", "J6", "FID1", "FID3", "TP38"])
