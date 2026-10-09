#!/usr/bin/env bash
# Rebuild the experiment board from the schematic: M0 netlist + board, then each milestone script in order.
# VARIANT=centre|pocket picks the placement (tools/m2_place.py, session 2.b); default centre.
# Every step is a plain script; rerunning the pipeline is the only way the board changes (no hand edits, KiCad closed).
#   tools/build_all.sh [m0…m4]        stop after this milestone
#   START=m4 tools/build_all.sh       rerun the routing alone from the M3 snapshot (out/m3/snapshot.kicad_pcb)
#   START=m2 tools/build_all.sh       rerun placement + copper copy from the M1 snapshot (out/m1/snapshot.kicad_pcb)
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
  mkdir -p out/m1; cp "$PCB" out/m1/snapshot.kicad_pcb; cp blocks.json out/m1/blocks.snapshot.json
fi
for step in m2_place m3_copy m4_route; do
  ms="${step:0:2}"
  [[ "$LAST" < "$ms" ]] && break
  [[ "$ms" < "$START" ]] && continue
  # a restart always begins from the snapshot of the milestone before it: the board on disk may hold later copper
  if [ "$step" = m2_place ] && [ "$START" = m2 ]; then
    cp out/m1/snapshot.kicad_pcb "$PCB"; cp out/m1/blocks.snapshot.json blocks.json
  fi
  if [ "$step" = m3_copy ] && [ "$START" = m3 ]; then
    echo "START=m3 is not supported (M2 leaves no snapshot); use START=m2" >&2; exit 2
  fi
  if [ "$step" = m4_route ]; then
    cp out/m3/snapshot.kicad_pcb "$PCB"; cp out/m3/blocks.snapshot.json blocks.json
  fi
  "$PY" "tools/$step.py" 2>&1 | filter
  if [ "$step" = m2_place ]; then
    # silk to JLCPCB's legend limits (DFM.md rows 17-19): line widths, reference text size and spots, lines over pads
    "$PY" tools/dfm_fix.py 2>&1 | filter
    mkdir -p out/m2; "$K" pcb drc --schematic-parity --severity-all --format json -o out/m2/drc.json "$PCB" >/dev/null
  fi
  if [ "$step" = m3_copy ]; then
    # trim Sofar's clipped lead-outs (dead ends toward the mote's processor) before routing: they would block the
    # ADIN pocket's exits; every trimmed item is recorded in blocks.json (blockcheck lists them as trimmed)
    "$PY" tools/m3b_planes.py 2>&1 | filter
    [ -z "${NOCLEAN:-}" ] && "$PY" tools/dangling.py m3 --all 2>&1 | filter
    mkdir -p out/m3; cp "$PCB" out/m3/snapshot.kicad_pcb; cp blocks.json out/m3/blocks.snapshot.json
  fi
  if [ "$step" = m4_route ] && [ -z "${NOCLEAN:-}" ]; then "$PY" tools/dangling.py m4 2>&1 | filter; fi
done
"$PY" tools/check_fixed.py ${HEIGHTS:+--heights "$HEIGHTS"} 2>&1 | filter | grep -v "^ok" || true
