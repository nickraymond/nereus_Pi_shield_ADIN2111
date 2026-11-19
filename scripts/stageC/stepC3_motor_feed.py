"""Routing stage C, part 3: a heavier 5 V feed for the motor driver U12 (QE finding 6 of pull request 39; Nick, routing
session's chat, 2026-11-18: "I'd like to have a robust solution that allows for higher current draw since this is motor
and NPU processing", and "Yes, both" to the question "Put the heavier motor feed and the switch-node pour net on the
board?").

KiCad's Python: stepC3_motor_feed.py <board .kicad_pcb (a copy outside git)>
Frame: X' = KiCad x - 100, y = 100 - KiCad y (mm). Positions read from the board of commit 33a0f67 on 2026-11-18.
Before this step U12's 5 V came through one zone on the PWR plane (15.2 um copper): a band 2.0 mm wide and a tab
1.75 mm wide that necks to 1.55 mm beside C61's GND via at (0.85, 43.6).
1. The PWR-plane zone "N6 5V U12" (stage C part 2) is redrawn: its band is 3.5 mm (y 44.3..47.8) and reaches west over
   the wing to X' -6.1, so the vias of the bulk capacitors C62 / C66 / C60 feed it directly. Its uuid goes to
   <board>.removed for the lock check.
2. A second zone of the same net on Internal 1, "N6 5V U12 In1", priority 1 over the ground pour "N6 GND In1"
   (priority 0): the same band and tab, plus a column X' -6.1..-4.4 down to y 40.4 over the three vias of the bulk
   capacitors. The five existing 5 V vias tie the two layers together; no new via, no track changed.
Both zones: clearance 0.3 mm, minimum width 0.25 mm, solid connection, islands always removed."""
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); FM, mm = pcbnew.FromMM, pcbnew.ToMM
PWR, I1 = b.GetLayerID("PWR Plane"), b.GetLayerID("Internal 1")
def V(x, y): return pcbnew.VECTOR2I(FM(100 + x), FM(100 - y))
net = [n for name, n in b.GetNetsByName().items() if str(name).endswith("/5V_PI")]; assert len(net) == 1
# the five vias that tie the two layers: both must be 5V_PI and reach both inner layers
vias = {(round(mm(t.GetPosition().x) - 100, 3), round(100 - mm(t.GetPosition().y), 3)): t for t in b.GetTracks()
        if t.GetClass() == "PCB_VIA" and t.GetNetCode() == net[0].GetNetCode()}
for p in [(1.694, 43.55), (1.694, 44.25), (-5.2, 41.07), (-5.2, 43.78), (-5.2, 45.2)]:
    assert p in vias, ("no 5V_PI via at", p); assert vias[p].IsOnLayer(PWR) and vias[p].IsOnLayer(I1), p
old = [z for z in b.Zones() if z.GetZoneName() == "N6 5V U12"]; assert len(old) == 1 and old[0].IsOnLayer(PWR)
assert not [z for z in b.Zones() if z.GetZoneName() == "N6 5V U12 In1"]
open(sys.argv[1] + ".removed", "w").write(old[0].m_Uuid.AsString()); b.Remove(old[0])
g1 = [z for z in b.Zones() if z.GetZoneName() == "N6 GND In1"]; assert g1 and all(z.GetAssignedPriority() == 0 for z in g1)
def zone(name, layer, prio, pts):
    z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(net[0]); z.SetZoneName(name); z.SetAssignedPriority(prio)
    o = pcbnew.SHAPE_POLY_SET(); o.NewOutline()
    for p in pts: o.Append(V(*p))
    z.Outline().Append(o); z.SetLocalClearance(FM(0.3)); z.SetMinThickness(FM(0.25)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS); z.SetIsRuleArea(False); z.SetFillMode(pcbnew.ZONE_FILL_MODE_POLYGONS); b.Add(z)
zone("N6 5V U12", PWR, 3, [(-6.1, 47.8), (3.0, 47.8), (3.0, 42.3), (1.25, 42.3), (1.25, 44.3), (-1.2, 44.3), (-1.2, 42.6), (-2.7, 42.6), (-2.7, 44.3), (-6.1, 44.3)])
zone("N6 5V U12 In1", I1, 1, [(-6.1, 47.8), (3.0, 47.8), (3.0, 42.3), (1.25, 42.3), (1.25, 44.3), (-4.4, 44.3), (-4.4, 40.4), (-6.1, 40.4)])
pcbnew.SaveBoard(sys.argv[1], b); print("zone 'N6 5V U12' redrawn on the PWR plane; zone 'N6 5V U12 In1' added on Internal 1")
