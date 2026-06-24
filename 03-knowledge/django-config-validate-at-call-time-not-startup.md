# django-config-validate-at-call-time-not-startup

## Summary
For optional/secret settings (API keys, third-party URLs), keep `default=''` in `settings.py` so the server always boots, then validate at CALL TIME — raise `ImproperlyConfigured` only when the feature is actually used.

## Why It Matters
`config('SUPABASE_ANON_KEY')` with no default crashes app startup if the env var is absent — taking down the whole site for one unconfigured integration. Validating at call time lets the server start; only the dependent sync/feature fails cleanly with a clear error. Deploy safety > strictness.

## Detail
```python
# settings.py — allow boot, no hard fail
SUPABASE_URL = config('SUPABASE_URL', default='')
SUPABASE_ANON_KEY = config('SUPABASE_ANON_KEY', default='')

# supabase_client.py — validate when used, not on import
def _headers():
    if not settings.SUPABASE_ANON_KEY:
        raise ImproperlyConfigured("SUPABASE_ANON_KEY not set — OTA sync disabled")
    if not settings.SUPABASE_URL.startswith('https://'):
        raise ImproperlyConfigured("SUPABASE_URL must be https://")
    return {'apikey': settings.SUPABASE_ANON_KEY, ...}
```

## Constraints / Gotchas
- Secrets read at call time, NEVER at module import (import-time read bakes in the value + fails on import).
- Pair with `assert_..._accessible()` pre-flight checks in management commands — fail with `CommandError`, not a traceback.

## Related
- [[ota-p2-impl-plan]] — must-fix #7 + simplicity correction source
- [[ota-sync-supabase-mirror]]
