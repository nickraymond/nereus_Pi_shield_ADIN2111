#!/bin/zsh
# Jobs A + B: cover from the committed 955d57c cover, then render page 1 for a look.
set -e
HERE=${0:A:h}; B=$HERE/../../board; O=~/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/stage17_schematic_docs/jobA
git -C $B checkout 955d57c -- Nereus_Pi_Shield_Adin2111.kicad_sch
python3 $HERE/jobAB_cover.py $B $O/board_views.png
rm -rf $O/svg; mkdir -p $O/svg
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli sch export svg -o $O/svg $B/Nereus_Pi_Shield_Adin2111.kicad_sch >/dev/null 2>&1
$HERE/svg2png.sh $O/svg/Nereus_Pi_Shield_Adin2111.svg $O/cover.png 3360 2376 >/dev/null
