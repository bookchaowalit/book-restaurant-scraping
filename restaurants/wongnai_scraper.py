#!/usr/bin/env python3
"""
Wongnai scraper — extracts restaurant/business data from window._wn JSON.
Wongnai embeds a full Redux store in the page that we parse directly.

MCP Tool: get_restaurant_reviews
Data: name, rating, address, phone, categories, price range, location, URL
"""

import asyncio
import csv
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import httpx
from adapters.outbound.engines.base import BaseScraper

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parent.parent.parent / "data"

# Location keys for different areas
LOCATION_KEYS = {
    "bangkok": "1",
    "chiangmai": "4",
    "phuket": "7",
    "pattaya": "5",
    "khonkaen": "6",
    "hua_hin": "10",
    "ayutthaya": "3",
    "korat": "8",
}

DEFAULT_LOCATIONS = ["bangkok", "chiangmai", "phuket", "pattaya"]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "th-TH,th;q=0.9,en-US;q=0.8,en;q=0.8",
}


def extract_wn_data(html: str) -> Optional[dict]:
    """Extract window._wn JSON from HTML."""
    m = re.search(r'window\._wn\s*=\s*({.*?});?\s*</script>', html, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


def parse_business(item: dict) -> dict:
    """Parse a business item from Wongnai's Redux store."""
    biz = item.get("business", {})
    if not biz:
        return {}

    contact = biz.get("contact", {}) or {}
    stats = biz.get("statistic", {}) or {}
    categories = biz.get("categories", []) or []
    neighborhoods = biz.get("neighborhoods", []) or []
    price_range = biz.get("priceRange", {}) or {}

    # Extract category names
    cat_names = [c.get("name", "") for c in categories if c.get("name")]
    cat_intl = [c.get("internationalName", "") for c in categories if c.get("internationalName")]

    # Extract neighborhood
    hood = ""
    if neighborhoods:
        n = neighborhoods[0]
        if isinstance(n, dict):
            hood = n.get("name", "")
        elif isinstance(n, str):
            hood = n

    return {
        "name": biz.get("displayName") or biz.get("name", ""),
        "rating": biz.get("rating", 0),
        "num_reviews": stats.get("numberOfReviews", 0),
        "num_bookmarks": stats.get("numberOfBookmarks", 0),
        "address": contact.get("address", ""),
        "phone": contact.get("phone", ""),
        "email": contact.get("email", ""),
        "website": contact.get("homepage", ""),
        "categories_th": ", ".join(cat_names),
        "categories_en": ", ".join(cat_intl),
        "neighborhood": hood,
        "price_range": price_range.get("name", ""),
        "lat": biz.get("lat"),
        "lng": biz.get("lng"),
        "zipcode": biz.get("zipcode", ""),
        "url": f"https://www.wongnai.com/{biz.get('url', '')}",
        "featured": biz.get("featured", False),
        "official": biz.get("official", False),
    }


def build_url(location_key: str, page: int = 1) -> str:
    """Build Wongnai URL with location and pagination."""
    base = f"https://www.wongnai.com/restaurants?locationKey={location_key}"
    if page > 1:
        base += f"&page={page}"
    return base


class WongnaiScraper(BaseScraper):
    """Scrape restaurant/business listings from Wongnai using embedded JSON."""

    def __init__(self, **kwargs):
        super().__init__(
            name="wongnai",
            rate_limit=kwargs.get("rate_limit", 4.0),
            max_retries=3,
            timeout=30.0,
        )
        self.locations = kwargs.get("locations", DEFAULT_LOCATIONS)
        self.max_pages = kwargs.get("max_pages", 3)

    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch a page with retries."""
        await self._wait_for_rate_limit()
        self.stats["requests"] += 1

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                    resp = await client.get(url, headers=HEADERS)
                    if resp.status_code >= 400:
                        logger.warning(f"[HTTP {resp.status_code}] {url}")
                        continue
                    self.stats["misses"] += 1
                    return resp.text
            except Exception as e:
                logger.error(f"[ERROR] {url}: {e} (attempt {attempt+1})")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)

        self.stats["errors"] += 1
        return None

    def parse_page(self, html: str) -> List[dict]:
        """Extract businesses from window._wn JSON."""
        data = extract_wn_data(html)
        if not data:
            return []

        store = data.get("store", {})
        sr = store.get("searchResult", {})
        value = sr.get("value", {})
        items = value.get("data", [])

        results = []
        for item in items:
            biz = parse_business(item)
            if biz.get("name"):
                results.append(biz)

        return results

    async def scrape_location(self, location_name: str, max_pages: int = 3):
        """Scrape all pages for a location."""
        loc_key = LOCATION_KEYS.get(location_name, "1")
        all_items = []

        for page in range(1, max_pages + 1):
            url = build_url(loc_key, page)
            logger.info(f"Scraping Wongnai: {location_name} page {page}")

            html = await self.fetch_page(url)
            if not html:
                break

            items = self.parse_page(html)
            if not items:
                break

            all_items.extend(items)
            logger.info(f"  Page {page}: {len(items)} businesses")

            # Check if there's a next page
            data = extract_wn_data(html)
            if data:
                next_page = data.get("store", {}).get("searchResult", {}).get("value", {}).get("next")
                if not next_page:
                    break

        for item in all_items:
            item["location_search"] = location_name
            self.add_result(item)

        return len(all_items)

    async def run(self, locations: list = None, max_pages: int = None, **kwargs):
        """Run scraper for all locations."""
        locations = locations or self.locations
        max_pages = max_pages or self.max_pages

        total = 0
        for loc in locations:
            count = await self.scrape_location(loc, max_pages)
            total += count
            logger.info(f"  {loc}: {count} businesses total")

        self.print_stats()
        self.export_csv("wongnai_businesses.csv")
        self.export_json("wongnai_businesses.json")

        # Also save to data/ directory for dashboard
        if self.results:
            save_results(self.results, OUTPUT_DIR)

        return self.results


def save_results(results: list, output_dir: Path):
    """Save results to data/ directory."""
    output_dir.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "name", "rating", "num_reviews", "num_bookmarks", "address", "phone",
        "categories_th", "categories_en", "neighborhood", "price_range",
        "lat", "lng", "zipcode", "url", "featured", "official", "location_search",
    ]

    # Current snapshot
    csv_path = output_dir / "wongnai_businesses.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    # History append
    history_path = output_dir / "wongnai_history.csv"
    file_exists = history_path.exists()
    with open(history_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames + ["scraped_at"], extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        now = datetime.now().isoformat()
        for r in results:
            row = {**r, "scraped_at": now}
            writer.writerow(row)

    logger.info(f"Saved {len(results)} businesses to {csv_path}")


async def main():
    scraper = WongnaiScraper()
    results = await scraper.run()
    print(f"\nTotal businesses scraped: {len(results)}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
