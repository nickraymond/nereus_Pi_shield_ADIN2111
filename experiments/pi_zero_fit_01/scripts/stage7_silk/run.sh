#!/bin/sh
# Stage 7 silkscreen proposal on a scratch copy of the committed board folder. Usage: sh run.sh [-v]     (the repo's board is only read)
set -e
HERE=$(cd "$(dirname "$0")" && pwd); ROOT=$(cd "$HERE/../../../.." && pwd); P=Nereus_Pi_Shield_Adin2111
OUT=~/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/stage7_silk; S="$OUT/silk_scratch"
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
MOTE="$ROOT/KiCAD_reference_designs/20250409_BM_Mote_000639-AB/BM_Mote_000639-AB.kicad_pcb"
FROZEN="$ROOT/Nereus_Pi_Shield_Adin2111/$P.kicad_pcb"; REPO="$ROOT/experiments/pi_zero_fit_01/board"
pgrep -lf kicad.app && { echo "KiCad is open"; exit 1; }
mkdir -p "$OUT"; rm -rf "$S"; mkdir -p "$S"; cp -Rp "$REPO" "$S/board"; B="$S/board/$P.kicad_pcb"
$CLI pcb drc --severity-all --schematic-parity --format json -o "$OUT/drc_silk_before.json" "$B" | grep -v Saved
$PY -B "$HERE/silk.py" "$B" "$MOTE" "$FROZEN" "$OUT/silk_report.json" 2>&1 | grep -v -e traits -e Debug:
$CLI pcb drc --severity-all --schematic-parity --format json -o "$OUT/drc_silk_after.json" "$B" | grep -v Saved
python3 "$HERE/../stage3_routing/drc_summary.py" "$OUT/drc_silk_before.json" | head -1
python3 "$HERE/../stage3_routing/drc_summary.py" "$OUT/drc_silk_after.json"
echo "before:"; python3 "$HERE/split.py" "$OUT/drc_silk_before.json" "$OUT/silk_report.json"
echo "after:";  python3 "$HERE/split.py" "$OUT/drc_silk_after.json" "$OUT/silk_report.json" $1
$PY -B "$HERE/check.py" "$REPO/$P.kicad_pcb" "$B" "$OUT/silk_report.json" 2>&1 | grep -v -e traits -e Debug:
$CLI sch export netlist --format kicadxml -o "$OUT/netlist.xml" "$S/board/$P.kicad_sch" >/dev/null
python3 "$HERE/netcheck.py" "$OUT/netlist.xml" "$OUT/silk_report.json"
[ "$NORENDER" = 1 ] && exit 0
$CLI pcb render --side top -w 2400 -h 1600 -o "$OUT/silk_top.png" "$B" >/dev/null; $CLI pcb render --side bottom -w 2400 -h 1600 -o "$OUT/silk_bottom.png" "$B" >/dev/null
$CLI pcb render --side top -w 6000 -h 4000 -o "$OUT/silk_top_big.png" "$B" >/dev/null; $CLI pcb render --side bottom -w 6000 -h 4000 -o "$OUT/silk_bottom_big.png" "$B" >/dev/null
z() { $PY "$HERE/crop.py" "$OUT/silk_$1_big.png" "$OUT/zoom_$1_$2.png" $1 $3 $4 $5 $6 2>/dev/null; }
z top west_end -0.5 5 22 34;        z top row_west 5 -0.5 34 13;      z top row_east 31 -0.5 65.5 13
z top south_west -0.5 26 31 40;     z top south_east 29 26 65.5 40;   z top led_group 28 30 43 40;    z top east_end 50 5 65.5 26
z bottom row_west 5 -0.5 34 13;     z bottom row_east 31 -0.5 65.5 13
z bottom south_east 38 24 65.5 40;  z bottom south_west -0.5 22 27 40; z bottom south_mid 20 26 45 40
z bottom mid_west -0.5 8 30 26;     z bottom mid_east 30 8 65.5 30
cd "$ROOT" && git status --short
