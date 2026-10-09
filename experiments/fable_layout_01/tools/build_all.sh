#!/usr/bin/env bash
# Rebuild the experiment board from the schematic: M0 netlist + board, then each milestone script in order.
# Every step is a plain script; rerunning the pipeline is the only way the board changes (no hand edits, KiCad closed).
#   tools/build_all.sh [m0…m4]        stop after this milestone
#   START=m4 tools/build_all.sh       rerun the routing alone from the M3 snapshot (out/m3/snapshot.kicad_pcb)
#   NOCLEAN=1                         skip the dangling-copper cleanup after M4 (for diagnosis)
set -euo pipefail
cd "$(dirname "$0")/.."
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
SCH=board/nereus_Pi_shield_ADIN2111.kicad_sch
PCB=board/nereus_Pi_shield_ADIN2111.kicad_pcb
LAST="${1:-m9}"
START="${START:-m0}"
filter() { grep -v "Debug: Adding duplicate image handler\|memory leak of type\|create wxApp before calling this" || true; }
if [[ "$START" < "m2" ]]; then
  mkdir -p out/m0
  "$K" sch erc --severity-all -o out/m0/erc.rpt "$SCH" >/dev/null
  "$K" sch export netlist -o out/m0/netlist.net "$SCH" >/dev/null
  echo "ERC: $(grep -o 'ERC messages: .*' out/m0/erc.rpt)"
  "$PY" tools/build_board.py out/m0/netlist.net "$PCB" 2>&1 | filter
  [[ "$LAST" < "m1" ]] && exit 0
  "$PY" tools/m1_fixed.py 2>&1 | filter
fi
for step in m2_place m3_copy m4_route; do
  ms="${step:0:2}"
  [[ "$LAST" < "$ms" ]] && break
  [[ "$ms" < "$START" ]] && continue
  if [ "$step" = m4_route ]; then
    cp out/m3/snapshot.kicad_pcb "$PCB"; cp out/m3/blocks.snapshot.json blocks.json
  fi
  "$PY" "tools/$step.py" 2>&1 | filter
  if [ "$step" = m3_copy ]; then mkdir -p out/m3; cp "$PCB" out/m3/snapshot.kicad_pcb; cp blocks.json out/m3/blocks.snapshot.json; fi
  if [ "$step" = m4_route ] && [ -z "${NOCLEAN:-}" ]; then "$PY" tools/dangling.py m4 2>&1 | filter; fi
done
"$PY" tools/check_fixed.py ${HEIGHTS:+--heights "$HEIGHTS"} 2>&1 | filter | grep -v "^ok" || true
