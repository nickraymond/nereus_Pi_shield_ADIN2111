"""Stage 17, jobs A and B: the cover page (page 1), text level.

A: the board-views picture (jobA1_board_views.py output) replaces the old full-size board picture, centred on the same
   x, the frame shortened to fit it; DIMENSIONS text 65.00 x 39.50 x 1.6 mm; the I2C address picture becomes a native
   table (style of page 2's tables); the index gains page 8.
B: three native tables (POWER, I/O FOR DEVELOPERS, NOTES) under the picture. Every figure's source is listed in
   SOURCES below and in the stage-17 report.
Usage: python3 jobAB_cover.py <board dir> <board_views.png>
"""
import base64, re, sys, uuid
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent)); import sx

D = Path(sys.argv[1]); F = D / 'Nereus_Pi_Shield_Adin2111.kicad_sch'; PIC = Path(sys.argv[2])
t = F.read_text(encoding='utf-8')
U = lambda tag: str(uuid.uuid5(uuid.NAMESPACE_URL, 'nereus/pi_zero_fit_01/stage17/cover/' + tag))
FS = 1.27                 # table text size (page 2's tables)
LINE = 1.85               # line pitch of 1.27 mm text in a cell (measured on the render)
MARG = 0.9525

def one(pattern, repl, text, count=1):
    new, n = re.subn(pattern, repl, text, count=count)
    assert n == count, (pattern, n); return new

# ---------------------------------------------------------------- A1: picture and frame
FX0, FX1, FY0 = 142.24, 403.86, 53.34
IMG_W = 220.0                                         # mm on the sheet
im = Image.open(PIC); pw, ph = im.size
IMG_H = IMG_W * ph / pw
FY1 = round(FY0 + IMG_H + 6.0, 2)                     # 3 mm white margin above and below the picture
scale = IMG_W / (pw / 300 * 25.4)                     # KiCad: 300 ppi at scale 1
cx, cy = round((FX0 + FX1) / 2, 3), round((FY0 + FY1) / 2, 3)
data = base64.b64encode(PIC.read_bytes()).decode()
chunks = [data[i:i + 76] for i in range(0, len(data), 76)]
img_blk = ('(image\n\t\t(at %s %s)\n\t\t(scale %.5f)\n\t\t(uuid "cfca9b83-9af9-44a2-b787-9334cd75e63d")\n\t\t(data "%s"'
           % (cx, cy, scale, chunks[0]) + ''.join('\n\t\t\t"%s"' % c for c in chunks[1:]) + '\n\t\t)\n\t)')
its = sx.items(t)
old_img = [(s, e) for s, e, k, b in its if k == 'image' and 'cfca9b83-9af9-44a2-b787-9334cd75e63d' in b]
i2c_img = [(s, e) for s, e, k, b in its if k == 'image' and '9635467d-52c8-4ba7-9bf9-07be27b77d4f' in b]
assert len(old_img) == 1 and len(i2c_img) == 1
# ---------------------------------------------------------------- tables
def table(tag, x, y, widths, rows, header=True, bold_first_col=False):
    """rows: list of lists of cell strings ('\n' = line break). Row height from the line count."""
    heights = []
    for r in rows:
        n = max(c.count('\n') + 1 for c in r)
        heights.append(round(2 * MARG + n * LINE + 0.2, 2))
    cells = []; yy = y
    for ri, (r, h) in enumerate(zip(rows, heights)):
        xx = x
        for ci, (c, w) in enumerate(zip(r, widths)):
            bold = (header and ri == 0) or (bold_first_col and ci == 0)
            esc = c.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
            cells.append(('\t\t\t(table_cell "%s"\n\t\t\t\t(exclude_from_sim no)\n\t\t\t\t(at %s %s 0)\n\t\t\t\t(size %s %s)\n'
                          '\t\t\t\t(margins %s %s %s %s)\n\t\t\t\t(span 1 1)\n\t\t\t\t(fill\n\t\t\t\t\t(type none)\n\t\t\t\t)\n'
                          '\t\t\t\t(effects\n\t\t\t\t\t(font\n\t\t\t\t\t\t(size %s %s)%s\n\t\t\t\t\t)\n\t\t\t\t\t(justify left top)\n\t\t\t\t)\n'
                          '\t\t\t\t(uuid "%s")\n\t\t\t)\n') % (esc, round(xx, 3), round(yy, 3), w, h, MARG, MARG, MARG, MARG, FS, FS,
                                                             '\n\t\t\t\t\t\t(bold yes)' if bold else '', U('%s/%d/%d' % (tag, ri, ci))))
            xx += w
        yy += h
    blk = ('(table\n\t\t(column_count %d)\n\t\t(border\n\t\t\t(external yes)\n\t\t\t(header %s)\n\t\t\t(stroke\n\t\t\t\t(width 0)\n'
           '\t\t\t\t(type solid)\n\t\t\t)\n\t\t)\n\t\t(separators\n\t\t\t(rows yes)\n\t\t\t(cols yes)\n\t\t\t(stroke\n\t\t\t\t(width 0)\n'
           '\t\t\t\t(type solid)\n\t\t\t)\n\t\t)\n\t\t(column_widths %s)\n\t\t(row_heights %s)\n\t\t(uuid "%s")\n\t\t(cells\n%s\t\t)\n\t)') % (
        len(widths), 'yes' if header else 'no', ' '.join(map(str, widths)), ' '.join(map(str, heights)), U(tag), ''.join(cells))
    return blk, round(yy, 2)

def text(tag, body, x, y, size=2.54, bold=True):
    return ('(text "%s"\n\t\t(exclude_from_sim no)\n\t\t(at %s %s 0)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size %s %s)%s\n\t\t\t)\n'
            '\t\t\t(justify left bottom)\n\t\t)\n\t\t(uuid "%s")\n\t)') % (body, x, y, size, size,
                                                                   '\n\t\t\t\t(thickness %s)\n\t\t\t\t(bold yes)' % round(size * 0.2, 4) if bold else '', U(tag))

# A3: I2C address table (from the schematic: page 2's I2C table, PowerMonitor / MotorADC notes, J1 / J3 nets, R50)
I2C = [['Bus', 'Pi pins', 'Device', 'Address'],
       ['I2C0', 'GPIO0 / GPIO1\n(pins 27 / 28)', 'INA232 bus power monitor (U4)', '0x41'],
       ['I2C0', 'GPIO0 / GPIO1', 'ADS1115 ADC (U13), ADDR to GND (R50)', '0x48'],
       ['I2C0', 'GPIO0 / GPIO1', 'keep free: HAT EEPROM probe at boot', '0x50'],
       ['I2C1', 'GPIO2 / GPIO3\n(pins 3 / 5)', 'none on this board; free for a\nLiFePO4wered UPS', '0x43'],
       ['I2C3 (sw)', 'GPIO22 / GPIO27\n(pins 15 / 13)', 'Qwiic J3 only, no device on board', '-']]
i2c_tbl, _ = table('i2c', 25.4, 176.53, [16.0, 25.4, 52.0, 14.0], I2C)

# ---------------------------------------------------------------- B: developer spec
SY = FY1 + 9.0                        # headings' baseline
POWER = [['POWER', 'Rating', 'Notes'],
         ['Bus in, PoDL on BM1 J10 /\nBM2 J9', '24 V nominal, 16-32 V', 'Bristlemouth bus'],
         ['Per port', '0.89 A max (21.4 W at 24 V)', 'port inductor L1 / L2: own load\nplus pass-through to other modules'],
         ['Module budget', '12 W per module', 'shield + Pi + payload together'],
         ['5 V rail (U10 LMR51430,\n3 A converter)', '1.5 A = 7.5 W continuous\n(Pi 1.0 A + motor 0.5 A);\npeaks about 2.2 A',
          'design target, thermally limited\nby U10: bench check pending'],
         ['Pi model on the 5 V rail', 'Zero 2 W: 2 A PSU, 350 mA typ.\n4 B: 3.0 A PSU, 600 mA typ.\n5: 5.0 A PSU, 800 mA typ.',
          'Pi 4 / 5 can draw more than this\nrail\'s 1.0 A Pi share: budget it or\npower the Pi separately'],
         ['3.3 V rail (U5 LMR51430)', 'shield logic only', 'ADIN2111, INA232, ADS1115, pot;\nPi 3V3 pads are the Pi\'s own rail'],
         ['Payload J5 VBUS OUT', 'bus voltage, 0.73 A typ. limit', 'U11 TPS26621 eFuse; on: GPIO26\nhigh; fault: GPIO6 low'],
         ['AUX 5 V J4', '5 V rail via JP1 2-3 and F1', 'F1 polyfuse 1.5 A hold / 3 A trip;\nJP1 as built (1-2) feeds the Pi'],
         ['Motor J7 (U12 MP6550)', 'limit 1.24 A (R48 4.02 kOhm)', 'on the 5 V rail; design load\n0.5 A continuous']]
IO = [['I/O FOR DEVELOPERS', 'Pins (nets)'],
      ['Pad row under the header\n(2.54 mm, bare holes)', 'J15: 5 V (PI_5V), GND, GPIO14 TX, GPIO15 RX (UART)\nJ16: PI_3V3, PI_3V3   J17: GND, GPIO17\n'
       'J18: GPIO12, GPIO7, GND, GND   J19: GPIO19, GPIO20, GPIO21'],
      ['Qwiic J3', 'I2C3 (software, GPIO22 SDA / GPIO27 SCL), PI_3V3, GND'],
      ['POT J8 (JST GH 3)', '1 = 3V3 (shield), 2 = wiper to ADC AIN1, 3 = GND'],
      ['MOTOR J7 (JST GH 4)', '1-2 = OUT1, 3-4 = OUT2 (MP6550 H-bridge)'],
      ['BM1 J10 / BM2 J9 (JST GH 4)', '1-2 = N, 3-4 = P (bus power + 10BASE-T1L data)'],
      ['AUX 5 V J4 / VBUS OUT J5', 'wire pads: 1 = +, 2 = GND'],
      ['GPIO used by the shield', 'SPI0 (GPIO8-11) + GPIO23 PWR, 24 RST, 25 INT, 16 TIMER: ADIN2111\n'
       'GPIO26 payload on, GPIO6 payload fault   GPIO4 ADC alert\nGPIO13 / GPIO18 motor IN1 / IN2 (PWM), GPIO5 motor sleep\n'
       'GPIO0 / 1 I2C0   GPIO22 / 27 I2C3   GPIO2 / 3 left free (I2C1)']]
NOTES = [['NOTES'],
         ['No USB power on the Pi while JP1 feeds it (JP1 1-2, as built).'],
         ['ADIN2111 SPI mode as built: JP3 CFG1 = 1, JP4 CFG0 = 0: generic SPI + CRC (row not checked\nagainst the datasheet; only CFG 0 0 is).'],
         ['Motor current reads on ADC AIN0 at 0.402 V/A (MP6550 VISEN).'],
         ['ADC inputs AIN2 / AIN3 are not brought out.'],
         ['Mounting: M2.5 screws, 2.75 mm holes.'],
         ['Board views: layout of commit 955d57c, 2026-11-16 (schematic rev AA).']]
X0 = FX0
pw_ = [38.0, 46.0, 48.0]                       # POWER widths: 132 mm
iw_ = [40.0, 89.62]                            # I/O widths: 129.62 mm (to the frame's right edge)
p_tbl, p_end = table('power', X0, SY + 1.5, pw_, POWER, bold_first_col=False)
i_tbl, i_end = table('io', X0 + sum(pw_), SY + 1.5, iw_, IO)
n_tbl, n_end = table('notes', X0 + sum(pw_), i_end + 2.54, [sum(iw_)], NOTES)
heading = text('spec_heading', 'DEVELOPER SPEC (summary; details on the following pages)', X0, SY - 0.5, 2.54, True)
print('frame y %.2f..%.2f, picture %.1f x %.1f mm, scale %.5f; spec tables end at y %.2f (power) / %.2f (io + notes)'
      % (FY0, FY1, IMG_W, IMG_H, scale, p_end, n_end))
assert max(p_end, n_end) < 236.0, 'spec runs into the licence text'

# ---------------------------------------------------------------- apply
new = []; i = 0
for s, e in sorted(old_img + i2c_img):
    new.append(t[i:s]); new.append(img_blk if (s, e) == old_img[0] else i2c_tbl); i = e
new.append(t[i:]); t = ''.join(new)
t = one(r'\(start 142\.24 53\.34\)\n\t\t\(end 403\.86 228\.6\)', '(start 142.24 53.34)\n\t\t(end 403.86 %s)' % FY1, t)
t = one(r'\(text "65\.00 x 56\.00 x 1\.6 mm"', '(text "65.00 x 39.50 x 1.6 mm"', t)
assert t.count('7  Power (buck converters)"') == 1
t = t.replace('7  Power (buck converters)"', '7  Power (buck converters)\\n8  Motor driver + ADC"')
t = one(r'\(text "I2c Address Table"', '(text "I2C Address Table"', t)
k = t.rindex('\n\t(sheet\n') + 1
t = t[:k] + '\t' + heading + '\n\t' + p_tbl + '\n\t' + i_tbl + '\n\t' + n_tbl + '\n' + t[k:]
assert t.count('(') == t.count(')')
F.write_text(t, encoding='utf-8'); print('cover written')
