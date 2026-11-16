"""Which LED shows which Bristlemouth port, from the schematic's netlist (not from the frozen board's order), and the label table.
Usage: python3 netcheck.py <netlist.xml (kicad-cli sch export netlist --format kicadxml)> <silk report.json>
Trace: LED cathode net -> the U1 pin on it (pin name says the port) ; U1's port-n line pins -> through 2-pin parts, transformers and chokes -> a connector."""
import sys, json, re, collections
import xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot(); rep = json.load(open(sys.argv[2]))
nets = {}; pins = collections.defaultdict(dict)       # net -> [(ref, pin, pinfunction)], ref -> pin -> net
for n in root.find('nets'):
    nm = n.get('name').split('/')[-1]
    for nd in n.findall('node'): nets.setdefault(nm, []).append((nd.get('ref'), nd.get('pin'), nd.get('pinfunction') or '')); pins[nd.get('ref')][nd.get('pin')] = nm
POWER = re.compile(r'GND|3V3|1V8|VBUS.*|.*VDD.*|.*PWR.*|5V.*|PI_.*|.*AVDD.*')
def reach(start):
    """nets reachable from a net through passives (R, C, L, T, D, FB), never through a power net or an IC"""
    seen, todo = {start}, [start]
    while todo:
        for ref, pin, fn in nets.get(todo.pop(), []):
            if not re.match(r'(R|C|L|T|FB)\d', ref): continue
            for p2, n2 in pins[ref].items():
                if n2 not in seen and not POWER.fullmatch(n2): seen.add(n2); todo.append(n2)
    return seen
u1 = {pin: (net, [fn for r, p, fn in nets[net] if r == 'U1' and p == pin][0]) for pin, net in pins['U1'].items()}
for led, label in (('D10', 'BM2'), ('D9', 'BM1')):
    lednets = set(pins[led].values()); via = [(p, fn, net) for p, (net, fn) in u1.items() if net in reach(list(lednets)[0]) | reach(list(lednets)[1]) and 'LED' in fn.upper()]
    port = {re.search(r'P?([12])_?LED|LED_?([12])', fn.upper()).group(0) for p, fn, net in via}
    pn = sorted({re.search(r'P([12])', fn.upper()).group(1) for p, fn, net in via})
    assert len(pn) == 1, (led, via)
    line = [(p, fn, net) for p, (net, fn) in u1.items() if re.match(r'P%s_(TX|RX)[NP]' % pn[0], fn.upper())]
    conns = set()
    for p, fn, net in line: conns |= {r for n2 in reach(net) for r, _, _ in nets[n2] if re.match(r'J\d', r)}
    cn = {r: sorted({n2 for n2 in pins[r].values()}) for r in conns}
    print('%s: nets %s -> U1 pin(s) %s = port %s; U1 port-%s line pins %s -> connector(s) %s; label "%s" %s' % (led, sorted(lednets), [(p, fn) for p, fn, net in via], pn[0], pn[0], [(p, fn) for p, fn, n in line], cn, label,
          'OK' if cn and all(any(label in x for x in v) for v in cn.values()) else 'MISMATCH'))
print('%-52s %-9s %-14s %-34s %s' % ('label for', 'text', 'pad', 'net(s) on the board', 'check'))
for w, s, p, n, ok in rep['net_check']: print('%-52s %-9s %-14s %-34s %s' % (w, s, p, n, ok))
