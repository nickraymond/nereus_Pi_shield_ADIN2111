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
instance of the same name: pad count, pad numbers, pad sizes and the multiset of
pad-to-pad distances (independent of rotation and flip), plus exact pad
positions against a front-side instance when there is one. Exit 1 on mismatch.
"""
import itertools
import math
import sys
from pathlib import Path


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


def _local_pads(fp, layer=None):
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
        out.append((p.GetNumber(), tuple(sorted((round(pcbnew.ToMM(s.x), 3), round(pcbnew.ToMM(s.y), 3)))),
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
            bp = _local_pads(inst, pcbnew.B_Cu if flipped else pcbnew.F_Cu)
            ref = inst.GetReference()
            if sorted(n for n, _, _ in lp) != sorted(n for n, _, _ in bp):
                problems.append(f"{name} vs {ref}: pad numbers differ")
            if sorted(s for _, s, _ in lp) != sorted(s for _, s, _ in bp):
                problems.append(f"{name} vs {ref}: pad sizes differ")
            if not _close(pad_distances([c for _, _, c in lp], 4), pad_distances([c for _, _, c in bp], 4)):
                problems.append(f"{name} vs {ref}: pad geometry differs")
            if not flipped:
                a = sorted((n, c) for n, _, c in lp)
                b = sorted((n, c) for n, _, c in bp)
                if not all(na == nb and _close(ca, cb) for (na, ca), (nb, cb) in zip(a, b)):
                    problems.append(f"{name} vs {ref} (front): pad positions differ")
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
