#!/bin/sh
# Plots of the six copper layers (colour, one PNG each, 5200 px) and crops of the areas stage 8 changed.
# Usage: sh look.sh <board.kicad_pcb> <out dir> <tag>     crops: <out dir>/<tag>_<area>_<layer>.png   (new-frame mm; 65.5 px per mm, as stage 3's view.sh)
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
B="$1"; O="$2"; T="$3"; mkdir -p "$O/plots_$T"
for L in F.Cu:top In1.Cu:in1 In2.Cu:gnd In3.Cu:in2 In4.Cu:pwr B.Cu:bot; do
  id=${L%%:*}; nm=${L##*:}
  $CLI pcb export svg --layers "$id,Edge.Cuts" --page-size-mode 2 --exclude-drawing-sheet -o "$O/plots_$T/cu_$nm.svg" "$B" >/dev/null 2>&1 || echo "svg failed $nm"
  qlmanage -t -s 5200 -o "$O/plots_$T" "$O/plots_$T/cu_$nm.svg" >/dev/null 2>&1 && mv "$O/plots_$T/cu_$nm.svg.png" "$O/plots_$T/cu_$nm.png"
done
python3 - "$O" "$T" <<'PY'
import sys
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
O, T = sys.argv[1:3]
AREAS = {'strip_w': (-0.5, -0.5, 33, 11), 'strip_e': (32, -0.5, 65.5, 11), 'west': (-0.5, 0, 14, 40), 'u1_y1': (34, 9, 54, 32), 'south_w': (-0.5, 28, 33, 40), 'south_e': (32, 28, 65.5, 40)}
for nm in ('top', 'in1', 'gnd', 'in2', 'pwr', 'bot'):
    im = Image.open('%s/plots_%s/cu_%s.png' % (O, T, nm)); k = im.width * 0.8187 / 65.0
    for a, (x0, y0, x1, y1) in AREAS.items():
        c = im.crop((int(max(x0, 0) * k), int(max(y0, 0) * k), int(x1 * k), int(y1 * k))); c.thumbnail((1900, 1900)); c.save('%s/look/%s_%s_%s.png' % (O, T, a, nm))
PY
ls "$O/look" | grep -c "^${T}_"
