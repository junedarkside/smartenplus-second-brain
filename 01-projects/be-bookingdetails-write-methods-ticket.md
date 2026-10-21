# BE ticket — `BookingDetailsViewSet` allows guest PATCH/DELETE

## Summary
`bookings/views.py:98` `BookingDetailsViewSet` is `AllowAny` + `ModelViewSet`. Read access is gated (auth owner / staff / guest `?email=` == `order__email`), but write methods are routed on the same queryset. Proven 2026-10-21 (throwaway Django test, no real data): guest with slug + matching `?email=` gets **PATCH 200 and DELETE 204 (booking deleted)**; PUT/POST 400 (validation only). The email is not a secret (it is in confirmation emails, and may be known to others), so this is a data-integrity hole. Found while fixing [[be-bookingpdf-permission-ticket]].

## Callers
FE only reads: `store/api/bookingsApi.js:79` `getBookingDetail` (GET) and `hooks/useBookingData.js`. Admin-dashboard: no use. No FE write found.

## Required (all done)
1. Make it read-only (`ReadOnlyModelViewSet` or `http_method_names = ['get', 'head', 'options']`). Verify no other client (mobile? none known) writes through it.
2. Regression test: guest/stranger PUT/PATCH/DELETE/POST -> 405, booking unchanged; authenticated owner too unless a write is needed.
3. Deploy with the BE batch; no FE dependency (FE only GETs).

Status 2026-10-21: **FIXED** in BE `develop` (`728bd13`, merge `637773a`), NOT pushed, NOT deployed. `BookingDetailsViewSet(ReadOnlyModelViewSet)`; tests `bookings.tests.BookingDetailsReadOnlyTest` (writes -> 405 for guest/owner/stranger on list+detail, row unchanged; reads still gated). Test verified to FAIL without the fix. Full BE suite 1466 tests, failing set == baseline (6 fail + 87 err, pre-existing). No FE dependency (FE only GETs). Not checked live (dev BE was not running).
