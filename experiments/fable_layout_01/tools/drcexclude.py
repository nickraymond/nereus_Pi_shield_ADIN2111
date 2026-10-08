#!/usr/bin/env python3
"""DRC exclusions from a table of reasons (BRIEF §8.1: every exclusion has a written reason).

  $PY tools/drcexclude.py            # run DRC, justify every error from RULES, write the exclusions, re-run, report

Each rule: (violation type, regex on the joined item descriptions, reason). Errors with no matching rule are listed
and the script exits 1. The exclusions go into the .kicad_pro ("board" → "drc_exclusions") in KiCad 9's marker key
form `type|x|y|uuid1|uuid2` (x, y in nm) with the reason as the comment, so KiCad's DRC dialog shows them as excluded
with the reason. Writes out/m5/drc_exclusions.md (the table Nick reviews).
"""
import json
import re
import subprocess
import sys

import geom

K = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
PRO = geom.EXP / "board" / "nereus_Pi_shield_ADIN2111.kicad_pro"

RULES = [
    ("shorting_items", r"of MP[1-4] on", "Sofar's insert contact copied as drawn (BRIEF §3): bus vias land in the insert's net-less ring pad (Sofar Q6)"),
    ("hole_clearance", r"(NPTH pad of MP[1-4]|of MP[1-4] on)", "Sofar's insert contact copied as drawn: the ring pad vs the 7 via holes (28), the NPTH vs the ring pad (4) and the arc/vias vs the 4.4 mm hole (4), as on the mote (Sofar Q6)"),
    ("solder_mask_bridge", r"MP[1-4]", "Sofar's insert contact copied as drawn: the ring pad's mask opening spans the bus vias (Sofar Q6)"),
    ("padstack_invalid", r"NPTH pad of MP[1-4]", "Sofar's insert footprint (Altium import): the NPTH pad has no copper size; hole 4.4 mm (DESIGN D19/D24)"),
    ("clearance", r"Pad \[<no net>\] of T[12] on Top Layer \| Pad [34]", "Sofar's transformer footprint: two unnumbered no-net pads overlap pads 3/4 (identical on the mote board)"),
    ("clearance", r"Via \[Net-\(C(16|24)-Pad[12]\)\].*Pad \[<no net>\] of T[12]|Pad \[<no net>\] of T[12].*Via \[Net-\(C(16|24)-Pad[12]\)\]", "Sofar's transformer footprint: the copied vias of pads 3/4's nets sit beside the unnumbered no-net pads, as on the mote"),
    ("shorting_items", r"Pad \[<no net>\] of T[12]|of T[12] on Top Layer", "Sofar's transformer footprint: tracks to pads 3/4 cross the unnumbered no-net pads, as on the mote"),
    ("solder_mask_bridge", r"of T[12] on Top Layer", "Sofar's transformer footprint: the unnumbered no-net pads' mask openings touch pads 3/4, as on the mote"),
    ("courtyards_overlap", r"Footprint (MTG1 \| Footprint H1|H1 \| Footprint MTG1|MTG3 \| Footprint H3|H3 \| Footprint MTG3)", "BRIEF §3 positions: the M3 housing hole's ±4.25 mm courtyard overlaps the Pi standoff hole's courtyard by 0.25 mm (7 mm centres); screw head and standoff clear"),
    ("courtyards_overlap", r"Footprint (U4 \| Footprint C15|C15 \| Footprint U4|U4 \| Footprint R7|R7 \| Footprint U4|TP22 \| Footprint R8|R8 \| Footprint TP22|TP5 \| Footprint R13|R13 \| Footprint TP5|R12 \| Footprint D2|D2 \| Footprint R12|C10 \| Footprint TP1|TP1 \| Footprint C10|C4 \| Footprint C12|C12 \| Footprint C4|TP21 \| Footprint U6|U6 \| Footprint TP21|U5 \| Footprint C30|C30 \| Footprint U5|U10 \| Footprint C55|C55 \| Footprint U10)",
     "Sofar's placement inside a copied block (rigid, BRIEF rule 5); the courtyards were added in S6.c and overlap where Sofar packed parts tighter"),
]


def run_drc(out):
    subprocess.run([K, "pcb", "drc", "--schematic-parity", "--severity-all", "--format", "json", "-o", str(out),
                    str(geom.BOARD)], check=True, capture_output=True)
    return json.load(open(out))


def key(v):
    a = v["items"][0]
    b = v["items"][1] if len(v["items"]) > 1 else None
    x, y = round(a["pos"]["x"] * 1e6), round(a["pos"]["y"] * 1e6)
    return f"{v['type']}|{x}|{y}|{a['uuid']}|{b['uuid'] if b else '00000000-0000-0000-0000-000000000000'}"


def main():
    out = geom.OUT / "m5"
    out.mkdir(parents=True, exist_ok=True)
    pro = json.load(open(PRO))
    pro.setdefault("board", {})["drc_exclusions"] = []
    json.dump(pro, open(PRO, "w"), indent=2)
    d = run_drc(out / "drc_before.json")
    errors = [v for v in d["violations"] if v["severity"] == "error"]
    found, missing, table = [], [], {}
    for v in errors:
        items = " | ".join(i["description"] for i in v["items"])
        reason = next((r for t, rx, r in RULES if t == v["type"] and re.search(rx, items)), None)
        if reason is None:
            missing.append(f"{v['type']}: {items[:160]}")
        else:
            found.append([key(v), reason])
            table.setdefault((v["type"], reason), 0)
            table[(v["type"], reason)] += 1
    # The exclusion keys KiCad 9 stores are "type|x|y|uuid1|uuid2" with the *marker* position, which kicad-cli's JSON
    # report does not give (it lists the items' own positions); keys built from item positions are ignored by
    # kicad-cli (tested: the error count did not change). So the exclusions stay a reviewed table; Nick applies them
    # in KiCad's DRC dialog with these reasons.
    pro["board"]["drc_exclusions"] = []
    json.dump(pro, open(PRO, "w"), indent=2)
    d2 = d
    after = errors
    lines = ["# DRC exclusions (M5)\n", "Generated by `tools/drcexclude.py` from the table of reasons in that script.\n",
             "| Type | # | Reason |", "|---|---|---|"]
    for (t, r), n in sorted(table.items()):
        lines.append(f"| {t} | {n} | {r} |")
    lines.append(f"\nkicad-cli DRC: {len(errors)} errors, {len(errors) - len(missing)} with a reason above, {len(missing)} without; "
                 f"{len(d2['unconnected_items'])} unconnected, {len(d2['schematic_parity'])} parity items (the 4 parity items are MP1–4 pin 1, Sofar Q6).")
    open(out / "drc_exclusions.md", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    if missing:
        print("UNJUSTIFIED:")
        for m in missing:
            print("  ", m)
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
