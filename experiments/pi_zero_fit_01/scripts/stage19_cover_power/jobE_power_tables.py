"""Stage 19, job E: the cover's POWER table (stage 17) becomes two compact native tables, POWER and EXAMPLE LOADS, with
three footnotes, in the same column (x 142.24 .. 274.24, from y 154.04). Content as given by the coordinator, checked:
0.89 A x 16 / 24 / 32 V = 14.2 / 21.4 / 28.5 W; Raspberry Pi power table (read 2026-11-16): Zero 2 W 350 mA bare, Camera
Module 250 mA, Pi 4 B 3.0 A, Pi 5 5.0 A; 0.73 A x 24 V = 17.5 W; F1 "1.5A hold / 3A trip" (Top-Level sheet).
Usage: python3 jobE_power_tables.py <cover .kicad_sch>
"""
import re, sys, uuid, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage17_schematic_docs')); import sx

F = sys.argv[1]; t = open(F, encoding='utf-8').read()
U = lambda tag: str(uuid.uuid5(uuid.NAMESPACE_URL, 'nereus/pi_zero_fit_01/stage19/cover/' + tag))
OLD = str(uuid.uuid5(uuid.NAMESPACE_URL, 'nereus/pi_zero_fit_01/stage17/cover/power'))
FS, LINE, MARG = 1.27, 1.85, 0.9525          # as the stage-17 tables
X0, Y0, W = 142.24, 154.04, 132.0

def table(tag, x, y, widths, rows):
    heights = [round(2 * MARG + max(c.count('\n') + 1 for c in r) * LINE + 0.2, 2) for r in rows]
    cells = []; yy = y
    for ri, (r, h) in enumerate(zip(rows, heights)):
        xx = x
        for ci, (c, w) in enumerate(zip(r, widths)):
            esc = c.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
            cells.append(('\t\t\t(table_cell "%s"\n\t\t\t\t(exclude_from_sim no)\n\t\t\t\t(at %s %s 0)\n\t\t\t\t(size %s %s)\n'
                          '\t\t\t\t(margins %s %s %s %s)\n\t\t\t\t(span 1 1)\n\t\t\t\t(fill\n\t\t\t\t\t(type none)\n\t\t\t\t)\n'
                          '\t\t\t\t(effects\n\t\t\t\t\t(font\n\t\t\t\t\t\t(size %s %s)%s\n\t\t\t\t\t)\n\t\t\t\t\t(justify left top)\n\t\t\t\t)\n'
                          '\t\t\t\t(uuid "%s")\n\t\t\t)\n') % (esc, round(xx, 3), round(yy, 3), w, h, MARG, MARG, MARG, MARG, FS, FS,
                                                             '\n\t\t\t\t\t\t(bold yes)' if ri == 0 else '', U('%s/%d/%d' % (tag, ri, ci))))
            xx += w
        yy += h
    blk = ('(table\n\t\t(column_count %d)\n\t\t(border\n\t\t\t(external yes)\n\t\t\t(header yes)\n\t\t\t(stroke\n\t\t\t\t(width 0)\n'
           '\t\t\t\t(type solid)\n\t\t\t)\n\t\t)\n\t\t(separators\n\t\t\t(rows yes)\n\t\t\t(cols yes)\n\t\t\t(stroke\n\t\t\t\t(width 0)\n'
           '\t\t\t\t(type solid)\n\t\t\t)\n\t\t)\n\t\t(column_widths %s)\n\t\t(row_heights %s)\n\t\t(uuid "%s")\n\t\t(cells\n%s\t\t)\n\t)') % (
        len(widths), ' '.join(map(str, widths)), ' '.join(map(str, heights)), U(tag), ''.join(cells))
    return blk, round(yy, 2)

def text(tag, body, x, y, size, bold=False, top=False):
    esc = body.replace('"', '\\"').replace('\n', '\\n')
    return ('(text "%s"\n\t\t(exclude_from_sim no)\n\t\t(at %s %s 0)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size %s %s)%s\n\t\t\t)\n'
            '\t\t\t(justify left %s)\n\t\t)\n\t\t(uuid "%s")\n\t)') % (esc, x, round(y, 3), size, size,
                                                                   '\n\t\t\t\t(thickness %s)\n\t\t\t\t(bold yes)' % round(size * 0.2, 4) if bold else '',
                                                                   'top' if top else 'bottom', U(tag))

POWER = [['Description', 'Nominal', 'Max'],
         ['Bus voltage', '24 V', '16 - 32 V'],
         ['Node total power, own load + pass-through\n(0.89 A through port inductors L1 / L2)', '21 W at 24 V', '14 W at 16 V, 28 W at 32 V'],
         ['Node own load, continuous', '8.7 W (Pi Zero 2 W +\nwiper, est.)', '12 W (Bristlemouth\nmodule budget) *'],
         ['5 V rail (U10)', '1.5 A / 7.5 W\ncontinuous *', '2.2 A peak\n(3 A converter)'],
         ['Motor J7 (from the 5 V rail)', '0.5 A', '1.24 A current limit'],
         ['VBUS OUT J5 (bus voltage, on with GPIO26)', 'payload within the\n12 W budget', '0.73 A typ., electronic\nfuse U11'],
         ['AUX 5 V J4 (5 V rail via JP1 2-3)', '-', '1.5 A hold / 3 A trip,\npolyfuse F1']]
FOOT = ['* Thermal limit of U10: bench validation pending.',
        'The 5 V rail, the payload and the 3.3 V logic all draw from the 12 W own-load budget: 7.5 W on the 5 V rail is about 8.4 W from the bus.',
        "VBUS OUT's 0.73 A limit (17.5 W at 24 V) is above that budget: it protects the port, it does not enforce the budget."]
LOADS = [['Load', 'Current at 5 V', 'Power', 'From this board'],
         ['Pi Zero 2 W + camera,\nvideo streaming', '1.0 A design allowance\n(typ. 0.35 A bare + 0.25 A camera)', '5 W', 'yes'],
         ['DC motor, wiper', '0.5 A continuous,\nspikes under 1 A', '2.5 W', 'yes'],
         ['Pi 4 B', 'recommended supply 3.0 A', '15 W', 'no: power the Pi\nseparately'],
         ['Pi 5', 'recommended supply 5.0 A', '25 W', 'no: power the Pi\nseparately']]

its = sx.items(t)
old = [(s, e) for s, e, k, b in its if k == 'table' and '(uuid "%s")' % OLD in b]
assert len(old) == 1, old
y = Y0 + 2.6
h1 = text('t_power', 'POWER', X0, y, 1.524, bold=True)
tb1, y = table('power', X0, y + 0.6, [56.0, 38.0, 38.0], POWER)
fn = text('foot', '\n'.join(FOOT), X0, y + 0.8, 1.0, top=True)
y += 0.8 + 3 * 1.65 + 3.4
h2 = text('t_loads', 'EXAMPLE LOADS', X0, y, 1.524, bold=True)
tb2, y_end = table('loads', X0, y + 0.6, [34.0, 50.0, 14.0, 34.0], LOADS)
print('POWER table + footnotes + EXAMPLE LOADS: y %.2f .. %.2f (licence text starts at 243.84)' % (Y0, y_end))
assert y_end < 241.0
s, e = old[0]
new = '\n\t'.join([h1, tb1, fn, h2, tb2])
t = t[:s] + new + t[e:]
assert t.count('(') == t.count(')')
open(F, 'w', encoding='utf-8').write(t); print('cover written')
