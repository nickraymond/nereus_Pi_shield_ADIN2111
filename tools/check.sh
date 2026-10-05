#!/usr/bin/env bash
# One-command check of the live schematic: ERC, netlist, PDF, net check vs the
# mote copper. Reads the project; never modifies it.
# Raw outputs → docs/design-review/out/ (git-ignored); docs/design-review/netcheck.md is tracked.
# Exit code is netcheck's: 0 = connectivity matches the copper, 1 = differences.
set -euo pipefail
cd "$(dirname "$0")/.."

K="${KICAD_CLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}"
PROJ=nereus_Pi_shield_ADIN2111
SCH="$PROJ/$PROJ.kicad_sch"
OUT=docs/design-review/out

[ -x "$K" ] || { echo "check: kicad-cli not found at $K (set KICAD_CLI)" >&2; exit 2; }
[ -f "$SCH" ] || { echo "check: schematic not found: $SCH" >&2; exit 2; }
if ls "$PROJ"/~*.lck >/dev/null 2>&1; then
  echo "check: WARNING — KiCad lock file present; results reflect the last *saved* files." >&2
fi
mkdir -p "$OUT"

"$K" sch erc --severity-all -o "$OUT/erc.rpt" "$SCH" >/dev/null
"$K" sch export netlist -o "$OUT/netlist.net" "$SCH" >/dev/null
"$K" sch export pdf -o "$OUT/schematic.pdf" "$SCH" >/dev/null

for f in erc.rpt netlist.net schematic.pdf; do
  [ -s "$OUT/$f" ] || { echo "check: $OUT/$f missing or empty" >&2; exit 2; }
done

echo "ERC:      $(grep -o 'ERC messages: .*' "$OUT/erc.rpt")"
echo "PDF:      $OUT/schematic.pdf ($(( $(wc -c < "$OUT/schematic.pdf") / 1024 )) KB)"
set +e
python3 tools/netcheck.py --netlist "$OUT/netlist.net"
status=$?
set -e
exit $status
