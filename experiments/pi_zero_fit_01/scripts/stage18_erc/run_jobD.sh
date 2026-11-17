#!/bin/zsh
# Job D from b70e64f: reset the sheets and the library, apply jobD_erc.py, then check (live ERC = with the project's
# stale exclusions stripped in a scratch copy only; the project file itself is never changed).
set -e
HERE=${0:A:h}; B=$HERE/../../board; O=~/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/stage18_erc/$1
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli; mkdir -p $O
pgrep -lf kicad.app && { echo 'KiCad is open'; exit 1 }
git -C $B checkout b70e64f -- . 
python3 $HERE/jobD_erc.py $B
python3 $HERE/board_sync.py $B/Nereus_Pi_Shield_Adin2111.kicad_pcb
$HERE/check.sh $1
