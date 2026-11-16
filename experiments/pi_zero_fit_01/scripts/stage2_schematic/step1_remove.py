#!/usr/bin/env python3
"""Step 1 (item A, as amended): remove MP1-MP4, J2, J6 and TP36 from the Top-Level sheet.

Nick, design session's chat, 2026-11-15: inserts, breakout header J2, header J6 and TP36 go. J4 / F1 (AUX 5 V) and
JP1 stay exactly as they are (scope change of the same day), so nothing of theirs is touched here.

- MP1-MP4, TP36: schedit.delete (the part, then its dead wire stubs and junctions). The bus wires and their BM1_P /
  BM1_N / BM2_P / BM2_N labels stay for the new connectors (step 2).
- J2 and J6: everything inside their drawing areas (part, wires, labels, power symbols) and the two section titles.
- J1 pins that only served J2 (8 UART_TX, 10 UART_RX, 11 ~{SPI1_CE1}, 12 ~{SPI1_CE0}, 35 SPI1_MISO, 38 SPI1_MOSI,
  40 SPI1_SCLK): stub and label removed, no-connect flag on the pin (the sheet's rule for unused GPIO pins).
  Kept: I2C0 (U4, new ADC), I2C3 (J3), MOTOR_* and ~{ADC_ALERT} (steps 3 and 4), PI_5V (JP1), PI_3V3.
"""
from s2lib import WIRE, box_delete, pins, read_top, refs, remove_exact, schedit, write_top

t = read_top()
if "J2" not in refs(t):
    raise SystemExit("step 1 already applied")
bm_before = {n: t.count(f'(label "{n}"') for n in ("BM1_P", "BM1_N", "BM2_P", "BM2_N")}

t, rep = schedit.delete(t, refs=["MP1", "MP2", "MP3", "MP4", "TP36"])
assert rep["parts"] == ["MP1", "MP2", "MP3", "MP4", "TP36"] and not rep["labels"] and not rep["power_symbols"], rep
print("  inserts and TP36:", rep)

t, rep = box_delete(t, (450.0, 300.0, 548.0, 350.0), ["J2"])
print("  J2 area:", rep)
assert sorted(rep["power"]) == ["#PWR07", "#PWR080", "#PWR084", "#PWR085"], rep
t, rep = box_delete(t, (345.0, 305.0, 400.0, 330.0), ["J6"])
print("  J6 area:", rep)
assert rep["power"] == ["#PWR093"] and rep["labels"] == ["PI_5V"], rep
t = remove_exact(t, "text_box", '\t(text_box "HEADER BREAKOUT FOR DEVELOPMENT')
t = remove_exact(t, "text_box", '\t(text_box "PI 3V3 REGULATED POWER"')

j1 = pins(t, "J1")
for pin, name in (("8", "UART_TX"), ("10", "UART_RX"), ("11", "~{SPI1_CE1}"), ("12", "~{SPI1_CE0}"),
                  ("35", "SPI1_MISO"), ("38", "SPI1_MOSI"), ("40", "SPI1_SCLK")):
    x, y = j1[pin]
    labels = [m for m in schedit.LABEL.finditer(t) if m.group(2) == name]
    assert len(labels) == 1 and float(labels[0].group(4)) == y, (name, len(labels))
    lx = float(labels[0].group(3))
    t = t[:labels[0].start()] + t[labels[0].end():]
    stubs = [m for m in WIRE.finditer(t) if {(float(m.group(1)), float(m.group(2))), (float(m.group(3)), float(m.group(4)))} == {(lx, y), (x, y)}]
    assert len(stubs) == 1, (name, len(stubs))
    t = t[:stubs[0].start()] + t[stubs[0].end():]
    t = schedit.add_no_connect(t, x, y)
    print(f"  J1 pin {pin}: {name} label and stub removed, no-connect flag at ({x}, {y})")

for n, c in bm_before.items():
    assert t.count(f'(label "{n}"') == c, n
for keep in ("J4", "F1", "JP1", "J5", "J3", "J1"):
    assert keep in refs(t), keep
write_top(t)
