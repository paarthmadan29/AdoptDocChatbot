from __future__ import annotations
import json
import re
from pathlib import Path
from typing import List, Tuple

import numpy as np
import requests
from bs4 import BeautifulSoup

# --------------------------- CONFIG -----------------------------------
DOCS_ROOT = "https://docs.truefoundry.com"
SEED_URLS = [
    "https://docs.truefoundry.com/docs/introduction",
]
CHUNK_SIZE = 150  # words per chunk
CHUNK_STRIDE = 20
EMBED_MODEL = "all-MiniLM-L6-v2"
INDEX_DIR = Path(__file__).with_suffix("").parent / "_index"
INDEX_DIR.mkdir(exist_ok=True)
EMB_FILE = INDEX_DIR / "embeddings.dat"
META_FILE = INDEX_DIR / "meta.json"

def extract_links(html: str, base_url: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("#"):
            continue
        if href.startswith("/"):
            href = DOCS_ROOT + href
        if href.startswith(DOCS_ROOT):
            links.append(href.split("#")[0])  # drop in‑page anchors
    return links


def clean_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(["nav", "aside", "footer"]):
        tag.decompose()
    text = soup.get_text(" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    return text


def crawl(seed_urls: List[str]) -> List[Tuple[str, str]]:
    visited, queue, pages = set(), list(seed_urls), []
    session = requests.Session()
    while queue:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)
        try:
            r = session.get(url, timeout=10)
            r.raise_for_status()
        except Exception as e:
            print(f"[warn] {url}: {e}")
            continue
        html = r.text
        pages.append((url, clean_text(html)))
        # queue new links within same domain
        for link in extract_links(html, url):
            if link not in visited and link.startswith(DOCS_ROOT):
                queue.append(link)
    return pages


def save_crawled_pages(pages: List[Tuple[str, str]], output_dir) -> Path:
    if output_dir is None:
        output_dir = Path("crawled_pages")
    
    all_pages_file = output_dir / "all_pages.json"
    with open(all_pages_file, 'w', encoding='utf-8') as f:
        json.dump(pages, f, indent=2, ensure_ascii=False)
    
    individual_dir = output_dir / "individual"
    individual_dir.mkdir(exist_ok=True)
    
    for i, (url, content) in enumerate(pages):
        filename = f"{i:04d}_{url.replace(DOCS_ROOT, '').strip('/').replace('/', '_')}.json"
        if filename == f"{i:04d}_.json":  # Handle root URL
            filename = f"{i:04d}_root.json"
            
        if len(filename) > 250:  # Max filename length is usually 255
            filename = f"{i:04d}_{filename[-240:]}"
            
        file_path = individual_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({
                "url": url,
                "content": content
            }, f, indent=2, ensure_ascii=False)
    
    index_file = output_dir / "index.json"
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump({
            "total_pages": len(pages),
            "pages": [{"id": i, "url": url} for i, (url, _) in enumerate(pages)]
        }, f, indent=2, ensure_ascii=False)
    
    print(f"[+] Saved {len(pages)} pages to {output_dir}")
    print(f"    - All pages: {all_pages_file}")
    print(f"    - Individual pages: {individual_dir}")
    print(f"    - Index: {index_file}")
    
    return output_dir

def build_index():
    print("[+] Crawling docs…")
    pages = crawl(SEED_URLS)
    print(f"[+] Fetched {len(pages)} pages")
    breakpoint()
    save_crawled_pages(pages, output_dir="src/data/crawl")
    return pages


if __name__ == "__main__":
    pages = build_index()
    breakpoint()
    