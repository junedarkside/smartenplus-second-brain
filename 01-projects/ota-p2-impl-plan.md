---
name: ota-p2-impl-plan
description: Reviewed implementation plan for P2 — Supabase→Django OTA booking sync. 3-agent review (implementer + code reviewer + architect). Verdict: 10 items must be fixed before build starts. Produced 2026-06-23.
metadata:
  type: project
  status: pre-build-fixes-required
  date: 2026-06-23
  parent: ota-portal-overview
---

# P2 Implementation Plan — Supabase Mirror (Reviewed 2026-06-23)

3-agent review: Backend Implementer → Code Reviewer → Architect Validator. **Verdict: not ready. 10 must-fix items before `makemigrations` runs.** All are in-place fixes; no architectural rethink needed.

---

## Prerequisites (owner answers before build)

| # | Question | Who |
|---|---|---|
| OQ-1 | Confirm anon-read RLS on `view_information` active — `curl` test | Owner / Supabase |
| OQ-2 | Confirm `SUPABASE_ANON_KEY` value (never committed) | Owner |
| OQ-3 | Confirm sync cadence = manual batch first (not Beat) | Owner |
| OQ-4 | Confirm Supabase column names match the field mapping (run `--dry-run` on first attempt) | Engineer |

---

## Files to create / modify

### New files
| File | Purpose |
|---|---|
| `cs/supabase_client.py` | Paginated PostgREST client (no SDK, `requests` only) |
| `cs/tasks.py` | Celery task `sync_ota_bookings` |
| `cs/management/__init__.py` | Package marker |
| `cs/management/commands/__init__.py` | Package marker |
| `cs/management/commands/sync_ota_bookings.py` | Thin `BaseCommand` wrapper |

### Modify
| File | Change |
|---|---|
| `cs/models.py` | Add `CsOtaBooking` + `CsSyncLog` |
| `cs/admin.py` | Register `CsOtaBookingAdmin` + `CsSyncLogAdmin` |
| `Smartenplus/settings.py` | Add `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_PAGE_SIZE` |

No `cs/urls.py` changes. No frontend changes. No `admin-dashboard` changes.

---

## Settings / env vars

Add after the `AUTO_SMARTENPLUS_API_KEY` block (~line 592). **Must fix #7: no `default=''`.**

```python
# Supabase OTA sync — server-side only; NEVER expose to client
SUPABASE_URL = config('SUPABASE_URL')           # no default — raises if unset
SUPABASE_ANON_KEY = config('SUPABASE_ANON_KEY') # no default — raises if unset
SUPABASE_PAGE_SIZE = config('SUPABASE_PAGE_SIZE', default=1000, cast=int)
# TODO P3c: add SUPABASE_SERVICE_ROLE_KEY here
```

---

## `CsOtaBooking` model — field spec

Define inside `cs/models.py` after `FeatureFlag`.

**Constants (top of class):**
```python
SOURCE_12GO = '12go'; SOURCE_KLOOK = 'klook'
SOURCE_CHOICES = [(SOURCE_12GO, '12Go'), (SOURCE_KLOOK, 'Klook')]
STATUS_CONFIRMED = 'confirmed'; STATUS_CANCELED = 'canceled'
STATUS_PENDING = 'pending'; STATUS_QUARANTINED = 'quarantined'
STATUS_CHOICES = [(STATUS_CONFIRMED, 'Confirmed'), (STATUS_CANCELED, 'Canceled'),
                  (STATUS_PENDING, 'Pending'), (STATUS_QUARANTINED, 'Quarantined')]
```

**Fields:**
| Field | Type | null | db_index | Notes |
|---|---|---|---|---|
| `source` | `CharField(20, choices=SOURCE_CHOICES)` | No | Yes | |
| `booking_id` | `CharField(100)` | No | No | |
| `booking_date` | `DateField` | Yes | Yes | |
| `booking_time` | `TimeField` | Yes | No | |
| `customer_name` | `CharField(255)` | Yes | No | CRLF-stripped on sync |
| `email` | `EmailField(db_index=True)` | Yes | Yes | Merge + portal lookup key |
| `phone` | `CharField(50)` | Yes | No | |
| `destination` | `CharField(255)` | Yes | No | |
| `status` | `CharField(20, choices=STATUS_CHOICES)` | Yes | Yes | Normalized |
| `raw_status` | `CharField(100)` | Yes | No | Original emoji string; audit only |
| `passenger_names` | `JSONField(null=True)` | Yes | No | **Fix: JSONField not TextField** — list of names; `editable=False`, excluded from list_display (PII) |
| `class_type` | `CharField(100)` | Yes | No | 12Go only |
| `participant` | `CharField(100)` | Yes | No | Klook only |
| `vehicle_type` | `CharField(100)` | Yes | No | 12Go only; used in P3b request taxonomy |
| `ota_booking_url` | `URLField(null=True)` | Yes | No | **Add now** — staff relay link; avoids painful P3b migration |
| `last_synced_at` | `DateTimeField(auto_now=True)` | — | No | Renamed from `django_synced_at` |
| `created_at` | `DateTimeField(auto_now_add=True)` | — | No | |

**Meta: (Must fix #3 — use `UniqueConstraint`):**
```python
class Meta:
    ordering = ['-booking_date', 'source']
    constraints = [
        models.UniqueConstraint(fields=['source', 'booking_id'],
                                name='cs_otabooking_source_bookingid_uniq')
    ]
    indexes = [
        models.Index(fields=['-booking_date', 'source'],
                     name='cs_otabooking_date_source_idx')
    ]
    verbose_name = 'OTA Booking'
    verbose_name_plural = 'OTA Bookings'
```

---

## `CsSyncLog` model — field spec (Must fix #4 — explicit fields)

```python
class CsSyncLog(models.Model):
    key = models.CharField(max_length=50, unique=True)
    last_success_at = models.DateTimeField(null=True, blank=True)
    last_run_at = models.DateTimeField(auto_now=True)
    rows_fetched = models.PositiveIntegerField(default=0)
    rows_upserted = models.PositiveIntegerField(default=0)
    rows_skipped = models.PositiveIntegerField(default=0)
    rows_excluded = models.PositiveIntegerField(default=0)
    rows_quarantined = models.PositiveIntegerField(default=0)
    error = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'OTA Sync Log'
        get_latest_by = 'last_success_at'
```

---

## `cs/supabase_client.py` — function spec

- **`_headers()`** — reads `settings.SUPABASE_URL` / `settings.SUPABASE_ANON_KEY` at call time (not import). **Must fix**: assert `SUPABASE_URL.startswith('https://')` — raise `ImproperlyConfigured` if not.
- **`fetch_ota_bookings(source=None) -> list[dict]`** — paginated loop with `Range` header + `Prefer: count=exact`. Use `requests.Session()` in `try/finally`. Per page: `Range: {offset}-{offset+page_size-1}`, 30s timeout. Assert `booking_id` and `source` sentinel fields on every row — **must fix #8**: use explicit `if not row.get('booking_id'): raise ValueError(...)`, not `assert`. Column allowlist: drop unexpected columns before returning rows.
- **`assert_ota_view_accessible() -> bool`** — fetches `Range: 0-0`. Raises `RuntimeError` on 401/403 or network failure.

---

## `sync_ota_bookings` Celery task — build order

Decorator **(must fix #1, #2)**:
```python
@shared_task(
    bind=True, name='cs.sync_ota_bookings',
    autoretry_for=(requests.exceptions.ConnectionError, requests.exceptions.Timeout),
    max_retries=3, default_retry_delay=60,
    time_limit=900, soft_time_limit=840,
)
```

Logic (numbered — each step ≤ 10 lines):
1. Acquire lock: `cache.add(LOCK_KEY, token, timeout=870)` — TTL = soft_time_limit + 30. Store `token = str(uuid4())`. Skip if not acquired.
2. `try`: fetch rows via `fetch_ota_bookings(source)`.
3. Per-row: strip CRLF + null bytes: `re.sub(r'[\x00\r\n]', ' ', v)`.
4. Exclude: `booking_date in (None, 'N/A', '', _SENTINEL_DATE)` or missing sentinels.
5. Normalize status via `_STATUS_MAP` (module-level dict). Unknown → `'quarantined'` + `logger.warning`.
6. Build `defaults` dict mapping Supabase columns → Django fields (confirm column names on `--dry-run` first run).
7. `update_or_create(source, booking_id, defaults)` — use `bulk_create(update_conflicts=True)` per batch of 500 for race safety (Django 4.1+). Skip if `dry_run`.
8. Write `CsSyncLog(key='ota_sync')` upsert with counts + `last_success_at=now()`. Gate on `not dry_run`.
9. `finally`: `if cache.get(LOCK_KEY) == token: cache.delete(LOCK_KEY)` — **must fix #2: verify token before delete**.
10. Return `{'fetched': N, 'upserted': N, 'skipped': N, 'excluded': N, 'quarantined': N}`.

**Module-level constants:**
```python
LOCK_KEY = 'cs:sync_ota_bookings:lock'
_SENTINEL_DATE = date(5000, 8, 2)  # 12Go placeholder for unconfirmed bookings
_STATUS_MAP = {'✅Confirmed': 'confirmed', '❎Canceled': 'canceled', 'Pending': 'pending'}
```

---

## Management command

Args: `--source` (choices `['12go', 'klook']`), `--dry-run` (store_true).

```python
try:
    assert_ota_view_accessible()
except RuntimeError as e:
    raise CommandError(str(e)) from e   # Must fix #CR: clean CommandError not traceback
```

If `--dry-run`: print first 3 raw rows for column-name verification before any upsert.
Call `sync_ota_bookings.apply(kwargs={...})`. Print counts.

---

## Migration

**Must fix #6: include `makemigrations` as a build step.**

```
python manage.py makemigrations cs   # creates 0003_csotabooking_cssynclog.py
python manage.py migrate
```

Migration number: `0003` (after `0002_featureflag`). If P1 lands a `cs/0003_*` first, renumber to `0004`. No cross-app FK — safe to run in any order relative to P1.

P3a migration must list `('cs', '0003_csotabooking_cssynclog')` (or renumbered) in `dependencies`.

---

## Admin

```python
@admin.register(CsOtaBooking)
class CsOtaBookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'source', 'booking_id', 'status', 'customer_name',
                    'email', 'destination', 'booking_date', 'last_synced_at']
    list_filter = ['source', 'status', 'booking_date']
    search_fields = ['booking_id', 'email', 'customer_name', 'destination']
    readonly_fields = ['source', 'booking_id', 'raw_status', 'last_synced_at', 'created_at']
    # passenger_names excluded — PII; accessible in detail view only
```

---

## Reuse flags (for P3a engineer)

- **Extract `_resolve_signed_token(request, header, loader_fn)`** from `cs/views.py` before P3a builds. P2 is the right phase to do this since it's already touching `cs/`. Avoids P3a duplicating token header-parse boilerplate.
- **`IsAdminOrIsStaff`** — reuse for any staff OTA view added in P3a. No new permission class.

---

## Must-fix checklist (all before `makemigrations`)

| # | Fix | Where |
|---|---|---|
| 1 | `autoretry_for` → network errors only | `tasks.py` decorator |
| 2 | Lock TTL = soft_time_limit+30; verify token before delete | `tasks.py` finally block |
| 3 | `unique_together` → `UniqueConstraint` | `models.py` Meta |
| 4 | `CsSyncLog` explicit fields (no `**counts`) | `models.py` |
| 5 | Remove Beat comment from scope — Beat activation is an ops task, not P2 | `celery.py` / plan |
| 6 | Add `makemigrations` to build checklist | Implementation step list |
| 7 | `SUPABASE_ANON_KEY` no default; raise `ImproperlyConfigured` if unset | `settings.py` |
| 8 | Replace `assert` with explicit `if not ... raise ValueError(...)` | `supabase_client.py` |
| 9 | `passenger_names` → `JSONField`, `editable=False`, excluded from list_display | `models.py` + `admin.py` |
| 10 | Add `ota_booking_url = URLField(null=True)` — avoids painful P3b migration | `models.py` |

---

## Verification checklist (post-deploy)

1. `curl` RLS pre-flight — `view_information` returns HTTP 200 with anon key.
2. `python manage.py sync_ota_bookings --dry-run` — prints 3 raw rows; confirm Supabase column names match field map; no DB writes.
3. First live sync: `upserted` ≈ 561, `excluded` ≥ 2 (`N/A` + `5000-08-02` sentinels), `quarantined` = 0 or low with warnings logged.
4. Idempotency: re-run immediately → `upserted=0`, `skipped≈561`.
5. `UniqueConstraint` test: attempt duplicate insert → `IntegrityError` raised.
6. `CsSyncLog.objects.latest()` → `last_success_at` non-null, `error` null.
7. CRLF + null-byte audit: `CsOtaBooking.objects.filter(customer_name__contains='\r').count()` → 0.
8. Anon key not in any client bundle: `grep -r "SUPABASE_ANON_KEY" smartenplus-frontend/src/` → 0 results.

---

## Related
[[ota-portal-overview]] · [[ota-sync-supabase-mirror]] · [[ota-portal-review]] · [[cs-api-contract]] · [[supabase-ota-booking-store]]
