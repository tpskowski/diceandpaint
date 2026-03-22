# -*- coding: utf-8 -*-
import hashlib
import json
import mimetypes
import re
import shutil
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup, Tag
from ftfy import fix_text
from markdownify import markdownify as md

ROOT = Path("working/diceandpaint-scrape")
PAGES_DIR = ROOT / "pages"
IMAGES_DIR = ROOT / "images"
MANIFEST_PATH = ROOT / "manifest.json"
START_URL = "https://www.diceandpaint.net/"
DOMAIN = "www.diceandpaint.net"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; diceandpaint-migrator/1.0; +https://www.diceandpaint.net/)"
}
TIMEOUT = 30

session = requests.Session()
session.headers.update(HEADERS)


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    scheme = parsed.scheme or "https"
    netloc = parsed.netloc or DOMAIN
    path = parsed.path or "/"
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    return urlunparse((scheme, netloc, path, "", "", ""))


def is_internal(url: str) -> bool:
    parsed = urlparse(url)
    return (parsed.netloc in {"", DOMAIN}) and parsed.scheme in {"", "http", "https"}


def slug_for_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        return "home"
    return re.sub(r"[^a-zA-Z0-9/_-]+", "-", path)


def page_output_path(url: str) -> Path:
    return PAGES_DIR / f"{slug_for_url(url)}.md"


def page_image_dir(url: str) -> Path:
    return IMAGES_DIR / slug_for_url(url)


def guess_extension(url: str, content_type: Optional[str]) -> str:
    if content_type:
        content_type = content_type.split(";")[0].strip().lower()
        guessed = mimetypes.guess_extension(content_type)
        if guessed:
            return ".jpg" if guessed == ".jpe" else guessed
    suffix = Path(urlparse(url).path).suffix
    return suffix or ".bin"


def clean_text(text: str) -> str:
    return fix_text(text).strip()


def clean_title(title: str) -> str:
    title = clean_text(title).replace("\u2014 Dice & Paint", "").replace(" - Dice & Paint", "").strip()
    return re.sub(r"\s+", " ", title)


def page_kind(url: str) -> str:
    path = urlparse(url).path.rstrip("/") or "/"
    if path == "/":
        return "home"
    if path == "/cart":
        return "utility"
    if path.startswith("/blog/category/"):
        return "blog-category"
    if path.startswith("/blog/tag/"):
        return "blog-tag"
    if path.startswith("/blog/"):
        return "blog-post"
    return "page"


def fetch(url: str) -> requests.Response:
    response = session.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    response.encoding = "utf-8"
    return response


def get_html(url: str) -> str:
    response = fetch(url)
    return clean_text(response.text)


def download_image(url: str, page_url: str) -> Optional[str]:
    try:
        response = fetch(url)
    except Exception:
        return None

    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]
    ext = guess_extension(url, response.headers.get("content-type"))
    image_dir = page_image_dir(page_url)
    image_dir.mkdir(parents=True, exist_ok=True)
    image_path = image_dir / f"{digest}{ext}"
    image_path.write_bytes(response.content)
    return image_path.relative_to(ROOT).as_posix()


def replace_image_sources(container: Tag, page_url: str) -> list[str]:
    downloaded = []
    seen = set()
    for img in container.find_all("img"):
        src = img.get("data-src") or img.get("src")
        if not src:
            continue
        absolute = urljoin(page_url, src)
        if absolute in seen:
            continue
        seen.add(absolute)
        local = download_image(absolute, page_url)
        if local:
            img["src"] = local
            downloaded.append(local)
    return downloaded


def find_title(soup: BeautifulSoup) -> str:
    og = soup.find("meta", attrs={"property": "og:title"})
    if og and og.get("content"):
        return clean_title(og["content"])
    h1 = soup.find("h1")
    if h1:
        return clean_title(h1.get_text(" ", strip=True))
    if soup.title and soup.title.string:
        return clean_title(soup.title.string)
    return "Dice & Paint"


def find_date(soup: BeautifulSoup, kind: str) -> Optional[str]:
    if kind != "blog-post":
        return None
    for attrs in [
        {"property": "article:published_time"},
        {"name": "article:published_time"},
        {"itemprop": "datePublished"},
    ]:
        node = soup.find("meta", attrs=attrs)
        if node and node.get("content"):
            return clean_text(node["content"])
    for selector in ["time", ".blog-meta-item--date", ".entry-date"]:
        node = soup.select_one(selector)
        if node:
            raw = node.get("datetime") or node.get_text(" ", strip=True) or ""
            return clean_text(raw) or None
    return None


def find_summary(soup: BeautifulSoup) -> Optional[str]:
    for attrs in [{"name": "description"}, {"property": "og:description"}]:
        node = soup.find("meta", attrs=attrs)
        if node and node.get("content"):
            return re.sub(r"\s+", " ", clean_text(node["content"]))
    return None


def find_content_container(soup: BeautifulSoup, kind: str) -> Tag:
    if kind == "blog-post":
        for selector in ["article", "main article", ".blog-item-wrapper", "main"]:
            node = soup.select_one(selector)
            if node:
                return node
    for selector in ["main", "article", "#content", ".sqs-layout"]:
        node = soup.select_one(selector)
        if node:
            return node
    return soup.body or soup


def clean_container(container: Tag) -> None:
    selectors = [
        "script",
        "style",
        "noscript",
        "form",
        "nav",
        "footer",
        ".header-menu",
        ".blog-item-author-profile-wrapper",
        ".newsletter-form",
        ".pagination",
        ".sqs-announcement-bar-dropzone",
        ".sqs-html-content + .sqs-block-button",
    ]
    for selector in selectors:
        for node in container.select(selector):
            node.decompose()


def extract_links(soup: BeautifulSoup, page_url: str) -> list[str]:
    results = []
    for a in soup.find_all("a", href=True):
        href = urljoin(page_url, a["href"])
        if not is_internal(href):
            continue
        normalized = normalize_url(href)
        path = urlparse(normalized).path
        if path.startswith("/api") or path.startswith("/sitemap"):
            continue
        if re.search(r"\.(jpg|jpeg|png|gif|svg|webp|pdf)$", path, re.I):
            continue
        results.append(normalized)
    return results


def to_markdown(container: Tag) -> str:
    text = md(str(container), heading_style="ATX", bullets="-")
    text = clean_text(text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def scrape_page(url: str) -> tuple[dict, list[str]]:
    html = get_html(url)
    soup = BeautifulSoup(html, "html.parser")
    kind = page_kind(url)
    title = find_title(soup)
    date = find_date(soup, kind)
    summary = find_summary(soup)
    container = find_content_container(soup, kind)
    container = BeautifulSoup(str(container), "html.parser")
    working = container.body or container
    clean_container(working)
    images = replace_image_sources(working, url)
    content = to_markdown(working)

    frontmatter = ["---", f'title: "{title.replace(chr(34), chr(39))}"', f'source_url: "{url}"', f'kind: "{kind}"']
    if date:
        frontmatter.append(f'date: "{date.replace(chr(34), chr(39))}"')
    if summary:
        frontmatter.append(f'summary: "{summary.replace(chr(34), chr(39))}"')
    if images:
        frontmatter.append("images:")
        for image in images:
            frontmatter.append(f"  - {image}")
    frontmatter.append("---")
    markdown = "\n".join(frontmatter) + "\n\n" + content + "\n"

    output_path = page_output_path(url)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")

    entry = {
        "url": url,
        "title": title,
        "date": date,
        "kind": kind,
        "path": output_path.relative_to(ROOT).as_posix(),
        "images": images,
    }
    return entry, extract_links(soup, url)


def main() -> None:
    if ROOT.exists():
        shutil.rmtree(ROOT)
    ROOT.mkdir(parents=True, exist_ok=True)
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    queue = [normalize_url(START_URL)]
    seen = set()
    manifest = []

    while queue:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        try:
            entry, links = scrape_page(url)
            manifest.append(entry)
            print(f"scraped {url}")
        except Exception as exc:
            print(f"failed {url}: {exc}")
            continue

        for link in links:
            if link not in seen and link not in queue:
                queue.append(link)

        time.sleep(0.15)

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"wrote {len(manifest)} pages to {ROOT}")


if __name__ == "__main__":
    main()