#!/bin/sh
# Per-copper-layer SVG plots + PNG previews of a board. Usage: plots.sh <board.kicad_pcb> <out dir> [tag]
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
B="$1"; O="$2"; T="${3:-}"; mkdir -p "$O"
for L in "Top Layer:F.Cu:top" "Internal 1:In1.Cu:in1" "GND Plane:In2.Cu:gnd" "Internal 2:In3.Cu:in2" "PWR Plane:In4.Cu:pwr" "6 Bottom Layer:B.Cu:bot"; do
  id=$(echo "$L" | cut -d: -f2); nm=$(echo "$L" | cut -d: -f3)
  $CLI pcb export svg --layers "$id,Edge.Cuts" --page-size-mode 2 --exclude-drawing-sheet --black-and-white -o "$O/cu_${nm}${T}.svg" "$B" >/dev/null 2>&1 || echo "svg failed $nm"
  qlmanage -t -s 2600 -o "$O" "$O/cu_${nm}${T}.svg" >/dev/null 2>&1 && mv "$O/cu_${nm}${T}.svg.png" "$O/cu_${nm}${T}.png"
done
ls "$O" | grep "cu_.*${T}.png" | wc -l
