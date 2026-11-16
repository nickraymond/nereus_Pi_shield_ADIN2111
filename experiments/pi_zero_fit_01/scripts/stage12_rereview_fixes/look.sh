#!/bin/sh
# Stage 12 (stage 9's look.sh, other areas): colour plots of the six copper layers (one PNG each, 5200 px), crops of the areas stage 12 changed and,
# per area, one montage of the six layers. Usage: sh look.sh <board.kicad_pcb> <out dir> <tag>   ->  <out dir>/look/<tag>_<area>_<layer>.png, <tag>_six_<area>.png
# (new-frame mm; the plot's scale as stage 9 measured it)
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
B="$1"; O="$2"; T="$3"; mkdir -p "$O/plots_$T" "$O/look"
for L in F.Cu:top In1.Cu:in1 In2.Cu:gnd In3.Cu:in2 In4.Cu:pwr B.Cu:bot; do
  id=${L%%:*}; nm=${L##*:}
  $CLI pcb export svg --layers "$id,Edge.Cuts" --page-size-mode 2 --exclude-drawing-sheet -o "$O/plots_$T/cu_$nm.svg" "$B" >/dev/null 2>&1 || echo "svg failed $nm"
  qlmanage -t -s 5200 -o "$O/plots_$T" "$O/plots_$T/cu_$nm.svg" >/dev/null 2>&1 && mv "$O/plots_$T/cu_$nm.svg.png" "$O/plots_$T/cu_$nm.png"
done
python3 - "$O" "$T" <<'PY'
import sys
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS = None
O, T = sys.argv[1:3]
AREAS = {'row_w': (8, 2.5, 34, 11), 'row_e': (32, 2.5, 62, 11), 'f1': (1, 13, 10, 21), 'pwm': (4, 4.5, 13, 12.5)}
NAMES = {'top': 'Top Layer', 'in1': 'Internal 1', 'gnd': 'GND Plane', 'in2': 'Internal 2', 'pwr': 'PWR Plane', 'bot': '6 Bottom Layer (seen from the top)'}
crops = {}
for nm in NAMES:
    im = Image.open('%s/plots_%s/cu_%s.png' % (O, T, nm)).convert('RGB'); k = im.width * 0.8187 / 65.0
    for a, (x0, y0, x1, y1) in AREAS.items():
        c = im.crop((int(x0 * k), int(y0 * k), int(x1 * k), int(y1 * k))); c.save('%s/look/%s_%s_%s.png' % (O, T, a, nm)); crops[(a, nm)] = c
for a in AREAS:
    cs = [crops[(a, nm)] for nm in NAMES]; w, h = cs[0].size; s = min(1.0, 950.0 / w); w2, h2 = int(w * s), int(h * s)
    m = Image.new('RGB', (2 * w2 + 10, 3 * (h2 + 26)), 'white'); d = ImageDraw.Draw(m)
    for i, (nm, c) in enumerate(zip(NAMES, cs)):
        x, y = (i % 2) * (w2 + 10), (i // 2) * (h2 + 26); m.paste(c.resize((w2, h2), Image.LANCZOS), (x, y + 24)); d.text((x + 4, y + 4), '%s  %s  x %g..%g  y %g..%g' % (NAMES[nm], T, AREAS[a][0], AREAS[a][2], AREAS[a][1], AREAS[a][3]), fill='black')
    m.save('%s/look/%s_six_%s.png' % (O, T, a))
PY
ls "$O/look" | grep -c "^${T}_"
