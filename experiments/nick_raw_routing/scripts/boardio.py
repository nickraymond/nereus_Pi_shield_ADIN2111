"""Load and save nick_raw_routing.kicad_pcb with pcbnew."""
import os
import subprocess
import sys
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
BOARD = os.path.join(HERE, "..", "nick_raw_routing.kicad_pcb")
mm = pcbnew.ToMM


def load(path=BOARD):
    return pcbnew.LoadBoard(path)


def save(board, path=BOARD):
    """Save, then load and save once more: the writer's output is stable only after the second pass.

    The second pass runs in a fresh process; a second LoadBoard in the same process leaves pcbnew's
    Python bindings unable to list drawings.
    """
    pcbnew.SaveBoard(path, board)
    code = "import pcbnew, sys; pcbnew.SaveBoard(sys.argv[1], pcbnew.LoadBoard(sys.argv[1]))"
    subprocess.run([sys.executable, "-c", code, path], check=True, stderr=subprocess.DEVNULL)


def report(refs):
    """Print the saved board's state from a fresh process."""
    subprocess.run([sys.executable, os.path.join(HERE, "report.py")] + list(refs), check=True, stderr=subprocess.DEVNULL)


def footprints(board):
    return {f.GetReference(): f for f in board.GetFootprints()}


def move_to(fp, x, y):
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))


def pos(fp):
    p = fp.GetPosition()
    return round(mm(p.x), 4), round(mm(p.y), 4)
