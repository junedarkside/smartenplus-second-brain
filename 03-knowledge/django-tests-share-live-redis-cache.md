---
name: django-tests-share-live-redis-cache
description: Django's test runner isolates the database but not a django-redis cache — tests read and write the live cache. Fix used 2026-09-29: dedicated Redis DB for `manage.py test` + guarded flush runner.
type: knowledge-atom
date: 2026-09-29
parent: backend-architecture
---

# Django Tests Share the Live Redis Cache

## Summary
`manage.py test` creates a throwaway test **database**, but `CACHES` stays whatever settings say. With django-redis pointed at the dev/prod Redis DB, tests write fixtures into the real cache and read the real site's cached responses.

## Why It Matters
Proven both directions (#439): a nav test left a `/test-destinations` fixture in the dev `navigation_v1_th` cache after its test DB was destroyed (phantom nav item on the dev site), and a hero-banner test failed because it read a `/front-page/` response the dev server had cached. Running the suite on a server sharing prod Redis could do the same to production.

## Fix (not locmem)
LocMemCache lacks `delete_pattern()`, which the signals use — so stay on Redis, but a different DB:
```python
TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'
TEST_REDIS_DB = 15
redis_server = f'redis://{host}:6379/{TEST_REDIS_DB if TESTING else 1}'
TEST_RUNNER = 'Smartenplus.test_runner.IsolatedCacheTestRunner'
```
The runner flushes DB 15 before and after the run and **raises if LOCATION isn't `/15`** (FLUSHDB must never reach the live DB). Isolation is per run, not per test — tests that need an empty cache still `cache.clear()` in `setUp`.

## Related
- [[view-level-response-cache-masks-new-fields]]
- [[backend-architecture]]
