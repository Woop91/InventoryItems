#!/usr/bin/env python3
"""Mark the parts Wardis is currently using, with their own photos.

Source data: data/parts_in_use.json, a list of entries:
  {"key": "<products.json key>", "photos": ["IMG_5881.jpg", ...]}
or, for a part not yet in the inventory, a new product:
  {"key": null, "name": ..., "category": ..., "description": ...,
   "technical_specs": ..., "brand": ..., "model": ..., "photos": [...]}

Photos live in images/my-photos/. Every product listed here gets
in_use = true and my_photos; every other product has in_use cleared, so this
file is the single list of what is in use. Safe to re-run.

Usage:
    python mark_in_use.py && python build_catalog.py --readme
"""
import json
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DATA = SCRIPT_DIR / "data" / "parts_in_use.json"
PRODUCTS = SCRIPT_DIR / "products.json"
PHOTO_DIR = "images/my-photos"


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


def main() -> None:
    products = json.loads(PRODUCTS.read_text(encoding="utf-8"))
    entries = json.loads(DATA.read_text(encoding="utf-8"))
    for p in products.values():
        p.pop("in_use", None)
        p.pop("my_photos", None)
    added = 0
    for e in entries:
        photos = [f"{PHOTO_DIR}/{name}" for name in e.get("photos", [])]
        key = e.get("key")
        if key is None:
            key = f"photo_{slug(e['name'])}"
            first = photos[0] if photos else None
            products[key] = {
                "product_id": slug(e["name"]),
                "name": e["name"],
                "csv_name": e["name"],
                "description": e.get("description") or "",
                "technical_specs": e.get("technical_specs") or "",
                "category": e.get("category") or "Component",
                "page_url": e.get("page_url"),
                "image_url": first,
                "learn_guide_url": e.get("learn_guide_url"),
                "unit_price": 0,
                "brand": e.get("brand"),
                "model": e.get("model"),
                "total_qty": 1,
                "orders": [],
                "source": "unrecorded",
                "last_scraped": None,
            }
            added += 1
        elif key not in products:
            raise SystemExit(f"unknown product key in {DATA.name}: {key}")
        products[key]["in_use"] = True
        products[key]["my_photos"] = photos
    PRODUCTS.write_text(json.dumps(products, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Marked {len(entries)} parts in use ({added} new to the inventory); products.json has {len(products)}")


if __name__ == "__main__":
    main()
