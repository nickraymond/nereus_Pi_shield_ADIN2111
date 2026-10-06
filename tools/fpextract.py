#!/usr/bin/env python3
"""Extract footprints from a board into a .pretty library, and verify them.

Runs on KiCad's bundled Python (it needs the pcbnew module):

  PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
  $PY tools/fpextract.py BOARD.kicad_pcb OUT.pretty NAMES.txt          # extract
  $PY tools/fpextract.py BOARD.kicad_pcb OUT.pretty NAMES.txt --verify # compare

NAMES.txt lists footprint names (without the library nickname), one per line.
The board is only read, never saved. For each name a front-side instance is
used when one exists; a back-side one is flipped to the front. Position and
rotation are zeroed and pad nets cleared, then KiCad's own writer saves it.

--verify reloads each library footprint and compares it with every board
instance of the same name: pad numbers, pad sizes (the matching copper side for
flipped parts), the multiset of pad-to-pad distances, and exact pad centres after
placing a copy of the library footprint the way the instance is placed (flipped
for back-side instances), so a mirrored library would fail. Exit 1 on mismatch.

Deliberate library fixes (S5.g, DESIGN D24) that verify allows for: the PoDL
threaded inserts' SMD pad is unnumbered on the board, so a new layout couldn't
put the bus net on it; the library pad is "1" (RENUMBER_SMD). 3D models are not
compared.
"""
import itertools
import math
import sys
from pathlib import Path


# footprint name -> {board SMD pad number: library pad number}
RENUMBER_SMD = {"78614015360-Footprint-2": {"": "1"}}


def renumbered(number, is_smd, mapping):
    """Library pad number expected for a board pad (deliberate fixes only touch SMD pads)."""
    return mapping.get(number, number) if (is_smd and mapping) else number


def choose_instance(instances):
    """Prefer a front-side instance. instances: [(footprint, flipped: bool)]."""
    front = [fp for fp, flipped in instances if not flipped]
    return (front[0], False) if front else (instances[0][0], True)


def pad_distances(points, nd=3):
    """Sorted pairwise distances (rounded) between pad centres."""
    return sorted(round(math.dist(a, b), nd) for a, b in itertools.combinations(points, 2))


def _instances_by_name(board):
    out = {}
    for fp in board.GetFootprints():
        name = fp.GetFPID().GetLibItemName().wx_str()
        out.setdefault(name, []).append((fp, fp.IsFlipped()))
    return out


def _local_pads(fp, layer=None, renumber=None):
    """[(number, (w, h), (x, y) relative to the footprint, unrotated)] in mm.

    KiCad's y axis points down, so undoing an orientation θ is the textbook
    rotation by +θ. `layer` picks the copper layer whose pad size is read
    (padstacks can differ front/back; a flipped instance's B.Cu is the
    library's F.Cu)."""
    import pcbnew
    layer = pcbnew.F_Cu if layer is None else layer
    o = fp.GetPosition()
    ang = fp.GetOrientation().AsRadians()
    out = []
    for p in fp.Pads():
        d = p.GetPosition() - o
        x, y = pcbnew.ToMM(d.x), pcbnew.ToMM(d.y)
        xr, yr = x * math.cos(ang) - y * math.sin(ang), x * math.sin(ang) + y * math.cos(ang)
        s = p.GetSize(layer)
        num = renumbered(p.GetNumber(), p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD, renumber)
        out.append((num, tuple(sorted((round(pcbnew.ToMM(s.x), 3), round(pcbnew.ToMM(s.y), 3)))),
                    (xr, yr)))
    return out


def _close(a, b, tol=0.005):
    return len(a) == len(b) and all(abs(x - y) <= tol for x, y in zip(a, b))


def extract(board_path, out_dir, names):
    import pcbnew
    board = pcbnew.LoadBoard(str(board_path))
    by = _instances_by_name(board)
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    report = []
    for name in names:
        if name not in by:
            raise SystemExit(f"fpextract: {name} is not on the board")
        src, flipped = choose_instance(by[name])
        fp = src.Duplicate()
        if fp.IsFlipped():
            fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
        fp.SetOrientation(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))
        fp.SetPosition(pcbnew.VECTOR2I(0, 0))
        fp.SetLocked(False)
        fp.SetReference("REF**")
        fp.SetValue(name)
        for p in fp.Pads():
            p.SetNetCode(0)
        pcbnew.PCB_IO_KICAD_SEXPR().FootprintSave(str(out_dir), fp)
        report.append((name, src.GetReference(), "back→front" if flipped else "front"))
    return report


def verify(board_path, out_dir, names):
    import pcbnew
    board = pcbnew.LoadBoard(str(board_path))
    by = _instances_by_name(board)
    problems = []
    for name in names:
        lib = pcbnew.PCB_IO_KICAD_SEXPR().FootprintLoad(str(out_dir), name)
        if lib is None:
            problems.append(f"{name}: not in {out_dir}")
            continue
        lp = _local_pads(lib)
        for inst, flipped in by[name]:
            fix = RENUMBER_SMD.get(name)
            bp = _local_pads(inst, pcbnew.B_Cu if flipped else pcbnew.F_Cu, fix)
            ref = inst.GetReference()
            if sorted(n for n, _, _ in lp) != sorted(n for n, _, _ in bp):
                problems.append(f"{name} vs {ref}: pad numbers differ")
            if sorted(s for _, s, _ in lp) != sorted(s for _, s, _ in bp):
                problems.append(f"{name} vs {ref}: pad sizes differ")
            if not _close(pad_distances([c for _, _, c in lp], 4), pad_distances([c for _, _, c in bp], 4)):
                problems.append(f"{name} vs {ref}: pad geometry differs")
            # exact placement check, flipped instances included: place a copy of the
            # library footprint the way the board instance is placed, compare pad centres
            placed = lib.Duplicate()
            placed.SetParent(board)  # Flip needs a parent board
            if flipped:
                placed.Flip(pcbnew.VECTOR2I(0, 0), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
            placed.SetOrientation(inst.GetOrientation())
            placed.SetPosition(inst.GetPosition())
            a = sorted((p.GetNumber(), pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)) for p in placed.Pads())
            b = sorted((renumbered(p.GetNumber(), p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD, fix),
                        pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)) for p in inst.Pads())
            if not all(na == nb and _close((xa, ya), (xb, yb)) for (na, xa, ya), (nb, xb, yb) in zip(a, b)):
                problems.append(f"{name} vs {ref}{' (back)' if flipped else ''}: placed pad positions differ")
    return problems


def main(argv):
    board, out, names_file = argv[:3]
    names = [n.strip() for n in Path(names_file).read_text().splitlines() if n.strip()]
    if "--verify" in argv:
        probs = verify(board, out, names)
        print(f"fpextract verify: {len(names)} footprints, {len(probs)} problem(s)")
        for p in probs:
            print("  " + p)
        return 1 if probs else 0
    for name, ref, side in extract(board, out, names):
        print(f"{name:40} from {ref:6} {side}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
