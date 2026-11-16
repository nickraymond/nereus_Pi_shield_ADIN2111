#!/bin/sh
# Stage 11: (1) the approved stage-7 silkscreen goes onto the committed board, (2) Bristlemouth logo and board name on the bottom,
# (3) J4's two holes 1.1 -> 1.3 mm.  Usage: sh run.sh <1|2|3>   rebuilds jobs 1..N from the stage-9 head 2fd2945, then the gates.
# sh run.sh j4only: job 3 alone on the board as it stands (the committed job-2 board). A rebuild gives every new silkscreen item a new id, so the
# committed job 3 was made this way; sh run.sh 3 gives the same board but for those ids.
set -e
HERE=$(cd "$(dirname "$0")" && pwd); ROOT=$(cd "$HERE/../../../.." && pwd); D=experiments/pi_zero_fit_01/board; P=Nereus_Pi_Shield_Adin2111
OUT=~/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/stage11_silk_logo; mkdir -p "$OUT"; S="$OUT/silk_scratch"
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
Q='grep -v -e traits -e Debug: -e swig/python'
S7="$HERE/../stage7_silk"; MOTE="$ROOT/KiCAD_reference_designs/20250409_BM_Mote_000639-AB/BM_Mote_000639-AB.kicad_pcb"; FROZEN="$ROOT/Nereus_Pi_Shield_Adin2111/$P.kicad_pcb"
APPROVED=~/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/stage7_silk/silk_scratch/board/$P.kicad_pcb     # the proposal Nick saw
N=${1:?usage: sh run.sh <1|2|3>}; cd "$ROOT"; IN=2fd2945; BASE=d30920b; B="$ROOT/$D/$P.kicad_pcb"
pgrep -lf kicad.app && { echo "KiCad is open"; exit 1; }
git show $BASE:$D/$P.kicad_pcb > "$OUT/board_stage2c.kicad_pcb"; git show $IN:$D/$P.kicad_pcb > "$OUT/board_head_$IN.kicad_pcb"
if [ "$N" != j4only ]; then
git show $IN:$D/$P.kicad_pcb > "$B"; git show $IN:$D/${P}_TopLevel.kicad_sch > "$ROOT/$D/${P}_TopLevel.kicad_sch"; J4=WirePads_1x02_P3.20mm_Oval2.2x3.3mm_Drill
git show $IN:$D/nereus.pretty/${J4}1.1mm.kicad_mod > "$ROOT/$D/nereus.pretty/${J4}1.1mm.kicad_mod"; rm -f "$ROOT/$D/nereus.pretty/${J4}1.3mm.kicad_mod"
fi
gates() {        # <tag> <job>: DRC, ERC, lock check, project files
  $CLI pcb drc --severity-all --schematic-parity --format json -o "$OUT/drc_$1.json" "$B" | grep -v Saved
  python3 "$HERE/../stage3_routing/drc_summary.py" "$OUT/drc_$1.json" -v -u
  [ -f "$OUT/drc_head.json" ] && python3 "$HERE/drcdiff.py" "$OUT/drc_head.json" "$OUT/drc_$1.json"
  (cd "$D" && $CLI sch erc --severity-all --format json -o "$OUT/erc_$1.json" $P.kicad_sch >/dev/null)
  python3 -c "import json,sys,collections; d=json.load(open(sys.argv[1])); v=[x for s in d['sheets'] for x in s['violations']]; print('ERC %d: %s' % (len(v), dict(collections.Counter(x['type'] for x in v))))" "$OUT/erc_$1.json"
  [ "$1" = head ] && return 0
  echo "== lock check"; $PY -B "$HERE/lock11.py" "$OUT/board_stage2c.kicad_pcb" "$B" "$OUT/board_head_$IN.kicad_pcb" $2 2>&1 | $Q || true
  for f in kicad_pro kicad_dru; do git diff --quiet $BASE -- $D/$P.$f && echo "identical to $BASE: .$f" || echo "!! .$f CHANGED"; done
  git diff --quiet $IN -- $(git ls-files $D | grep -e kicad_sch -e kicad_sym -e lib-table) && echo "schematic, symbol libraries, library tables: identical to $IN" || { echo "schematic differs from $IN in:"; git diff --stat $IN -- $(git ls-files $D | grep -e kicad_sch -e kicad_sym -e lib-table) | cat; git diff -U0 $IN -- $D/${P}_TopLevel.kicad_sch | grep '^[-+][^-+]'; }
}
if [ "$N" != j4only ]; then
if [ "$N" = head ]; then gates head 0; exit 0; fi
echo "== job 1: the stage-7 silkscreen on the board (silk.py on a scratch copy of the folder; the board file alone is copied back)"
rm -rf "$S"; mkdir -p "$S"; cp -Rp "$ROOT/$D" "$S/board"
$PY -B "$S7/silk.py" "$S/board/$P.kicad_pcb" "$MOTE" "$FROZEN" "$OUT/silk_report.json" 2>&1 | $Q > "$OUT/silk_log.txt"; grep -e '^labels placed' -e '^net check' -e '^Menlo' -e '^our designators' "$OUT/silk_log.txt" | cut -c1-200
$PY -B "$S7/check.py" "$B" "$S/board/$P.kicad_pcb" "$OUT/silk_report.json" 2>&1 | $Q
$PY -B "$HERE/same_silk.py" "$APPROVED" "$S/board/$P.kicad_pcb" 2>&1 | $Q
$CLI sch export netlist --format kicadxml -o "$OUT/netlist.xml" "$ROOT/$D/$P.kicad_sch" >/dev/null
python3 "$S7/netcheck.py" "$OUT/netlist.xml" "$OUT/silk_report.json" > "$OUT/netcheck.txt"; grep -c ' OK$' "$OUT/netcheck.txt" | sed 's/^/netcheck.py rows OK: /'; grep -c MISMATCH "$OUT/netcheck.txt" | sed 's/^/netcheck.py MISMATCH: /' || true
cp "$S/board/$P.kicad_pcb" "$B"
echo "silk warnings, ours / Sofar's, head:"; python3 "$S7/split.py" "$OUT/drc_head.json" "$OUT/silk_report.json"
if [ "$N" = 1 ]; then gates job1 1; echo "after job 1:"; python3 "$S7/split.py" "$OUT/drc_job1.json" "$OUT/silk_report.json"; git status --short; exit 0; fi
echo "== job 2: logo and board name on the bottom"
# WR=0.8: with the frozen board's letter widths (WR=1.0) no arrangement clears the via holes; 0.8 gives the stage-7 label proportion (1.0 x 0.75)
WR=0.8 $PY -B "$HERE/logo.py" "$B" "$FROZEN" "$OUT/logo_report.json" "$MOTE" 2>&1 | $Q
if [ "$N" = 2 ]; then gates job2 2; python3 "$S7/split.py" "$OUT/drc_job2.json" "$OUT/silk_report.json"; python3 "$HERE/near.py" "$OUT/drc_job2.json" "$OUT/logo_report.json"; git status --short; exit 0; fi
fi
echo "== job 3: J4 holes 1.3 mm"
$PY -B "$HERE/j4_measure.py" "$B" 2>&1 | $Q > "$OUT/j4_before.txt"
python3 -B "$HERE/j4_holes.py" "$B" "$ROOT/$D/nereus.pretty" "$ROOT/$D/${P}_TopLevel.kicad_sch"
$PY -B "$HERE/j4_measure.py" "$B" 2>&1 | $Q | tee "$OUT/j4_after.txt"
$PY -B "$S7/check.py" "$OUT/board_head_$IN.kicad_pcb" "$B" "$OUT/silk_report.json" 2>&1 | $Q | grep -e DIFFERENT -e Sofar | sed 's/^/   stage-7 check against the head (pads and footprints differ in J4 only, listed by the lock check): /' || true
gates job3 3; python3 "$HERE/near.py" "$OUT/drc_job3.json" "$OUT/logo_report.json" | head -1
python3 -c "import json,sys; [print('DRC item at J4:', v['type'], '|', ' | '.join(i['description'][:70] for i in v['items'])) for v in json.load(open(sys.argv[1]))['violations'] if any(' J4' in i['description'] + ' ' and ('of J4' in i['description'] or i['description'].endswith('J4')) for i in v['items'])]" "$OUT/drc_job3.json"
git status --short
