# BE ticket — `BookingPDFViewSet` has no access control

## Summary
`bookingsummary/{slug}/bookingpdf/` returns full booking JSON to anyone who has the slug. The slug is only `urlsafe_base64` of the booking id, so it is guessable, not a secret. Found 2026-10-21 during i18n M5c-2 slice c; demonstrated live in Chrome (HTTP 200, full JSON, `Allow` includes POST).

## Where
`smartenplus-backend/bookings/views.py:117` `BookingPDFViewSet`:
- no `permission_classes` (settings have no default permission, so DRF default = AllowAny)
- filters by `urlsafe_base64_decode(slug)` only
- is a `ModelViewSet`, so GET/POST (and presumably PUT/PATCH/DELETE) are routed

## Callers
None active. FE `pages/bookings/[bookingId]/download.js` (the only caller, unauthenticated) was deleted in `ac71e8be`. Not used by admin-dashboard. Only an old backend test doc mentions it. The FE ticket page `/bookings/[id]/pdf` uses `bookingdetails`, not this endpoint.

## Required (pick one of 1 or 2, then 3 and 4)
1. **Delete** the viewset and its route (preferred: no callers).
2. Or mirror `BookingDetailsViewSet` (`views.py:97`): authenticated user gets own bookings, staff all, guest must send `?email=` equal to `order__email`, else `queryset.none()`. Guests cannot be forced to log in, so email-match is the floor.
3. Make it read-only (`ReadOnlyModelViewSet` or `http_method_names = ['get']`).
4. Test whether a guest can mutate with PUT/PATCH/DELETE/POST today. **Untested**; if yes, this is a data-integrity bug, raise severity.

## Not in scope of the i18n work
Pure backend change. FE needs no change if option 1 is taken.

Related: [[i18n-rollout-plan]] (M5c-2 slice c row).
