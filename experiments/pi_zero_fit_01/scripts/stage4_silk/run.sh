#!/bin/sh
# Silkscreen clean-up on a scratch copy of the committed board folder. Usage: sh run.sh     (the repo's board is only read)
set -e
HERE=$(cd "$(dirname "$0")" && pwd); ROOT=$(cd "$HERE/../../../.." && pwd); P=Nereus_Pi_Shield_Adin2111
OUT=~/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/stage4_gpio_silk; S="$OUT/silk_scratch"
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
MOTE="$ROOT/KiCAD_reference_designs/20250409_BM_Mote_000639-AB/BM_Mote_000639-AB.kicad_pcb"
pgrep -lf kicad.app && { echo "KiCad is open"; exit 1; }
rm -rf "$S"; mkdir -p "$S"; cp -Rp "$ROOT/experiments/pi_zero_fit_01/board" "$S/board"; B="$S/board/$P.kicad_pcb"
$CLI pcb drc --severity-all --schematic-parity --format json -o "$OUT/drc_silk_before.json" "$B" | grep -v Saved
$PY -B "$HERE/silk.py" "$B" "$MOTE" "$OUT/silk_report.json" 2>&1 | grep -v -e traits -e Debug:
$CLI pcb drc --severity-all --schematic-parity --format json -o "$OUT/drc_silk_after.json" "$B" | grep -v Saved
python3 "$HERE/../stage3_routing/drc_summary.py" "$OUT/drc_silk_after.json"
echo "before:"; python3 "$HERE/split.py" "$OUT/drc_silk_before.json" "$OUT/silk_report.json"
echo "after:";  python3 "$HERE/split.py" "$OUT/drc_silk_after.json" "$OUT/silk_report.json" $1
$CLI pcb render --side top -w 2400 -h 1600 -o "$OUT/silk_top.png" "$B" >/dev/null; $CLI pcb render --side bottom -w 2400 -h 1600 -o "$OUT/silk_bottom.png" "$B" >/dev/null
$CLI pcb render --side top -w 6000 -h 4000 -o "$OUT/silk_top_big.png" "$B" >/dev/null; $CLI pcb render --side bottom -w 6000 -h 4000 -o "$OUT/silk_bottom_big.png" "$B" >/dev/null
$PY "$HERE/crop.py" "$OUT/silk_top_big.png" "$OUT/silk_zoom_west.png" top -0.5 5.5 22 34 2>/dev/null
$PY "$HERE/crop.py" "$OUT/silk_top_big.png" "$OUT/silk_zoom_south_w.png" top -0.5 26 33 40 2>/dev/null
$PY "$HERE/crop.py" "$OUT/silk_top_big.png" "$OUT/silk_zoom_south_e.png" top 30 26 65.5 40 2>/dev/null
$PY "$HERE/crop.py" "$OUT/silk_top_big.png" "$OUT/silk_zoom_east.png" top 50 0 65.5 26 2>/dev/null
$PY "$HERE/crop.py" "$OUT/silk_bottom_big.png" "$OUT/silk_zoom_se_bottom.png" bottom 40 26 65.5 40 2>/dev/null
$PY "$HERE/crop.py" "$OUT/silk_bottom_big.png" "$OUT/silk_zoom_sw_bottom.png" bottom -0.5 26 33 40 2>/dev/null
$PY "$HERE/crop.py" "$OUT/silk_bottom_big.png" "$OUT/silk_zoom_nw_bottom.png" bottom -0.5 0 25 26 2>/dev/null
rm -f "$OUT/silk_zoom_south.png"
cd "$ROOT" && git status --short
