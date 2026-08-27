#!/usr/bin/env python3
"""Run the bounded Wongnai adapters owned by this repository."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from restaurants.wongnai_scraper import WongnaiScraper

JOBS = (
    {
        "name": "wongnai_bangkok",
        "locations": ["bangkok"],
        "output_stem": "wongnai_bangkok",
        "source_url": "https://www.wongnai.com/restaurants?locationKey=1",
    },
    {
        "name": "wongnai_upcountry",
        "locations": ["khonkaen", "korat", "pattaya"],
        "output_stem": "wongnai_upcountry",
        "source_url": "https://www.wongnai.com/restaurants?locationKey=6",
    },
)


async def run_restaurants(
    output_dir: Path,
    max_pages: int = 3,
    min_rows: int = 20,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for job in JOBS:
        scraper = WongnaiScraper(
            locations=job["locations"],
            page_size=100,
            min_rows=min_rows,
            output_stem=job["output_stem"],
            source_url=job["source_url"],
            output_dir=output_dir,
        )
        batch = await scraper.run(max_pages=max_pages)
        results.extend(batch)
        print(f"[run_restaurants] {job['name']}: {batch[0].get('count') if batch else 0}")
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Run book-restaurant-scraping Wongnai jobs")
    parser.add_argument("--max-pages", type=int, default=3)
    parser.add_argument("--min-rows", type=int, default=20)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data" / "exported")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    results = asyncio.run(run_restaurants(args.output_dir, args.max_pages, args.min_rows))
    if args.json:
        print(json.dumps(results, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
