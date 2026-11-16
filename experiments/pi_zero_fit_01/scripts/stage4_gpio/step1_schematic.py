#!/usr/bin/env python3
"""Stage 4, step 1: schematic. Only the Top-Level sheet is edited (text edits with the repo's tools/schedit.py, as stage 2 / 2c).

 1. J1 pins 8, 10, 11, 12, 35, 38 (GPIO14, 15, 17, 18, 19, 20): the no-connect flag goes, a stub and a label GPIOnn come.
    Pins 3 / 5 (GPIO2 / 3, reserved for the LiFePO4+ board's I2C1), 26 (GPIO7) and 40 (GPIO21) keep their flags.
 2. Four pad rows, stock symbols Connector_Generic:Conn_01x02 / Conn_01x03, stock footprints
    Connector_PinHeader_2.54mm:PinHeader_1x02 / 1x03_P2.54mm_Vertical (1.7 mm pads, 1.0 mm drill):
    J11 GPIO14 / GPIO15, J12 GPIO18 / GPIO19, J13 GPIO17 / GPIO20, J14 GND x 3.
 3. Four test points, copies of TP38 (Vault:PCB_TP_1.5mm): TP40 MOTOR_IN1, TP41 MOTOR_OUT1, TP42 MOTOR_OUT2, TP43 I2C0_SCL.
Usage: python3 step1_schematic.py <board dir>
"""
import re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / "tools"))           # the repo's own schedit.py / midwire.py / netcheck.py (read only)
import schedit
from midwire import symbol_pins
BOARD = Path(sys.argv[1]); TOP = BOARD / "Nereus_Pi_Shield_Adin2111_TopLevel.kicad_sch"
PROJECT = "Nereus_Pi_Shield_Adin2111"
SHEET_PATH = "/30e82bf5-1344-486b-817c-02d3b0649ce4/3c398828-e355-49f6-be37-cb3640d2c671"
STOCK = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Connector_Generic.kicad_sym"
t = TOP.read_text(encoding="utf-8")
refs = {schedit.symbol_ref(b) for _, _, b in schedit.top_level(t, "symbol")}
if "J11" in refs: raise SystemExit("step 1 already applied")
assert not refs & {"J12", "J13", "J14", "TP40", "TP41", "TP42", "TP43"}
pins = lambda ref: {n: (round(x, 4), round(y, 4)) for r, n, x, y in symbol_pins(t) if r == ref}

def stub(pin, name, dx):
    global t
    x, y = pin
    t = schedit.add_wire(t, x, y, round(x + dx, 4), y)
    t = schedit.add_label(t, name, round(x + dx, 4), y, 180 if dx < 0 else 0)

# --- 1. J1
GPIO = {"8": "GPIO14", "10": "GPIO15", "11": "GPIO17", "12": "GPIO18", "35": "GPIO19", "38": "GPIO20"}
j1 = pins("J1")
for num, name in GPIO.items():
    x, y = j1[num]; assert x == 121.92, (num, x)             # all six are on the symbol's left side
    hit = [m for m in schedit.NO_CONNECT.finditer(t) if (float(m.group(1)), float(m.group(2))) == (x, y)]
    assert len(hit) == 1, (num, hit)
    t = t[:hit[0].start()] + t[hit[0].end():]
    stub((x, y), name, -5.08)

# --- 2. pad rows, in the clear area left of the header (x 60..115, y 170..215)
assert not schedit.bbox_clear(t, 60, 170, 115, 215), "the place for J11..J14 / TP40..TP43 is not clear"
t = schedit.ensure_lib_symbol(t, "Connector_Generic:Conn_01x03", STOCK)
FP = "Connector_PinHeader_2.54mm:PinHeader_1x0%d_P2.54mm_Vertical"
ROWS = (("J11", 2, 177.8, ("GPIO14", "GPIO15"), "GPIO14 / GPIO15"), ("J12", 2, 185.42, ("GPIO18", "GPIO19"), "GPIO18 / GPIO19"),
        ("J13", 2, 193.04, ("GPIO17", "GPIO20"), "GPIO17 / GPIO20"), ("J14", 3, 203.2, ("GND", "GND", "GND"), "GND pads"))
src_gnd = next(b for _, _, b in schedit.top_level(t, "symbol") if schedit.symbol_ref(b) == "#PWR01")
gx, gy = map(float, re.search(r'\(lib_id "[^"]+"\)\s*\(at ([-\d.]+) ([-\d.]+)', src_gnd).groups())
gpin = pins("#PWR01"); gpx, gpy = list(gpin.values())[0]
allsch = "".join(p.read_text() for p in BOARD.glob("*.kicad_sch"))
for ref, n, y, nets, value in ROWS:
    t, _ = schedit.add_symbol(t, "Connector_Generic:Conn_01x0%d" % n, ref, value, 85.09, y, footprint=FP % n, sheet_path=SHEET_PATH,
                              ref_offset=(0, -5.08), value_offset=(7.62, 0))
    t = t.replace('(project ""', '(project "%s"' % PROJECT)
    p = pins(ref); assert len(p) == n, p
    if nets[0] == "GND":
        xs = {p[k][0] for k in p}; assert len(xs) == 1; x = xs.pop(); ys = sorted(p[k][1] for k in p)
        for yy in ys: t = schedit.add_wire(t, x, yy, x - 5.08, yy)
        t = schedit.add_wire(t, x - 5.08, ys[0], x - 5.08, ys[1]); t = schedit.add_wire(t, x - 5.08, ys[1], x - 5.08, ys[2])
        t = schedit.add_wire(t, x - 5.08, ys[2], x - 5.08, ys[2] + 2.54)
        import uuid
        t = schedit._insert_after_last(t, "junction", '\t(junction\n\t\t(at %s %s)\n\t\t(diameter 0)\n\t\t(color 0 0 0 0)\n\t\t(uuid "%s")\n\t)\n' % (schedit.fmt(x - 5.08), schedit.fmt(ys[1]), uuid.uuid4()), fallback_kind="wire")
        t = schedit._insert_after_last(t, "junction", '\t(junction\n\t\t(at %s %s)\n\t\t(diameter 0)\n\t\t(color 0 0 0 0)\n\t\t(uuid "%s")\n\t)\n' % (schedit.fmt(x - 5.08), schedit.fmt(ys[2]), uuid.uuid4()), fallback_kind="wire")
        new = schedit.next_ref([allsch, t], "#PWR")
        t = schedit.clone_symbol(t, t, "#PWR01", new, x - 5.08 - (gpx - gx), ys[2] + 2.54 - (gpy - gy), SHEET_PATH)
    else:
        for k, name in zip(sorted(p, key=int), nets): stub(p[k], name, -5.08)
    for s, e, b in schedit.top_level(t, "symbol"):          # description, as the other connectors carry one
        if schedit.symbol_ref(b) == ref:
            nb = b.replace('(property "Description" ""', '(property "Description" "Exposed through-hole pads, 2.54 mm pitch, 1.0 mm hole (no part fitted): %s"' % ", ".join(nets), 1)
            t = t[:s] + nb + t[e:]; break

# --- 3. test points (copies of TP38)
TPS = (("TP40", 172.72, "MOTOR_IN1"), ("TP41", 182.88, "MOTOR_OUT1"), ("TP42", 193.04, "MOTOR_OUT2"), ("TP43", 203.2, "I2C0_SCL"))
for ref, y, name in TPS:
    assert len(re.findall(r'\(label "%s"' % re.escape(name), t)) >= 1, name
    t = schedit.clone_symbol(t, t, "TP38", ref, 105.41, y, SHEET_PATH)
    (px, py), = pins(ref).values()
    t = schedit.add_wire(t, px, py, px, py + 2.54)
    t = schedit.add_label(t, name, px, py + 2.54, 0)
assert t.count("(") == t.count(")"), "unbalanced parentheses"
TOP.write_text(t, encoding="utf-8")
print("  J1: 6 no-connect flags -> labels %s; J11..J14; TP40..TP43" % ", ".join(GPIO.values()))
