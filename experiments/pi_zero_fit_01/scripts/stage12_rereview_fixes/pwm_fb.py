"""MOTOR_IN1 / MOTOR_IN2 against the converter's feedback net 5V_FB and its switch node. New-frame mm. Usage: <KiCad python> pwm_fb.py <board>
Copper edge to copper edge in plan view: to the 5V_FB via (its 0.6 mm pad, every layer), to 5V_FB tracks and pads per layer, to the nearest
5V_Buck_SW pad / track / via."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage3_routing'))
import s3lib, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); g = s3lib.Geo(b); out = []
for net in ('MOTOR_IN1', 'MOTOR_IN2'):
    mine = [(L, e) for L in g.L for e in g.L[L] if e[1] == net and e[0] == 'cap' and e[4].startswith('track')]
    for other in ('5V_FB', '5V_Buck_SW'):
        best = {}
        for L2 in g.L:
            for kind, n2, bb, data, desc in g.L[L2]:
                if n2 != other: continue
                isvia = desc.startswith('via')
                if kind == 'poly': continue
                for L, (k1, n1, bb1, d1, desc1) in mine:
                    if kind == 'cap': d = s3lib.seg_seg(d1[0], d1[1], data[0], data[1]) - data[2] - d1[2]
                    else: x0, y0, x1, y1 = data; d = s3lib.seg_poly(d1[0], d1[1], [[(x0, y0), (x1, y0), (x1, y1), (x0, y1)]]) - d1[2]
                    key = 'via' if isvia else L2
                    if d < best.get(key, (9,))[0]: best[key] = (d, desc, L)
        out.append('%s (%s) to %-10s: %s' % (net, '/'.join(sorted({L for L, _ in mine})), other, ';  '.join('%s %.3f mm [%s]' % (k, max(v[0], 0) if v[0] > -1e-9 else v[0], v[1][:44]) for k, v in sorted(best.items(), key=lambda kv: kv[1][0]))))
print('\n'.join(out))
