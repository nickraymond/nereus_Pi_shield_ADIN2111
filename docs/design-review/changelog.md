# Schematic change log

*Every edit to the live schematic, newest sprint first. Part of the S6 design-review package.*

## S1 — Fix the Altium import (2026-10-05, branch `sprint/1-import-fix`)

### S1.1 Pins that sat mid-wire, now connected (21 locations)

Altium connects a pin that touches a wire anywhere along it; KiCad only
connects at wire ends, so the import left these pins unconnected. At each
location the wire was split at the pin end and a junction added
(`tools/midwire.py --fix`). Result: netcheck went from 39/53 matched with
14 opens to 53/53 matched with 0 opens and 0 shorts.

| Sheet | Location (mm) | Pins now connected |
|---|---|---|
| ADIN2111 | (124.46, 73.4822) | R1.1 |
| ADIN2111 | (215.9, 228.4222) | C13.1 |
| ADIN2111 | (226.06, 228.4222) | C14.1 |
| Load | (152.4, 134.4422) | C49.1 |
| Load | (261.62, 164.9222) | R33.1, TP34.1 |
| Load | (271.78, 134.4422) | C50.1 |
| Load | (279.4, 172.5422) | TP35.1, R35.1 |
| Load | (292.1, 134.4422) | D3.1 |
| Master | (124.46, 205.74) | TP36.1 |
| Master | (292.1, 119.38) | TP8.1 |
| Master | (304.8, 187.96) | TP22.1 |
| Master | (368.3, 185.42) | TP20.1 |
| Master | (378.46, 190.5) | TP21.1 |
| Master | (472.44, 104.14) | TP3.1 |
| Master | (472.44, 106.68) | TP5.1 |
| Master | (472.44, 121.92) | TP7.1 |
| Master | (472.44, 124.46) | TP13.1 |
| PoDL | (43.18, 63.3222) | D4.1 |
| PoDL | (43.18, 175.0822) | D5.1 |
| PowerMon | (177.8, 149.6822) | R8.2 |
| PowerMon | (177.8, 159.8422) | R8.1 |

**Why not the original junction fix?** `Archive/shield_junction_fix.zip`
marks the same 33 locations (these 21 plus 12 on parts S2 deletes) with
junctions only. It had never been applied to the live project. Tested one
junction at a time in KiCad 9.0.6, each one connects its pin but most also
disconnect a neighbouring pin on the same wire (e.g. the C49.1 junction drops
U9.1 off VBUS). Splitting the wire at the pin connects it with no side effects.

### S1.2 Orphan sheet files deleted

`BM_Mote_1_Processor.kicad_sch` and `BM_Mote_1_USB.kicad_sch` were not
referenced by any sheet or by the project file. Deleting them changed neither
the ERC counts nor the netlist.

### S1.3 Power symbols numbered

All 65 power symbols had the same reference, `#PWR?`, in both the
property and the instance record (the checklist's "65 duplicate references").
They are now `#PWR01`–`#PWR65` in hierarchy order (Master 01–17, Power 18–27,
ADIN2111 28–50, PoDL 51–57, PowerMon 58, Load 59–65). ERC counts and the
netlist are unchanged.

### S1.4 ADIN_VDDIO label — verified, not changed

The plain label `ADIN_VDDIO` on the ADIN2111 sheet sits on the C13/C14 wire,
and the netlist has one `ADIN_VDDIO` net holding U3.A1 (switch output),
U1.18/U1.46, the R1/R3/R5/R6 pull-ups, TP2, C13 and C14, matching the copper.
The checklist's goal (pull-ups powered from ADIN_VDDIO) is met, so the label
was left as it is.

### S1 result

| Check | Before S1 | After S1 |
|---|---|---|
| netcheck (excl. S2 deletions) | 39/53 matched, 14 opens | **53/53, 0 opens, 0 shorts** |
| Pins mid-wire (kept parts) | 21 | **0** |
| ERC errors / warnings | 90 / 578 | 65 / 590 |
| Unnumbered power symbols | 65 | 0 |
