#!/usr/bin/env python3
"""ERC exclusions from a reviewed table of reasons.

KiCad 9 stores each ERC exclusion in the .kicad_pro as [key, comment], where key is
"type|x|y|item-uuid|aux-uuid|sheet-path|item-sheet-path|aux-sheet-path" with x, y in
schematic internal units (100 nm) — see KiCad 9.0 eeschema/sch_marker.cpp,
SCH_MARKER::SerializeToString. The key moves with the item, so exclusions written by
hand go stale when a symbol is moved. This tool regenerates them from
docs/design-review/erc_justifications.csv (columns: type, item, reason; `item` is a
regex on kicad-cli's item description, e.g. "^Symbol FID\\d+ Hidden pin").

  python3 tools/ercexclude.py           check: every ERC error is justified and the
                                        .kicad_pro exclusions are current (exit 1 if not:
                                        an unjustified error, a stale or a missing exclusion)
  python3 tools/ercexclude.py --write   rewrite the .kicad_pro exclusions from the table

Runs ERC on a temporary copy with the exclusions cleared; never touches the schematic.
Python standard library only.
"""
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJ = "nereus_Pi_shield_ADIN2111"
PRO = ROOT / PROJ / f"{PROJ}.kicad_pro"
TABLE = ROOT / "docs/design-review/erc_justifications.csv"
KICAD = os.environ.get("KICAD_CLI", "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
NIL = "00000000-0000-0000-0000-000000000000"


def load_rules(path):
    with open(path, newline="") as f:
        rules = [(r["type"].strip(), re.compile(r["item"].strip()), r["reason"].strip()) for r in csv.DictReader(f)]
    if not rules:
        raise ValueError(f"{path}: no rules")
    return rules


def iu(json_coord):
    """kicad-cli 9 JSON positions are in units of 100 mm (FID1 at 229.87 mm prints 2.2987); IU = 100 nm."""
    return round(json_coord * 1e6)


def key(vtype, item, sheet_path):
    """The exclusion key KiCad 9 writes for a single-item violation on a placed item (checked: it matches)."""
    return f"{vtype}|{iu(item['pos']['x'])}|{iu(item['pos']['y'])}|{item['uuid']}|{NIL}|{sheet_path}|{sheet_path}|"


def errors(erc_json):
    """(type, items, sheet uuid path) for every error-severity violation."""
    out = []
    for sheet in erc_json["sheets"]:
        for v in sheet["violations"]:
            if v["severity"] == "error":
                out.append((v["type"], v["items"], sheet["uuid_path"]))
    return out


def justify(errs, rules):
    """Return ({key: reason}, [unjustified error descriptions])."""
    found, missing = {}, []
    for vtype, items, path in errs:
        item = items[0]
        reason = next((r for t, rx, r in rules if t == vtype and rx.search(item["description"])), None)
        if len(items) > 1:
            # Two-item errors carry a second uuid and sheet path whose key form isn't confirmed here:
            # exclude those in KiCad's ERC dialog by hand rather than write a key that never matches.
            missing.append(f"{vtype}: {item['description']} (+{len(items) - 1} item: exclude in KiCad by hand)")
        elif reason is None:
            missing.append(f"{vtype}: {item['description']}")
        else:
            found[key(vtype, item, path)] = reason
    return found, missing


def run_erc():
    with tempfile.TemporaryDirectory() as tmp:
        dst = Path(tmp) / PROJ
        shutil.copytree(ROOT / PROJ, dst, ignore=shutil.ignore_patterns("~*.lck", "*-backups"))
        pro = json.loads((dst / PRO.name).read_text())
        pro["erc"]["erc_exclusions"] = []
        (dst / PRO.name).write_text(json.dumps(pro, indent=2, ensure_ascii=False) + "\n")
        out = Path(tmp) / "erc.json"
        r = subprocess.run([KICAD, "sch", "erc", "--format", "json", "--severity-all", "-o", str(out),
                            str(dst / f"{PROJ}.kicad_sch")], capture_output=True, text=True)
        if r.returncode != 0 or not out.exists():
            raise RuntimeError(f"kicad-cli ERC failed: {r.stderr.strip() or r.stdout.strip()}")
        return json.loads(out.read_text())


def main(argv):
    write = "--write" in argv
    rules = load_rules(TABLE)
    found, missing = justify(errors(run_erc()), rules)
    pro = json.loads(PRO.read_text())
    current = {e[0] if isinstance(e, list) else e: (e[1] if isinstance(e, list) else "")
               for e in pro["erc"]["erc_exclusions"]}
    if write:
        pro["erc"]["erc_exclusions"] = [[k, found[k]] for k in sorted(found)]
        PRO.write_text(json.dumps(pro, indent=2, ensure_ascii=False) + "\n")
        current = found
    stale = sorted(set(current) - set(found))
    absent = sorted(set(found) - set(current))
    print(f"ercexclude: {len(found)} errors justified, {len(missing)} unjustified, "
          f"{len(stale)} stale / {len(absent)} missing exclusions")
    for m in missing:
        print(f"  unjustified  {m}")
    if stale or absent:
        print("  exclusions out of date (an item moved?): run python3 tools/ercexclude.py --write")
    return 1 if (missing or stale or absent) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
