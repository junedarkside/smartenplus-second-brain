# CSP Duplicate Headers — Browser Enforces the Intersection

## Summary

Two `Content-Security-Policy` response headers do **not** override each other. The browser enforces **every** CSP header independently; the effective policy is their **intersection**, most-restrictive-wins per directive. A second, narrower header silently vetoes everything the first one allows.

## Context

Discovered in session #362 after a production console dump showed Google Ads, GA4, and Cloudflare Insights all blocked. `curl -sI https://www.smartenplus.co.th/ | grep -ci content-security-policy` returned **2**.

SmartEnPlus had CSP in nginx alone since 2025-12-05 (`025a61c0`), extended six times as new third-party domains appeared. Commit `b39bc140` (2026-08-25, Meta Pixel work) added a **second** CSP block to `next.config.js`, written fresh, inheriting none of those six fixes. Every blocked URL in the console mapped verbatim to a directive string from the *new* header.

The commit shipped with a comment asserting nginx "wins over this header." That belief is what let a duplicate ship without review flagging it.

## Problem

Three compounding failure modes, all of which apply beyond this codebase:

1. **"The other layer wins" is wrong.** There is no precedence between CSP headers. Both apply. Adding a header can only ever *restrict*, never *relax*.
2. **`NODE_ENV`-gating hides it.** `dc4ad7d6` wrapped the Next.js CSP in `process.env.NODE_ENV === 'production'`. Dev then sends no CSP at all, so local testing is clean and the break only appears after a prod deploy.
3. **Auditing files in isolation misses it.** Session #361 audited both CSP files and declared them correct — each *was* correct on its own. The bug only exists in how many headers ship. **Only `curl -I` against the live origin reveals it.**

## Details

### Never assume one policy is a subset of another — diff them

The first fix plan was "just delete the narrower header." A per-directive diff of both **live** headers proved that assumption false. The Next.js header uniquely allowed:

| Directive | Only in the narrower header | Impact of naive delete |
|---|---|---|
| `img-src` | `platform-lookaside.fbsbx.com`, `profile.line-scdn.net` | Facebook + LINE OAuth avatars break |
| `img-src` | `via.placeholder.com`, `api.omise.co`, `www.google-analytics.com` | placeholder / omise / GA images break |
| `font-src` | `data:` | inline data-URI fonts break |
| `frame-src` | `www.facebook.com` | Meta Pixel iframe breaks |

Deleting first would have broken avatars for every social-login user. The correct sequence is **backfill the surviving policy first, then delete the duplicate**.

### `remotePatterns` is not CSP

The avatar hosts *were* listed in `next.config.js` `images.remotePatterns` — which governs the **Next.js image optimizer**, not CSP. Two unrelated mechanisms.

This matters because `ProfileHeader.js:33` renders MUI `<Avatar src={...}>`, and **MUI emits a plain `<img>`, not `next/image`**. It never proxies through the optimizer, so it gets no same-origin exemption and is subject to `img-src` directly. Same pattern at `ProfileButton.js:122`, `Comment.js:28`, `Post.js:156`.

### `form-action` has no `default-src` fallback

Removing the duplicate un-masked a second, pre-existing error: `form-action 'self'` blocking the Meta Pixel's hidden-form POST to `facebook.com/tr/`. That directive had been in nginx for 8 months but was masked — the narrower header blocked the Pixel *earlier* (at `script-src`/`connect-src`), so it never reached its form fallback.

`form-action` is one of the CSP directives with **no `default-src` fallback**. An existing `connect-src https://www.facebook.com` does nothing for it; the host must be listed on `form-action` explicitly. Other no-fallback directives include `base-uri`, `frame-ancestors`, and `report-uri`.

Scope `form-action` sources tightly (exact host, not `*.facebook.com`) — it governs where the browser may POST form data, so an over-broad source has more real consequence than elsewhere. It also governs **every** form on the site, so a mistake breaks checkout.

## Decision

**One CSP header, one file.** nginx (`nginx/sites-available/smartenplus.conf:158`) is the sole source of truth for SmartEnPlus.

Keeping two lists in sync was rejected: every future third-party domain would need adding in two places or prod breaks again — exactly the failure that occurred. nginx was already the more complete and more actively maintained of the two, and it applies regardless of `NODE_ENV`.

## Consequences

- Any new third-party domain goes in nginx **only**. `next.config.js` carries a comment saying so.
- nginx conf is **bind-mounted** (`docker-compose.prod.yml:37`, `./nginx/sites-available:ro`), so it ships with the normal app deploy — no separate nginx deploy.
- **`nginx -t` must be run manually right after deploy.** The compose healthcheck runs it only *after* container start on a 30s interval — too late to prevent a malformed directive taking the site down — and `deploy-ghcr.sh` has no nginx-specific rollback.
- Un-masking is expected: fixing one CSP block can reveal the next one down the chain. That is the same pattern, not a failed fix.

## Reusable checklist

When a CSP violation appears in production:

1. `curl -sI <origin> | grep -ci content-security-policy` — **more than 1 is the bug.**
2. If 1, diff the live header against the repo file — a hand-edit on the server would be destroyed by the deploy's `git reset --hard && git clean -fd`.
3. Check whether the violating directive has a `default-src` fallback. `form-action`, `base-uri`, `frame-ancestors`, `report-uri` do **not**.
4. Before deleting any policy, **diff it per-directive** against the one that will survive. Backfill first, delete second.
5. After fixing, re-check the console — expect the next masked violation to surface.

## Related

- [[master-state]] — session #362
- `nginx/sites-available/smartenplus.conf:158` · `next.config.js` · `docker-compose.prod.yml:37`
