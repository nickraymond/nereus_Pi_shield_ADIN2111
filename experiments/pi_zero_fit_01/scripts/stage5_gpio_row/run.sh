#!/bin/sh
# Stage 5 (the pad row under J1): rebuild from the stage-4 board (commit 397fdfd) and the stage-3 schematic (5f43210), then check.  Usage: sh run.sh
set -e
HERE=$(cd "$(dirname "$0")" && pwd); ROOT=$(cd "$HERE/../../../.." && pwd); D=experiments/pi_zero_fit_01/board; P=Nereus_Pi_Shield_Adin2111
OUT=~/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/stage5_gpio_row; mkdir -p "$OUT"
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
Q='grep -v -e traits -e Debug: -e swig/python'
cd "$ROOT"; IN=397fdfd; SCH=5f43210; BASE=d30920b
pgrep -lf kicad.app && { echo "KiCad is open"; exit 1; }
git show $BASE:$D/$P.kicad_pcb > "$OUT/board_stage2c.kicad_pcb"
git show $IN:$D/$P.kicad_pcb > "$ROOT/$D/$P.kicad_pcb"; git show $SCH:$D/${P}_TopLevel.kicad_sch > "$ROOT/$D/${P}_TopLevel.kicad_sch"
echo "== step 1 schematic"; python3 -B "$HERE/step1_schematic.py" "$ROOT/$D"
(cd "$D" && $CLI sch export netlist -o "$OUT/netlist_s5.net" $P.kicad_sch >/dev/null && $CLI sch erc --severity-all --format json -o "$OUT/erc_s5.json" $P.kicad_sch | tail -1)
python3 -B "$HERE/../stage2c_delta/ercdiff.py" "$OUT/erc_baseline_397fdfd.json" "$OUT/erc_s5.json"
echo "== step 2 board sync"; $PY -B "$HERE/step2_sync.py" --remove "$ROOT/$D/$P.kicad_pcb" 2>&1 | $Q
$PY -B "$HERE/step2_sync.py" "$ROOT/$D/$P.kicad_pcb" "$OUT/netlist_s5.net" "$ROOT/$D/$P.kicad_pcb" 2>&1 | $Q
echo "== step 3 routing"; S3_BASE="$OUT/board_stage2c.kicad_pcb" $PY -B "$HERE/step3_route.py" "$ROOT/$D/$P.kicad_pcb" "$ROOT/$D/$P.kicad_pcb" "$OUT/log_s5.json" 2>&1 | $Q || true
if [ -f "$HERE/step4_review.py" ] && [ -z "$NO_STEP4" ]; then echo "== step 4 review fixes"; S3_BASE="$OUT/board_stage2c.kicad_pcb" $PY -B "$HERE/step4_review.py" "$ROOT/$D/$P.kicad_pcb" "$ROOT/$D/$P.kicad_pcb" "$OUT/log_s5_review.json" 2>&1 | $Q || true; fi
$CLI pcb drc --severity-all --schematic-parity --format json -o "$OUT/drc_s5.json" "$ROOT/$D/$P.kicad_pcb" | grep -v Saved
python3 "$HERE/../stage3_routing/drc_summary.py" "$OUT/drc_s5.json" -v -u
echo "== lock check"; $PY -B "$HERE/lock5.py" "$OUT/board_stage2c.kicad_pcb" "$ROOT/$D/$P.kicad_pcb" 2>&1 | $Q || true
for f in kicad_pro kicad_dru; do git diff --quiet $BASE -- $D/$P.$f && echo "identical to $BASE: .$f" || echo "!! .$f CHANGED"; done
git status --short
