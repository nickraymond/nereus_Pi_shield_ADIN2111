#!/usr/bin/env python3
"""The board's numbers in one place (read only): out/m4/summary.json from the check outputs, so REPORT.md, the review
page and the before/after page quote the same figures (nothing typed by hand).

  $PY tools/summary.py            (after tools/check_rules.py out/m4/rules.md, tools/drc_summary.py m4, tools/drcexclude.py,
                                   tools/dfm.py check m4, tools/check_fixed.py, tools/blockcheck.py out/m4/blockcheck.md)
"""
import hashlib
import json
import re
import subprocess

import geom

OUT = geom.OUT / "m4"


def main():
    S = {}
    S["board_md5"] = hashlib.md5(open(geom.BOARD, "rb").read()).hexdigest()
    S["commit"] = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=geom.EXP).stdout.strip()
    S["size_mm"] = [geom.OUTLINE["x1"] - geom.OUTLINE["x0"], geom.OUTLINE["y1"] - geom.OUTLINE["y0"]]
    r = json.load(open(OUT / "routing.json"))
    S["pairs"] = {p["net"]: {"mm": p["total_mm"], "limit": p["limit_mm"], "vias": p["vias"], "ok": p["ok"]} for p in r["pairs"] if "net" in p}
    S["failed"] = [{"net": f["net"].rsplit("/", 1)[-1], "why": f["why"]} for f in r["failed"]]
    S["routed_mm"] = {x["net"]: x["length_new_mm"] for x in r["routed"]}
    S["stitch_vias"] = len(r["stitch"])
    S["routing_notes"] = [n for n in r["notes"] if "pair port" in n and "parity" in n or "grid" in n or "total" in n or "fan-out" in n or "margin" in n]
    txt = (OUT / "drc_summary.txt").read_text()
    S["drc"] = {"errors": int(re.search(r"errors: (\d+)", txt).group(1)), "warnings": int(re.search(r"warnings: (\d+)", txt).group(1)),
                "unconnected": int(re.search(r"unconnected_items: (\d+)", txt).group(1)), "parity": int(re.search(r"schematic_parity: (\d+)", txt).group(1)),
                "by_type": dict(re.findall(r"^(\d+) \('(\w+)'", txt, re.M) and [(k, int(n)) for n, k in re.findall(r"^(\d+) \('(\w+)'", txt, re.M)])}
    ex = (geom.OUT / "m5" / "drc_exclusions.md").read_text()
    m = re.search(r"kicad-cli DRC: (\d+) errors, (\d+) with a reason above, (\d+) without", ex)
    S["drc_exclusions"] = {"errors": int(m.group(1)), "justified": int(m.group(2)), "unjustified": int(m.group(3))}
    rules = (OUT / "rules.md").read_text()
    S["rules"] = {"below_class": int(re.search(r"Below the class minimum[^:]*: (\d+)", rules).group(1)),
                  "thin_links": int(re.search(r"Links routed at 0.15 mm[^:]*: (\d+)", rules).group(1)),
                  "clearance_items": int(re.search(r"Violations of the class clearance[^:]*: (\d+)", rules).group(1)),
                  "kelvin": re.findall(r"\| (U4\.\d ↔ R8\.\d[^|]*)\| (yes|NO) \|", rules)}
    bc = (OUT / "blockcheck.md").read_text()
    S["blockcheck"] = {"missing": int(re.search(r"(\d+) missing", bc).group(1)) if re.search(r"(\d+) missing", bc) else None,
                       "trimmed": int(re.search(r"(\d+) trimmed", bc).group(1)) if re.search(r"(\d+) trimmed", bc) else None}
    if (OUT / "dfm.json").exists():
        d = json.load(open(OUT / "dfm.json"))
        S["dfm"] = {k: v[2] for k, v in d.items() if isinstance(v, list) and len(v) == 3 and isinstance(v[2], bool)}
        S["dfm_pass"] = sum(1 for v in S["dfm"].values() if v)
        S["dfm_fail"] = sorted(k for k, v in S["dfm"].items() if not v)
    if (geom.OUT / "m2" / "dfm_fix.json").exists():
        S["dfm_fix"] = json.load(open(geom.OUT / "m2" / "dfm_fix.json"))
    # pair segment counts (the staircase measure, QE round 2 N3)
    import pcbnew
    b = geom.load()
    segs = {}
    for t in b.GetTracks():
        n = t.GetNetname().rsplit("/", 1)[-1]
        if "DATA" in n and t.GetClass() == "PCB_TRACK":
            segs[n] = segs.get(n, 0) + 1
    S["pair_segments"] = segs
    json.dump(S, open(OUT / "summary.json", "w"), indent=1)
    print(json.dumps({k: S[k] for k in ("commit", "board_md5", "size_mm", "pairs", "pair_segments", "drc", "drc_exclusions", "rules", "blockcheck", "failed")}, indent=1))
    if "dfm_pass" in S:
        print("DFM", S["dfm_pass"], "pass; fail:", S["dfm_fail"])


if __name__ == "__main__":
    main()
