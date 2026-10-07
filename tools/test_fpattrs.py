#!/usr/bin/env python3
"""Unit tests for fpattrs.py's text helpers (no pcbnew needed).

Run: python3 tools/test_fpattrs.py. The pcbnew-backed paths (reading footprints, choosing the courtyard) are
checked by running the tool with --write and then fpextract.py --verify on KiCad's Python."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fpattrs import MM, fmt, insert_text  # noqa: E402

FP = """(footprint "X"
\t(version 20241229)
\t(layer "F.Cu")
\t(property "Reference" "REF**"
\t\t(at 0 0 0)
\t)
\t(fp_line
\t\t(start 0 0)
\t\t(end 1 0)
\t)
\t(pad "1" smd rect
\t\t(at -0.85 0 90)
\t)
)"""


class TestFpAttrs(unittest.TestCase):
    def test_fmt(self):
        self.assertEqual(fmt(1_700_000), "1.7")
        self.assertEqual(fmt(-1_050_000), "-1.05")
        self.assertEqual(fmt(0), "0")
        self.assertEqual(fmt(MM), "1")

    def test_attr_goes_before_first_graphic(self):
        out = insert_text(FP, "smd", None).split("\n")
        self.assertEqual(out[out.index("\t(attr smd)") + 1], "\t(fp_line")
        self.assertLess(out.index("\t)"), out.index("\t(attr smd)"))      # after the property block

    def test_courtyard_goes_before_first_pad(self):
        out = insert_text(FP, None, (-1_700_000, -1_050_000, 1_700_000, 1_050_000))
        lines = out.split("\n")
        self.assertEqual(out.count('(layer "F.CrtYd")'), 4)
        self.assertLess(max(i for i, l in enumerate(lines) if "F.CrtYd" in l), lines.index('\t(pad "1" smd rect'))
        self.assertIn("\t\t(start -1.7 -1.05)", lines)
        self.assertIn("\t\t\t(width 0.05)", lines)
        self.assertEqual(out.count("("), out.count(")"))

    def test_nothing_to_do(self):
        self.assertEqual(insert_text(FP, None, None), FP)


if __name__ == "__main__":
    unittest.main()
