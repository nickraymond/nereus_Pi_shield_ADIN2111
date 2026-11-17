"""Stage 18, job D: close the ERC errors and the removable warnings, text level, connectivity unchanged.

1  FID1..FID6: a no-connect flag on the hidden pin "0" (tip at symbol + (7.62, 0)).
2  Pin types (TI datasheets read 2026-11-16): LMR51430 SLUSEF4A Pin Functions: SW pin 2 "Switching output of the converter
   ... Connect this pin to the power inductor" -> power_out; CB pin 6 "Bootstrap capacitor connection" -> passive.
   TPS62840 SLVSEC6 Pin Functions: SW (YBG B2) "connected to the internal MOSFET switches. Connect the inductor" -> power_out.
   Changed in the Power sheet's embedded symbols and in BM_Mote_000639-AB-altium-import.kicad_sym alike; the board pads'
   pintype follows.
3  Dangling wire ends (Altium-import leftovers): each end is trimmed back to the nearest connection point on the wire;
   a wire that shrinks to nothing is removed.
4  ADIN sheet: local label ADIN_VDDIO kept (it is the link; see step 4 below).
5  multiple_net_names: Sofar's inner labels. A label used once only names a wire that the hierarchical label names already:
   removed. A label used twice links two places: the copy on the hierarchical label's wire is removed, the far copy becomes a
   hierarchical label of the outer name. Each removed / renamed label leaves a text note "Sofar: <name>" at its place.
Usage: python3 jobD_erc.py <board dir>
"""
import re, sys, uuid, os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import geom
from geom import sx

D = Path(sys.argv[1]); P = lambda s: D / ('Nereus_Pi_Shield_Adin2111%s.kicad_sch' % s)
U = lambda tag: str(uuid.uuid5(uuid.NAMESPACE_URL, 'nereus/pi_zero_fit_01/stage18/' + tag))
files = {}
def get(s):
    if s not in files: files[s] = P(s).read_text(encoding='utf-8')
    return files[s]
def block(text, pred):
    hits = [(s, e, b) for s, e, k, b in sx.items(text) if pred(k, b)]; assert len(hits) == 1, len(hits); return hits[0]
def replace_block(s_, pred, new):
    t = get(s_); s, e, b = block(t, pred); files[s_] = t[:s] + new(b) + t[e:]
def insert(s_, blk):
    t = get(s_); k = t.rindex('\n\t(sheet_instances') + 1 if '\n\t(sheet_instances' in t else t.rindex('\n)') + 1
    files[s_] = t[:k] + '\t' + blk + '\n' + t[k:]
def note(tag, body, x, y):
    return ('(text "%s"\n\t\t(exclude_from_sim no)\n\t\t(at %s %s 0)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t\t(italic yes)\n'
            '\t\t\t)\n\t\t\t(justify left top)\n\t\t)\n\t\t(uuid "%s")\n\t)') % (body, x, round(y + 1.27, 4), U(tag))
log = []

# 1 fiducials
t = get('_TopLevel')
for s, e, k, b in sx.items(t):
    if k == 'symbol' and (sx.ref(b) or '').startswith('FID'):
        X, Y = sx.at(b); assert re.search(r'\(at [-\d.]+ [-\d.]+ 0\)', b) and '(mirror' not in b
        x, y = round(X + 7.62, 4), Y
        insert('_TopLevel', '(no_connect\n\t\t(at %s %s)\n\t\t(uuid "%s")\n\t)' % (x, y, U('nc/' + sx.ref(b))))
        log.append('no-connect on %s pin 0 at (%s, %s)' % (sx.ref(b), x, y))

# 2 pin types
CHANGES = {'POWER_0_LMR51430YDDCR_Sofar Ocean Technologies, Inc.': {'2': 'power_out', '6': 'passive'},
           'POWER_0_c4b2ba52c5c06523be8e235897d707d_Altium Content Vault': {'B2': 'power_out'}}
def retype(sym, changes):
    out = sym; done = []
    for m in list(re.finditer(r'\(pin (\w+) (\w+)\n', sym)):
        st = m.start(); pb = sym[st:sx._close(sym, st)]; num = re.search(r'\(number "([^"]*)"', pb).group(1)
        if num in changes:
            new = pb.replace('(pin %s %s' % (m.group(1), m.group(2)), '(pin %s %s' % (changes[num], m.group(2)), 1)
            out = out.replace(pb, new, 1); done.append((num, m.group(1), changes[num]))
    assert sorted(d[0] for d in done) == sorted(changes), done
    return out, done
LIBF = D / 'BM_Mote_000639-AB-altium-import.kicad_sym'; lib = LIBF.read_text(encoding='utf-8'); pw = get('_Power')
for name, ch in CHANGES.items():
    i = pw.index('\n\t\t(symbol "BM_Mote_000639-AB-altium-import:%s"' % name) + 3; j = sx._close(pw, i)
    new, done = retype(pw[i:j], ch); pw = pw[:i] + new + pw[j:]
    a = lib.index('\n\t(symbol "%s"' % name) + 2; z = sx._close(lib, a)
    new2, done2 = retype(lib[a:z], ch); lib = lib[:a] + new2 + lib[z:]
    assert sorted(done) == sorted(done2); log.append('%s: pins %s' % (name.split('_')[2] if 'LMR' in name else 'TPS62840 (U6)', done))
files['_Power'] = pw

# 3 dangling wire ends: (sheet, uuid prefix)
for s_, u in [('_Power', 'f6812f4b'), ('_Power', '0944b7cc'), ('_PoDL', '08f8a60f'), ('_PoDL', '5c0e86ca'),
              ('_PowerMonitor', '7691c6e3'), ('_ADIN2111', '713f3756'), ('_ADIN2111', '9d26956e')]:
    t = get(s_); pts = geom.points(t); ws = geom.wires(t)
    me = [w for w in ws if w[0].startswith(u)]; assert len(me) == 1; wid, (a, b) = me[0]
    def connected(p):
        return (round(p[0], 4), round(p[1], 4)) in pts or any(
            w[0] != wid and (any(abs(q[0] - p[0]) < 1e-3 and abs(q[1] - p[1]) < 1e-3 for q in w[1]) or geom.on_seg(p, *w[1])) for w in ws)
    cand = [p for p in pts if geom.on_seg(p, a, b)] + [q for w in ws if w[0] != wid for q in w[1] if geom.on_seg(q, a, b)]
    ends = [a, b]
    for n in range(2):
        if not connected(ends[n]):
            far = ends[1 - n]; d = lambda p: abs(p[0] - ends[n][0]) + abs(p[1] - ends[n][1])
            inner = sorted([p for p in cand if d(p) > 1e-6], key=d)
            assert inner, (s_, u, 'nothing on the wire to trim to'); ends[n] = inner[0]
    if abs(ends[0][0] - ends[1][0]) < 1e-6 and abs(ends[0][1] - ends[1][1]) < 1e-6:
        replace_block(s_, lambda k, b_: k == 'wire' and '(uuid "%s' % u in b_, lambda b_: ''); log.append('%s wire %s removed (%s)' % (s_, u, (a, b)))
    else:
        f = lambda v: ('%.4f' % v).rstrip('0').rstrip('.')
        replace_block(s_, lambda k, b_: k == 'wire' and '(uuid "%s' % u in b_,
                      lambda b_: re.sub(r'\(pts\s*\(xy [^)]*\) \(xy [^)]*\)\s*\)', '(pts\n\t\t\t(xy %s %s) (xy %s %s)\n\t\t)' % (f(ends[0][0]), f(ends[0][1]), f(ends[1][0]), f(ends[1][1])), b_))
        log.append('%s wire %s %s -> %s' % (s_, u, (a, b), tuple(ends)))
for s_ in files: files[s_] = re.sub(r'\n\t\n', '\n', files[s_])

# 4 ADIN_VDDIO local label: kept. Removing it splits the net (C13 / C14 / TP2 / U1 18, 46 / U3 A1 from the ADIN_VDDIO power
#   symbols): the "global" power symbol does not join that wire, the local label does. The warning stays, explained.

# 5 inner labels
ONCE = [('_PoDL', 'DATA1_P'), ('_PoDL', 'DATA1_N'), ('_PoDL', 'DATA2_P'), ('_PoDL', 'DATA2_N'), ('_LoadSwitch', 'VBUS_P'),
        ('_Power', '3V3_Buck_Input'), ('_Power', '5V_Buck_Input'), ('_Power', '1V8_Buck_Input')]
TWICE = {'PHY1_P': 'BM1_P', 'PHY1_N': 'BM1_N', 'PHY2_P': 'BM2_P', 'PHY2_N': 'BM2_N'}
for s_, name in ONCE:
    t = get(s_); hits = [b for _, _, k, b in sx.items(t) if k == 'label' and sx.label_name(b) == name]; assert len(hits) == 1, (name, len(hits))
    x, y = sx.at(hits[0]); replace_block(s_, lambda k, b: k == 'label' and sx.label_name(b) == name, lambda b: '')
    insert(s_, note('n/' + name, 'Sofar: ' + name, x, y)); log.append('%s: label %s removed, note left' % (s_, name))
for name, outer in TWICE.items():
    t = get('_PoDL'); labs = [b for _, _, k, b in sx.items(t) if k == 'label' and sx.label_name(b) == name]; assert len(labs) == 2
    hier = [b for _, _, k, b in sx.items(t) if k == 'hierarchical_label' and sx.label_name(b) == outer]; assert len(hier) == 1
    hy = sx.at(hier[0])[1]
    near = [b for b in labs if abs(sx.at(b)[1] - hy) < 1e-3]; far = [b for b in labs if b not in near]; assert len(near) == 1 and len(far) == 1
    xn, yn = sx.at(near[0]); xf, yf = sx.at(far[0])
    files['_PoDL'] = get('_PoDL').replace(near[0], '', 1)
    u = re.search(r'\(uuid "([^"]+)"\)', far[0]).group(1)
    hl = ('(hierarchical_label "%s"\n\t\t(shape passive)\n\t\t(at %s %s 0)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n'
          '\t\t\t(justify left)\n\t\t)\n\t\t(uuid "%s")\n\t)') % (outer, xf, yf, u)
    files['_PoDL'] = get('_PoDL').replace(far[0], hl, 1)
    insert('_PoDL', note('n/%s/near' % name, 'Sofar: ' + name, xn, yn)); insert('_PoDL', note('n/%s/far' % name, 'Sofar: ' + name, xf, yf))
    log.append('PoDL: %s near %s removed; far copy (%s, %s) -> hierarchical %s; notes left' % (name, outer, xf, yf, outer))
for s_ in files: files[s_] = re.sub(r'\n\t\n', '\n', files[s_])

for s_, t in files.items():
    assert t.count('(') == t.count(')'), s_; P(s_).write_text(t, encoding='utf-8')
LIBF.write_text(lib, encoding='utf-8')
print('\n'.join(log))
