#!/bin/sh
# Stage 16 (JP2 / JP3 / JP4 2.0 mm north, labels below them). Usage: sh run.sh head | build | gates
set -e
HERE=$(cd "$(dirname "$0")" && pwd); ROOT=$(cd "$HERE/../../../.." && pwd); D=experiments/pi_zero_fit_01/board; P=Nereus_Pi_Shield_Adin2111
OUT=~/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/stage16_jumpers; mkdir -p "$OUT"
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
q() { grep -v -e traits -e Debug: -e swig/python -e kimath -e Overflow -e '^$' || true; }
N=${1:?usage: sh run.sh head | build | gates}; cd "$ROOT"; IN=e51dfdc; BASE=d30920b; B="$ROOT/$D/$P.kicad_pcb"
pgrep -lf kicad.app && { echo "KiCad is open"; exit 1; }
git show $IN:$D/$P.kicad_pcb > "$OUT/board_head_$IN.kicad_pcb"; git show $BASE:$D/$P.kicad_pcb > "$OUT/board_stage2c.kicad_pcb"
gates() {
  $CLI pcb drc --severity-all --schematic-parity --format json -o "$OUT/drc_$1.json" "$B" | grep -v Saved
  python3 "$HERE/../stage3_routing/drc_summary.py" "$OUT/drc_$1.json" -v -u
  [ "$1" != head ] && python3 "$HERE/../stage11_silk_logo/drcdiff.py" "$OUT/drc_head.json" "$OUT/drc_$1.json"
  (cd "$D" && $CLI sch erc --severity-all --format json -o "$OUT/erc_$1.json" $P.kicad_sch >/dev/null)
  python3 -c "import json,sys,collections; d=json.load(open(sys.argv[1])); v=[x for s in d['sheets'] for x in s['violations']]; print('ERC %d: %s' % (len(v), dict(collections.Counter(x['type'] for x in v))))" "$OUT/erc_$1.json"
  [ "$1" = head ] && return 0
  echo "== lock check"; $PY -B "$HERE/lock16.py" "$OUT/board_head_$IN.kicad_pcb" "$B" "$OUT/board_stage2c.kicad_pcb" 2>&1 | q
  git diff --quiet $IN -- $(git ls-files $D | grep -v kicad_pcb) && echo "every other file in board/ (.kicad_pro, .kicad_dru, schematic, libraries): identical to $IN" || { echo "!! files differ from $IN:"; git diff --stat $IN -- $(git ls-files $D | grep -v kicad_pcb) | cat; }
}
case "$N" in
head) git diff --quiet $IN -- $D || { echo "board/ is not $IN"; exit 1; }; gates head; exit 0;;
build) git diff --quiet $IN -- $D || { echo "build starts from $IN"; exit 1; }
   echo "== stage 16: jumpers 2.0 mm north"; $PY -B "$HERE/job16.py" "$B" "$OUT/log_job16.json" 2>&1 | q
   git checkout $IN -- $D/$P.kicad_pro 2>/dev/null || true;;    # SaveBoard rewrites the project file: put it back
gates) ;;
esac
gates job16
git status --short
