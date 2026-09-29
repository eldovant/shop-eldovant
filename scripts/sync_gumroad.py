#!/usr/bin/env python3
"""Build a public ELDOVANT catalogue from Gumroad seller products, for GitHub Pages.

The API token is read only from the environment; it is never written into HTML/JS.
Only a whitelisted subset of non-personal, customer-facing product data is exported.
A failed API request aborts the deploy rather than replacing the live shop with an empty list.
"""

from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

API = "https://api.gumroad.com/v2/products"


class PlainHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.result = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        elif not self.skip and tag in ("p", "br", "div", "li", "h1", "h2", "h3"):
            self.result.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1
        elif not self.skip and tag in ("p", "div", "li"):
            self.result.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.result.append(data)


def plaintext(value):
    if not value:
        return ""
    parser = PlainHTML()
    parser.feed(str(value))
    result = "".join(parser.result).replace("\xa0", " ")
    result = re.sub(r"[ \t]+", " ", result)
    result = re.sub(r"\n\s*\n\s*\n+", "\n\n", result)
    return result.strip()


def https_url(value):
    if not isinstance(value, str):
        return ""
    value = value.strip()
    parsed = urlparse(value)
    return value if parsed.scheme == "https" and parsed.netloc and not parsed.username else ""


def product_cover(product):
    direct = https_url(product.get("thumbnail_url"))
    if direct:
        return direct
    for cover in product.get("covers") or []:
        if isinstance(cover, str):
            candidate = cover
        elif isinstance(cover, dict):
            candidate = cover.get("url") or cover.get("original_url") or cover.get("large_url")
        else:
            continue
        candidate = https_url(candidate)
        if candidate:
            return candidate
    return ""


def allowed(product, required_tag="", excluded_ids=None):
    if not isinstance(product, dict):
        return False
    if str(product.get("id", "")) in (excluded_ids or set()):
        return False
    if product.get("published") is not True:
        return False
    if product.get("deleted") or product.get("archived") or product.get("is_archived"):
        return False
    if product.get("require_shipping") is True:
        return False
    # These visibility fields are not present in every Gumroad API response.
    if product.get("is_unlisted") is True or product.get("unlisted") is True:
        return False
    if product.get("is_hidden") is True or product.get("hidden") is True:
        return False
    if product.get("show_on_profile") is False:
        return False
    if str(product.get("visibility") or "").lower() in ("unlisted", "private", "hidden"):
        return False
    tags = product.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    tags = [str(tag).strip().lower() for tag in tags]
    if "eldovant-hide" in tags or "private" in tags:
        return False
    if required_tag and required_tag.lower() not in tags:
        return False
    if not https_url(product.get("short_url")):
        return False
    return True


def price_object(product):
    if product.get("customizable_price") or product.get("is_tiered_membership"):
        # Exact amounts differ by variant or buyer choice; Gumroad checkout is authoritative.
        return None
    cents = product.get("price")
    currency = str(product.get("currency") or "").upper()
    if cents is None or not re.fullmatch(r"[A-Z]{3}", currency):
        return None
    try:
        amount = Decimal(str(cents)) / Decimal("100")
        if amount < 0:
            return None
        return {"amount": float(amount), "currency": currency}
    except (InvalidOperation, TypeError, ValueError):
        return None


def transform_products(raw_products, required_tag="", excluded_ids=None):
    result = []
    seen = set()
    for product in raw_products:
        if not allowed(product, required_tag, excluded_ids):
            continue
        identifier = str(product["id"])
        if identifier in seen:
            continue
        seen.add(identifier)
        description = plaintext(product.get("description"))[:5000]
        summary = plaintext(product.get("custom_summary")) or description
        summary = summary[:197].rstrip() + "…" if len(summary) > 200 else summary
        tags = product.get("tags") or []
        if isinstance(tags, str):
            tags = [tag.strip() for tag in tags.split(",")]
        category = next((str(tag) for tag in tags if tag and str(tag).lower() not in ("eldovant-shop", "eldovant-hide", "private")), "Digital editions")
        item = {
            "id": identifier,
            "title": plaintext(product.get("name"))[:200] or "ELDOVANT Digital Edition",
            "summary": summary,
            "description": description,
            "category": category,
            "kind": "Digital release",
            "status": "available",
            "checkoutUrl": https_url(product["short_url"]),
            "cover": product_cover(product),
            "delivery": "Delivered digitally through Gumroad",
        }
        price = price_object(product)
        if price is not None:
            item["price"] = price
        result.append(item)
    if result:
        result[0]["featured"] = True
    return result


def fetch_products(token):
    all_products = []
    next_key = ""
    page_keys_seen = set()
    for _ in range(100):
        url = API + (("?" + urlencode({"page_key": next_key})) if next_key else "")
        request = Request(url, headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/json",
            "User-Agent": "ELDOVANT-Shop-Catalogue-Sync/1.0"
        })
        with urlopen(request, timeout=30) as reply:
            payload = json.load(reply)
        if not isinstance(payload, dict) or payload.get("success") is not True or not isinstance(payload.get("products"), list):
            raise RuntimeError("Gumroad API returned an unsuccessful or invalid product response.")
        all_products.extend(payload["products"])
        next_key = payload.get("next_page_key") or ""
        if not next_key:
            return all_products
        if next_key in page_keys_seen:
            raise RuntimeError("Gumroad API repeated a pagination cursor.")
        page_keys_seen.add(next_key)
    raise RuntimeError("Gumroad API product pagination exceeded the safety limit.")


def build_site(project_root, destination, products):
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    for filename in ("index.html", ".nojekyll"):
        file = project_root / filename
        if file.is_file():
            shutil.copy2(file, destination / filename)
    assets = project_root / "assets"
    if assets.is_dir():
        shutil.copytree(assets, destination / "assets")
    data = {
        "entity": "ELDOVANT",
        "contact": {"email": "contact@eldovant.com"},
        "shop": {
            "enabled": True,
            "provider": "Gumroad",
            "supportEmail": "contact@eldovant.com",
            "delivery": {
                "method": "Digital delivery through Gumroad",
                "after": "Gumroad sends the purchase confirmation and the download or access details to the email you used at checkout."
            },
            "products": products
        }
    }
    js_json = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    js_json = js_json.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    (destination / "eldovant-data.js").write_text("/* Generated from Gumroad API. DO NOT EDIT. */\nwindow.ELDOVANT_DATA = " + js_json + ";\n", encoding="utf-8")
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, help="Use a local API response for offline tests only. Do not use in production.")
    parser.add_argument("--output", type=Path, default=Path("build/site"))
    args = parser.parse_args()
    project_root = Path(__file__).resolve().parents[1]
    if args.fixture:
        data = json.loads(args.fixture.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            if data.get("success") is not True:
                raise SystemExit("Test fixture must contain success=true.")
            raw = data.get("products", [])
        else:
            raw = data
    else:
        token = os.environ.get("GUMROAD_ACCESS_TOKEN", "").strip()
        if not token:
            raise SystemExit("GUMROAD_ACCESS_TOKEN is missing. Add it as a GitHub Actions repository secret.")
        try:
            raw = fetch_products(token)
        except Exception as exc:
            raise SystemExit("Catalogue fetch failed. The currently deployed site was not changed. " + type(exc).__name__) from None
    if not isinstance(raw, list):
        raise SystemExit("Product payload has an invalid shape.")
    excluded = set(x.strip() for x in os.environ.get("GUMROAD_EXCLUDE_IDS", "").split(",") if x.strip())
    tag = os.environ.get("SHOP_REQUIRED_TAG", "").strip()
    products = transform_products(raw, tag, excluded)
    build_site(project_root, args.output, products)
    print(f"ELDOVANT catalogue ready: {len(products)} eligible public digital products.")
    print(f"Generated deployment files at: {args.output}")


if __name__ == "__main__":
    main()
