#!/usr/bin/env python3
"""Build every case study into a self-contained page.

A case is a directory under src/cases/ holding `case.html` plus an `assets/`
folder. The build inlines the shared theme, the subsetted webfonts, and each
image referenced by an @IMG_*@ token, producing files with no external requests
at all — no CDN, no asset paths, nothing to break when the page is moved.

Outputs per case:
  case-studies/<name>/artifact.html   body-only fragment, for hosts that supply
                                      their own document shell
  index.html                          full document, for the case marked PRIMARY

The primary case is written to the repository root because that is what static
hosts serve at `/`. Keeping the page only at a nested path is what produces a
404 on the bare domain.

Usage:  python3 src/build.py
"""
import base64
import pathlib
import re
import sys

SRC = pathlib.Path(__file__).resolve().parent
ROOT = SRC.parent
THEME = SRC / "theme"
CASES = SRC / "cases"

PRIMARY = "draftroom"

MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
        ".gif": "image/gif", ".webp": "image/webp", ".svg": "image/svg+xml"}


def build(case_dir: pathlib.Path) -> str:
    html = (case_dir / "case.html").read_text(encoding="utf-8")
    html = html.replace("/*@FONTS@*/", (THEME / "fonts.css").read_text(encoding="utf-8"))
    html = html.replace("/*@THEME@*/", (THEME / "theme.css").read_text(encoding="utf-8"))

    # @IMG_NAME@ resolves to assets/img_name.<ext>
    for token in sorted(set(re.findall(r"@IMG_[A-Z0-9_]+@", html))):
        stem = "img_" + token[5:-1].lower()
        matches = [p for p in (case_dir / "assets").iterdir() if p.stem == stem]
        if len(matches) != 1:
            raise SystemExit(f"{case_dir.name}: {token} -> expected one {stem}.*, found {matches}")
        asset = matches[0]
        mime = MIME.get(asset.suffix.lower())
        if not mime:
            raise SystemExit(f"{case_dir.name}: unsupported asset type {asset.name}")
        data = base64.b64encode(asset.read_bytes()).decode()
        html = html.replace(token, f"data:{mime};base64,{data}")

    leftover = set(re.findall(r"@[A-Z0-9_]+@|/\*@\w+@\*/", html))
    if leftover:
        raise SystemExit(f"{case_dir.name}: unreplaced build tokens: {leftover}")
    return html


def wrap_document(fragment: str) -> str:
    title = re.search(r"<title>(.*?)</title>", fragment, re.S)
    if not title:
        raise SystemExit("case.html must contain a <title>")
    head = (
        '<!doctype html>\n<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<meta name="description" content="Case study: rewriting a B2B work-management '
        'product around how creative teams actually work.">\n'
        '<meta name="color-scheme" content="light dark">\n'
    )
    body = fragment.replace('<a class="t-skip"', '</head>\n<body>\n<a class="t-skip"', 1)
    if "</head>" not in body:
        raise SystemExit("case.html must contain the skip link that opens <body>")
    return head + body + "\n</body>\n</html>\n"


def main() -> None:
    case_dirs = sorted(d for d in CASES.iterdir() if (d / "case.html").is_file())
    if not case_dirs:
        raise SystemExit("no cases found under src/cases/")
    if PRIMARY not in {d.name for d in case_dirs}:
        raise SystemExit(f"PRIMARY case {PRIMARY!r} not found")

    written = []
    for case_dir in case_dirs:
        fragment = build(case_dir)
        out = ROOT / "case-studies" / case_dir.name
        out.mkdir(parents=True, exist_ok=True)
        (out / "artifact.html").write_text(fragment, encoding="utf-8")
        written.append(out / "artifact.html")
        if case_dir.name == PRIMARY:
            (ROOT / "index.html").write_text(wrap_document(fragment), encoding="utf-8")
            written.append(ROOT / "index.html")

    for path in written:
        print(f"{path.relative_to(ROOT).as_posix():38} {path.stat().st_size / 1024:8.1f} KB")


if __name__ == "__main__":
    sys.exit(main())
