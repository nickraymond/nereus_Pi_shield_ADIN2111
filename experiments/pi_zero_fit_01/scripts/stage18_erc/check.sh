#!/bin/zsh
# check.sh <tag>: ERC as the project runs it, ERC "live" (scratch copy with the project's stale erc_exclusions emptied),
# netlist vs b70e64f, DRC with parity, project files unchanged.
HERE=${0:A:h}; B=$HERE/../../board; O=~/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/stage18_erc/$1
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli; mkdir -p $O; S=$(mktemp -d)
$K sch erc --severity-all --format json -o $O/erc.json $B/Nereus_Pi_Shield_Adin2111.kicad_sch >/dev/null 2>&1
cp $B/*.kicad_sch $B/*.kicad_sym $B/sym-lib-table $B/fp-lib-table $B/Nereus_Pi_Shield_Adin2111.kicad_pro $S/; for d in $B/*.pretty; do ln -s $d $S/; done
python3 -c "import json,sys; p=sys.argv[1]; d=json.load(open(p)); d['erc']['erc_exclusions']=[]; json.dump(d,open(p,'w'),indent=2)" $S/Nereus_Pi_Shield_Adin2111.kicad_pro
$K sch erc --severity-all --format json -o $O/erc_live.json $S/Nereus_Pi_Shield_Adin2111.kicad_sch >/dev/null 2>&1; rm -rf $S
$K sch export netlist --format kicadxml -o $O/net.xml $B/Nereus_Pi_Shield_Adin2111.kicad_sch >/dev/null 2>&1
$K pcb drc --severity-all --schematic-parity --format json -o $O/drc.json $B/Nereus_Pi_Shield_Adin2111.kicad_pcb >/dev/null 2>&1
echo '== ERC (project)'; python3 $HERE/ercls.py $O/erc.json | sed -n 1,2p
echo '== ERC live'; python3 $HERE/ercls.py $O/erc_live.json
python3 $HERE/../stage17_schematic_docs/netcompare.py $O/../base/net.xml $O/net.xml | sed -n 1,3p
python3 - $O <<'PY'
import json,collections,sys
d=json.load(open(sys.argv[1]+'/drc.json')); c=collections.Counter((v['severity'],v['type']) for v in d['violations'])
print('DRC errors', {k[1]:n for k,n in c.items() if k[0]=='error'}, 'warnings', sum(n for k,n in c.items() if k[0]=='warning'), 'types', len(c), 'unconnected', len(d['unconnected_items']), 'parity', len(d['schematic_parity']))
PY
git -C $B diff --quiet b70e64f -- Nereus_Pi_Shield_Adin2111.kicad_pro Nereus_Pi_Shield_Adin2111.kicad_dru && echo '.kicad_pro / .kicad_dru unchanged'
