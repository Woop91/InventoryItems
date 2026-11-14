#!/usr/bin/env python3
"""Build index.html, a browsable catalog of products.json.

The page groups products by category (or by store), with search, sorting,
store and category filters, and a picture for every product. Product data is
embedded in the page so it works when opened straight from disk.

Usage:
    python build_catalog.py                  # products.json -> index.html
    python build_catalog.py --json X --html Y
"""
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

SCRIPT_DIR = Path(__file__).resolve().parent

CURRENCY = {"USD": "$", "GBP": "£", "EUR": "€"}

STORE_NAMES = {
    "adafruit.com": "Adafruit",
    "aliexpress.com": "AliExpress",
    "pimoroni.com": "Pimoroni",
    "waveshare.com": "Waveshare",
    "sparkfun.com": "SparkFun",
    "mouser.com": "Mouser",
    "amazon.com": "Amazon",
    "orbtronic.com": "Orbtronic",
    "batteryjunction.com": "Battery Junction",
    "voltaplex.com": "Voltaplex",
    "homedepot.com": "Home Depot",
}


def store_of(p: dict) -> str:
    """Return a display store name for a product."""
    src = p.get("source")
    if not src:
        host = urlparse(p.get("page_url") or "").netloc.lower()
        src = host[4:] if host.startswith("www.") else host
        src = src or "adafruit.com"
    return STORE_NAMES.get(src, src)


def slim(key: str, p: dict) -> dict:
    """Keep only the fields the page uses."""
    return {
        "id": key,
        "name": p.get("name") or p.get("csv_name") or key,
        "desc": p.get("description") or "",
        "specs": p.get("technical_specs") or "",
        "cat": p.get("category") or "Uncategorized",
        "store": store_of(p),
        "img": p.get("image_url") or "",
        "url": p.get("page_url") or "",
        "guide": p.get("learn_guide_url") or "",
        "price": p.get("unit_price") or 0,
        "cur": CURRENCY.get(p.get("currency") or "USD", "$"),
        "unit": p.get("price_unit") or "",
        "qty": p.get("total_qty") or 0,
        "pack": p.get("pack") or "",
        "pdf": p.get("source_pdf") or "",
    }


def build(products: dict, html_path: Path) -> None:
    items = [slim(k, v) for k, v in products.items()]
    data = json.dumps(items, ensure_ascii=False).replace("</", "<\\/")
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    template = (SCRIPT_DIR / "catalog_template.html").read_text(encoding="utf-8")
    html = template.replace("/*__DATA__*/[]", data).replace("__GENERATED__", stamp)
    html_path.write_text(html, encoding="utf-8")
    print(f"Wrote {html_path} with {len(items)} products")


# README table order; categories not listed here follow in A-Z order.
CATEGORY_ORDER = [
    "Microcontroller", "Sensor", "Display", "LED", "Breakout Board", "FeatherWing",
    "Motor/Actuator", "Motor Driver/ESC", "Switch/Button", "Audio", "Wireless/RF",
    "Component", "Cable/Connector", "Prototyping", "Power", "Battery", "Kit", "Tool",
    "Enclosure", "Storage", "Accessory", "Book/Subscription",
]


def anchor(text: str) -> str:
    """GitHub heading anchor."""
    return re.sub(r"[^a-z0-9 -]", "", text.lower()).replace(" ", "-")


def readme_section(products: dict) -> str:
    """Markdown 'Categories by Source' index plus one table per store and category."""
    stores: dict[str, dict[str, list]] = {}
    for p in products.values():
        stores.setdefault(store_of(p), {}).setdefault(p.get("category") or "Uncategorized", []).append(p)
    rank = {c: i for i, c in enumerate(CATEGORY_ORDER)}
    for store in stores:
        stores[store] = dict(sorted(stores[store].items(), key=lambda kv: (rank.get(kv[0], len(rank)), kv[0])))
    out = ["## Categories by Source", ""]
    for store, cats in stores.items():
        out += [f"### {store} ({sum(map(len, cats.values()))} products)", ""]
        out += [f"- [{c}](#{anchor(f'{store} - {c}')}) ({len(ps)})" for c, ps in cats.items()]
        out.append("")
    out += ["---", ""]
    for store, cats in stores.items():
        out += [f"# {store} Products", ""]
        for cat, ps in cats.items():
            out += [f"## {store} - {cat}", "", "| ID | Product | Qty | Price | Links |",
                    "|------|---------|----:|------:|-------|"]
            for p in sorted(ps, key=lambda p: str(p["product_id"])):
                name = p["name"] if p.get("source_pdf") else p.get("csv_name") or p["name"]
                price = f"{CURRENCY.get(p.get('currency') or 'USD', '$')}{p['unit_price']:.2f}" if p.get("unit_price") else "—"
                links = [f"[Product]({p['page_url']})"] if p.get("page_url") else []
                if p.get("learn_guide_url"):
                    links.append(f"[Guide]({p['learn_guide_url']})")
                out.append(f"| {p['product_id']} | {name.replace('|', '/')} | {p.get('total_qty') or 1} | {price} | {' · '.join(links)} |")
            out.append("")
        out += ["---", ""]
    return "\n".join(out).rstrip("-\n") + "\n"


def update_readme(products: dict, readme: Path) -> None:
    text = readme.read_text(encoding="utf-8")
    head = text.split("## Categories by Source", 1)[0]
    readme.write_text(head + readme_section(products), encoding="utf-8")
    print(f"Updated product tables in {readme}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", type=Path, default=SCRIPT_DIR / "products.json")
    ap.add_argument("--html", type=Path, default=SCRIPT_DIR / "index.html")
    ap.add_argument("--readme", action="store_true", help="also regenerate the product tables in README.md")
    args = ap.parse_args()
    products = json.loads(args.json.read_text(encoding="utf-8"))
    build(products, args.html)
    if args.readme:
        update_readme(products, SCRIPT_DIR / "README.md")


if __name__ == "__main__":
    main()
