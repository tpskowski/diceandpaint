import rss from "@astrojs/rss";
import type { APIContext } from "astro";
import { getCollection } from "astro:content";

const FALLBACK_SITE = "https://www.diceandpaint.net";

export async function buildRssFeed(context: Pick<APIContext, "site">) {
  const site = context.site ?? new URL(FALLBACK_SITE);
  const selfUrl = new URL("/rss.xml", site).toString();
  const posts = (await getCollection("posts", ({ data }) => !data.draft)).sort(
    (a, b) => b.data.publishDate.getTime() - a.data.publishDate.getTime(),
  );

  return rss({
    title: "Dice & Paint",
    description: "Dice & Paint is a post-first tabletop journal for reviews, model galleries, guides, and rules notes.",
    site,
    xmlns: {
      atom: "http://www.w3.org/2005/Atom",
    },
    customData: `<language>en-us</language><atom:link href="${selfUrl}" rel="self" type="application/rss+xml" />`,
    items: posts.map((post) => ({
      title: post.data.title,
      description: post.data.summary,
      pubDate: post.data.publishDate,
      link: `/posts/${post.id}/`,
      categories: Array.from(new Set([post.data.category, ...post.data.tags])),
    })),
  });
}
