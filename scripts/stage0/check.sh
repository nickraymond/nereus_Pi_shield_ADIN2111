#!/bin/sh
# Stage 0 check of the schematic as it is now: usage  check.sh <tag>   (tag: baseline | 0a | 0b)
# Adapted from experiments/pi_zero_fit_01/scripts/stage2_schematic/check.sh (development branch).
# kicad-cli writes a .kicad_prl beside the project, so the checks run on a copy outside git (without the board file):
# ERC (JSON and text report), netlist export, then the net diff and ERC diff against the baseline.
set -e
cd "$(dirname "$0")"
TAG=${1:?tag}
OUT=$HOME/NereusData/nereus_Pi_shield_ADIN2111/n6_shield/stage0
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
D=$OUT/$TAG
W=$D/project
mkdir -p "$D"; rm -rf "$W"; mkdir -p "$W"
if [ "$TAG" = baseline ]; then
  git -C ../.. archive HEAD N6_Shield_ADIN2111 | tar -x -C "$W" --strip-components=1
  ( cd ../.. && git ls-tree -r HEAD --name-only N6_Shield_ADIN2111 | grep '\.kicad_sch$' | while read f; do
      printf '%s  %s\n' "$(git show "HEAD:$f" | shasum -a 256 | cut -d' ' -f1)" "$f"; done ) > "$D/sheets_sha256.txt"
else
  rsync -a --exclude '*.kicad_prl' --exclude '*-backups' ../../N6_Shield_ADIN2111/ "$W/"
  ( cd ../.. && shasum -a 256 N6_Shield_ADIN2111/*.kicad_sch ) > "$D/sheets_sha256.txt"
fi
rm -f "$W"/*.kicad_pcb
rm -f "$D/erc_$TAG.json" "$D/erc_$TAG.rpt" "$D/netlist_$TAG.net"
( cd "$W" && $K sch erc --severity-all --format json -o "../erc_$TAG.json" Nereus_Pi_Shield_Adin2111.kicad_sch | tail -1 \
  && $K sch erc --severity-all --format report -o "../erc_$TAG.rpt" Nereus_Pi_Shield_Adin2111.kicad_sch >/dev/null \
  && $K sch export netlist -o "../netlist_$TAG.net" Nereus_Pi_Shield_Adin2111.kicad_sch | tail -1 )
test -s "$D/erc_$TAG.json" && test -s "$D/netlist_$TAG.net"
python3 -B ercdiff.py "$OUT/baseline/erc_baseline.json" "$D/erc_$TAG.json" > "$D/ercdiff_$TAG.txt"
tail -4 "$D/ercdiff_$TAG.txt"
if [ "$TAG" != baseline ]; then
  python3 -B netdiff.py "$OUT/baseline/netlist_baseline.net" "$D/netlist_$TAG.net" > "$D/netdiff_$TAG.txt"
  grep -E '^(baseline|NETS IDENTICAL|   [0-9]+ pins)' "$D/netdiff_$TAG.txt"
fi
