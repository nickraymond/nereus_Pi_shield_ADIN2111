#!/usr/bin/env python3
"""Tests for tools/ercexclude.py (key format, matching). No KiCad needed."""
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ercexclude import NIL, errors, is_manual, iu, justify, key  # noqa: E402

ITEM = {"description": "Symbol FID1 Hidden pin 0 [NC, Passive, Line]",
        "pos": {"x": 2.2987, "y": 3.2385}, "uuid": "63b235cc-7b80-4d92-a67a-d180d0bdc57f"}
PATH = "/30e82bf5-1344-486b-817c-02d3b0649ce4/3c398828-e355-49f6-be37-cb3640d2c671"


class TestErcExclude(unittest.TestCase):
    def test_iu(self):
        self.assertEqual(iu(2.2987), 2298700)      # 229.87 mm
        self.assertEqual(iu(1.344422), 1344422)

    def test_key_format(self):
        # The exact form KiCad 9.0.6 accepted for this item (checked with kicad-cli on a copy).
        self.assertEqual(key("pin_not_connected", ITEM, PATH),
                         f"pin_not_connected|2298700|3238500|63b235cc-7b80-4d92-a67a-d180d0bdc57f|{NIL}|{PATH}|{PATH}|")

    def test_errors_only(self):
        js = {"sheets": [{"uuid_path": PATH, "violations": [
            {"severity": "error", "type": "pin_not_connected", "items": [ITEM]},
            {"severity": "warning", "type": "endpoint_off_grid", "items": [ITEM]}]}]}
        self.assertEqual(errors(js), [("pin_not_connected", [ITEM], PATH)])

    def test_justify(self):
        rules = [("pin_not_connected", re.compile(r"^Symbol FID\d+ Hidden pin"), "fiducial")]
        other = dict(ITEM, description="Symbol J9 Pin 1 [1, Passive, Line]")
        found, missing = justify([("pin_not_connected", [ITEM], PATH), ("pin_not_connected", [other], PATH),
                                  ("power_pin_not_driven", [ITEM], PATH)], rules)
        self.assertEqual(list(found.values()), ["fiducial"])
        self.assertEqual(len(missing), 2)      # wrong ref; wrong type

    def test_manual_entries(self):
        self.assertTrue(is_manual(["k", "manual: two-item error, reviewed"]))
        self.assertTrue(is_manual(["k", "Manual: x"]))
        self.assertFalse(is_manual(["k", "fiducial"]))
        self.assertFalse(is_manual("k"))

    def test_two_item_error_not_keyed(self):
        rules = [("pin_not_connected", re.compile(r"^Symbol FID\d+ Hidden pin"), "fiducial")]
        found, missing = justify([("pin_not_connected", [ITEM, ITEM], PATH)], rules)
        self.assertEqual(found, {})
        self.assertIn("by hand", missing[0])


if __name__ == "__main__":
    unittest.main()
