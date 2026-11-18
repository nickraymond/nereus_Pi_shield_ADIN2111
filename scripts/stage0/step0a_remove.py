#!/usr/bin/env python3
"""Stage 0, step 0a (STAGE0_PLAN.md): remove what goes. Schematic only.

Written new for the N6 shield; the method (box_delete of a drawing area with the expected parts asserted, exact
removal of titles) is that of `experiments/pi_zero_fit_01/scripts/stage2_schematic/step1_remove.py` on `development`.

Removed (Nick, first-pass session's chat, 2026-11-17, quoted in STAGE0_PLAN.md):
- VBUS-out switch: the whole "Load Switch" sub-sheet (U11, C59, R34, R36, R41, R42, D3, C49, and R35, C50, TP35,
  which the netlist places on that sheet) with its sheet symbol; on the Top-Level sheet R11, TP19 and the pads J5.
- 5 V jumper JP1, polyfuse F1, AUX pads J4.
- The Pi header J1 and the pad rows J15 to J19.
- R10, R24 (I2C3 pull-ups) and the I2C3 labels at the Qwiic connector J3.
Kept for step 0b: every label on the sub-sheet pins (ADIN_*, MOTOR_*, I2C0_*, ~{ADC_ALERT}), R26 / R27 with their
PI_3V3 symbols, the GND symbol with its PWR_FLAG below the old header (GND's only power flag on the schematic).
Sheet numbering: the pages after the removed sheet move up by one (PoDL 4, Power Monitor 5, Power 6, Motor + ADC 7).
"""
import re
from s0lib import (box_delete, cell_text, drop_lib_symbol, read, refs, remove_exact, remove_junction, remove_label, remove_wire,
                   replace_once, schedit, sheet_file, table_drop_rows, table_remove, wire, write)

t = read("top")
if "J1" not in refs(t):
    raise SystemExit("step 0a already applied")
used_before = set(re.findall(r'\(lib_id "([^"]+)"\)', t))

# --- the Pi header area. R26 / R27 stay: their wires are shortened to start at a label instead of at J1's pins
for y, name, lx in ((156.21, "I2C0_SDA", 223.52), (158.75, "I2C0_SCL", 222.25)):
    t = remove_wire(t, (217.17, y), (237.49, y))
    t = remove_label(t, "label", name, lx, y)
    t = wire(t, (229.87, y), (237.49, y))
    t = schedit.add_label(t, name, 229.87, y, 180)
# GND symbol #PWR66 and PWR_FLAG #FLG01 stay where they are, without J1's ground pin above them
t = remove_wire(t, (196.85, 212.09), (196.85, 217.17))
t = remove_junction(t, 196.85, 217.17)
t, rep = box_delete(t, (140.0, 105.0, 228.0, 214.0), ["J1", "JP1", "R10", "R24"])
print("  Pi header area:", rep)
assert rep["power"] == ["#FLG03", "#PWR012", "#PWR065", "#PWR087"], rep
assert rep["no_connects"] == 2 and "ADIN_TIMER" in rep["labels"] and "5V_LIFEPO4" in rep["labels"], rep
# the section title "RASPBERRY PI - 40-PIN HEADER" stays in place until step 0b renames it for the N6 headers

# --- pad rows J15 to J19
t, rep = box_delete(t, (30.0, 120.0, 110.0, 225.0), ["J15", "J16", "J17", "J18", "J19"])
print("  pad rows:", rep)
assert rep["power"] == ["#PWR118", "#PWR119", "#PWR120", "#PWR121"], rep

# --- VBUS-out switch on the Top-Level sheet: J5, R11, TP19, the sheet symbol, titles and notes
t, rep = box_delete(t, (25.0, 262.0, 160.0, 345.0), ["J5", "R11", "TP19"])
print("  payload switch area:", rep)
assert rep["power"] == ["#PWR02", "#PWR05", "#PWR81"] and rep["labels"] == ["PAYLOAD_EN", "~{PAYLOAD_FAULT}"], rep
sheets = [(s, e, b) for s, e, b in schedit.top_level(t, "sheet") if '(property "Sheetname" "Load Switch"' in b]
assert len(sheets) == 1 and "Nereus_Pi_Shield_Adin2111_LoadSwitch.kicad_sch" in sheets[0][2]
t = t[:sheets[0][0]] + t[sheets[0][1]:]
t = remove_exact(t, "text_box", '\t(text_box "LOAD SWITCH - PAYLOAD POWER"')
t = remove_exact(t, "text_box", '\t(text_box "R11 (0 Ω, DNP): bypass for payload switch U11')
t = remove_exact(t, "text", '\t(text "Payload power out: J5')

# --- AUX 5 V path: F1, J4
t, rep = box_delete(t, (250.0, 370.0, 290.0, 395.0), ["F1", "J4"])
print("  AUX 5 V area:", rep)
assert rep["power"] == ["#PWR091"] and rep["labels"] == ["5V_LIFEPO4"], rep
t = remove_exact(t, "text_box", '\t(text_box "POWER PATH FOR EXTERNAL SHIELD"')
t = table_remove(t, "Mode")      # the JP1 mode table

# --- I2C3 at the Qwiic connector J3 (pins 3 and 4 are re-used for the one bus in step 0b)
for name, y in (("I2C3_SDA", 382.27), ("I2C3_SCL", 379.73)):
    t = remove_label(t, "label", name, 367.03, y)
    t = remove_wire(t, (364.49, y), (367.03, y))

# --- page numbers of the sheets after the removed one
for name, old, new in (("PoDL", "5", "4"), ("Power Regulators", "7", "6"), ("Motor + ADC", "8", "7")):
    hit = [(s, e, b) for s, e, b in schedit.top_level(t, "sheet") if f'(property "Sheetname" "{name}"' in b]
    assert len(hit) == 1 and hit[0][2].count(f'(page "{old}")') == 1, name
    t = t[:hit[0][0]] + hit[0][2].replace(f'(page "{old}")', f'(page "{new}")') + t[hit[0][1]:]

left = refs(t)
for gone in ("J1", "J15", "J16", "J17", "J18", "J19", "JP1", "F1", "J4", "J5", "R11", "TP19", "R10", "R24"):
    assert gone not in left, gone
for keep in ("R26", "R27", "R43", "J3", "J9", "J10", "TP8", "TP38", "H1", "H2", "H3", "H4", "#PWR66", "#FLG01", "#FLG07"):
    assert keep in left, keep
for gone in ("PI_5V", "5V_LIFEPO4", "PAYLOAD_EN", "~{PAYLOAD_FAULT}", "I2C3_SDA", "I2C3_SCL", "GPIO7", "GPIO21"):
    assert f'(label "{gone}"' not in t, gone
# embedded library symbols that no part uses any more (KiCad drops them itself on its next save)
for lib_id in sorted(used_before - set(re.findall(r'\(lib_id "([^"]+)"\)', t))):
    t = drop_lib_symbol(t, lib_id)
    print("  embedded symbol dropped:", lib_id)
write("top", t)

# --- Power Monitor's page number, in the PoDL sheet's sheet symbol (nothing else in that file changes)
p = read("podl")
p = replace_once(p, '(page "6")', '(page "5")')
write("podl", p)

# --- the Load Switch sheet file
ls = read("load")
on_sheet = sorted(r for r in refs(ls) if not r.startswith("#"))
assert on_sheet == sorted("U11 C59 R34 R36 R41 R42 D3 C49 R35 C50 TP35".split()), on_sheet
sheet_file("load").unlink()
print("  Load Switch sheet removed with", " ".join(on_sheet))

# --- cover page: index, and the two specification rows of removed circuits
r = read("root")
r = cell_text(r, "1  Cover\\n2  Top-Level\\n3  ADIN2111 (Single-Pair Ethernet)\\n4  Load Switch (payload port)\\n5  PoDL (Power over Data Line)\\n"
                 "6  Bus Power Monitor\\n7  Power (buck converters)\\n8  Motor driver + ADC",
              "1  Cover\\n2  Top-Level\\n3  ADIN2111 (Single-Pair Ethernet)\\n4  PoDL (Power over Data Line)\\n"
              "5  Bus Power Monitor\\n6  Power (buck converters)\\n7  Motor driver + ADC")
r = table_drop_rows(r, "Description", ["VBUS OUT J5 (bus voltage, on with GPIO26)", "AUX 5 V J4 (5 V rail via JP1 2-3)"])
r = replace_once(r, "\\nVBUS OUT's 0.73 A limit (17.5 W at 24 V) is above that budget: it protects the port, it does not enforce the budget.", "")
write("root", r)
print("  cover page: index renumbered, rows VBUS OUT J5 and AUX 5 V J4 removed")
