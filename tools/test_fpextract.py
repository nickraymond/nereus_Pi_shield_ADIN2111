#!/usr/bin/env python3
"""Unit tests for fpextract.py's pure helpers (no pcbnew needed).

Run: python3 tools/test_fpextract.py. The pcbnew-backed extract/verify paths
are exercised by running fpextract.py --verify on KiCad's Python."""
import unittest

from fpextract import _close, choose_instance, pad_distances


class FpextractTest(unittest.TestCase):
    def test_prefers_a_front_side_instance(self):
        self.assertEqual(choose_instance([("b1", True), ("f1", False)]), ("f1", False))
        self.assertEqual(choose_instance([("b1", True), ("b2", True)]), ("b1", True))

    def test_pad_distances_ignore_rotation_and_mirror(self):
        pts = [(0, 0), (1, 0), (0, 2)]
        rotated = [(0, 0), (0, 1), (-2, 0)]
        mirrored = [(0, 0), (-1, 0), (0, 2)]
        self.assertEqual(pad_distances(pts), pad_distances(rotated))
        self.assertEqual(pad_distances(pts), pad_distances(mirrored))
        self.assertNotEqual(pad_distances(pts), pad_distances([(0, 0), (1.1, 0), (0, 2)]))

    def test_close_tolerance(self):
        self.assertTrue(_close((1.714, 4.255), (1.715, 4.255)))
        self.assertFalse(_close((1.714,), (1.814,)))
        self.assertFalse(_close((1, 2), (1,)))


if __name__ == "__main__":
    unittest.main()
