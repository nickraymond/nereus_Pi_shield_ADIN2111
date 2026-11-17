#!/bin/zsh
# check.sh <tag>: ERC, DRC with schematic parity, netlist compare against the baseline, project files unchanged.
HERE=${0:A:h}; B=$HERE/../../board; O=~/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/stage17_schematic_docs/$1
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli; mkdir -p $O
$K sch erc --severity-all --format json -o $O/erc.json $B/Nereus_Pi_Shield_Adin2111.kicad_sch >/dev/null 2>&1
$K pcb drc --severity-all --schematic-parity --format json -o $O/drc.json $B/Nereus_Pi_Shield_Adin2111.kicad_pcb >/dev/null 2>&1
$K sch export netlist --format kicadxml -o $O/net.xml $B/Nereus_Pi_Shield_Adin2111.kicad_sch >/dev/null 2>&1
python3 - $O <<'PY'
import json,collections,sys
O=sys.argv[1]; d=json.load(open(O+'/drc.json'))
c=collections.Counter((v['severity'],v['type']) for v in d['violations'])
print('DRC errors', {k[1]:n for k,n in c.items() if k[0]=='error'}, 'warnings', sum(n for k,n in c.items() if k[0]=='warning'),
      'unconnected', len(d['unconnected_items']), 'parity', len(d['schematic_parity']))
e=json.load(open(O+'/erc.json')); print('ERC', sum(len(s['violations']) for s in e['sheets']))
PY
python3 $HERE/netcompare.py $O/../baseline/net.xml $O/net.xml | head -2
git -C $B diff --quiet 955d57c -- Nereus_Pi_Shield_Adin2111.kicad_pro Nereus_Pi_Shield_Adin2111.kicad_dru && echo '.kicad_pro / .kicad_dru unchanged from 955d57c'
