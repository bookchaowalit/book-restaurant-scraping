# Upgrade plan — book-restaurant-scraping

## Current state

Score: **7.5/10** (pass 1: 5 -> 7; pass 2: 7 -> 7.5) — one bounded,
fixture-tested Wongnai adapter with polite fetching, job isolation, minimal raw
captures, CLI bounds, lint and offline CI. Main gap: only one source exists.

## Backlog

### P0
- (none open)

### P1
- Add a fixture-tested second restaurant source (e.g. a public open-data
  listing) or document why Wongnai alone is enough for the downstream product.
- Existing `data/exported/*_raw.json` files from before pass 2 still hold full
  HTML; the owner should delete or regenerate them locally (not in Git).

### P2
- Add a conditional GET/ETag cache to avoid refetching unchanged pages.
- Document the downstream data product that consumes `data/exported/`.

## Done in this pass (pass 1)
- `restaurants/http.py`: identifying UA, 30 s timeout, bounded retry with
  backoff for 429/5xx/timeouts only, capped `Retry-After`.
- `fetch_pages`: 2 s delay between pages, early stop on an empty page.
- `run_restaurants.py`: failing job no longer blocks the next; error class
  only; non-zero exit on any failure.
- Tests for pagination/delay/dedupe/min-rows, malformed entries, retry
  policy, job isolation (5 -> 15 tests). Added ruff, pytest config, CI;
  untracked committed `__pycache__`.

## Done in this pass (pass 2)
- Raw capture now stores `trimmed_capture(state)` (whitelisted business fields
  the parser reads) instead of full page HTML — no review text, reviewer
  names or session state.
- `latitude`/`longitude` keep a real `0.0` (None check instead of `or ""`).
- `run_restaurants.py`: `--max-pages` 1-5 and `--min-rows` 1-500 validated by
  argparse (exit 2 before any work); `main(argv)` is testable.
- Tests 15 -> 20 (+4 subtests).
