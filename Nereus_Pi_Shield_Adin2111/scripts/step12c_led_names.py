"""Step 12c: the port LEDs carry their port's name (Nick, 2026-11-11, comment on the summary doc: "change P1
and P2 to BM1 and BM2 so they match the silk screen above the threaded inserts").

- "P1" under D9 (east, ADIN port 1, beside the BM1 inserts) becomes "BM1"; "P2" under D10 (west, port 2,
  beside the BM2 inserts) becomes "BM2". Same place and size. "PWR" under D8 stays.
- Silkscreen only.
"""
import sys
import pcbnew
import boardio

FACE = "Menlo"
mm = pcbnew.ToMM
b = boardio.load()
fp = boardio.footprints(b)
TOP = b.GetLayerID("Top Overlay")
texts = [d for d in b.GetDrawings() if d.GetClass() == "PCB_TEXT" and d.GetLayer() == TOP]
at = lambda d: (round(mm(d.GetPosition().x), 2), round(mm(d.GetPosition().y), 2))
if any(d.GetText() in ("BM1", "BM2") and at(d)[1] == 131.0 for d in texts):
    sys.exit("step 12c already applied (BM1 / BM2 stand under the LEDs); nothing done")
# each LED is on its port's net, and its port's inserts are on the same side of the board
nets = lambda ref: {p.GetNetname().split("/")[-1] for p in fp[ref].Pads()}
assert "~{ADIN_P1_LED1}" in nets("D9") and "~{ADIN_P2_LED1}" in nets("D10"), (nets("D9"), nets("D10"))
x = lambda ref: mm(fp[ref].GetPosition().x)
assert x("D9") > x("D10") and min(x("MP1"), x("MP2")) > max(x("MP3"), x("MP4")), "port 1 / BM1 east, port 2 / BM2 west"
assert "BM1_P" in nets("MP1") and "BM2_P" in nets("MP3"), (nets("MP1"), nets("MP3"))
faces = open(boardio.BOARD).read().count('(face "%s")' % FACE)
NEW = {("P1", (151.8, 131.0)): "BM1", ("P2", (145.8, 131.0)): "BM2"}
done = []
for d in texts:
    k = (d.GetText(), at(d))
    if k in NEW:
        d.SetText(NEW[k]); done.append(NEW[k])
assert sorted(done) == ["BM1", "BM2"], done
boardio.save(b)
kept = open(boardio.BOARD).read().count('(face "%s")' % FACE)
assert kept == faces, (faces, kept)
print("  LED names: P1 -> BM1 under D9, P2 -> BM2 under D10; %d texts in %s Bold" % (kept, FACE))
