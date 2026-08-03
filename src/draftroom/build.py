#!/usr/bin/env python3
"""Build the Draftroom case study page.

Inlines the subsetted webfonts and the screenshots into a single file, so the
page renders identically anywhere it is dropped — no CDN, no asset directory,
no build step at serve time.

Outputs, both written to case-studies/draftroom/:
  index.html     standalone page; opens directly in a browser
  artifact.html  body-only fragment for hosts that supply their own document shell

Usage:  python3 src/draftroom/build.py
"""
import base64
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT = ROOT / "case-studies" / "draftroom"

IMAGES = {
    "@IMG_AUDIT@": "img_audit.jpg",
    "@IMG_RESEARCH@": "img_research.jpg",
    "@IMG_TABLE@": "img_table.jpg",
    "@IMG_WORKSPACE@": "img_workspace.jpg",
}

html = (HERE / "case.src.html").read_text(encoding="utf-8")
html = html.replace("/*@FONTS@*/", (HERE / "fonts.css").read_text(encoding="utf-8"))

for token, name in IMAGES.items():
    if token not in html:
        raise SystemExit(f"token {token} is missing from case.src.html")
    raw = (HERE / "assets" / name).read_bytes()
    html = html.replace(token, "data:image/jpeg;base64," + base64.b64encode(raw).decode())

leftover = set(re.findall(r"@[A-Z_]+@|/\*@\w+@\*/", html))
if leftover:
    raise SystemExit(f"unreplaced build tokens: {leftover}")

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "artifact.html").write_text(html, encoding="utf-8")

standalone = (
    '<!doctype html>\n<html lang="en">\n<head>\n'
    '<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    '<meta name="description" content="Case study: rewriting a B2B work-management '
    'product around how creative teams actually work.">\n'
    '<meta name="color-scheme" content="light dark">\n'
    + html.replace('<a class="skip"', '</head>\n<body>\n<a class="skip"', 1)
    + "\n</body>\n</html>\n"
)
(OUT / "index.html").write_text(standalone, encoding="utf-8")

for f in ("index.html", "artifact.html"):
    print(f"{f:16} {(OUT / f).stat().st_size / 1024:8.1f} KB")
