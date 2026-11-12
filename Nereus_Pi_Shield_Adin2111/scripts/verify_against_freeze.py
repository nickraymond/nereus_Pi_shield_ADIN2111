#!/usr/bin/env python3
"""Prove that the board still is the frozen layout (tag s9-layout-freeze, Nick 2026-11-11).

Two kinds of difference are allowed, and nothing else:
  1. the hidden BOM fields of the footprints (BOM review 2026-11; see bom_fields_board_sync_2026_11.py),
  2. the sheet file name each footprint records, (sheetfile "..."), which changed with the project rename
     of 2026-11-12 (rename_project_2026_11.py).
With both taken out, the two board files must be identical byte for byte.

  python3 verify_against_freeze.py                      # the board here against the tag, read with git show
  python3 verify_against_freeze.py <board at the tag> <board>
Exit code 0 = identical apart from those two; 1 = something else differs (the first place is printed).
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bom_fields_board_sync_2026_11 as bom  # noqa: E402

HERE = Path(__file__).resolve().parent.parent
BOARD = HERE / "Nereus_Pi_Shield_Adin2111.kicad_pcb"
TAG = "s9-layout-freeze"
TAG_PATH = "experiments/nick_raw_routing/nick_raw_routing.kicad_pcb"  # where the board was at the tag
SHEETFILE = re.compile(r'\(sheetfile "[^"]*"\)')


def at_tag():
    r = subprocess.run(["git", "show", f"{TAG}:{TAG_PATH}"], cwd=HERE, capture_output=True)
    if r.returncode:
        sys.exit(f"verify: cannot read {TAG}:{TAG_PATH} ({r.stderr.decode().strip()}); "
                 f"is the tag here? `git fetch origin tag {TAG}`, or pass the two board files")
    return r.stdout.decode("utf-8")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) == 2:
        a, b = bom.read(args[0]), bom.read(args[1])
    elif not args:
        a, b = at_tag(), bom.read(BOARD)
    else:
        sys.exit(__doc__)
    sa, sb = SHEETFILE.findall(a), SHEETFILE.findall(b)
    renamed = sum(x != y for x, y in zip(sa, sb)) if len(sa) == len(sb) else "?"
    na, nb = (SHEETFILE.sub('(sheetfile "")', bom.strip_fields(t)) for t in (a, b))
    print(f"sheetfile values: {len(sa)} at the freeze, {len(sb)} now, {renamed} differ")
    if na == nb:
        print("identical to the freeze apart from the BOM fields and sheet file names")
        return 0
    la, lb = na.split("\n"), nb.split("\n")
    i = next((k for k, (x, y) in enumerate(zip(la, lb)) if x != y), min(len(la), len(lb)))
    print("DIFFERENT outside the BOM fields and sheet file names; first difference (line of the reduced text "
          f"{i + 1}):\n  freeze: {la[i][:160] if i < len(la) else '(end)'}\n  now:    {lb[i][:160] if i < len(lb) else '(end)'}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
