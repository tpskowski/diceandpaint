# Repository Instructions

## Project Scope
- This repository is an Astro static website.
- Blog posts live in markdown or MDX under `src/content/posts`.
- Standalone site pages and category landing pages live in `src/content/pages`.
- Keep the final output statically deployable unless the user explicitly asks for server behavior.

## Current Structure
- `src/content/posts/` holds the homepage feed content.
- `src/content/pages/` holds standalone pages, grouped by top-level site category.
- `src/content/pages/guides/` maps to the `Guides` section.
- `src/content/pages/reviews/` maps to the `Reviews` section.
- `src/content/pages/model-gallery/` maps to the `Model Gallery` section.
- `src/content/pages/homebrew-rules/` maps to the `Homebrew Rules` section.
- `src/content/pages/unlisted/` holds routable pages that should stay out of nav and library listings.
- `src/pages/index.astro` renders the blog feed landing page.
- `src/pages/posts/[slug].astro` renders individual posts.
- `src/pages/[...slug].astro` renders standalone pages and nested folder indexes.
- `src/pages/library.astro` lists site pages.
- `src/data/navigation.ts` defines the mixed internal/external navigation model.
- `src/layouts/` holds Astro layouts.
- `src/components/` holds reusable Astro components.
- `src/components/TableOfContents.astro` renders the left TOC rail for non-home pages.
- `src/styles/global.css` holds the shared site styling.
- `src/scripts/faro.ts` initializes Grafana Faro in the browser.
- `public/` holds static assets.

## Working Rules
- Preserve the markdown-first content model by default.
- Use `.md` for simple editorial content and `.mdx` only when embedded components are necessary.
- Add or extend collection schema fields in `src/content.config.ts` when metadata requirements change.
- Before pushing or building, check any new file under `src/content/pages` including drafts for required schema frontmatter, especially `title` and `summary`.
- Keep the homepage post-first: linked thumbnails and post metadata, not long article text dumps.
- Maintain navigation as data in `src/data/navigation.ts` so category growth and off-site links stay manageable.
- Keep non-blog pages organized under the folder that matches the top-level nav category whenever possible.
- Put routable but intentionally unlisted pages under `src/content/pages/unlisted/`.
- Keep dependencies focused; do not add frontend libraries unless they solve a concrete problem.

## Frontend Tasks
- Avoid generic, overbuilt layouts.
- One composition: The first viewport must read as one composition, not a dashboard unless the page is actually a dashboard.
- Brand first: On branded pages, the brand or product name must be a hero-level signal, not just nav text or an eyebrow. No headline should overpower the brand.
- Brand test: If the first viewport could belong to another brand after removing the nav, the branding is too weak.
- Typography: Use expressive, purposeful fonts and avoid default stacks such as Inter, Roboto, Arial, or system defaults.
- Background: Do not rely on flat, single-color backgrounds. Use gradients, images, or subtle patterns to build atmosphere.
- Full-bleed hero only: On landing pages and promotional surfaces, the hero image should be a dominant edge-to-edge visual plane or background by default. Do not use inset hero images, side-panel hero images, rounded media cards, tiled collages, or floating image blocks unless the existing design system clearly requires it.
- Hero budget: The first viewport should usually contain only the brand, one headline, one short supporting sentence, one CTA group, and one dominant image. Do not place stats, schedules, event listings, address blocks, promos, this-week callouts, metadata rows, or secondary marketing content in the first viewport.
- No hero overlays: Do not place detached labels, floating badges, promo stickers, info chips, or callout boxes on top of hero media.
- Cards: Default to no cards. Never use cards in the hero. Cards are allowed only when they are the container for a user interaction. If removing a border, shadow, background, or radius does not hurt interaction or understanding, it should not be a card.
- One job per section: Each section should have one purpose, one headline, and usually one short supporting sentence.
- Real visual anchor: Imagery should show the product, place, atmosphere, or context. Decorative gradients and abstract backgrounds do not count as the main visual idea.
- Reduce clutter: Avoid pill clusters, stat strips, icon rows, boxed promos, schedule snippets, and multiple competing text blocks.
- Use motion to create presence and hierarchy, not noise. Ship at least 2-3 intentional motions for visually led work.
- Color and look: Choose a clear visual direction, define CSS variables, avoid purple-on-white defaults, and avoid purple bias or dark mode bias.
- Ensure the page loads properly on both desktop and mobile.
- For React code, prefer modern patterns including `useEffectEvent`, `startTransition`, and `useDeferredValue` when appropriate if used by the team. Do not add `useMemo` or `useCallback` by default unless already used. Follow the repo's React Compiler guidance.
- Exception: If working within an existing website or design system, preserve the established patterns, structure, and visual language.

## Documentation
- Update `README.md` when collections, routes, or workflow expectations change.
- Keep setup steps short and accurate.
