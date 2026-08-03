#!/usr/bin/env python3
"""Build every case study, in every theme it has been written for.

A case is a directory under src/cases/ holding an `assets/` folder and one or
more `case.<theme>.html` templates. Each template names the theme it is written
against; the theme supplies the tokens, primitives and webfaces from
src/themes/<theme>/. The build inlines the theme CSS, the subsetted fonts, and
every image referenced by an @IMG_*@ token, producing files with no external
requests at all — nothing to break when a page is moved or served from a
different host.

Outputs:
  case-studies/<case>/<theme>.html   body-only fragment, for hosts that supply
                                     their own document shell
  index.html                         full document, built from PRIMARY_CASE in
                                     PRIMARY_THEME

The primary page is written to the repository root because that is what static
hosts serve at `/`. Keeping it only at a nested path is what produces a 404 on
the bare domain.

Usage:  python3 src/build.py
"""
import base64
import pathlib
import re
import sys

SRC = pathlib.Path(__file__).resolve().parent
ROOT = SRC.parent
THEMES = SRC / "themes"
CASES = SRC / "cases"

PRIMARY_CASE = "draftroom"
PRIMARY_THEME = "minimal"

MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
        ".gif": "image/gif", ".webp": "image/webp", ".svg": "image/svg+xml"}


def build(case_dir: pathlib.Path, theme: str) -> str:
    theme_dir = THEMES / theme
    if not theme_dir.is_dir():
        raise SystemExit(f"{case_dir.name}: no theme named {theme!r} in src/themes/")

    html = (case_dir / f"case.{theme}.html").read_text(encoding="utf-8")
    for token, path in (("/*@FONTS@*/", theme_dir / "fonts.css"),
                        ("/*@THEME@*/", theme_dir / "theme.css")):
        if token not in html:
            raise SystemExit(f"{case_dir.name}/{theme}: template is missing {token}")
        html = html.replace(token, path.read_text(encoding="utf-8"))

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
        html = html.replace(token, f"data:{mime};base64,"
                            + base64.b64encode(asset.read_bytes()).decode())

    leftover = set(re.findall(r"@[A-Z0-9_]+@|/\*@\w+@\*/", html))
    if leftover:
        raise SystemExit(f"{case_dir.name}/{theme}: unreplaced build tokens: {leftover}")
    return html


def wrap_document(fragment: str) -> str:
    if not re.search(r"<title>.*?</title>", fragment, re.S):
        raise SystemExit("template must contain a <title>")
    skip = re.search(r'<a class="[\w-]*skip"', fragment)
    if not skip:
        raise SystemExit("template must open its body with a skip link")
    head = (
        '<!doctype html>\n<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<meta name="description" content="Case study: rewriting a B2B work-management '
        'product around how creative teams actually work.">\n'
        '<meta name="color-scheme" content="light dark">\n'
    )
    body = fragment.replace(skip.group(0), "</head>\n<body>\n" + skip.group(0), 1)
    return head + body + "\n</body>\n</html>\n"


def main() -> None:
    case_dirs = sorted(d for d in CASES.iterdir() if d.is_dir())
    written = []
    primary_seen = False

    for case_dir in case_dirs:
        themes = sorted(p.name.split(".")[1] for p in case_dir.glob("case.*.html"))
        if not themes:
            raise SystemExit(f"{case_dir.name}: no case.<theme>.html templates found")
        out = ROOT / "case-studies" / case_dir.name
        out.mkdir(parents=True, exist_ok=True)

        for theme in themes:
            fragment = build(case_dir, theme)
            (out / f"{theme}.html").write_text(fragment, encoding="utf-8")
            written.append(out / f"{theme}.html")
            if case_dir.name == PRIMARY_CASE and theme == PRIMARY_THEME:
                (ROOT / "index.html").write_text(wrap_document(fragment), encoding="utf-8")
                written.append(ROOT / "index.html")
                primary_seen = True

    if not primary_seen:
        raise SystemExit(f"primary {PRIMARY_CASE}/{PRIMARY_THEME} was never built")

    for path in written:
        print(f"{path.relative_to(ROOT).as_posix():38} {path.stat().st_size / 1024:8.1f} KB")


if __name__ == "__main__":
    sys.exit(main())
