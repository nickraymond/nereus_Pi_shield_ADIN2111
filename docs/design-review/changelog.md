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
