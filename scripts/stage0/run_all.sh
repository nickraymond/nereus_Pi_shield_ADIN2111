#!/bin/sh
# Rebuild the stage 0 schematic (steps 0a and 0b) from the committed starting sheets, with the checks after each step.
# Method as experiments/pi_zero_fit_01/scripts/stage2_schematic/run_all.sh (development branch); here the starting
# point is `git show HEAD:<file>` for the eight sheets and nereus.kicad_sym, restored into the working tree.
# Nothing is committed. Outputs: ~/NereusData/nereus_Pi_shield_ADIN2111/n6_shield/stage0/ (never into git).
set -e
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1
OUT=$HOME/NereusData/nereus_Pi_shield_ADIN2111/n6_shield/stage0
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
if pgrep -lf KiCad | grep -v kicad-cli | grep -q .; then echo "KiCad is running: close it first"; exit 1; fi
P=N6_Shield_ADIN2111
for f in $(git -C ../.. ls-tree -r HEAD --name-only $P | grep -E '\.kicad_sch$|/nereus\.kicad_sym$'); do
  git -C ../.. show "HEAD:$f" > "../../$f"
done
echo "baseline"; sh check.sh baseline
echo "step 0a"; python3 -B step0a_remove.py; sh check.sh 0a
echo "step 0b"; python3 -B step0b_add_remap.py; sh canon.sh; sh check.sh 0b
python3 -B pintable.py "$OUT/0b/netlist_0b.net" > "$OUT/0b/tables_0b.md"; tail -3 "$OUT/0b/tables_0b.md"
( cd "$OUT/0b/project" && $K sch export pdf -o "$OUT/N6_shield_stage0_schematic.pdf" Nereus_Pi_Shield_Adin2111.kicad_sch | tail -1 )
# nothing but the schematic sheets and the project symbol library may differ from HEAD
git -C ../.. status --short -- $P
