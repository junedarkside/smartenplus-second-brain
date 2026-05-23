# ISR 429 Cold-Start Fix 2026-05-23

## Summary
Cold `npm run dev` causes 429 Too Many Requests on `/front-page/`. One hard browser refresh fixes it for the session. Root cause: DRF anon throttle window (500/hour) persists across dev restarts — previous session burns the quota.

## Scrutiny Corrections (2026-05-23)

Initial diagnosis contained two false claims — corrected after audit:

### FALSE CLAIM 1 — "REVALIDATE_SECONDS=60 causes burst"
`REVALIDATE_SECONDS` is **irrelevant in `next dev` mode**. Next.js dev always runs `getStaticProps` on every request regardless of `revalidate` value. ISR cache is bypassed entirely in dev. Changing 60→300 has zero effect on local 429s.

### FALSE CLAIM 2 — "trips/[...slug].js hits /front-page/ during ISR revalidation"
`getStaticPaths` runs **only at `next build`** — never during runtime ISR revalidation. During revalidation, only `getStaticProps` runs. `trips/[...slug].js getStaticProps` hits `/admin-dashboard-routes/home/…` — not `/front-page/`. Zero concurrent contribution at runtime.

---

## Actual Root Cause

**Backend:** `FrontPageViewSet` (`pages_info/views.py:92`) has no custom `throttle_classes` → inherits global DRF defaults (`settings.py:405-411`):
```python
'anon': '500/hour'   # sliding window per IP
'user': '5000/hour'
```

**Frontend dev behavior:** `getStaticProps` in `homepagev2.js` (via `pages/index.js` re-export) runs on **every** browser request to `/` in dev. Each load = 1 `/front-page/` call.

**Why cold start triggers 429:** DRF sliding window does NOT reset when `python manage.py runserver` restarts. Previous dev session requests still count against the hourly window. Active dev session (frequent reloads, HMR, tab switching) burns through 500/hour quickly. Next cold start opens with a depleted quota → first request hits 429.

**Why one refresh fixes it:** The 429 response itself is not cached. The throttle check passes on retry if the window has ticked, or the Django process is restarted between the two loads.

**`FrontPageViewSet.list` is expensive:** 6 separate DB queries per call (`views.py:336-346` — hero_banners, locations, home_routes, categories, top_reviews, stations). No response-level cache on `list()`. Each dev reload hits all 6 queries fresh.

---

## Correct Fixes

### Fix A (PRIMARY) — Add response cache to `FrontPageViewSet.list`
**File:** `pages_info/views.py:327`

```python
FRONT_PAGE_CACHE_KEY = 'frontpage_list_response'
FRONT_PAGE_CACHE_TTL = 300  # 5 minutes

def list(self, request):
    cached = cache.get(FRONT_PAGE_CACHE_KEY)
    if cached:
        return Response(cached)
    
    response_data = {}
    # ... existing 6 fetch calls ...
    
    cache.set(FRONT_PAGE_CACHE_KEY, response_data, timeout=FRONT_PAGE_CACHE_TTL)
    return Response(response_data)
```

Result: all dev reloads hit Django cache after first call. 1 DB hit per 5 min instead of 1 per page load. Eliminates 429 regardless of throttle window state.

**Cache invalidation:** must bust `FRONT_PAGE_CACHE_KEY` when routes/locations/banners change. Add `cache.delete(FRONT_PAGE_CACHE_KEY)` to existing station signal handler and any equivalent signals.

### Fix B — Increase anon throttle rate for dev (OPTIONAL)
**File:** `settings.py:410`

```python
'anon': '2000/hour',  # was 500/hour
```

Buys headroom but doesn't fix the underlying DB query cost. Fix A is better.

### Fix C — RTK Query refetch semantics (keep — unrelated bug)
**File:** `hooks/useTripData.js:16,24`
```js
{ skip: skipFetching, refetchOnMountOrArgChange: true } // was 300
```
`300` (number) = "refetch if cache older than 300s" → fires immediately on cold mount. `true` = "refetch on arg change" — correct intent. Hits `/api/v1/trips/` not `/front-page/`, but still a real bug.

### Fix D — RefreshTokenHandler deps (keep — unrelated bug)
**File:** `components/auth/refreshTokenHandler.js:25`
```js
}, [session?.accessTokenExpiry, props.setInterval]) // was props
```

### DROP — Fix 1 from initial report
~~`REVALIDATE_SECONDS = 300`~~ — no effect in dev. Only relevant for production ISR cadence. Leave at 60 or raise for prod reasons only, not for 429.

---

## Fix Priority

| Priority | Fix | Layer | Impact |
|----------|-----|-------|--------|
| P0 | Response cache on `FrontPageViewSet.list` | Backend | Eliminates 429 |
| P1 | `refetchOnMountOrArgChange: true` | Frontend | Fixes RTK bug |
| P1 | `props.setInterval` in deps | Frontend | Fixes re-render noise |
| Optional | Raise anon throttle rate | Backend | Buys headroom |

---

## Status
REWORKED 2026-05-23 after scrutiny audit. Fixes not yet implemented.

## Verification
1. Apply Fix A. Restart Django.
2. `npm run dev` → open homepage cold
3. Backend terminal: `/front-page/` appears once, then cache serves subsequent reloads
4. Make 20+ rapid reloads — no 429
5. Restart Django (`runserver`) without `rm -rf .next` — cold start still no 429 (cache persists in Redis/memcache between process restarts if configured)

## Related
- [[nextjs-patterns]] — ISR only applies in production (`next start`), not dev
- [[hydration-infinite-refresh-fix-2026-05-20]] — different cause (hydration mismatch)
- [[backend-architecture]] — Django throttling, DRF defaults
