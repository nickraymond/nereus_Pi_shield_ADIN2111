#!/usr/bin/env bash
# Rebuild the experiment board from the schematic: M0 netlist + board, then each milestone script in order.
# Every step is a plain script; rerunning the pipeline is the only way the board changes (no hand edits, KiCad closed).
set -euo pipefail
cd "$(dirname "$0")/.."
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
SCH=board/nereus_Pi_shield_ADIN2111.kicad_sch
PCB=board/nereus_Pi_shield_ADIN2111.kicad_pcb
LAST="${1:-m9}"            # stop after this milestone (m0 … m5)
filter() { grep -v "Debug: Adding duplicate image handler\|memory leak of type\|create wxApp before calling this" || true; }
mkdir -p out/m0
"$K" sch erc --severity-all -o out/m0/erc.rpt "$SCH" >/dev/null
"$K" sch export netlist -o out/m0/netlist.net "$SCH" >/dev/null
echo "ERC: $(grep -o 'ERC messages: .*' out/m0/erc.rpt)"
"$PY" tools/build_board.py out/m0/netlist.net "$PCB" 2>&1 | filter
[[ "$LAST" < "m1" ]] && exit 0
"$PY" tools/m1_fixed.py 2>&1 | filter
for step in m2_place m3_copy m4_route m5_finish; do
  ms="${step:0:2}"
  [[ "$LAST" < "$ms" ]] && break
  [ -f "tools/$step.py" ] && "$PY" "tools/$step.py" 2>&1 | filter
done
"$PY" tools/check_fixed.py ${HEIGHTS:+--heights "$HEIGHTS"} 2>&1 | filter | grep -v "^ok" || true
