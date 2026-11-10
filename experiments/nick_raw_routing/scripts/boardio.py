"""Load and save nick_raw_routing.kicad_pcb with pcbnew."""
import os
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
BOARD = os.path.join(HERE, "..", "nick_raw_routing.kicad_pcb")
mm = pcbnew.ToMM


def load(path=BOARD):
    return pcbnew.LoadBoard(path)


def save(board, path=BOARD):
    """Save, then load and save once more: the writer's output is stable only after the second pass."""
    pcbnew.SaveBoard(path, board)
    pcbnew.SaveBoard(path, pcbnew.LoadBoard(path))


def footprints(board):
    return {f.GetReference(): f for f in board.GetFootprints()}


def move_to(fp, x, y):
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))


def pos(fp):
    p = fp.GetPosition()
    return round(mm(p.x), 4), round(mm(p.y), 4)
