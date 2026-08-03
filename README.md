# Portfolio

Case studies by **Muhammad Rayis**, Product & UX Design.

| Page | Live file | Source |
| --- | --- | --- |
| Index | [`index.html`](index.html) | [`src/index.minimal.html`](src/index.minimal.html) |
| Draftroom — solving project management for creative teams | [`draftroom/index.html`](draftroom/index.html) | [`src/cases/draftroom/`](src/cases/draftroom/) |
| Wall — product strategy for a hyper-local social app | [`wall/index.html`](wall/index.html) | [`src/cases/wall/`](src/cases/wall/) |
| Reelify — UX and microcopy audit for a Shopify shoppable-video app | [`reelify/index.html`](reelify/index.html) | [`src/cases/reelify/`](src/cases/reelify/) |

Two themes are maintained. `minimal` is live; `marked` is kept buildable so the
directions can be compared rather than remembered.

## Structure

```
src/
  themes/
    minimal/         near-white, soft-cornered, quiet — the live direction
      theme.css      design tokens + primitives
      fonts.css      @font-face rules with subsetted woff2 payloads inlined
    marked/          neo-brutalist alternate
      theme.css
      fonts.css
  cases/
    draftroom/
      case.minimal.html   markup + case CSS for the minimal theme
      case.marked.html    the same case written against the marked theme
      assets/             screenshots, cropped and recompressed for the web
    wall/
      case.minimal.html   strategy case study; no screenshots, so its visuals
                          are built in markup
  index.minimal.html      the portfolio index
  build.py                inlines theme, fonts and images into standalone pages
```

A template is named `case.<theme>.html` and is written against that theme's
primitives. Themes are not interchangeable at runtime — each case carries one
template per theme it supports.

Build after editing a template, the theme, or an asset:

```sh
python3 src/build.py
```

It writes:

- **`index.html`** (repo root) — the portfolio index, from
  `src/index.<theme>.html`.
- **`<case>/index.html`** — each case study in `PRIMARY_THEME`, so it is served
  at a clean `/<case>` URL.
- **`case-studies/<case>/<theme>.html`** — a body-only fragment of every case in
  every theme, without `<!doctype>`/`<html>`/`<head>`/`<body>`, for hosts that
  supply their own document shell. These paths are stable; published artifacts
  track them.

Each template carries its own `<meta name="description">` directly after its
`<title>`; the build hoists it into `<head>` rather than guessing one.

Both are committed, so a case study is viewable straight from the repo without
running anything.

### Adding a case study

Create `src/cases/<name>/case.<theme>.html`, build with that theme's prefixed
classes (`m-` for minimal, `t-` for marked), and run the build — the case is
discovered automatically and published at `/<name>`. Add an `assets/` folder
beside the template if it has images and reference them as `@IMG_FOO@`, which
resolves to `assets/img_foo.*`; a case with no images needs no assets folder.
Then add a card for it in `src/index.minimal.html`.

Every case must have a template for `PRIMARY_THEME` — the build refuses
otherwise, since the case would have no page at its own URL.

## Deployment

The site is static — no framework, no install, no build step on the host.
Vercel, Netlify and GitHub Pages all serve it as-is from the repository root.
`vercel.json` sets `cleanUrls` and declares no build command, which keeps the
deployment a plain static upload.

`index.html` lives **at the root** because that is what a static host serves at
`/`. Keeping the page only at a nested path is what produces a 404 on the bare
domain.

## Design notes

### `minimal` — the live theme

Near-white ground, imagery floating in soft grey wells, monospaced micro-labels
in outlined chips, and one violet accent. Quiet by default: colour and weight are
spent only where the content needs emphasis, so the writing carries the page.

- **Colour** — `#FFFFFF` ground with `#F4F3F1` wells, deliberately warm-neutral so
  they read as paper rather than screen. Ink `#191818`, muted `#9A9791`, and a
  single accent `#6E4FF6` reserved for the thesis, links and live states.
- **Type** — Plus Jakarta Sans for everything readable, Roboto Mono for labels,
  tags and captions. Subsetted to the glyphs actually used: about 35 KB of woff2.
- **Structure** — sections open with a bare mono label (About, Problem, Research,
  Approach, Outcome). Shipped features use a three-up grid of well → statement →
  tag; where subgrid is available those three bands share rows across columns, so
  the wells come out identical rather than each sizing to its own contents.
- **Motion** — none. At this weight, movement would read as decoration.

### `marked` — the alternate

Neo-brutalist: hard 2px rules, flat unmodulated colour, offset shadows, no
gradients or radii. Its idea is **markup** — a document attacked with a red pen
and a highlighter, where retired vocabulary is struck through in red and its
replacement swept in yellow. Bone `#E8E4D8` ground, `#FF3B00` corrections,
`#FFE000` replacements; Bricolage Grotesque 800 uppercase over Archivo and
JetBrains Mono (~67 KB). Sections open with an inverted bar carrying a stage name
drawn from the product's own shipped status language. Two stepped motion moments,
both collapsing under `prefers-reduced-motion: reduce`.

### Both themes

Light and dark are first-class in each. Palettes are defined as custom properties
and redefined under `prefers-color-scheme` and an explicit `data-theme`
attribute, so a host-level toggle wins in either direction — dark is a considered
translation, not an inversion.

Layout is verified free of horizontal overflow from 320px to 1920px, in both
themes.

Fonts are licensed under the SIL Open Font License 1.1 (Plus Jakarta Sans,
Roboto Mono, Bricolage Grotesque, Archivo, JetBrains Mono), which permits
embedding.
