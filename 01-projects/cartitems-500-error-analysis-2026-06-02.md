# CartItems 500 Error — Production Bug Analysis

## Summary

**RESOLVED 2026-06-02.** `POST /carts/{id}/cartitems/` returned HTML 500 when booking day-trip/experience contracts. Root cause: `contract.trip = None` on non-transport contracts → `AttributeError` in `check_advance_hour()` → unhandled → Django HTML 500.

## Context

Reported 2026-06-02. Production URL: `https://api.smartenplus.co.th/carts/c8b48780-7178-4950-acec-925595f9e2f8/cartitems/`

RTK Query error object:
```
status: 'PARSING_ERROR'
originalStatus: 500
data: Django HTML 500 page
error: "SyntaxError: Unexpected token '<'..."
```

## Atoms Extracted
- [[view-utility-call-exception-wrapper]] — the `try/except → ValidationError` pattern at view boundary
- [[contract-trip-null-non-transport-pattern]] — `contract.trip` null-guard (covered in detail below)

## Root Cause (Confirmed)

### Real Cause — `contract.trip = None` in `check_advance_hour()`

`carts/views.py:143` calls `check_advance_hour(contract_id, traveling_date_str)` inside `get_serializer_class()` with no exception guard.

`carts/utils.py:591`:
```python
trip_departure_time = contract.trip.departure_time  # CRASH if contract.trip is None
```

Day-trip/experience contracts (`DAY_TOUR`, `SPA_WELLNESS`, etc.) have `trip = None` — the admin action `sanitize_category_fields()` explicitly sets `trip=None` for all non-transport contracts. `None.departure_time` → `AttributeError` → unhandled → Django 500 HTML page (not JSON, because DRF only catches its own exceptions).

**Evidence:** `operators/models.py:232` — `trip = ForeignKey(..., null=True, blank=True)`. `operators/admin.py:985` — `sanitize_category_fields()` clears `trip` for non-transport categories.

## Fix Applied — `9ef2752` (backend develop, merged main 2026-06-02)

**`carts/utils.py:591`** — one-line null guard:
```python
# Before
trip_departure_time = contract.trip.departure_time
# After
trip_departure_time = contract.trip.departure_time if contract.trip else None
```
Fallback already present at line 592-593: `None` → defaults to `time(6, 0, 0)`.

**`carts/views.py:143`** — exception wrapper at call site:
```python
try:
    advance_ok = check_advance_hour(contract_id, traveling_date_str)
except Exception:
    logger.exception("[CartItem] check_advance_hour crashed for contract_id=%s", contract_id)
    raise ValidationError("Unable to validate booking time. Please try again.")
```
Future crashes in `check_advance_hour` now return JSON 400, not HTML 500.

## Vault Corrections (original analysis had errors)

### Bug 1 — WRONG — guard already existed
Original claim: `isLoading` not passed → button clickable during fetch → stale ratecards sent.
**Reality:** `PremiumBookingPanel.js:58` and `DayTripMobileBookingBar.js:166` both hide widget entirely (not just disable) while `isLoading`. Guard was already correct. No fix needed.

### Bug 2 — FALSE ALARM — backend always returns `id`
`ContractRateCardSerializer` fields: `['id', 'rate_date', 'ratecard', 'selling_rate', 'bar_rate']`. Backend always returns `id`, never `pk`. `.id ?? .pk` fix unnecessary.

### Bug 3 — REAL but secondary
`DayTripBookingWidget.js:338`: `error.status >= 500` fails silently when RTK sets `status = 'PARSING_ERROR'` (string). Error masking — not the cause of 500, just hides it. **Not fixed this session** — deferred.

### Bug 4 — NEW (dev-only edge case)
`shouldSkipInitialFetch = !!initialContract && !selectedDate`. If `initialContract = null` (unbuilt slug), query fires without date → empty ratecards → `contract_ratecard: []` → 500. Low priority, dev-only.

## Remaining Open Items

| # | Item | Priority |
|---|------|----------|
| Bug 3 | Fix `PARSING_ERROR` catch in `DayTripBookingWidget.js:338` | P1 |
| Bug 4 | Guard `initialContract = null` + empty ratecards path | P3 |

## Related

- [[cart]] — CartItem model, cartitems endpoint
- [[nextjs-isr-ratecard-empty-array-guard]] — similar stale data guard
- [[payment-checkout-architecture-audit]] — error handling patterns
- [[view-utility-call-exception-wrapper]] — the `try/except → ValidationError` pattern (new atom)
- [[contract-trip-null-non-transport-pattern]] — the `contract.trip` null-guard pattern
