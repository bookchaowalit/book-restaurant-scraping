# Upgrade plan — book-restaurant-scraping

## Current state

Score: **7/10** (was 5/10) — one bounded, fixture-tested Wongnai adapter with
polite fetching, job isolation, lint and offline CI. Gaps: raw HTML captures
are stored in full, and only one source exists.

## Backlog

### P0
- (none open)

### P1
- Store a trimmed raw capture (the `searchResult` slice of `window._wn`)
  instead of full page HTML, to cut size and avoid retaining unrelated
  user-generated content (review snippets, reviewer names).
- `latitude`/`longitude` use `value or ""`, so a real `0.0` becomes empty;
  compare against `None` instead (harmless for Thailand, but wrong in general).
- Validate `--max-pages`/`--min-rows` in argparse so bad values fail before
  any network call.

### P2
- Add a conditional GET/ETag cache to avoid refetching unchanged pages.
- Document the downstream data product that consumes `data/exported/`.

## Done in this pass
- `restaurants/http.py`: identifying UA, 30 s timeout, bounded retry with
  backoff for 429/5xx/timeouts only, capped `Retry-After`.
- `fetch_pages`: 2 s delay between pages, early stop on an empty page.
- `run_restaurants.py`: failing job no longer blocks the next; error class
  only; non-zero exit on any failure.
- Tests for pagination/delay/dedupe/min-rows, malformed entries, retry
  policy, job isolation (5 -> 15 tests). Added ruff, pytest config, CI;
  untracked committed `__pycache__`.
