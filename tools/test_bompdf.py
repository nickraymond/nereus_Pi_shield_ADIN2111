#!/usr/bin/env python3
"""Unit tests for bompdf.py's HTML builder (no AppKit needed). Run: python3 tools/test_bompdf.py"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from bompdf import CHANGED, build  # noqa: E402

KEYS = ["Refs", "Qty", "Value (MPN)", "Mfr", "Planned MPN", "Planned Mfr", "Planned LCSC", "Planned note", "DNP",
        "Sourcing", "Alt1 MPN", "Alt1 Mfr", "Alt1 LCSC", "Alt2 MPN", "Alt2 Mfr", "Alt2 LCSC", "Alt note", "Footprint"]


def row(**kw):
    r = dict.fromkeys(KEYS, "")
    r.update(kw)
    return r


class TestBomPdf(unittest.TestCase):
    def test_counts_and_highlight(self):
        rows = [row(Refs="R1,R2", Qty="2", **{"Value (MPN)": "A", "Planned MPN": "A", "Footprint": "Vault:R0402"}),
                row(Refs="C1", Qty="1", **{"Value (MPN)": "B", "Planned MPN": "B2", "Planned LCSC": "C123"}),
                row(Refs="R9", Qty="1", DNP="DNP", **{"Value (MPN)": "Z", "Planned MPN": "Z"})]
        page = build(rows)
        self.assertIn("3 lines, 3 fitted parts per board (+ 1 DNP)", page)
        self.assertIn("1 lines where the planned part differs", page)
        self.assertEqual(page.count(f"<tr style='background:{CHANGED}'>"), 1)   # only C1
        self.assertIn("LCSC C123", page)
        self.assertIn("<td valign='top' width='130'>R0402</td>", page)        # library nickname dropped
        self.assertIn("<i>(DNP)</i>", page)

    def test_escapes_text(self):
        page = build([row(Refs="R1", Qty="1", **{"Value (MPN)": "A<B", "Planned MPN": "A<B", "Planned note": "x & y"})])
        self.assertIn("A&lt;B", page)
        self.assertIn("x &amp; y", page)


if __name__ == "__main__":
    unittest.main()
