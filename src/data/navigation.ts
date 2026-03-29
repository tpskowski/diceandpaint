export type NavLink = {
  label: string;
  href: string;
  external?: boolean;
};

export type NavGroup = {
  label: string;
  href?: string;
  items?: NavLink[];
};

export const primaryNav: NavGroup[] = [
  {
    label: "Blog",
    href: "/",
  },
  {
    label: "Guides",
    href: "/guides/",
    items: [
      { label: "Legions Imperialis Buyers Guide", href: "/guides/legions-imperialis-buyers-guide/" },
      { label: "Legiones Astartes Review", href: "/guides/legions-imperialis-legiones-astartes-review/" },
    ],
  },
  {
    label: "Reviews",
    href: "/reviews/",
    items: [
      { label: "Eat The Reich", href: "/reviews/eat-the-reich/" },
    ],
  },
  {
    label: "Model Gallery",
    href: "/model-gallery/",
    items: [
      { label: "Battletech", href: "/model-gallery/battletech/" },
      { label: "Steel Rift", href: "/model-gallery/steel-rift/" },
    ],
  },
  {
    label: "Homebrew Rules",
    href: "/homebrew-rules/",
    items: [
      { label: "Necromunda Toxic Rivers", href: "/homebrew-rules/toxicrivers/" },
    ],
  },
];

