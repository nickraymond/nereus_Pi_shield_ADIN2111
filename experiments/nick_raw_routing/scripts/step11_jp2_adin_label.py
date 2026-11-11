"""Step 11: JP2 turned 90 degrees clockwise and the label "ADIN" above D8 (Nick, 2026-11-11: D8 shows the
ADIN's power, not the whole board's; "After that change push").

- JP2 (LED strap, bridged link on 1210 pads) turns from upright to lying east-west and moves 0.4 mm east and
  0.3 mm north, to (149.00, 124.00): pad 1 (ADIN_VDDIO) east, pad 2 (ADIN_LED_VDD) west. The 0.4 mm keeps
  pad 2 clear of the ADIN_LED_VDD via at (146.40, 125.20). That frees 2 mm between JP2 and D8.
- ADIN_VDDIO: top track from the via at (152.55, 122.40) to pad 1 re-laid; ADIN_LED_VDD: top track from pad 2
  to its via re-laid. 5 old top segments removed, 5 added. Nothing else moves.
- Silkscreen: "ADIN" above D8, so the middle LED reads ADIN over PWR. JP2's designator stays under "LED".
"""
import re
import subprocess
import sys
import pcbnew
import boardio
from boardio import add_track, mm, place

F = pcbnew.FromMM
V = lambda x, y: pcbnew.VECTOR2I(F(x), F(y))
FACE = "Menlo"
b = boardio.load()
fp = boardio.footprints(b)
tracks = list(b.GetTracks())
sn = lambda t: t.GetNetname().split("/")[-1]
TOP = b.GetLayerID("Top Overlay")
if any(d.Type() == pcbnew.PCB_TEXT_T and d.GetText() == "ADIN" for d in b.GetDrawings()):
    sys.exit("step 11 already applied (text 'ADIN' exists); nothing done")
assert boardio.pos(fp["JP2"]) == (148.6, 124.3), boardio.pos(fp["JP2"])


def seg(t, net, a, c):
    if t.Type() == pcbnew.PCB_VIA_T or sn(t) != net or b.GetLayerName(t.GetLayer()) != "Top Layer":
        return False
    e = [(mm(t.GetStart().x), mm(t.GetStart().y)), (mm(t.GetEnd().x), mm(t.GetEnd().y))]
    near = lambda p, q: abs(p[0] - q[0]) < 0.02 and abs(p[1] - q[1]) < 0.02
    return (near(e[0], a) and near(e[1], c)) or (near(e[0], c) and near(e[1], a))


old = [((152.55, 122.40), (150.40, 122.40), "ADIN_VDDIO"), ((150.40, 122.40), (149.95, 122.85), "ADIN_VDDIO"), ((149.95, 122.85), (148.60, 122.85), "ADIN_VDDIO"),
       ((148.60, 125.75), (146.95, 125.75), "ADIN_LED_VDD"), ((146.95, 125.75), (146.40, 125.20), "ADIN_LED_VDD")]
dead = [t for t in tracks if any(seg(t, n, a, c) for a, c, n in old)]
assert len(dead) == 5, len(dead)

ref = fp["JP2"].Reference()
ref_at = ref.GetPosition()
place(fp["JP2"], 149.00, 124.00, {"1": (150.45, 124.00), "2": (147.55, 124.00)})
ref.SetPosition(ref_at); ref.SetTextAngleDegrees(0)

L = add_track(b, "ADIN_VDDIO", "Top Layer", [(152.55, 122.40), (151.25, 122.40), (150.45, 123.20), (150.45, 124.00)])
L += add_track(b, "ADIN_LED_VDD", "Top Layer", [(147.55, 124.00), (147.55, 124.05), (146.40, 125.20)])

t = pcbnew.PCB_TEXT(b)
t.SetText("ADIN"); t.SetLayer(TOP); t.SetTextSize(V(0.8, 1.0)); t.SetTextThickness(F(0.15))
t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER); t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
t.SetPosition(V(148.80, 126.45)); b.Add(t)

for d in dead:
    b.Remove(d)
boardio.save(b)

# the new text takes the board's silkscreen font (step 9h): the face is written into the file's text block
s = open(boardio.BOARD).read()
m = re.search(r'\t\(gr_text "ADIN"\n(?:\t\t.*\n)+?\t\)\n', s)
blk = m.group(0)
assert "(face" not in blk
j = blk.find("\n", blk.find("(font\n")) + 1
indent = re.match(r"\t*", blk[j:]).group(0)
s = s.replace(blk, blk[:j] + indent + '(face "%s")\n' % FACE + indent + "(bold yes)\n" + blk[j:])
open(boardio.BOARD, "w").write(s)
code = "import pcbnew, sys; pcbnew.SaveBoard(sys.argv[1], pcbnew.LoadBoard(sys.argv[1]))"
subprocess.run([sys.executable, "-c", code, boardio.BOARD], check=True, stderr=subprocess.DEVNULL)
faces = open(boardio.BOARD).read().count('(face "%s")' % FACE)
assert faces == 227, faces
print("  JP2 at %s; 5 top segments removed, %.2f mm added; text ADIN at (148.80, 126.45); %d texts in %s Bold" % (boardio.pos(fp["JP2"]), L, faces, FACE))
boardio.report(["JP2"])
