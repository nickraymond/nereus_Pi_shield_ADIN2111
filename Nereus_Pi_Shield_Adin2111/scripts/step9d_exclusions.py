"""Step 9d: DRC exclusions for the 16 GND vias inside Sofar's keepout 'NoConnect_Pwr_MCU' under U1.

They are the ADIN2111's thermal vias, identical to the mote; Nick decided to keep them (DESIGN D34, 2026-11-10).
Plain Python 3, KiCad closed:  python3 step9d_exclusions.py <drc report .json from kicad-cli>
Each exclusion is KiCad's marker string "type|x nm|y nm|item uuid|second item uuid" plus a comment, written to
board.design_settings.drc_exclusions in the project file. Nothing else in the project file changes.
"""
import json
import os
import sys

PRO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Nereus_Pi_Shield_Adin2111.kicad_pro")
PRO = os.environ.get("NRR_PRO", PRO)
COMMENT = "GND thermal via under U1 in Sofar's keepout, same as the mote; kept (DESIGN D34)"
NIL = "00000000-0000-0000-0000-000000000000"

drc = json.load(open(sys.argv[1]))
hits = [v for v in drc["violations"] if v["type"] == "items_not_allowed"]
assert len(hits) == 16, len(hits)
rows = []
for v in hits:
    assert "NoConnect_Pwr_MCU" in v["description"] and len(v["items"]) == 1, v
    it = v["items"][0]
    assert it["description"].startswith("Via [GND]"), it
    assert 151.5 < it["pos"]["x"] < 156.5 and 110.5 < it["pos"]["y"] < 115.5, it      # U1's exposed pad
    rows.append(["items_not_allowed|%d|%d|%s|%s" % (round(it["pos"]["x"] * 1e6), round(it["pos"]["y"] * 1e6), it["uuid"], NIL), COMMENT])
rows.sort()
pro = json.load(open(PRO, encoding="utf-8"))
have = pro["board"]["design_settings"]["drc_exclusions"]
if have == rows:
    sys.exit("step 9d already applied; nothing done")
assert have == [], have
pro["board"]["design_settings"]["drc_exclusions"] = rows
with open(PRO, "w", encoding="utf-8") as f:
    json.dump(pro, f, indent=2, ensure_ascii=False)
    f.write("\n")
print("  %d exclusions written" % len(rows))
