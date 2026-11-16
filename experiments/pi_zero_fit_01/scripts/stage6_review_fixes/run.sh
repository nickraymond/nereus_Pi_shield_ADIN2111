#!/bin/sh
# Stage 6 (electrical review fixes, converter heat spreading): rebuild from the stage-5 board (commit 76d258b), then check.  Usage: sh run.sh [1]   (1 = step 1 only)
set -e
HERE=$(cd "$(dirname "$0")" && pwd); ROOT=$(cd "$HERE/../../../.." && pwd); D=experiments/pi_zero_fit_01/board; P=Nereus_Pi_Shield_Adin2111
OUT=~/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/stage6_review_fixes; mkdir -p "$OUT"
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
Q='grep -v -e traits -e Debug: -e swig/python'
cd "$ROOT"; IN=76d258b; BASE=d30920b; TAG=s6${1:+_step$1}
pgrep -lf kicad.app && { echo "KiCad is open"; exit 1; }
git show $BASE:$D/$P.kicad_pcb > "$OUT/board_stage2c.kicad_pcb"
git show $IN:$D/$P.kicad_pcb > "$ROOT/$D/$P.kicad_pcb"
echo "== step 1 review findings"; S3_BASE="$OUT/board_stage2c.kicad_pcb" $PY -B "$HERE/step1_review.py" "$ROOT/$D/$P.kicad_pcb" "$ROOT/$D/$P.kicad_pcb" "$OUT/log_s6_step1.json" 2>&1 | $Q || true
if [ -z "$1" ] && [ -f "$HERE/step2_heat.py" ]; then echo "== step 2 converter heat spreading"; S3_BASE="$OUT/board_stage2c.kicad_pcb" $PY -B "$HERE/step2_heat.py" "$ROOT/$D/$P.kicad_pcb" "$ROOT/$D/$P.kicad_pcb" "$OUT/log_s6_step2.json" 2>&1 | $Q || true; fi
$CLI pcb drc --severity-all --schematic-parity --format json -o "$OUT/drc_$TAG.json" "$ROOT/$D/$P.kicad_pcb" | grep -v Saved
python3 "$HERE/../stage3_routing/drc_summary.py" "$OUT/drc_$TAG.json" -v -u
(cd "$D" && $CLI sch erc --severity-all --format json -o "$OUT/erc_$TAG.json" $P.kicad_sch | tail -1)
python3 -B "$HERE/../stage2c_delta/ercdiff.py" "$OUT/erc_baseline_76d258b.json" "$OUT/erc_$TAG.json" | tail -3
echo "== lock check"; $PY -B "$HERE/lock6.py" "$OUT/board_stage2c.kicad_pcb" "$ROOT/$D/$P.kicad_pcb" 2>&1 | $Q || true
$PY -B "$HERE/../stage5_gpio_row/planes.py" "$ROOT/$D/$P.kicad_pcb" 2>/dev/null > "$OUT/planes_$TAG.txt"; diff "$OUT/planes_head.txt" "$OUT/planes_$TAG.txt" && echo "planes: same as head" || true
$PY -B "$HERE/checks.py" "$ROOT/$D/$P.kicad_pcb" "$OUT/board_stage2c.kicad_pcb" 2>/dev/null > "$OUT/checks_$TAG.txt"
for f in kicad_pro kicad_dru; do git diff --quiet $BASE -- $D/$P.$f && echo "identical to $BASE: .$f" || echo "!! .$f CHANGED"; done
git status --short
