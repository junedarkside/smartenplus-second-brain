---
name: activities-location-search-backend-text-id-type-mismatch
description: Backend expects `location_id` (string UUID) but frontend sends text string. Type mismatch causes 400 errors. Backend `products/views.py:446` filters by UUID, receives freeform location name.
metadata:
  type: knowledge
  status: active
  date: 2026-06-22
  parent: activities-location-search-bug
---

# Activities Location Search — Backend Text/ID Type Mismatch

## Summary
Backend expects `location_id` (UUID string) but frontend sends freeform text (location name). Type mismatch → 400 errors. `products/views.py:446` filters by UUID, receives location name.

## Why It Matters
Location search always fails. User types "Chiang Mai" → backend gets `"Chiang Mai"` → filters `Station.id::eq` against UUID → zero results.

## Detail
**Backend code (bug):**
```python
# products/views.py:446
def search_locations(request):
    location_id = request.data.get('location_id')  # Expects UUID
    stations = Station.objects.filter(id=location_id)  # FAIL on text
```

**Frontend sends:**
```jsx
// DayTripLocationSearch.js:20
const handleLocationSelect = (locationName) => {
  setSearchParams({ location: locationName });  // Sends "Chiang Mai"
  // Backend expects: location_id: "uuid-123-456"
};
```

**Fix backend (accept text OR ID):**
```python
location_text = request.data.get('location')  # Freeform name
location_id = request.data.get('location_id')   # UUID

if location_text:
    stations = Station.objects.filter(
        Q(name__icontains=location_text) |
        Q(place__name__icontains=location_text)
    )
elif location_id:
    stations = Station.objects.filter(id=location_id)
```

**OR fix frontend:** Send `location_id` when user selects, not text.

## Constraints / Gotchas
Database has `name` (string) + `place__name` (text search). Partial matches (`__icontains`) more user-friendly.

## Related
- [[activities-location-search-inputvalue-divergence]] — companion bug
- [[activities-location-search-bug]] — parent audit (3 critical bugs)
