"""Stage 17, job C step 1: move the motor driver (U12 group, J7), the ADC (U13 group, J8) and test points TP40..TP43 from the
Top-Level sheet into a new hierarchical sub-sheet "Motor + ADC" (file ..._MotorADC.kicad_sch, page 8). Text level only.

- Every moved item keeps its text and UUID; symbols keep their references; their instance path gets the new sheet's UUID.
- Items are picked by region (page-2 coordinates) and checked against the expected reference list.
- Labels of nets that leave the block become hierarchical labels (passive); the block's own nets keep local labels.
- On page 2 the block is replaced by a sheet symbol with one pin per crossing net, each wired to a local label of the same
  name (the nets keep their names), and a title text box "MOTOR DRIVER + ADC" in the style of the other blocks.
Usage: python3 jobC1_schematic.py <board dir>
"""
import re, sys, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent)); import sx

D = Path(sys.argv[1]); TOPF = D / 'Nereus_Pi_Shield_Adin2111_TopLevel.kicad_sch'; NEWF = D / 'Nereus_Pi_Shield_Adin2111_MotorADC.kicad_sch'
ROOT, TOPSHEET = '30e82bf5-1344-486b-817c-02d3b0649ce4', '3c398828-e355-49f6-be37-cb3640d2c671'
SHEET_UUID = str(uuid.uuid5(uuid.NAMESPACE_URL, 'nereus/pi_zero_fit_01/stage17/motor_adc_sheet'))   # stable across reruns
NAME, PAGE = 'Motor + ADC', '8'
PARTS = {'U12', 'C60', 'C61', 'C62', 'C63', 'C64', 'C66', 'R48', 'J7', 'U13', 'C65', 'C67', 'R49', 'R50', 'R51', 'J8',
         'TP40', 'TP41', 'TP42', 'TP43'}
CROSS = ['5V_PI', 'MOTOR_IN1', 'MOTOR_IN2', 'MOTOR_nSLEEP', '~{ADC_ALERT}', 'I2C0_SDA', 'I2C0_SCL']
# page-2 regions (x0, x1, y0, y1) and where each lands on the new A3 sheet (dx, dy)
REGIONS = {'motor': ((170, 395, 262, 345), (-140, -215)),
           'adc':   ((400, 585, 268, 345), (-370, -110)),
           # test points TP40..TP43 (one column on page 2) become a row beside J7, 22 mm apart
           'tp40':  ((15, 25, 165, 177), (250, -105)),
           'tp41':  ((15, 25, 177, 187), (272, -115.16)),
           'tp42':  ((15, 25, 187, 197.5), (294, -125.32)),
           'tp43':  ((15, 25, 197.5, 210), (316, -135.48))}

top = TOPF.read_text(encoding='utf-8'); assert not NEWF.exists(), 'new sheet exists already: start from the committed files'
its = sx.items(top)

def region(p):
    for k, ((x0, x1, y0, y1), _) in REGIONS.items():
        if x0 <= p[0] <= x1 and y0 <= p[1] <= y1: return k
    return None

pick = []   # (start, end, kind, block, region)
for s, e, k, b in its:
    if k in ('wire',):
        rs = {region(p) for p in sx.pts(b)}
        if len(rs) == 1 and None not in rs: pick.append((s, e, k, b, rs.pop()))
    elif k in ('symbol', 'junction', 'no_connect', 'label', 'text', 'text_box', 'global_label', 'hierarchical_label'):
        r = region(sx.at(b))
        if r: pick.append((s, e, k, b, r))
refs = {sx.ref(b) for _, _, k, b, _ in pick if k == 'symbol'}
parts = {r for r in refs if not r.startswith('#')}
assert parts == PARTS, ('picked parts differ', sorted(parts ^ PARTS))
assert not [b for _, _, k, b, _ in pick if k == 'global_label'], 'a global label in the block'
print('moved: %d items; parts %s; power symbols %s' % (len(pick), ' '.join(sorted(parts)), ' '.join(sorted(refs - parts))))

# wires by end point, to turn labels into hierarchical labels that point away from their wire
wires = [sx.pts(b) for _, _, k, b, _ in pick if k == 'wire']
def facing(p):
    """180 when the label's wire runs to the right of its anchor (label points left), else 0."""
    for w in wires:
        for i, q in enumerate(w):
            if abs(q[0] - p[0]) < 1e-3 and abs(q[1] - p[1]) < 1e-3:
                o = w[1 - i]
                if o[0] > p[0] + 1e-3: return 180
                return 0
    raise SystemExit('label at %s has no wire' % (p,))

out_blocks, converted = [], []
for s, e, k, b, r in pick:
    dx, dy = REGIONS[r][1]
    if k == 'symbol':
        b2 = b.replace('(path "/%s/%s"' % (ROOT, TOPSHEET), '(path "/%s/%s/%s"' % (ROOT, TOPSHEET, SHEET_UUID))
        assert b2.count(SHEET_UUID) == 1, sx.ref(b)
        b = b2
    if k == 'label' and sx.label_name(b) in CROSS:
        name = sx.label_name(b); p = sx.at(b); rot = facing(p)
        u = re.search(r'\(uuid "([^"]+)"\)', b).group(1)
        b = ('(hierarchical_label "%s"\n\t\t(shape passive)\n\t\t(at %s %s %d)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n'
             '\t\t\t)\n\t\t\t(justify %s)\n\t\t)\n\t\t(uuid "%s")\n\t)') % (name, sx.at(b)[0], sx.at(b)[1], rot, 'right' if rot == 180 else 'left', u)
        converted.append(name)
    out_blocks.append(sx.shift(b, dx, dy))
print('labels made hierarchical:', sorted(converted))
assert set(converted) == set(CROSS), sorted(set(CROSS) - set(converted))

# lib symbols the moved symbols use, copied from the Top-Level sheet
lib_ids = sorted({re.search(r'\(lib_id "([^"]+)"\)', b).group(1) for _, _, k, b, _ in pick if k == 'symbol'})
libs_blk = next(b for _, _, k, b in its if k == 'lib_symbols')
libs = []
for m in re.finditer(r'\n\t\t\(symbol "((?:[^"\\]|\\.)*)"', libs_blk):
    if m.group(1) in lib_ids:
        st = m.start() + 1; libs.append(libs_blk[st:sx._close(libs_blk, st + 2)])
assert len(libs) == len(lib_ids), (lib_ids, len(libs))

new_uuid = str(uuid.uuid5(uuid.NAMESPACE_URL, 'nereus/pi_zero_fit_01/stage17/motor_adc_file'))
head = ('(kicad_sch\n\t(version 20260306)\n\t(generator "eeschema")\n\t(generator_version "10.0")\n\t(uuid "%s")\n\t(paper "A3")\n'
        '\t(title_block\n\t\t(title "Motor Driver + ADC")\n\t\t(date "2026-11-16")\n\t\t(rev "AA")\n'
        '\t\t(comment 1 "${PCBPARTNAME} · ${PCBPARTNUMBER}")\n\t\t(comment 2 "Author: ${AUTHOR}")\n'
        '\t\t(comment 3 "Derived from Sofar Bristlemouth mote 000639-AB")\n\t)\n' % new_uuid)

# page 2: remove the moved items, add the sheet symbol, its wires and labels, and the title
cut = sorted((s, e) for s, e, *_ in pick)
t = []; i = 0
for s, e in cut:
    t.append(top[i:s].rstrip('\t')); i = e
    if top[i] == '\n': i += 1
t.append(top[i:]); top2 = ''.join(t)

SX, SY, SW, SH = 241.3, 290.83, 50.8, 25.4     # sheet symbol where the motor driver was
U = lambda tag: str(uuid.uuid5(uuid.NAMESPACE_URL, 'nereus/pi_zero_fit_01/stage17/' + tag))
pins, extra = [], []
for n, name in enumerate(CROSS):
    y = round(SY + 5.08 + 2.54 * n, 2)
    pins.append('\t\t(pin "%s" passive\n\t\t\t(at %s %s 180)\n\t\t\t(uuid "%s")\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n'
                '\t\t\t\t)\n\t\t\t\t(justify left)\n\t\t\t)\n\t\t)\n' % (name, SX, y, U('pin/' + name)))
    x0 = round(SX - 17.78, 2)
    extra.append('\t(wire\n\t\t(pts\n\t\t\t(xy %s %s) (xy %s %s)\n\t\t)\n\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)\n'
                 '\t\t(uuid "%s")\n\t)\n' % (x0, y, SX, y, U('wire/' + name)))
    extra.append('\t(label "%s"\n\t\t(at %s %s 0)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n'
                 '\t\t\t(justify left bottom)\n\t\t)\n\t\t(uuid "%s")\n\t)\n' % (name, x0, y, U('label/' + name)))
tb = next(b for _, _, k, b, _ in pick if k == 'text_box' and b.startswith('(text_box "MOTOR DRIVER'))
tb = re.sub(r'\(uuid "[^"]+"\)', '(uuid "%s")' % U('title'), tb.replace('"MOTOR DRIVER - MP6550"', '"MOTOR DRIVER + ADC"', 1))
tb = re.sub(r'\(at [-\d.]+ [-\d.]+ 0\)', '(at %s %s 0)' % (SX, round(SY + SH + 5.08, 2)), tb, count=1)
extra.append('\t' + tb + '\n')
tp_title = re.sub(r'\(uuid "[^"]+"\)', '(uuid "%s")' % U('tp_title'), tb.replace('"MOTOR DRIVER + ADC"', '"TEST POINTS"', 1))
tp_title = re.sub(r'\(at [-\d.]+ [-\d.]+ 0\)', '(at 260.35 50.8 0)', tp_title, count=1).replace('(size 120 6.35)', '(size 80 6.35)')
body = head + '\t(lib_symbols\n' + ''.join('\t\t' + l + '\n' for l in libs) + '\t)\n' + ''.join('\t' + b + '\n' for b in out_blocks + [tp_title]) + ')\n'
assert body.count('(') == body.count(')')
NEWF.write_text(body, encoding='utf-8')
ls = next(b for _, _, k, b in its if k == 'sheet' and '"Load Switch"' in b)
sheet = ('(sheet\n\t\t(at %s %s)\n\t\t(size %s %s)\n' % (SX, SY, SW, SH)) + ls[ls.index('\t\t(exclude_from_sim'):ls.index('\t\t(uuid')]
sheet += '\t\t(uuid "%s")\n' % SHEET_UUID
sheet += ('\t\t(property "Sheetname" "%s"\n\t\t\t(at %s %s 0)\n' % (NAME, SX, round(SY - 2.54, 2))) + \
         '\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(justify left bottom)\n\t\t\t)\n\t\t)\n'
sheet += ('\t\t(property "Sheetfile" "%s"\n\t\t\t(at %s %s 0)\n' % (NEWF.name, SX, SY)) + \
         '\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(justify left bottom)\n\t\t\t)\n\t\t)\n'
sheet += ''.join(pins)
sheet += '\t\t(instances\n\t\t\t(project "Nereus_Pi_Shield_Adin2111"\n\t\t\t\t(path "/%s/%s"\n\t\t\t\t\t(page "%s")\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)' % (ROOT, TOPSHEET, PAGE)
# insert the new items before the first sheet block (sheets stay together)
k = top2.index('\n\t(sheet\n') + 1
top2 = top2[:k] + '\t' + sheet + '\n' + ''.join(extra) + top2[k:]
assert top2.count('(') == top2.count(')')
TOPF.write_text(top2, encoding='utf-8')
print('wrote', NEWF.name, 'and the Top-Level sheet; sheet uuid', SHEET_UUID)
