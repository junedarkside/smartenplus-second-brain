# ExteaContractSerializer — No Ratecard Field

## Summary
`ExteaContractSerializer` (used by `/admin-dashboard-routes/home/{from}/{to}/`) has no `ratecard` field. Frontend components using `contracts[]` from this endpoint cannot derive price directly.

## Details

`ExteaContractSerializer` fields:
```python
fields = ['id', 'slug', 'operator', 'trip', 'type', 'is_actived', 'start_date', 'end_date']
```

`AvialableContractSerializer` fields (used by `data[0].avaliable_routes[]`):
```python
fields = ['slug', 'name', 'operator', 'ratecard', 'trip', 'end_date']
```

Both serializers share the same `slug` field on `Contract` model.

## Price Source Pattern for ISR-Rendered Components

Build a `slug → minPrice` map from `data[0].avaliable_routes[]`:

```js
const priceBySlug = {};
(data[0]?.avaliable_routes || []).forEach(r => {
  const defaultRates = (r.ratecard || []).filter(
    rc => rc.rate_date === null &&
    (rc.ratecard === 'ADULT' || rc.ratecard === 'VEHICLE') &&
    parseFloat(rc.selling_rate) > 0
  );
  const min = Math.min(...defaultRates.map(rc => parseFloat(rc.selling_rate)));
  if (isFinite(min)) priceBySlug[r.slug] = min;
});
```

Then: `priceBySlug[contract.slug]` gives the stable baseline price.

## Why `rate_date === null`

`ratecard[]` contains two types:
- `rate_date=null` — default/baseline rate, applies year-round
- `rate_date='2025-12-25'` — date-specific override (peak season, holidays)

ISR-rendered "from" prices should show year-round baseline only. Date-specific rates belong to the live RTK Query (`tripsFilterSet.min_rate`), not static pages.

## Related
- `products/serializers.py` — `ExteaContractSerializer` line ~968, `AvialableContractSerializer` line ~771
- `components/trips/TripSummary.js` — uses this pattern (`priceBySlug`)
- [[isr-client-rtk-stats-seo-pattern]]
