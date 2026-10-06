#!/usr/bin/env python3
"""Unit tests for fpextract.py's pure helpers (no pcbnew needed).

Run: python3 tools/test_fpextract.py. The pcbnew-backed extract/verify paths
are exercised by running fpextract.py --verify on KiCad's Python."""
import unittest

from fpextract import RENUMBER_SMD, _close, choose_instance, pad_distances, renumbered


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

    def test_renumbered_only_touches_listed_smd_pads(self):
        fix = RENUMBER_SMD["78614015360-Footprint-2"]
        self.assertEqual(renumbered("", True, fix), "1")      # the insert's SMD pad
        self.assertEqual(renumbered("", False, fix), "")      # its NPTH hole stays unnumbered
        self.assertEqual(renumbered("2", True, fix), "2")
        self.assertEqual(renumbered("", True, None), "")      # other footprints untouched

    def test_close_tolerance(self):
        self.assertTrue(_close((1.714, 4.255), (1.715, 4.255)))
        self.assertFalse(_close((1.714,), (1.814,)))
        self.assertFalse(_close((1, 2), (1,)))


if __name__ == "__main__":
    unittest.main()
