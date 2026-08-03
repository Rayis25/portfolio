# Portfolio

Case studies by **Muhammad Rayis**, Lead UX Designer.

| Case study | Live file | Source |
| --- | --- | --- |
| Draftroom — solving project management for creative teams | [`index.html`](index.html) | [`src/draftroom/`](src/draftroom/) |

## Deployment

The site is static — no framework, no install, no build step on the host. Vercel,
Netlify and GitHub Pages all serve it as-is from the repository root.

`index.html` is committed **at the root** because that is what a static host serves
at `/`. Keeping the page only at a nested path is what produces a 404 on the bare
domain. When a second case study lands, the root becomes an index that links to
each one, and the case studies move under `case-studies/`.

`vercel.json` sets `cleanUrls` and disables trailing slashes; it declares no build
command, which is what keeps the deployment a plain static upload.

## How a case study is built

Each case study is authored as one template plus its assets, and compiled into a
single self-contained HTML file. Fonts and images are inlined as data URIs, so a
built page renders identically from a local file, a static host, or an embed —
with no CDN, no asset paths, and no build step at serve time.

```
src/draftroom/
  case.src.html      markup, styles and behaviour; @TOKEN@ placeholders for assets
  fonts.css          @font-face rules with subsetted woff2 payloads inlined
  assets/*.jpg       screenshots, cropped and recompressed for the web
  build.py           inlines everything and writes both outputs
```

Rebuild after editing the template or swapping an asset:

```sh
python3 src/draftroom/build.py
```

It writes two files:

- **`index.html`** (repo root) — a complete document. Open it in a browser, or let a
  static host serve it at `/`.
- **`case-studies/draftroom/artifact.html`** — the same page without
  `<!doctype>`/`<html>`/`<head>`/`<body>`, for hosts that supply their own document
  shell. This path is stable; the published artifact tracks it.

Both are committed, so the case study is viewable straight from the repo without
running anything.

## Design notes

The page is set as a **proof sheet**, taking its vernacular from the drafting room
the product is named after: a narrow reading measure, a monospaced margin rail
carrying editor's marks, and a single correction red reserved for the moments where
old vocabulary is struck out and replaced. Section markers reuse the product's own
shipped status language — Brief, Audit, Insight, Reframe, Revision, Final,
Delivered — rather than generic numbering.

- **Type** — Newsreader (display and pull quotes), Archivo (body), IBM Plex Mono
  (margin marks, labels, data). All three are subsetted to the glyphs the page
  actually uses, which keeps the inlined faces around 100 KB total.
- **Colour** — a drafting-paper grey-green ground with blue-biased ink, plus two
  semantic accents: redline for corrections, stamp green for approvals and outcomes.
- **Themes** — light and dark are both first-class. The palette is defined as custom
  properties and redefined under `prefers-color-scheme` and an explicit
  `data-theme` attribute, so a host-level theme toggle wins in either direction.
- **Motion** — two moments only: the hero strike-through, and a staggered reveal on
  the vocabulary rows. Both collapse to their final state under
  `prefers-reduced-motion: reduce`.

Fonts are licensed under the SIL Open Font License 1.1 (Newsreader, Archivo,
IBM Plex Mono), which permits embedding.
