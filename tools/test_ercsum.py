#!/usr/bin/env python3
"""Unit tests for ercsum.py. Run: python3 tools/test_ercsum.py"""
import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from ercsum import group_item, main, parse

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


    def _run(self, text, *flags):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "erc.rpt"
            p.write_text(text)
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = main([str(p), *flags])
            return code, out.getvalue(), err.getvalue()

    def test_main_ok_and_lists_connector_pin_numbers(self):
        code, out, _ = self._run(REPORT, "--items")
        self.assertEqual(code, 0)
        self.assertIn("1 × J1 pins (3)", out)

    def test_main_fails_on_count_mismatch(self):
        code, _, err = self._run(REPORT.replace("Errors 3", "Errors 4"))
        self.assertEqual(code, 1)
        self.assertIn("don't match", err)

    def test_main_fails_without_totals_line(self):
        code, _, err = self._run(REPORT.replace(" ** ERC messages: 4  Errors 3  Warnings 1", ""))
        self.assertEqual(code, 1)
        self.assertIn("no 'ERC messages", err)


if __name__ == "__main__":
    unittest.main()
