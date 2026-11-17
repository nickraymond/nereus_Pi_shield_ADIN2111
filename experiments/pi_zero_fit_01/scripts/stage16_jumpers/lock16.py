"""Stage 16 lock check. Usage: <KiCad python> lock16.py <head board e51dfdc> <board> [stage-2c board d30920b]
Every difference against the head board must be on this list: footprints JP2 / JP3 / JP4 exactly 2.0 mm north (same side, angle, footprint, pad
nets; every pad 2.0 mm north, nothing else about it); tracks / vias gone or new only on ADIN_VDDIO, ADIN_LED_VDD, CFG0_STRAP, CFG1_STRAP, GND and
only inside x 9..21, y 31..39; bottom silkscreen: the three footprints' own items 2.0 mm north, board texts 2.0 mm north only those named in MOVED.
Zones, copper graphics, every other footprint, pad, track, via and silkscreen item: identical. With the stage-2c board: says which of the removed
items were already on that board (Sofar's frozen layout or stage 2c) and confirms none of them is a footprint or zone."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage3_routing'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage12_rereview_fixes'))
import s3lib, pcbnew
_src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage12_rereview_fixes', 'lock12.py')).read()   # padtab() and silk() of stage 12, without its main part
F, B = pcbnew.F_SilkS, pcbnew.B_SilkS; exec(_src[_src.index('def padtab'):_src.index("if sys.argv[1] == '--head'")])
JPS = ('JP2', 'JP3', 'JP4'); DYI = -2000000; NETS = {'ADIN_VDDIO', 'ADIN_LED_VDD', 'CFG0_STRAP', 'CFG1_STRAP', 'GND'}; MOVED = {'JP2', 'JP3'}
hb = pcbnew.LoadBoard(sys.argv[1]); h = s3lib.snapshot(hb); ps_h = padtab(hb); sh = silk(hb)
nb = pcbnew.LoadBoard(sys.argv[2]); n = s3lib.snapshot(nb); ps_n = padtab(nb); sn_ = silk(nb)
bad = []; fp = []; gone = []; new = []
inbox = lambda x, y: 9 <= pcbnew.ToMM(x) - s3lib.DX <= 21 and 31 <= pcbnew.ToMM(y) - s3lib.DY <= 39
for k in set(h) | set(n):
    x, y = h.get(k), n.get(k)
    if x == y: continue
    if k[0] == 'F' and x and y and x[0] in JPS and y[0] == x[0] and y[1] == x[1] and y[2] == x[2] + DYI and x[3:6] == y[3:6] and x[7] == y[7]: fp.append(x[0]); continue
    if k[0] == 'T' and not (x and y):
        t = x or y; pts = [(t[1], t[2])] if t[0] == 'via' else [(t[1], t[2]), (t[3], t[4])]
        if s3lib.sn(t[-1]) in NETS and all(inbox(*p) for p in pts): (gone if x else new).append((k, t)); continue
    bad.append((k, x, y))
pd = [k for k in set(ps_h) | set(ps_n) if ps_h.get(k) != ps_n.get(k)]
okp = all(k[0] in JPS and k in ps_h and k in ps_n and ps_n[k][0] == ps_h[k][0] and ps_n[k][1] == ps_h[k][1] + DYI and ps_n[k][2:] == ps_h[k][2:] for k in pd)
def shifted(x):
    if x[0] == 'text': return x[:4] + (x[4] + DYI,) + x[5:]
    return x[:5] + (x[5] + DYI, x[6], x[7] + DYI, x[8])
import collections      # multisets: a footprint outline has items that land on each other's old places, so a plain set difference would mis-pair them
moving = lambda x: x[1] in JPS or (x[1] == '' and x[0] == 'text' and x[2] in MOVED)
ch = collections.Counter(repr(shifted(x)) if moving(x) else repr(x) for x in sh); cn = collections.Counter(repr(x) for x in sn_)
okfp = sum(1 for x in sh if x[1] in JPS); okbt = [x[2] for x in sh if x[1] == '' and x[0] == 'text' and x[2] in MOVED]
bad += [('silk expected, not found', x) for x in (ch - cn).elements()] + [('silk new', x) for x in (cn - ch).elements()]
cnt = lambda s, c: sum(1 for k in s if k[0] == c)
print('  against the head board: %d footprints, %d tracks + vias, %d zones, %d copper graphics, %d pads, %d silkscreen items compared' % (cnt(h, 'F'), cnt(h, 'T'), cnt(h, 'Z'), cnt(h, 'D'), len(ps_h), len(sh)))
print('    footprints moved 2.0 mm north: %s; pads that differ: %d (all 2.0 mm north, nothing else: %s)' % (sorted(fp), len(pd), 'yes' if okp else 'NO'))
M = lambda t: '(%.3f, %.3f)' % (pcbnew.ToMM(t[1]) - s3lib.DX, pcbnew.ToMM(t[2]) - s3lib.DY)
for lab, L in (('gone', gone), ('new', new)):
    vs = sorted('%s %s' % (s3lib.sn(t[-1]), M(t)) for k, t in L if t[0] == 'via'); trk = {}
    for k, t in L:
        if t[0] != 'via': kk = (s3lib.sn(t[-1]), hb.GetLayerName(t[6])); trk[kk] = trk.get(kk, 0) + 1
    print('    vias %s: %s;  track segments %s: %s' % (lab, '; '.join(vs) or 'none', lab, ', '.join('%s %s %d' % (a, b, c) for (a, b), c in sorted(trk.items()))))
print('    silkscreen: %d footprint items of JP2 / JP3 / JP4 moved with them; board texts moved 2.0 mm north: %s; other differences: %d' % (okfp, sorted(okbt), len(bad)))
for x in bad[:20]: print('   !', str(x)[:260])
if len(sys.argv) > 3:
    import re; base = set(re.findall(r'\(uuid "([0-9a-f-]{36})"\)', open(sys.argv[3]).read()))
    old = [(s3lib.sn(t[-1]), t[0], M(t)) for k, t in gone if k[2:] in base]
    print('    removed items that were on the stage-2c board d30920b (frozen layout or stage 2c): %d %s' % (len(old), old))
ok = not bad and okp and sorted(fp) == list(JPS) and len(pd) == 8 and sorted(okbt) == sorted(MOVED)
print('  LOCK', 'PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)
