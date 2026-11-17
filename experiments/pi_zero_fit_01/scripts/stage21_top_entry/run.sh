#!/bin/sh
# Stage 21 (top-entry connectors; only J9 fits, see job21.py). Usage: sh run.sh build | gates
set -e
HERE=$(cd "$(dirname "$0")" && pwd); ROOT=$(cd "$HERE/../../../.." && pwd); D=experiments/pi_zero_fit_01/board; P=Nereus_Pi_Shield_Adin2111
OUT=~/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/stage21_top_entry; mkdir -p "$OUT"
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
q() { grep -v -e traits -e Debug: -e swig/python -e kimath -e Overflow -e '^$' || true; }
N=${1:?usage: sh run.sh build | gates}; cd "$ROOT"; IN=4676018; B="$ROOT/$D/$P.kicad_pcb"
pgrep -lf kicad.app && { echo "KiCad is open"; exit 1; }
git show $IN:$D/$P.kicad_pcb > "$OUT/board_$IN.kicad_pcb"
case "$N" in
build) git diff --quiet $IN -- $D || { echo "build starts from $IN"; exit 1; }
   echo "== fit of the five vertical footprints"; $PY -B "$HERE/fit21.py" "$B" 2>&1 | q | tee "$OUT/fit21.txt"
   echo "== stage 21: J9 top-entry"; $PY -B "$HERE/job21.py" "$B" "$OUT/log_job21.json" 2>&1 | q
   git checkout $IN -- $D/$P.kicad_pro 2>/dev/null || true     # SaveBoard rewrites the project file: put it back
   echo "== schematic fields"; python3 "$HERE/sch21.py" "$D";;
gates) ;;
esac
$CLI pcb drc --severity-all --schematic-parity --format json -o "$OUT/drc_job21.json" "$B" | grep -v Saved
python3 "$HERE/../stage3_routing/drc_summary.py" "$OUT/drc_job21.json" -v -u
python3 "$HERE/../stage11_silk_logo/drcdiff.py" "$OUT/drc_base.json" "$OUT/drc_job21.json"
(cd "$D" && $CLI sch erc --severity-all --format json -o "$OUT/erc_job21.json" $P.kicad_sch >/dev/null)
python3 -c "import json,sys,collections; d=json.load(open(sys.argv[1])); v=[x for s in d['sheets'] for x in s['violations']]; print('ERC: %s' % dict(collections.Counter((x['severity'], x['type']) for x in v)))" "$OUT/erc_job21.json"
echo "== lock check"; $PY -B "$HERE/lock21.py" "$OUT/board_$IN.kicad_pcb" "$B" 2>&1 | q
git diff --quiet $IN -- $D/$P.kicad_pro $D/$P.kicad_dru && echo ".kicad_pro / .kicad_dru: identical to $IN" || echo "!! .kicad_pro / .kicad_dru differ from $IN"
git status --short
