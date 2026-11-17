#!/bin/zsh
# Job C from the committed state of 955d57c: reset the three files, move the block, sync the board, check.
set -e
HERE=${0:A:h}; B=$HERE/../../board; O=~/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/stage17_schematic_docs/c1
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
mkdir -p $O; pgrep -lf kicad.app && { echo 'KiCad is open: close it'; exit 1 }
git -C $B checkout 955d57c -- Nereus_Pi_Shield_Adin2111_TopLevel.kicad_sch Nereus_Pi_Shield_Adin2111.kicad_pcb
rm -f $B/Nereus_Pi_Shield_Adin2111_MotorADC.kicad_sch
python3 $HERE/jobC1_schematic.py $B
$K sch export netlist --format kicadxml -o $O/net.xml $B/Nereus_Pi_Shield_Adin2111.kicad_sch >/dev/null
python3 $HERE/netcompare.py $O/../baseline/net.xml $O/net.xml
python3 $HERE/jobC2_board.py $B/Nereus_Pi_Shield_Adin2111.kicad_pcb $O/net.xml
