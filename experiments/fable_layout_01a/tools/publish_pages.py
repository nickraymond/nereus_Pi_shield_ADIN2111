#!/usr/bin/env python3
"""Package the design review for publishing as one artifact (read only): out/publish/index.html = the review page without the
document skeleton (the artifact host adds its own), before_after.html with its skeleton, and the list of supporting files.
  python3 tools/publish_pages.py            → out/publish/{index.html, before_after.html}, out/publish/files.json
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "out" / "publish"
OUT.mkdir(parents=True, exist_ok=True)
rv = (HERE / "out" / "review" / "index.html").read_text()
body = re.sub(r"^<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>", "", rv)
body = body.replace("</head><body>", "", 1).replace("</body></html>", "", 1)
(OUT / "index.html").write_text(body)
(OUT / "before_after.html").write_text((HERE / "out" / "before_after" / "index.html").read_text())
files = {}
for p in sorted((HERE / "out" / "review").glob("*.svg")):
    files[p.name] = str(p.relative_to(HERE))
for p in sorted((HERE / "out" / "before_after").glob("*.svg")):
    files[p.name] = str(p.relative_to(HERE))
for sub in ("before", "after"):
    for p in sorted((HERE / "out" / "before_after" / sub).glob("*.svg")):
        files[f"{sub}/{p.name}"] = str(p.relative_to(HERE))
json.dump(files, open(OUT / "files.json", "w"), indent=1)
print(len(files), "files;", len(body) // 1024, "KB index")
