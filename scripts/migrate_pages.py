# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(r"E:\git\diceandpaint")
SCRAPE_ROOT = ROOT / "working" / "diceandpaint-scrape" / "organized" / "standalone-pages"
SRC_PAGES = ROOT / "src" / "content" / "pages"
PUBLIC_PAGES = ROOT / "public" / "pages"
MANIFEST_PATH = SCRAPE_ROOT / "manifest.json"

SKIP_URLS = {
    "https://www.diceandpaint.net/",
    "https://www.diceandpaint.net/necromundarules/toxicrivers",
    "https://www.diceandpaint.net/necromunda-rules-1",
}

ORDER_MAP = {
    "buying-guides": 20,
    "imperialis-buying-guide-starter": 21,
    "imperialis-buying-guide-astartes": 22,
    "imperialis-buying-guide-auxilia": 23,
    "reviews": 30,
    "eat-the-reich": 31,
    "model-gallery": 40,
    "battletech": 41,
    "steel-rift": 42,
    "3rd-royal-guards": 43,
    "10th-skye-rangers": 44,
    "15th-marik-militia-free-worlds-league-c-3007": 45,
    "house-imarra": 46,
    "67th-north-horizon-corps-fire-support-team": 47,
    "necromunda-rules": 50,
}

TITLE_OVERRIDES = {
    "reviews": "Reviews",
    "model-gallery": "Model Gallery",
}

SUMMARY_OVERRIDES = {
    "buying-guides": "Overview page for the Legions Imperialis buying guide series.",
    "reviews": "Long-form tabletop review archive and featured review pages.",
    "model-gallery": "Painted model galleries organized by game and force.",
    "battletech": "Battletech force galleries and painted unit showcases.",
    "steel-rift": "Steel Rift painted force galleries and model showcases.",
    "necromunda-rules": "House rules and reference pages for Necromunda.",
}

REPLACEMENTS = {
    "\u00a0": " ",
    "Â": "",
    "â€™": "'",
    "â€œ": '"',
    "â€\x9d": '"',
    "â€“": "-",
    "â€”": "-",
    "â€¦": "...",
    "âˆ’": "-",
}


def fix_text(text: str) -> str:
    for bad, good in REPLACEMENTS.items():
        text = text.replace(bad, good)
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def parse_frontmatter(text: str):
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    block = text[4:end]
    body = text[end + 5 :].lstrip("\n")
    data = {}
    current = None
    for raw in block.splitlines():
        if raw.startswith("  - ") and current:
            data.setdefault(current, []).append(raw[4:].strip().strip('"'))
            continue
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.strip()
        current = key
        if value == "":
            data[key] = []
        elif value.startswith('"') and value.endswith('"'):
            data[key] = value[1:-1]
        else:
            data[key] = value
    return data, body


def summarize(body: str, slug_name: str) -> str:
    if slug_name in SUMMARY_OVERRIDES:
        return SUMMARY_OVERRIDES[slug_name]
    for chunk in body.split("\n\n"):
        line = chunk.strip()
        if not line or line.startswith("#") or line.startswith("![") or line.startswith("[") or line.startswith("Updated ") or line.startswith("Written by"):
            continue
        clean = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", line)
        clean = re.sub(r"\s+", " ", clean).strip()
        if clean:
            if len(clean) > 180:
                clean = clean[:177].rsplit(" ", 1)[0] + "..."
            return clean.replace('"', "'")
    return "Migrated standalone page from diceandpaint.net."


def slug_from_url(url: str) -> str:
    path = urlparse(url).path.strip("/")
    return path or "home"


def copy_asset(src_relative: str, target_dir: Path) -> str:
    src = ROOT / "working" / "diceandpaint-scrape" / "organized" / src_relative
    target_dir.mkdir(parents=True, exist_ok=True)
    dest = target_dir / Path(src_relative).name
    shutil.copy2(src, dest)
    return dest.name


def clean_body(title: str, body: str) -> str:
    body = fix_text(body)
    lines = body.splitlines()
    cleaned = []
    skipping = True
    title_variants = {title.strip(), title.replace("&", "and").strip()}
    for raw in lines:
        line = raw.strip()
        if skipping:
            if not line:
                continue
            if line.startswith("# ") and line[2:].strip() in title_variants:
                continue
            skipping = False
        cleaned.append(raw)
    while cleaned and not cleaned[0].strip():
        cleaned.pop(0)
    return "\n".join(cleaned).strip() + "\n"


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    for path in [
        SRC_PAGES / "about.mdx",
        SRC_PAGES / "buying-guides.mdx",
        SRC_PAGES / "model-gallery.mdx",
        SRC_PAGES / "reviews.mdx",
    ]:
        if path.exists():
            path.unlink()

    for entry in manifest:
        url = entry["url"]
        if url in SKIP_URLS:
            continue

        slug = slug_from_url(url)
        slug_name = Path(slug).name
        out_path = SRC_PAGES / (slug + ".md")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        asset_dir = PUBLIC_PAGES / slug

        source_path = SCRAPE_ROOT / Path(entry["organized_markdown"]).name
        raw = source_path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(raw)
        title = TITLE_OVERRIDES.get(slug_name, str(meta.get("title", slug_name.replace("-", " ").title())))
        body = clean_body(title, body)
        summary = summarize(body, slug_name)
        order = ORDER_MAP.get(slug_name, 100)

        for image in entry.get("organized_images", []):
            copy_asset(image, asset_dir)

        body = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", lambda m: f"![{m.group(1)}](/pages/{slug}/{Path(m.group(2)).name})", body)

        frontmatter = "\n".join([
            "---",
            f'title: "{title.replace(chr(34), "")}"',
            f'summary: "{summary.replace(chr(34), "")}"',
            f"order: {order}",
            "---",
            "",
        ])
        out_path.write_text(frontmatter + body, encoding="utf-8")

    necro_page = SRC_PAGES / "necromunda-rules.md"
    necro_page.write_text(
        "---\n"
        'title: "Necromunda Rules"\n'
        'summary: "House rules and reference pages for Necromunda."\n'
        "order: 50\n"
        "---\n\n"
        "## Available Rules\n\n"
        "- [Toxic Rivers](/toxicrivers/)\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
