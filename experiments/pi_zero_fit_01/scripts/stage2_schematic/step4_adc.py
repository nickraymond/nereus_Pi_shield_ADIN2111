#!/usr/bin/env python3
"""Step 4 (items C and D, ADC): ADS1115 copied from the Urchin board, and connector J8 "POT".

Urchin -> this board:
  U2 ADS1115IDGS          -> U13   VDD = shield 3V3 (Urchin: +3V3)
  C8 100nF 50V (VDD)      -> C65
  R4 10 kOhm (ALERT/RDY pull-up to the ADC's supply) -> R49, to shield 3V3; net ~{ADC_ALERT} (J1 pin 7)
  R5 10 kOhm (ADDR to GND, address 1001000b = 0x48, SBAS444E Table 7-2) -> R50
  SCL / SDA: Urchin = the Pi's GPIO3 / GPIO2 bus with the board's other I2C chip. Here I2C0_SCL / I2C0_SDA (J1 pins
             28 / 27), the bus of the shield's own I2C chip U4 with pull-ups R26 / R27, as this sheet's note says
             ("I2C0 GPIO0/1 = shield: INA232 0x41, ADS1115 0x48"). The Urchin's bus pull-ups R1 / R2 are not copied.
  AIN0 = MP6550 VISEN (as on the Urchin) -> MOTOR_VISEN
  AIN1 = pot wiper (Urchin: test point TP5; this sheet's note: "AIN1 = shaft pot") -> POT_WIPER
  AIN2, AIN3: test points TP6 / TP7 on the Urchin -> no-connect flags (unused inputs may float, SBAS444E 9.1.4)
J8 "POT": JST GH 3-pin side entry SM03B-GHS-TB; 1 = 3V3, 2 = wiper, 3 = GND (the design session's assumption; the
Urchin has no 3-pin connector to follow).
"""
from s2lib import (clone_urchin, fields_right, junction, note, pins, power, read_top, refs, schedit, set_props, stub_label, title,
                   urchin_fields, wire, write_top)

t = read_top()
if "U13" in refs(t):
    raise SystemExit("step 4 already applied")
X, Y = 449.58, 314.96
t = clone_urchin(t, "U2", "U13", X, Y)
p = pins(t, "U13")
assert p["8"] == (449.58, 302.26) and p["4"] == (439.42, 312.42), p

t = stub_label(t, p["4"], "MOTOR_VISEN", -2.54)
t = stub_label(t, p["5"], "POT_WIPER", -2.54)
t = schedit.add_no_connect(t, *p["6"])
t = schedit.add_no_connect(t, *p["7"])
# supply and decoupling
t = wire(t, p["8"], (X, 297.18))
t = power(t, "3V3", X, 297.18)
t = clone_urchin(t, "C8", "C65", 416.56, 302.26)
c = pins(t, "C65")
assert c["1"] == (416.56, 299.72), c
t = wire(t, (X, 299.72), c["1"])
t = junction(t, X, 299.72)
t = wire(t, c["2"], (416.56, 307.34))
t = power(t, "GND", 416.56, 307.34)
t = wire(t, p["3"], (X, 327.66))
t = power(t, "GND", X, 327.66)
# ALERT with its pull-up
ax, ay = p["2"]
t = wire(t, (ax, ay), (477.52, ay))
t = schedit.add_label(t, "~{ADC_ALERT}", 477.52, ay, 0)
t = clone_urchin(t, "R4", "R49", 469.9, ay - 5.08)
r = pins(t, "R49")
assert r["2"] == (469.9, ay - 2.54), r
t = wire(t, r["2"], (469.9, ay))
t = junction(t, 469.9, ay)
t = wire(t, r["1"], (469.9, r["1"][1] - 2.54))
t = power(t, "3V3", 469.9, r["1"][1] - 2.54)
# bus
t = stub_label(t, p["10"], "I2C0_SCL", 2.54)
t = stub_label(t, p["9"], "I2C0_SDA", 2.54)
# address resistor
dx, dy = p["1"]
t = clone_urchin(t, "R5", "R50", 482.6, dy + 2.54)
r = pins(t, "R50")
assert r["1"] == (482.6, dy), r
t = wire(t, (dx, dy), r["1"])
t = wire(t, r["2"], (482.6, 327.66))
t = power(t, "GND", 482.6, 327.66)

# POT connector
t = clone_urchin(t, "J3", "J8", 520.7, 313.69, lib_name="SM03B-GHS", drop_pins=("4",))
t = schedit.set_properties(t, "J8", {"Value": "SM03B-GHS", "Description": "CONN HEADER SMD R/A 3POS 1.25MM",
                                     "Footprint": "Connector_JST:JST_GH_SM03B-GHS-TB_1x03-1MP_P1.25mm_Horizontal"})
j = pins(t, "J8")
assert sorted(j) == ["1", "2", "3"], j
t = wire(t, j["1"], (508.0, j["1"][1]), (508.0, j["1"][1] - 2.54))
t = power(t, "3V3", 508.0, j["1"][1] - 2.54)
t = stub_label(t, j["2"], "POT_WIPER", -2.54)
t = wire(t, j["3"], (508.0, j["3"][1]), (508.0, j["3"][1] + 2.54))
t = power(t, "GND", 508.0, j["3"][1] + 2.54)
t = note(t, "POT", 516.89, 302.26, 2.54)

for ref in ("C65", "R49", "R50"):
    t = fields_right(t, ref, 2.54 if ref != "C65" else 3.81)
t = urchin_fields(t, "U13", "U2", "ADS1115IDGS")
t = urchin_fields(t, "C65", "C8", "CC0402KRX5R9BB104")
t = urchin_fields(t, "R49", "R4", "RC0402JR-0710KL")
t = urchin_fields(t, "R50", "R5", "RC0402JR-0710KL")
t = set_props(t, "J8", {"FUNCTION": "POT", "PLANNED MPN": "SM03B-GHS-TB", "PLANNED MFR": "JST", "PLANNED LCSC": "",
                        "PLANNED NOTE": "3-pin version of the Urchin board's GH connectors; 1 = 3V3, 2 = wiper, 3 = GND (assumed order); LCSC number not looked up"})
t = note(t, "ADS1115 on shield 3V3, bus I2C0, address 0x48 (ADDR to GND through R50).\\n"
            "AIN0 = MP6550 VISEN, AIN1 = pot wiper (J8), AIN2 / AIN3 unused.\\n"
            "J8: 1 = 3V3, 2 = wiper, 3 = GND (assumed order).", 411.48, 285.75)
t = title(t, "ADC - ADS1115, POT", 411.48, 339.09, 110)
write_top(t)
print("  U13 ADS1115, C65, R49, R50, J8 POT placed")
