# DRF Nested Serializer Silent EN Fallback — Missing Request Context

## Summary
DRF nested serializers inherit `context` from the outermost serializer — but only if context is passed to that outermost serializer. Omitting `context={'request': request}` causes all nested serializers to default to English, silently, with no error.

## Problem
`products/views.py` `custom_route` action (`/admin-dashboard-routes/home/<from>/<to>/`) called:

```python
contract_serializer = ExteaContractSerializer(
    contract_queryset, many=True)  # ← no context
```

Chain: `ExteaContractSerializer` → `ExtraTripSerializer` → `RouteSerializer`.

`RouteSerializer.to_representation()` calls `request_language(self.context.get('request'))`. With no context, `self.context.get('request')` = `None` → `request_language(None)` returns `'en'` → the `if lang != 'en':` guard never fires → `translated_departure_station` / `translated_arrival_station` never injected.

The station name translations were prefetched (lines 1862–1863 already had the correct `prefetch_related`) — they just were never consumed.

## Fix
```python
contract_serializer = ExteaContractSerializer(
    contract_queryset, many=True, context={'request': request})
```

One argument. Commit `b5bb84f` on `fix/route-serializer-translated-station-names` → merged to `smartenplus-backend` develop 2026-10-07.

## Pattern Rule
**Every outermost serializer call in a view must pass `context={'request': request}`.** If any nested serializer uses `self.context.get('request')` for language, auth, or URL resolution, omitting context at the top silently breaks all of them. There is no error — the serializer runs with default/fallback values.

## Related FE Fix
`RouteDepartureInfo.js` + `RouteArrivalInfo.js` — both use `r.translated_departure_station || r.departure_station` (FE commit `b9317d4d`).

## Related
[[route-info-station-i18n-missing-context]] · [[serializer-field-omission-starves-ui]] · [[trip-route-page-seo-aeo-geo-audit]]
