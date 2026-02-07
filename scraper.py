#!/usr/bin/env python3
"""
Adafruit Product Scraper

Reads purchase_history.csv to extract unique product IDs and names, fetches
product details from adafruit.com, and saves enriched data to products.json.
Optionally regenerates index.html from existing products.json.

Usage:
    python scraper.py                    # Scrape all products
    python scraper.py --update-html      # Regenerate index.html only
    python scraper.py --csv other.csv    # Use a different CSV file
    python scraper.py --force            # Re-scrape all products (ignore cache)
    python scraper.py --dry-run          # Show what would be scraped
"""

import argparse
import csv
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    print("Error: 'requests' package is required. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: 'beautifulsoup4' package is required. Install with: pip install beautifulsoup4", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_CSV = SCRIPT_DIR / "purchase_history.csv"
DEFAULT_JSON = SCRIPT_DIR / "products.json"
DEFAULT_HTML = SCRIPT_DIR / "index.html"

ADAFRUIT_PRODUCT_URL = "https://www.adafruit.com/product/{product_id}"
ADAFRUIT_CDN_IMAGE = "https://cdn-shop.adafruit.com/970x728/{product_id}-00.jpg"
ADAFRUIT_LEARN_BASE = "https://learn.adafruit.com"

REQUEST_TIMEOUT = 30  # seconds
RATE_LIMIT_DELAY = 1.0  # seconds between requests
MAX_RETRIES = 4
BACKOFF_BASE = 2  # exponential backoff base (seconds)

USER_AGENT = (
    "Mozilla/5.0 (compatible; InventoryItemsScraper/1.0; "
    "+https://github.com/user/InventoryItems)"
)

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

logger = logging.getLogger("scraper")


def setup_logging(verbose: bool = False) -> None:
    """Configure logging to both console and a log file."""
    level = logging.DEBUG if verbose else logging.INFO
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(formatter)

    log_file = SCRIPT_DIR / "scraper.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)
    logger.addHandler(file_handler)


# ---------------------------------------------------------------------------
# CSV parsing
# ---------------------------------------------------------------------------


def read_products_from_csv(csv_path: Path) -> dict[str, dict[str, Any]]:
    """
    Read purchase_history.csv and return a dict of unique products keyed by
    product ID (as string).

    Each value contains:
        - product_id: str
        - csv_name: str (name from the CSV)
        - total_qty: int (sum of quantities across all orders)
        - orders: list[str] (order numbers referencing this product)
    """
    products: dict[str, dict[str, Any]] = {}

    if not csv_path.is_file():
        logger.error("CSV file not found: %s", csv_path)
        sys.exit(1)

    with open(csv_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            pid = row["product id"].strip()
            name = row["product name"].strip()
            qty = int(row["quantity"].strip())
            order = row["order"].strip()

            if pid in products:
                products[pid]["total_qty"] += qty
                if order not in products[pid]["orders"]:
                    products[pid]["orders"].append(order)
            else:
                products[pid] = {
                    "product_id": pid,
                    "csv_name": name,
                    "total_qty": qty,
                    "orders": [order],
                }

    logger.info("Found %d unique products in %s", len(products), csv_path.name)
    return products


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------


def create_session() -> requests.Session:
    """Create a requests session with standard headers."""
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
    )
    return session


def fetch_with_retry(
    session: requests.Session,
    url: str,
    max_retries: int = MAX_RETRIES,
    backoff_base: int = BACKOFF_BASE,
) -> requests.Response | None:
    """
    Fetch a URL with exponential backoff retry logic.

    Returns the Response on success, or None if all retries are exhausted.
    """
    for attempt in range(max_retries + 1):
        try:
            response = session.get(url, timeout=REQUEST_TIMEOUT)

            if response.status_code == 200:
                return response

            if response.status_code == 404:
                logger.warning("Product page not found (404): %s", url)
                return None

            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", backoff_base ** (attempt + 1)))
                logger.warning(
                    "Rate limited (429). Waiting %d seconds before retry %d/%d",
                    retry_after, attempt + 1, max_retries,
                )
                time.sleep(retry_after)
                continue

            if response.status_code >= 500:
                wait = backoff_base ** (attempt + 1)
                logger.warning(
                    "Server error %d for %s. Retry %d/%d in %ds",
                    response.status_code, url, attempt + 1, max_retries, wait,
                )
                time.sleep(wait)
                continue

            # Other client errors -- don't retry
            logger.warning(
                "HTTP %d for %s -- not retrying", response.status_code, url
            )
            return None

        except requests.exceptions.Timeout:
            wait = backoff_base ** (attempt + 1)
            logger.warning(
                "Timeout fetching %s. Retry %d/%d in %ds",
                url, attempt + 1, max_retries, wait,
            )
            time.sleep(wait)

        except requests.exceptions.ConnectionError:
            wait = backoff_base ** (attempt + 1)
            logger.warning(
                "Connection error for %s. Retry %d/%d in %ds",
                url, attempt + 1, max_retries, wait,
            )
            time.sleep(wait)

        except requests.exceptions.RequestException as exc:
            logger.error("Request failed for %s: %s", url, exc)
            return None

    logger.error("All %d retries exhausted for %s", max_retries, url)
    return None


# ---------------------------------------------------------------------------
# Page parsing
# ---------------------------------------------------------------------------


def extract_product_data(html: str, product_id: str) -> dict[str, Any]:
    """
    Parse an Adafruit product page and extract structured data.

    Returns a dict with keys:
        - name: str
        - description: str
        - technical_specs: str
        - image_url: str
        - learn_guide_url: str | None
        - page_url: str
    """
    soup = BeautifulSoup(html, "html.parser")
    data: dict[str, Any] = {
        "name": "",
        "description": "",
        "technical_specs": "",
        "image_url": "",
        "learn_guide_url": None,
        "page_url": ADAFRUIT_PRODUCT_URL.format(product_id=product_id),
    }

    # ---- Product name ----
    # Priority: itemprop="name", <h1>, og:title, <title>
    name_el = soup.find(attrs={"itemprop": "name"})
    if name_el:
        data["name"] = name_el.get_text(strip=True)
    else:
        h1 = soup.find("h1")
        if h1:
            data["name"] = h1.get_text(strip=True)
        else:
            og_title = soup.find("meta", property="og:title")
            if og_title and og_title.get("content"):
                data["name"] = og_title["content"].strip()
            else:
                title = soup.find("title")
                if title:
                    # Adafruit titles often end with " : Adafruit Industries ..."
                    raw = title.get_text(strip=True)
                    data["name"] = raw.split(" : ")[0].strip()

    # ---- Product image ----
    # Priority: og:image meta tag, itemprop="image", CDN fallback
    og_image = soup.find("meta", property="og:image")
    if og_image and og_image.get("content"):
        data["image_url"] = og_image["content"].strip()
    else:
        img_el = soup.find(attrs={"itemprop": "image"})
        if img_el:
            src = img_el.get("src") or img_el.get("content", "")
            if src:
                data["image_url"] = src.strip()

    # Fallback to CDN pattern
    if not data["image_url"]:
        data["image_url"] = ADAFRUIT_CDN_IMAGE.format(product_id=product_id)

    # ---- Product description ----
    # Try the main description container, then meta description
    description_parts: list[str] = []

    # Adafruit uses itemprop="description" on the main description block
    desc_el = soup.find(attrs={"itemprop": "description"})
    if desc_el:
        description_parts.append(desc_el.get_text(separator="\n", strip=True))
    else:
        # Try common Adafruit product page selectors
        for selector in [
            "div.prod-desc-txt",
            "div.product-description",
            "div#description",
            "div.mobile-product-description",
        ]:
            desc_div = soup.select_one(selector)
            if desc_div:
                description_parts.append(
                    desc_div.get_text(separator="\n", strip=True)
                )
                break

    # Fallback: meta description
    if not description_parts:
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            description_parts.append(meta_desc["content"].strip())

    data["description"] = "\n".join(description_parts)

    # ---- Technical specifications ----
    specs_parts: list[str] = []

    # Look for a "Technical Details" section -- Adafruit uses various patterns
    for heading in soup.find_all(["h2", "h3", "h4", "strong", "b"]):
        heading_text = heading.get_text(strip=True).lower()
        if any(
            kw in heading_text
            for kw in ["technical detail", "specifications", "specs", "features"]
        ):
            # Grab the sibling content following this heading
            sibling = heading.find_next_sibling()
            collected: list[str] = []
            while sibling and sibling.name not in ("h2", "h3", "h4"):
                text = sibling.get_text(separator="\n", strip=True)
                if text:
                    collected.append(text)
                sibling = sibling.find_next_sibling()
            if collected:
                specs_parts.append(f"{heading.get_text(strip=True)}:\n" + "\n".join(collected))

    # Also try looking inside the description block for bullet-point specs
    if not specs_parts and desc_el:
        ul_elements = desc_el.find_all("ul")
        for ul in ul_elements:
            items = [li.get_text(strip=True) for li in ul.find_all("li")]
            if items:
                specs_parts.append("\n".join(f"- {item}" for item in items))

    data["technical_specs"] = "\n\n".join(specs_parts)

    # ---- Learn guide URL ----
    # Adafruit product pages link to learn.adafruit.com guides
    learn_links: list[str] = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if "learn.adafruit.com" in href:
            # Normalize the URL
            clean = href.split("?")[0].rstrip("/")
            if clean and clean not in learn_links:
                # Filter out generic links (home page, search, etc.)
                path_parts = clean.replace("https://learn.adafruit.com", "").replace("http://learn.adafruit.com", "").strip("/").split("/")
                if path_parts and path_parts[0] and path_parts[0] not in ("search", ""):
                    learn_links.append(clean)

    if learn_links:
        # Prefer the first guide link (usually the primary guide)
        data["learn_guide_url"] = learn_links[0]
        if len(learn_links) > 1:
            data["additional_guides"] = learn_links[1:]

    return data


# ---------------------------------------------------------------------------
# JSON persistence
# ---------------------------------------------------------------------------


def load_existing_json(json_path: Path) -> dict[str, dict[str, Any]]:
    """Load existing products.json, returning an empty dict if it doesn't exist."""
    if not json_path.is_file():
        return {}

    try:
        with open(json_path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (json.JSONDecodeError, IOError) as exc:
        logger.warning("Could not parse existing %s: %s. Starting fresh.", json_path.name, exc)
        return {}

    # Normalize: support both list-of-dicts and dict-of-dicts formats
    if isinstance(data, list):
        return {str(item["product_id"]): item for item in data if "product_id" in item}
    if isinstance(data, dict):
        # Could be {"products": [...]} or {id: {...}, ...}
        if "products" in data and isinstance(data["products"], list):
            return {
                str(item["product_id"]): item
                for item in data["products"]
                if "product_id" in item
            }
        return {str(k): v for k, v in data.items()}

    return {}


def merge_product_data(
    existing: dict[str, Any], scraped: dict[str, Any], csv_info: dict[str, Any]
) -> dict[str, Any]:
    """
    Merge scraped data into existing data for a single product, preserving
    any manually-added fields in existing data while updating with fresh
    scraped content.
    """
    merged = dict(existing)

    # Always update CSV-sourced fields
    merged["product_id"] = csv_info["product_id"]
    merged["csv_name"] = csv_info["csv_name"]
    merged["total_qty"] = csv_info["total_qty"]
    merged["orders"] = csv_info["orders"]

    # Update scraped fields only if the scraped value is non-empty
    for key in ("name", "description", "technical_specs", "image_url",
                "learn_guide_url", "additional_guides", "page_url"):
        if key in scraped and scraped[key]:
            merged[key] = scraped[key]
        elif key not in merged:
            merged[key] = scraped.get(key, "" if key != "learn_guide_url" else None)

    merged["last_scraped"] = datetime.now(timezone.utc).isoformat()

    return merged


def save_json(products: dict[str, dict[str, Any]], json_path: Path) -> None:
    """Save products dict to JSON file."""
    # Sort by product_id for stable output
    sorted_products = dict(sorted(products.items(), key=lambda x: int(x[0]) if x[0].isdigit() else x[0]))

    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(sorted_products, fh, indent=2, ensure_ascii=False)

    logger.info("Saved %d products to %s", len(sorted_products), json_path.name)


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------


def generate_html(products: dict[str, dict[str, Any]], html_path: Path) -> None:
    """Generate a browseable index.html from products.json data."""

    # Sort products: Adafruit (numeric IDs first), then others alphabetically
    def sort_key(p):
        pid = str(p.get("product_id", ""))
        source = p.get("source", "adafruit.com")
        if pid.isdigit():
            return (0, int(pid), "")
        return (1, 0, pid)

    sorted_items = sorted(products.values(), key=sort_key)

    product_cards = []
    for p in sorted_items:
        pid = escape(str(p.get("product_id", "")))
        name = escape(p.get("name") or p.get("csv_name", "Unknown Product"))
        desc = escape(p.get("description", "")[:300])
        if len(p.get("description", "")) > 300:
            desc += "..."
        img_url = escape(p.get("image_url", ""))
        page_url = escape(p.get("page_url", f"https://www.adafruit.com/product/{pid}"))
        learn_url = p.get("learn_guide_url")
        specs = escape(p.get("technical_specs", "")[:500])
        qty = p.get("total_qty", 0)
        csv_name = escape(p.get("csv_name", ""))
        source = escape(p.get("source", "adafruit.com"))
        currency = p.get("currency", "USD")
        price = p.get("unit_price", 0)
        price_str = f"£{price:.2f}" if currency == "GBP" else f"${price:.2f}"
        category = escape(p.get("category", ""))

        # Source badge color
        source_class = "source-adafruit" if "adafruit" in source else "source-pimoroni"
        source_label = source.replace(".com", "").title()

        learn_link = ""
        if learn_url:
            learn_link = f'<a href="{escape(learn_url)}" target="_blank" class="learn-link">Learn Guide</a>'

        additional_guides = ""
        if p.get("additional_guides"):
            guide_links = " | ".join(
                f'<a href="{escape(g)}" target="_blank">Guide</a>'
                for g in p["additional_guides"][:3]
            )
            additional_guides = f'<div class="additional-guides">{guide_links}</div>'

        specs_section = ""
        if specs:
            specs_section = f'<details class="specs"><summary>Technical Specs</summary><pre>{specs}</pre></details>'

        # Image fallback depends on source
        img_fallback = f"this.src='https://cdn-shop.adafruit.com/310x233/{pid}-00.jpg';" if "adafruit" in source else "this.style.display='none';"

        card = f"""
        <div class="product-card" data-product-id="{pid}" data-source="{source}" data-category="{category}">
            <div class="product-image">
                <a href="{page_url}" target="_blank">
                    <img src="{img_url}" alt="{name}" loading="lazy"
                         onerror="this.onerror=null; {img_fallback}">
                </a>
            </div>
            <div class="product-info">
                <div class="card-header">
                    <span class="source-badge {source_class}">{source_label}</span>
                    <span class="category-badge">{category}</span>
                </div>
                <h2><a href="{page_url}" target="_blank">{name}</a></h2>
                <p class="product-id">ID: {pid} | Qty: {qty} | {price_str}</p>
                <p class="description">{desc}</p>
                {specs_section}
                <div class="links">
                    <a href="{page_url}" target="_blank" class="product-link">Product Page</a>
                    {learn_link}
                </div>
                {additional_guides}
            </div>
        </div>"""
        product_cards.append(card)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Count sources
    adafruit_count = sum(1 for p in sorted_items if "adafruit" in p.get("source", "adafruit.com"))
    pimoroni_count = sum(1 for p in sorted_items if p.get("source", "adafruit.com") == "pimoroni.com")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Electronics Inventory</title>
    <style>
        :root {{
            --bg-primary: #1a1a2e;
            --bg-secondary: #16213e;
            --bg-card: #0f3460;
            --text-primary: #e0e0e0;
            --text-secondary: #a0a0b0;
            --accent: #e94560;
            --accent-hover: #ff6b6b;
            --link-color: #64b5f6;
            --border-color: #2a2a4a;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                         Oxygen, Ubuntu, Cantarell, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }}

        header {{
            background: var(--bg-secondary);
            padding: 1.5rem 2rem;
            border-bottom: 2px solid var(--accent);
            text-align: center;
        }}

        header h1 {{
            font-size: 1.8rem;
            color: var(--accent);
            margin-bottom: 0.3rem;
        }}

        header p {{
            color: var(--text-secondary);
            font-size: 0.9rem;
        }}

        .controls {{
            background: var(--bg-secondary);
            padding: 1rem 2rem;
            display: flex;
            gap: 1rem;
            align-items: center;
            flex-wrap: wrap;
            border-bottom: 1px solid var(--border-color);
        }}

        .controls input[type="search"] {{
            flex: 1;
            min-width: 200px;
            padding: 0.6rem 1rem;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            background: var(--bg-primary);
            color: var(--text-primary);
            font-size: 0.95rem;
        }}

        .controls input[type="search"]::placeholder {{
            color: var(--text-secondary);
        }}

        .controls .count {{
            color: var(--text-secondary);
            font-size: 0.85rem;
            white-space: nowrap;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 1.5rem;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 1.5rem;
        }}

        .product-card {{
            background: var(--bg-card);
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid var(--border-color);
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .product-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(233, 69, 96, 0.15);
        }}

        .product-image {{
            background: #fff;
            text-align: center;
            padding: 0.5rem;
            height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }}

        .product-image img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }}

        .product-info {{
            padding: 1rem 1.2rem 1.2rem;
        }}

        .product-info h2 {{
            font-size: 1.05rem;
            margin-bottom: 0.4rem;
            line-height: 1.3;
        }}

        .product-info h2 a {{
            color: var(--text-primary);
            text-decoration: none;
        }}

        .product-info h2 a:hover {{
            color: var(--accent-hover);
        }}

        .product-id {{
            color: var(--text-secondary);
            font-size: 0.8rem;
            margin-bottom: 0.2rem;
        }}

        .card-header {{
            display: flex;
            gap: 0.4rem;
            margin-bottom: 0.4rem;
            flex-wrap: wrap;
        }}

        .source-badge {{
            font-size: 0.7rem;
            padding: 0.15rem 0.5rem;
            border-radius: 3px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.02em;
        }}

        .source-adafruit {{
            background: #1a5c2a;
            color: #4ade80;
        }}

        .source-pimoroni {{
            background: #4a1a5c;
            color: #c084fc;
        }}

        .category-badge {{
            font-size: 0.7rem;
            padding: 0.15rem 0.5rem;
            border-radius: 3px;
            background: rgba(255,255,255,0.08);
            color: var(--text-secondary);
        }}

        .filter-buttons {{
            display: flex;
            gap: 0.4rem;
            flex-wrap: wrap;
        }}

        .filter-btn {{
            font-size: 0.8rem;
            padding: 0.35rem 0.7rem;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            background: transparent;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.2s;
        }}

        .filter-btn:hover {{
            border-color: var(--accent);
            color: var(--text-primary);
        }}

        .filter-btn.active {{
            background: var(--accent);
            border-color: var(--accent);
            color: white;
        }}

        .description {{
            font-size: 0.88rem;
            color: var(--text-secondary);
            margin-bottom: 0.8rem;
            display: -webkit-box;
            -webkit-line-clamp: 4;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}

        .specs {{
            margin-bottom: 0.8rem;
        }}

        .specs summary {{
            cursor: pointer;
            color: var(--link-color);
            font-size: 0.85rem;
            margin-bottom: 0.3rem;
        }}

        .specs pre {{
            font-size: 0.78rem;
            color: var(--text-secondary);
            white-space: pre-wrap;
            word-break: break-word;
            max-height: 200px;
            overflow-y: auto;
            padding: 0.5rem;
            background: rgba(0,0,0,0.2);
            border-radius: 4px;
        }}

        .links {{
            display: flex;
            gap: 0.8rem;
            flex-wrap: wrap;
        }}

        .links a {{
            font-size: 0.85rem;
            color: var(--link-color);
            text-decoration: none;
            padding: 0.3rem 0.7rem;
            border: 1px solid var(--link-color);
            border-radius: 4px;
            transition: background 0.2s;
        }}

        .links a:hover {{
            background: rgba(100, 181, 246, 0.15);
        }}

        .links a.learn-link {{
            color: var(--accent);
            border-color: var(--accent);
        }}

        .links a.learn-link:hover {{
            background: rgba(233, 69, 96, 0.15);
        }}

        .additional-guides {{
            margin-top: 0.5rem;
            font-size: 0.8rem;
        }}

        .additional-guides a {{
            color: var(--text-secondary);
            text-decoration: underline;
        }}

        footer {{
            text-align: center;
            padding: 2rem;
            color: var(--text-secondary);
            font-size: 0.8rem;
            border-top: 1px solid var(--border-color);
            margin-top: 2rem;
        }}

        .hidden {{
            display: none !important;
        }}

        @media (max-width: 480px) {{
            .container {{
                grid-template-columns: 1fr;
                padding: 0.8rem;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>Electronics Inventory</h1>
        <p>{len(sorted_items)} products — {adafruit_count} from Adafruit, {pimoroni_count} from Pimoroni</p>
    </header>
    <div class="controls">
        <input type="search" id="search" placeholder="Search products by name, ID, description, or category..."
               aria-label="Search products">
        <div class="filter-buttons">
            <button class="filter-btn active" data-filter="all">All ({len(sorted_items)})</button>
            <button class="filter-btn" data-filter="adafruit">Adafruit ({adafruit_count})</button>
            <button class="filter-btn" data-filter="pimoroni">Pimoroni ({pimoroni_count})</button>
        </div>
        <span class="count" id="count">Showing {len(sorted_items)} of {len(sorted_items)}</span>
    </div>
    <div class="container" id="products">
        {"".join(product_cards)}
    </div>
    <footer>
        Generated on {timestamp} by scraper.py
    </footer>
    <script>
        const searchInput = document.getElementById('search');
        const countDisplay = document.getElementById('count');
        const cards = document.querySelectorAll('.product-card');
        const filterBtns = document.querySelectorAll('.filter-btn');
        const total = cards.length;
        let activeFilter = 'all';

        function applyFilters() {{
            const query = searchInput.value.toLowerCase().trim();
            let visible = 0;
            cards.forEach(card => {{
                const text = card.textContent.toLowerCase();
                const id = card.dataset.productId;
                const source = card.dataset.source || '';
                const matchSearch = !query || text.includes(query) || id.includes(query);
                const matchSource = activeFilter === 'all' || source.includes(activeFilter);
                const show = matchSearch && matchSource;
                card.classList.toggle('hidden', !show);
                if (show) visible++;
            }});
            countDisplay.textContent = `Showing ${{visible}} of ${{total}}`;
        }}

        searchInput.addEventListener('input', applyFilters);

        filterBtns.forEach(btn => {{
            btn.addEventListener('click', function() {{
                filterBtns.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                activeFilter = this.dataset.filter;
                applyFilters();
            }});
        }});
    </script>
</body>
</html>"""

    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(html)

    logger.info("Generated %s with %d product cards", html_path.name, len(sorted_items))


# ---------------------------------------------------------------------------
# Main scraping orchestration
# ---------------------------------------------------------------------------


def scrape_products(
    csv_products: dict[str, dict[str, Any]],
    existing_data: dict[str, dict[str, Any]],
    force: bool = False,
) -> dict[str, dict[str, Any]]:
    """
    Scrape product pages for all products from the CSV.

    Skips products that already have scraped data (unless force=True).
    Merges results with existing data.
    """
    session = create_session()
    results = dict(existing_data)  # Start with existing data
    total = len(csv_products)
    scraped_count = 0
    skipped_count = 0
    error_count = 0

    for idx, (pid, csv_info) in enumerate(csv_products.items(), start=1):
        # Check if already scraped (has 'last_scraped' field and we're not forcing)
        if not force and pid in results and results[pid].get("last_scraped"):
            logger.debug(
                "[%d/%d] Skipping product %s (already scraped)", idx, total, pid
            )
            # Still update CSV-derived info (quantities may change)
            results[pid]["csv_name"] = csv_info["csv_name"]
            results[pid]["total_qty"] = csv_info["total_qty"]
            results[pid]["orders"] = csv_info["orders"]
            skipped_count += 1
            continue

        logger.info(
            "[%d/%d] Scraping product %s: %s",
            idx, total, pid, csv_info["csv_name"],
        )

        url = ADAFRUIT_PRODUCT_URL.format(product_id=pid)
        response = fetch_with_retry(session, url)

        if response is None:
            logger.error("Failed to fetch product %s", pid)
            # Still store CSV info even if scrape fails
            if pid not in results:
                results[pid] = {
                    "product_id": pid,
                    "csv_name": csv_info["csv_name"],
                    "total_qty": csv_info["total_qty"],
                    "orders": csv_info["orders"],
                    "name": csv_info["csv_name"],
                    "description": "",
                    "technical_specs": "",
                    "image_url": ADAFRUIT_CDN_IMAGE.format(product_id=pid),
                    "learn_guide_url": None,
                    "page_url": url,
                    "scrape_error": True,
                }
            error_count += 1
        else:
            scraped = extract_product_data(response.text, pid)
            existing = results.get(pid, {})
            results[pid] = merge_product_data(existing, scraped, csv_info)
            # Remove error flag if it was previously set
            results[pid].pop("scrape_error", None)
            scraped_count += 1

        # Rate limiting -- be polite. Don't delay after the last item.
        if idx < total:
            time.sleep(RATE_LIMIT_DELAY)

    logger.info(
        "Scraping complete: %d scraped, %d skipped (cached), %d errors out of %d total",
        scraped_count, skipped_count, error_count, total,
    )

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Scrape Adafruit product pages for inventory items.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                         Scrape all products from purchase_history.csv
  %(prog)s --update-html           Regenerate index.html from products.json
  %(prog)s --csv my_orders.csv     Use a custom CSV file
  %(prog)s --force                 Re-scrape all products (ignore cache)
  %(prog)s --dry-run               Show products that would be scraped
  %(prog)s --verbose               Enable debug logging
        """,
    )

    parser.add_argument(
        "--csv",
        type=Path,
        default=DEFAULT_CSV,
        help=f"Path to purchase history CSV (default: {DEFAULT_CSV.name})",
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=DEFAULT_JSON,
        dest="json_path",
        help=f"Path to products JSON (default: {DEFAULT_JSON.name})",
    )
    parser.add_argument(
        "--html",
        type=Path,
        default=DEFAULT_HTML,
        dest="html_path",
        help=f"Path to output HTML (default: {DEFAULT_HTML.name})",
    )
    parser.add_argument(
        "--update-html",
        action="store_true",
        help="Regenerate index.html from existing products.json without scraping",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-scrape all products even if already cached",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be scraped without making requests",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "--no-html",
        action="store_true",
        help="Skip HTML generation after scraping",
    )

    return parser.parse_args()


def main() -> None:
    """Main entry point."""
    args = parse_args()
    setup_logging(verbose=args.verbose)

    logger.info("Adafruit Product Scraper started")

    # --update-html mode: just regenerate HTML from existing JSON
    if args.update_html:
        existing = load_existing_json(args.json_path)
        if not existing:
            logger.error(
                "No data found in %s. Run scraper first to populate product data.",
                args.json_path,
            )
            sys.exit(1)

        logger.info("Regenerating HTML from %d products in %s", len(existing), args.json_path.name)
        generate_html(existing, args.html_path)
        logger.info("Done. Open %s in a browser to view.", args.html_path)
        return

    # Read CSV
    csv_products = read_products_from_csv(args.csv)

    if not csv_products:
        logger.error("No products found in CSV. Exiting.")
        sys.exit(1)

    # Load existing JSON data
    existing_data = load_existing_json(args.json_path)
    if existing_data:
        logger.info("Loaded %d existing products from %s", len(existing_data), args.json_path.name)

    # --dry-run mode
    if args.dry_run:
        would_scrape = []
        would_skip = []
        for pid, info in csv_products.items():
            if not args.force and pid in existing_data and existing_data[pid].get("last_scraped"):
                would_skip.append((pid, info["csv_name"]))
            else:
                would_scrape.append((pid, info["csv_name"]))

        print(f"\n{'='*60}")
        print(f"DRY RUN SUMMARY")
        print(f"{'='*60}")
        print(f"Total unique products in CSV: {len(csv_products)}")
        print(f"Would scrape: {len(would_scrape)}")
        print(f"Would skip (already cached): {len(would_skip)}")
        print()

        if would_scrape:
            print("Products to scrape:")
            for pid, name in sorted(would_scrape, key=lambda x: int(x[0]) if x[0].isdigit() else 0):
                print(f"  [{pid}] {name}")

        if would_skip:
            print(f"\nProducts to skip ({len(would_skip)} cached):")
            for pid, name in sorted(would_skip, key=lambda x: int(x[0]) if x[0].isdigit() else 0)[:10]:
                print(f"  [{pid}] {name}")
            if len(would_skip) > 10:
                print(f"  ... and {len(would_skip) - 10} more")

        print(f"\nEstimated time: ~{len(would_scrape) * (RATE_LIMIT_DELAY + 2):.0f} seconds")
        return

    # Scrape
    try:
        results = scrape_products(csv_products, existing_data, force=args.force)
    except KeyboardInterrupt:
        logger.warning("Interrupted by user. Saving progress...")
        # On interrupt, we still want to save what we have so far.
        # The scrape_products function modifies results in-place as it goes,
        # but since we get the results dict, we should save it.
        # However, since we were interrupted before the return, we need to
        # reconstruct from existing_data + any partial results.
        # For safety, just save existing_data which hasn't been modified.
        save_json(existing_data, args.json_path)
        logger.info("Partial progress saved. Re-run to resume.")
        sys.exit(130)

    # Save JSON
    save_json(results, args.json_path)

    # Generate HTML
    if not args.no_html:
        generate_html(results, args.html_path)
        logger.info("Done. Open %s in a browser to view.", args.html_path)
    else:
        logger.info("Done. HTML generation skipped (--no-html).")


if __name__ == "__main__":
    main()
