#!/usr/bin/env python3
"""Stage 8, job 3: schematic (Top-Level sheet). MOTOR_IN1 moves from J1 pin 32 (GPIO12 / PWM0) to J1 pin 12 (GPIO18 / PWM0); the spare pad
J18 pad 1 (x 41.39 in the pad row), GPIO18 until now, becomes GPIO12, fed from pin 32. MOTOR_IN2 stays on pin 33 (GPIO13 / PWM1).
Three labels are renamed where they stand (no wire, symbol or junction changes), and J18's value and description texts follow:
  label at J1 pin 12's stub  (116.84, 120.65)  GPIO18    -> MOTOR_IN1
  label at J1 pin 32's stub  (165.1, 148.59)   MOTOR_IN1 -> GPIO12
  label at J18 pin 1's stub  (74.93, 208.28)   GPIO18    -> GPIO12
Usage: python3 job3_schematic.py <board dir>"""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))
import schedit
from midwire import symbol_pins
TOP = Path(sys.argv[1]) / "Nereus_Pi_Shield_Adin2111_TopLevel.kicad_sch"
t = TOP.read_text(encoding="utf-8"); n0 = len(t)
pins = {(r, n): (round(x, 4), round(y, 4)) for r, n, x, y in symbol_pins(t)}
assert pins[("J1", "12")] == (121.92, 120.65) and pins[("J1", "32")] == (162.56, 148.59) and pins[("J18", "1")] == (80.01, 208.28), "pins are not where this script expects them"
assert not re.search(r'\(label "GPIO12"', t), "run on the stage-7 sheet"
for old, new, at in (("GPIO18", "MOTOR_IN1", "116.84 120.65 180"), ("MOTOR_IN1", "GPIO12", "165.1 148.59 0"), ("GPIO18", "GPIO12", "74.93 208.28 180")):
    a = '(label "%s"\n\t\t(at %s)' % (old, at); assert t.count(a) == 1, (old, at, t.count(a))
    t = t.replace(a, '(label "%s"\n\t\t(at %s)' % (new, at)); print("  label at (%s): %s -> %s" % (at, old, new))
for a, b in (('(property "Value" "pad row: GPIO18 / GPIO7 / GND / GND"', '(property "Value" "pad row: GPIO12 / GPIO7 / GND / GND"'),
             ("(no part fitted): GPIO18, GPIO7, GND, GND", "(no part fitted): GPIO12, GPIO7, GND, GND")):
    assert t.count(a) == 1, a
    t = t.replace(a, b)
assert not re.search(r'\(label "GPIO18"', t) and len(re.findall(r'\(label "GPIO12"', t)) == 2 and len(re.findall(r'\(label "MOTOR_IN1"', t)) == 3
assert len(t) - n0 == 3 + (-3) + 0 + 0 + 0, len(t) - n0      # GPIO18 -> MOTOR_IN1 (+3), MOTOR_IN1 -> GPIO12 (-3), the other three keep their length
TOP.write_text(t, encoding="utf-8")
