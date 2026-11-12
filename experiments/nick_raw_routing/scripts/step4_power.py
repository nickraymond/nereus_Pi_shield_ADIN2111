"""Step 4 of the routing plan: power.

1. GND plane under the 5 V converter and the 5 V input. Sofar's GND plane has a notch in its north-west corner
   (x < 132.5 for y 88..95, narrowing to x < 125 at y 103): the mote's board ended there. U10, C54/C55 and J4 sit in
   that notch, so their GND vias reached no plane. A new GND zone on the GND Plane layer fills the notch from the
   west edge to Sofar's plane and joins the north strip. It stops at y 103.2, clear of the BM2_N bus trunk.
2. J4 pad 1 to F1 pad 2 (1.0 mm, top). J4 pad 2 (GND) is a through-hole pad inside the new zone.
3. J3 pin 1 (GND): one via into the new zone.
4. TP38 to the 5V_PI track; U11's exposed pad to the U11_RTN island.
5. PI_3V3: J1 pin 1 and pin 17 joined on Internal 2 along the header channel. J2 pins 9/11/13 get PI_3V3 from a
   new zone on the PWR Plane layer (x 143.9..167.2, y 76.6..86.8, with a tab to y 89.2 around the three pins).
   Its clearance is 0.25 mm, not 0.3: between two header pins that leaves a 0.34 mm web, where 0.3 leaves 0.24 mm
   and the plane cannot pass. The PI_5V pour gives up its east end (x 146.4 -> 143.65 beside J1 pin 17, 144.6
   beside J6).
6. VBUS_OUT to J5 pad 1: top from Sofar's via (135.13, 100.60) west to two new vias, then bottom along y 99.6
   and down the west edge (1.0 mm on the outer layers; D12 asks for 890 mA).
7. J5 pad 2 (GND): bottom, 1.0 mm, to two new vias into Sofar's GND plane at (125.7, 114.9 / 115.9).
New vias 0.6 / 0.3 mm.
"""
import sys
import pcbnew
import boardio
from boardio import add_track, add_via, pad_xy, via_xy, mm

MM = pcbnew.FromMM
b = boardio.load()
fp = boardio.footprints(b)
tracks = list(b.GetTracks())
zones = {z.GetZoneName(): z for z in b.Zones() if z.GetZoneName()}
if "GND north-west fill (5 V converter, J4, J3)" in zones:
    sys.exit("step 4 already applied (the north-west GND zone exists); nothing done")
strip = zones["GND north strip (Pi header)"]
pour5 = zones["PI_5V north pour"]

def new_zone(name, net, layer_name, pts, priority, like, clearance=None):
    z = pcbnew.ZONE(b)
    z.SetZoneName(name)
    z.SetNet(boardio.net_of(b, net))
    z.SetLayer(b.GetLayerID(layer_name))
    z.SetAssignedPriority(priority)
    z.SetLocalClearance(MM(clearance) if clearance else like.GetLocalClearance())
    z.SetMinThickness(like.GetMinThickness())
    z.SetPadConnection(like.GetPadConnection())
    z.SetThermalReliefGap(like.GetThermalReliefGap())
    z.SetThermalReliefSpokeWidth(like.GetThermalReliefSpokeWidth())
    z.SetIslandRemovalMode(like.GetIslandRemovalMode())
    o = z.Outline()
    o.NewOutline()
    for x, y in pts:
        o.Append(MM(x), MM(y))
    b.Add(z)
    return z

# ---- 1. GND plane fills the north-west notch
new_zone("GND north-west fill (5 V converter, J4, J3)", "GND", "GND Plane",
         [(116.8, 87.5), (132.9, 87.5), (132.9, 96.0), (129.9, 96.0), (129.9, 98.4), (126.8, 101.4), (125.4, 103.2), (116.8, 103.2)],
         2, strip)

L = {}
# ---- 2. J4 pad 1 to F1 pad 2
j4, f1 = pad_xy(b, "J4", "1"), pad_xy(b, "F1", "2")
L["J4-F1"] = add_track(b, "Net-(J4-Pin_1)", "Top Layer", [f1, (f1[0], 90.30), (120.20, 91.40), (120.20, j4[1])], 1.0)
# ---- 3. J3 pin 1 to GND
j3 = pad_xy(b, "J3", "1")
add_via(b, "GND", 124.30, 98.40)
L["GND"] = add_track(b, "GND", "Top Layer", [j3, (123.40, j3[1]), (123.40, 99.30), (124.30, 98.40)], 0.3)
# ---- 4. TP38, U11 exposed pad
tp = pad_xy(b, "TP38", "1")
L["5V_PI"] = add_track(b, "5V_PI", "Top Layer", [tp, (tp[0], 84.23)], 0.5)
ep = pad_xy(b, "U11", "11")
L["U11_RTN"] = add_track(b, "U11_RTN", "Top Layer", [ep, (ep[0], 96.40)], 0.3)   # into the island's filled body

# ---- 5. PI_3V3
p1, p17 = pad_xy(b, "J1", "1"), pad_xy(b, "J1", "17")
L["PI_3V3"] = add_track(b, "PI_3V3", "Internal 2", [(p17[0], 82.60), (p17[0] - 0.30, 82.90), (p1[0] + 2.03, 82.90), p1], 0.3)
o = pour5.Outline()
was = [(round(mm(o.CVertex(i).x), 2), round(mm(o.CVertex(i).y), 2)) for i in range(o.TotalVertices())]
assert was == [(116.8, 76.6), (146.4, 76.6), (146.4, 86.4), (123.2, 86.4), (123.2, 88.1), (121.9, 88.1), (121.9, 86.4), (116.8, 86.4)], was
o.RemoveAllContours()
o.NewOutline()
for x, y in [(116.8, 76.6), (143.65, 76.6), (143.65, 83.0), (144.6, 83.0), (144.6, 86.4)] + was[3:]:
    o.Append(MM(x), MM(y))
z33 = [z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == "3V3" and b.GetLayerName(z.GetFirstLayer()) == "PWR Plane"]
assert len(z33) == 1
new_zone("PI_3V3 north-east pour (J1 pin 17, J2 pins 9/11/13)", "PI_3V3", "PWR Plane",
         [(143.9, 76.6), (167.2, 76.6), (167.2, 89.2), (159.2, 89.2), (159.2, 86.8), (144.9, 86.8), (144.9, 82.75), (143.9, 82.75)],
         z33[0].GetAssignedPriority() + 2, pour5, clearance=0.25)

# ---- 6. VBUS_OUT to J5 pad 1
v_out = via_xy(tracks, "VBUS_OUT", (135.13, 100.60))
j5_1, j5_2 = pad_xy(b, "J5", "1"), pad_xy(b, "J5", "2")
add_via(b, "VBUS_OUT", 126.60, 100.60)
add_via(b, "VBUS_OUT", 127.60, 100.60)
L["VBUS_OUT"] = add_track(b, "VBUS_OUT", "Top Layer", [v_out, (126.60, v_out[1])], 1.0)
L["VBUS_OUT"] += add_track(b, "VBUS_OUT", "6 Bottom Layer",
                           [(127.60, 100.60), (126.60, 100.60), (125.60, 99.60), (120.30, 99.60), (120.30, j5_1[1] - 0.30)], 1.0)
# ---- 7. J5 pad 2 to GND
add_via(b, "GND", 125.70, 114.90)
add_via(b, "GND", 125.70, 115.90)
L["GND"] += add_track(b, "GND", "6 Bottom Layer",
                      [(j5_2[0] + 1.50, j5_2[1]), (122.20, j5_2[1]), (125.70, j5_2[1] - 3.50), (125.70, 114.90)], 1.0)

boardio.save(b)
for n, v in L.items():
    print("  %-10s %.2f mm added" % (n, v))
print("  zones added: GND north-west fill, PI_3V3 north-east pour; PI_5V pour east edge 146.4 -> 143.65; 5 vias added")
boardio.report(["J4", "J5", "J3", "TP38"])
