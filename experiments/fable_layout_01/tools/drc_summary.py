#!/usr/bin/env python3
"""kicad-cli DRC → out/<m>/drc.json and drc_summary.txt (counts per type and severity, unconnected, parity).

  $PY tools/drc_summary.py m4
"""
import collections
import json
import subprocess
import sys

import geom

K = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"


def main(stage):
    out = geom.OUT / stage
    out.mkdir(parents=True, exist_ok=True)
    subprocess.run([K, "pcb", "drc", "--schematic-parity", "--severity-all", "--format", "json", "-o", str(out / "drc.json"),
                    str(geom.BOARD)], check=True, capture_output=True)
    d = json.load(open(out / "drc.json"))
    c = collections.Counter((v["type"], v["severity"]) for v in d["violations"])
    lines = [f"{n} {k}" for k, n in sorted(c.items())]
    lines.append(f"unconnected_items: {len(d['unconnected_items'])}")
    lines.append(f"schematic_parity: {len(d['schematic_parity'])}")
    errors = sum(n for k, n in c.items() if k[1] == "error")
    warnings = sum(n for k, n in c.items() if k[1] == "warning")
    lines.append(f"errors: {errors}  warnings: {warnings}")
    for u in d["unconnected_items"]:
        lines.append("open: " + " | ".join(i["description"][:70] for i in u["items"]))
    (out / "drc_summary.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "m4")
