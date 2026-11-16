#!/bin/sh
# Stage 2b, from the pristine inputs every time. Usage: sh scripts/run_all.sh   (KiCad must not have this scratch project open)
set -e
S=$(cd "$(dirname "$0")/.." && pwd); B="$S/board"; P=Nereus_Pi_Shield_Adin2111; PCB="$B/$P.kicad_pcb"
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
run() { n=$1; shift; echo "== $n"; "$PY" "$S/scripts/$n.py" "$@" 2>"$S/build/$n.stderr"; }
mkdir -p "$S/build"
# pristine inputs: stage-1 board, stage-2 schematic, project files, nereus library
cp "$S/board_in_stage1.kicad_pcb" "$PCB"; cp "$S"/sch_in/*.kicad_sch "$B/"; cp "$S"/proj_in/*.kicad_pr? "$S"/proj_in/*.kicad_dru "$S"/proj_in/*-lib-table "$B/"
rm -rf "$B/nereus.pretty"; cp -R "$S/lib_in/nereus.pretty" "$B/nereus.pretty"
"$K" sch export netlist -o "$S/build/netlist_before.net" "$B/$P.kicad_sch" >/dev/null
run step1_diff "$PCB" "$S/build/netlist_before.net" | tee "$S/build/step1_diff_before.txt"
run step2_link_connectors "$PCB" "$S/build/netlist_before.net" "$PCB"; cp "$PCB" "$S/build/after_step2.kicad_pcb"
run step3_add_parts "$PCB" "$S/build/netlist_before.net" "$PCB" | tee "$S/build/step3_placement.txt"; cp "$PCB" "$S/build/after_step3.kicad_pcb"
run step4_j4_footprint "$PCB" "$PCB"; cp "$PCB" "$S/build/after_step4.kicad_pcb"
"$K" sch export netlist -o "$S/netlist_stage2b.net" "$B/$P.kicad_sch" >/dev/null
"$K" sch erc --severity-all --format json -o "$S/erc_stage2b.json" "$B/$P.kicad_sch" | tail -1
run step5_nets "$PCB" "$S/netlist_stage2b.net" "$PCB"; cp "$PCB" "$S/build/after_step5.kicad_pcb"
run step6_fill "$PCB" "$PCB"
echo "== diff after"; "$PY" "$S/scripts/step1_diff.py" "$PCB" "$S/netlist_stage2b.net" 2>/dev/null | tee "$S/build/step1_diff_after.txt" | tail -8
echo "== lock check"; "$PY" "$S/scripts/verify_locks.py" "$S/board_in_stage1.kicad_pcb" "$PCB" 2>/dev/null | tee "$S/build/lock_check.txt"
echo "== DRC"; "$K" pcb drc --severity-all --schematic-parity --format json -o "$S/drc_stage2b.json" "$PCB" | tail -3
"$PY" "$S/scripts/drc_summary.py" "$S/drc_in.json" "$S/drc_stage2b.json" "$S/erc_in.json" "$S/erc_stage2b.json" | tee "$S/build/gates.txt"
echo "== renders"; "$K" pcb render --side top -w 2600 -h 1700 -o "$S/top.png" "$PCB" >/dev/null; "$K" pcb render --side bottom -w 2600 -h 1700 -o "$S/bottom.png" "$PCB" >/dev/null
for f in "$P.kicad_pro" "$P.kicad_dru" fp-lib-table sym-lib-table; do cmp -s "$S/proj_in/$f" "$B/$f" && echo "unchanged: $f" || echo "CHANGED: $f"; done
for f in "$S"/sch_in/*.kicad_sch; do cmp -s "$f" "$B/$(basename "$f")" || echo "schematic file changed: $(basename "$f") ($(diff "$f" "$B/$(basename "$f")" | grep -c '^>') line)"; done
