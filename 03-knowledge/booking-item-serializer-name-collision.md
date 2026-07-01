# BookingItemSerializer Name Collision

## Summary
`BookingItemSerializer` is defined in **4 separate apps** (`orders`, `bookings`, `tickets`, `dialogue`). A view's `serializer_class = BookingItemSerializer` binds to whichever module the view **imports** from — not the "obvious" one. Adding a field to the wrong class = silent no-op on the response.

## Context
Customer booking page (`/bookings/<slug>`) never showed sent `TripNotification`s even though the data existed + was `prefetch_related`. Session #205/#204 added `notifications` to `bookings.serializers.BookingItemDetailSerializer` — but the customer endpoint (`BookingDetailsViewSet`) actually uses `orders.serializers.BookingItemSerializer` (`bookings/views.py:11`). Field added to the wrong class → dropped from serialization.

## The trap
- `grep "class BookingItemSerializer"` returns 4 hits across apps. Same name, different `Meta.fields`, different fields.
- `bookings.serializers.BookingItemSerializer` is a near-empty stub (`fields=['slug']`); `orders.serializers.BookingItemSerializer` is the rich `__all__` one. Naive grep/read misleads.
- `BookingDetailsViewSet.serializer_class = BookingItemSerializer` looks local but resolves via the view's import line, not definitions in the same file.

## How to avoid
1. **Find the binding, not the class:** to know which serializer a response uses, check the **view's import** (`from <app>.serializers import BookingItemSerializer`) + the view's `serializer_class` line — not a global class search.
2. **Verify empirically:** `python manage.py shell -c "from <app>.views import <ViewSet>; print(<ViewSet>.serializer_class.__module__, <ViewSet>.serializer_class.Meta.fields)"` — resolves the actual bound class.
3. **Confirm the field reaches the wire:** curl the endpoint, grep the response keys. Field-presence unit tests on the *correct* serializer class guard regressions.
4. Long-term: rename to disambiguate (e.g. `orders.OrderBookingItemSerializer`) — but that's a wide refactor (4 apps, many imports). Defer; just document the collision.

## Related
[[cs-flat-dict-list-endpoint-pattern]] · [[command-centre-direct-notify-redesign]]
