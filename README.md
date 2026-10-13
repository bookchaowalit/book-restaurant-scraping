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

## Polite collection

`restaurants/http.py` is the only network path: an identifying `User-Agent`
(`book-restaurant-scraping/1.0`), a 30 s timeout, and at most three attempts
with exponential backoff that retry only timeouts, connection errors, HTTP 429
(honouring `Retry-After` as seconds or an HTTP-date, capped at 60 s) and
5xx; 403/404 fail at once. The helper is kept identical to
book-ecommerce-scraping's `ecommerce/http.py` apart from the User-Agent.
`fetch_pages` waits 2 s between pages, is capped at 5 pages x 100 rows, and
stops as soon as a page returns no results. `scripts/run_restaurants.py`
isolates jobs: a failing job is reported as `{"job": ..., "error":
"<ExceptionClass>"}` and the exit code is 1. Raw JSON, snapshot CSV and
history CSV are written atomically (`restaurants/atomic_io.py`: temp file +
fsync + `os.replace`), so a killed cron run never leaves a truncated export
or a torn history row.

Rows keep only business contact data that Wongnai publishes for the venue
(address, business phone, homepage). The raw capture
(`<stem>_raw.json`, under git-ignored `data/`) is no longer full page HTML: it
keeps, per page, only the search-result business fields the parser reads
(`trimmed_capture`), so review snippets, reviewer names and page/session state
are never stored. `--max-pages` (1-5) and `--min-rows` (1-500) are validated
before any request.

## Checks (offline)

```bash
pip install -r requirements.txt pytest ruff
ruff check .
python -m pytest -q
python3 scripts/run_restaurants.py --dry-run --json   # plan only, no network
```

Tests replay `tests/fixtures/` and mock the HTTP layer; CI
(`.github/workflows/ci.yml`) runs the same commands.

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
