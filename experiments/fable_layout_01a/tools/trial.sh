#!/usr/bin/env bash
# Trial run of the pipeline on a scratch copy (M0 placement trials, the OPTIONS addendum): never on the board here.
#   tools/trial.sh <name> <variant> <last milestone m2|m4>      → $SCRATCH/exp/<name>/, log $SCRATCH/<name>.log
# The copy must sit two levels below a directory that holds (a link to) KiCAD_reference_designs/ (geom.MOTE).
set -euo pipefail
cd "$(dirname "$0")/.."
S="${SCRATCH:?set SCRATCH to the scratchpad directory}"
name="$1"; variant="$2"; last="${3:-m2}"
mkdir -p "$S/exp"
[ -e "$S/KiCAD_reference_designs" ] || ln -s "$(cd ../..; pwd)/KiCAD_reference_designs" "$S/KiCAD_reference_designs"
rsync -a --delete --exclude out ./ "$S/exp/$name/"
cd "$S/exp/$name"
export VARIANT="$variant" HEIGHTS=heights.json
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
{ echo "== trial $name variant=$variant last=$last $(date)"; tools/build_all.sh "$last"; echo "== build exit $?";
  "$PY" tools/check_fixed.py --heights heights.json | grep -v "^ok" || true
  "$PY" tools/drc_summary.py "$last" | grep -i "courtyard\|errors:\|unconnected" || true
  "$PY" - <<'PYEOF'
import json, sys
sys.path.insert(0, "tools")
import geom
b = geom.load(); fps = geom.fp_by_ref(b)
d = json.load(open("out/%s/drc.json" % sys.argv[1] if len(sys.argv) > 1 else "out/m2/drc.json")) if False else None
PYEOF
} > "$S/$name.log" 2>&1 || true
grep -v "Debug: Adding\|memory leak\|wxApp" "$S/$name.log" | tail -40
