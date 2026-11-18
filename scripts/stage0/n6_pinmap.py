"""Pin NUMBER -> (N6 signal, shield net) for the two N6 headers. Used by step0b_add_remap.py and pintable.py.

How the numbers were worked out (2026-11-17, this session):
- Footprint Connector_PinHeader_2.54mm:PinHeader_2x08_P2.54mm_Vertical, library frame (read with pcbnew): pad 1 at
  (0, 0), pad 2 at (2.54, 0), pad 3 at (0, 2.54) ... pad 15 at (0, 17.78), pad 16 at (2.54, 17.78): odd pads in one
  column, even pads in the other, rows running in +y.
- Mock P places both headers with header() of scripts/n6_rough_board.py: flipped left-right to the N6-facing (bottom)
  side, not turned, pad centroid at (X', y) = (2.83, 10.48) for J21 and (32.73, 10.48) for J22. The same calls run on
  an empty board give: pads 1 / 2 at y 19.37 (row 1, camera end) ... pads 15 / 16 at y 1.59 (row 8, USB end);
  J21 odd pads at X' 4.10, even pads at X' 1.56; J22 odd pads at X' 34.00, even pads at X' 31.46.
- The mock's frame is the shield seen from its top side = the N6 seen from its back, so X' = 35.56 - x of the N6
  model's frame (N6_FACTS.md: columns x 1.56 left outer, 4.10 left inner, 31.42 right inner, 33.96 right outer; the
  mock's west pad columns sit 0.04 mm off the mirrored model values 1.60 / 4.14).
  J22 (east) = N6 left header J2: odd pads = left OUTER column (P0 ... P6, 3V3), even pads = left INNER column.
  J21 (west) = N6 right header J3: odd pads = right INNER column, even pads = right OUTER column (RESET ... VIN, GND).
- Row k (1 = camera end ... 8 = USB end) is pads 2k-1 and 2k. Signals per column and row: N6_FACTS.md, header table.
This holds only if the board step places the footprints exactly as header() does, and it rests on N6_FACTS.md's open
item: the left / right sense of a real N6 seen from the back is not yet confirmed on a board.
Net None = not connected (no-connect flag); "GND", "N6_3V3" = power symbols; the others are labels.
"""
J22 = {  # east header, N6 J2 "left"
    1: ("P0", "N6_MOSI"), 2: ("ETH LED", None), 3: ("P1", "N6_MISO"), 4: ("ETH B-", None),
    5: ("P2", "N6_SCK"), 6: ("ETH B+", None), 7: ("P3", "~{N6_CS}"), 8: ("ETH A-", None),
    9: ("P4", "I2C0_SCL"), 10: ("ETH A+", None), 11: ("P5", "I2C0_SDA"), 12: ("PWR WKUP", None),
    13: ("P6", "~{ADIN_INT}"), 14: ("RAW", None), 15: ("3V3", "N6_3V3"), 16: ("GND", "GND"),
}
J21 = {  # west header, N6 J3 "right"
    1: ("ETH C+", None), 2: ("RESET", None), 3: ("ETH C-", None), 4: ("P11", None),
    5: ("ETH D+", None), 6: ("P10", None), 7: ("ETH D-", None), 8: ("P9", "~{ADIN_RST}"),
    9: ("P14", "MOTOR_nSLEEP"), 10: ("P8", "MOTOR_IN2"), 11: ("P13", "ADIN_PWR"), 12: ("P7", "MOTOR_IN1"),
    13: ("BOOT0", None), 14: ("VIN", "5V_PI"), 15: ("3V3", "N6_3V3"), 16: ("GND", "GND"),
}
HEADERS = {"J21": J21, "J22": J22}
assert sum(1 for m in HEADERS.values() for s, n in m.values() if n is None) == 15
