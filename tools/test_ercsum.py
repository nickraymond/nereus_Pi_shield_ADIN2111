#!/usr/bin/env python3
"""Unit tests for ercsum.py. Run: python3 tools/test_ercsum.py"""
import unittest

from ercsum import group_item, parse

REPORT = """ERC report (2026-10-05)

***** Sheet /
[pin_not_connected]: Pin not connected
    ; error
    @(10.00 mm, 20.00 mm): Symbol J1 Pin 3 [SDA/GPIO2, Bidirectional, Line]
[pin_not_connected]: Pin not connected
    ; error
    @(1.00 mm, 2.00 mm): Symbol FID1 Hidden pin 0 [NC, Passive, Line]
[pin_not_connected]: Pin not connected
    ; error
    @(3.00 mm, 4.00 mm): Hierarchical Sheet Pin SW_FLAGB
[endpoint_off_grid]: Symbol pin or wire end off connection grid
    ; warning
    @(5.00 mm, 6.00 mm): Horizontal Wire, length 2.54 mm

 ** ERC messages: 4  Errors 3  Warnings 1
"""


class ErcsumTest(unittest.TestCase):
    def test_parse_counts_every_item_kind(self):
        rows = parse(REPORT)
        self.assertEqual(len(rows), 4)
        self.assertEqual(sum(1 for r in rows if r[0] == "error"), 3)
        self.assertIn(("error", "pin_not_connected", "Hierarchical Sheet Pin SW_FLAGB"), rows)

    def test_group_item(self):
        self.assertEqual(group_item("Symbol J1 Pin 3 [SDA/GPIO2, Bidirectional, Line]"), "J1 pins")
        self.assertEqual(group_item("Symbol FID1 Hidden pin 0 [NC, Passive, Line]"), "Symbol FID1 Hidden pin 0")


if __name__ == "__main__":
    unittest.main()
