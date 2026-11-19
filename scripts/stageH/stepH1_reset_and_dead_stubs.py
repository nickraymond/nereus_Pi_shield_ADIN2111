"""Stage H, part 1: the reset line's tap moved off the crystal, and Sofar's dead copper removed.
Nick, routing session's chat, 2026-11-18, on Sofar's leftovers (dangling tracks, no-net zones, his reset track under the
crystal): "yes remove them but you need to be careful, another session had to do this very carefully because deleteing
them all simply would have deleted good copper". QE round 3, finding R3-1.

KiCad's Python: stepH1_reset_and_dead_stubs.py <board .kicad_pcb (a copy outside git)>
Frame: X' = KiCad x - 100, y = 100 - KiCad y (mm). Positions read from the board of commit b5ec89f on 2026-11-18.

What was looked at first (n6_shield/trial_leftovers/dangle_analysis.txt: each flagged track walked from its open end
back to the first point where anything else of its net touches; padless_nets.txt: nets with copper and no pad):
STAYS
- 2 of the 9 `track_dangling` warnings are not dead: GND bottom at (27.532, 40.534) and VBUS bottom at
  (27.357, 30.033). Both ends lie in copper of their net, which has pads; only the end points miss each other.
- The 2 `isolated_copper` warnings are Sofar's named zones NoConnect_Left / NoConnect_Right on the PWR plane (73.6 and
  48.8 mm2, no net, priority 7), the same on the mote reference. They are meant to be there.
REMOVED
  1. ~ADIN_RST, Internal 1: Sofar's track from his corner (9.507, 17.404) under the crystal and on east to its open end
     at (27.557, 7.158): 11 segments, 23.95 mm. On the mote it went on to the processor.
  2. GND, bottom: from the via at (30.607, 36.133) east by (31.407, 36.133) and (31.707, 35.833) to the open end at
     (31.943, 35.597): 3 segments, 1.56 mm. It went to D3 pad 2 (part removed). The via and the track west of it stay.
  3. 3V3, top: (29.060, 37.501)-(30.184, 37.501), 1.12 mm; it went to R35 pad 2 (part removed in stage 0a).
  4. Net VBUS_OUT, all of it: 16 tracks (20.5 mm, 0.6 mm wide) and 4 vias. The net has NO pad: it was the output of the
     load switch U11, removed in stage 0 (STAGE0_PLAN.md: "remain on the board as copper of Sofar's with no pad").
  5. Net ~PAYLOAD_FAULT, all of it: 9 tracks (5.8 mm) and 2 vias. NO pad either (R35, TP35 and U11 are gone).
  The script refuses to run if either of those two nets has a pad or a zone, or another item count.
- This branch's reset tap of stage D part 2 ran from Sofar's corner (10.007, 15.633) south-west under Y1 and C8. It is
  removed with the east 1.52 mm of its y 13.02 run. New tap, Internal 1, 0.2 mm: from Sofar's corner (9.507, 17.404)
  west at y 17.404 (0.8 mm north of the crystal's box), 45 degrees south-west between the GND via at (7.257, 16.783)
  and C8, south at X' 6.75, 45 degrees into the old run at (5.87, 13.02). No via.
Uuids of everything removed go to <board>.removed for the lock check."""
import sys, math, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); FM, mm = pcbnew.FromMM, pcbnew.ToMM
def V(x, y): return pcbnew.VECTOR2I(FM(100 + x), FM(100 - y))
P = lambda v: (mm(v.x) - 100, 100 - mm(v.y))
def near(p, q): return math.hypot(p[0] - q[0], p[1] - q[1]) < 0.003
ALLT = list(b.GetTracks())   # one snapshot: the list is not read again after a Remove
ALL = [t for t in ALLT if t.GetClass() == "PCB_TRACK"]
rem, gone = [], []
def mark(t): assert t.m_Uuid.AsString() not in rem; rem.append(t.m_Uuid.AsString()); gone.append(t)
def take(netend, layer, a, c):
    L = b.GetLayerID(layer)
    hit = [t for t in ALL if t.GetLayer() == L and str(t.GetNetname()).endswith(netend)
           and ((near(P(t.GetStart()), a) and near(P(t.GetEnd()), c)) or (near(P(t.GetStart()), c) and near(P(t.GetEnd()), a)))]
    assert len(hit) == 1, (netend, layer, a, c, len(hit)); mark(hit[0])
RST = "~{ADIN_RST}"; I1 = "Internal 1"
# this branch's tap of stage D part 2
take(RST, I1, (10.007, 15.633), (7.394, 13.02)); take(RST, I1, (7.394, 13.02), (2.87, 13.02))
# 1. Sofar's reset track east of the new tap
ch = [(9.507, 17.404), (9.507, 16.133), (10.007, 15.633), (11.107, 15.633), (11.607, 16.133), (17.707, 16.133), (18.018, 15.822),
      (18.463, 15.377), (20.197, 15.377), (25.807, 9.766), (25.807, 8.908), (27.557, 7.158)]
for a, c in zip(ch, ch[1:]): take(RST, I1, a, c)
# 2. and 3. two short dead ends on nets that have pads
take("GND", "6 Bottom Layer", (30.607, 36.133), (31.407, 36.133)); take("GND", "6 Bottom Layer", (31.407, 36.133), (31.707, 35.833))
take("GND", "6 Bottom Layer", (31.707, 35.833), (31.943, 35.597)); take("3V3", "Top Layer", (29.060, 37.501), (30.184, 37.501))
# 4. and 5. the two nets without a pad
for name, ntr, nvia in (("VBUS_OUT", 16, 4), ("~{PAYLOAD_FAULT}", 9, 2)):
    nets = [x for nm, x in b.GetNetsByName().items() if str(nm).split("/")[-1] == name]; assert len(nets) == 1, name; nc = nets[0].GetNetCode()
    assert not [p for f in b.GetFootprints() for p in f.Pads() if p.GetNetCode() == nc], name + " has a pad"
    assert not [z for z in b.Zones() if z.GetNetCode() == nc], name + " has a zone"
    its = [t for t in ALLT if t.GetNetCode() == nc]
    assert (sum(1 for t in its if t.GetClass() == "PCB_TRACK"), sum(1 for t in its if t.GetClass() == "PCB_VIA")) == (ntr, nvia), name
    for t in its: mark(t)
open(sys.argv[1] + ".removed", "w").write(" ".join(rem))
# the new tap starts on the end of Sofar's segment that stays: (10.783, 18.681)-(9.507, 17.404)
n = [x for name, x in b.GetNetsByName().items() if str(name).endswith(RST)]; assert len(n) == 1
assert [t for t in ALL if t.m_Uuid.AsString() not in rem and str(t.GetNetname()).endswith(RST) and (near(P(t.GetEnd()), (9.507, 17.404)) or near(P(t.GetStart()), (9.507, 17.404)))], "Sofar's corner (9.507, 17.404) not found"
for t in gone: b.Remove(t)
pts = [(9.507, 17.404), (8.904, 17.404), (6.75, 15.25), (6.75, 13.9), (5.87, 13.02), (2.87, 13.02)]; tot = 0
for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
    dx, dy = abs(x1 - x0), abs(y1 - y0); assert dx < 1e-6 or dy < 1e-6 or abs(dx - dy) < 1e-3
    t = pcbnew.PCB_TRACK(b); t.SetStart(V(x0, y0)); t.SetEnd(V(x1, y1)); t.SetWidth(FM(0.2)); t.SetLayer(b.GetLayerID(I1)); t.SetNet(n[0]); b.Add(t); tot += math.hypot(x1 - x0, y1 - y0)
pcbnew.SaveBoard(sys.argv[1], b)
print("  removed %d items: 2 segments of this branch's reset tap; Sofar's: 11 of his reset track, 4 of two dead ends, 25 tracks and 6 vias of the two nets without a pad. New reset tap %.1f mm, 5 segments, no via" % (len(rem), tot))
