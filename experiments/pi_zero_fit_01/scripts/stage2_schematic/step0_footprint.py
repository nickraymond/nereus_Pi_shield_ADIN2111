"""Step 0b: extract the MP6550GG footprint from the Urchin board into board/urchin.pretty and verify it.

Runs on KiCad's bundled Python (pcbnew). The Urchin board is only read. The instance (U1) is copied, moved to the
origin at 0 degrees (flipped to the front if it sits on the back), its pad nets cleared, and saved with KiCad's own
writer. Verification: the saved footprint is reloaded and its pads (number, size, shape, position relative to the
footprint, in the footprint's own frame) are compared with the board instance.
"""
import os
import sys
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
BOARD = os.path.join(HERE, "..", "urchin_ref", "UrchinCam_01.kicad_pcb")
LIB = os.path.abspath(os.path.join(HERE, "..", "board", "urchin.pretty"))
NAME, REF = "MP6550GG", "U1"


def pads(fp):
    out = []
    for p in fp.Pads():
        pos = p.GetFPRelativePosition()
        out.append((p.GetNumber(), round(pcbnew.ToMM(pos.x), 4), round(pcbnew.ToMM(pos.y), 4),
                    round(pcbnew.ToMM(p.GetSize(pcbnew.F_Cu).x), 4), round(pcbnew.ToMM(p.GetSize(pcbnew.F_Cu).y), 4),
                    p.GetShape(pcbnew.F_Cu), p.GetAttribute()))
    return sorted(out)


b = pcbnew.LoadBoard(BOARD)
src = [f for f in b.GetFootprints() if f.GetReference() == REF][0]
assert src.GetFPID().GetUniStringLibItemName() == NAME, src.GetFPID().GetUniStringLibId()
flipped = src.IsFlipped()
want = pads(src) if not flipped else None
fp = pcbnew.Cast_to_FOOTPRINT(src.Duplicate(False))
if flipped:
    fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
fp.SetOrientationDegrees(0)
fp.SetPosition(pcbnew.VECTOR2I(0, 0))
for p in fp.Pads():
    p.SetNetCode(0)
fp.SetReference("REF**")
os.makedirs(LIB, exist_ok=True)
plug = pcbnew.PCB_IO_MGR.FindPlugin(pcbnew.PCB_IO_MGR.KICAD_SEXP)
plug.FootprintSave(LIB, fp)
back = plug.FootprintLoad(LIB, NAME)
got = pads(back)
print("  %s from Urchin %s (%s side): %d pads" % (NAME, REF, "back" if flipped else "front", len(got)))
for row in got:
    print("    pad %s at (%s, %s) size %s x %s" % row[:5])
if want is not None and want != got:
    sys.exit("MISMATCH between the Urchin instance and the saved footprint:\n%s\n%s" % (want, got))
# seen from the front, pads 1..12 must run counter-clockwise (y points down, so the shoelace sum is negative):
# a footprint saved mirrored would fail here
pts = [(r[1], r[2]) for r in sorted(got, key=lambda r: int(r[0]))]
area = sum(a[0] * c[1] - c[0] * a[1] for a, c in zip(pts, pts[1:] + pts[:1]))
assert len(got) == len(list(src.Pads())) == 12 and area < 0, ("pad order is not counter-clockwise from the front", area)
print("  verify: 12 pads, numbered counter-clockwise seen from the front (not mirrored)"
      + ("; identical to the board instance" if want is not None else "; the Urchin instance sits on the back and was flipped"))
