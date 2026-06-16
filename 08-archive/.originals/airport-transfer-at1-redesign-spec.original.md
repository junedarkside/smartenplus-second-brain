# Airport Transfer AT-1 Redesign Spec

## Summary
Full spec for AT-1: professional homepage airport transfer section. Image card + IATA badge + carousel mobile + serializer expansion. Zero impact on other components.

## Context
Extracted from [[transportation-category-audit-2026-05-30]]. Goal: match Grab/Klook/12Go level polish on homepage airport section. Backend adds `station_name` + `iata_code` to local serializer only.

## Details

### Scope

| File | Change |
|---|---|
| `components/airport-transfer/AirportTransferRouteCard.js` | Full visual redesign — image card |
| `lib/homepage/components/AirportTransferSection.js` | Layout upgrade — carousel mobile / grid desktop |
| `products/serializers.py` (backend) | Expand local StationSerializer only |

**Not changed:** all other homepage sections, `homepagev2.js`, detail pages, other airport-transfer components, API URL, Redux, RTK Query.

### Backend: Serializer Expansion

Expand the **local** `StationSerializer` inside `HomeSerializer` scope only (`products/serializers.py:696`). This class is used only by `HomeSerializer` — no shared serializer is touched.

```python
# Add to StationSerializer fields list
fields = ['location', 'slug', 'station_name', 'iata_code']

# Add to HomeSerializer fields list
fields = ['route_name', 'departure_station', 'arrival_station',
          'slug', 'query_count', 'lowest_price', 'operator_count']
```

Both `station_name` and `iata_code` exist on Station model. `route_name` exists on Route. Additive change — no breaking effect.

### New Card: AirportTransferRouteCard

**Design pattern:** GYG split-card (same as `PopularRouteImageCard.js`) — image top + info bottom.

```
┌─────────────────────────────┐
│  [location.image OR         │  ← h-[160px], gradient fallback if no image
│   blue gradient + plane]    │
│  [BKK] badge top-left       │  ← iata_code, bg-fb-blue, text-white, rounded
├─────────────────────────────┤
│  Suvarnabhumi Airport       │  ← station_name, text-sm font-semibold gray-900
│  → Bangkok City Center      │  ← arrival location_name, text-sm gray-500
│  ─────────────────          │
│  2 operators  From THB 450  │  ← footer: operators left, price right
└─────────────────────────────┘
```

Design tokens:
- Card: `bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm hover:shadow-lg`
- Image: `h-[160px] object-cover group-hover:scale-105 transition-transform duration-300`
- Gradient fallback: `bg-gradient-to-br from-blue-900 to-blue-600` + `FlightTakeoffOutlinedIcon` overlay
- IATA badge: `bg-fb-blue text-white text-xs font-bold px-2 py-0.5 rounded absolute top-2 left-2`
- Airport name: `text-sm font-semibold text-gray-900 leading-tight`
- Destination: `text-sm text-gray-500`
- Operators: `text-xs text-gray-400`
- Price: `text-sm font-bold text-gray-900`

Props interface: `{ route, onClick }` — unchanged from today.

### Section Layout Upgrade

- Mobile: horizontal carousel via `CardCarouselContainer` (exists at `components/UI/CardCarouselContainer.js`)
- Desktop lg+: 4-column grid (same as current)
- Card width in carousel: `w-[75vw] sm:w-[45vw] md:w-[30vw] lg:w-full`
- Section header: add subtitle + "View all →" link

```jsx
<header className="flex items-center justify-between pt-2 px-2">
  <div className="flex items-center gap-2">
    <FlightTakeoffOutlinedIcon className="text-gray-600" fontSize="small" />
    <div>
      <h2 className="text-xl font-semibold text-gray-900">Airport Transfers</h2>
      <p className="text-xs text-gray-400 mt-0.5">Private transfers from Thailand's major airports</p>
    </div>
  </div>
  <Link href="/airport-transfer" className="text-xs text-fb-blue font-medium hover:underline">
    View all →
  </Link>
</header>
```

### Null Safety Requirements
- `iata_code` null → hide badge entirely
- `lowest_price` null → "Check price" (existing behavior)
- `location.image` null → gradient fallback
- `station_name` null → fall back to `location.location_name`

### Verification
1. `npm run dev` → homepage loads, section visible
2. Cards show image/gradient, IATA badge, station name, price
3. Null price card shows "Check price" — no crash
4. Card click → `/airport-transfer/{slug}/` → detail page unchanged
5. Mobile: carousel scrolls; desktop: 4-col grid
6. No console errors; other sections unaffected
7. `npm run build` passes

## Related
- [[transportation-category-audit-2026-05-30]] — full category audit + architecture justification
- [[django-serializer-shadowing-pattern]] — why local StationSerializer, not shared
- [[carousel-design-standard]] — Embla carousel patterns
- [[airport-transfer-redesign-2026]] — frontend implementation notes
