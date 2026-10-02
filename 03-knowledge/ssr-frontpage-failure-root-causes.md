# SSR Front-Page Render Failure — Root Causes

## Summary

Homepage (`/` and `/th`) renders empty in production but works in dev. Four confirmed causes, all fixable without infrastructure changes. Investigated 2026-10-02.

## Context

Architecture:
```
Next.js (FE EC2) → SSR getStaticProps → https://api.smartenplus.co.th → nginx → gunicorn (1 worker, 30s timeout) → Django → RDS + Redis
```

No internal Docker network shortcut between FE and BE — all SSR fetches go over public HTTPS.

`baseURL = process.env.NEXT_PUBLIC_API_URL` — same URL for SSR and browser. No `INTERNAL_API_URL`.

## Problem

Four compounding failure modes. Any one alone can cause empty homepage for up to 1 hour.

## Cause 1 — AnonRateThrottle 500/hour (P0)

`FrontPageViewSet` inherits global `AnonRateThrottle`. Prod limit = 500/hour (`DEBUG=False`).

SSR requests are unauthenticated → counted against anon quota. ISR revalidations + crawlers exhaust this fast. 429 → `fetchData` throws → `Promise.allSettled` resolves rejected → `frontPageData = {}` → empty homepage.

**Fix:** Add `throttle_classes = []` to `FrontPageViewSet` in `pages_info/views.py`.

## Cause 2 — fetchData Has No Timeout (P0)

`helpers/fetchData.js` uses axios with `timeout=0` (infinite) by default. `getStaticProps` calls `fetchData(urls.frontPage)` with no timeout argument.

If gunicorn is slow (cold cache, slow RDS query, deploy restart): SSR hangs indefinitely → Next.js render queue blocks → FE container starves under load.

Gunicorn kills its own worker at 30s — but axios doesn't know, waits for the TCP connection to drop. On connection drop: error → `Promise.allSettled` → empty data.

**Fix:** Pass `timeout: 15000` in `homepagev2.js:318` call: `fetchData(urls.frontPage, 'GET', null, {}, 15000)`.

## Cause 3 — ISR revalidate=3600 Caches Failures for 1 Hour (P1)

`REVALIDATE_SECONDS = 3600` (`lib/homepage/constants.js`). On failed BE fetch (empty `{}`), Next.js caches the broken props for 1 hour before retrying.

User experiences: blank homepage for up to 1h after any BE blip.

**Fix:** `REVALIDATE_SECONDS = 300` or `600`. Use on-demand revalidation signal from BE for fast recovery (backend signal already exists: `REVALIDATION_SECRET` env var).

## Cause 4 — Redis Cache Has No Exception Guard (P2)

`FrontPageViewSet.list()` calls `cache.get()` and `cache.set()` without try/except. Redis `allkeys-lru` evicts under memory pressure (100MB limit, Redis shared with other caches) → cache miss storm → all concurrent SSR requests hit DB simultaneously → gunicorn queue overflows.

Redis crash or restart: unhandled exception → 500 → SSR gets 500 → empty data.

**Fix:** Wrap cache operations in try/except in `pages_info/views.py:411,427`.

## Cause 5 — FRONT_PAGE_CACHE_TTL = 300s Too Short (P2)

5-minute Django-side cache means fresh DB aggregation (8 queries) every 5 minutes × 2 locales = cold hit every 2.5 minutes on average. On 1 worker/2 thread gunicorn, cold hits queue up under any load.

**Fix:** Increase `FRONT_PAGE_CACHE_TTL` from 300 to 1800 seconds in `pages_info/views.py`.

## Dev vs Prod Difference

| Condition | Dev | Prod |
|---|---|---|
| BE response time | Fast (local) | External HTTPS + cold RDS |
| AnonRateThrottle | 5000/hr | 500/hr |
| Gunicorn | `runserver` (unlimited) | 1 worker, 30s timeout |
| Redis TTL | N/A or local | 300s, shared 100MB |
| ISR revalidate | SSR every request | 3600s stale window |
| fetchData timeout | Infinite (works OK fast) | Infinite (hangs on slow BE) |

## Fix Order

1. `throttle_classes = []` on `FrontPageViewSet` — unblocks 429s immediately (BE deploy)
2. `fetchData` timeout 15s in `homepagev2.js` — caps SSR hang (FE deploy)
3. `REVALIDATE_SECONDS = 300` — failures self-heal in 5 min (FE deploy)
4. Redis try/except + TTL=1800 — reduce cold-hit storm (BE deploy)

## Verification

```bash
# Check historic throttle/timeout hits
docker logs smartenplus-backend_web_1 2>&1 | grep -E "429|front-page|timeout" | tail -50

# Check FE container for ECONNRESET/timeout
docker logs <fe_container> 2>&1 | grep -E "front-page|ECONNRESET|timeout" | tail -50

# Confirm throttle fix: hit endpoint 510 times
for i in $(seq 1 510); do curl -s -o /dev/null -w "%{http_code}\n" https://api.smartenplus.co.th/front-page/; done | sort | uniq -c
```

## Related

- [[prod-capacity-celery-audit]] — same 1 vCPU/1GB EC2, same gunicorn single-worker constraint
- [[polling-backoff-jitter-pattern]] — same class of issue (many concurrent requests → server overload)
- Vault `EC2-INSTANCE-UPSIZE` — real capacity fix, prerequisite for gunicorn worker bump
