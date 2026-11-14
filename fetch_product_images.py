#!/usr/bin/env python3
"""Download a picture for every product whose image is still a remote URL.

For each product it reads the product page's og:image (the store's own main
picture), falls back to the existing image_url, saves a 480px JPEG under
images/products/, and points image_url at the local copy. The original remote
URL is kept in image_source_url. Products that already have a local image are
skipped, so it is safe to re-run.

Requires Pillow (pip install pillow).

Usage:
    python fetch_product_images.py && python build_catalog.py
"""
import io
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
PRODUCTS = SCRIPT_DIR / "products.json"
IMAGE_DIR = SCRIPT_DIR / "images" / "products"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
OG = re.compile(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)', re.I)


def get(url: str, timeout: int = 25) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except urllib.error.HTTPError as err:
        if err.code not in (403, 429):
            raise
    # Some stores (Shopify) turn away Python's client but serve curl.
    out = subprocess.run(["curl", "-sfL", "-m", str(timeout), "-A", UA, url], capture_output=True, check=True)
    return out.stdout


def page_images(page_url: str) -> list[str]:
    """Picture URLs a product page names for itself, best first."""
    try:
        html = get(page_url).decode("utf-8", "ignore")
    except Exception:
        return []
    found = []
    m = OG.search(html)
    if m:
        url = m.group(1).replace("&amp;", "&")
        url = "https:" + url if url.startswith("//") else url
        found.append(url)
        # Adafruit sometimes lists the picture without its extension.
        if not re.search(r"\.(jpe?g|png|gif|webp)(\?|$)", url, re.I):
            found += [url + ext for ext in (".jpg", ".jpeg", ".png")]
    pid = page_url.rstrip("/").rsplit("/", 1)[-1]
    if "adafruit.com" in page_url and pid.isdigit():
        # Fall back to the page's own gallery pictures, at full size.
        for name in dict.fromkeys(re.findall(rf"cdn-shop\.adafruit\.com/\d+x\d+/({pid}-\d+\.(?:jpe?g|png))", html)):
            found.append(f"https://cdn-shop.adafruit.com/970x728/{name}")
    return found


def save_thumb(data: bytes, dest: Path) -> None:
    im = Image.open(io.BytesIO(data))
    im.seek(0)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, "white")
        bg.paste(im, mask=im.split()[-1])
        im = bg
    im = im.convert("RGB")
    im.thumbnail((480, 480))
    im.save(dest, "JPEG", quality=82)


def main() -> None:
    products = json.loads(PRODUCTS.read_text(encoding="utf-8"))
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    done = failed = 0
    for key, p in products.items():
        current = p.get("image_url") or ""
        if current and not current.startswith("http"):
            continue
        candidates = []
        if p.get("page_url"):
            candidates += page_images(p["page_url"])
        if current:
            candidates.append(current)
        dest = IMAGE_DIR / (re.sub(r"[^A-Za-z0-9_-]+", "-", key).strip("-") + ".jpg")
        for url in candidates:
            try:
                save_thumb(get(url), dest)
            except Exception:
                continue
            p["image_source_url"] = url
            p["image_url"] = dest.relative_to(SCRIPT_DIR).as_posix()
            done += 1
            break
        else:
            failed += 1
            print(f"no picture: {key} ({p.get('name')})", file=sys.stderr)
        time.sleep(1.5)
    PRODUCTS.write_text(json.dumps(products, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Downloaded {done} pictures, {failed} without a picture")


if __name__ == "__main__":
    main()
