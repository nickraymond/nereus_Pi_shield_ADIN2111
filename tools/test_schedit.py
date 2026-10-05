#!/usr/bin/env python3
"""Unit tests for schedit.py. Run: python3 tools/test_schedit.py"""
import re
import unittest

from midwire import WIRE
from schedit import add_label, add_no_connect, add_symbol, add_wire, copy_block, delete, next_ref, set_properties

LIB = ('\t(lib_symbols\n'
       '\t\t(symbol "lib:R"\n\t\t\t(symbol "R_0_1"\n'
       '\t\t\t\t(pin passive line\n\t\t\t\t\t(at 0 0 0)\n\t\t\t\t\t(number "1")\n\t\t\t\t)\n'
       '\t\t\t\t(pin passive line\n\t\t\t\t\t(at 10 0 180)\n\t\t\t\t\t(number "2")\n\t\t\t\t)\n'
       '\t\t\t)\n\t\t)\n'
       '\t\t(symbol "lib:GND"\n\t\t\t(power)\n\t\t\t(symbol "GND_0_1"\n'
       '\t\t\t\t(pin power_in line\n\t\t\t\t\t(at 0 0 0)\n\t\t\t\t\t(number "1")\n\t\t\t\t)\n'
       '\t\t\t)\n\t\t)\n\t)\n')


def sym(lib, ref, x, y):
    return (f'\t(symbol\n\t\t(lib_id "lib:{lib}")\n\t\t(at {x} {y} 0)\n\t\t(unit 1)\n'
            f'\t\t(property "Reference" "{ref}"\n\t\t)\n'
            f'\t\t(instances\n\t\t\t(project ""\n\t\t\t\t(path "/a"\n\t\t\t\t\t(reference "{ref}")\n'
            '\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n')


def wire(x1, y1, x2, y2, u):
    return (f'\t(wire\n\t\t(pts\n\t\t\t(xy {x1} {y1}) (xy {x2} {y2})\n\t\t)\n'
            f'\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)\n\t\t(uuid "{u}")\n\t)\n')


def label(name, x, y):
    return f'\t(label "{name}"\n\t\t(at {x} {y} 0)\n\t\t(uuid "l-{name}")\n\t)\n'


def junction(x, y):
    return f'\t(junction\n\t\t(at {x} {y})\n\t\t(diameter 0)\n\t\t(color 0 0 0 0)\n\t\t(uuid "j{x}")\n\t)\n'


# P1 (doomed, pins at 0,0 and 10,0). Island A: P1.1 -> GND symbol only (dies whole).
# Island B: P1.2 -> stub -> T at (20,0) -> R2.1 at (20,10) and label KEEP at (30,0).
SHEET = ('(kicad_sch\n' + LIB
         + junction(20, 0)
         + wire(0, 0, 0, -10, "wa") + wire(10, 0, 20, 0, "wb1") + wire(20, 0, 30, 0, "wb2") + wire(20, 0, 20, 10, "wb3")
         + label("DEAD", 0, -5) + label("KEEP", 30, 0)
         + sym("R", "P1", 0, 0) + sym("GND", "#PWR01", 0, -10) + sym("R", "R2", 20, 10)
         + '\t(sheet_instances\n\t)\n)\n')


def wires(text):
    return sorted(m.groups()[:4] for m in WIRE.finditer(text))


class DeleteTest(unittest.TestCase):
    def setUp(self):
        self.out, self.rep = delete(SHEET, refs={"P1"}, labels={"DEAD"})

    def test_part_label_and_orphan_power_symbol_removed(self):
        self.assertEqual(self.rep["parts"], ["P1"])
        self.assertEqual(self.rep["labels"], ["DEAD"])
        self.assertEqual(self.rep["power_symbols"], ["#PWR01"])
        self.assertNotIn('"Reference" "P1"', self.out)
        self.assertNotIn("#PWR01", self.out)

    def test_dead_island_and_stub_removed_kept_wiring_stays(self):
        self.assertEqual(wires(self.out), [("20", "0", "20", "10"), ("20", "0", "30", "0")])
        self.assertIn('(label "KEEP"', self.out)
        self.assertIn('"Reference" "R2"', self.out)

    def test_junction_with_two_connections_dropped(self):
        self.assertEqual(self.rep["junctions"], 1)
        self.assertNotIn("(junction", self.out)

    def test_label_part_way_along_a_stub_is_kept_on_a_shortened_wire(self):
        # P1.2 at (10,0) -> wire to (40,0) with label MID at (25,0) and R2.1 moved to (40,0)
        s = ('(kicad_sch\n' + LIB + wire(10, 0, 40, 0, "w") + label("MID", 25, 0)
             + sym("R", "P1", 0, 0) + sym("R", "R2", 40, 0) + '\t(sheet_instances\n\t)\n)\n')
        out, _ = delete(s, refs={"P1"})
        self.assertEqual(wires(out), [("25", "0", "40", "0")])
        self.assertIn('(label "MID"', out)

    def test_untouched_island_left_alone(self):
        extra = SHEET.replace("\t(sheet_instances", wire(100, 100, 110, 100, "lonely") + "\t(sheet_instances")
        out, _ = delete(extra, refs={"P1"}, labels={"DEAD"})
        self.assertIn(("100", "100", "110", "100"), wires(out))


class AddTest(unittest.TestCase):
    def test_add_symbol_has_pins_and_instance(self):
        out, u = add_symbol(SHEET, "lib:R", "R9", "1k", 50, 50, sheet_path="/a/b")
        block = out[out.index(f'(uuid "{u}")') - 200:]
        self.assertIn('(property "Reference" "R9"', out)
        self.assertEqual(len(re.findall(r'\(pin "\d"\n\t\t\t\(uuid', block.split("(instances")[0])), 2)
        self.assertIn('(path "/a/b"\n\t\t\t\t\t(reference "R9")', out)

    def test_add_wire_label_nc_and_next_ref(self):
        out = add_no_connect(add_label(add_wire(SHEET, 1, 2, 3, 2), "N1", 1, 2), 5, 5)
        self.assertIn(("1", "2", "3", "2"), wires(out))
        self.assertIn('(label "N1"', out)
        self.assertIn("(no_connect\n\t\t(at 5 5)", out)
        self.assertEqual(next_ref([SHEET], "#PWR"), "#PWR02")
        self.assertEqual(next_ref([SHEET], "J"), "J1")


class CopyTest(unittest.TestCase):
    def setUp(self):
        n = iter(["#PWR09"])
        self.out, self.rep = copy_block(SHEET, (15, -1, 35, 11), 0, 50, {"R2": "R12"},
                                        {"KEEP": "KEEP2"}, lambda: next(n))

    def test_symbols_wires_labels_copied_and_renamed(self):
        self.assertEqual(self.rep["symbols"], {"R2": "R12"})
        self.assertIn('(property "Reference" "R12"', self.out)
        self.assertIn('(reference "R12")', self.out)
        self.assertIn('(property "Reference" "R2"', self.out)  # original kept
        self.assertIn(("20", "50", "20", "60"), wires(self.out))
        self.assertIn(("20", "50", "30", "50"), wires(self.out))
        self.assertNotIn(("10", "50", "20", "50"), wires(self.out))  # one end outside the box
        self.assertIn('(label "KEEP2"\n\t\t(at 30 50 0)', self.out)
        self.assertIn("(junction\n\t\t(at 20 50)", self.out)

    def test_uuids_are_new(self):
        uu = re.findall(r'\(uuid "([^"]*)"\)', self.out)
        self.assertEqual(len(uu), len(set(uu)))

    def test_unmapped_part_in_box_is_an_error(self):
        with self.assertRaises(ValueError):
            copy_block(SHEET, (15, -1, 35, 11), 0, 50, {}, {}, lambda: "#PWR09")

    def test_set_properties(self):
        s = SHEET.replace('(property "Reference" "R2"\n\t\t)\n',
                          '(property "Reference" "R2"\n\t\t)\n\t\t(property "OLD" "x"\n\t\t\t(at 0 0 0)\n\t\t)\n')
        out = set_properties(s, "R2", {"Reference": "R2", "NEW": "y"}, keep_only=())
        self.assertNotIn('"OLD"', out)
        self.assertIn('(property "NEW" "y"', out)

    def test_set_properties_handles_escaped_quotes(self):
        # QE S4 F1: a value like 0.039\"(1.00mm) used to be skipped silently
        s = SHEET.replace('(property "Reference" "R2"\n\t\t)\n',
                          '(property "Reference" "R2"\n\t\t)\n\t\t(property "SIZE" "0.063\\"Lx0.031\\"W"\n\t\t\t(at 0 0 0)\n\t\t)\n')
        self.assertIn('\\"Lx', s)
        out = set_properties(s, "R2", {}, keep_only=())
        self.assertNotIn('"SIZE"', out)


if __name__ == "__main__":
    unittest.main()
