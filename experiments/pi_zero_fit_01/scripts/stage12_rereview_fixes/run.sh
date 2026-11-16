#!/bin/sh
# Stage 12 (re-review fixes N1, N2, N4 / N9, N5; larger logo). Usage: sh run.sh head | 1 | 2 | 3 | 4 | gates <n>
#   head     gates on the head board 2bf006f (baseline files)
#   1..4     applies that one job to the board as it stands, then the gates. Built and committed in the order 1, 3, 4, 2 (job 2 last: it moves a via
#            of the frozen board, so it is the commit that can be dropped alone); each job starts from the commit before it (job 1 from 2bf006f)
#   gates n  the gates alone, as after job n
set -e
HERE=$(cd "$(dirname "$0")" && pwd); ROOT=$(cd "$HERE/../../../.." && pwd); D=experiments/pi_zero_fit_01/board; P=Nereus_Pi_Shield_Adin2111
OUT=~/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/stage12_rereview_fixes; mkdir -p "$OUT"
S11=~/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/stage11_silk_logo
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
q() { grep -v -e traits -e Debug: -e swig/python || true; }
S7="$HERE/../stage7_silk"; MOTE="$ROOT/KiCAD_reference_designs/20250409_BM_Mote_000639-AB/BM_Mote_000639-AB.kicad_pcb"; FROZEN="$ROOT/Nereus_Pi_Shield_Adin2111/$P.kicad_pcb"
N=${1:?usage: sh run.sh head | 1 | 2 | 3 | 4 | gates <n>}; cd "$ROOT"; IN=2bf006f; BASE=d30920b; B="$ROOT/$D/$P.kicad_pcb"
export F1VIA=bfd1637c-3da6-4060-8bca-e9443c262415      # the frozen board's via at (4.267, 17.687), 5V_LIFEPO4: job 2 moves it
pgrep -lf kicad.app && { echo "KiCad is open"; exit 1; }
git show $BASE:$D/$P.kicad_pcb > "$OUT/board_stage2c.kicad_pcb"; git show $IN:$D/$P.kicad_pcb > "$OUT/board_head_$IN.kicad_pcb"
gates() {        # <tag> <job>
  $CLI pcb drc --severity-all --schematic-parity --format json -o "$OUT/drc_$1.json" "$B" | grep -v Saved
  python3 "$HERE/../stage3_routing/drc_summary.py" "$OUT/drc_$1.json" -v -u
  [ -f "$OUT/drc_head.json" ] && [ "$1" != head ] && python3 "$HERE/../stage11_silk_logo/drcdiff.py" "$OUT/drc_head.json" "$OUT/drc_$1.json"
  (cd "$D" && $CLI sch erc --severity-all --format json -o "$OUT/erc_$1.json" $P.kicad_sch >/dev/null)
  python3 -c "import json,sys,collections; d=json.load(open(sys.argv[1])); v=[x for s in d['sheets'] for x in s['violations']]; print('ERC %d: %s' % (len(v), dict(collections.Counter(x['type'] for x in v))))" "$OUT/erc_$1.json"
  $PY -B "$HERE/../stage5_gpio_row/planes.py" "$B" 2>/dev/null > "$OUT/planes_$1.txt"
  $PY -B "$HERE/row_measure.py" "$B" 2>&1 | q > "$OUT/row_$1.txt"; tail -8 "$OUT/row_$1.txt"
  $PY -B "$HERE/../stage5_gpio_row/via_in_pad.py" "$B" "$OUT/board_stage2c.kicad_pcb" "$FROZEN" 2>&1 | q > "$OUT/via_in_pad_$1.txt"; tail -1 "$OUT/via_in_pad_$1.txt"
  $PY -B "$HERE/pwm_fb.py" "$B" 2>&1 | q > "$OUT/pwm_fb_$1.txt"; cat "$OUT/pwm_fb_$1.txt"
  [ "$1" = head ] && return 0
  python3 "$HERE/planes_cmp.py" "$OUT/planes_head.txt" "$OUT/planes_$1.txt" || true
  echo "== lock check"; $PY -B "$HERE/lock12.py" "$OUT/board_stage2c.kicad_pcb" "$B" "$OUT/board_head_$IN.kicad_pcb" $2 2>&1 | q
  for f in kicad_pro kicad_dru; do git diff --quiet $BASE -- $D/$P.$f && echo "identical to $BASE: .$f" || echo "!! .$f CHANGED"; done
  git diff --quiet $IN -- $(git ls-files $D | grep -v -e kicad_pcb) && echo "every other file in board/ (schematic, libraries, tables, project): identical to $IN" || { echo "!! files differ from $IN:"; git diff --stat $IN -- $(git ls-files $D | grep -v kicad_pcb) | cat; }
  $CLI sch export netlist --format kicadxml -o "$OUT/netlist.xml" "$ROOT/$D/$P.kicad_sch" >/dev/null
  python3 "$S7/netcheck.py" "$OUT/netlist.xml" "$OUT/silk_report_s12.json" > "$OUT/netcheck_$1.txt"; echo "netcheck.py: $(grep -c ' OK$' "$OUT/netcheck_$1.txt") rows OK, $(grep -c MISMATCH "$OUT/netcheck_$1.txt" || true) MISMATCH"
  $PY -B "$HERE/rowlabels.py" "$B" "$OUT/silk_report_s12.json" 2>&1 | q
}
case "$N" in
head) git diff --quiet $IN -- $D || { echo "board/ is not $IN"; exit 1; }; gates head 0; exit 0;;
gates) N=$2;;
1) git diff --quiet $IN -- $D || { echo "job 1 starts from $IN"; exit 1; }
   echo "== job 1: pad row"; $PY -B "$HERE/job1_row.py" "$B" "$OUT/board_stage2c.kicad_pcb" "$S11/silk_report.json" "$OUT/silk_report_s12.json" "$OUT/log_job1.json" 2>&1 | q;;
2) git diff --quiet HEAD -- $D || { echo "job 2 starts from the commit of job 4"; exit 1; }
   echo "== job 2: via at F1 pad 1"; $PY -B "$HERE/job2_f1.py" "$B" "$OUT/log_job2.json" 2>&1 | q;;
3) git diff --quiet HEAD -- $D || { echo "job 3 starts from the commit of job 1"; exit 1; }
   echo "== job 3: PWM pair's bend"; $PY -B "$HERE/job3_pwm.py" "$B" "$OUT/board_stage2c.kicad_pcb" "$OUT/log_job3.json" 2>&1 | q;;
4) git diff --quiet HEAD -- $D || { echo "job 4 starts from the commit of job 3"; exit 1; }
   echo "== job 4: larger logo and name"; $PY -B "$HERE/logo12.py" --remove "$B" 2>&1 | q
   VIAS=tented WR=1.0 $PY -B "$HERE/logo12.py" "$B" "$FROZEN" "$OUT/logo_report.json" "$MOTE" 2>&1 | q      # PROP=frozen: logo and name in the frozen board's proportion instead (not built)
   ;;
esac
case "$N" in 1) DONE=1;; 3) DONE=13;; 4) DONE=134;; 2) DONE=1342;; esac
gates job$N $DONE
if [ -f "$OUT/logo_report.json" ] && [ "$N" != 1 ] && [ "$N" != 3 ]; then python3 "$HERE/../stage11_silk_logo/near.py" "$OUT/drc_job$N.json" "$OUT/logo_report.json"; $PY -B "$HERE/counters.py" "$B" 2>&1 | q | tee "$OUT/counters_job$N.txt"; fi
git status --short
