#!/bin/sh
# Rebuild the stage-2 schematic from the baseline copy, step by step, then run the checks.
set -e
cd "$(dirname "$0")"
S=..
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
export PYTHONDONTWRITEBYTECODE=1
cp $S/board_baseline/*.kicad_sch $S/board_baseline/fp-lib-table $S/board_baseline/sym-lib-table $S/board/
rm -rf $S/board/urchin.pretty $S/board/urchin.kicad_sym
echo "step 0: libraries"
python3 step0_libs.py
rm -f $S/render/urchin_sym_parsecheck.kicad_sym
$K sym upgrade --force -o $S/render/urchin_sym_parsecheck.kicad_sym $S/board/urchin.kicad_sym | tail -1
$PY step0_footprint.py 2>&1 | grep -v wxApp
test -f $S/board/urchin.pretty/MP6550GG.kicad_mod
for s in step1_remove.py step2_bus_connectors.py step3_motor.py step4_adc.py step5_notes.py; do
  [ -f $s ] || continue
  echo "$s"
  python3 $s
done
sh check.sh
sh render.sh
