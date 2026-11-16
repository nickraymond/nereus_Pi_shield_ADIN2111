#!/bin/sh
# ERC, netlist and net diff of the scratch project against the baseline.
cd "$(dirname "$0")"
S=..
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
( cd $S/board && $K sch erc --severity-all --format json -o ../erc_stage2.json Nereus_Pi_Shield_Adin2111.kicad_sch | tail -1 \
  && $K sch export netlist -o ../netlist_stage2.net Nereus_Pi_Shield_Adin2111.kicad_sch | tail -1 ) || exit 1
python3 -B netdiff.py > $S/netdiff_stage2.txt && tail -4 $S/netdiff_stage2.txt
python3 -B ercdiff.py > $S/ercdiff_stage2.txt && tail -3 $S/ercdiff_stage2.txt
