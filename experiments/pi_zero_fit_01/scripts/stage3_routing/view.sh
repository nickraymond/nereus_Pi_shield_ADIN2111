#!/bin/sh
# Crop of copper layer(s) for a look. Usage: view.sh <board> <layers e.g. F.Cu or "F.Cu,B.Cu"> <x0> <y0> <x1> <y1> <out.png> [bw]   (new-frame mm; 65.5 px per mm)
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
T=$(mktemp -d); B="$1"; L="$2"; BW=""; [ -n "$8" ] && BW="--black-and-white"
$CLI pcb export svg --layers "$L,Edge.Cuts" --page-size-mode 2 --exclude-drawing-sheet $BW -o "$T/v.svg" "$B" >/dev/null 2>&1
qlmanage -t -s 5200 -o "$T" "$T/v.svg" >/dev/null 2>&1
$PY - "$T/v.svg.png" "$3" "$4" "$5" "$6" "$7" 2>/dev/null <<'PY'
import sys, wx
app = wx.App(False); im = wx.Image(sys.argv[1]); k = im.GetWidth() * 0.8187 / 65.0   # the thumbnail carries a margin; measured on a full-board render
x0, y0, x1, y1 = [float(a) for a in sys.argv[2:6]]
sub = im.GetSubImage(wx.Rect(int(x0 * k), int(y0 * k), int((x1 - x0) * k), int((y1 - y0) * k)))
sub.SaveFile(sys.argv[6], wx.BITMAP_TYPE_PNG)
PY
rm -rf "$T"
