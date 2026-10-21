# BE ticket — `BookingPDFViewSet` has no access control

**STATUS 2026-10-21: FIXED in BE `develop` (`0394977`, merge `8f02428`), NOT pushed, NOT deployed. DEPLOY GATE below.**

## Summary
`bookingsummary/{slug}/bookingpdf/` returns full booking JSON to anyone who has the slug. The slug is only `urlsafe_base64` of the booking id, so it is guessable, not a secret. Found 2026-10-21 during i18n M5c-2 slice c; demonstrated live in Chrome (HTTP 200, full JSON, `Allow` includes POST).

## Where
`smartenplus-backend/bookings/views.py:117` `BookingPDFViewSet`:
- no `permission_classes` (settings have no default permission, so DRF default = AllowAny)
- filters by `urlsafe_base64_decode(slug)` only
- is a `ModelViewSet`, so GET/POST (and presumably PUT/PATCH/DELETE) are routed

## Callers
- BE code: only `apis/urls.py` (import + register) and `bookings/views.py`. No `reverse()`, no tests, none in admin-dashboard.
- FE: `pages/bookings/[bookingId]/download.js` was the only caller. Deleted on FE `develop` (`ac71e8be`) but **STILL ON `main` (prod)** and fetches `.../bookingpdf/` (line 52). So prod FE calls it today.
- FE ticket page `/bookings/[id]/pdf` uses `bookingdetails`, not this endpoint.

## Required (pick one of 1 or 2, then 3 and 4)
1. **Delete** the viewset and its route (preferred: no callers).
2. Or mirror `BookingDetailsViewSet` (`views.py:97`): authenticated user gets own bookings, staff all, guest must send `?email=` equal to `order__email`, else `queryset.none()`. Guests cannot be forced to log in, so email-match is the floor.
3. Make it read-only (`ReadOnlyModelViewSet` or `http_method_names = ['get']`).
4. Test whether a guest can mutate with PUT/PATCH/DELETE/POST today. **Untested**; if yes, this is a data-integrity bug, raise severity.

## Not in scope of the i18n work
Pure backend change. FE needs no change if option 1 is taken.

Related: [[i18n-rollout-plan]] (M5c-2 slice c row).

## Severity (proven 2026-10-21 in a throwaway Django test, no real data)
Anonymous client, slug only, no login, no email: GET list 200, GET detail 200, **PATCH 200, DELETE 204 (booking row deleted)**, PUT/POST 400 (validation only). So any guest could edit or delete any booking. HIGH.

## Done
Deleted `BookingPDFViewSet`, its import and route; dropped unused `urlsafe_base64_*` import. Tests `bookings.tests.RemovedBookingPdfRouteTest` (2): old URL 404 for GET/POST/PUT/PATCH/DELETE on list and detail; `bookingdetails` guest needs matching `?email=`, stranger user gets empty. Full BE suite 1464 tests, failing set identical to baseline (6 fail + 87 err, all pre-existing).

## DEPLOY GATE (hard)
Do NOT deploy BE until: (a) FE `develop`→`main` deployed with `smartenplus_next_cache` cleared; (b) `git ls-tree main` shows no `download.js`; (c) short wait for stale browser tabs/caches; (d) no email/PDF/link points to `/bookings/<id>/download` (these 404 after the FE deploy). Order: FE first, then BE.

## Stale docs (not edited)
`CLAUDE.md.original.md:312`, `docs/operations/BOOKINGS_REFACTOR_PLAN.md:34,460-472,663`, `BOOKINGS_REFACTOR_TEST_PLAN.md:38,114,308`.

## Follow-up
Same hole on `BookingDetailsViewSet` -> [[be-bookingdetails-write-methods-ticket]] (also FIXED, BE develop `637773a`).
