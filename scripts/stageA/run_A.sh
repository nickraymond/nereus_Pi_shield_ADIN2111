#!/bin/sh
# Routing stage A (bus): BM2_N and BM2_P on the top layer. Runs on copies outside git (pcbnew.SaveBoard rewrites the
# .kicad_pro beside the board); only the .kicad_pcb is copied back into the worktree. Nothing is committed.
# Base = the board committed at HEAD (stage 0c). Zones are refilled by kicad-cli after the edit.
set -e
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1
OUT=$HOME/NereusData/nereus_Pi_shield_ADIN2111/n6_shield/stageA
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
P=N6_Shield_ADIN2111; N=Nereus_Pi_Shield_Adin2111; BASE=${1:-HEAD}
if pgrep -lf KiCad | grep -v kicad-cli | grep -q .; then echo "KiCad is running: close it first"; exit 1; fi
rm -rf "$OUT/work" "$OUT/base"; mkdir -p "$OUT/work" "$OUT/base"
git -C ../.. archive $BASE $P | tar -x -C "$OUT/work" --strip-components=1
git -C ../.. archive $BASE $P | tar -x -C "$OUT/base" --strip-components=1
echo "base: $(git -C ../.. rev-parse --short $BASE)"
$PY stepA_bus.py "$OUT/work/$N.kicad_pcb" 2>"$OUT/stepA.err" | grep -v "swig/python detected" | tee "$OUT/stepA.log"
for f in $N.kicad_pro $N.kicad_dru; do git -C ../.. show "$BASE:$P/$f" > "$OUT/work/$f"; done
( cd "$OUT/base" && $K pcb drc --schematic-parity --severity-all --format json -o "$OUT/drc_base.json" $N.kicad_pcb >/dev/null 2>&1 || true )
( cd "$OUT/work" && $K pcb drc --refill-zones --save-board --schematic-parity --severity-all --format json -o "$OUT/drc_A.json" $N.kicad_pcb >/dev/null 2>&1 || true
  $K pcb drc --schematic-parity --severity-all --format report -o "$OUT/drc_A.rpt" $N.kicad_pcb >/dev/null 2>&1 || true )
for f in $N.kicad_pro $N.kicad_dru; do git -C ../.. show "$BASE:$P/$f" | cmp -s - "$OUT/work/$f" || { echo "kicad-cli changed $f"; exit 1; }; done
python3 -B ../stage0/drcsum.py "$OUT/drc_A.json" "$OUT/drc_base.json" | sed 's/starting board/before the stage/' | tee "$OUT/drcsum_A.txt"
$PY lockcheck_all.py "$OUT/base/$N.kicad_pcb" "$OUT/work/$N.kicad_pcb" 2>/dev/null | grep -v "swig/python" | tee "$OUT/lock_A.txt"
$PY buscheck.py "$OUT/work/$N.kicad_pcb" 2>/dev/null | grep -v "swig/python" | tee "$OUT/bus_A.txt"
cp "$OUT/work/$N.kicad_pcb" "../../$P/$N.kicad_pcb"
echo "files that differ from $BASE in $P (must be the board only):"; git -C ../.. status --short -- $P
( cd "$OUT/work" && $K pcb render --side top --quality basic --width 1500 --height 2100 -o "$OUT/N6_shield_stageA_top.png" $N.kicad_pcb >/dev/null 2>&1 || true )
ls -la "$OUT"/N6_shield_stageA_top.png
