#!/bin/sh
# Stage 8 (mounting holes 2.75 mm; LCSC numbers; MOTOR_IN1 to GPIO18 and both PWM lines round the north-west): rebuild from the stage-7
# commit c9a67c8 (board and schematic of a9d0778), then check.  Usage: sh run.sh <1|2|3>   (jobs 1..N are applied, in order)
set -e
HERE=$(cd "$(dirname "$0")" && pwd); ROOT=$(cd "$HERE/../../../.." && pwd); D=experiments/pi_zero_fit_01/board; P=Nereus_Pi_Shield_Adin2111
OUT=~/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/stage8_pwm_holes; mkdir -p "$OUT"
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
Q='grep -v -e traits -e Debug: -e swig/python'
cd "$ROOT"; IN=c9a67c8; BASE=d30920b; N=${1:?job number 1, 2 or 3}; TAG=s8_job$N
pgrep -lf kicad.app && { echo "KiCad is open"; exit 1; }
git show $BASE:$D/$P.kicad_pcb > "$OUT/board_stage2c.kicad_pcb"
git show $IN:$D/$P.kicad_pcb > "$ROOT/$D/$P.kicad_pcb"
for f in $(git ls-tree --name-only $IN $D/ | grep kicad_sch); do git show $IN:$f > "$ROOT/$f"; done
echo "== job 1 mounting holes"; $PY -B "$HERE/job1_holes.py" "$ROOT/$D/$P.kicad_pcb" "$ROOT/Nereus_Pi_Shield_Adin2111/Pi_Zero_outline.dxf" 2>&1 | $Q
if [ $N -ge 2 ]; then echo "== job 2 LCSC numbers"; python3 -B "$HERE/job2_lcsc.py" "$ROOT/$D" "$HOME/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/stage7_lcsc/LCSC_LOOKUP.md"
  (cd "$D" && $CLI sch export netlist -o "$OUT/netlist_s8_job2.net" $P.kicad_sch >/dev/null)
  $PY -B "$HERE/job2_sync.py" "$ROOT/$D/$P.kicad_pcb" "$OUT/netlist_s8_job2.net" 2>&1 | $Q; fi
if [ $N -ge 3 ]; then echo "== job 3 schematic"; python3 -B "$HERE/job3_schematic.py" "$ROOT/$D"
  (cd "$D" && $CLI sch export netlist -o "$OUT/netlist_s8_job3.net" $P.kicad_sch >/dev/null)
  echo "== job 3 board sync"; $PY -B "$HERE/job3_sync.py" --rip "$ROOT/$D/$P.kicad_pcb" "$OUT/board_stage2c.kicad_pcb" 2>&1 | $Q
  $PY -B "$HERE/job3_sync.py" "$ROOT/$D/$P.kicad_pcb" "$OUT/netlist_s8_job3.net" 2>&1 | $Q
  [ -n "$NOROUTE" ] && exit 0
  echo "== job 3 routing"; S3_BASE="$OUT/board_stage2c.kicad_pcb" $PY -B "$HERE/job3_route.py" "$ROOT/$D/$P.kicad_pcb" "$ROOT/$D/$P.kicad_pcb" "$OUT/log_s8_job3.json" 2>&1 | $Q || true; fi
$CLI pcb drc --severity-all --schematic-parity --format json -o "$OUT/drc_$TAG.json" "$ROOT/$D/$P.kicad_pcb" | grep -v Saved
python3 "$HERE/../stage3_routing/drc_summary.py" "$OUT/drc_$TAG.json" -v -u
(cd "$D" && $CLI sch erc --severity-all --format json -o "$OUT/erc_$TAG.json" $P.kicad_sch | tail -1)
python3 -B "$HERE/../stage2c_delta/ercdiff.py" "$OUT/erc_baseline_c9a67c8.json" "$OUT/erc_$TAG.json" | tail -6
echo "== lock check"; $PY -B "$HERE/lock8.py" "$OUT/board_stage2c.kicad_pcb" "$ROOT/$D/$P.kicad_pcb" 2>&1 | $Q || true
$PY -B "$HERE/../stage5_gpio_row/planes.py" "$ROOT/$D/$P.kicad_pcb" 2>/dev/null > "$OUT/planes_$TAG.txt"; diff "$OUT/planes_head.txt" "$OUT/planes_$TAG.txt" && echo "planes: same as head" || true
$PY -B "$HERE/../stage6_review_fixes/checks.py" "$ROOT/$D/$P.kicad_pcb" "$OUT/board_stage2c.kicad_pcb" 2>/dev/null > "$OUT/checks_$TAG.txt"
if [ $N -ge 3 ]; then $PY -B "$HERE/measure.py" "$ROOT/$D/$P.kicad_pcb" MOTOR_IN1 MOTOR_IN2 GPIO12 ADIN_TIMER 2>&1 | $Q > "$OUT/measure_$TAG.txt"; $PY -B "$HERE/nognd.py" "$ROOT/$D/$P.kicad_pcb" MOTOR_IN1 MOTOR_IN2 2>&1 | $Q > "$OUT/nognd_$TAG.txt"; cat "$OUT/measure_$TAG.txt" "$OUT/nognd_$TAG.txt"; fi
for f in kicad_pro kicad_dru; do git diff --quiet $BASE -- $D/$P.$f && echo "identical to $BASE: .$f" || echo "!! .$f CHANGED"; done
git status --short
