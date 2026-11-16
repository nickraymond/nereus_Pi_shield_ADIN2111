"""Plane piece counts, head -> now, from two outputs of stage 5's planes.py. Fails if any zone has more pieces. Usage: python3 planes_cmp.py <head.txt> <now.txt>"""
import sys, re
def tab(p):
    d = {}
    for l in open(p):
        m = re.match(r'(.{11}) (\S+)\s+(.*?)\s+box (\(.*?\)-\(.*?\))\s+pieces (\d+)\s+area ([\d.]+)', l)
        if m: d[(m.group(1).strip(), m.group(2), m.group(3), m.group(4))] = (int(m.group(5)), float(m.group(6)))
    return d
a, b = tab(sys.argv[1]), tab(sys.argv[2]); worse = 0; assert set(a) == set(b) and a, (len(a), len(b))
for k in sorted(a):
    if a[k] != b[k]: print('   %-11s %-8s %-40s pieces %d -> %d, area %.2f -> %.2f mm2%s' % (k[0], k[1], k[2][:40], a[k][0], b[k][0], a[k][1], b[k][1], '   WORSE' if b[k][0] > a[k][0] else '')); worse += b[k][0] > a[k][0]
print('   planes: %d zone fills compared, more pieces than the head: %d' % (len(a), worse)); sys.exit(1 if worse else 0)
