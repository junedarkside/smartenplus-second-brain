# ISR Stale Data Audit — Trip Detail Page

## Summary
Next.js ISR `revalidate: 300` broken in Docker standalone deployment. Pages cached once, never regenerated. Only redeploy (clearing Docker volume) forces fresh data. On-demand revalidation API route proposed as fix.

## Context
Admin updates trip data (timeline, pricing, description, images) via admin-dashboard. Customers see stale data until next deploy. Business impact: incorrect pricing, outdated schedules, wrong images shown to booking customers.

## Problem
`/trips/detail/[slug]` uses `revalidate: 300` (5 min ISR). After admin saves changes, page stays stale for hours. Hard refresh does not help. Only full redeploy resolves.

## Root Cause Analysis

### Evidence Trail

**What works (verified):**
1. Django signals fire correctly — `ContractViewSet.update()` and `update_timeline()` both call `instance.save()`, triggering `post_save` signal
2. Redis cache invalidation works — `cache.delete_pattern(f"product_detail_v1_{instance.slug}_*")` clears backend cache (django-redis 5.4.0 confirmed)
3. Admin-dashboard update path — timeline page calls `PATCH /admin-dashboard-operators/contract-details/{slug}/update-timeline/` → `instance.save()` → signal fires
4. No nginx HTML caching — nginx only caches `/_next/static/`, no `proxy_cache` for HTML
5. No CDN layer — direct nginx → Next.js proxy
6. Signal registration verified — `operators/apps.py` `ready()` imports `operators.signals`

**What's broken:**
- **Next.js ISR `revalidate: 300` does not trigger page regeneration in Docker standalone mode**
- CLAUDE.md workaround confirms: "deploy script must clear smartenplus_next_cache Docker volume or ISR persists forever"
- Local `.next/cache/` has no `fetch-cache/` subdirectory — ISR cache handler may not properly write revalidation metadata
- `revalidate: 300` set at `pages/trips/detail/[...slug].js:464` but never triggers regeneration

### Architecture Diagram

```
Admin Dashboard → PATCH API → Django saves Contract
                                    ↓
                            post_save signal
                                    ↓
                    cache.delete_pattern (Redis) ✅ works
                                    ↓
                    Next.js ISR cache ❌ never notified
                                    ↓
                    Page serves stale HTML from Docker volume
                                    ↓
                    Only fix: redeploy clears volume
```

### Docker ISR Setup

```
Dockerfile:
  COPY --from=builder /app/.next/standalone ./    ← standalone server
  mkdir -p /app/.next/cache                        ← ISR cache dir

docker-compose.prod.yml:
  volumes:
    - next_cache:/app/.next/cache                   ← persistent volume

deploy-ghcr.sh:
  docker volume rm smartenplus_next_cache           ← cleared on deploy
```

Next.js 14.2.5 standalone mode with `output: 'standalone'`. Volume mounts to `/app/.next/cache/`. Cache path should be correct (relative to `server.js` at `/app/server.js`).

### CSR Overlay (partial mitigation)

`useCheckContractQuery` at `[...slug].js:84-87` refreshes on mount:
- `ratecard`, `start_date`, `end_date`, `stop_sale_dates`, `is_actived`, `operational_days`

**What stays stale** (ISR shell, not covered by CSR overlay):
- Product name, description, images
- Timeline, route_info, policies
- JSON-LD structured data (SEO impact)
- Meta tags, og tags
- Breadcrumbs
- Reviews

## Decision: On-Demand Revalidation API Route

### Options Evaluated

| Option | Verdict | Why |
|--------|---------|-----|
| A. On-demand revalidation | **Selected** | 1 file frontend + 30 lines backend. Bypasses broken timer. Instant update. Reusable for 19 ISR pages |
| B. Reduce revalidate (300→60) | Rejected | Timer is broken, not slow. No benefit |
| C. revalidateTag/revalidatePath | Rejected | Requires refactoring fetchData from axios to fetch(). Same result as A with more work |
| D. Full CSR (disable ISR) | Rejected | Destroys SEO. No structured data for crawlers |

### Option A Detail

**Frontend** — new `pages/api/revalidate.js`:
- POST endpoint with `REVALIDATION_SECRET` validation
- Calls `res.revalidate(path)` for each path in request
- Accepts single `path` or `paths` array for batch revalidation
- Server-only env var, never in client bundle

**Backend** — modify `operators/signals.py`:
- Add `_trigger_revalidation(slug)` function
- Background thread (non-blocking, daemon, 5s timeout)
- Calls `POST {FRONTEND_URL}/api/revalidate` with paths array
- Fire-and-forget with logging: admin save never fails if revalidation call fails
- Safety net: broken `revalidate: 300` still exists as eventual fallback

**New env vars:**
- `REVALIDATION_SECRET` (frontend + backend, shared)
- `FRONTEND_URL` (backend only)

### Files to Change

| File | Repo | Action |
|------|------|--------|
| `pages/api/revalidate.js` | frontend | Create |
| `operators/signals.py` | backend | Modify |
| `scripts/deploy-ghcr.sh` | frontend | Modify |
| `.env.example` | frontend | Modify |
| `settings.py` | backend | Modify |

### Deployment Order

1. Frontend first (endpoint sits idle, zero risk)
2. Backend second (signal now calls revalidation)
3. Verify: admin edit → page updates on next visit

### Risks

| Risk | Mitigation |
|------|------------|
| Backend can't reach frontend | Thread fails silently with logging. Broken `revalidate: 300` as fallback |
| Secret leaked | Not `NEXT_PUBLIC_`. Server-only env var |
| Multiple rapid saves | `res.revalidate()` is idempotent. Last call wins |
| Non-existent path | Next.js handles gracefully, returns error but doesn't crash |

### Future Extension

| Backend Event | Paths |
|---|---|
| Contract save | `/trips/detail/{slug}`, `/activities/detail/{slug}` |
| Blog post update | `/blog/{slug}`, `/blog` |
| Homepage content | `/` |

API route is generic — accepts any paths array. Only Django signals need additions.

## Related
- [[nextjs-patterns]] — ISR, RTK Query, revalidation patterns
- [[nextjs-isr-ratecard-empty-array-guard]] — CSR overlay array merge guard
- [[docker-production]] — Docker volume, deploy script, cache clearing
- [[isr-429-cold-start-fix-2026-05-23]] — Related ISR issue (429 on cold start)
- [[operators]] — Contract model, signals, cache invalidation
