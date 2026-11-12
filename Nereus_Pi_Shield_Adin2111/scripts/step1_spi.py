"""Step 1 of the routing plan: the four ADIN SPI nets, J1 pin to Sofar's existing via, no new via.

Layers (stackup JLC06161H-3313): SCK and CS on Internal 2 (0.11 mm above the GND plane); MOSI and MISO on
Internal 1, the layer Sofar uses for these nets between the vias and U1. The GND plane lies between the two.
West to east the Pi pins are MOSI, MISO, SCK/CS and the vias are CS, SCK, MISO, MOSI, so on each layer the
two nets keep their order: CS drops between J1 pins 21 and 23 to come out west of SCK, and MOSI runs
between the two J1 rows to the same gap to come out east of MISO. All four pass J2 through its first two
pin gaps (x 151.59 and 154.13), one track per gap per layer. Tracks 0.2 mm.

Also in this step:
- the PI_3V3 branch on Internal 2 along y 89.5 (added 2026-11-09) is removed: it crossed the SCK and CS
  paths. J2 pins 9/11/13 get PI_3V3 back in step 4 (power).
- the dead top-layer stubs of CS, SCK and MOSI above their vias are removed; MISO's stub stays for R9.
- MOSI's via is removed: with its top stub gone, Sofar's track and the new one meet on Internal 1 at the
  same point, so the via would join nothing and only leave a stub in the line.
"""
import sys
import pcbnew
import boardio
from boardio import add_track, find_tracks, pad_xy, via_xy

b = boardio.load()
tracks = list(b.GetTracks())
if any(t.GetNetname().endswith("ADIN_SCK") and b.GetLayerName(t.GetLayer()) == "Internal 2" for t in tracks):
    sys.exit("step 1 already applied (ADIN_SCK has copper on Internal 2); nothing done")

P = 1.27                                   # half the 2.54 mm pin pitch: the middle of a pin gap
mosi, miso = pad_xy(b, "J1", "19"), pad_xy(b, "J1", "21")
sck, cs = pad_xy(b, "J1", "23"), pad_xy(b, "J1", "24")
v_cs = via_xy(tracks, "~{ADIN_CS}", (157.25, 101.85))
v_sck = via_xy(tracks, "ADIN_SCK", (157.75, 101.39))
v_miso = via_xy(tracks, "ADIN_MISO", (158.25, 101.85))
v_mosi = via_xy(tracks, "ADIN_MOSI", (158.74, 101.50))
j2 = pad_xy(b, "J2", "2")                  # J2's north-west pin
GAP1, GAP2 = j2[0] + P, j2[0] + 3 * P      # the first two pin gaps of J2: x 151.59 and 154.13
ROW_MID = (sck[1] + cs[1]) / 2             # y between the two J1 rows
J1_GAP = miso[0] + P                       # x between J1 pins 21 and 23
SOUTH = 89.00                              # y just below J2's south row

def to_via(x, y, via):
    """From (x, y) go south-east at 45 degrees to the via's x, then straight south into the via."""
    dx = via[0] - x
    return [(x, y), (via[0], y + dx), via]

branch = find_tracks(b, tracks, "PI_3V3", "Internal 2", (146.9, 87.5, 160.6, 89.6))
assert len(branch) == 2, len(branch)
stubs = [t for n in ("~{ADIN_CS}", "ADIN_SCK", "ADIN_MOSI") for t in find_tracks(b, tracks, n, "Top Layer", (157.0, 99.5, 159.0, 101.95))]
assert len(stubs) == 9, len(stubs)

L = {}
# Internal 2: CS (west) and SCK (east)
L["~{ADIN_CS}"] = add_track(b, "~{ADIN_CS}", "Internal 2",
    [cs, (J1_GAP, ROW_MID), (J1_GAP, 82.40), (GAP1, 82.40 + GAP1 - J1_GAP)] + to_via(GAP1, SOUTH, v_cs))
L["ADIN_SCK"] = add_track(b, "ADIN_SCK", "Internal 2",
    [sck, (sck[0], 82.30), (GAP2, 82.30 + GAP2 - sck[0])] + to_via(GAP2, SOUTH, v_sck))
# Internal 1: MISO (west) and MOSI (east)
L["ADIN_MISO"] = add_track(b, "ADIN_MISO", "Internal 1",
    [miso, (miso[0], 82.20), (GAP1, 82.20 + GAP1 - miso[0])] + to_via(GAP1, SOUTH, v_miso))
L["ADIN_MOSI"] = add_track(b, "ADIN_MOSI", "Internal 1",
    [mosi, (mosi[0] + P, ROW_MID), (J1_GAP, ROW_MID), (J1_GAP, 81.60), (GAP2, 81.60 + GAP2 - J1_GAP)] + to_via(GAP2, SOUTH, v_mosi))

mosi_via = [t for t in tracks if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname().endswith("ADIN_MOSI")
            and abs(boardio.mm(t.GetPosition().x) - v_mosi[0]) < 0.01 and abs(boardio.mm(t.GetPosition().y) - v_mosi[1]) < 0.01]
assert len(mosi_via) == 1
for t in branch + stubs + mosi_via:
    b.Remove(t)
boardio.save(b)
for n, v in L.items():
    print("  %-12s %.2f mm added" % (n, v))
print("  removed: %d PI_3V3 segments on Internal 2, %d top stub segments, %d via (MOSI)" % (len(branch), len(stubs), len(mosi_via)))
boardio.report([])
