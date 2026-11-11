"""Step 12b: the screw sizes on the bottom spelled out (Nick, 2026-11-11, comment on the summary doc:
'Please try to fit "Threaded Inserts" and "Mounting Holes" if you can so easier to understand').

- "INSERTS M3  MOUNT M2.5" behind JP1 becomes two lines, "THREADED INSERTS M3" (y 83.30) and
  "MOUNTING HOLES M2.5" (y 84.90). The two lines of the USB warning under them stay where they are.
- Silkscreen only.
"""
import re
import subprocess
import sys
import pcbnew
import boardio

F = pcbnew.FromMM
V = lambda x, y: pcbnew.VECTOR2I(F(x), F(y))
FACE = "Menlo"
b = boardio.load()
BOT = b.GetLayerID("Bottom Overlay")
texts = [d for d in b.GetDrawings() if d.GetClass() == "PCB_TEXT" and d.GetLayer() == BOT]
if any(d.GetText() == "THREADED INSERTS M3" for d in texts):
    sys.exit("step 12b already applied (text 'THREADED INSERTS M3' exists); nothing done")
old = [d for d in texts if d.GetText() == "INSERTS M3  MOUNT M2.5"]
assert len(old) == 1, len(old)
NEW = [("THREADED INSERTS M3", 83.30), ("MOUNTING HOLES M2.5", 84.90)]
for s, y in NEW:
    t = pcbnew.PCB_TEXT(b)
    t.SetText(s); t.SetLayer(BOT); t.SetTextSize(V(0.74, 1.0)); t.SetTextThickness(F(0.15))
    t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER); t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
    t.SetMirrored(True); t.SetPosition(V(126.60, y)); b.Add(t)
b.Remove(old[0])
boardio.save(b)

# the new texts take the board's silkscreen font (step 9h): the face is written into the file's text blocks
s = open(boardio.BOARD).read()
before = s.count('(face "%s")' % FACE)


def face(m):
    blk = m.group(0)
    if ('(layer "F.SilkS"' not in blk and '(layer "B.SilkS"' not in blk) or "(hide yes)" in blk or "(face" in blk:
        return blk
    j = blk.find("\n", blk.find("(font\n")) + 1
    indent = re.match(r"\t*", blk[j:]).group(0)
    return blk[:j] + indent + '(face "%s")\n' % FACE + indent + "(bold yes)\n" + blk[j:]


s = re.sub(r'\t\(gr_text "(?:[^"\\]|\\.)*"\n(?:\t\t.*\n)+?\t\)\n', face, s)
faces = s.count('(face "%s")' % FACE)
assert faces - before == len(NEW), (before, faces)
open(boardio.BOARD, "w").write(s)
code = "import pcbnew, sys; pcbnew.SaveBoard(sys.argv[1], pcbnew.LoadBoard(sys.argv[1]))"
subprocess.run([sys.executable, "-c", code, boardio.BOARD], check=True, stderr=subprocess.DEVNULL)
kept = open(boardio.BOARD).read().count('(face "%s")' % FACE)
assert kept == faces, (faces, kept)
print("  1 bottom text removed, %d added (%s); %d texts in %s Bold" % (len(NEW), " / ".join(n for n, y in NEW), kept, FACE))
