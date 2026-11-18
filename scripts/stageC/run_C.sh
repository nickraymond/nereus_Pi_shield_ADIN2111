#!/bin/sh
# Routing stage C (power). Usage: [ALLOW_REF=<footprint the step may change>] run_C.sh <step script> <tag> [base commit]. Runs on copies outside git; only the
# .kicad_pcb is copied back into the worktree. Nothing is committed. Zones are refilled by kicad-cli after the edit.
set -e
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1
STEP=$1; TAG=$2; BASE=${3:-HEAD}
OUT=$HOME/NereusData/nereus_Pi_shield_ADIN2111/n6_shield/stage$TAG
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
P=N6_Shield_ADIN2111; N=Nereus_Pi_Shield_Adin2111
if pgrep -x kicad >/dev/null || pgrep -x pcbnew >/dev/null || pgrep -x eeschema >/dev/null; then echo "KiCad is running: close it first"; exit 1; fi
rm -rf "$OUT/work" "$OUT/base"; mkdir -p "$OUT/work" "$OUT/base"
git -C ../.. archive $BASE $P | tar -x -C "$OUT/work" --strip-components=1
git -C ../.. archive $BASE $P | tar -x -C "$OUT/base" --strip-components=1
echo "base: $(git -C ../.. rev-parse --short $BASE)"
$PY "$STEP" "$OUT/work/$N.kicad_pcb" >"$OUT/step.log" 2>"$OUT/step.err" || { grep -v -E "swig|stdpbase" "$OUT/step.err" | tail -5; echo "$STEP FAILED"; exit 1; }
grep -v "swig/python detected" "$OUT/step.log"
for f in $N.kicad_pro $N.kicad_dru; do git -C ../.. show "$BASE:$P/$f" > "$OUT/work/$f"; done
( cd "$OUT/base" && $K pcb drc --schematic-parity --severity-all --format json -o "$OUT/drc_base.json" $N.kicad_pcb >/dev/null 2>&1 || true )
( cd "$OUT/work" && $K pcb drc --refill-zones --save-board --schematic-parity --severity-all --format json -o "$OUT/drc.json" $N.kicad_pcb >/dev/null 2>&1 || true
  $K pcb drc --schematic-parity --severity-all --format report -o "$OUT/drc.rpt" $N.kicad_pcb >/dev/null 2>&1 || true )
for f in $N.kicad_pro $N.kicad_dru; do git -C ../.. show "$BASE:$P/$f" | cmp -s - "$OUT/work/$f" || { echo "kicad-cli changed $f"; exit 1; }; done
python3 -B ../stage0/drcsum.py "$OUT/drc.json" "$OUT/drc_base.json" -v | sed 's/starting board/before the stage/' | tee "$OUT/drcsum.txt" | grep -v -E "^   warning  (text_|silk_|lib_footprint|nonmirrored|padstack)|^   (items_not_allowed|skew_out_of_range) "
ALLOW=""; if [ -n "$ALLOW_REF" ]; then ALLOW="--allow $($PY -c "import sys,pcbnew; print(pcbnew.LoadBoard(sys.argv[1]).FindFootprintByReference(sys.argv[2]).m_Uuid.AsString())" "$OUT/base/$N.kicad_pcb" "$ALLOW_REF" 2>/dev/null | tail -1)"; echo "lock check allows $ALLOW_REF to change"; fi
$PY ../stageA/lockcheck_all.py "$OUT/base/$N.kicad_pcb" "$OUT/work/$N.kicad_pcb" $ALLOW 2>/dev/null | grep -v "swig/python" | tee "$OUT/lock.txt"
$PY ../stageB/planecheck.py "$OUT/work/$N.kicad_pcb" "$OUT/base/$N.kicad_pcb" 2>/dev/null | grep -v "swig/python" | tee "$OUT/plane.txt"
$PY ../stageA/buscheck.py "$OUT/work/$N.kicad_pcb" 2>/dev/null | grep -v "swig/python" | tail -1
cp "$OUT/work/$N.kicad_pcb" "../../$P/$N.kicad_pcb"
echo "files that differ from $BASE in $P (must be the board only):"; git -C ../.. status --short -- $P
i=1
for LYR in "Top Layer" "Internal 1" "GND Plane" "Internal 2" "PWR Plane" "6 Bottom Layer"; do
  n=$(echo "$LYR" | tr ' ' '_')
  ( cd "$OUT/work" && $K pcb export svg --layers "$LYR,Edge.Cuts" --mode-single --exclude-drawing-sheet --page-size-mode 2 -o "$OUT/L${i}_$n.svg" $N.kicad_pcb >/dev/null 2>&1 )
  echo "<html><body style='margin:0;background:#fff'><img src='L${i}_$n.svg' style='width:1400px'></body></html>" > "$OUT/L${i}_$n.html"
  "$CHROME" --headless --disable-gpu --screenshot="$OUT/N6_shield_stage${TAG}_L${i}_$n.png" --window-size=1400,2076 "file://$OUT/L${i}_$n.html" >/dev/null 2>&1
  i=$((i + 1))
done
ls "$OUT" | grep png
