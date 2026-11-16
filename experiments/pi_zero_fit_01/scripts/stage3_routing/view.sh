#!/bin/sh
# Crop of copper layer(s) for a look. Usage: view.sh <board> <layers e.g. F.Cu or "F.Cu,B.Cu"> <x0> <y0> <x1> <y1> <out.png> [px]   (new-frame mm)
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
T=$(mktemp -d); B="$1"; L="$2"
$CLI pcb export svg --layers "$L,Edge.Cuts" --page-size-mode 0 --exclude-drawing-sheet -o "$T/v.svg" "$B" >/dev/null 2>&1
python3 - "$T/v.svg" "$3" "$4" "$5" "$6" <<'PY'
import sys, re
p = sys.argv[1]; x0, y0, x1, y1 = [float(a) for a in sys.argv[2:6]]; s = open(p).read()
DX, DY = 113.47, 89.34          # page mode 0 keeps board coordinates (mm) in the viewBox
w, h = x1 - x0, y1 - y0; side = max(w, h)
s = re.sub(r'viewBox="[^"]*"', 'viewBox="%.4f %.4f %.4f %.4f"' % (x0 + DX, y0 + DY, side, side), s, count=1)
s = re.sub(r'width="[^"]*"', 'width="%.4fmm"' % side, s, count=1); s = re.sub(r'height="[^"]*"', 'height="%.4fmm"' % side, s, count=1)
open(p, 'w').write(s)
PY
qlmanage -t -s "${8:-1400}" -o "$T" "$T/v.svg" >/dev/null 2>&1
mv "$T/v.svg.png" "$7"; rm -rf "$T"
