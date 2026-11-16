#!/usr/bin/env python3
"""Step 0: libraries for the parts copied from the Urchin board (Nick's UrchinCam_Expander_PCBA_01).

- board/urchin.kicad_sym: the Urchin schematic's own embedded lib symbols for the parts that are copied (MP6550,
  ADS1115IDGS, SM04B-GHS, the 0402 resistors and capacitors), unchanged, plus three derived symbols:
    Res_4.99k_0402_1p  = Res_2k_0402_1p with value 4.99 kOhm (new ISET resistor)
    CAP_47uF_bulk      = CAP_10uF_0402_10V with value 47 uF, footprint C_1206 (bulk capacitor, part to choose)
    SM03B-GHS          = SM04B-GHS with three pins (POT connector)
- board/urchin.pretty/MP6550GG.kicad_mod: extracted from the Urchin board by run_all.sh (repo_tools/fpextract.py).
- nickname "urchin" in sym-lib-table and fp-lib-table.
"""
import re
from s2lib import BOARD, URCHIN_SCH, URCHIN_SYM, blocks, schedit

COPY = ["Motor_Drivers:MP6550", "Analog_ADC:ADS1115IDGS", "Connectors:SM04B-GHS", "Resistors:Res_10k_0402_5p",
        "Resistors:Res_2k_0402_1p", "Capacitors:CAP_100nF_0402_50V", "Capacitors:CAP_10uF_0402_10V",
        "Capacitors:CAP_470nF_0402_50V"]

src = URCHIN_SCH.read_text(encoding="utf-8")
ls = next(schedit.top_level(src, "lib_symbols"))[2]
syms = {}
for lib_id in COPY:
    b = next(blocks(ls, f'symbol "{lib_id}"'))
    assert "(extends " not in b
    name = lib_id.split(":", 1)[1]
    b = b.replace(f'(symbol "{lib_id}"', f'(symbol "{name}"', 1)
    # schematic lib_symbols are indented two tabs, a library one
    syms[name] = "\t" + "".join(l[1:] if l.startswith("\t") else l for l in b.splitlines(True)).rstrip("\n") + "\n"


def prop(block, name, value):
    out, n = re.subn(r'(\(property "%s" )"[^"]*"' % re.escape(name), lambda m: m.group(1) + '"' + value + '"', block, count=1)
    assert n == 1, name
    return out


def derive(base, name):
    b = syms[base].replace(f'(symbol "{base}"', f'(symbol "{name}"', 1)
    n = b.count(f'(symbol "{base}_')
    assert n >= 1
    return b.replace(f'(symbol "{base}_', f'(symbol "{name}_')


r = derive("Res_2k_0402_1p", "Res_4.99k_0402_1p")
r = prop(prop(r, "Value", "4.99kΩ 1%"), "Description", "RES 4.99K OHM 1% 0402; part to choose (Urchin R3: 2 kΩ CRCW04022K00FKED)")
r = prop(r, "ki_keywords", "RES 4.99K OHM 1% 0402")
syms["Res_4.99k_0402_1p"] = r

c = derive("CAP_10uF_0402_10V", "CAP_47uF_bulk")
c = prop(prop(c, "Value", "47uF TBD"), "Footprint", "Capacitor_SMD:C_1206_3216Metric")
c = prop(c, "Description", "CAP CER 47UF, 10 V or more, bulk at MP6550 VIN; part and footprint to choose")
c = prop(c, "ki_keywords", "CAP CER 47UF bulk")
syms["CAP_47uF_bulk"] = c

j = derive("SM04B-GHS", "SM03B-GHS")
j = prop(prop(j, "Value", "SM03B-GHS"), "Footprint", "Connector_JST:JST_GH_SM03B-GHS-TB_1x03-1MP_P1.25mm_Horizontal")
j = prop(j, "Description", "CONN HEADER SMD R/A 3POS 1.25MM")
# body ends below pin 3 (-1.27) instead of pin 4 (-3.81); pin 4 and its contact mark go
assert j.count("(end 1.27 -5.08)") == 1
j = j.replace("(end 1.27 -5.08)", "(end 1.27 -2.54)")
j = j.replace("(at 0.508 -6.858 0)", "(at 0.508 -4.318 0)", 1)
mark = re.search(r'\t\t\t\(rectangle\n\t\t\t\t\(start -1\.27 -3\.683\)\n.*?\n\t\t\t\)\n', j, re.S)
pin4 = re.search(r'\t\t\t\(pin passive line\n\t\t\t\t\(at -5\.08 -3\.81 0\)\n.*?\n\t\t\t\)\n(?=\t\t\)|\t\t\t\()', j, re.S)
assert mark and pin4 and '"Pin_4"' in pin4.group(0) and pin4.group(0).count("(pin ") == 1
j = j.replace(pin4.group(0), "").replace(mark.group(0), "")
assert j.count("(pin passive line") == 3 and j.count("(") == j.count(")")
syms["SM03B-GHS"] = j

lib = ('(kicad_symbol_lib\n\t(version 20251024)\n\t(generator "kicad_symbol_editor")\n\t(generator_version "10.0")\n'
       + "".join(syms[k] for k in sorted(syms)) + ")\n")
assert lib.count("(") == lib.count(")")
URCHIN_SYM.write_text(lib, encoding="utf-8")
print("  urchin.kicad_sym:", ", ".join(sorted(syms)))

for table, line in (("sym-lib-table", '  (lib (name "urchin")(type "KiCad")(uri "${KIPRJMOD}/urchin.kicad_sym")(options "")(descr "Symbols copied from the Urchin board schematic (UrchinCam_Expander_PCBA_01), plus three derived from them"))\n'),
                    ("fp-lib-table", '  (lib (name "urchin")(type "KiCad")(uri "${KIPRJMOD}/urchin.pretty")(options "")(descr "Footprints extracted from the Urchin board (UrchinCam_01.kicad_pcb) with fpextract.py"))\n')):
    p = BOARD / table
    t = p.read_text()
    if '(name "urchin")' not in t:
        t = t.rstrip().rstrip(")").rstrip() + "\n" + line + ")\n"
        p.write_text(t)
        print("  added urchin to", table)
