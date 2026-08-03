# Portfolio

Case studies by **Muhammad Rayis**, Lead UX Designer.

| Case study | Live file | Source |
| --- | --- | --- |
| Draftroom — solving project management for creative teams | [`index.html`](index.html) | [`src/cases/draftroom/`](src/cases/draftroom/) |

## Structure

```
src/
  theme/
    theme.css        design tokens + primitives, shared by every case
    fonts.css        @font-face rules with subsetted woff2 payloads inlined
  cases/
    draftroom/
      case.html      markup + case-specific CSS; @IMG_*@ tokens for assets
      assets/        screenshots, cropped and recompressed for the web
  build.py           inlines theme, fonts and images into standalone pages
```

Build after editing a template, the theme, or an asset:

```sh
python3 src/build.py
```

It writes, for every case under `src/cases/`:

- **`case-studies/<name>/artifact.html`** — the page without
  `<!doctype>`/`<html>`/`<head>`/`<body>`, for hosts that supply their own
  document shell. These paths are stable; published artifacts track them.
- **`index.html`** (repo root) — a complete document, for the case named by
  `PRIMARY` in `build.py`.

Both are committed, so a case study is viewable straight from the repo without
running anything.

### Adding a case study

Create `src/cases/<name>/case.html` with an `assets/` folder beside it, build
with the theme's `t-` classes, and reference images as `@IMG_FOO@` (which
resolves to `assets/img_foo.*`). Run the build. Nothing else needs changing
unless the new case should become `PRIMARY`.

## Deployment

The site is static — no framework, no install, no build step on the host.
Vercel, Netlify and GitHub Pages all serve it as-is from the repository root.
`vercel.json` sets `cleanUrls` and declares no build command, which keeps the
deployment a plain static upload.

`index.html` lives **at the root** because that is what a static host serves at
`/`. Keeping the page only at a nested path is what produces a 404 on the bare
domain.

## Design notes

The theme is **neo-brutalist**: hard 2px rules, flat unmodulated colour, offset
shadows, and no gradients, radii or soft edges anywhere. Its one idea is
**markup** — the case study is a document that has been attacked with a red pen
and a highlighter. Retired vocabulary is struck through in red; its replacement
is swept in yellow. That is the argument of the work, performed rather than
described.

- **Colour** — bone `#E8E4D8` ground, `#111` ink, and two accents that carry
  meaning rather than decoration: `#FF3B00` for corrections and failures,
  `#FFE000` for replacements and emphasis. Nothing else is coloured.
- **Type** — Bricolage Grotesque 800 for display (uppercase, tight), Archivo for
  reading text, JetBrains Mono for labels, data and captions. All three are
  subsetted to the glyphs the pages actually use — about 67 KB of woff2 total.
- **Structure** — every section opens with an inverted bar carrying its stage
  name and index. The stages reuse the product's own shipped status language
  (Brief, Audit, Insight, Reframe, Revision, Final, Delivered) rather than
  generic numbering, so the structure encodes something true about the work.
- **Themes** — light and dark are both first-class. The palette is defined as
  custom properties and redefined under `prefers-color-scheme` and an explicit
  `data-theme` attribute, so a host-level toggle wins in either direction. Ink
  and paper swap, which inverts the bars rather than washing them out.
- **Motion** — two moments, both stepped rather than eased so they read as
  mechanical: the hero strike-through and highlighter sweep, and a staggered
  reveal down the vocabulary table. Both collapse to their final state under
  `prefers-reduced-motion: reduce`.

Layout is verified free of horizontal overflow from 320px to 1920px.

Fonts are licensed under the SIL Open Font License 1.1 (Bricolage Grotesque,
Archivo, JetBrains Mono), which permits embedding.
