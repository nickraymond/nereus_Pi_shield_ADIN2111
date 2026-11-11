"""Step 12: the ADIN strap table on the bottom as a ruled table; the board name leaves the bottom
(Nick, 2026-11-11: "that table should go on the board bottom if possible", "Make the strap table a true
table", "Yes build it, but say Bold Box instead of Heavy Box", "remove the Pi Shield name on the bottom").

- Ruled table in the east strip of the bottom silkscreen, 10.6 x 10.8 mm: columns CFG 1 | CFG 0 | SPI MODE,
  four mode rows copied from the schematic's table "ADIN2111 SPI CFG Straps" (BM_Mote_1_ADIN2111.kicad_sch).
  The as-built row (CFG1 = 1, CFG0 = 0: generic SPI with CRC, the default bridges of JP3 and JP4) has a
  0.25 mm frame (the other rules are 0.15 mm); the caption under the table says so.
- The screw sizes and the USB warning move from the east strip to the space behind JP1 (three lines).
- "Pi Shield" and "ADIN2111 Rev0" are removed from the bottom; the name stays on the top.
- The designators of J1 and D2 shift to clear the new texts. No copper and no footprint moves.
"""
import re
import subprocess
import sys
import pcbnew
import boardio

F = pcbnew.FromMM
V = lambda x, y: pcbnew.VECTOR2I(F(x), F(y))
FACE = "Menlo"
ADV = 0.843          # Menlo Bold: advance per character = 0.843 x text width
b = boardio.load()
fp = boardio.footprints(b)
BOT = b.GetLayerID("Bottom Overlay")
assert BOT == pcbnew.B_SilkS, BOT
texts = [d for d in b.GetDrawings() if d.GetClass() == "PCB_TEXT" and d.GetLayer() == BOT]
if any(d.GetText() == "SPI MODE" for d in texts):
    sys.exit("step 12 already applied (text 'SPI MODE' exists); nothing done")
GONE = ("INSERTS  M3", "MOUNT    M2.5", "NO USB POWER ON", "THE PI WHILE", "JP1 FEEDS IT", "Pi Shield", "ADIN2111 Rev0")
old = [d for d in texts if d.GetText() in GONE]
assert sorted(d.GetText() for d in old) == sorted(GONE), [d.GetText() for d in old]
added = []


def text(s, x, y, w=0.74, h=1.0):
    t = pcbnew.PCB_TEXT(b)
    t.SetText(s); t.SetLayer(BOT); t.SetTextSize(V(w, h)); t.SetTextThickness(F(0.15))
    t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER); t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
    t.SetMirrored(True); t.SetPosition(V(x, y)); b.Add(t)
    added.append(s)


def line(x1, y1, x2, y2, w=0.15):
    s = pcbnew.PCB_SHAPE(b)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(BOT); s.SetStart(V(x1, y1)); s.SetEnd(V(x2, y2)); s.SetWidth(F(w)); b.Add(s)
    return 1


# ---- ruled table. u runs left to right for the reader of the bottom side: x = XL - u
XL, Y0, RH, W = 180.30, 106.90, 1.80, 0.70
C = [0.0, 1.5, 3.0, 10.6]                    # column borders: CFG1 | CFG0 | SPI MODE
X = lambda u: XL - u
row = lambda r: Y0 + RH * r                  # top of row r
mid = lambda r: Y0 + RH * (r + 0.5)
n = 0
for r in (0, 2, 3, 4, 5, 6):                 # horizontal rules, full width
    n += line(X(C[0]), row(r), X(C[3]), row(r))
n += line(X(C[0]), row(1), X(C[2]), row(1))  # under "CFG" only: SPI MODE spans both header rows
for u in (C[0], C[2], C[3]):
    n += line(X(u), row(0), X(u), row(6))
n += line(X(C[1]), row(1), X(C[1]), row(6))
text("CFG", X((C[0] + C[2]) / 2), mid(0), w=W)
text("1", X((C[0] + C[1]) / 2), mid(1), w=W)
text("0", X((C[1] + C[2]) / 2), mid(1), w=W)
text("SPI MODE", X((C[2] + C[3]) / 2), Y0 + RH, w=W)
MODES = [("1", "0", "GENERIC+CRC"), ("1", "1", "GENERIC"), ("0", "0", "OPEN+PROT"), ("0", "1", "OPEN")]
for i, (c1, c0, mode) in enumerate(MODES):
    r = i + 2
    text(c1, X((C[0] + C[1]) / 2), mid(r), w=W)
    text(c0, X((C[1] + C[2]) / 2), mid(r), w=W)
    text(mode, X(C[2] + 0.45 + len(mode) * ADV * W / 2), mid(r), w=W)
# the as-built row: bold frame. 0.25 mm keeps the texts of this row and the next 0.15 mm clear of it (0.30 did not)
for a, c in (((C[0], row(2)), (C[3], row(2))), ((C[0], row(3)), (C[3], row(3))), ((C[0], row(2)), (C[0], row(3))), ((C[3], row(2)), (C[3], row(3)))):
    n += line(X(a[0]), a[1], X(c[0]), c[1], w=0.25)
text("BOLD BOX = AS BUILT", X((C[0] + C[3]) / 2), row(6) + 1.25, w=0.62, h=0.9)

# ---- screw sizes and the USB warning behind JP1 (clear of the corner fiducial and of C53's designator)
for i, s in enumerate(["INSERTS M3  MOUNT M2.5", "NO USB POWER ON THE PI", "WHILE JP1 FEEDS IT"]):
    text(s, 126.60, 84.90 + 1.6 * i)
fp["J1"].Reference().SetPosition(V(134.00, 83.60))
fp["D2"].Reference().SetPosition(V(167.35, 107.35))
for d in old:
    b.Remove(d)
boardio.save(b)

# ---- the new texts take the board's silkscreen font (step 9h): the face is written into the file's text blocks
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
assert faces - before == len(added), (before, faces, len(added))
open(boardio.BOARD, "w").write(s)
code = "import pcbnew, sys; pcbnew.SaveBoard(sys.argv[1], pcbnew.LoadBoard(sys.argv[1]))"
subprocess.run([sys.executable, "-c", code, boardio.BOARD], check=True, stderr=subprocess.DEVNULL)
kept = open(boardio.BOARD).read().count('(face "%s")' % FACE)
assert kept == faces, (faces, kept)
print("  %d bottom texts removed (%s); %d texts and %d lines added; %d texts in %s Bold" % (len(old), ", ".join(GONE[-2:]) + " and the 5 note lines", len(added), n, kept, FACE))
