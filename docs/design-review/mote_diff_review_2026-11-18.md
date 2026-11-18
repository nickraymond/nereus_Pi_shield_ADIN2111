# Sofar's mote reference against today's N6 shield board (2026-11-18)

Asked for by Nick (routing session's chat, 2026-11-18) after the BM1_P repair: "that warrants a full review of the
diff from the reference mote design and the current design".

**Method.** `scripts/review2/motediff.py <mote reference> <starting board> <board to check>`, KiCad's Python. It
compares by geometry (ends, layer, width, pad boxes, zone corners), not by uuid, so it does not lean on the stage lock
checks. Net names differ between the Altium import and this project, so nets are compared through a map built from the
pads of the parts that are on both boards. Boards: REF = `KiCAD_reference_designs/20250409_BM_Mote_000639-AB` on
`development` (`23dae22`); START = `325599c` (the Pi Zero shield this branch started from); NOW = `197115e`.
Full output: `~/NereusData/nereus_Pi_shield_ADIN2111/n6_shield/review2/motediff_197115e.txt`.

## Result

| Sofar's mote has | Same on today's board | Not the same |
|---|---|---|
| 1907 tracks, 332 vias | 870 tracks, 185 vias (ends, layer, width, net) | 1037 tracks, 147 vias missing: **all already missing on START**, none changed |
| 16 zones, 154 rule areas | 15 zones, 154 rule areas (corners, layers, every setting) | 1 zone: finding 1 |
| 18 copper drawings | 17 | 1 (BM1_P polygon at L1): finding 2 |
| 167 footprints | 74 at the turned place with the same pads; T1, T2 in place with START's pads | 79 missing, 12 moved: all on START already, except C50, R11, R35, TP19, TP35 (removed in stage 0a, Nick's decision) |

**This branch changed none of Sofar's copper.** Every item of the mote that the starting board carried is on today's
board at the turned place with the same width, layer and net.

Of the missing copper, 659 items are on 33 nets that have no pad left (the mote's processor, USB, flash, debug). The
other 525 are on 22 nets that still have pads; joined into connected pieces, every piece touches only parts that were
removed or moved, except the bus copper to the connectors (the connectors moved), three GND pieces beside the removed
U7 / C49 / R34, and the items in findings 1 and 2.

Netlist among the 88 parts on both boards: 34 nets renamed only, 23 same name. Real differences, all intended and all
on START already except the first: R26.2 / R27.2 from 3V3 to N6_3V3 (stage 0, Nick's decision); J3's four pins re-used
(debug port to I2C0 and supply); R2.2 from GND to CFG1_STRAP; R9.2 from the old ADC net to ADIN_MISO.

## Findings

1. **Open, needs Nick's word (a locked item of Sofar's).** The 3V3 converter's switch node (U5 pin 2, L3 pad 1, C28
   pad 1) has a top-layer copper pour on the mote: 21.29 mm2 on net 3V3_Buck_SW. On START and today the same zone has
   **no net** and fills 3.63 mm2 of copper that touches nothing; the node is carried by its tracks alone (0.5 mm at
   each end, 1.0 mm between). It is one of the three `isolated_copper` warnings that were filed as "Sofar's no-net
   zones". Trial on a scratch copy (`trial_sw_zone/`): giving the zone its net back fills 21.35 mm2, errors unchanged,
   one warning fewer, lock / pour / plane / bus checks pass. Not changed on the board.
2. **Correction of the record.** The BM1_P track that stage 0c dropped and `d39a491` put back was not Sofar's. On the
   mote, his via at (20.057, 7.458) joins L1 pad 3 through a copper polygon and the 2.0 mm bus track; the Pi Zero work
   had replaced both by one 0.2 mm top track, and that is what came back. The line carries data from T1 pin 6 on
   Sofar's own 0.2 mm Internal 2 track, so 0.2 mm is no new neck.
3. **Why that track went, and what the checks did not cover.** Stage 0c removed all 747 tracks and vias of the Pi
   Zero work's own routing, by design (the board was placed anew). The lock checks protect copper that matches the
   mote reference; the Pi Zero work's copper inside the block was outside them. Stages A to G rebuilt every
   connection (0 unconnected, parity 0). DRC cannot show copper that was only extra (the Pi Zero board had 80 GND
   items of its own, for example); the per-net list is at the end of the output.
4. Sofar's zone fills are smaller where the new outline cuts the mote's box (GND plane 1211 to 1017 mm2, 3V3 on the
   PWR plane 475 to 362 mm2, P_IN 178 to 168 mm2). Every pad of these nets is connected (0 unconnected). The cause
   was not checked zone by zone.
5. This branch's own copper with an end inside the mote's outline box: 250 items on 35 nets (list in the output).
