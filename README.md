# diceandpaint

Astro-based static site for the migrated Dice & Paint archive.

## Stack

- Astro for routing, layouts, and static output
- Markdown/MDX content collections for posts and pages
- Plain CSS in `src/styles/global.css`
- Grafana Faro client instrumentation via `src/scripts/faro.ts`

## Content model

- `src/content/posts/` holds blog posts for the homepage feed and `/posts/[slug]/` routes.
- `src/content/pages/` holds non-blog site content, organized by top-level nav category.
- `src/content/pages/guides/` maps to `/guides/`.
- `src/content/pages/reviews/` maps to `/reviews/`.
- `src/content/pages/model-gallery/` maps to `/model-gallery/`.
- `src/content/pages/homebrew-rules/` maps to `/homebrew-rules/`.
- `src/content/pages/unlisted/` holds routable pages that should not appear in nav or the library page.
- `src/content/pages/unlisted/markdown-examples.md` is the markdown rendering reference page at `/unlisted/markdown-examples/`.

## Routing

- `/` renders the post feed from `src/pages/index.astro`.
- `/posts/[slug]/` renders blog posts from `src/pages/posts/[slug].astro`.
- `src/pages/[...slug].astro` renders all standalone page content from `src/content/pages/`, including nested folder indexes.
- `/library/` lists non-hidden standalone pages.

## Key files

- `src/data/navigation.ts` controls the top navigation groups and links.
- `src/components/SiteHeader.astro` renders the header and dropdown menus.
- `src/components/TableOfContents.astro` renders the left TOC rail on non-home pages.
- `src/layouts/BaseLayout.astro` is the shared shell and loads Faro.
- `src/layouts/PageLayout.astro` is the shared standalone-page layout.
- `src/content.config.ts` defines the content schemas.

## Project structure

```text
.
|-- public/
|-- scripts/
|-- src/
|   |-- components/
|   |-- content/
|   |   |-- pages/
|   |   |   |-- guides/
|   |   |   |-- homebrew-rules/
|   |   |   |-- model-gallery/
|   |   |   |-- reviews/
|   |   |   `-- unlisted/
|   |   `-- posts/
|   |-- data/
|   |-- layouts/
|   |-- pages/
|   |   |-- posts/
|   |   |   `-- [slug].astro
|   |   |-- [...slug].astro
|   |   |-- index.astro
|   |   `-- library.astro
|   |-- scripts/
|   |-- styles/
|   `-- content.config.ts
|-- working/
|-- astro.config.mjs
|-- package.json
`-- tsconfig.json
```

## Local development

```powershell
cmd /c npm install
cmd /c npm run dev
```

Optional local env:

- copy `.env.example` to `.env.local`
- set Grafana Faro values there if you want local telemetry

## Build

```powershell
cmd /c npm run build
```

The production output is written to `dist/`.

## Licensing

This repository uses a split licensing model:

- code, configuration, and build/tooling files: MIT, see `LICENSE`
- original editorial text: CC BY 4.0, see `CONTENT_LICENSE.md`
- images and other media: not automatically CC-licensed; they remain with their respective copyright holders unless explicitly noted otherwise

Third-party runtime dependency notices are summarized in `THIRD_PARTY_NOTICES.md`.
