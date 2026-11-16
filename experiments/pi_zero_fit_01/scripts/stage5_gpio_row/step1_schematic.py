#!/usr/bin/env python3
"""Stage 5, step 1: schematic. Run on the stage-3 Top-Level sheet (commit 5f43210): stage 4's four scattered pad groups J11..J14 are
not carried over; one pad row under J1 (15 pads in five groups) replaces them. Text edits with the repo's tools/schedit.py, as stage 2 / 2c / 4.

 1. J1 pins 8, 10, 11, 12, 26, 35, 38, 40 (GPIO14, 15, 17, 18, 7, 19, 20, 21): no-connect flag (where there is one) goes, a stub
    and a label GPIOnn come. Pins 3 / 5 (GPIO2 / 3, I2C1 for the LiFePO4+ board) keep their flags.
 2. The pad row, five stock symbols Connector_Generic:Conn_01x0N with stock footprints
    Connector_PinHeader_2.54mm:PinHeader_1x0N_P2.54mm_Vertical (1.7 mm pads, 1.0 mm drill), west to east:
      J15  PI_5V, GND, GPIO14, GPIO15     J16  PI_3V3, PI_3V3     J17  GND, GPIO17
      J18  GPIO18, GPIO7, GND, GND        J19  GPIO19, GPIO20, GPIO21
    Bare solder holes, no part: the symbols are out of the BOM.
 3. Four test points as in stage 4 (copies of TP38): TP40 MOTOR_IN1, TP41 MOTOR_OUT1, TP42 MOTOR_OUT2, TP43 I2C0_SCL.
Usage: python3 step1_schematic.py <board dir>
"""
import re, sys, uuid
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / "tools"))           # the repo's own schedit.py / midwire.py (read only)
import schedit
from midwire import symbol_pins
BOARD = Path(sys.argv[1]); TOP = BOARD / "Nereus_Pi_Shield_Adin2111_TopLevel.kicad_sch"
PROJECT = "Nereus_Pi_Shield_Adin2111"
SHEET_PATH = "/30e82bf5-1344-486b-817c-02d3b0649ce4/3c398828-e355-49f6-be37-cb3640d2c671"
STOCK = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Connector_Generic.kicad_sym"
t = TOP.read_text(encoding="utf-8")
refs = {schedit.symbol_ref(b) for _, _, b in schedit.top_level(t, "symbol")}
assert not refs & {"J11", "J12", "J13", "J14", "J15", "J16", "J17", "J18", "J19", "TP40", "TP41", "TP42", "TP43"}, "run on the stage-3 sheet"
pins = lambda ref: {n: (round(x, 4), round(y, 4)) for r, n, x, y in symbol_pins(t) if r == ref}

def stub(pin, name, dx):
    global t
    x, y = pin
    t = schedit.add_wire(t, x, y, round(x + dx, 4), y)
    t = schedit.add_label(t, name, round(x + dx, 4), y, 180 if dx < 0 else 0)
def junction(x, y):
    global t
    t = schedit._insert_after_last(t, "junction", '\t(junction\n\t\t(at %s %s)\n\t\t(diameter 0)\n\t\t(color 0 0 0 0)\n\t\t(uuid "%s")\n\t)\n' % (schedit.fmt(x), schedit.fmt(y), uuid.uuid4()), fallback_kind="wire")

# --- 1. J1
GPIO = {"8": "GPIO14", "10": "GPIO15", "11": "GPIO17", "12": "GPIO18", "26": "GPIO7", "35": "GPIO19", "38": "GPIO20", "40": "GPIO21"}
j1 = pins("J1"); flags = 0
for num, name in GPIO.items():
    x, y = j1[num]; assert x in (121.92, 162.56), (num, x)    # left or right side of the symbol
    sgn = -1 if x == 121.92 else 1
    hit = [m for m in schedit.NO_CONNECT.finditer(t) if (float(m.group(1)), float(m.group(2))) == (x, y)]
    if not hit:      # pin 26: the flag sits at the end of a 2.54 mm wire that is already there; the new stub starts at that end
        hit = [m for m in schedit.NO_CONNECT.finditer(t) if (float(m.group(1)), float(m.group(2))) == (round(x + sgn * 2.54, 4), y)]
        x = round(x + sgn * 2.54, 4)
    assert len(hit) == 1, (num, hit)
    t = t[:hit[0].start()] + t[hit[0].end():]; flags += 1
    stub((x, y), name, sgn * (5.08 - abs(x - j1[num][0])))

# --- 2. the pad row, in the clear area left of the header
assert not schedit.bbox_clear(t, 55, 165, 115, 235), "the place for J15..J19 / TP40..TP43 is not clear"
for n in (3, 4): t = schedit.ensure_lib_symbol(t, "Connector_Generic:Conn_01x0%d" % n, STOCK)
FP = "Connector_PinHeader_2.54mm:PinHeader_1x0%d_P2.54mm_Vertical"
ROWS = (("J15", 172.72, ("PI_5V", "GND", "GPIO14", "GPIO15")), ("J16", 187.96, ("PI_3V3", "PI_3V3")), ("J17", 198.12, ("GND", "GPIO17")),
        ("J18", 210.82, ("GPIO18", "GPIO7", "GND", "GND")), ("J19", 228.6, ("GPIO19", "GPIO20", "GPIO21")))
allsch = "".join(p.read_text() for p in BOARD.glob("*.kicad_sch"))
def power(src_ref, prefix, x, y):
    """a copy of power symbol src_ref with its pin at (x, y)"""
    global t
    (px, py), = pins(src_ref).values()
    blk = next(b for _, _, b in schedit.top_level(t, "symbol") if schedit.symbol_ref(b) == src_ref)
    ox, oy = map(float, re.search(r'\(lib_id "[^"]+"\)\s*\(at ([-\d.]+) ([-\d.]+)', blk).groups())
    t = schedit.clone_symbol(t, t, src_ref, schedit.next_ref([allsch, t], prefix), x - (px - ox), y - (py - oy), SHEET_PATH)
for ref, y, nets in ROWS:
    n = len(nets)
    t, _ = schedit.add_symbol(t, "Connector_Generic:Conn_01x0%d" % n, ref, "pad row: " + " / ".join(nets), 85.09, y, footprint=FP % n, sheet_path=SHEET_PATH,
                              ref_offset=(0, -7.62), value_offset=(12.7, -7.62))
    t = t.replace('(project ""', '(project "%s"' % PROJECT)
    p = pins(ref); assert len(p) == n, p
    order = sorted(p, key=int); x = p[order[0]][0]
    for k, name in zip(order, nets):
        if name not in ("GND", "PI_3V3"): stub(p[k], name, -5.08)
    for name, src, up in (("PI_3V3", "#PWR065", True), ("GND", "#PWR66", False)):      # one power symbol per run of neighbouring pins
        ys = [p[k][1] for k, nm in zip(order, nets) if nm == name]
        if not ys: continue
        assert len(ys) == 1 or abs(ys[1] - ys[0] - 2.54) < 1e-6, (ref, name, ys)
        last = nets[-1] == name                      # nothing under the run: the symbol can sit close; else it goes out past the labels
        X = round(x + (-12.7 if up else -5.08 if last else -17.78), 4)
        for yy in ys: t = schedit.add_wire(t, x, yy, X, yy)
        if len(ys) == 2: t = schedit.add_wire(t, X, ys[0], X, ys[1]); junction(X, ys[0] if up else ys[1])
        if up: t = schedit.add_wire(t, X, ys[0], X, ys[0] - 2.54); power(src, "#PWR", X, ys[0] - 2.54)
        else: t = schedit.add_wire(t, X, ys[-1], X, ys[-1] + 2.54); power(src, "#PWR", X, ys[-1] + 2.54)
    for s, e, b in schedit.top_level(t, "symbol"):          # description; out of the BOM (no part is fitted)
        if schedit.symbol_ref(b) == ref:
            nb = b.replace('(property "Description" ""', '(property "Description" "Exposed through-hole pads under J1, 2.54 mm pitch, 1.7 mm pad, 1.0 mm hole (no part fitted): %s"' % ", ".join(nets), 1)
            nb = nb.replace("(in_bom yes)", "(in_bom no)", 1); assert nb != b
            t = t[:s] + nb + t[e:]; break

# --- 3. test points (copies of TP38), as stage 4
TPS = (("TP40", 172.72, "MOTOR_IN1"), ("TP41", 182.88, "MOTOR_OUT1"), ("TP42", 193.04, "MOTOR_OUT2"), ("TP43", 203.2, "I2C0_SCL"))
for ref, y, name in TPS:
    assert len(re.findall(r'\(label "%s"' % re.escape(name), t)) >= 1, name
    t = schedit.clone_symbol(t, t, "TP38", ref, 105.41, y, SHEET_PATH)
    (px, py), = pins(ref).values()
    t = schedit.add_wire(t, px, py, px, py + 2.54)
    t = schedit.add_label(t, name, px, py + 2.54, 0)
assert t.count("(") == t.count(")"), "unbalanced parentheses"
TOP.write_text(t, encoding="utf-8")
print("  J1: %d no-connect flags removed, 8 labels %s; J15..J19; TP40..TP43" % (flags, ", ".join(GPIO.values())))
