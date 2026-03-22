# -*- coding: utf-8 -*-
import json
import mimetypes
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from ftfy import fix_text

ROOT = Path('working/diceandpaint-scrape')
RAW_MANIFEST = ROOT / 'manifest.json'
ORG_ROOT = ROOT / 'organized'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; diceandpaint-preview-enricher/1.0; +https://www.diceandpaint.net/)'
}
TIMEOUT = 30

session = requests.Session()
session.headers.update(HEADERS)


def clean_text(text: str) -> str:
    return fix_text(text).strip()


def guess_extension(url: str, content_type: str | None) -> str:
    if content_type:
        content_type = content_type.split(';')[0].strip().lower()
        guessed = mimetypes.guess_extension(content_type)
        if guessed:
            return '.jpg' if guessed == '.jpe' else guessed
    suffix = Path(urlparse(url).path).suffix
    return suffix or '.bin'


def download_preview(preview_url: str, page_image_dir: Path) -> str | None:
    response = session.get(preview_url, timeout=TIMEOUT)
    response.raise_for_status()
    ext = guess_extension(preview_url, response.headers.get('content-type'))
    out = page_image_dir / f'preview{ext}'
    page_image_dir.mkdir(parents=True, exist_ok=True)
    out.write_bytes(response.content)
    return out.relative_to(ROOT).as_posix()


def fetch_preview_url(page_url: str) -> str | None:
    response = session.get(page_url, timeout=TIMEOUT)
    response.raise_for_status()
    response.encoding = 'utf-8'
    soup = BeautifulSoup(clean_text(response.text), 'html.parser')
    for attrs in [
        {'property': 'og:image'},
        {'name': 'twitter:image'},
        {'property': 'twitter:image'},
    ]:
        node = soup.find('meta', attrs=attrs)
        if node and node.get('content'):
            return urljoin(page_url, clean_text(node['content']))
    return None


def update_markdown_frontmatter(md_path: Path, preview_path: str) -> None:
    text = md_path.read_text(encoding='utf-8')
    parts = text.split('---', 2)
    if len(parts) < 3:
        return
    frontmatter = parts[1].strip().splitlines()
    body = parts[2]
    frontmatter = [line for line in frontmatter if not line.startswith('preview_image:')]
    frontmatter.append(f'preview_image: "{preview_path}"')
    new_text = '---\n' + '\n'.join(frontmatter) + '\n---' + body
    md_path.write_text(new_text, encoding='utf-8')


def main() -> None:
    raw_items = json.loads(RAW_MANIFEST.read_text(encoding='utf-8'))
    organized_manifest = json.loads((ORG_ROOT / 'manifest.json').read_text(encoding='utf-8')) if (ORG_ROOT / 'manifest.json').exists() else []
    org_by_url = {item['url']: item for item in organized_manifest}

    for item in raw_items:
        if item.get('kind') != 'blog-post':
            continue
        preview_url = fetch_preview_url(item['url'])
        if not preview_url:
            continue
        raw_page_dir = ROOT / 'images' / Path(item['path']).with_suffix('').as_posix().replace('pages/', '')
        raw_preview = download_preview(preview_url, raw_page_dir)
        if not raw_preview:
            continue
        item['preview_url'] = preview_url
        item['preview_image'] = raw_preview
        update_markdown_frontmatter(ROOT / item['path'], raw_preview)

        org_item = org_by_url.get(item['url'])
        if org_item:
            bucket = org_item['organized_bucket']
            org_dir = ORG_ROOT / bucket / 'images' / Path(item['path']).with_suffix('').as_posix().replace('pages/', '')
            response = session.get(preview_url, timeout=TIMEOUT)
            response.raise_for_status()
            ext = guess_extension(preview_url, response.headers.get('content-type'))
            org_path = org_dir / f'preview{ext}'
            org_dir.mkdir(parents=True, exist_ok=True)
            org_path.write_bytes(response.content)
            rel_org = org_path.relative_to(ORG_ROOT).as_posix()
            org_item['preview_url'] = preview_url
            org_item['preview_image'] = rel_org
            update_markdown_frontmatter(ORG_ROOT / org_item['organized_markdown'], rel_org)

    RAW_MANIFEST.write_text(json.dumps(raw_items, indent=2), encoding='utf-8')
    if organized_manifest:
        (ORG_ROOT / 'manifest.json').write_text(json.dumps(organized_manifest, indent=2), encoding='utf-8')
        for bucket in ['posts', 'standalone-pages', 'taxonomy', 'utility']:
            path = ORG_ROOT / bucket / 'manifest.json'
            if path.exists():
                bucket_items = [item for item in organized_manifest if item.get('organized_bucket') == bucket]
                path.write_text(json.dumps(bucket_items, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()