import { defineConfig } from "astro/config";
import mdx from "@astrojs/mdx";

import cloudflare from "@astrojs/cloudflare";

export default defineConfig({
  site: "https://www.diceandpaint.net",
  integrations: [mdx()],
  output: "static",

  redirects: {
    "/imperialis-buying-guide-astartes": "/guides/legions-imperialis-buyers-guide/",
    "/imperialis-buying-guide-starter": "/guides/legions-imperialis-buyers-guide/",
    "/imperialis-buying-guide-auxilia": "/guides/legions-imperialis-buyers-guide/",
  },

  adapter: cloudflare(),
});