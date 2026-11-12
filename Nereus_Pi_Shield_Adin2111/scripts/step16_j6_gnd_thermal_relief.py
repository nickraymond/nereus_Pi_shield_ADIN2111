"""Step 16: thermal relief on J6's three GND pins (review finding M-S6; mocked on a scratch copy first; Nick's
comment on the proposal in the summary doc, 2026-11-11: "approved").

J6 (the 2 x 3 "PI 5V" header, soldered by hand) has its GND pins 2, 4, 6 at y 87.64, on the line where the zone
"GND north strip (Pi header)" (thermal relief) meets Sofar's GND zone (solid pad connection). Each pin had a
gap on its north side only and stood in solid copper on the other three.

- The three pads get the pad setting "thermal relief", which every zone then follows, so Sofar's zone is not
  edited. Spoke width and gap come from each zone's own thermal settings.
- No part, track or via changes. The zones are refilled by the DRC run that follows this script.
"""
import sys
import pcbnew
import boardio

b = boardio.load()
j6 = boardio.footprints(b)["J6"]
gnd = [p for p in j6.Pads() if p.GetNetname().split("/")[-1] == "GND"]
assert sorted(p.GetNumber() for p in gnd) == ["2", "4", "6"], [p.GetNumber() for p in gnd]
if all(p.GetLocalZoneConnection() == pcbnew.ZONE_CONNECTION_THERMAL for p in gnd):
    sys.exit("step 16 already applied (J6's GND pads are set to thermal relief); nothing done")
assert all(p.GetLocalZoneConnection() == pcbnew.ZONE_CONNECTION_INHERITED for p in gnd), [p.GetLocalZoneConnection() for p in gnd]
for p in gnd:
    p.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_THERMAL)
for z in b.Zones():
    if not z.GetIsRuleArea():
        z.SetNeedRefill(True)
boardio.save(b)
print("  J6 pads 2, 4, 6 (GND) set to thermal relief; refill follows with the DRC run")
