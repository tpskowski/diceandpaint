import { glob } from "astro/loaders";
import { defineCollection, z } from "astro:content";

const pages = defineCollection({
  loader: glob({
    pattern: "**/*.{md,mdx}",
    base: "./src/content/pages",
  }),
  schema: z.object({
    title: z.string(),
    summary: z.string(),
    order: z.number().default(100),
    hidden: z.boolean().default(false),
    route: z.string().optional(),
  }),
});

const posts = defineCollection({
  loader: glob({
    pattern: "**/*.{md,mdx}",
    base: "./src/content/posts",
  }),
  schema: z.object({
    title: z.string(),
    summary: z.string(),
    publishDate: z.coerce.date(),
    category: z.string(),
    tags: z.array(z.string()).default([]),
    thumbnail: z.string(),
    thumbnailAlt: z.string(),
    hideHero: z.boolean().default(false),
    draft: z.boolean().default(false),
  }),
});

export const collections = {
  pages,
  posts,
};
