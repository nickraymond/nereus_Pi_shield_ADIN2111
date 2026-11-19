"""Routing stage C, part 4: the 3V3 converter's switch-node pour gets its net back (finding 1 of
docs/design-review/mote_diff_review_2026-11-18.md; Nick, routing session's chat, 2026-11-18: "Yes, both" to the
question "Put the heavier motor feed and the switch-node pour net on the board?").

KiCad's Python: stepC4_sw_pour_net.py <board .kicad_pcb (a copy outside git)>
The top-layer zone at KiCad x 115.26..122.51 (X' 15.26..22.51, y 30.46..33.88) is on net 3V3_Buck_SW on Sofar's mote
reference (U5 pin 2, L3 pad 1, C28 pad 1; 21.29 mm2 filled). On the starting board 325599c and until this step it had
no net and filled 3.63 mm2 of copper that touched nothing. This is one of Sofar's locked zones: only its net changes,
no corner and no setting; its uuid goes to <board>.removed so the lock check allows that one change."""
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); mm = pcbnew.ToMM
net = [n for name, n in b.GetNetsByName().items() if str(name).endswith("/3V3_Buck_SW")]; assert len(net) == 1
zs = [z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetCode() == 0 and z.IsOnLayer(b.GetLayerID("Top Layer"))]
assert len(zs) == 1, len(zs)
q = zs[0].Outline().BBox(); assert abs(mm(q.GetLeft()) - 115.26) < 0.02 and abs(mm(q.GetRight()) - 122.51) < 0.02, (mm(q.GetLeft()), mm(q.GetRight()))
open(sys.argv[1] + ".removed", "w").write(zs[0].m_Uuid.AsString()); zs[0].SetNet(net[0])
pcbnew.SaveBoard(sys.argv[1], b); print("zone net set to 3V3_Buck_SW")
