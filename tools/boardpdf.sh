#!/usr/bin/env bash
# Board drawings of the JLC board as one PDF: docs/design-review/board.pdf (9 pages, A4, scale 1 : 1, vector).
# Reads the board; never modifies it. macOS only (the pages are joined with PDFKit, tools/pdfmerge.js).
#   1 index · 2 top view · 3 bottom view, mirrored = as seen from below · 4-9 the six copper layers, seen from the top
# kicad-cli plots at 1 : 1 only here: with --scale other than 1 the board lands off the page (tried 2026-11-12).
set -euo pipefail
cd "$(dirname "$0")/.."

K="${KICAD_CLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}"
PROJ=Nereus_Pi_Shield_Adin2111
PCB="$PROJ/$PROJ.kicad_pcb"
OUT="${1:-docs/design-review/board.pdf}"
case "$OUT" in /*) ABS="$OUT" ;; *) ABS="$PWD/$OUT" ;; esac
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT

[ -x "$K" ] || { echo "boardpdf: kicad-cli not found at $K (set KICAD_CLI)" >&2; exit 2; }
[ -f "$PCB" ] || { echo "boardpdf: board not found: $PCB" >&2; exit 2; }

"$K" pcb export pdf --mode-single --include-border-title -l F.SilkS,F.Mask,Edge.Cuts -o "$T/2_top.pdf" "$PCB" >/dev/null
"$K" pcb export pdf --mode-single --include-border-title --mirror -l B.SilkS,B.Mask,Edge.Cuts -o "$T/3_bottom.pdf" "$PCB" >/dev/null
"$K" pcb export pdf --mode-multipage --include-border-title -l F.Cu,In1.Cu,In2.Cu,In3.Cu,In4.Cu,B.Cu --common-layers Edge.Cuts \
  -o "$T/4_copper.pdf" "$PCB" >/dev/null

cat > "$T/index.html" <<HTML
<html><head><meta charset='utf-8'><style>body{font-family:Helvetica;font-size:11pt} h2{font-size:16pt} td,th{font-size:11pt}</style></head><body>
<h2>$PROJ: board drawings</h2>
<p>Plotted by kicad-cli from <tt>$PCB</tt> at commit $(git rev-parse --short HEAD), $(date +%Y-%m-%d).
Scale 1 : 1 on A4 (outline 65.00 x 56.00 mm); the pages are vector drawings, zoom in to read them.
The layout is frozen (tag s9-layout-freeze, 2026-11-11).</p>
<table border='1' cellspacing='0' cellpadding='5' style='border-collapse:collapse'>
<tr><th align='left'>Page</th><th align='left'>Drawing</th><th align='left'>Board layers</th></tr>
<tr><td>2</td><td>Top view</td><td>top silkscreen, top solder-mask openings (pads), outline</td></tr>
<tr><td>3</td><td>Bottom view, mirrored: as seen from below</td><td>bottom silkscreen, bottom solder-mask openings, outline</td></tr>
<tr><td>4</td><td>Copper layer 1, seen from the top</td><td>Top Layer (F.Cu)</td></tr>
<tr><td>5</td><td>Copper layer 2, seen from the top</td><td>Internal 1 (In1.Cu)</td></tr>
<tr><td>6</td><td>Copper layer 3, seen from the top</td><td>GND Plane (In2.Cu)</td></tr>
<tr><td>7</td><td>Copper layer 4, seen from the top</td><td>Internal 2 (In3.Cu)</td></tr>
<tr><td>8</td><td>Copper layer 5, seen from the top</td><td>PWR Plane (In4.Cu)</td></tr>
<tr><td>9</td><td>Copper layer 6, seen from the top</td><td>Bottom Layer (B.Cu)</td></tr>
</table>
<p>Regenerate: <tt>tools/boardpdf.sh</tt></p></body></html>
HTML
osascript -l JavaScript tools/html2pdf.js "$T/index.html" "$T/1_index.pdf" landscape >/dev/null
n=$(osascript -l JavaScript tools/pdfmerge.js "$ABS" "$T/1_index.pdf" "$T/2_top.pdf" "$T/3_bottom.pdf" "$T/4_copper.pdf")
[ "$n" = "9 pages" ] || { echo "boardpdf: expected 9 pages, got '$n'" >&2; exit 1; }
echo "boardpdf: $n → $OUT ($(( $(wc -c < "$OUT") / 1024 )) KB)"
