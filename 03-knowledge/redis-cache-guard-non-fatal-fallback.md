# Redis Cache Guard — Non-Fatal Fallback Pattern

**Problem:** `cache.get(key)` raises an exception when Redis is down (OOM, restart, network blip, connection refused). Uncaught exception → 500 → user sees error page → `getStaticProps` catch block → ISR HTML caches the error.

**Pattern:** Wrap `cache.get` and `cache.set` in `try/except`. Log warning, fall through to live DB query (or skip the cache write). Service stays degraded-but-functional during Redis outage.

```python
try:
    cached = cache.get(cache_key)
    if cached:
        return Response(cached)
except Exception as e:
    logger.warning('Redis cache.get failed for %s: %s', key, e)
# fall through to live DB

# ... live query ...

try:
    cache.set(cache_key, response_data, timeout=TTL)
except Exception as e:
    logger.warning('Redis cache.set failed for %s: %s', key, e)
return Response(response_data)  # success even if cache write failed
```

**Where to apply:** Any viewset with `cache.get(...)` + `cache.set(...)` pattern. Especially high-traffic endpoints serving ISR (product detail, front page, slug lists).

**Why log warning not error:**
- `logger.error` triggers ops alerts
- `logger.warning` is informational — expected to happen during Redis maintenance/restart
- Log still appears in observability dashboards for forensics

**Why no retry:** Cache writes are idempotent; next request retries automatically. Adding retry on write path adds latency for all users during Redis hiccups.

**Related:**
- `drf-throttle-exemption-isr-cache-miss-storms.md` (sibling fix in #452)
- `docker-standalone-isr-revalidate-gap.md` (separate Redis-related failure mode)
- `getstaticprops-fetch-timeout-isr-blocking.md` (V1 catch-block, paired defense)

**Source:** Session #452, PR `fix/be-throttle-redis-guards`, commit `f95c657`.