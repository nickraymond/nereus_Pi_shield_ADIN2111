#!/usr/bin/env python3
"""Unit tests for netcheck.py on tiny hand-written fixtures. Run: python3 tools/test_netcheck.py"""
import unittest

from netcheck import compare, netlist_connectivity, pcb_connectivity

PCB = """(kicad_pcb
  (footprint "R" (property "Reference" "R1")
    (pad "1" smd rect (net 1 "A")) (pad "2" smd rect (net 2 "B")))
  (footprint "R" (property "Reference" "R2")
    (pad "1" smd rect (net 1 "A")) (pad "2" smd rect (net 2 "B")) (pad "" np_thru_hole circle))
  (footprint "TP" (property "Reference" "TP1")
    (pad "1" smd circle (net 1 "A")))
  (footprint "U" (property "Reference" "U9")
    (pad "1" smd rect (net 3 "C")))
)"""


def netlist(*nets):
    body = "".join(f'(net (code "{i}") (name "{name}") '
                   + "".join(f'(node (ref "{n.split(".")[0]}") (pin "{n.split(".")[1]}"))' for n in nodes)
                   + ")" for i, (name, nodes) in enumerate(nets, 1))
    return f"(export (nets {body}))"


def run(sch):
    pcb_nets, no_net = pcb_connectivity(PCB)
    return compare(pcb_nets, no_net, netlist_connectivity(sch))


class NetcheckTest(unittest.TestCase):
    def test_parses_pcb_and_skips_unnumbered_pads(self):
        nets, no_net = pcb_connectivity(PCB)
        self.assertEqual(nets["A"], {"R1.1", "R2.1", "TP1.1"})
        self.assertEqual(no_net, set())

    def test_match_ignores_names_and_unshared_parts(self):
        r = run(netlist(("/x/A", ["R1.1", "R2.1", "TP1.1"]), ("B2", ["R1.2", "R2.2", "J9.1"])))
        self.assertEqual(r["matched"], ["A", "B"])
        self.assertFalse(r["opens"] or r["shorts"])
        self.assertEqual(r["only_pcb"], ["U9"])
        self.assertEqual(r["only_sch"], ["J9"])

    def test_open_detected(self):
        r = run(netlist(("A", ["R1.1", "R2.1"]), ("unconnected-(TP1-Pad1)", ["TP1.1"]),
                        ("B", ["R1.2", "R2.2"])))
        self.assertEqual(list(r["opens"]), ["A"])
        self.assertFalse(r["shorts"])

    def test_short_detected(self):
        r = run(netlist(("AB", ["R1.1", "R2.1", "TP1.1", "R1.2", "R2.2"])))
        self.assertEqual(list(r["shorts"]), ["AB"])

    def test_unpaired_pins(self):
        r = run(netlist(("A", ["R1.1", "R2.1", "TP1.1", "TP1.2"]), ("B", ["R1.2"])))
        self.assertEqual(r["pins_not_in_copper"], ["TP1.2"])
        self.assertEqual(r["pads_not_in_schematic"], ["R2.2"])


if __name__ == "__main__":
    unittest.main()
