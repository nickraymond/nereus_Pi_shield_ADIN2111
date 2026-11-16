#!/usr/bin/env python3
"""Stage 8, job 2: LCSC numbers for the nine parts stage 2 added without one. Schematic fields only (Top-Level sheet).
For each part: the existing, empty field PLANNED LCSC is filled (C + digits, hidden as it was); a field SOURCING
"JLC stock (read 2026-11-16)" is added in the form the other parts carry it (hidden, a copy of the part's own PLANNED LCSC block);
"LCSC number not looked up" in PLANNED NOTE becomes "LCSC number confirmed on JLC's part page (read 2026-11-16)".
The numbers are checked against the lookup table (LCSC_LOOKUP.md, read on JLC's part pages 2026-11-16): any difference stops the script.
Usage: python3 job2_lcsc.py <board dir> <LCSC_LOOKUP.md>"""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))
import schedit
PARTS = {"U12": "C3681248", "U13": "C468683", "C60": "C408132", "C64": "C386109", "R48": "C137968", "J7": "C189895", "J9": "C189895", "J10": "C189895", "J8": "C514175"}
SOURCING = "JLC stock (read 2026-11-16)"; OLD = "LCSC number not looked up"; NEW = "LCSC number confirmed on JLC's part page (read 2026-11-16)"
BOARD = Path(sys.argv[1]); TOP = BOARD / "Nereus_Pi_Shield_Adin2111_TopLevel.kicad_sch"
look = {}
for line in Path(sys.argv[2]).read_text(encoding="utf-8").splitlines():
    c = [x.strip() for x in line.split("|")]
    if len(c) == 14 and re.fullmatch(r"[A-Z]+\d+", c[1]) and re.fullmatch(r"C\d+", c[5]): look[c[1]] = c[5]      # the Result table only (12 columns)
assert look == PARTS, ("the lookup table and this script differ", look, PARTS)
t = TOP.read_text(encoding="utf-8"); n0 = t.count("(") - t.count(")"); sym0 = len(list(schedit.top_level(t, "symbol")))
for ref, num in PARTS.items():
    blk = next(b for _, _, b in schedit.top_level(t, "symbol") if schedit.symbol_ref(b) == ref)
    p = {m.group(1): m for m in schedit.PROP.finditer(blk)}
    assert p["PLANNED LCSC"].group(2) == "" and "SOURCING" not in p and OLD in p["PLANNED NOTE"].group(2), ref
    assert "(hide yes)" in p["PLANNED LCSC"].group(0)
    note = p["PLANNED NOTE"].group(2).replace(OLD, NEW)
    t = schedit.set_properties(t, ref, {"PLANNED LCSC": num, "PLANNED NOTE": note})
    blk = next(b for _, _, b in schedit.top_level(t, "symbol") if schedit.symbol_ref(b) == ref)
    m = next(m for m in schedit.PROP.finditer(blk) if m.group(1) == "PLANNED LCSC")
    src = m.group(0).replace('"PLANNED LCSC" "%s"' % num, '"SOURCING" "%s"' % SOURCING, 1); assert src != m.group(0)
    last = list(schedit.PROP.finditer(blk))[-1]
    t = t.replace(blk, blk[:last.end()] + src + blk[last.end():], 1)
    print("  %-4s PLANNED LCSC %-9s SOURCING added; note: ...%s" % (ref, num, note[-75:]))
assert t.count("(") - t.count(")") == n0 and len(list(schedit.top_level(t, "symbol"))) == sym0, "unbalanced edit"
TOP.write_text(t, encoding="utf-8")
for f in sorted(BOARD.glob("*.kicad_sch")):
    for _, _, b in schedit.top_level(f.read_text(encoding="utf-8"), "symbol"):
        p = {m.group(1): m.group(2) for m in schedit.PROP.finditer(b)}
        if p.get("PLANNED LCSC", "x") == "": print("  still empty PLANNED LCSC: %s (%s; PLANNED NOTE: %s; SOURCING: %s)" % (schedit.symbol_ref(b), p.get("Value"), p.get("PLANNED NOTE"), p.get("SOURCING")))
        if OLD in b: print("  !! still says not looked up:", schedit.symbol_ref(b))
