#!/usr/bin/env python3
"""Merge products from saved purchase PDFs (mostly AliExpress order snapshots)
into products.json.

Source data: data/purchase_pdfs.json, one record per product, extracted from the
"Electronic data" PDF folder. Pictures were pulled from each PDF into
images/purchases/. Running this again is safe: entries are keyed by slug and
replaced in place.

Usage:
    python add_purchase_pdfs.py && python build_catalog.py
"""
import json
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DATA = SCRIPT_DIR / "data" / "purchase_pdfs.json"
PRODUCTS = SCRIPT_DIR / "products.json"
IMAGE_DIR = "images/purchases"


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


def main() -> None:
    products = json.loads(PRODUCTS.read_text(encoding="utf-8"))
    records = json.loads(DATA.read_text(encoding="utf-8"))
    added = 0
    for r in records:
        site = r.get("store_site") or "aliexpress.com"
        prefix = site.split(".")[0]
        key = f"{prefix}_{slug(r['name'])}"
        products[key] = {
            "product_id": slug(r["name"]),
            "name": r["name"],
            "csv_name": r.get("csv_name") or r["name"],
            "description": r.get("description") or "",
            "technical_specs": r.get("technical_specs") or "",
            "category": r.get("category") or "Component",
            "page_url": r.get("page_url"),
            "image_url": f"{IMAGE_DIR}/{r['image']}" if r.get("image") else None,
            "learn_guide_url": None,
            "unit_price": r.get("unit_price") or 0,
            "price_unit": r.get("price_unit"),
            "pack": r.get("pack"),
            "brand": r.get("brand"),
            "model": r.get("model"),
            "currency": "USD",
            "total_qty": r.get("qty") or 1,
            "orders": [prefix],
            "source": site,
            "source_pdf": r["source_pdf"],
            "last_scraped": None,
        }
        added += 1
    PRODUCTS.write_text(json.dumps(products, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Merged {added} purchase-PDF products; products.json now has {len(products)}")


if __name__ == "__main__":
    main()
