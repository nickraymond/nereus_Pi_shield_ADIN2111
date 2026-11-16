#!/bin/sh
# Stage 9 (MOTOR_IN1 / MOTOR_IN2 change places at J1 pins 12 / 33; the two swap vias and the Internal 1 piece go): rebuild from the stage-8
# head 61e1a9d, then check.  Usage: sh run.sh        (HEADONLY=1: measure the head board only, change nothing)
set -e
HERE=$(cd "$(dirname "$0")" && pwd); ROOT=$(cd "$HERE/../../../.." && pwd); D=experiments/pi_zero_fit_01/board; P=Nereus_Pi_Shield_Adin2111
OUT=~/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/stage9_pwm_swap; mkdir -p "$OUT"
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
Q='grep -v -e traits -e Debug: -e swig/python'
cd "$ROOT"; IN=61e1a9d; BASE=d30920b
pgrep -lf kicad.app && { echo "KiCad is open"; exit 1; }
git show $BASE:$D/$P.kicad_pcb > "$OUT/board_stage2c.kicad_pcb"
git show $IN:$D/$P.kicad_pcb > "$ROOT/$D/$P.kicad_pcb"
for f in $(git ls-tree --name-only $IN $D/ | grep kicad_sch); do git show $IN:$f > "$ROOT/$f"; done
measure() {      # <tag>: DRC, ERC, planes, stage 6's checks, the two nets' distances and no-GND runs, on the board as it stands
  $CLI pcb drc --severity-all --schematic-parity --format json -o "$OUT/drc_$1.json" "$ROOT/$D/$P.kicad_pcb" | grep -v Saved
  python3 "$HERE/../stage3_routing/drc_summary.py" "$OUT/drc_$1.json" -v -u
  (cd "$D" && $CLI sch erc --severity-all --format json -o "$OUT/erc_$1.json" $P.kicad_sch | tail -1)
  $PY -B "$HERE/../stage5_gpio_row/planes.py" "$ROOT/$D/$P.kicad_pcb" 2>/dev/null > "$OUT/planes_$1.txt"
  $PY -B "$HERE/../stage6_review_fixes/checks.py" "$ROOT/$D/$P.kicad_pcb" "$OUT/board_stage2c.kicad_pcb" 2>/dev/null > "$OUT/checks_$1.txt"
  $PY -B "$HERE/measure.py" "$ROOT/$D/$P.kicad_pcb" MOTOR_IN1 MOTOR_IN2 2>&1 | $Q > "$OUT/measure_$1.txt"; $PY -B "$HERE/nognd.py" "$ROOT/$D/$P.kicad_pcb" MOTOR_IN1 MOTOR_IN2 2>&1 | $Q > "$OUT/nognd_$1.txt"
  cat "$OUT/measure_$1.txt" "$OUT/nognd_$1.txt"; grep -e '^MOTOR_IN' -e 'MOTOR_IN[12]  ' "$OUT/checks_$1.txt" || true
}
if [ -n "$HEADONLY" ]; then echo "== head $IN"; cp "$ROOT/$D/$P.kicad_pcb" "$OUT/board_head_$IN.kicad_pcb"; measure head; git status --short; exit 0; fi
echo "== step 1 schematic"; python3 -B "$HERE/step1_schematic.py" "$ROOT/$D"
(cd "$D" && $CLI sch export netlist -o "$OUT/netlist_s9.net" $P.kicad_sch >/dev/null)
echo "== step 2 board sync"; $PY -B "$HERE/step2_sync.py" --rip "$ROOT/$D/$P.kicad_pcb" "$OUT/board_stage2c.kicad_pcb" 2>&1 | $Q
$PY -B "$HERE/step2_sync.py" "$ROOT/$D/$P.kicad_pcb" "$OUT/netlist_s9.net" 2>&1 | $Q
echo "== step 3 routing"; $PY -B "$HERE/step3_route.py" "$ROOT/$D/$P.kicad_pcb" "$ROOT/$D/$P.kicad_pcb" "$OUT/log_s9.json" 2>&1 | $Q || true
measure s9
python3 -B "$HERE/../stage2c_delta/ercdiff.py" "$OUT/erc_head.json" "$OUT/erc_s9.json" | tail -6
echo "== lock check"; $PY -B "$HERE/lock9.py" "$OUT/board_stage2c.kicad_pcb" "$ROOT/$D/$P.kicad_pcb" "$OUT/board_head_$IN.kicad_pcb" 2>&1 | $Q || true
diff "$OUT/planes_head.txt" "$OUT/planes_s9.txt" && echo "planes: same as head" || true
for f in kicad_pro kicad_dru; do git diff --quiet $BASE -- $D/$P.$f && echo "identical to $BASE: .$f" || echo "!! .$f CHANGED"; done
git status --short
