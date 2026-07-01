# CS Flat-Dict List Endpoint Pattern

## Summary
Staff-only list endpoints in the `cs` app return flat lists of plain dicts (no DRF serializer) for command-centre table consumption.

## Context
Command-centre tabs (OTA Bookings, Direct Bookings) render MUI tables from a flat row shape. Heavy nested serializers (`AdminBookingSummarySerializer`) are wrong-shaped — paginated, nested, missing flat fields (id, email, route/category). Public catalog filters also silently ignore params ([[public-api-filter-silent-ignore]]).

## Pattern
`APIView` + `IsAdminOrIsStaff`, `get()` returns a list comprehension of plain dicts:
```python
class XListView(APIView):
    permission_classes = [IsAdminOrIsStaff]
    def get(self, request):
        qs = Model.objects.select_related('user', 'order').all().order_by('-date', '-id')
        return Response([{'id': o.id, 'slug': o.slug, ...} for o in qs])
```
Denormalized fields used directly (no join). Derived fields (customer_name/email/pax from `passenger_details` JSON) via null-guarded module helpers that return `None`, never raise (CLAUDE.md helper rule).

## When to use
- Staff admin table needing a flat, unpaginated row.
- Examples: `OtaBookingListView` (cs/views.py:422), `BookingItemListView` (cs/views.py).

## Tradeoffs
- **Pro:** zero serializer boilerplate, exact client shape, cheap query.
- **Con:** no pagination/validation/browsable-API; field list duplicated client+server (keep in sync manually).
- **Don't use** for public endpoints or write paths.

## Related
[[command-centre-direct-notify-redesign]] · [[public-api-filter-silent-ignore]]
