"""Step 25: the schematic's front sheet shows the board, top and bottom, with its length and width (Nick, this
session's chat, 2026-11-11: "update the front sheet of the schematic to show top and bottom views of the board with
dimensions for length and width like you'd expect on a drawing").

Run with the system python3 (needs Pillow and kicad-cli), from anywhere:
    python3 step25_front_sheet_views.py <out dir for the picture>

- Renders the frozen board's top and bottom side with kicad-cli (orthographic), crops each to the board, and
  draws both on one picture with dimension lines: 65.00 mm and 56.00 mm, the size of the Edge.Cuts outline as
  read from the board file (centre lines x 116.301..181.301, y 76.104..132.104).
- Front sheet (nick_raw_routing.kicad_sch, A3): the picture goes into the frame that held "Pi shield renders: TBD
  (after layout)"; that text is removed and the frame loses its grey fill, which would cover the picture.
  "DIMENSIONS: TBD (after layout)" becomes "65.00 x 56.00 x 1.6 mm"; corner radius, layer count and mounting
  holes stand in a note under the views. Nothing electrical changes: the sheet holds no parts or wires.
"""
import base64
import io
import os
import re
import subprocess
import sys
import uuid
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
BOARD = os.environ.get("NRR_BOARD") or os.path.join(HERE, "..", "nick_raw_routing.kicad_pcb")
SCH = os.path.join(os.path.dirname(os.path.abspath(BOARD)), "nick_raw_routing.kicad_sch")
KCLI = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
OUT = sys.argv[1]
W_MM, H_MM = 65.00, 56.00                  # Edge.Cuts outline, read from the board (outline.py of this session)
DIMS = "65.00 x 56.00 x 1.6 mm"            # the text beside "DIMENSIONS:" (27 characters fit before the frame)
NOTE = "Outline 65.00 x 56.00 mm, corners R3.0, 1.6 mm thick, 6 copper layers.  4 mounting holes 2.70 mm on 58.00 x 49.00 mm.  Views at %.2f : 1 on A3."
GREY = "(fill\n\t\t\t(type color)\n\t\t\t(color 210 210 210 1)\n\t\t)"   # the placeholder frame's grey fill, which would cover the picture
FRAME = (142.24, 53.34, 403.86, 228.6)     # the frame on the front sheet
DPI = 200
PAPER_W, PAPER_H = 250.0, 165.0            # picture size on the sheet, mm
VIEW_W = 100.0                             # width of each board view on the sheet, mm
OLD_RENDERS = "Pi shield renders: TBD (after layout)"
OLD_DIMS = "TBD (after layout)"

sch = open(SCH, encoding="utf-8").read()
if OLD_RENDERS not in sch:
    sys.exit("step 25 already applied (the placeholder text is gone); nothing done")
assert sch.count('(text "%s"' % OLD_RENDERS) == 1 and sch.count('(text "%s"' % OLD_DIMS) == 1
assert sch.count("\n\t(symbol") == 0 and sch.count("\n\t(wire") == 0, "the front sheet holds parts or wires"

px = lambda v: int(round(v * DPI / 25.4))
font = lambda size: ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", px(size))


def view(side):
    """The board's render, cropped to the board by its alpha channel, VIEW_W wide."""
    png = os.path.join(OUT, "render_%s.png" % side)
    subprocess.run([KCLI, "pcb", "render", "--side", side, "--width", "2600", "--height", "2300", "--quality", "basic", "-o", png, BOARD],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    im = Image.open(png).convert("RGBA")
    im = im.crop(im.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox())
    ratio = im.size[0] / im.size[1]
    assert abs(ratio - W_MM / H_MM) < 0.01, "the %s render is not the bare outline (ratio %.4f, outline %.4f)" % (side, ratio, W_MM / H_MM)
    w = px(VIEW_W)
    return im.resize((w, int(round(w / ratio))), Image.LANCZOS)


def arrow(d, tip, direction, size):
    x, y = tip
    dx, dy = direction
    d.polygon([(x, y), (x - dx * size - dy * size * 0.3, y - dy * size - dx * size * 0.3), (x - dx * size + dy * size * 0.3, y - dy * size + dx * size * 0.3)], fill="black")


def dim_h(d, x0, x1, y_obj, y_dim, text):
    for x in (x0, x1):
        d.line([(x, y_obj - px(1.0)), (x, y_dim - px(1.5))], fill="black", width=px(0.18))
    d.line([(x0, y_dim), (x1, y_dim)], fill="black", width=px(0.18))
    arrow(d, (x0, y_dim), (-1, 0), px(2.2)); arrow(d, (x1, y_dim), (1, 0), px(2.2))
    f = font(4.2)
    tw = d.textlength(text, font=f)
    d.text(((x0 + x1 - tw) / 2, y_dim - px(5.6)), text, fill="black", font=f)


def dim_v(canvas, d, y0, y1, x_obj, x_dim, text, left):
    s = -1 if left else 1
    for y in (y0, y1):
        d.line([(x_obj + s * px(1.0), y), (x_dim + s * px(1.5), y)], fill="black", width=px(0.18))
    d.line([(x_dim, y0), (x_dim, y1)], fill="black", width=px(0.18))
    arrow(d, (x_dim, y0), (0, -1), px(2.2)); arrow(d, (x_dim, y1), (0, 1), px(2.2))
    f = font(4.2)
    tw = int(d.textlength(text, font=f))
    t = Image.new("RGBA", (tw + 4, px(5.4)), (255, 255, 255, 0))
    ImageDraw.Draw(t).text((2, 0), text, fill="black", font=f)
    t = t.rotate(90, expand=True)
    canvas.paste(t, (x_dim - px(1.0) - t.size[0] if left else x_dim + px(1.0), (y0 + y1 - t.size[1]) // 2), t)


os.makedirs(OUT, exist_ok=True)
canvas = Image.new("RGB", (px(PAPER_W), px(PAPER_H)), "white")
d = ImageDraw.Draw(canvas)
top, bot = view("top"), view("bottom")
vw, vh = top.size
gap = (canvas.size[0] - 2 * vw) // 3
y0 = px(36)
for i, (im, name) in enumerate(((top, "TOP VIEW"), (bot, "BOTTOM VIEW (seen from below)"))):
    x0 = gap + i * (vw + gap)
    canvas.paste(im, (x0, y0), im)
    dim_h(d, x0, x0 + vw, y0, y0 - px(9), "%.2f mm" % W_MM)
    dim_v(canvas, d, y0, y0 + vh, x0 if i == 0 else x0 + vw, x0 - px(7) if i == 0 else x0 + vw + px(7), "%.2f mm" % H_MM, left=(i == 0))
    f = font(5.0)
    d.text((x0 + (vw - d.textlength(name, font=f)) / 2, y0 + vh + px(5)), name, fill="black", font=f)
note = NOTE % (VIEW_W / W_MM)
f = font(3.2)
d.text(((canvas.size[0] - d.textlength(note, font=f)) / 2, y0 + vh + px(16)), note, fill="black", font=f)
small = canvas.quantize(colors=96, method=Image.MEDIANCUT, dither=Image.NONE)
buf = io.BytesIO()
small.save(buf, format="PNG", optimize=True)     # no resolution tag: KiCad then takes its default, 300 ppi
open(os.path.join(OUT, "front_sheet_views.png"), "wb").write(buf.getvalue())

b64 = base64.b64encode(buf.getvalue()).decode()
lines = [b64[i:i + 76] for i in range(0, len(b64), 76)]
data = '(data "%s"\n' % lines[0] + "".join('\t\t\t"%s"\n' % ln for ln in lines[1:]) + "\t\t)"
cx, cy = (FRAME[0] + FRAME[2]) / 2, (FRAME[1] + FRAME[3]) / 2
image = "\n\t(image\n\t\t(at %.2f %.2f)\n\t\t(scale %.5f)\n\t\t(uuid \"%s\")\n\t\t%s\n\t)" % (cx, cy, 300.0 / DPI, uuid.uuid4(), data)

text = re.search(r'\n\t\(text "%s"\n.*?\n\t\)(?=\n\t\()' % re.escape(OLD_RENDERS), sch, re.S)
assert text and text.group(0).count("\n\t(text") == 1
new = sch.replace(text.group(0), "")
new = new.replace('(text "%s"' % OLD_DIMS, '(text "%s"' % DIMS)
frame = re.search(r"\n\t\(rectangle\n\t\t\(start 142\.24 53\.34\)\n\t\t\(end 403\.86 228\.6\)\n.*?\n\t\)(?=\n\t\()", new, re.S)
assert frame and frame.group(0).count(GREY) == 1, "the grey placeholder frame was not found"
new = new.replace(frame.group(0), frame.group(0).replace(GREY, "(fill\n\t\t\t(type none)\n\t\t)"))
first = new.index("\n\t(image\n")
new = new[:first] + image + new[first:]
assert new.count("\n\t(image\n") == 3 and OLD_RENDERS not in new and DIMS in new
open(SCH, "w", encoding="utf-8").write(new)
print("  picture %d x %d px, %d kB as PNG; front sheet grows by %d kB" % (canvas.size[0], canvas.size[1], len(buf.getvalue()) // 1024, (len(new) - len(sch)) // 1024))
print("  placed at (%.2f, %.2f), scale %.2f (KiCad takes embedded pictures at 300 ppi; this one is %d ppi)" % (cx, cy, 300.0 / DPI, DPI))
