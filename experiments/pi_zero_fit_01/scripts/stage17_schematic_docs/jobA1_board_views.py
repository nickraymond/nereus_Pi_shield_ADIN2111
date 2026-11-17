"""Stage 17, job A step 1: the cover's board-views picture for this board (65.00 x 39.50 mm).

Reads the outline, thickness, copper layer count and mounting holes from the board (KiCad Python; run with the KiCad
python), renders top and bottom with kicad-cli (orthographic, straight on), finds the board edge in each render (the
solder-mask green), crops to it on white, and composes an SVG with dimension lines, view labels and the caption; Chrome
rasterises it. Outputs go to the stage-17 NereusData folder.  Usage: python3 jobA1_board_views.py <board.kicad_pcb>
"""
import json, os, subprocess, sys
from PIL import Image, ImageChops

PCB = sys.argv[1]
O = os.path.expanduser('~/NereusData/nereus_Pi_shield_ADIN2111/pi_zero_fit_2026-11-15/stage17_schematic_docs/jobA')
os.makedirs(O, exist_ok=True)
CLI = '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

# ---- figures from the board file (read by KiCad's own python in a child process)
KPY = '/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3'
FIGS = r'''
import sys, json, pcbnew
PCB = sys.argv[1]
b = pcbnew.LoadBoard(PCB); mm = pcbnew.ToMM
edges = [d for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts]
arcs = [d for d in edges if d.GetShapeStr() == 'Arc']
radii = sorted({round(mm(d.GetRadius()), 3) for d in arcs}); assert len(arcs) == 4 and len(radii) == 1, (len(arcs), radii)
r = radii[0]
cx = sorted({round(mm(d.GetCenter().x), 3) for d in arcs}); cy = sorted({round(mm(d.GetCenter().y), 3) for d in arcs})
W = round(cx[-1] - cx[0] + 2 * r, 3); H = round(cy[-1] - cy[0] + 2 * r, 3)
T = mm(b.GetDesignSettings().GetBoardThickness()); NL = b.GetCopperLayerCount()
holes = [f for f in b.GetFootprints() if f.GetReference().startswith('H') and 'MountingHole' in f.GetFPIDAsString()]
hx = sorted({round(mm(f.GetPosition().x), 3) for f in holes}); hy = sorted({round(mm(f.GetPosition().y), 3) for f in holes})
drills = sorted({round(mm(p.GetDrillSize().x), 3) for f in holes for p in f.Pads()})
assert len(holes) == 4 and len(drills) == 1, (len(holes), drills)
hw, hh = round(hx[-1] - hx[0], 3), round(hy[-1] - hy[0], 3)
fig = dict(W=W, H=H, r=r, T=T, NL=NL, n=len(holes), drill=drills[0], hw=hw, hh=hh, fp=holes[0].GetFPIDAsString())
print(json.dumps(fig))
'''
res = subprocess.run([KPY, '-c', FIGS, PCB], check=True, capture_output=True, text=True)
fig = json.loads(res.stdout.strip().splitlines()[-1]); globals().update(fig)
r, T, NL, hw, hh = fig['r'], fig['T'], fig['NL'], fig['hw'], fig['hh']
holes = [None] * fig['n']; drills = [fig['drill']]
print('board figures:', fig)
assert (W, H, r, T, NL, hw, hh, drills[0]) == (65.0, 39.5, 3.0, 1.6, 6, 58.0, 23.0, 2.75), 'figures differ from the caption text'

# ---- renders, cropped at the board edge
views = {}
for side in ('top', 'bottom'):
    png = os.path.join(O, 'render_%s.png' % side)
    subprocess.run([CLI, 'pcb', 'render', '--side', side, '--width', '2400', '--height', '1600', '--background', 'transparent',
                    '--quality', 'high', '-o', png, PCB], check=True, capture_output=True)
    im = Image.open(png).convert('RGBA'); R, G, B_, A = im.split()
    green = ImageChops.multiply(ImageChops.subtract(G, R).point(lambda v: 255 if v > 15 else 0), A.point(lambda v: 255 if v > 200 else 0))
    bb = green.getbbox(); w, h = bb[2] - bb[0], bb[3] - bb[1]
    print('  %s: board edge in render %s, %.2f x %.2f px/mm' % (side, bb, w / W, h / H))
    assert abs((w / h) / (W / H) - 1) < 0.01, 'render aspect does not match the outline'
    crop = im.crop(bb); white = Image.new('RGBA', crop.size, (255, 255, 255, 255)); white.alpha_composite(crop)
    out = os.path.join(O, 'view_%s.png' % side); white.convert('RGB').save(out); views[side] = (out, w, h)

# ---- SVG composition (units = CSS px)
VW = 760; VH = VW * H / W                 # each view drawn at 760 px wide
X1, X2, Y0 = 120, 1030, 120
CW, CH = 1910, Y0 + VH + 150
def dim_h(x0, x1, y_board, y_line, text):
    return ('<line x1="{a}" y1="{yb}" x2="{a}" y2="{e}" class="ext"/><line x1="{b}" y1="{yb}" x2="{b}" y2="{e}" class="ext"/>'
            '<line x1="{a}" y1="{y}" x2="{b}" y2="{y}" class="dim" marker-start="url(#ar)" marker-end="url(#ar)"/>'
            '<text x="{c}" y="{t}" class="lab" text-anchor="middle">{s}</text>').format(
        a=x0, b=x1, yb=y_board - 6, e=y_line - 10, y=y_line, c=(x0 + x1) / 2, t=y_line - 14, s=text)
def dim_v(y0, y1, x_board, x_line, text, side):
    tx = x_line - 16 if side == 'left' else x_line + 16
    rot = -90 if side == 'left' else 90
    xb = x_board - 6 if side == 'left' else x_board + 6
    xe = x_line - 10 if side == 'left' else x_line + 10
    return ('<line x1="{xb}" y1="{a}" x2="{xe}" y2="{a}" class="ext"/><line x1="{xb}" y1="{b}" x2="{xe}" y2="{b}" class="ext"/>'
            '<line x1="{x}" y1="{a}" x2="{x}" y2="{b}" class="dim" marker-start="url(#ar)" marker-end="url(#ar)"/>'
            '<text x="{tx}" y="{c}" class="lab" text-anchor="middle" transform="rotate({rot} {tx} {c})">{s}</text>').format(
        xb=xb, xe=xe, a=y0, b=y1, x=x_line, tx=tx, c=(y0 + y1) / 2, rot=rot, s=text)
ws, hs = '%.2f mm' % W, '%.2f mm' % H
caption = ('Outline %.2f x %.2f mm, corners R%.1f, %.1f mm thick, %d copper layers. %d mounting holes %.2f mm (M2.5) on the '
           'Raspberry Pi Zero pattern, %.1f x %.1f mm.' % (W, H, r, T, NL, len(holes), drills[0], hw, hh))
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{CW}" height="{CH:.0f}" viewBox="0 0 {CW} {CH:.0f}">
<defs><marker id="ar" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="12" markerHeight="12" orient="auto-start-reverse" markerUnits="userSpaceOnUse">
<path d="M0,1 L12,6 L0,11 z" fill="#000"/></marker>
<style>.ext{{stroke:#000;stroke-width:1.2}} .dim{{stroke:#000;stroke-width:1.6}} .lab{{font:30px Helvetica,Arial,sans-serif;fill:#000}}
.title{{font:36px Helvetica,Arial,sans-serif;fill:#000}} .cap{{font:24px Helvetica,Arial,sans-serif;fill:#000}}</style></defs>
<rect width="100%" height="100%" fill="#fff"/>
<image x="{X1}" y="{Y0}" width="{VW}" height="{VH:.2f}" xlink:href="view_top.png" preserveAspectRatio="none"/>
<image x="{X2}" y="{Y0}" width="{VW}" height="{VH:.2f}" xlink:href="view_bottom.png" preserveAspectRatio="none"/>
{dim_h(X1, X1 + VW, Y0, Y0 - 40, ws)}
{dim_h(X2, X2 + VW, Y0, Y0 - 40, ws)}
{dim_v(Y0, Y0 + VH, X1, X1 - 40, hs, 'left')}
{dim_v(Y0, Y0 + VH, X2 + VW, X2 + VW + 40, hs, 'right')}
<text x="{X1 + VW / 2}" y="{Y0 + VH + 60:.1f}" class="title" text-anchor="middle">TOP VIEW</text>
<text x="{X2 + VW / 2}" y="{Y0 + VH + 60:.1f}" class="title" text-anchor="middle">BOTTOM VIEW (seen from below)</text>
<text x="{CW / 2}" y="{Y0 + VH + 118:.1f}" class="cap" text-anchor="middle">{caption}</text>
</svg>'''
sp = os.path.join(O, 'board_views.svg'); open(sp, 'w').write(svg)
png = os.path.join(O, 'board_views_raw.png')
subprocess.run([CHROME, '--headless', '--disable-gpu', '--hide-scrollbars', '--allow-file-access-from-files',
                '--force-device-scale-factor=2', '--window-size=%d,%d' % (CW, int(CH)), '--screenshot=' + png, 'file://' + sp],
               check=True, capture_output=True)
im = Image.open(png).convert('RGB')
q = im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
final = os.path.join(O, 'board_views.png'); q.save(final, optimize=True, dpi=(300, 300))
print('caption:', caption)
print('picture %s: %d x %d px, %.0f kB' % (final, *q.size, os.path.getsize(final) / 1024))
