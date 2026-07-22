---
name: station-mapping-seat-api-visibility
description: Station Mapping admin page shows which operator/API a mapping serves (Seat API chip + grid column + per-station filter); serializer fields that back it. Shipped #260.
metadata:
  type: project
---

# Station Mapping — Seat-API Visibility + Per-Station Filter

## Summary

The Station Mapping admin page (`admin-dashboard` `pages/routemanagement/operators/station-mapping/index.js`) now answers three questions a mapping row couldn't before: **which operator's external API is this ID for, is that mapping actually used, and which operators is a given internal station mapped to.** Shipped #260 on `feat/mapping-dialog-supabase` → develop.

## Context — the fan-out invariant

One internal `Station` (pure geography, no operator field) fans out to **many** `OperatorStationMapping` rows, one per operator:
```
Station "Hatyai Airport" (id 3)
   ├─ (Silaphat,  station=3) → "8"
   ├─ (lomprayah, station=3) → "8"   ← same pier, different operator = different external ID
   └─ (OperatorX, station=3) → "..."
```
`unique_together(operator, our_station)` caps it at one ID **per operator** per station. At seat-check time, `operator = contract.seat_check_operator or contract.operator` picks the single row for the resolved operator (see [[seat-availability-reseller-operator-gap]]). The mapping's operator column IS the bind between an `operator_station_id` and a specific operator's API.

## What shipped

**Backend** (`operators/serializers.py`):
- `OperatorSerializer` — added `seat_availability_api_url` to `Meta.fields` (was omitted → dashboard couldn't tell which operators are seat-checkable).
- `OperatorStationMappingSerializer` — added `operator_seat_api_url` (`source='operator.seat_availability_api_url'`) + `operator_has_api` (`SerializerMethodField` → `bool(obj.operator.seat_availability_api_url)`).
- `OperatorStationMappingViewSet.get_queryset` — added `?our_station=` filter (alongside existing `?operator=`).

**Frontend** (`station-mapping/index.js`):
- Add/Edit dialog: on operator pick, show a **Seat API chip** — `Seat API` (green + URL) if the operator has a URL, or `No API` warning ("mapping won't be used for live checks").
- Grid: **Seat API** column, `Live`/`None` chip per row from `operator_has_api`.
- **Filter by station** dropdown (reuses already-loaded `stations` list) → pick a pier to see every operator mapped to it with their external IDs.

## Why it matters

Before this, the "Operator Station ID" was a blank free-text box with no signal about which operator's API it served or whether that operator even had an API. A mapping under an API-less operator was invisible dead weight. Now the operator column + Seat API chip answer "which operator/API" and "is it used"; the station filter answers "which operators serve this pier."

## Not built (deferred)

**Part B — Supabase autocomplete for `operator_station_id`.** Would fetch an operator's real station IDs from Supabase `RouteID` when picked, turning the free-text box into a freeSolo Autocomplete (manual entry preserved). Blocked: anon key can't read `RouteID` (project exposes schema `api`, anon has zero table grants; service-role withheld as a security boundary). Requires a **backend proxy** (service-role, `Accept-Profile: public`, mirror `cs/supabase_client.py`). See [[station-mapping-multi-operator-design]].

## Related

[[seat-availability-reseller-operator-gap]] · [[station-mapping-multi-operator-design]] · [[admin-dashboard-contracts]]
