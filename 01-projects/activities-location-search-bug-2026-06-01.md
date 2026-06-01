# Activities Location Search Bug — Team Audit 2026-06-01

## Summary

Location search on `/activities` returns zero results for any text input (e.g., "Phuket"). Two independent root causes confirmed: backend expects Location integer IDs, frontend sends city name strings; and frontend Autocomplete `inputValue` diverges from `value` prop so URL-restored location is invisible to users. 4-specialist audit (Frontend, Next.js, Backend, DRF) + scrutinize pass. 3 critical bugs, 3 medium bugs. Backend fix: 4 lines. Frontend fix: 6 lines.

---

## Context

- **Route:** `/activities` → `FilterDayTripsPage.js` → `useDayTripFilters.js` → `dayTripsApi.js` → `GET /api/v1/contract/`
- **Branch audited:** `260601-fix/activities-browse-audit`
- **Public endpoint:** `products/views.py:355` `ContractViewSet` — `permission_classes = [AllowAny]`, `is_actived=True, confirm=True` hardcoded (NOT the admin `operators/views.py:95` `ContractViewSet` which requires `IsAuthenticated`)
- **Previous audit** (`activities-day-tour-page-review-2026-06-01.md`) addressed UX/design/code quality. Did NOT investigate location search failure specifically.

---

## Root Cause Chain

### RC-1 [CRITICAL] — Backend location filter: string input → `.none()`

**File:** `smartenplus-backend/products/views.py:446-453`

```python
location_ids = self.request.query_params.get('location')
if location_ids:
    location_ids_list = _parse_int_list(location_ids)  # "Phuket" → []
    if location_ids_list:
        queryset = queryset.filter(service_areas__id__in=location_ids_list).distinct()
    else:
        queryset = queryset.none()  # ← ZERO RESULTS for any text input
```

Frontend sends `?location=Phuket`. `_parse_int_list("Phuket")` returns `[]` (safely catches `ValueError`). `if location_ids_list:` is False → `.none()`.

**No text-search fallback exists.** Location filter assumes all callers send integer IDs.

### RC-2 [CRITICAL] — Frontend Autocomplete: `inputValue` doesn't sync with `value` prop

**File:** `smartenplus-frontend/components/activities/shared/DayTripLocationSearch.js:20`

```js
const [inputValue, setInputValue] = useState(value || '');  // initialized once
```

When user navigates to `/activities?location=Phuket`, `useDayTripFilters` hydrates `filters.location = "Phuket"` from URL. `FilterDayTripsPage` passes `value="Phuket"` to `DayTripLocationSearch`. BUT `inputValue` stays `""` (initial mount value). MUI Autocomplete uses `inputValue` for the visible text field — user sees blank input while `value="Phuket"` is in state.

### RC-3 [CRITICAL] — Frontend freetext doesn't trigger search until blur/select

**File:** `smartenplus-frontend/components/activities/shared/DayTripLocationSearch.js:26-28`

```js
const handleInputChange = (event, newInputValue) => {
  setInputValue(newInputValue);
  // ← onChange(newInputValue) NEVER called — parent never sees typed text
};
```

User types "Phuket" → `inputValue` updates locally → parent `filters.location` stays `null` → API called without `?location=` → all results returned unfiltered. Only selecting from dropdown OR blurring the field triggers `onChange` → `handleChange` → parent update. Freetext search doesn't work without selection.

---

## Team Findings

### Frontend Specialist (React)

| ID | Sev | Finding |
|----|-----|---------|
| F-1 | Critical | `inputValue` never syncs with `value` prop — URL-restored location invisible |
| F-2 | Critical | `handleInputChange` doesn't emit to parent — freetext typing silently discarded |
| F-3 | Medium | `handleClear` emits `null` instead of `''` — type inconsistency |

**What works:** Autocomplete `freeSolo` config correct, POPULAR_DESTINATIONS includes all major cities, location value flows correctly to `useGetContractsQuery` args, `useDayTripFilters` URL hydration with `router.isReady` guard works.

### Next.js Specialist (RTK Query)

| ID | Sev | Finding |
|----|-----|---------|
| N-1 | Critical | `getState().session` always `undefined` — NextAuth session not in Redux (affects auth endpoints only; `getContracts` is public, unaffected) |
| N-2 | Medium | Double-fetch risk: `FilterDayTripsPage` `useEffect` updating filter from `initialLocation` prop + `useDayTripFilters` hydration both fire on mount |
| N-3 | Medium | `initialLocation` effect in `FilterDayTripsPage` fragile — should be in hook not component |

**What works:** `router.isReady` guard prevents spurious URL push, RTK Query cache key construction correct, Accept-Language header set, pagination + category filter URL sync working.

### Backend Specialist (Django)

| ID | Sev | Finding |
|----|-----|---------|
| B-1 | Critical | `products/views.py:446-453` — text location input → `.none()` (RC-1 confirmed) |
| B-2 | Critical | `service_areas` M2M is the only location join — `primary_location` FK (operators/models.py:402) ignored in public filter |
| B-3 | Medium | DAY_TOUR contracts with `trip=NULL` cannot be found by trip-route location chains (transport-side filter in admin viewset only) |

**What works:** `_parse_int_list` safe on bad input (returns `[]`, no crash), `is_actived=True, confirm=True` hardcoded correctly, `icontains` ORM queries safe from SQL injection.

### DRF Specialist

**Key correction:** There are **two** `ContractViewSet` classes:
- `operators/views.py:95` — admin internal, `IsAuthenticated`, NOT used by frontend
- `products/views.py:355` — public browse, `AllowAny`, IS used by frontend via `apis/urls.py:38`

**Previous bug report context was wrong on permission bug.** No 401 issue — public endpoint correctly configured.

| ID | Sev | Finding |
|----|-----|---------|
| D-1 | Info | `status=active` param sent by frontend is silently **ignored** by `products.ContractViewSet` — it hardcodes `is_actived=True`. Param is harmless but misleading. |
| D-2 | Medium | 1-hour cache (`cache_key = f"contract_list_v1_{md5(params)}"`) means location filter fix won't be visible for up to 1 hour after deploy |

**What works:** Permission correct (`AllowAny`), serializer correct, URL routing correct, caching + pagination work.

---

## Debate & Resolution

### Debate 1 — Is F-2 (freetext not emitting) truly critical?

Frontend specialist says freetext typing never updates parent. However: MUI Autocomplete with `freeSolo` fires `onChange` on Enter keypress and on blur with the typed value. So typing + pressing Enter DOES work. Typing without Enter/blur does NOT.

**Verdict:** Confirmed medium-to-high severity. Not critical (Enter works) but broken UX — users expect results to filter as they type or at least on selection without pressing Enter. Still fix it.

### Debate 2 — Should handleInputChange emit to parent (real-time search)?

Next.js specialist questions whether emitting every keystroke would over-fetch. Backend has 1-hour cache. RTK Query deduplicates by cache key.

**Verdict:** Emit on input change is fine. RTK deduplication prevents extra API calls for the same query. Adds debounce if performance concern arises later.

### Debate 3 — `primary_location` vs `service_areas` for location filter

Backend says both exist on Contract. DRF confirms public endpoint only uses `service_areas`. Which is correct for DAY_TOUR?

**Verdict:** Add both to filter with OR. `service_areas` is the canonical M2M. `primary_location` is single FK for upselling. For text search, check `service_areas__location_name__icontains` OR `primary_location__location_name__icontains`. Safe to OR them — `.distinct()` already applied.

---

## Decision — Fix Sequence

### Fix 1 [Backend] — Add text-search fallback to `products/views.py` location filter

**File:** `smartenplus-backend/products/views.py:446-453`

```python
# BEFORE:
location_ids = self.request.query_params.get('location')
if location_ids:
    location_ids_list = _parse_int_list(location_ids)
    if location_ids_list:
        queryset = queryset.filter(
            service_areas__id__in=location_ids_list
        ).distinct()
    else:
        queryset = queryset.none()

# AFTER:
location_ids = self.request.query_params.get('location')
if location_ids:
    location_ids_list = _parse_int_list(location_ids)
    if location_ids_list:
        queryset = queryset.filter(
            Q(service_areas__id__in=location_ids_list) |
            Q(primary_location__id__in=location_ids_list)
        ).distinct()
    else:
        # Text fallback: location name string (e.g. "Phuket")
        queryset = queryset.filter(
            Q(service_areas__location_name__icontains=location_ids) |
            Q(service_areas__city__icontains=location_ids) |
            Q(service_areas__province__icontains=location_ids) |
            Q(primary_location__location_name__icontains=location_ids) |
            Q(primary_location__city__icontains=location_ids) |
            Q(primary_location__province__icontains=location_ids)
        ).distinct()
```

Requires `Q` import — check if already imported at top of `products/views.py`.

### Fix 2 [Backend] — Clear cache after deploy

Cache TTL is 1 hour. After deploying Fix 1, invalidate cache:
```python
# Django shell or management command
from django.core.cache import cache
cache.clear()  # or cache.delete_pattern("contract_list_v1_*") if using redis
```

Or set `timeout=300` (5 min) in development to shorten TTL during testing.

### Fix 3 [Frontend] — Sync `inputValue` with `value` prop

**File:** `smartenplus-frontend/components/activities/shared/DayTripLocationSearch.js`

```js
// Add after line 20:
React.useEffect(() => {
  setInputValue(value || '');
}, [value]);
```

### Fix 4 [Frontend] — Emit on input change (freetext search)

**File:** `smartenplus-frontend/components/activities/shared/DayTripLocationSearch.js:26-28`

```js
// BEFORE:
const handleInputChange = (event, newInputValue) => {
  setInputValue(newInputValue);
};

// AFTER:
const handleInputChange = (event, newInputValue) => {
  setInputValue(newInputValue);
  if (event) onChange(newInputValue || null);
};
```

The `if (event)` guard prevents firing during programmatic Autocomplete resets (MUI calls `onInputChange` with `event=null` during internal resets).

### Fix 5 [Frontend] — Clear emits `null` (acceptable, no change needed)

`handleClear` sending `null` is consistent with `useDayTripFilters` which checks `if (filters.location)` before adding to URL. No fix required — null and empty string both treated as "no filter".

---

## Ranked Summary

| Priority | ID | File | Fix |
|----------|----|------|-----|
| P0 | RC-1/Fix 1 | `products/views.py:446-453` | Text-search fallback + primary_location OR join |
| P0 | RC-2/Fix 3 | `DayTripLocationSearch.js:20` | Sync `inputValue` with `value` prop via `useEffect` |
| P0 | RC-3/Fix 4 | `DayTripLocationSearch.js:26-28` | Emit `onChange` in `handleInputChange` |
| P1 | Fix 2 | Django cache | `cache.clear()` after backend deploy |
| P2 | N-3 | `FilterDayTripsPage.js:28-36` | Move `initialLocation` sync into `useDayTripFilters` |
| Backlog | N-1 | `dayTripsApi.js` | NextAuth session → Redux sync (affects authenticated endpoints only) |

---

## Tradeoffs

| Decision | Chosen | Skipped |
|----------|--------|---------|
| Text-search fallback in backend | Yes — zero frontend API change | New `/api/v1/locations/?name=Phuket` lookup + frontend map — extra round-trip, more infra |
| Include `primary_location` in filter OR | Yes — covers DAY_TOUR without `service_areas` set | `service_areas` only — misses contracts admins set primary_location on |
| Emit `onChange` on every keystroke | Yes — RTK deduplication prevents excess calls | Debounce — adds complexity for marginal gain |
| Search `city` + `province` fields | Yes — user might type "Phuket Province" | `location_name` only — misses partial name matches |

---

## Consequences

- After Fix 1 + cache clear: location text search works for any contract with `service_areas` or `primary_location` set
- Admin must ensure DAY_TOUR contracts have `service_areas` populated — if both fields are null, contract won't appear in location searches (data quality issue, not code)
- Fix 4 (freetext emit) makes search feel instant — no need to press Enter or select from dropdown

---

## Related

- [[activities-day-tour-page-review-2026-06-01]] — UX/design/code quality audit on same page (FQ-0, UX-1 through UX-5 are separate issues)
- [[adr-experiences-nav-category-filtering-2026-05-25]] — Category URL param filter chain (working correctly, not related to this bug)
- [[stations]] — `Location` model: `location_name`, `city`, `province`, `normalized_location_name` fields
- [[backend-architecture]] — `products` app = public API; `operators` app = admin API
