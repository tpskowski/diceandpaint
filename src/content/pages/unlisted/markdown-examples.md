---
title: Markdown Examples
summary: Reference page showing how common markdown patterns render in the site styles.
order: 999
hidden: true
---

This page exists as a rendering reference for site content. It is intentionally unlisted.

# Heading Level 1

This body `h1` verifies first-level markdown headings inside page content.

## Heading Level 2

This body `h2` verifies second-level markdown headings inside page content.

### Heading Level 3

This body `h3` verifies third-level markdown headings inside page content.

#### Heading Level 4

This body `h4` verifies fourth-level markdown headings inside page content.

## Paragraphs and emphasis

Markdown supports plain paragraphs, **bold text**, *italic text*, ***bold italic text***, ~~strikethrough~~, and `inline code`.

You can also include a [standard link](https://www.diceandpaint.net/) inside a sentence.

## Blockquotes

> Paint guides, battle reports, and reviews often need a pull quote or a rules reminder.
>
> Blockquotes can span multiple paragraphs and preserve visual separation from body copy.

## Lists

### Unordered

- Acrylic paints
- Drybrushes
- Texture paste
- Varnish

### Ordered

1. Prime the model.
2. Block in the base colors.
3. Shade recesses.
4. Add highlights.

### Task list

- [x] Migrate the first post
- [x] Add a table of contents
- [ ] Final cleanup pass

## Horizontal rule

---

## Code

Inline code works for short references like `src/content/posts`.

```md
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
```

```js
const paintScheme = {
  primary: "#324F50",
  highlight: "#7FF5FA",
};
```

## Table

| Format | Example | Notes |
| --- | --- | --- |
| Bold | `**text**` | Strong emphasis |
| Italic | `*text*` | Light emphasis |
| Code | `` `text` `` | Inline references |

## Image

![Example miniature terrain image](/pages/toxicrivers/65ddfb5c1e9e.webp)

Images render inline and can be followed by normal body text.

## Mixed content

Sometimes a section needs a short list followed by a quote and a link.

- Fast to scan
- Easy to maintain
- Works well in markdown-first workflows

> Use markdown for editorial structure, then move to MDX only when a component is genuinely necessary.

See the [Old World Meta Watch](/posts/old-world-meta-watch-triple-gts/) post for a live content example.
