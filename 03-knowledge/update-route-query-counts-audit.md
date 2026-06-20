# update_route_query_counts — Task Audit

> **Status:** REPORT ONLY — 2026-06-20  
> **Verdict:** NOT the cause of the production AWS CPU/network spike at 01:00. Spike is `precompute_popular_contracts` (every `:00`). This task runs Monday 00:30 only — graph shows 00:30 flat. 2 real fixes still needed (retry + index). 2 data-quality issues for product team.  
> **Source:** 3-agent debate (Backend Engineer / Senior Reviewer / SRE) + CloudWatch evidence

---

## Code Under Review

**File:** `products/tasks.py:11–35`  
**Schedule:** Weekly, Monday 00:30 Bangkok (`crontab(day_of_week=1, hour=0, minute=30)`)

```python
@shared_task
def update_route_query_counts():
    end_date = timezone.now()
    start_date = end_date - timezone.timedelta(weeks=WEEKS)  # WEEKS = 1

    query_counts = (
        QueryLog.objects
        .filter(query_time__gte=start_date, query_time__lte=end_date)
        .values('route')
        .annotate(count=Count('id'))
    )
    for item in query_counts:
        Route.objects.filter(id=item['route']).update(query_count=item['count'])

    clear_old_query_logs.delay()

@shared_task
def clear_old_query_logs():
    delete_before_date = timezone.now() - timezone.timedelta(weeks=WEEKS)
    QueryLog.objects.filter(query_time__lt=delete_before_date).delete()
```

**`query_count` consumers:**
- `products/services.py:224` — recommendation popularity boost (threshold: `> 100`)
- `products/views.py:1195` — homepage sort `-query_count`
- `pages_info/views.py:362` — page sort `-query_count`
- `products/serializers.py:1109` — exposed in API response

---

## Is This Causing Server Down?

**No.** Task runs on Celery worker (not web process). N+1 loop is PK-indexed, fast at current scale (~31 routes with counts). `QueryLog` steady-state size is ~7k rows (cleanup works correctly). No crash, no 500, no downtime risk today.

---

## Findings

### REAL BUG 1 — No retry, no error handling (P1)

Both tasks are plain `@shared_task` — no `bind=True`, no `max_retries`, no `try/except`, zero logging. A single Celery/DB hiccup at Monday 00:30:
1. `update_route_query_counts` fails silently — `query_count` is stale for the full next week
2. `clear_old_query_logs.delay()` is never called — `QueryLog` accumulates an extra week of rows
3. No log, no alert, no retry

Violates project policy (CLAUDE.md: "All tasks: `bind=True, max_retries, default_retry_delay`").

**Fix — both tasks:**
```python
@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def update_route_query_counts(self):
    try:
        end_date = timezone.now()
        start_date = end_date - timezone.timedelta(weeks=WEEKS)
        query_counts = list(
            QueryLog.objects
            .filter(query_time__gte=start_date, query_time__lte=end_date)
            .values('route')
            .annotate(count=Count('id'))
        )
        for item in query_counts:
            Route.objects.filter(id=item['route']).update(query_count=item['count'])
        clear_old_query_logs.delay()
        logger.info("update_route_query_counts: updated %d routes", len(query_counts))
    except Exception as exc:
        logger.exception("update_route_query_counts failed: %s", exc)
        raise self.retry(exc=exc, countdown=min(300 * (2 ** self.request.retries), 3600))

@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def clear_old_query_logs(self):
    try:
        delete_before_date = timezone.now() - timezone.timedelta(weeks=WEEKS)
        deleted, _ = QueryLog.objects.filter(query_time__lt=delete_before_date).delete()
        logger.info("clear_old_query_logs: deleted %d rows", deleted)
    except Exception as exc:
        logger.exception("clear_old_query_logs failed: %s", exc)
        raise self.retry(exc=exc, countdown=min(300 * (2 ** self.request.retries), 3600))
```

Note: `list()` added to force-evaluate queryset once (reused in logger; also avoids double-eval if used in future zero-reset logic).

---

### REAL BUG 2 — No index on `QueryLog.query_time` (P1 — insurance)

`QueryLog.query_time = DateTimeField(auto_now_add=True)` — no `db_index=True`. The weekly aggregation does a full table scan. At 7k rows (current steady state) this is ~1ms — not a problem today. But if `clear_old_query_logs` ever fails to run for several weeks, or if traffic grows significantly, this becomes a slow query at 00:30.

**Fix — migration:**
```python
migrations.AlterField(
    model_name='querylog',
    name='query_time',
    field=models.DateTimeField(auto_now_add=True, db_index=True),
)
```

SRE verdict: not causing issues today, but cheap insurance. Ship with BUG 1 fix.

---

### DATA QUALITY — Stale `query_count` for zero-query routes (P1 — product decision required)

Routes with zero searches this week are not touched by the loop — they keep their `query_count` from a prior week indefinitely. A route with `query_count=200` from 6 months ago stays at 200 forever, gets the recommendation popularity boost (threshold `>100`), and tops sort order on homepage and pages_info. The field behaves as "all-time high water mark" not "rolling 7-day window" as the code implies.

**Debate verdict:** This is wrong data that corrupts recommendations. But resetting to 0 causes a cliff-edge sort shuffle every Monday. This is a **product decision** — fix only after confirming intended semantics.

If product confirms rolling-window behavior:
```python
# After the update loop, reset all routes NOT in this week's window
active_ids = [item['route'] for item in query_counts]
Route.objects.exclude(id__in=active_ids).update(query_count=0)
```

**Guard required:** if `query_counts` is empty (no logs this week), `active_ids` is `[]` and `exclude(id__in=[])` resets ALL routes to 0. Add guard:
```python
if active_ids:
    Route.objects.exclude(id__in=active_ids).update(query_count=0)
```

---

### DATA QUALITY — `bulk_create` with nullable `trip.route` → IntegrityError (P1)

`views.py:211`: `QueryLog(route=trip.route)` — `Trip.route` is nullable. If any active `Trip` has `route=None`, `bulk_create` raises `IntegrityError` and the **entire search response returns 500** (not just the logging).

```python
# Current (unsafe)
for trip in trips:
    query_logs.append(QueryLog(route=trip.route))

# Fix
for trip in trips:
    if trip.route_id:
        query_logs.append(QueryLog(route_id=trip.route_id))
```

SRE: this is a real 500 risk on the search endpoint, not just wrong data. But it requires a Trip with `route=None` to exist. Check production DB before treating as urgent.

---

### NOT A BUG — `clear_old_query_logs` race condition

Debated: does `.delay()` create a race where cleanup deletes logs before they're counted? **No.**

Count window: `query_time >= now-7d AND <= now`  
Delete window: `query_time < now-7d`

Ranges are strictly disjoint. By the time `clear_old_query_logs` executes (async, after dispatch), the count is already committed. No log in the count window can be deleted by the cleanup. **Not a bug.**

### NOT A BUG — N+1 UPDATE loop

500 PK-indexed single-row UPDATEs at 00:30 on a Celery worker ≈ under 1 second. Not user-facing. Not a crash risk at current scale. The `Case/When` bulk update optimization was debated and **rejected** — naive version with `default=0` would zero all routes on any empty-Case edge case. Fix the retry issue first; optimize the loop only if the table grows to thousands of routes.

---

## Fix Priority

| # | Issue | Action | Files |
|---|-------|--------|-------|
| 1 | No retry/logging on both tasks | Fix now | `products/tasks.py` |
| 2 | No index on `QueryLog.query_time` | Fix now (migration) | `products/models.py` + migration |
| 3 | `bulk_create` with nullable `trip.route` | Fix now (1 line guard) | `products/views.py:211` |
| 4 | Stale `query_count` for zero-query routes | Ask product first | `products/tasks.py` (after decision) |

---

## Steady-State Table Size

`QueryLog` grows ~1 row per search per trip result. Cache TTL is 15min so same route pair can create logs at most ~96x/day. At moderate traffic, 7k rows/week is a reasonable estimate. Cleanup works correctly (disjoint date ranges), so table stays bounded. At 7k rows/week, even without the `query_time` index, the full table scan is ~1ms. The index is insurance, not emergency.

---

## Related

- [[celery-tasks]] — project Celery patterns and retry policy
- [[precompute-popular-contracts-audit]] — sister task audit (same file)
- [[precompute-popular-contracts-fix-plan]] — fix plan pattern to follow
