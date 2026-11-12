#!/usr/bin/env python3
"""Sprint 10 (2026-11-12): rename the KiCad project from nick_raw_routing to Nereus_Pi_Shield_Adin2111.

Run once, on Nick's go ("make the changes"). Names only; no net, part, value, copper or silkscreen changes:
  - the four root files  nick_raw_routing.kicad_{pro,sch,pcb,dru} -> Nereus_Pi_Shield_Adin2111.*
  - the six sheet files  BM_Mote_1_* -> Nereus_Pi_Shield_Adin2111_* (SHEETS below)
  - in every .kicad_sch: (project "<old>" -> (project "<new>"  (the instance blocks hold every reference
                         designator and page number; a missed one loses the annotation)
                         (property "Sheetfile" "<old sheet>" -> the new sheet file
  - in the .kicad_pcb:   (sheetfile "<old sheet>") -> the new sheet file (footprint metadata, no geometry)
  - in the .kicad_pro:   its own file name, the root sheet's file name and name (2 places), PCBPARTNAME;
                         edited as text so the DRC exclusions, their comments and the JLC rules stay as they are
The script stops before writing if a count is not what it expects.

  python3 rename_project_2026_11.py            # dry run
  python3 rename_project_2026_11.py --write
Check afterwards: scripts/verify_against_freeze.py, ERC 39, DRC with parity, netlist against the one before.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
OLD, NEW = "nick_raw_routing", "Nereus_Pi_Shield_Adin2111"
SHEETS = {
    "BM_Mote_1_Master.kicad_sch": NEW + "_TopLevel.kicad_sch",
    "BM_Mote_1_ADIN2111.kicad_sch": NEW + "_ADIN2111.kicad_sch",
    "BM_Mote_1_Load.kicad_sch": NEW + "_LoadSwitch.kicad_sch",
    "BM_Mote_1_PoDL.kicad_sch": NEW + "_PoDL.kicad_sch",
    "BM_Mote_1_Power.kicad_sch": NEW + "_Power.kicad_sch",
    "BM_Mote_1_PowerMon.kicad_sch": NEW + "_PowerMonitor.kicad_sch",
}
ROOT_EXT = ("kicad_pro", "kicad_sch", "kicad_pcb", "kicad_dru")
OLD_PARTNAME = "nereus_Pi_shield_ADIN2111"


def read(p):
    with open(p, encoding="utf-8", newline="") as f:
        return f.read()


def write(p, t):
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(t)


def swap(text, old, new, expect=None, what=""):
    n = text.count(old)
    if expect is not None and n != expect:
        sys.exit(f"STOP, nothing written: {what}: expected {expect} of {old!r}, found {n}")
    return text.replace(old, new), n


def main():
    d = Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else HERE
    if (d / f"{NEW}.kicad_pro").exists() and not (d / f"{OLD}.kicad_pro").exists():
        print(f"already renamed: {d / (NEW + '.kicad_pro')} exists")
        return
    log, files = [], {}
    for p in sorted(d.glob("*.kicad_sch")):
        t = read(p)
        t, n = swap(t, f'(project "{OLD}"', f'(project "{NEW}"')
        others = set(re.findall(r'\(project "([^"]*)"', t)) - {NEW}
        if others:
            sys.exit(f"STOP, nothing written: {p.name} has instances of other projects: {sorted(others)}")
        log.append(f"{p.name}: {n} project instances")
        for old, new in SHEETS.items():
            t, k = swap(t, f'(property "Sheetfile" "{old}"', f'(property "Sheetfile" "{new}"')
            if k:
                log.append(f"{p.name}: Sheetfile {old} -> {new}")
        files[p] = t
    pcb = d / f"{OLD}.kicad_pcb"
    t = read(pcb)
    total = 0
    for old, new in SHEETS.items():
        t, k = swap(t, f'(sheetfile "{old}")', f'(sheetfile "{new}")')
        total += k
    unmapped = sorted({x for x in re.findall(r'\(sheetfile "([^"]*)"\)', t) if x not in SHEETS.values()})
    if unmapped:
        sys.exit(f"STOP, nothing written: board sheetfile values with no new name: {unmapped}")
    log.append(f"{pcb.name}: {total} sheetfile values")
    files[pcb] = t
    pro = d / f"{OLD}.kicad_pro"
    t = read(pro)
    t, _ = swap(t, f'"filename": "{OLD}.kicad_pro"', f'"filename": "{NEW}.kicad_pro"', 1, "meta.filename")
    t, _ = swap(t, f'"filename": "{OLD}.kicad_sch"', f'"filename": "{NEW}.kicad_sch"', 1, "root sheet file")
    t, _ = swap(t, f'"name": "{OLD}"', f'"name": "{NEW}"', 1, "root sheet name")
    t, _ = swap(t, f'      "{OLD}"\n', f'      "{NEW}"\n', 1, "sheets[0] name")
    t, _ = swap(t, f'"PCBPARTNAME": "{OLD_PARTNAME}"', f'"PCBPARTNAME": "{NEW}"', 1, "PCBPARTNAME")
    if OLD in t:
        sys.exit(f"STOP, nothing written: {OLD} is still in {pro.name}")
    log.append(f"{pro.name}: 5 values")
    files[pro] = t
    print("\n".join(log))
    if "--write" not in sys.argv:
        print("dry run, nothing written")
        return
    for p, t in files.items():
        write(p, t)
    for ext in ROOT_EXT:
        (d / f"{OLD}.{ext}").rename(d / f"{NEW}.{ext}")
    for old, new in SHEETS.items():
        (d / old).rename(d / new)
    print("written and renamed")


if __name__ == "__main__":
    main()
