#!/usr/bin/env bash
# One-command check of the JLC board's project (Nereus_Pi_Shield_Adin2111/): ERC, DRC with schematic parity,
# the board against the layout freeze, netlist, schematic PDF, BOM. Reads the project; never modifies it.
# Raw outputs → docs/design-review/out/ (git-ignored); docs/design-review/bom.csv is tracked.
# Exit code 0 = every figure is the recorded one; 1 = a figure moved (the line says which); 2 = a tool or file is missing.
# The recorded figures are the frozen board's (TRACKER S9 / S10): change them only with a change Nick approved.
set -euo pipefail
cd "$(dirname "$0")/.."

K="${KICAD_CLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}"
PROJ=Nereus_Pi_Shield_Adin2111
SCH="$PROJ/$PROJ.kicad_sch"
PCB="$PROJ/$PROJ.kicad_pcb"
OUT=docs/design-review/out
BOM=docs/design-review/bom.csv
# ERC items · DRC errors not excluded (skew on Sofar's data pairs, Q13) · excluded · unconnected · parity · parts · nets
EXPECT="39 3 16 0 0 143 110"

[ -x "$K" ] || { echo "check: kicad-cli not found at $K (set KICAD_CLI)" >&2; exit 2; }
[ -f "$SCH" ] || { echo "check: schematic not found: $SCH" >&2; exit 2; }
[ -f "$PCB" ] || { echo "check: board not found: $PCB" >&2; exit 2; }
if ls "$PROJ"/~*.lck >/dev/null 2>&1; then
  echo "check: WARNING — KiCad lock file present; results reflect the last *saved* files." >&2
fi
mkdir -p "$OUT"

"$K" sch erc --severity-all --format json -o "$OUT/erc.json" "$SCH" >/dev/null
"$K" sch erc --severity-all -o "$OUT/erc.rpt" "$SCH" >/dev/null
"$K" pcb drc --refill-zones --schematic-parity --severity-all --format json -o "$OUT/drc.json" "$PCB" >/dev/null
"$K" sch export netlist -o "$OUT/netlist.net" "$SCH" >/dev/null
"$K" sch export pdf -o "$OUT/schematic.pdf" "$SCH" >/dev/null
# Tracked BOM of this board: Sofar's specified part, the planned part + why, sourcing, backups (bom_review_2026-11.md).
"$K" sch export bom -o "$BOM" \
  --fields 'Reference,${QUANTITY},Value,MANUFACTURER,PLANNED MPN,PLANNED MFR,PLANNED LCSC,PLANNED NOTE,${DNP},SOURCING,ALT1 MPN,ALT1 MFR,ALT1 LCSC,ALT2 MPN,ALT2 MFR,ALT2 LCSC,ALT NOTE,Footprint' \
  --labels 'Refs,Qty,Value (MPN),Mfr,Planned MPN,Planned Mfr,Planned LCSC,Planned note,DNP,Sourcing,Alt1 MPN,Alt1 Mfr,Alt1 LCSC,Alt2 MPN,Alt2 Mfr,Alt2 LCSC,Alt note,Footprint' \
  --group-by 'Value,${DNP}' "$SCH" >/dev/null

for f in erc.json erc.rpt drc.json netlist.net schematic.pdf; do
  [ -s "$OUT/$f" ] || { echo "check: $OUT/$f missing or empty" >&2; exit 2; }
done
[ -s "$BOM" ] || { echo "check: $BOM missing or empty" >&2; exit 2; }

set +e
python3 - "$OUT" "$EXPECT" <<'PY'
import json, re, sys
out, expect = sys.argv[1], [int(x) for x in sys.argv[2].split()]
erc = json.load(open(f"{out}/erc.json"))
drc = json.load(open(f"{out}/drc.json"))
v = drc["violations"]
net = open(f"{out}/netlist.net", encoding="utf-8").read()
got = [sum(len(s["violations"]) for s in erc["sheets"]),
       sum(1 for x in v if x["severity"] == "error" and not x.get("excluded")),
       sum(1 for x in v if x.get("excluded")),
       len(drc.get("unconnected_items", [])), len(drc.get("schematic_parity", [])),
       len(re.findall(r"\(comp\s*\(ref ", net)), len(re.findall(r"\(net\s*\(code ", net))]
names = ["ERC items", "DRC errors not excluded", "DRC excluded", "unconnected", "parity issues", "parts", "nets"]
print("ERC:      %d items" % got[0])
print("DRC:      %d errors not excluded, %d excluded, %d unconnected, %d parity issues" % tuple(got[1:5]))
print("Netlist:  %d parts, %d nets" % tuple(got[5:]))
moved = [f"{n}: {g}, recorded {e}" for n, g, e in zip(names, got, expect) if g != e]
if moved:
    print("check: FIGURES MOVED — " + "; ".join(moved) + f" (reports in {out}/)")
sys.exit(1 if moved else 0)
PY
status=$?
frz_out=$(python3 "$PROJ/scripts/verify_against_freeze.py" 2>&1); frz=$?
set -e
echo "Freeze:   ${frz_out##*$'\n'}"
echo "PDF:      $OUT/schematic.pdf ($(( $(wc -c < "$OUT/schematic.pdf") / 1024 )) KB)"
echo "BOM:      $BOM ($(( $(wc -l < "$BOM") - 1 )) rows)"
[ $frz -ne 0 ] && { echo "$frz_out"; status=1; }
exit $status
