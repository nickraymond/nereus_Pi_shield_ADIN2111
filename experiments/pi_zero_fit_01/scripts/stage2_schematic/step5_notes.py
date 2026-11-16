#!/usr/bin/env python3
"""Step 5: the sheet's own notes follow the changes (text only, no net changes)."""
from s2lib import read_top, write_top

t = read_top()
old = [
    "ADS1115 0x48 (bluewired). R26/R27",
    "J2 breakout 3V3 pins (9, 11) = PI_3V3. Shield 3V3 is for shield parts only.",
    "ADS1115: AIN0 = MP6550 VISEN (200 mV/A), AIN1 = shaft pot, AIN2 = spare. AIN3 unused.",
]
new = [
    "ADS1115 0x48 (U13). R26/R27",
    "Shield 3V3 is for shield parts only (ADC U13, pot J8); PI_3V3 feeds Qwiic and the I2C pull-ups.",
    "ADS1115: AIN0 = MP6550 VISEN (499 mV/A with R48 4.99k), AIN1 = shaft pot (J8), AIN2 / AIN3 unused.",
]
if new[0] in t:
    raise SystemExit("step 5 already applied")
for o, n in zip(old, new):
    assert t.count(o) == 1, o
    t = t.replace(o, n)
write_top(t)
print("  notes updated: ADS1115 on the board, J2 line replaced, VISEN scale")
