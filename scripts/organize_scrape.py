# -*- coding: utf-8 -*-
import json
import shutil
from pathlib import Path

ROOT = Path('working/diceandpaint-scrape')
RAW_MANIFEST = ROOT / 'manifest.json'
ORGANIZED = ROOT / 'organized'
PAGES_OUT = ORGANIZED / 'standalone-pages'
POSTS_OUT = ORGANIZED / 'posts'
TAXONOMY_OUT = ORGANIZED / 'taxonomy'
UTILITY_OUT = ORGANIZED / 'utility'
INDEX_PATH = ORGANIZED / 'README.md'


def safe_bucket(kind: str) -> str:
    if kind == 'blog-post':
        return 'posts'
    if kind == 'page' or kind == 'home':
        return 'standalone-pages'
    if kind in {'blog-category', 'blog-tag'}:
        return 'taxonomy'
    return 'utility'


def bucket_dir(name: str) -> Path:
    return {
        'posts': POSTS_OUT,
        'standalone-pages': PAGES_OUT,
        'taxonomy': TAXONOMY_OUT,
        'utility': UTILITY_OUT,
    }[name]


def rel_root_path(path_str: str) -> Path:
    return ROOT / Path(path_str)


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2), encoding='utf-8')


def main() -> None:
    items = json.loads(RAW_MANIFEST.read_text(encoding='utf-8'))
    if ORGANIZED.exists():
        shutil.rmtree(ORGANIZED)

    for directory in [ORGANIZED, PAGES_OUT, POSTS_OUT, TAXONOMY_OUT, UTILITY_OUT]:
        directory.mkdir(parents=True, exist_ok=True)

    grouped: dict[str, list[dict]] = {
        'posts': [],
        'standalone-pages': [],
        'taxonomy': [],
        'utility': [],
    }

    for item in items:
        bucket = safe_bucket(item['kind'])
        grouped[bucket].append(item)

        src = rel_root_path(item['path'])
        dest = bucket_dir(bucket) / Path(item['path']).name
        shutil.copy2(src, dest)

        copied_images = []
        for image in item.get('images', []):
            image_src = rel_root_path(image)
            image_dest = bucket_dir(bucket) / image
            image_dest.parent.mkdir(parents=True, exist_ok=True)
            if image_src.exists():
                shutil.copy2(image_src, image_dest)
                copied_images.append(image_dest.relative_to(ORGANIZED).as_posix())

        item['organized_bucket'] = bucket
        item['organized_markdown'] = dest.relative_to(ORGANIZED).as_posix()
        item['organized_images'] = copied_images

    for bucket, bucket_items in grouped.items():
        bucket_items.sort(key=lambda item: ((item.get('date') or ''), item['title']))
        write_json(bucket_dir(bucket) / 'manifest.json', bucket_items)

    write_json(ORGANIZED / 'manifest.json', items)

    lines = [
        '# Scrape Organization',
        '',
        'This directory reorganizes the raw scrape into migration buckets without changing the Astro site.',
        '',
        '## Buckets',
        '',
        f'- `posts/`: {len(grouped["posts"])} blog posts',
        f'- `standalone-pages/`: {len(grouped["standalone-pages"])} home and page-style entries',
        f'- `taxonomy/`: {len(grouped["taxonomy"])} blog category and tag pages',
        f'- `utility/`: {len(grouped["utility"])} utility pages',
        '',
        '## Files',
        '',
        '- `manifest.json` at this level contains all entries with their organized destinations.',
        '- Each bucket also has its own `manifest.json`.',
        '- Images are copied into the same bucket under an `images/` subtree.',
    ]
    INDEX_PATH.write_text('\n'.join(lines) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()