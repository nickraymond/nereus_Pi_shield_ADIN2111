"""Write JLC's limits and stackup into the project settings. No copper, footprint or zone is touched.

Sources, read 2026-11-10 10:36 AM PT:
  https://jlcpcb.com/capabilities/pcb-capabilities   (limits)
  https://jlcpcb.com/impedance                        (stackup JLC06161H-3313: 1.6 mm, 1 oz outer, 0.5 oz inner)

Three files change, all in one commit so `git revert` of that commit is the rollback:
  nick_raw_routing.kicad_pro   board setup constraints
  nick_raw_routing.kicad_dru   two custom rules for through-hole pads
  nick_raw_routing.kicad_pcb   stackup and solder-mask minimum web (setup block only)

Old and new values: docs/design-review/jlc_rules_2026-11.md
Run with plain python3, then scripts/normalize.py with KiCad's python.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PRO = os.path.join(HERE, "..", "nick_raw_routing.kicad_pro")
DRU = os.path.join(HERE, "..", "nick_raw_routing.kicad_dru")
PCB = os.path.join(HERE, "..", "nick_raw_routing.kicad_pcb")

# name: (value before, value after)
RULES = {
    "min_clearance": (0.0, 0.10),              # JLC multilayer 1 oz: 0.09
    "min_track_width": (0.0, 0.10),            # JLC multilayer 1 oz: 0.09
    "min_via_diameter": (0.5, 0.45),           # JLC min 0.25; a 0.2 hole costs extra only under 0.45
    "min_through_hole_diameter": (0.3, 0.2),   # JLC min 0.15, preferred 0.2
    "min_hole_to_hole": (0.25, 0.2),           # JLC via hole to hole 0.2 (pad holes: custom rule below)
    "min_silk_clearance": (0.0, 0.15),         # JLC pad to silkscreen 0.15
    "min_text_height": (0.8, 1.0),             # JLC 1.0
    "min_text_thickness": (0.08, 0.15),        # JLC 0.15
}
# unchanged on purpose: min_hole_clearance 0.25 (JLC via hole to track 0.2), min_copper_edge_clearance 0.5 (JLC 0.2),
# min_via_annular_width 0.1 (JLC: via diameter >= hole + 0.1, i.e. 0.05)

DRU_ADD = '''
   (rule "JLC through-hole pad: hole to copper"
     (condition "A.Type == 'Pad' && A.Pad_Type == 'Through-hole'")
     (constraint hole_clearance (min 0.3mm)))
   (rule "JLC pad hole to pad hole"
     (condition "A.Type == 'Pad' && B.Type == 'Pad'")
     (constraint hole_to_hole (min 0.45mm)))
'''

def cu(name, t):
    return '\t\t\t(layer "%s"\n\t\t\t\t(type "copper")\n\t\t\t\t(thickness %s)\n\t\t\t)\n' % (name, t)

def di(n, kind, t, material, er):
    return ('\t\t\t(layer "dielectric %d"\n\t\t\t\t(type "%s")\n\t\t\t\t(thickness %s)\n\t\t\t\t(material "%s")\n'
            '\t\t\t\t(epsilon_r %s)\n\t\t\t\t(loss_tangent 0.02)\n\t\t\t)\n' % (n, kind, t, material, er))

# JLC06161H-3313. Mask 0.6 mil over traces, Er 3.8; prepreg 3313 Er 4.1, 2116 Er 4.16; core Er 4.6 (JLC's page).
# loss_tangent 0.02 is KiCad's default, not a JLC figure.
STACKUP = (
    '\t\t(stackup\n'
    '\t\t\t(layer "F.SilkS"\n\t\t\t\t(type "Top Silk Screen")\n\t\t\t)\n'
    '\t\t\t(layer "F.Paste"\n\t\t\t\t(type "Top Solder Paste")\n\t\t\t)\n'
    '\t\t\t(layer "F.Mask"\n\t\t\t\t(type "Top Solder Mask")\n\t\t\t\t(thickness 0.01524)\n\t\t\t\t(epsilon_r 3.8)\n\t\t\t)\n'
    + cu("F.Cu", 0.035) + di(1, "prepreg", 0.0994, "3313", 4.1)
    + cu("In1.Cu", 0.0152) + di(2, "core", 0.55, "FR4", 4.6)
    + cu("In2.Cu", 0.0152) + di(3, "prepreg", 0.1088, "2116", 4.16)
    + cu("In3.Cu", 0.0152) + di(4, "core", 0.55, "FR4", 4.6)
    + cu("In4.Cu", 0.0152) + di(5, "prepreg", 0.0994, "3313", 4.1)
    + cu("B.Cu", 0.035)
    + '\t\t\t(layer "B.Mask"\n\t\t\t\t(type "Bottom Solder Mask")\n\t\t\t\t(thickness 0.01524)\n\t\t\t\t(epsilon_r 3.8)\n\t\t\t)\n'
    '\t\t\t(layer "B.Paste"\n\t\t\t\t(type "Bottom Solder Paste")\n\t\t\t)\n'
    '\t\t\t(layer "B.SilkS"\n\t\t\t\t(type "Bottom Silk Screen")\n\t\t\t)\n'
    '\t\t\t(copper_finish "ENIG")\n'
    '\t\t\t(dielectric_constraints no)\n'
    '\t\t)\n'
)

pro = json.load(open(PRO))
rules = pro["board"]["design_settings"]["rules"]
for name, (old, new) in RULES.items():
    assert rules[name] == old, (name, rules[name], old)
    rules[name] = new
with open(PRO, "w") as f:
    json.dump(pro, f, indent=2, ensure_ascii=False)
    f.write("\n")

dru = open(DRU).read()
assert "JLC" not in dru
open(DRU, "w").write(dru.rstrip("\n") + "\n" + DRU_ADD)

pcb = open(PCB).read()
anchor = "\t(setup\n\t\t(pad_to_mask_clearance 0.025)\n"
assert pcb.count(anchor) == 1 and "(stackup" not in pcb and "solder_mask_min_width" not in pcb
pcb = pcb.replace(anchor, "\t(setup\n" + STACKUP + "\t\t(pad_to_mask_clearance 0.025)\n\t\t(solder_mask_min_width 0.1)\n")
open(PCB, "w").write(pcb)
print("settings written; now run normalize.py with KiCad's python")
