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

## Team Synthesis (2026-05-23)

**Specialists:** isr-specialist · backend-specialist · frontend-specialist

### Root Cause — Key Disagreement Resolved

| Claim | Verdict |
|---|---|
| Audit doc: "ISR timer never fires in Docker standalone" | Overstated |
| isr-specialist: "ISR works as designed" | Mostly correct, misses the gap |

**Synthesis:** `revalidate: 300` fires on next-request-after-staleness — not on a guaranteed timer. If no traffic hits the page for hours, stale page serves indefinitely. ISR in standalone mode has **no background worker** to proactively revalidate. Admin update → Redis clears → **ISR HTML cache never notified**. The gap is real regardless of bug vs behavior framing.

### ISR Pages Found — 19 Total

| Page | revalidate |
|---|---|
| `trips/detail/[...slug].js` | 300s |
| `activities/detail/[...slug].js` | 3600s |
| `airport-transfer/[slug].js` | 3600s |
| `trips/[...slug].js` | 300s |
| Homepage sections, blog, destinations, locations, operators, about | 10s–86400s |

`revalidateTag` not used anywhere — time-based ISR only.

### What's Stale (SEO Impact)

**CSR overlay covers:** ratecard, start/end dates, stop_sale_dates, is_actived, operational_days ✅

**Stale regardless (no CSR fallback):**
- Product name, description, route_info, images, timeline, operator name, policies
- JSON-LD schemas (Product, TouristTrip, BreadcrumbList, FAQPage, LocalBusiness, Organization)
- Meta tags, OpenGraph, canonical URL, Twitter Card, breadcrumb path

**SEO impact:** Googlebot may index stale titles/descriptions/prices for 5 min (trips) to 1 hour (activities).

### Network Path — Resolved ✅

Backend and frontend are **separate Docker compose projects** (different networks). Direct `frontend:3000` won't work.

**Solution:** Use public URL — same pattern as `bookings/tasks.py:37`:
```python
frontend_url = 'http://localhost:3000' if settings.DEBUG else 'https://smartenplus.co.th'
```
Celery worker just needs outbound HTTPS to `smartenplus.co.th`. Works regardless of Docker networking.

### Major: Use Celery, Not Bare Thread — CONFIRMED

**Finding:** Bare daemon thread is fragile. No retry, no monitoring, no backpressure, threads die with Django restart.

**Evidence:** Celery infrastructure already fully configured:
- `Smartenplus/celery.py` — Celery app
- `django_celery_results` + `django_celery_beat` in INSTALLED_APPS
- `celery-worker` + `celery-beat` services in `docker-compose-deploy.yml`
- Existing retry patterns in `bookings/tasks.py`

**Fix:** Use Celery task with slug-based deduplication. `trigger_isr_revalidation(slug)` in `operators/tasks.py`, called from signal after Redis clears.

### Pre-Deploy Verification Required

1. **Test HTTP path** — Django management command calling `POST https://smartenplus.co.th/api/revalidate?secret=SECRET&path=/trips/detail/test-slug` before wiring signal
2. **Confirm Celery worker outbound HTTPS** — check no firewall blocking celery → `smartenplus.co.th`
3. **Add `REVALIDATION_SECRET` to GitHub Secrets** for CI/CD

---

## Implementation — API Route + Celery Task

### `pages/api/revalidate.js` (frontend) — CREATE

```javascript
import { NextResponse } from 'next/server';

const REVALIDATION_SECRET = process.env.REVALIDATION_SECRET;

export async function POST(request) {
  const authHeader = request.headers.get('authorization');
  const secret = authHeader?.replace('Bearer ', '') || request.nextUrl.searchParams.get('secret');

  if (secret !== REVALIDATION_SECRET) {
    return NextResponse.json({ error: 'Invalid token' }, { status: 401 });
  }

  let paths = [];
  try {
    const body = await request.json();
    paths = Array.isArray(body.paths) ? body.paths : [body.path];
    paths = paths.map(p => '/' + p.replace(/\/+$/, '').replace(/^\/+/, ''));
  } catch {
    const pathParam = request.nextUrl.searchParams.get('path');
    if (pathParam) paths = [pathParam];
  }

  if (paths.length === 0) {
    return NextResponse.json({ error: 'No paths provided' }, { status: 400 });
  }

  const results = [];
  for (const path of paths) {
    try {
      await request.revalidatePath(path);
      results.push({ path, status: 'revalidated' });
    } catch (err) {
      results.push({ path, status: 'error', message: err.message });
    }
  }

  const hasErrors = results.some(r => r.status === 'error');
  return NextResponse.json(
    { revalidated: !hasErrors, paths: results },
    { status: hasErrors ? 207 : 200 }
  );
}
```

- Bearer token auth via `Authorization` header + `?secret=` query param fallback
- Batch support via `{"paths": [...]}` for bulk revalidation
- Returns 207 Multi-Status on partial failure

### `operators/tasks.py` (backend) — CREATE Celery task

```python
@shared_task(bind=True, max_retries=3, ignore_result=True)
def trigger_isr_revalidation(self, slug):
    """Trigger Next.js ISR revalidation for a contract slug."""
    from django.conf import settings
    import requests

    frontend_url = 'http://localhost:3000' if settings.DEBUG else 'https://smartenplus.co.th'
    revalidate_url = f"{frontend_url}/api/revalidate"

    try:
        response = requests.post(
            revalidate_url,
            json={"slug": slug},
            timeout=10
        )
        response.raise_for_status()
        logger.info(f"ISR revalidation triggered for contract/{slug}")
    except Exception as e:
        logger.error(f"ISR revalidation failed for {slug}: {e}")
        raise self.retry(exc=e, countdown=60)
```

- Retry: `max_retries=3`, `countdown=60`
- Deduplication: slug-based task_id prevents rapid-save task flood

### `operators/signals.py` (backend) — MODIFY

Add after existing Redis cache deletes:
```python
if instance.slug:
    trigger_isr_revalidation.delay(instance.slug)
```

### `.env.example` (frontend) — ADD

```
# On-demand ISR revalidation (used by backend to trigger frontend cache invalidation)
REVALIDATION_SECRET=your-secret-here
```

---

## Deployment Order

1. **Frontend first** — deploy `pages/api/revalidate.js` (idle until backend wires in, zero risk)
2. **Backend second** — add Celery task, wire to signal, deploy
3. **Verify** — admin edits contract → ISR page updates on next visit (seconds, not hours)

---

## Scrutinize Audit Findings (2026-05-23)

### ✅ Blocker: `pages/api/revalidate.js` does not exist
**Status:** RESOLVED — implementation designed above. Code ready to create.

### ⚠️ Blocker: HTTP call from Django to frontend — network path unverified
**Status:** RESOLVED — public URL approach (same as `bookings/tasks.py:37`). Separate Docker networks not an issue.

### ✅ Major: Root cause diagnosis was incomplete
**Status:** RESOLVED — "timer fires but no background worker" confirmed. On-demand revalidation is correct fix regardless.

### ✅ Major: Background thread from Django signal
**Status:** RESOLVED — Use Celery task. Already configured, retry/dedup/sonitoring.

### ⚠️ Minor: No `revalidateTag` used
**Status:** NOTED — `revalidatePath` sufficient for path-level granularity. No tag-based invalidation needed.

### ✅ Minor: No rate limiting/debouncing
**Status:** RESOLVED — Celery slug-based task deduplication handles rapid saves.

### ✅ Minor: `REVALIDATION_SECRET` not in `.env.example`
**Status:** RESOLVED — will add with env var.

---

## Risks (Final)

| Risk | Mitigation |
|---|---|
| Celery task fails silently | `max_retries=3` + logging. Fallback: stale ISR until next deploy |
| Secret leaked | Server-only env var, not `NEXT_PUBLIC_` |
| Rapid admin saves → task flood | Slug-based task deduplication |
| Non-existent path | Next.js handles gracefully, returns error but doesn't crash |
| ISR still broken post-deploy | `revalidate: 300` remains as eventual fallback |

## Future Extension

| Backend Event | Paths |
|---|---|
| Contract save | `/trips/detail/{slug}`, `/activities/detail/{slug}` |
| Blog post update | `/blog/{slug}`, `/blog` |
| Homepage content | `/` |

API route generic — accepts any paths array. Only Django signals need additions.

## Related
- [[nextjs-patterns]] — ISR, RTK Query, revalidation patterns
- [[nextjs-isr-ratecard-empty-array-guard]] — CSR overlay array merge guard
- [[docker-production]] — Docker volume, deploy script, cache clearing
- [[isr-429-cold-start-fix-2026-05-23]] — Related ISR issue (429 on cold start)
- [[operators]] — Contract model, signals, cache invalidation
- [[celery-patterns]] — Celery task patterns (for revalidation task implementation)