#!/bin/sh
# Put the two sheets that got new items into KiCad's own item order, so that KiCad's next save changes nothing.
# Written new. A copy of the project (outside git) is re-saved by kicad-cli (`sch upgrade --force`, one sheet at a
# time); a re-saved sheet is copied back only if it holds exactly the same lines as the scripted one (same multiset
# of lines: a pure reordering). The checks (check.sh 0b) run after this, on the result.
set -e
cd "$(dirname "$0")"
OUT=$HOME/NereusData/nereus_Pi_shield_ADIN2111/n6_shield/stage0
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
W=$OUT/canon
rm -rf "$W"; mkdir -p "$W"
rsync -a --exclude '*.kicad_prl' --exclude '*.kicad_pcb' ../../N6_Shield_ADIN2111/ "$W/"
for f in Nereus_Pi_Shield_Adin2111_TopLevel.kicad_sch Nereus_Pi_Shield_Adin2111_MotorADC.kicad_sch; do
  ( cd "$W" && $K sch upgrade --force "$f" >/dev/null )
  python3 -B - "$W/$f" "../../N6_Shield_ADIN2111/$f" <<'PY'
import collections, shutil, sys
new, old = sys.argv[1], sys.argv[2]
a, b = (collections.Counter(open(p, encoding="utf-8").read().splitlines()) for p in (new, old))
if a != b:
    sys.exit("canon: KiCad's re-save of %s is not a pure reordering (%d / %d lines differ); nothing copied"
             % (old, sum((a - b).values()), sum((b - a).values())))
same = open(new, encoding="utf-8").read() == open(old, encoding="utf-8").read()
shutil.copyfile(new, old)
print("  canon: %s %s" % (old.split("/")[-1], "already in KiCad's order" if same else "items put in KiCad's order (same lines)"))
PY
done
