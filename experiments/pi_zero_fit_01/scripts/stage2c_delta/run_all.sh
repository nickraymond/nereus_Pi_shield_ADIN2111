#!/bin/sh
# Stage 2c, from the pristine stage-2b project every time. Usage: sh scripts_2c/run_all.sh   (KiCad must not have this scratch project open)
set -e
S=$(cd "$(dirname "$0")/.." && pwd); B="$S/board"; IN="$S/board_in_stage2b"; O="$S/build_2c"; P=Nereus_Pi_Shield_Adin2111; PCB="$B/$P.kicad_pcb"
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
export PYTHONDONTWRITEBYTECODE=1
run() { n=$1; shift; echo "== $n"; "$PY" "$S/scripts_2c/$n.py" "$@" 2>"$O/$n.stderr"; }
mkdir -p "$O"
# pristine inputs: the whole stage-2b project
rm -rf "$B"; cp -Rp "$IN" "$B"
(cd "$B" && "$K" sch export netlist -o "$O/netlist_in.net" $P.kicad_sch >/dev/null && "$K" sch erc --severity-all --format json -o "$O/erc_in.json" $P.kicad_sch | tail -1)
"$K" pcb drc --severity-all --schematic-parity --format json -o "$O/drc_in.json" "$IN/$P.kicad_pcb" | tail -3
echo "== step1_schematic"; (cd "$S/scripts_2c" && python3 -B step1_schematic.py)
(cd "$B" && "$K" sch export netlist -o "$S/netlist_stage2c.net" $P.kicad_sch >/dev/null && "$K" sch erc --severity-all --format json -o "$S/erc_stage2c.json" $P.kicad_sch | tail -1)
python3 -B "$S/scripts_2c/netdiff.py" "$O/netlist_in.net" "$S/netlist_stage2c.net" > "$S/netdiff_stage2c.txt"; grep -c . "$S/netdiff_stage2c.txt" >/dev/null
python3 -B "$S/scripts_2c/netdiff.py" "$S/../stage2_scratch/netlist_stage2.net" "$S/netlist_stage2c.net" > "$O/netdiff_vs_stage2_scratch.txt"
sed -n '1,4p;/^NETS REMOVED/,$p' "$S/netdiff_stage2c.txt"
python3 -B "$S/scripts_2c/ercdiff.py" "$O/erc_in.json" "$S/erc_stage2c.json" | tee "$S/ercdiff_stage2c.txt"
run step2_remove "$PCB" "$S/netlist_stage2c.net" "$PCB"; cp "$PCB" "$O/after_step2.kicad_pcb"
run step3_place "$PCB" "$S/netlist_stage2c.net" "$PCB" | tee "$O/step3_placement.txt"
run step4_j4_silk "$PCB" "$PCB"
run step5_parity "$PCB" "$S/netlist_stage2c.net" "$PCB"
run step6_fill "$PCB" "$PCB"
echo "== lock check"; "$PY" "$S/scripts_2c/verify_locks.py" "$IN/$P.kicad_pcb" "$PCB" 2>/dev/null | tee "$O/lock_check.txt"
echo "== DRC"; "$K" pcb drc --severity-all --schematic-parity --format json -o "$S/drc_stage2c.json" "$PCB" | tail -3
python3 -B "$S/scripts_2c/drc_summary.py" "$O/drc_in.json" "$S/drc_stage2c.json" "$O/erc_in.json" "$S/erc_stage2c.json" | tee "$O/gates.txt"
echo "== renders"; "$K" pcb render --side top -w 2600 -h 1700 -o "$S/top.png" "$PCB" >/dev/null; "$K" pcb render --side bottom -w 2600 -h 1700 -o "$S/bottom.png" "$PCB" >/dev/null
sh "$S/scripts_2c/render_sch.sh"
for f in "$P.kicad_pro" "$P.kicad_dru" fp-lib-table sym-lib-table; do cmp -s "$IN/$f" "$B/$f" && echo "unchanged: $f" || echo "CHANGED: $f"; done
for f in "$IN"/*.kicad_sch; do cmp -s "$f" "$B/$(basename "$f")" || echo "schematic file changed: $(basename "$f")"; done
(cd "$B" && find . -type f ! -name '*.kicad_sch' ! -name '*.kicad_pcb' | while read f; do cmp -s "$f" "$IN/$f" || echo "other file changed: $f"; done)
