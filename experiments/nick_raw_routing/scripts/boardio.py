"""Load and save nick_raw_routing.kicad_pcb with pcbnew."""
import os
import subprocess
import sys
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
# NRR_BOARD points the scripts at another copy of the board (for a trial on a scratch copy)
BOARD = os.environ.get("NRR_BOARD") or os.path.join(HERE, "..", "nick_raw_routing.kicad_pcb")
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


def net_of(board, short):
    """Net by its last path element, e.g. "ADIN_SCK" for "/Top-Level Schematic/ADIN_SCK"."""
    hits = [n for name, n in board.GetNetsByName().items() if str(name).split("/")[-1] == short]
    assert len(hits) == 1, (short, len(hits))
    return hits[0]


def pad_xy(board, ref, num):
    for p in footprints(board)[ref].Pads():
        if p.GetNumber() == num:
            return mm(p.GetPosition().x), mm(p.GetPosition().y)
    raise KeyError((ref, num))


def via_xy(tracks, short, near):
    """The via of net `short` closest to `near` (x, y); it must be within 0.1 mm. `tracks`: list(board.GetTracks())."""
    best = None
    for t in tracks:
        if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname().split("/")[-1] == short:
            x, y = mm(t.GetPosition().x), mm(t.GetPosition().y)
            d = ((x - near[0]) ** 2 + (y - near[1]) ** 2) ** 0.5
            if best is None or d < best[0]:
                best = (d, x, y)
    assert best and best[0] < 0.1, (short, near, best)
    return best[1], best[2]


def add_track(board, short, layer_name, pts, width=0.2):
    """Add straight segments through pts [(x, y), ...] on one layer. Returns the length in mm."""
    net = net_of(board, short)
    layer = board.GetLayerID(layer_name)
    assert layer >= 0, layer_name
    total = 0.0
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
        t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
        t.SetWidth(pcbnew.FromMM(width))
        t.SetLayer(layer)
        t.SetNet(net)
        board.Add(t)
        total += ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    return total


def find_tracks(board, tracks, short, layer_name, box):
    """The segments of net `short` on a layer that lie wholly inside box (x0, y0, x1, y1).

    `tracks` is one list(board.GetTracks()) taken before any removal: after a Remove, pcbnew's Python
    bindings can no longer list the tracks, so collect first and remove last.
    """
    x0, y0, x1, y1 = box
    layer = board.GetLayerID(layer_name)
    found = []
    for t in tracks:
        if t.Type() == pcbnew.PCB_VIA_T or t.GetLayer() != layer or t.GetNetname().split("/")[-1] != short:
            continue
        ends = [(mm(t.GetStart().x), mm(t.GetStart().y)), (mm(t.GetEnd().x), mm(t.GetEnd().y))]
        if all(x0 <= x <= x1 and y0 <= y <= y1 for x, y in ends):
            found.append(t)
    return found


def add_via(board, short, x, y, diameter=0.6, drill=0.3):
    """Add a through via. Default 0.6 mm with a 0.3 mm hole, the size for new vias (Sofar's 0.45 / 0.2 stay at the ADIN)."""
    v = pcbnew.PCB_VIA(board)
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    v.SetWidth(pcbnew.F_Cu, pcbnew.FromMM(diameter))
    v.SetDrill(pcbnew.FromMM(drill))
    v.SetNet(net_of(board, short))
    board.Add(v)
    return v


def place(fp, x, y, pads, top=None):
    """Move a footprint to (x, y), optionally to the top side, and turn it until its pads sit at `pads`
    ({number: (x, y)}, 0.02 mm tolerance). Fails loudly if no rotation fits."""
    if top is True and fp.IsFlipped():
        fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    move_to(fp, x, y)
    for rot in (0, 90, 180, 270):
        fp.SetOrientationDegrees(rot)
        got = {p.GetNumber(): (mm(p.GetPosition().x), mm(p.GetPosition().y)) for p in fp.Pads()}
        if all(abs(got[n][0] - px) < 0.02 and abs(got[n][1] - py) < 0.02 for n, (px, py) in pads.items()):
            return rot
    raise AssertionError("%s: no rotation puts its pads at %s (last tried: %s)" % (fp.GetReference(), pads, got))


def move_vertex(tracks, short, layer_id, old, new, expect=2):
    """Move every end of net `short` on a layer that sits at `old` (0.02 mm) to `new`. `tracks`: list(board.GetTracks())."""
    hits = 0
    for t in tracks:
        if t.Type() != pcbnew.PCB_TRACE_T or t.GetLayer() != layer_id or t.GetNetname().split("/")[-1] != short:
            continue
        for get, put in ((t.GetStart, t.SetStart), (t.GetEnd, t.SetEnd)):
            p = get()
            if abs(mm(p.x) - old[0]) < 0.02 and abs(mm(p.y) - old[1]) < 0.02:
                put(pcbnew.VECTOR2I(pcbnew.FromMM(new[0]), pcbnew.FromMM(new[1])))
                hits += 1
    assert hits == expect, (short, old, hits)
