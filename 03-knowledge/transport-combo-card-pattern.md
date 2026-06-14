# Transport Combo Card Pattern

## Summary
MUI icon mini-cards for transport combination filter — visual identity over text pills.

## Problem
`TransportationOptionsFilter.js` used horizontal pill buttons showing raw API strings like "Speedboat (Express) + Van (Standard)". No visual differentiation from sort pills above. Technical vehicle class suffixes irrelevant to travelers.

## Decision
Replace pills with mini-cards: MUI icon row + clean label. Different visual language from sort pills (which remain pills). Section hidden when ≤1 combo — no UI for non-decisions.

## Icon Map
Derived from `type_class.toLowerCase()` per leg in `transportation_com[]`:

| type_class contains | Icon |
|---|---|
| speedboat / speed boat / ferry | `DirectionsBoatFilledOutlined` |
| van / minivan | `AirportShuttleOutlined` |
| bus | `DirectionsBusOutlined` |
| private / car / transfer | `DirectionsCarFilledOutlined` |
| fallback | `CommuteOutlined` |

## Label Rule
Join `type_class` values title-cased with ` + `. Drop `(Express)`/`(Standard)` vehicle class — too technical.

## Visibility Rule
- Zero combos → `return null`
- 1 combo (prod) → `return null` (no choice = no UI)
- 1 combo (dev) → show via `process.env.NODE_ENV !== 'development'` guard

## Active State
`border-2 border-[#3b5998] bg-blue-50` + checkmark badge `absolute top-1.5 right-1.5 w-4 h-4 rounded-full bg-[#3b5998]`. Icons: `color: #3b5998`.

## Inactive State
`border-2 border-gray-200 bg-white`. Icons: `color: #9CA3AF`.

## Props Interface (unchanged)
```js
TransportationOptionsFilter({ availableOptionsData, selectedOption, onSelectionChange })
```
`getDisplayStringFromOption` export preserved — used by `useTripFilters.js`.

## Related
- `components/trips/TransportationOptionsFilter.js` — implementation (`496c74a`)
- [[trip-search-results-implementation-plan-2026-06-14]] — R2 context
- [[activities-sort-filter-ux]] — sort pill pattern (different visual language)
