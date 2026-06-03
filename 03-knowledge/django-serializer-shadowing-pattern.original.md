# Django Serializer Shadowing Pattern

## Summary
A local `class StationSerializer` defined in `products/serializers.py` silently shadows the imported `StationSerializer` from `stations/serializers.py` — exposing a different subset of fields with no error.

## Problem
`products/serializers.py` imports `StationSerializer` from `stations.serializers` (line 4) but then redefines the class name at line 696:

```python
from stations.serializers import StationSerializer  # full serializer: fields='__all__'
# ... 690 lines later ...
class StationSerializer(serializers.ModelSerializer):  # local override: only {location, slug}
    location = LocationSerializer(source='location_name')
    class Meta:
        model = Station
        fields = ['location', 'slug']
```

`HomeSerializer` (line 706) uses the local one — returns `{location: {location_name, ...}, slug}` only. No `station_name`, no `iata_code`.

## Consequence
Frontend code reading `departure_station.station_name` or `departure_station.iata_code` gets `undefined`. Card components silently return `null` (via guard `if (!airportName || !destination)`) — no error thrown, just empty UI.

## Detection
Symptom: section header renders but zero cards show. Root cause NOT obvious from frontend alone — requires `curl /front-page/` and inspecting actual JSON shape.

## Fix Applied (2026-05-30)
`AirportTransferRouteCard.js` reads `departure_station?.location?.location_name` (not `station_name`). See commit `1eec0aa`.

## Related
- [[airport-transfer-redesign-2026]] — where this was discovered
- `products/serializers.py:696` — local StationSerializer definition
- `products/serializers.py:706` — HomeSerializer using it
