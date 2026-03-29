import rss from "@astrojs/rss";
import { getCollection } from "astro:content";

export async function GET(context) {
  const posts = (await getCollection("posts", ({ data }) => !data.draft)).sort(
    (a, b) => b.data.publishDate.getTime() - a.data.publishDate.getTime(),
  );

  return rss({
    title: "Dice & Paint",
    description: "Dice & Paint is a post-first tabletop journal for reviews, model galleries, guides, and rules notes.",
    site: context.site ?? "https://www.diceandpaint.net",
    items: posts.map((post) => ({
      title: post.data.title,
      description: post.data.summary,
      pubDate: post.data.publishDate,
      link: `/posts/${post.id}/`,
      categories: [post.data.category, ...post.data.tags],
    })),
    customData: "<language>en-us</language>",
  });
}
