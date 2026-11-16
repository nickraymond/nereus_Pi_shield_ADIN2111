#!/bin/sh
# Rebuild one phase from the previous phase's committed board, then check it.  Usage: sh run.sh <A|B|C|D|F|G|H|I|E>
# Order: A B C D, then F (BM1 trunk fix, J5 moved), G (power rest), H (signals rest), I (ground), E (clean-up).
# Input board: phase A = the stage 2c board (commit d30920b); later phases = the commit whose subject starts
# "pi_zero_fit_01 stage 3 phase <previous>". Output: board/ in the worktree. DRC JSON and logs go to NereusData.
set -e
P="$1"; HERE=$(cd "$(dirname "$0")" && pwd); ROOT=$(cd "$HERE/../../../.." && pwd)
BRD=experiments/pi_zero_fit_01/board/Nereus_Pi_Shield_Adin2111.kicad_pcb
OUT=~/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/stage3_routing; mkdir -p "$OUT"
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
cd "$ROOT"
BASE=d30920b
case "$P" in A) PREV=$BASE;; B) Q=A;; C) Q=B;; D) Q=C;; F) Q=D;; G) Q=F;; H) Q=G;; I) Q=H;; E) Q=I;; esac
[ -n "$Q" ] && PREV=$(git log --grep="^pi_zero_fit_01 stage 3 phase $Q" -1 --format=%H)
[ -n "$PREV" ] || { echo "no commit for the previous phase"; exit 1; }
git show $BASE:$BRD > "$OUT/board_stage2c.kicad_pcb"
git show $PREV:$BRD > "$OUT/in_$P.kicad_pcb"
echo "phase $P from $PREV"
cp "$OUT/in_$P.kicad_pcb" "$ROOT/$BRD"     # load from inside the project folder, so pcbnew reads the project's own rules
S3_BASE="$OUT/board_stage2c.kicad_pcb" $PY "$HERE/phase$P.py" "$ROOT/$BRD" "$ROOT/$BRD" "$OUT/log_$P.json" 2>&1 | grep -v -e 'assert ""traits""' -e 'Debug: Adding' || true
$CLI pcb drc --severity-all --schematic-parity --format json -o "$OUT/drc_$P.json" "$ROOT/$BRD" | grep -v Saved
python3 "$HERE/drc_summary.py" "$OUT/drc_$P.json" -v
python3 "$HERE/drc_summary.py" "$OUT/drc_$P.json" -u | grep "^U" > "$OUT/unconnected_$P.txt" || true
$PY -c "import sys; sys.path.insert(0, '$HERE'); import s3lib; sys.exit(0 if s3lib.verify_lock('$OUT/board_stage2c.kicad_pcb', '$ROOT/$BRD') else 1)" 2>&1 | grep -v -e 'assert ""traits""' -e 'Debug: Adding'
for f in kicad_pro kicad_dru kicad_sch; do git diff --quiet $BASE -- experiments/pi_zero_fit_01/board/Nereus_Pi_Shield_Adin2111.$f || echo "!! .$f CHANGED"; done
echo "project rules (.kicad_pro, .kicad_dru) and schematic: compared with $BASE"
git status --short | grep -v stage3_routing | grep -v LOG.md | grep -v STAGE3 || true
