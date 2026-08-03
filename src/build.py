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
  index.html                         the portfolio index, from src/index.<theme>.html
  <case>/index.html                  each case study, in PRIMARY_THEME, so it is
                                     served at a clean /<case> URL
  case-studies/<case>/<theme>.html   body-only fragment of every case in every
                                     theme, for hosts that supply their own
                                     document shell

index.html sits at the repository root because that is what static hosts serve
at `/`. Keeping a page only at a nested path is what produces a 404 on the bare
domain.

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

PRIMARY_THEME = "minimal"

MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
        ".gif": "image/gif", ".webp": "image/webp", ".svg": "image/svg+xml"}


def build(template: pathlib.Path, theme: str, assets: pathlib.Path | None = None) -> str:
    theme_dir = THEMES / theme
    if not theme_dir.is_dir():
        raise SystemExit(f"{template.name}: no theme named {theme!r} in src/themes/")

    html = template.read_text(encoding="utf-8")
    for token, path in (("/*@FONTS@*/", theme_dir / "fonts.css"),
                        ("/*@THEME@*/", theme_dir / "theme.css")):
        if token not in html:
            raise SystemExit(f"{template.name}/{theme}: template is missing {token}")
        html = html.replace(token, path.read_text(encoding="utf-8"))

    # @IMG_NAME@ resolves to assets/img_name.<ext>
    for token in sorted(set(re.findall(r"@IMG_[A-Z0-9_]+@", html))):
        if assets is None or not assets.is_dir():
            raise SystemExit(f"{template.name}: {token} used but no assets/ directory")
        stem = "img_" + token[5:-1].lower()
        matches = [p for p in assets.iterdir() if p.stem == stem]
        if len(matches) != 1:
            raise SystemExit(f"{template.name}: {token} -> expected one {stem}.*, found {matches}")
        asset = matches[0]
        mime = MIME.get(asset.suffix.lower())
        if not mime:
            raise SystemExit(f"{template.name}: unsupported asset type {asset.name}")
        html = html.replace(token, f"data:{mime};base64,"
                            + base64.b64encode(asset.read_bytes()).decode())

    leftover = set(re.findall(r"@[A-Z0-9_]+@|/\*@\w+@\*/", html))
    if leftover:
        raise SystemExit(f"{template.name}/{theme}: unreplaced build tokens: {leftover}")
    return html


def wrap_document(fragment: str) -> str:
    """Wrap a body fragment in a document shell.

    The page's own <meta name="description"> is hoisted out of the fragment into
    <head>, so each template owns its description instead of the build guessing.
    """
    if not re.search(r"<title>.*?</title>", fragment, re.S):
        raise SystemExit("template must contain a <title>")
    skip = re.search(r'<a class="[\w-]*skip"', fragment)
    if not skip:
        raise SystemExit("template must open its body with a skip link")

    desc = ""
    m = re.search(r'^[ \t]*<meta name="description"[^>]*>\n?', fragment, re.M)
    if m:
        desc = m.group(0).strip() + "\n"
        fragment = fragment.replace(m.group(0), "", 1)

    head = (
        '<!doctype html>\n<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        + desc
        + '<meta name="color-scheme" content="light dark">\n'
    )
    body = fragment.replace(skip.group(0), "</head>\n<body>\n" + skip.group(0), 1)
    return head + body + "\n</body>\n</html>\n"


def main() -> None:
    written = []

    index_tpl = SRC / f"index.{PRIMARY_THEME}.html"
    if not index_tpl.is_file():
        raise SystemExit(f"missing portfolio index template {index_tpl.name}")
    (ROOT / "index.html").write_text(
        wrap_document(build(index_tpl, PRIMARY_THEME)), encoding="utf-8")
    written.append(ROOT / "index.html")

    case_dirs = sorted(d for d in CASES.iterdir() if d.is_dir())
    if not case_dirs:
        raise SystemExit("no cases found under src/cases/")

    for case_dir in case_dirs:
        themes = sorted(p.name.split(".")[1] for p in case_dir.glob("case.*.html"))
        if not themes:
            raise SystemExit(f"{case_dir.name}: no case.<theme>.html templates found")
        if PRIMARY_THEME not in themes:
            raise SystemExit(f"{case_dir.name}: no template for the primary theme "
                             f"{PRIMARY_THEME!r}; it would have no page at /{case_dir.name}")

        frag_dir = ROOT / "case-studies" / case_dir.name
        frag_dir.mkdir(parents=True, exist_ok=True)
        assets = case_dir / "assets"

        for theme in themes:
            fragment = build(case_dir / f"case.{theme}.html", theme, assets)
            (frag_dir / f"{theme}.html").write_text(fragment, encoding="utf-8")
            written.append(frag_dir / f"{theme}.html")
            if theme == PRIMARY_THEME:
                page_dir = ROOT / case_dir.name
                page_dir.mkdir(parents=True, exist_ok=True)
                (page_dir / "index.html").write_text(wrap_document(fragment), encoding="utf-8")
                written.append(page_dir / "index.html")

    for path in written:
        print(f"{path.relative_to(ROOT).as_posix():40} {path.stat().st_size / 1024:8.1f} KB")


if __name__ == "__main__":
    sys.exit(main())
