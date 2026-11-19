#!/bin/sh
# Routing stage B (planes): our zones round Sofar's block. Runs on copies outside git; only the .kicad_pcb is copied
# back into the worktree. Nothing is committed. Base = the board committed at HEAD (stage A), or the commit given.
set -e
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1
OUT=$HOME/NereusData/nereus_Pi_shield_ADIN2111/n6_shield/stageB
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
P=N6_Shield_ADIN2111; N=Nereus_Pi_Shield_Adin2111; BASE=${1:-HEAD}
if pgrep -lf KiCad | grep -v kicad-cli | grep -q .; then echo "KiCad is running: close it first"; exit 1; fi
rm -rf "$OUT/work" "$OUT/base"; mkdir -p "$OUT/work" "$OUT/base"
git -C ../.. archive $BASE $P | tar -x -C "$OUT/work" --strip-components=1
git -C ../.. archive $BASE $P | tar -x -C "$OUT/base" --strip-components=1
echo "base: $(git -C ../.. rev-parse --short $BASE)"
$PY stepB_planes.py "$OUT/work/$N.kicad_pcb" >"$OUT/stepB.log" 2>"$OUT/stepB.err" || { grep -v -E "swig|stdpbase" "$OUT/stepB.err" | tail -5; echo "stepB_planes.py FAILED"; exit 1; }
grep -v "swig/python detected" "$OUT/stepB.log"
for f in $N.kicad_pro $N.kicad_dru; do git -C ../.. show "$BASE:$P/$f" > "$OUT/work/$f"; done
( cd "$OUT/base" && $K pcb drc --schematic-parity --severity-all --format json -o "$OUT/drc_base.json" $N.kicad_pcb >/dev/null 2>&1 || true )
( cd "$OUT/work" && $K pcb drc --refill-zones --save-board --schematic-parity --severity-all --format json -o "$OUT/drc_B.json" $N.kicad_pcb >/dev/null 2>&1 || true
  $K pcb drc --schematic-parity --severity-all --format report -o "$OUT/drc_B.rpt" $N.kicad_pcb >/dev/null 2>&1 || true )
for f in $N.kicad_pro $N.kicad_dru; do git -C ../.. show "$BASE:$P/$f" | cmp -s - "$OUT/work/$f" || { echo "kicad-cli changed $f"; exit 1; }; done
python3 -B ../stage0/drcsum.py "$OUT/drc_B.json" "$OUT/drc_base.json" | sed 's/starting board/before the stage/' | tee "$OUT/drcsum_B.txt"
$PY ../stageA/lockcheck_all.py "$OUT/base/$N.kicad_pcb" "$OUT/work/$N.kicad_pcb" 2>/dev/null | grep -v "swig/python" | tee "$OUT/lock_B.txt"
$PY planecheck.py "$OUT/work/$N.kicad_pcb" "$OUT/base/$N.kicad_pcb" 2>/dev/null | grep -v "swig/python" | tee "$OUT/plane_B.txt"
$PY ../stageA/buscheck.py "$OUT/work/$N.kicad_pcb" 2>/dev/null | grep -v "swig/python" | tail -6 | tee "$OUT/bus_B.txt"
cp "$OUT/work/$N.kicad_pcb" "../../$P/$N.kicad_pcb"
echo "files that differ from $BASE in $P (must be the board only):"; git -C ../.. status --short -- $P
i=1
for LYR in "Top Layer" "Internal 1" "GND Plane" "Internal 2" "PWR Plane" "6 Bottom Layer"; do
  n=$(echo "$LYR" | tr ' ' '_')
  ( cd "$OUT/work" && $K pcb export svg --layers "$LYR,Edge.Cuts" --mode-single --exclude-drawing-sheet --page-size-mode 2 -o "$OUT/B_L${i}_$n.svg" $N.kicad_pcb >/dev/null 2>&1 )
  echo "<html><body style='margin:0;background:#fff'><img src='B_L${i}_$n.svg' style='width:900px'></body></html>" > "$OUT/B_L${i}_$n.html"
  "$CHROME" --headless --disable-gpu --screenshot="$OUT/N6_shield_stageB_L${i}_$n.png" --window-size=900,1335 "file://$OUT/B_L${i}_$n.html" >/dev/null 2>&1
  i=$((i + 1))
done
ls "$OUT"/N6_shield_stageB_L*.png
