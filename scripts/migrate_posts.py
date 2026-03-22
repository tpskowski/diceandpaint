# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

ROOT = Path(r"E:\git\diceandpaint")
SCRAPE_ROOT = ROOT / "working" / "diceandpaint-scrape" / "organized" / "posts"
SRC_POSTS = ROOT / "src" / "content" / "posts"
PUBLIC_POSTS = ROOT / "public" / "posts"
MANIFEST_PATH = SCRAPE_ROOT / "manifest.json"

MONTH_LINE = re.compile(r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}$")
CATEGORY_LINK_LINE = re.compile(r"^(\[[^\]]+\]\(/blog/category/[^)]+\))+\s*$")
TAG_LINK_LINE = re.compile(r"^(\[[^\]]+\]\(/blog/tag/[^)]+\))+\s*$")
TITLE_LINE = re.compile(r"^#\s+(.+?)\s*$")

REPLACEMENTS = {
    "\u00a0": " ",
    "\u00c2\u00a0": " ",
    "\u00e2\u20ac\u2122": "'",
    "\u00e2\u20ac\u0153": '"',
    "\u00e2\u20ac\x9d": '"',
    "\u00e2\u20ac\u201c": "-",
    "\u00e2\u20ac\u201d": "-",
    "\u00e2\u20ac\u00a6": "...",
    "\u00e2\u20ac\u02dc": "'",
    "\u00f0\u0178\u201d\u00a5": "fire",
    "\u00e3\u20ac\u2019": "",
    "\u00e2\u02c6\u2019": "-",
}


def fix_text(text: str) -> str:
    for bad, good in REPLACEMENTS.items():
        text = text.replace(bad, good)
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    block = text[4:end]
    body = text[end + 5 :].lstrip("\n")
    data: dict[str, Any] = {}
    current_key: str | None = None
    for raw_line in block.splitlines():
        if raw_line.startswith("  - ") and current_key:
            data.setdefault(current_key, []).append(raw_line[4:].strip().strip('"'))
            continue
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_key = key
        if value == "":
            data[key] = []
        elif value.startswith('"') and value.endswith('"'):
            data[key] = value[1:-1]
        else:
            data[key] = value
    return data, body


def extract_links(line: str, kind: str) -> list[str]:
    return re.findall(rf"\[([^\]]+)\]\(/blog/{kind}/[^)]+\)", line)


def summarize(text: str) -> str:
    for chunk in text.split("\n\n"):
        line = chunk.strip()
        if not line or line.startswith("#") or line.startswith("!["):
            continue
        clean = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", line)
        clean = re.sub(r"\s+", " ", clean).strip()
        if clean:
            if len(clean) > 180:
                clean = clean[:177].rsplit(" ", 1)[0] + "..."
            return clean.replace('"', "'")
    return "Migrated post from diceandpaint.net."


def infer_category(title: str, body: str, tags: list[str]) -> str:
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    for line in lines[:5]:
        if CATEGORY_LINK_LINE.match(line):
            cats = extract_links(line, "category")
            if cats:
                return cats[0].replace("-", " ").title()
    if tags:
        return tags[0].replace("-", " ").title()
    if "RPG" in title:
        return "RPG"
    if "Old World" in title or "SBOT" in title:
        return "Old World"
    return "Blog"


def clean_body(title: str, body: str) -> tuple[str, list[str], list[str]]:
    body = fix_text(body)
    lines = body.splitlines()
    cleaned: list[str] = []
    categories: list[str] = []
    tags: list[str] = []
    skip_leading = True

    for raw in lines:
        line = raw.strip()
        if skip_leading:
            if not line:
                continue
            title_match = TITLE_LINE.match(line)
            if title_match and title_match.group(1).strip() == title.strip():
                continue
            if CATEGORY_LINK_LINE.match(line):
                categories = extract_links(line, "category")
                continue
            if MONTH_LINE.match(line):
                continue
            if line.startswith("Written By "):
                continue
            skip_leading = False
        cleaned.append(raw)

    while cleaned and not cleaned[0].strip():
        cleaned.pop(0)
    while cleaned and not cleaned[-1].strip():
        cleaned.pop()

    if cleaned and TAG_LINK_LINE.match(cleaned[-1].strip()):
        tags = extract_links(cleaned[-1].strip(), "tag")
        cleaned.pop()

    return "\n".join(cleaned).strip() + "\n", categories, tags


def copy_asset(src_relative: str, target_dir: Path) -> str:
    src = ROOT / "working" / "diceandpaint-scrape" / "organized" / src_relative
    if not src.exists():
        raise FileNotFoundError(src)
    target_dir.mkdir(parents=True, exist_ok=True)
    dest = target_dir / Path(src_relative).name
    shutil.copy2(src, dest)
    return dest.name


def iso_offset(date_str: str) -> str:
    return re.sub(r"([+-]\d{2})(\d{2})$", r"\1:\2", date_str)


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    imported = 0
    skipped = 0

    for entry in manifest:
        source_slug = Path(entry["organized_markdown"]).stem
        if source_slug == "old-world-meta-watch-24-10-24":
            skipped += 1
            continue

        source_path = SCRAPE_ROOT / Path(entry["organized_markdown"]).name
        raw = source_path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(raw)
        title = str(meta.get("title", source_slug.replace("-", " ").title()))
        body, categories, tags = clean_body(title, body)
        summary = str(meta.get("summary") or summarize(body))
        category = infer_category(title, body, tags or categories)

        out_slug = source_slug
        out_path = SRC_POSTS / f"{out_slug}.md"
        asset_dir = PUBLIC_POSTS / out_slug

        preview_name = "preview.webp"
        if entry.get("preview_image"):
            preview_name = copy_asset(entry["preview_image"], asset_dir)

        for image in entry.get("organized_images", []):
            copy_asset(image, asset_dir)

        def replace_image(match: re.Match[str]) -> str:
            alt = match.group(1)
            rel = match.group(2)
            filename = Path(rel).name
            return f"![{alt}](/posts/{out_slug}/{filename})"

        body = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace_image, body)

        frontmatter = [
            "---",
            f'title: "{title.replace(chr(34), "\\\"")}"',
            f'summary: "{summary.replace(chr(34), "\\\"")}"',
            f'publishDate: "{iso_offset(str(meta.get("date", "")))}"',
            f'category: "{category}"',
            "tags:",
        ]
        for tag in tags or ["blog"]:
            frontmatter.append(f'  - "{tag}"')
        frontmatter.extend([
            f'thumbnail: "/posts/{out_slug}/{preview_name}"',
            f'thumbnailAlt: "Preview image for the {title.replace(chr(34), "")} article."',
            "hideHero: false",
            "draft: false",
            "---",
            "",
        ])

        out_path.write_text("\n".join(frontmatter) + body, encoding="utf-8")
        imported += 1

    print(json.dumps({"imported": imported, "skipped": skipped}, indent=2))


if __name__ == "__main__":
    main()
