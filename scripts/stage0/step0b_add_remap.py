#!/usr/bin/env python3
"""Stage 0, step 0b (STAGE0_PLAN.md): add the N6 headers and re-map. Schematic only. Runs after step0a_remove.py.

Written new for the N6 shield; the method (parts copied from existing parts of this schematic with every field,
label stubs, power symbols by copy, asserts on pin positions) is that of step3_motor.py / step4_adc.py in
`experiments/pi_zero_fit_01/scripts/stage2_schematic/` on `development`.

What it does:
- PI_3V3 becomes N6_3V3 (power symbol nereus:N6_3V3, added to nereus.kicad_sym as a renamed copy of PI_3V3).
- J21 (west, N6 J3) and J22 (east, N6 J2): Connector_Generic:Conn_02x08_Odd_Even, footprint
  Connector_PinHeader_2.54mm:PinHeader_2x08_P2.54mm_Vertical; pin numbers per n6_pinmap.py; fifteen no-connect flags.
- 5 V: the N6's VIN pin (J21 pin 14) sits on U10's output net 5V_PI. With JP1 gone there is one 5 V net and its name
  stays 5V_PI (hierarchical pins of the Power and Motor + ADC sheets unchanged); the name PI_5V is gone.
- SPI: R53 (MOSI), R54 (MISO), R55 (SCK), R56 (CS), 33 ohm 0402 (UNI-ROYAL 0402WGF330JTCE, LCSC C25105, fields laid
  out as R38's), between the header-side nets N6_MOSI / N6_MISO / N6_SCK / ~{N6_CS} and the existing nets ADIN_MOSI /
  ADIN_MISO / ADIN_SCK / ~{ADIN_CS}. R52, 10 k (copy of R7: RC0402JR-0710KL), pulls ~{ADIN_CS} up to ADIN_VDDIO on
  the ADIN side of R56. R9's strap tap stays on ADIN_MISO, on the ADIN side of R54 (Sofar's ADIN sheet is untouched).
- I2C: one bus, I2C0_SCL / I2C0_SDA on P4 / P5; Qwiic J3 pins 3 / 4 on it; R26 / R27 on N6_3V3.
- ~{ADC_ALERT}: no header pin; R49 stays, the net ends on test point TP44 (Motor + ADC sheet); the hierarchical pin
  goes. ADIN_TIMER: ends at R47 and test point TP45 (Top-Level sheet, by the existing global label name).
- ADC and pot supply: J8 pin 1, U13 VDD with C65, R49 from 3V3 to N6_3V3; C68 1 uF (copy of C2: CL05A105KP5NNNC).
- Connectors J7, J9, J10, J8, J3: top-entry footprints and part numbers (TOP_ENTRY_VARIANT.md on `development`).
- Mounting holes: H4 removed (three bare holes H1 to H3).
- Notes and titles that named the Pi are corrected where they would now be wrong.
"""
import re
from n6_pinmap import HEADERS
from s0lib import (_set_prop_at, KICAD_SYMBOLS, MOTOR_PATH, PROJECT_DIR, TOP_PATH, block_of, blocks, cell_text, clone_part, connector,
                   drop_lib_symbol, get_props, global_label, junction, note, pins, power, read, refs, remove_label,
                   remove_wire, replace_once, schedit, set_props, stub_label, swap_power_symbol, table_drop_rows, wire,
                   write)

t = read("top")
if "J1" in refs(t):
    raise SystemExit("run step0a_remove.py first")
if "J21" in refs(t):
    raise SystemExit("step 0b already applied")
m = read("motor")
adin, power_sheet, pmon = read("adin"), read("power"), read("pmon")      # read only: sources of parts to copy

# ---------------------------------------------------------------- 1. N6_3V3 power symbol
libfile = PROJECT_DIR / "nereus.kicad_sym"
lib = libfile.read_text(encoding="utf-8")
if '(symbol "N6_3V3"' not in lib:
    i = lib.index('\t(symbol "PI_3V3"\n')
    sym = lib[i:lib.index("\n\t)\n", i) + 4]
    assert sym.count("PI_3V3") == 4, sym.count("PI_3V3")      # symbol name, unit name, Value, pin name
    new = sym.replace("PI_3V3", "N6_3V3").replace("global label with name '3V3'", "global label with name 'N6_3V3'")
    lib = lib[:i] + new + lib[i:]
    assert lib.count("(") == lib.count(")")
    libfile.write_text(lib, encoding="utf-8")
    print("  nereus.kicad_sym: N6_3V3 added (PI_3V3 left in the library, no sheet uses it any more)")
t = schedit.ensure_lib_symbol(t, "nereus:N6_3V3", libfile)
m = schedit.ensure_lib_symbol(m, "nereus:N6_3V3", libfile)
for ref in ("#PWR077", "#PWR078", "#PWR013", "#PWR088"):       # R27, R26, Qwiic J3 pin 2, the PWR_FLAG row
    t = swap_power_symbol(t, ref, "nereus:PI_3V3", "nereus:N6_3V3", "N6_3V3")
t = drop_lib_symbol(t, "nereus:PI_3V3")

# ---------------------------------------------------------------- 2. the N6 headers
t = schedit.ensure_lib_symbol(t, "Connector_Generic:Conn_02x08_Odd_Even", KICAD_SYMBOLS / "Connector_Generic.kicad_sym")
FP = "Connector_PinHeader_2.54mm:PinHeader_2x08_P2.54mm_Vertical"
NOTE = ("Header part not chosen (STAGE0_PLAN.md decision 6). Footprint on the N6-facing side, flipped, pad 1 at the "
        "camera end, placed as header() in scripts/n6_rough_board.py; pin numbers per scripts/stage0/n6_pinmap.py")
HX = 175.26
for ref, y0, value, func in (("J21", 140.97, "N6 J3 (right), 2x8", "West header = the N6's right header J3"),
                             ("J22", 180.34, "N6 J2 (left), 2x8", "East header = the N6's left header J2")):
    t = connector(t, "Connector_Generic:Conn_02x08_Odd_Even", ref, value, FP, HX, y0, TOP_PATH,
                  {"FUNCTION": func, "PLANNED MPN": "", "PLANNED LCSC": "", "PLANNED NOTE": NOTE})
    p = pins(t, ref)
    assert p["1"] == (round(HX - 5.08, 4), round(y0 - 7.62, 4)) and p["16"] == (round(HX + 7.62, 4), round(y0 + 10.16, 4)), p
    ncs = 0
    for num, (sig, net) in sorted(HEADERS[ref].items()):
        x, y = p[str(num)]
        left = num % 2 == 1
        d = -1 if left else 1
        just = "right bottom" if left else "left bottom"
        if net is None:
            t = schedit.add_no_connect(t, x, y)
            t = note(t, sig, x + d * 1.6, y + 0.5, 1.0, just)
            ncs += 1
            continue
        t = note(t, sig, x + d * 0.8, y - 0.4, 1.0, just)
        if net == "GND":
            assert not left
            t = wire(t, (x, y), (x + 10.16, y), (x + 10.16, y + 2.54))
            t = power(t, "#PWR01", x + 10.16, y + 2.54, TOP_PATH)
        elif net == "N6_3V3":
            assert left
            t = wire(t, (x, y), (x - 10.16, y))
            t = power(t, "#PWR088", x - 10.16, y, TOP_PATH, rot=270, value_at=(-3.81, 0, 90, "right"))
        else:
            t = stub_label(t, (x, y), net, d * 10.16)
    print(f"  {ref}: {16 - ncs} pins wired, {ncs} no-connect flags")
t = cell_text(t, "RASPBERRY PI - 40-PIN HEADER", "OPENMV N6 - HEADERS J21 / J22")
t = note(t, "J21 = west header (the N6's right header J3), J22 = east header (the N6's left header J2). Small text = the N6's pin name.\\n"
            "Footprints on the N6-facing side (flipped), pad 1 at the camera end, odd pads on the east column of each header:\\n"
            "as header() in scripts/n6_rough_board.py (mock P). Pin numbers: scripts/stage0/n6_pinmap.py.", 149.86, 114.3)

# ---------------------------------------------------------------- 3. SPI series resistors and the CS pull-up
R38_FIELDS = get_props(power_sheet, "R38")
assert R38_FIELDS["Value"] == "0402WGF1332TCE" and R38_FIELDS["PLANNED MFR"] == "UNI-ROYAL", R38_FIELDS
SX1, SX2 = 309.88, 292.1          # pin 1 (ADIN side, right) and pin 2 (N6 side, left) of a resistor turned to lie flat
for ref, y, n6, adin_net in (("R53", 162.56, "N6_MOSI", "ADIN_MOSI"), ("R54", 172.72, "N6_MISO", "ADIN_MISO"),
                             ("R55", 182.88, "N6_SCK", "ADIN_SCK"), ("R56", 193.04, "~{N6_CS}", "~{ADIN_CS}")):
    t = clone_part(t, power_sheet, "R38", ref, SX1, y, TOP_PATH, rot=270,
                   shown={"Reference": (-9.144, -2.794, 90, None), "RESISTANCE": (-8.89, 3.048, 90, None)})
    p = pins(t, ref)
    assert p == {"1": (SX1, y), "2": (SX2, y)}, (ref, p)
    t = set_props(t, ref, {
        "Value": "0402WGF330JTCE", "Description": "RES 33 OHM 1% 1/16W 0402", "RESISTANCE": "33R",
        "PLANNED MPN": "0402WGF330JTCE", "PLANNED LCSC": "C25105", "SHEET": "TopLevel",
        "PLANNED NOTE": "SPI series resistor, 33 ohm 1 % 0402; JLC basic part proposed in STAGE0_PLAN.md decision 3 "
                        "(jlcpcb.com/partdetail/C25105, read 2026-11-17); field layout copied from R38 (same maker and series)",
        "SOURCING": "JLC basic part; the page showed no stock figure (STAGE0_PLAN.md, read 2026-11-17)"})
    t = stub_label(t, p["2"], n6, -2.54)
    if ref != "R56":
        t = stub_label(t, p["1"], adin_net, 2.54)
# CS: the ADIN-side wire runs on to the pull-up R52 (to ADIN_VDDIO), so the pull-up is on the ADIN side of R56
PX, PY = 330.2, 175.26
t = wire(t, (SX1, 193.04), (PX, 193.04))
t = schedit.add_label(t, "~{ADIN_CS}", SX1 + 2.54, 193.04, 0)
t = clone_part(t, pmon, "R7", "R52", PX, PY, TOP_PATH)
assert pins(t, "R52") == {"1": (PX, PY), "2": (PX, 193.04)}, pins(t, "R52")
assert get_props(t, "R52")["Value"] == "RC0402JR-0710KL" and get_props(t, "R52")["PLANNED LCSC"] == "C60489"
t = set_props(t, "R52", {"SHEET": "TopLevel",
                         "PLANNED NOTE": "CS pull-up to ADIN_VDDIO, on the ADIN side of R56; same part as R7 / R49 (fields copied from R7)"})
t = power(t, "#PWR048", PX, PY, TOP_PATH, src=adin)
t = note(t, "SPI: 33 Ω in series at the N6 end (N6 side left, ADIN side right).\\nR52 pulls CS up to ADIN_VDDIO on the ADIN side of R56.", 265.43, 200.66)

# ---------------------------------------------------------------- 4. ADIN_TIMER: ends at R47 and a test point
TX, TY = 292.1, 142.24
t = clone_part(t, t, "TP22", "TP45", TX, TY, TOP_PATH)
assert pins(t, "TP45") == {"1": (TX, 144.78)}, pins(t, "TP45")
t = wire(t, (TX, 144.78), (TX, 146.05), (TX - 2.54, 146.05))
t = global_label(t, "ADIN_TIMER", TX - 2.54, 146.05, 180)

# ---------------------------------------------------------------- 5. Qwiic J3 on the one I2C bus; connector parts
j3 = pins(t, "J3")
assert j3 == {"1": (364.49, 387.35), "2": (364.49, 384.81), "3": (364.49, 382.27), "4": (364.49, 379.73)}, j3
t = stub_label(t, j3["3"], "I2C0_SDA", 2.54)
t = stub_label(t, j3["4"], "I2C0_SCL", 2.54)
t = cell_text(t, "Qwiic CONNECTOR\\nI2C3 SOFTWARE EMULATION\\n", "Qwiic CONNECTOR\\nI2C0 (N6 P4 / P5)\\n")
SRC = "TOP_ENTRY_VARIANT.md on development: read on jlcpcb.com 2026-11-17, pages showed In Stock"
GH4 = {"Value": "BM04B-GHS-TBT(LF)(SN)", "Footprint": "Connector_JST:JST_GH_BM04B-GHS-TBT_1x04-1MP_P1.25mm_Vertical",
       "Description": "CONN HEADER SMD TOP ENTRY 4POS 1.25MM", "PLANNED MPN": "BM04B-GHS-TBT(LF)(SN)", "PLANNED LCSC": "C161692",
       "PLANNED NOTE": "Top-entry JST GH; pin order unchanged. Part and LCSC number: " + SRC, "SOURCING": "JLC (" + SRC + ")"}
for ref in ("J9", "J10"):
    assert get_props(t, ref)["PLANNED MPN"] == "SM04B-GHS-TB", ref
    t = set_props(t, ref, GH4)
assert get_props(t, "J3")["PLANNED MPN"] == "SM04B-SRSS-TB(LF)(SN)"
t = set_props(t, "J3", {"Value": "BM04B-SRSS-TB(LF)(SN)", "Footprint": "Connector_JST:JST_SH_BM04B-SRSS-TB_1x04-1MP_P1.00mm_Vertical",
                        "PLANNED MPN": "BM04B-SRSS-TB(LF)(SN)", "PLANNED LCSC": "C160390",
                        "PLANNED NOTE": "Qwiic connector on the one I2C bus (I2C0), top entry. Part and LCSC number: " + SRC,
                        "SOURCING": "JLC (" + SRC + ")"})
t = replace_once(t, "Bristlemouth bus: JST GH 4-pin, side entry,", "Bristlemouth bus: JST GH 4-pin, top entry,")

# ---------------------------------------------------------------- 6. ~{ADC_ALERT} leaves the Top-Level sheet
t = remove_label(t, "label", "~{ADC_ALERT}", 223.52, 306.07)
t = remove_wire(t, (223.52, 306.07), (241.3, 306.07))
i = t.index('\t\t(pin "~{ADC_ALERT}" passive\n')
j = t.index("\n\t\t)\n", i) + 5
assert "(at 241.3 306.07 180)" in t[i:j] and t[i:j].count("(pin ") == 1
t = t[:i] + t[j:]

# ---------------------------------------------------------------- 7. three mounting holes
h4 = block_of(t, "H4")
assert "MountingHole_2.7mm_M2.5" in h4 and "(pin " not in h4
t = t.replace(h4, "", 1)
assert {"H1", "H2", "H3"} <= refs(t) and "H4" not in refs(t)

# ---------------------------------------------------------------- 8. the I2C table on the Top-Level sheet
t = table_drop_rows(t, "Bus", ["I2C1", "I2C3 (sw)", ""])      # the Pi's I2C1, the software bus, and the empty row
t = cell_text(t, "GPIO0 / 1", "N6 P4 SCL / P5 SDA")
t = cell_text(t, "R26/R27 4.7k to PI_3V3", "R26/R27 4.7k to N6_3V3")
t = cell_text(t, "Keep 0x50 free (HAT EEPROM probe at boot)", "The N6's I2C2, the only bus; Qwiic J3 is on it")
assert "PI_3V3" not in t and "I2C3" not in t and "GPIO" not in t, "a Pi name is left on the Top-Level sheet"
write("top", t)

# ================================================================ Motor + ADC sheet
# supply of U13 (with C65), R49 and J8 pin 1: the mote's 3V3 -> N6_3V3
want = {"#PWR108": (79.58, 187.18), "#PWR111": (99.9, 189.72), "#PWR113": (138.0, 197.34)}
on_3v3 = {schedit.symbol_ref(b) for _, _, b in schedit.top_level(m, "symbol") if '(lib_id "BM_Mote_000639-AB-altium-import:3V3_BAR")' in b}
assert on_3v3 == set(want), on_3v3
for ref, at in want.items():
    assert pins(m, ref)[""] == at, (ref, pins(m, ref))
    m = swap_power_symbol(m, ref, "BM_Mote_000639-AB-altium-import:3V3_BAR", "nereus:N6_3V3", "N6_3V3")
m = drop_lib_symbol(m, "BM_Mote_000639-AB-altium-import:3V3_BAR")
u13, c65, r49, j8 = pins(m, "U13"), pins(m, "C65"), pins(m, "R49"), pins(m, "J8")
assert u13["8"] == (79.58, 192.26) and c65["1"] == (46.56, 189.72) and r49["1"] == (99.9, 192.26) and j8["1"] == (145.62, 199.88)
# C68, 1 uF, on the same supply wire as C65, to GND
CX = 31.32
m = wire(m, (46.56, 189.72), (CX, 189.72))
m = junction(m, 46.56, 189.72)
m = clone_part(m, adin, "C2", "C68", CX, 189.72, MOTOR_PATH)
assert pins(m, "C68") == {"1": (CX, 189.72), "2": (CX, 194.8)}, pins(m, "C68")
c68 = get_props(m, "C68")
assert c68["Value"] == "CL05A105KP5NNNC" and c68["VOLTAGE RATING"] == "10V" and c68["CAPACITANCE"] == "1uF" and c68["PLANNED LCSC"] == "C14445", c68
m = set_props(m, "C68", {"SHEET": "MotorADC", "PLANNED NOTE": "1 uF at U13 on N6_3V3 (STAGE0_PLAN.md decision 5); same part as C2 / C4 (fields copied from C2)"})
m = wire(m, (CX, 194.8), (CX, 197.34))
m = power(m, "#PWR109", CX, 197.34, MOTOR_PATH)
# ~{ADC_ALERT}: the hierarchical label becomes a local label; test point TP44 in the sheet's test-point row
hl = [(s, e, b) for s, e, b in schedit.top_level(m, "hierarchical_label") if b.startswith('\t(hierarchical_label "~{ADC_ALERT}"')]
assert len(hl) == 1 and "(at 107.52 199.88 0)" in hl[0][2]
m = m[:hl[0][0]] + m[hl[0][1]:]
m = schedit.add_label(m, "~{ADC_ALERT}", 107.52, 199.88, 0)
m = clone_part(m, m, "TP43", "TP44", 387.76, 72.39, MOTOR_PATH)
assert pins(m, "TP44") == {"1": (387.76, 74.93)}
m = wire(m, (387.76, 74.93), (387.76, 77.47))
m = schedit.add_label(m, "~{ADC_ALERT}", 387.76, 77.47, 0)
# connectors
assert get_props(m, "J7")["PLANNED MPN"] == "SM04B-GHS-TB" and get_props(m, "J8")["PLANNED MPN"] == "SM03B-GHS-TB"
m = set_props(m, "J7", GH4)
m = set_props(m, "J8", {"Value": "BM03B-GHS-TBT(LF)(SN)", "Footprint": "Connector_JST:JST_GH_BM03B-GHS-TBT_1x03-1MP_P1.25mm_Vertical",
                        "Description": "CONN HEADER SMD TOP ENTRY 3POS 1.25MM", "PLANNED MPN": "BM03B-GHS-TBT(LF)(SN)", "PLANNED LCSC": "C161691",
                        "PLANNED NOTE": "Top-entry JST GH, 3 pins; 1 = N6_3V3, 2 = wiper, 3 = GND (assumed order, unchanged). Part and LCSC number: " + SRC,
                        "SOURCING": "JLC (" + SRC + ")"})
# the longer part number would run into R51: J8's value text goes below the connector
j8b = block_of(m, "J8")
m = m.replace(j8b, _set_prop_at(j8b, "Value", 142.0, 209.6, 0, "left"), 1)
m = replace_once(m, "ADS1115 on shield 3V3, bus I2C0", "ADS1115 on N6_3V3 (the N6's 3V3 pin), bus I2C0")
m = replace_once(m, "J8: 1 = 3V3, 2 = wiper", "J8: 1 = N6_3V3, 2 = wiper")
write("motor", m)
print("  Motor + ADC: U13 / C65 / R49 / J8 pin 1 on N6_3V3, C68 added, ~{ADC_ALERT} on TP44, J7 / J8 parts")

# ================================================================ cover page: I2C address table
r = read("root")
r = table_drop_rows(r, "Bus", ["keep free: HAT EEPROM probe at boot", "none on this board; free for a\\nLiFePO4wered UPS"])
r = cell_text(r, "Pi pins", "N6 pins")
r = cell_text(r, "GPIO0 / GPIO1\\n(pins 27 / 28)", "P4 (SCL) / P5 (SDA)")
r = cell_text(r, "GPIO0 / GPIO1", "P4 / P5")
r = cell_text(r, "I2C3 (sw)", "I2C0")
r = cell_text(r, "GPIO22 / GPIO27\\n(pins 15 / 13)", "P4 / P5")
r = cell_text(r, "Qwiic J3 only, no device on board", "Qwiic J3, no device on board")
write("root", r)
print("  cover page: I2C address table follows the one bus on P4 / P5")
