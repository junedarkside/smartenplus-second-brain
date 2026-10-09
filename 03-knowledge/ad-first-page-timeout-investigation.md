---
name: ad-first-page-timeout-investigation
description: AD dashboard first page timeout after the 2026-10-07/08 station-translation-bot release — 4-specialist code review, ranked suspects, corrected cache-flush fix, measure-first runbook. Nothing measured on prod yet.
metadata:
  type: knowledge
  status: open
  date: 2026-10-09
  source: code + config read only (no prod access); 4 agents (postgres-pro, backend-architect, react-specialist, devops-engineer)
---

# AD First Page Timeout After 2026-10-07/08 Release

## Summary
`smartenplus-dashboard.vercel.app` first page (`pages/index.js` → `dashboard/Main/Main.js`) will not render and BE queries are slow after BE + FE + AD shipped together. **Root cause NOT confirmed.** Most likely a saturated 2-slot web tier made worse by the release's extra load, with the route-description N+1 as the biggest known new cost. Thai visual report: https://claude.ai/artifact/4kqVSV7zELKEMtX3XKijEd (private).

## Context
Release = station translation bot + review API (BE `stations/*`, migration `0049`), AD sidebar badge + Translation Review page. Prod web = `docker-compose-rds.yml`, gunicorn `--workers 1 --threads 2 --timeout 30`, `mem_limit 256m` → **2 concurrent requests**, micro-tier box ([[prod-capacity-celery-audit]], source-verified). AD first page fires 4 calls per tab at once (stats, trips `page_size=50`, bookings, sidebar summary), so any query over ~1 s queues the rest. Vercel limit (10 s Hobby / 60 s Pro) trips before gunicorn's 30 s kill.

## Suspects (ranked, agents disagreed on order)
| | Suspect | Status |
|---|---|---|
| C | `RouteSerializer` station-description N+1 (142 queries on `/trips`, from `f0d3a04`/`d54a5c9`, 2026-10-07) | **Already fixed on BE `develop f2fa237`, NOT deployed.** See [[destination-trips-slow-root-cause]]. Likely the largest single cost. AD trips call (`pageSize=50`) hits it |
| A | Web tier 1×2 slots: slow request → queue → 30 s worker kill | Config known; saturation under load unmeasured |
| B | Migration `0049` row-by-row backfill, atomic, runs in container start (10–30 s 502 expected, [[release-b-thai-names-runbook]]) | Check deploy-log `migrate` duration; run `ANALYZE stations_stationtranslation` |
| D | Cache flush per `StationTranslation` save: 3× `delete_pattern` SCAN on shared Redis (`stations/translation_signals.py:82-88`) | Exists in code; bot capped ~200 writes/h, so impact unproven |
| E | AD sidebar poll every 60 s per tab incl. background (`pages/dashboard/SideList.js:177-180`, not `SideBarListMenu`) | Amplifier only. COUNT is cheap (~5–20 ms at 100k rows) |
| F | Summary COUNT with no index | **Ruled out** as cause |
Ruled out: `?include=translations` station list (prefetch, constant-query test), `pre_save` SELECT (negligible). AD itself does not block the page: `getServerSideProps` only reads the JWT cookie; a slow BE shows endless skeletons because `fetchBaseQuery` has no timeout.

## Corrected fix for D (the first plan was wrong)
First idea: skip flush when `source='bot' and not is_reviewed`. **Wrong:** approve keeps `source='bot'`, so **revert** (`review_views.py:119-124`) and admin un-tick (`admin_translations.py:77-79`) look like bot drafts → no flush → visitors keep stale Thai up to 15 min. Correct rule: `pre_save` records `_was_reviewed` (1 PK lookup; new row = False; skip when `update_fields` lacks `is_reviewed`); skip flush only if **not reviewed before AND not reviewed now**; on delete skip only if `not instance.is_reviewed`. Key on state, never `source`. Update `test_translation_review_api.py:242-248` (reject of bot drafts → 0 flushes; add reject of approved row → 1). Bot cannot overwrite an approved row (409 guard, `stations/serializers.py:761,768`), drafts are never served (`translation_api.py:34,75`).

## Other findings
- Partial index `Index(['-updated_at'], condition=Q(is_reviewed=False, source='bot'))` beats composite `(is_reviewed, source)`; only after `EXPLAIN` on prod.
- `_unchanged_filter` (`review_views.py:49`) ORs up to 500 `(id AND updated_at)` pairs = 1000 bind params; use `id__in` + compare `updated_at` in Python.
- `StationTranslation.save()` reads `station.station_name` per full save (extra SELECT per bot write).
- Route-overview / FAQ bot viewsets have no 409 guard and do not flush (existing staleness gap, out of scope).
- AD fix: poll 5 min + `skipPollingIfUnfocused` + `refetchOnFocus` (inert unless `setupListeners(store.dispatch)` is called in `store/index.js`) + `timeout: 15000` on `fetchBaseQuery`. Also check `/api/user/list-users/` (used as stats, may be huge) and whether NextAuth jwt/session callbacks call the BE. Related pattern: [[polling-backoff-jitter-pattern]].

## Runbook (measure first)
1. Evidence: DevTools Network on AD first page; gunicorn `WORKER TIMEOUT` / `Booting worker` counts; nginx 499/502/504 by path; `pg_stat_statements`, `pg_stat_activity`; Redis `INFO commandstats` (scan/del), `SLOWLOG`; Vercel `FUNCTION_INVOCATION_TIMEOUT`. No `KEYS` / `--bigkeys`.
2. Pause the bot (external HTTP client, not Celery; reversible, `batch_id` idempotent) — needs user OK.
3. Fastest likely win: **deploy `f2fa237`** (already on develop). Stopgap: gunicorn 2–3 workers × 4 threads only if `mem_limit` allows.
4. Forward-fix only, **no BE rollback** (0049 added a column). Branches off `develop`, never `main`.
5. AD redeploy with poll/timeout change after BE is healthy; resume bot slowly, watch 30 min.
6. Post-mortem + alerts (WORKER TIMEOUT, 5xx, Redis evictions). Rule: data migrations on live tables must be batched or non-atomic.

## Cross-repo impact
Public FE: none (cache keys and payload shapes unchanged). AD: poll cadence + timeout only (`/admin-dashboard-*` admin-only). BE: signal condition, optional index, serializer prefetch (done), compose config.

## Lessons
- Review panels disagreed with the lead's top hypothesis (flush storm); evidence from existing vault notes (capacity, N+1) outranked it. Check the vault for already-fixed causes before planning new fixes.
- A fix keyed on a mutable label (`source`) instead of state broke a path found only by a reviewer.

## Related
[[destination-trips-slow-root-cause]] · [[prod-capacity-celery-audit]] · [[bot-draft-then-human-approve-design]] · [[version-checked-approve-reject]] · [[polling-backoff-jitter-pattern]]

## Update 2026-10-09 (later): fixes merged + AD-wide N+1 scan
**Merged to develop, NOT deployed:** AD `eb520bf` (sidebar 60 s poll removed → refetch on focus/reconnect/approve; `timeout: 15000` on `stationTranslationsApi`), BE `c3ea619` (draft-only translation writes skip the Redis flush; keyed on prior+current `is_reviewed`; 11 tests in `stations/test_translation_flush_skip.py`; `stations` suite 242 green). Unchanged vs plan: `_unchanged_filter` left alone; reject/import (deferred) still flush once. No migrations; deploy BE then AD.

**Local N+1 scan** of 34 AD endpoints (GET only, local dev DB, queries at page_size 2 vs 20; query count is a proxy, local RTT ~0.1 ms vs 1-3 ms RDS). Worst:
| Endpoint | Queries | Cause |
|---|---|---|
| `GET /admin-dashboard/booking-summary/` (**AD first page**, `useGetDashboardBookingsQuery`) | 1186 for 679 rows, **unpaginated** (no `PAGE_SIZE`, bare `PageNumberPagination`) | `to_attr` prefetch lands on `contract` but `bookings/serializers.py:222` reads it on the booking item → 680 image queries; `contract_ratecard` unprefetched (481); trip override stations not select_related |
| `admin-dashboard-orders/order-summary/` | 1633 for 544 rows | billingprofile / extraitem / cards_refund per row (cause not code-verified) |
| `admin-dashboard-routes/trips/` (**first page**, pageSize 50 ≈ 320 extrapolated) | 16→131 for 2→20 rows | station / stationtranslation / location / contract per row; `f2fa237` fixed only the public `/trips` |
| tickets 154/35 rows; contracts 22→133; locations 10→108; routes 11→73; places/stations/stop-sale/gallery/cs ~1-3 per row | | |
Flat/clean: home, route-faqs, route-picker, operators, vehicle-class/type, station-mappings, cities, provinces, hero-banners. `list-users` flat 27 queries (first page).
First page therefore fires ~1500+ queries across 3 calls on a 2-slot backend; booking-summary grows with every booking, so it needs no new trigger.

**4-agent review (postgres-pro, backend-architect, react-specialist, code-reviewer) → merged plan** (also in plan file):
- Gate 0: deploy the 3 merged commits, re-measure; if timeout gone, N+1 = hardening.
- Do NOT change the default `booking-summary` shape (bare list; AD reads `results ?? response`); pagination = contract change needing sign-off; do not touch its unauthenticated-viewset Known Issue.
- Dashboard needs its own endpoint (`booking-summary/dashboard/` → `{total, recent[7], route_counts}`): capping the list would corrupt the Main.js route pie % and "Showing 7 of N". Pie rule: count rows with a route name, denominator = all bookings; add `-created` order.
- Branches, one each off develop, never bundled: (1) `perf/booking-summary-queries` (extract queryset helper first: `bookings/views.py` = 500 lines; read `obj.contract._prefetched_image_gallery`; image prefetch `is_deleted=False` + order; ratecard `select_related`; admin queryset only, serializer shared with customer views), (2) dashboard summary endpoint + AD `dashboardApi.js`/`Main.js`, (3) `perf/ad-trips-queries` (`TripDashBoardViewSet products/views.py:1279`, file 2709 lines), (4) `perf/order-summary-queries` (`orders/serializers.py` defines `OrderSummarySerializer` twice, 2nd shadows 1st; coupon apply/remove returns it = payment-adjacent; prefetch only, run payment tests), (5) tickets/contracts/locations/routes only if on first-page path.
- Each fix: golden JSON before/after, `assertNumQueries` bounded at 1/5/20 rows (repo has none today), full `manage.py test`, customer-path output test.
- Verify CI Django version: `requirements.test.txt` pins <4.1 where a sliced `Prefetch` raises (prod 4.2.16). Indexes only if EXPLAIN shows a sort: `(is_active, traveling_date DESC)` CONCURRENTLY; `pg_trgm` for `icontains` search. Rank 3-5 with prod `pg_stat_statements`.
- Optional AD: defer booking call via RTK `skip` (one `useState` + `requestIdleCallback`, no useEffect chain); keep trips pageSize 50 unless product owner agrees.
Lessons: a local scan across all endpoints found the first-page killer (`booking-summary`) that code review of the release never looked at; the release-specific hypotheses may only be amplifiers.

## Update 2026-10-09 (session #476): merges, slash-less calls, CPU credits
**Merged to develop (pushed):** BE `5227bd8` booking-summary (1186 -> 6 queries local, JSON identical, query-budget tests at 1/5/20 rows, full-suite failure set = develop baseline); FE `8b02a812` + AD `db2e849` trailing slash. **Deployed by user: BE only** (`f2fa237`, `c3ea619`, `5227bd8`). AD (`eb520bf`, `db2e849`) and FE not deployed yet.
**Slash-less calls (found from a pasted prod log, then scanned FE + AD):** DRF routers need a trailing slash, so `APPEND_SLASH` answered 301 and the client re-sent: 2 BE worker slots per call. Hot ones were FE ISR `product-detail/<slug>`, `admin-dashboard-routes/home/<from>/<to>`, `stationsinfo/<slug>`; also `family-and-friends`, `carts/<id>`, `contract/<id>`, AD `contracts-stop-sale/<id>`. Parity: same payload, only the 301 hop is gone. nginx has no `$request_time`, so the log alone proved nothing about slowness; one nginx 499 = client timeout (FE `fetchData` 8 s).
**CPU credits (user's CloudWatch screenshot, graph ends 10-09 17:25):** CPUCreditBalance 144 (max) until ~10-07 night, then drains to 0; CPU ~5% -> ~12% sustained; usage ~0.8 credits/5 min vs earn ~0.5 (6/h). Drain ~40 h matches. 144 max = t2.micro / t3.nano class (type + credit mode unconfirmed). At 0 the CPU is throttled to ~10%/vCPU, so every container slows: likeliest explanation of the timeout. Recovery only if load < baseline (~5% load: +3 credits/h -> ~7 h to 20, ~2 days to 144). Relief (user only): Unlimited credits, upsize, cut load. **Station bot is NOT running (user), so suspect D/bot is dropped.**
**Lesson:** a burstable box hides a load increase for ~1.5 days until the credit buffer is gone; alarm on CPUCreditBalance, not CPU %.
**Still not measured on prod:** per-container CPU (`docker stats`), `celery-beat` restart loop, AD request timings, `WORKER TIMEOUT` counts.
