# Recommendation Type Selection by Service Category

## Rule

At checkout, recommendation type depends on cart composition — NOT a single fixed type.

```
transport items in cart  → last transport item → type='packages'
no transport, has activity → first non-skip item → type='activity'
event/attraction only   → skip query entirely
```

## Why not `similar`

`similar` = same arrival station, any departure. After same-route filter, returns 0 for transport carts. User already chose route — showing route variants is irrelevant.

## Why not `alternatives`

`alternatives` = same exact route, different operator. Always filtered by same-route rule → always 0.

## Type → function mapping

| type | function | returns |
|---|---|---|
| `packages` | `find_package_contracts` | Return trip + onward connections |
| `activity` | `find_activity_contracts` | DAY_TOUR/SPA/etc at arrival location |
| `similar` | `find_similar_contracts` | Same arrival, any departure (transport only) |
| `hybrid` | all combined | Mix — used by post-booking only |

## Non-transport cart anchor

For DAY_TOUR/SPA-only carts, `type='activity'` is used. Dispatch branches on source contract type:
- Has `trip.route.arrival_station` → `find_activity_contracts()` (transport→activity)
- No arrival_station → `find_nearby_activities()` (activity→activity via `primary_location`)

See [[activity-to-activity-cross-sell]] for full dispatch logic + scoring.

## Type → function mapping (updated 2026-06-11)

| type | function | returns |
|---|---|---|
| `packages` | `find_package_contracts` | Return trip + onward connections |
| `activity` (transport source) | `find_activity_contracts` | DAY_TOUR/SPA/etc at arrival_station location |
| `activity` (activity source) | `find_nearby_activities` | DAY_TOUR/SPA/etc at primary_location |
| `similar` | `find_similar_contracts` | Same arrival, any departure (transport only) |
| `hybrid` | all combined | Mix — used by post-booking only |

## Context
SmartEnPlus checkout cross-sell, 2026-06-10. Updated 2026-06-11.
