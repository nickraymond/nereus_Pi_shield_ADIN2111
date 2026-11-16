"""Crop a kicad-cli render (whole board, default view) to a board window. Usage: <KiCad python> crop.py <in.png> <out.png> <top|bottom> x0 y0 x1 y1   (new-frame mm)
The board (65 x 39.5 mm) lies between 17.6 % and 82.3 % of the image width and 20.15 % and 79.8 % of its height (measured on a 2400 x 1600 render);
the bottom view is mirrored left-right."""
import sys, wx
app = wx.App(False); im = wx.Image(sys.argv[1]); W, H = im.GetWidth(), im.GetHeight()
x0, y0, x1, y1 = [float(a) for a in sys.argv[4:8]]
if sys.argv[3] == 'bottom': x0, x1 = 65.0 - x1, 65.0 - x0
fx = lambda x: int((0.176 + (0.823 - 0.176) * x / 65.0) * W); fy = lambda y: int((0.2015 + (0.798 - 0.2015) * y / 39.5) * H)
im.GetSubImage(wx.Rect(fx(x0), fy(y0), fx(x1) - fx(x0), fy(y1) - fy(y0))).SaveFile(sys.argv[2], wx.BITMAP_TYPE_PNG)
