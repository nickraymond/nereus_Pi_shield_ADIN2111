#!/usr/bin/env python3
"""Step 3 (items C and D, motor): MP6550 motor driver copied from the Urchin board, and connector J7 "MOTOR".

Urchin (UrchinCam_01.kicad_sch, netlist) -> this board:
  U1  MP6550            -> U12   VIN = 5V_PI (Nick: "the motor driver needs to run on the 5V rail"); Urchin: +5V
  C7  10uF 10V  (VIN)   -> C60
  C31 100nF 50V (VIN)   -> C61
  -                     -> C62   47 uF bulk at VIN (review G S3; part to choose)
  C5  100nF 50V (VCC)   -> C63
  C6  470nF 50V (V3P3)  -> C64
  R3  2 kOhm (ISET)     -> R48   4.99 kOhm 1 %: limit 0.5 V / (100 uA/A x 4.99 kOhm) = 1.00 A (MP6550 Rev. 1.0 p. 11)
  J3  SM04B-GHS         -> J7    pins 1+2 = OUT1, 3+4 = OUT2, as on the Urchin
  IN1 (pin 1)  <- J1 pin 32 (Urchin PI_GPIO12)  = MOTOR_IN1
  IN2 (pin 10) <- J1 pin 33 (Urchin PI_GPIO13)  = MOTOR_IN2
  nSLEEP_HB (pin 12) <- J1 pin 29 (Urchin PI_GPIO5) = MOTOR_nSLEEP
  nSLEEP_LDO (pin 5): only a test point (TP1) on the Urchin -> no-connect flag (internal pull-down, LDO off)
  VISEN (pin 11) -> ADC AIN0 on the Urchin -> label MOTOR_VISEN (step 4)
Not copied: the Urchin's test points TP1, TP16, TP18, TP21.
"""
from s2lib import (clone_urchin, fields_right, gh4_ganged, junction, note, pins, power, read_top, refs, schedit, stub_label, title,
                   urchin_fields, wire, write_top)

t = read_top()
if "U12" in refs(t):
    raise SystemExit("step 3 already applied")
X, Y = 294.64, 314.96
t = clone_urchin(t, "U1", "U12", X, Y)
p = pins(t, "U12")
assert p["9"] == (278.13, 307.34) and p["3"] == (294.64, 327.66), p

# supply rail with the three capacitors
rail_y = p["9"][1]
left = 204.47
t = wire(t, p["9"], (left, rail_y))
t = schedit.add_label(t, "5V_PI", left, rail_y, 180)
for ref, src, x, lib in (("C61", "C31", 246.38, None), ("C60", "C7", 229.87, None), ("C62", "C7", 212.09, "CAP_47uF_bulk")):
    t = clone_urchin(t, src, ref, x, rail_y + 5.08, lib_name=lib)
    c = pins(t, ref)
    assert c["1"] == (x, rail_y + 2.54), c
    t = wire(t, (x, rail_y), c["1"])
    t = junction(t, x, rail_y)
    t = wire(t, c["2"], (x, c["2"][1] + 2.54))
    t = power(t, "GND", x, c["2"][1] + 2.54)
    t = fields_right(t, ref)
t = schedit.set_properties(t, "C62", {"Value": "47uF TBD", "Footprint": "Capacitor_SMD:C_1206_3216Metric",
                                      "Description": "CAP CER 47UF, 10 V or more, bulk at MP6550 VIN; part and footprint to choose"})

# control and sense
t = stub_label(t, p["1"], "MOTOR_IN1", -2.54)
t = stub_label(t, p["10"], "MOTOR_IN2", -2.54)
t = stub_label(t, p["12"], "MOTOR_nSLEEP", -2.54)
t = schedit.add_no_connect(t, *p["5"])
t = stub_label(t, p["11"], "MOTOR_VISEN", -2.54)
t = wire(t, p["3"], (p["3"][0], 330.2))
t = power(t, "GND", p["3"][0], 330.2)

# outputs
t = stub_label(t, p["2"], "MOTOR_OUT1", 2.54)
t = stub_label(t, p["8"], "MOTOR_OUT2", 2.54)
# ISET resistor, V3P3 and VCC capacitors
for ref, src, pin, x, lib in (("R48", "R3", "7", 317.5, "Res_4.99k_0402_1p"), ("C64", "C6", "4", 335.28, None), ("C63", "C5", "6", 353.06, None)):
    px, py = p[pin]
    t = clone_urchin(t, src, ref, x, py + 2.54, lib_name=lib)
    c = pins(t, ref)
    assert c["1"] == (x, py), (ref, c)
    t = wire(t, (px, py), (x, py))
    t = wire(t, c["2"], (x, 330.2))
    t = power(t, "GND", x, 330.2)
t = schedit.set_properties(t, "R48", {"Value": "4.99kΩ 1%",
                                      "Description": "RES 4.99K OHM 1% 0402; part to choose (Urchin R3: 2 kΩ CRCW04022K00FKED)"})

t = gh4_ganged(t, "J3", "J7", 388.62, 311.15, "MOTOR_OUT1", "MOTOR_OUT2", "MOTOR", "Same part and pinout as the Urchin board's J3")
t = note(t, "MOTOR", 384.81, 299.72, 2.54)

t = urchin_fields(t, "U12", "U1", "MP6550GG")
t = urchin_fields(t, "C60", "C7", "GRM155R61A106ME11D")
t = urchin_fields(t, "C61", "C31", "CC0402KRX5R9BB104")
t = urchin_fields(t, "C63", "C5", "CC0402KRX5R9BB104")
t = urchin_fields(t, "C64", "C6", "UMK105ABJ474KV-F")
t = schedit.set_properties(t, "U12", {"Footprint": "urchin:MP6550GG"})
from s2lib import set_props  # noqa: E402
t = set_props(t, "R48", {"PLANNED MPN": "", "PLANNED LCSC": "", "PLANNED NOTE": "Part to choose: 4.99 kΩ 1 % 0402. Urchin R3 was 2 kΩ (2.5 A limit); changed on review G S3 for a 1.0 A limit"})
t = set_props(t, "C62", {"PLANNED MPN": "", "PLANNED LCSC": "", "PLANNED NOTE": "Part to choose: 47 µF ceramic, 10 V or more; no 47 µF ceramic in this project's or the Urchin's BOM. Footprint C_1206 is a placeholder"})

t = note(t, "MP6550 on the 5 V rail (5V_PI). R48 sets the current limit and the VISEN scale:\\n"
            "limit = 0.5 V / (100 µA/A x R48) = 1.00 A; VISEN = 0.499 V/A (MP6550 Rev. 1.0, p. 11).\\n"
            "Urchin board: 2 kΩ (2.5 A). C62 = added bulk; C60, C61, C63, C64 as on the Urchin.\\n"
            "nSLEEP_LDO open: internal pull-down, 3.3 V LDO off (Urchin: test point only).", 204.47, 290.83)
t = title(t, "MOTOR DRIVER - MP6550", 203.2, 339.09, 120)
write_top(t)
print("  U12 MP6550, C60-C64, R48, J7 MOTOR placed")
