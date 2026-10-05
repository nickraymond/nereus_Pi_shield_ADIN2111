#!/usr/bin/env python3
"""Unit tests for midwire.py. Run: python3 tools/test_midwire.py"""
import unittest

from midwire import WIRE, JUNCTION, find, on_interior, split_and_join

WIRE_TXT = ('\t(wire\n\t\t(pts\n\t\t\t(xy 10 20.0022) (xy 30 20.0022)\n\t\t)\n'
            '\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)\n\t\t(uuid "w1")\n\t)\n')
# A one-pin part whose pin end lands at (15, 20.0022): placed at (15, 22.5422), lib pin at (0, 2.54).
SHEET = ('(kicad_sch\n\t(lib_symbols\n\t\t(symbol "lib:TP"\n\t\t\t(symbol "TP_0_1"\n'
         '\t\t\t\t(pin passive line\n\t\t\t\t\t(at 0 2.54 270)\n\t\t\t\t\t(number "1")\n\t\t\t\t)\n'
         '\t\t\t)\n\t\t)\n\t)\n' + WIRE_TXT +
         '\t(symbol\n\t\t(lib_id "lib:TP")\n\t\t(at 15 22.5422 0)\n\t\t(unit 0)\n'
         '\t\t(property "Reference" "TP1"\n\t\t)\n\t)\n)\n')


class MidwireTest(unittest.TestCase):
    def test_on_interior(self):
        self.assertTrue(on_interior(15, 20.0022, 10, 20.0022, 30, 20.0022))
        self.assertFalse(on_interior(10, 20.0022, 10, 20.0022, 30, 20.0022))  # an end
        self.assertFalse(on_interior(15, 21, 10, 20.0022, 30, 20.0022))       # off the wire

    def test_find_pin_mid_wire(self):
        self.assertEqual(find(SHEET, {}), {(15.0, 20.0022): ["TP1.1"]})
        self.assertEqual(find(SHEET, {"TP1": "deleted later"}), {})

    def test_split_and_join(self):
        out = split_and_join(SHEET, 15, 20.0022)
        ends = sorted(m.groups()[:4] for m in WIRE.finditer(out))
        self.assertEqual(ends, [("10", "20.0022", "15", "20.0022"), ("15", "20.0022", "30", "20.0022")])
        self.assertEqual(JUNCTION.findall(out), [("15", "20.0022")])
        self.assertEqual(find(out, {}), {})
        self.assertEqual(len(set(__import__("re").findall(r'\(uuid "([^"]+)"\)', out))), 3)


    def test_symbol_whose_name_ends_in_digits_is_seen(self):
        # Connector:Raspberry_Pi_2_3 ends in "_2_3", like a unit sub-symbol; its pins
        # were skipped before S4.b
        s = SHEET.replace('"lib:TP"', '"lib:Pi_2_3"').replace('"TP_0_1"', '"Pi_2_3_1_1"')
        self.assertEqual(find(s, {}), {(15.0, 20.0022): ["TP1.1"]})

if __name__ == "__main__":
    unittest.main()
