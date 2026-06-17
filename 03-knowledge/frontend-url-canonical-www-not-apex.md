# FRONTEND_URL Must Be Canonical www (Not Apex) — Backend→Frontend POSTs

## Summary

Backend `FRONTEND_URL` (`Smartenplus/settings.py:373`) must point at the **canonical www host** `https://www.smartenplus.co.th`, NOT the apex `https://smartenplus.co.th`. The apex 301-redirects to www, and `requests.post()` **drops the body + Authorization header across a cross-host redirect** → any backend→frontend POST silently fails.

## The bug it caused (ISR revalidation never landed)

On-demand ISR revalidation: backend `revalidate_frontend_isr` task POSTs `{FRONTEND_URL}/api/revalidate` with a Bearer secret. Prod `FRONTEND_URL` resolved to apex (the old default). Chain:
1. POST → `https://smartenplus.co.th/api/revalidate`
2. Server 301 → `https://www.smartenplus.co.th/...`
3. `requests` follows the redirect as GET / without re-sending the JSON body + `Authorization` → frontend gets no slug / no secret → 401 or no-op.
4. Revalidation never happens → edited page stays stale. Symptom looked like "the whole feature is broken" but secret + code were correct.

## Canonical host source of truth

`www` is canonical — confirmed by frontend `NEXT_PUBLIC_DOMAIN=https://www.smartenplus.co.th` and `next-sitemap.config.js siteUrl='https://www.smartenplus.co.th'`. Apex redirects to www at the edge.

## Rule

- Any backend setting that builds a URL the **backend itself calls** (revalidate webhook) OR that users click (password-reset link, `accounts/views.py:312`) → use the canonical www host to avoid the redirect.
- Fix was 1 line (correct the `config()` default) + set prod env explicitly. Do NOT add redirect-following/host-rewrite code — that's papering over a config value.
- General: when a server-to-server POST "silently does nothing," check for an apex↔www (or http↔https) redirect eating the body.

## Related
- [[docker-standalone-isr-revalidate-gap]]
- [[on-demand-revalidation-api-route]]
- [[seo-canonical-getsiteurl-pattern]]
