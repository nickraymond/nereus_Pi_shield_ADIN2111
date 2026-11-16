#!/usr/bin/env python3
"""Stage 9: schematic (Top-Level sheet). The two motor-driver inputs change places at the Pi header:
  MOTOR_IN1  J1 pin 12 (GPIO18 / PWM0) -> J1 pin 33 (GPIO13 / PWM1)
  MOTOR_IN2  J1 pin 33 (GPIO13 / PWM1) -> J1 pin 12 (GPIO18 / PWM0)
Two labels are renamed where they stand (no wire, symbol or junction changes; same length, so the file keeps its size):
  label at J1 pin 12's stub  (116.84, 120.65)  MOTOR_IN1 -> MOTOR_IN2
  label at J1 pin 33's stub  (165.1, 151.13)   MOTOR_IN2 -> MOTOR_IN1
No text on any sheet names the GPIO of either input (searched: GPIO13, GPIO18, PWM, MOTOR_IN), so nothing else changes.
Usage: python3 step1_schematic.py <board dir>"""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))
from midwire import symbol_pins
TOP = Path(sys.argv[1]) / "Nereus_Pi_Shield_Adin2111_TopLevel.kicad_sch"
t = TOP.read_text(encoding="utf-8"); n0 = len(t)
pins = {(r, n): (round(x, 4), round(y, 4)) for r, n, x, y in symbol_pins(t)}
assert pins[("J1", "12")] == (121.92, 120.65) and pins[("J1", "33")] == (162.56, 151.13), "pins are not where this script expects them"
c0 = {n: len(re.findall(r'\(label "%s"' % n, t)) for n in ("MOTOR_IN1", "MOTOR_IN2")}; assert c0 == {"MOTOR_IN1": 3, "MOTOR_IN2": 2}, c0
A = '(label "MOTOR_IN1"\n\t\t(at 116.84 120.65 180)'; B = '(label "MOTOR_IN2"\n\t\t(at 165.1 151.13 0)'
assert t.count(A) == 1 and t.count(B) == 1, "run on the stage-8 sheet"
t = t.replace(A, A.replace("MOTOR_IN1", "MOTOR_IN2")).replace(B, B.replace("MOTOR_IN2", "MOTOR_IN1"))
print("  label at (116.84 120.65): MOTOR_IN1 -> MOTOR_IN2 (J1 pin 12)"); print("  label at (165.1 151.13): MOTOR_IN2 -> MOTOR_IN1 (J1 pin 33)")
assert len(t) == n0 and {n: len(re.findall(r'\(label "%s"' % n, t)) for n in c0} == c0
TOP.write_text(t, encoding="utf-8")
