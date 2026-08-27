# book-restaurant-scraping

**Tier:** C / tool prototype (portfolio breadth, not interview flagship)  
**Owner path:** `bookchaowalit/book-apps/tools/book-restaurant-scraping`

## Purpose

Restaurant listing scrape prototype (Wongnai-style module).

## Entry points

- `restaurants/wongnai_scraper.py`

## Stack

Python

## How to run (local)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 scripts/run_restaurants.py --max-pages 3 --min-rows 20
bash setup_cron.sh install   # optional; weekly Sunday 00:15
```

Output stays in this repository's `data/exported/`.

## Boundaries

- **Not** a lake-first data product. Durable market datasets live under `book-*-data` repos.
- **Not** coupled to Solo Empire monorepo runtime. Nested Git repo; commit only inside this tree.
- Never commit `.env`, cookies, session dumps, or scraped PII dumps to Git.

## Limitations (honest)

Prototype only. Respect ToS. Not a consumer app backend.

## Related

- Active collection product: `book-job-scraping` (Tier A tool)
- Lake products: `book-crypto-data`, `book-fx-data`, `book-stock-data`, …
- Solo Empire catalog: `repository-catalog/BOOK-DEV-BACKLOG-BD.md` (BD-012)
