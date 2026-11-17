#!/bin/zsh
# svg2png.sh <file.svg> <out.png> <width px> <height px>: rasterise an SVG with headless Chrome (whole page, no crop).
set -e
in=${1:A}; out=${2:A}; w=$3; h=$4
tmp=$(mktemp -d); html=$tmp/p.html
print "<html><body style='margin:0;background:white'><img src='file://$in' style='width:${w}px;height:${h}px;display:block'></body></html>" > $html
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --hide-scrollbars --allow-file-access-from-files \
  --window-size=$w,$h --screenshot=$out "file://$html" >/dev/null 2>&1
rm -rf $tmp; ls -la $out
