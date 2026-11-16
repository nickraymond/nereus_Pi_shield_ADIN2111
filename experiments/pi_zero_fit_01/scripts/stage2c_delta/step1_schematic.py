#!/usr/bin/env python3
"""Stage 2c, step 1: schematic changes (Nick, design session's chat, 2026-11-15). Only the Top-Level sheet is edited.

 1. R48 = 4.02 kOhm 1 %, RC0402FR-074K02L (Yageo RC0402FR-07 series, as R34 / R23 / R1 on this board), footprint of R34.
 2. Pot: R51 100 kOhm (RMCF0402FT100K, as R21 / R35 / R36) and C67 100 nF (CL05A104KA5NNNC), DNP, from POT_WIPER to GND.
 3. C62 = 22 uF 16 V 0805 (GRM21BR61C226ME44L, as C56 / C57), C66 = a second one in parallel.
    Vetted parts / footprints for the stage-2 passives: C61, C63, C65 -> CL05A104KA5NNNC; R49, R50 -> footprint and LCSC of R7 / R10 / R24.
 5. J4's Description follows its footprint.
MPN, manufacturer and LCSC numbers of the vetted parts are the ones in docs/design-review/bom.csv (read 2026-11-15).
"""
import re
from s2lib import (SHEET_PATH, fields_right, junction, note, pins, power, read_top, refs, schedit, set_props, wire, write_top)

t = read_top()
if "R51" in refs(t):
    raise SystemExit("step 1 already applied")

RC0402 = "Vault:FP-RC0402-0_4-IPC_C"      # R34 (RC0402FR-079K09L), R7 / R10 / R24 (RC0402JR-0710KL)
CL278 = "Vault:FP-CL278-IPC_C"            # C1, C3, C9-C15, C28, C53 (CL05A104KA5NNNC)
RMCF = "Vault:FP-RMCF0402-IPC_C"          # R21, R35-R37, R43 (RMCF0402FT100K)
C0805 = "Capacitor_SMD:C_0805_2012Metric"  # C56, C57 (GRM21BR61C226ME44L)
VET = "Vetted part and footprint of this board"


def clone(t, src, new, x, y):
    return schedit.clone_symbol(t, t, src, new, x, y, SHEET_PATH)


# --- 1. R48
t = set_props(t, "R48", {
    "Value": "4.02kΩ 1%", "Footprint": RC0402,
    "Description": "RES 4.02K OHM 1% 1/16W 0402 p/n RC0402FR-074K02L: MP6550 current limit 0.5 V / (100 µA/A x 4.02 kΩ) = 1.24 A",
    "PLANNED MPN": "RC0402FR-074K02L", "PLANNED MFR": "Yageo", "PLANNED LCSC": "",
    "PLANNED NOTE": "4.02 kΩ: Nick, 2026-11-15 (4.02 k, so we don't clip - it's transient). Yageo RC0402FR-07 series as R34 / R23 / R1, footprint of R34; this value is not in the BOM yet, LCSC number not looked up"})

# --- 3. bulk: C62 becomes one of two 22 uF 0805, C66 the other (left of C62 on the rail; the 5V_PI label moves to the new end)
BULK = {"Value": "22uF 16V", "Footprint": C0805,
        "Description": "Chip Capacitor, 22 uF, +/- 20%, 16 V, X5R, 0805 p/n GRM21BR61C226ME44L; bulk at MP6550 VIN, two in parallel (C62, C66) = 44 uF nominal",
        "PLANNED MPN": "GRM21BR61C226ME44L", "PLANNED MFR": "Murata", "PLANNED LCSC": "C86817",
        "PLANNED NOTE": VET + " (C56 / C57). Replaces the 47 uF 1206 placeholder (Nick, 2026-11-15: reuse vetted footprints)"}
t = set_props(t, "C62", BULK)
RAIL_Y, OLD_END, NEW_END, X66 = 307.34, 204.47, 186.69, 194.31
lab = [m for m in schedit.LABEL.finditer(t) if m.group(2) == "5V_PI" and (float(m.group(3)), float(m.group(4))) == (OLD_END, RAIL_Y)]
assert len(lab) == 1, lab
t = t[:lab[0].start()] + t[lab[0].end():]
assert not schedit.bbox_clear(t, 176.0, 300.0, OLD_END - 0.1, 325.0), "the place for C66 is not clear"
t = wire(t, (OLD_END, RAIL_Y), (X66, RAIL_Y), (NEW_END, RAIL_Y))
t = schedit.add_label(t, "5V_PI", NEW_END, RAIL_Y, 180)
t = clone(t, "C62", "C66", X66, RAIL_Y + 5.08)
c = pins(t, "C66")
assert c["1"] == (X66, RAIL_Y + 2.54), c
t = wire(t, (X66, RAIL_Y), c["1"])
t = junction(t, X66, RAIL_Y)
t = wire(t, c["2"], (X66, c["2"][1] + 2.54))
t = power(t, "GND", X66, c["2"][1] + 2.54)

# --- vetted 100 nF and 10 k
for ref in ("C61", "C63", "C65"):
    t = set_props(t, ref, {"Value": "100nF 25V", "Footprint": CL278,
                           "Description": "Cap Ceramic 100nF 25V X5R ±10% SMD 0402 p/n CL05A104KA5NNNC",
                           "PLANNED MPN": "CL05A104KA5NNNC", "PLANNED MFR": "Samsung", "PLANNED LCSC": "C100072",
                           "PLANNED NOTE": VET + " (C1, C3, C9-C15, C28, C53); was the Urchin's CC0402KRX5R9BB104 (50 V) on a hand-solder footprint"})
for ref in ("R49", "R50"):
    t = set_props(t, ref, {"Footprint": RC0402, "PLANNED MPN": "RC0402JR-0710KL", "PLANNED MFR": "Yageo", "PLANNED LCSC": "C60489",
                           "PLANNED NOTE": VET + " (R7, R10, R24); same part as on the Urchin board, footprint changed from the hand-solder one"})

# --- 2. pot pull-down and optional filter capacitor, right of J8
Y, XL, XR, XC = 309.88, 543.56, 546.1, 561.34
assert not schedit.bbox_clear(t, 529.0, 304.0, 592.0, 332.0), "the place for R51 / C67 is not clear"
t = clone(t, "R49", "R51", XR, Y + 2.54)
t = clone(t, "C65", "C67", XC, Y + 2.54)
r, c = pins(t, "R51"), pins(t, "C67")
assert r["1"] == (XR, Y) and c["1"] == (XC, Y), (r, c)
t = wire(t, (XL, Y), (XR, Y), (XC, Y))
t = schedit.add_label(t, "POT_WIPER", XL, Y, 180)
for ref, x, p in (("R51", XR, r), ("C67", XC, c)):
    t = wire(t, p["2"], (x, p["2"][1] + 2.54))
    t = power(t, "GND", x, p["2"][1] + 2.54)
    t = fields_right(t, ref, 2.54 if ref == "R51" else 3.81)
t = set_props(t, "R51", {
    "Value": "100kΩ 1%", "Footprint": RMCF,
    "Description": "100kΩ ±1% 0.063W 0402 p/n RMCF0402FT100K: pot wiper pull-down, holds AIN1 at 0 V in the pot's dead zone (wiper open)",
    "PLANNED MPN": "RMCF0402FT100K", "PLANNED MFR": "Stackpole", "PLANNED LCSC": "C7055151",
    "PLANNED NOTE": VET + " (R21, R35-R37, R43). Fix from the Urchin bring-up bench finding (about 30° dead zone, input floats); untested, Nick tests it"})
t = set_props(t, "C67", {
        "Description": "Cap Ceramic 100nF 25V X5R ±10% SMD 0402 p/n CL05A104KA5NNNC: optional filter on the pot wiper, NOT FITTED",
    "PLANNED NOTE": VET + " (C1, C3, C9-C15, C28, C53). DNP: optional, footprint only"})
# DNP attribute on C67
hit = [(s, e, b) for s, e, b in schedit.top_level(t, "symbol") if schedit.symbol_ref(b) == "C67"]
assert len(hit) == 1 and hit[0][2].count("(dnp no)") == 1
s, e, b = hit[0]
t = t[:s] + b.replace("(dnp no)", "(dnp yes)", 1) + t[e:]

# --- 5. J4's Description
old = "5 V in: two through-hole wire pads (4.2 x 2.6 mm oval, 1.3 mm hole)"      # J5 (payload) has the 4.2 x 2.6 pads and keeps its text
assert t.count(old) == 1
t = t.replace(old, "5 V in: two through-hole wire pads (2.2 x 3.3 mm oval, 1.1 mm hole, 3.2 mm pitch)")

# --- the sheet's own notes follow
for o, n in (
    ("limit = 0.5 V / (100 µA/A x R48) = 1.00 A; VISEN = 0.499 V/A (MP6550 Rev. 1.0, p. 11).",
     "limit = 0.5 V / (100 µA/A x 4.02 kΩ) = 1.24 A; VISEN = 0.402 V/A (MP6550 Rev. 1.0, p. 11)."),
    ("C62 = added bulk; C60, C61, C63, C64 as on the Urchin.",
     "C62 + C66 = added bulk, 2 x 22 µF (C56's part); C60, C64 as on the Urchin; C61, C63 = this board's 100 nF."),
    ("AIN0 = MP6550 VISEN (499 mV/A with R48 4.99k)", "AIN0 = MP6550 VISEN (402 mV/A with R48 4.02k)"),
):
    assert t.count(o) == 1, o
    t = t.replace(o, n)
t = note(t, "R51 holds AIN1 at 0 V where the pot's\\nwiper is open (dead zone, about 30°).\\nC67: optional filter, not fitted. Untested.", 529.59, 327.66)
write_top(t)
print("  R48 4.02k; C62 -> 22uF 0805 + C66; C61 / C63 / C65 and R49 / R50 on vetted footprints; R51 + C67 (DNP) on POT_WIPER; J4 description; notes")
