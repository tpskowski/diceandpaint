# Scrape Organization

This directory reorganizes the raw scrape into migration buckets without changing the Astro site.

## Buckets

- `posts/`: 16 blog posts
- `standalone-pages/`: 17 home and page-style entries
- `taxonomy/`: 57 blog category and tag pages
- `utility/`: 1 utility pages

## Files

- `manifest.json` at this level contains all entries with their organized destinations.
- Each bucket also has its own `manifest.json`.
- Images are copied into the same bucket under an `images/` subtree.
