"""Step 9h: silkscreen style (Nick approved mock round 2 on 2026-11-11: "Yes, build it"). No copper changes.

Positions come from step9h_silk_style.json, written by the planner in step9h_plan/ (it keeps texts off pads,
part bodies, other silkscreen and the fiducials' mask openings).

- Font: Menlo Bold on every visible silkscreen text, for its slashed zero (0 against O). pcbnew's Python
  interface cannot set a font face, so the face is written into the saved board file's text blocks.
- Function names large (1.3 to 1.8 mm), the designator small and centred under them: CFG0 / JP4, CFG1 / JP3,
  LED / JP2, 5V SEL / JP1, PI 5V / J6, I2C3 / J3.
- J4 reads "+5V / AUX OUT / GND" and J5 "VBUS OUT / + / GND", each in a box, on both sides. The boxes are
  open towards the board edge; J4's top line lies on L6's outline. The footprints' own "+" and "GND" texts
  on J4 and J5 are removed (replaced by these).
- Reference designators: all 0.8 mm high, 0.75 mm wide, horizontal; six are turned 90 degrees where nothing
  else fits (the json lists them). F1, the mounting holes, the inserts and the fiducials stay hidden.
- Board name and logo move from the north-east corner into the east strip beside L1, turned 90 degrees
  ("Pi Shield" 2.6 mm high, the logo 1.15 times its size).
- Bottom side: J2's pin names, ratings in two columns under J2, screw sizes and the USB warning in the
  east strip.
"""
import json
import os
import re
import subprocess
import sys
import pcbnew
import boardio
from boardio import mm

F = pcbnew.FromMM
V = lambda x, y: pcbnew.VECTOR2I(F(x), F(y))
FACE = "Menlo"
P = json.load(open(os.path.join(boardio.HERE, "step9h_silk_style.json")))
b = boardio.load()
LAY = {"T": b.GetLayerID("Top Overlay"), "B": b.GetLayerID("Bottom Overlay")}
draw = list(b.GetDrawings())
if any(d.Type() == pcbnew.PCB_TEXT_T and d.GetText() == "VBUS OUT" for d in draw):
    sys.exit("step 9h already applied (text 'VBUS OUT' exists); nothing done")
fps = boardio.footprints(b)

# ---- old board-level silkscreen texts go; the plan holds the full new set
old = [d for d in draw if d.Type() == pcbnew.PCB_TEXT_T and d.GetLayer() in LAY.values()]
assert len(old) == 49, len(old)
own = [(fps[r], g) for r in ("J4", "J5") for g in fps[r].GraphicalItems() if g.Type() == pcbnew.PCB_TEXT_T and g.GetLayer() in LAY.values()]
assert sorted(g.GetText() for f, g in own) == ["+", "+", "GND", "GND"], [g.GetText() for f, g in own]

# ---- logo: turned 90 degrees, 1.15 x, to the north end of the east strip
logo = [d for d in draw if d.Type() == pcbnew.PCB_SHAPE_T and d.GetLayer() == LAY["T"] and d.GetShape() == pcbnew.SHAPE_T_POLY
        and mm(d.GetBoundingBox().GetX()) > 176 and mm(d.GetBoundingBox().GetBottom()) < 96]
assert len(logo) == 2, len(logo)
c0 = max(logo, key=lambda d: d.GetBoundingBox().GetWidth()).GetBoundingBox().GetCenter()
for d in logo:
    d.Rotate(c0, pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T)); d.Move(pcbnew.VECTOR2I(-c0.x, -c0.y)); d.Scale(1.15); d.Move(V(177.25, 101.10))

for d in old:
    b.Remove(d)
for f, g in own:
    f.Remove(g)

# ---- new texts and box lines
JUST = {"C": pcbnew.GR_TEXT_H_ALIGN_CENTER, "R": pcbnew.GR_TEXT_H_ALIGN_RIGHT, "L": pcbnew.GR_TEXT_H_ALIGN_LEFT}
for t in P["texts"]:
    x = pcbnew.PCB_TEXT(b)
    x.SetText(t["t"]); x.SetLayer(LAY[t["side"]])
    x.SetTextSize(V(t["w"], t["h"])); x.SetTextThickness(F(0.15))
    x.SetHorizJustify(JUST[t["just"]]); x.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
    x.SetMirrored(t["side"] == "B"); x.SetTextAngleDegrees(t["ang"]); x.SetPosition(V(t["x"], t["y"]))
    b.Add(x)
for l in P["lines"]:
    s = pcbnew.PCB_SHAPE(b)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(LAY[l["side"]]); s.SetStart(V(*l["a"])); s.SetEnd(V(*l["b"])); s.SetWidth(F(l["w"]))
    b.Add(s)

# ---- reference designators
assert len(P["refs"]) == 128 and not P["hide"], (len(P["refs"]), P["hide"])
for r in P["refs"]:
    t = fps[r["ref"]].Reference()
    assert (t.GetLayer() == LAY["B"]) == fps[r["ref"]].IsFlipped() == (r["side"] == "B"), r
    t.SetVisible(True); t.SetTextSize(V(P["rw"], P["rh"])); t.SetTextThickness(F(0.15))
    t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER); t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
    t.SetKeepUpright(True); t.SetTextAngleDegrees(r["ang"]); t.SetPosition(V(r["x"], r["y"]))
shown = sorted(f.GetReference() for f in b.GetFootprints() if f.Reference().IsVisible() and f.Reference().GetLayer() in LAY.values())
assert shown == sorted(r["ref"] for r in P["refs"]), set(shown) ^ set(r["ref"] for r in P["refs"])

boardio.save(b)

# ---- font face on every visible silkscreen text, in the file's text
s = open(boardio.BOARD).read()


def face(m):
    blk = m.group(0)
    if ('(layer "F.SilkS"' not in blk and '(layer "B.SilkS"' not in blk) or "(hide yes)" in blk or "(face" in blk:
        return blk
    i = blk.find("(font\n")
    if i < 0:
        return blk
    j = blk.find("\n", i) + 1
    indent = re.match(r"\t*", blk[j:]).group(0)
    return blk[:j] + indent + '(face "%s")\n' % FACE + indent + "(bold yes)\n" + blk[j:]


for pat in (r'\t\(gr_text "(?:[^"\\]|\\.)*"\n(?:\t\t.*\n)+?\t\)\n',
            r'\t\t\(property "Reference" "(?:[^"\\]|\\.)*"\n(?:\t\t\t.*\n)+?\t\t\)\n',
            r'\t\t\(fp_text user "(?:[^"\\]|\\.)*"\n(?:\t\t\t.*\n)+?\t\t\)\n'):
    s = re.sub(pat, face, s)
faces = s.count('(face "%s")' % FACE)
assert faces >= len(P["texts"]) + len(P["refs"]), faces
open(boardio.BOARD, "w").write(s)
code = "import pcbnew, sys; pcbnew.SaveBoard(sys.argv[1], pcbnew.LoadBoard(sys.argv[1]))"
subprocess.run([sys.executable, "-c", code, boardio.BOARD], check=True, stderr=subprocess.DEVNULL)
kept = open(boardio.BOARD).read().count('(face "%s")' % FACE)
assert kept == faces, (faces, kept)
print("  %d old texts and %d footprint texts removed; %d texts, %d box lines added; %d designators set (%d turned 90: %s)" % (
    len(old), len(own), len(P["texts"]), len(P["lines"]), len(P["refs"]), sum(1 for r in P["refs"] if r["ang"]),
    " ".join(sorted(r["ref"] for r in P["refs"] if r["ang"]))))
print("  font %s Bold on %d silkscreen texts; logo turned and moved to (177.25, 101.10)" % (FACE, kept))
