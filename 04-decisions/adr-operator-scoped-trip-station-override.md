# ADR: Operator-Scoped Trip Times & Own-Station Override

## Status
proposed — 2026-07-22 (plan only, no code shipped)

## Context

`Contract.trip` is a shared FK (`operators/models.py:237`, `related_name='contract_trip'`) — many Contracts point at one `Trip`. `Trip` owns `departure_time`/`arrival_time` (`products/models.py:105-106`); `Trip.route → Route` owns `departure_station`/`arrival_station` (`products/models.py:24-27`) as pure geography with **no owner**.

**Consequence today:** editing a Trip's time or a Route's station in the admin dashboard mutates the shared row and **ripples to every sibling Contract**. There is no per-operator override layer.

**Business driver (user, 2026-07-22):** operators must set their OWN trip times AND their OWN check-in station. Example: Lomprayah checks customers in at their own office, not a generic shared bus station. Different operators run the same route geography with different departure times and different physical check-in points. Hard constraint: **all existing data must keep working unchanged** in admin dashboard + customer frontend + booking (~20 FE read sites depend on `contract.trip.departure_time` as `"HH:MM:SS"` and `trip.route.departure_station` as a name string via `StringRelatedField`).

Distinction clarified during analysis: `Place` (`stations/models.py:150`) = a counter/desk *inside* a station (pickup point, already has `owner` FK). `Station` = the departure point itself — and an operator's office can BE their station, but `Station` has no owner today.

## Decision

Three nullable, additive fields. Existing NULL rows resolve exactly as today; new operator-scoped trips carry their own time + station without touching siblings.

1. **`Trip.operator`** FK → Operator (nullable, SET_NULL, indexed). NULL = shared/legacy trip; set = operator-scoped. Operator owns the **time** at Trip level (time is what ripples).
2. **`Trip.departure_station` + `Trip.arrival_station`** FK → Station (nullable, SET_NULL). Station **override**. NULL = use `trip.route`'s stations (today's behavior); set = operator's own check-in station. Route stays shared geography, untouched.
3. **`Station.owner`** FK → Operator (nullable, SET_NULL) — mirrors existing `Place.owner` (`stations/models.py:168`). NULL = public/shared; set = operator's private office/pier.

**Resolution SSOT** — read-only properties on `Trip`: `effective_departure_station = departure_station or route.departure_station` (same for arrival). Serializers, seat-check, and any future FE resolve through these — never re-implement the fallback inline. Seat check (`operators/views.py:~997`) switches from `route.departure_station` to `trip.effective_departure_station`, so an operator-owned station maps under the correct operator via `OperatorStationMapping` (operator resolution `contract.seat_check_operator or contract.operator` unchanged — see [[seat-availability-reseller-operator-gap]]).

**Backward-compat mechanism:** serializer resolves the override into the *existing* keys (Phase B patches `trip.route.departure_station` to the override name string when set), so the customer FE ships unchanged through the admin-dashboard rollout. Times untouched.

## Alternatives Considered

1. **Operator at Station level only** — rejected. Two operators use the same physical pier; per-operator external IDs already handled by `OperatorStationMapping`. Doesn't fix the *time* ripple, which is the actual pain.
2. **Operator at Route level (fork route per operator)** — rejected. Route = pure shared geography by design; adding operator there breaks intentional route reuse across operators and multiplies route rows. Not where the ripple originates.
3. **Per-contract time override columns on Contract** — viable but rejected as primary. Puts time on Contract while stations still live two hops away on Route; splits ownership awkwardly and doesn't give operators a clean "their trip" entity. Trip-level operator + station override keeps one coherent operator-owned Trip.
4. **Chosen: nullable Trip.operator + Trip station override + Station.owner** — accepted. Additive, backward-compatible, no serializer rename, FE unchanged through Phase C. Time owned where it ripples (Trip); station stays shared geo except explicit operator override.

## Tradeoffs
- **Gained:** operators set own time + own check-in station; sibling contracts isolated; zero-downtime additive migration; FE untouched through admin rollout; seat-check correctness for owned stations.
- **Lost:** two ways to express a station now exist (route station vs trip override) — must always resolve via `effective_*` to avoid drift.
- **Risk:** `TripDashBoardViewSet.update` (`products/views.py:1033`) is hand-rolled and silently drops unhandled payload keys — new Trip fields need explicit write-wiring or they won't save. Duplicate-trip check (`~1061`) may falsely block an operator's same-route/time variant → extend filter with `operator`. FindTrip cache signal keys on route location, not override (fine for current scope).

## Consequences
- Migrations: `stations` (Station.owner) then `products` (3× Trip AddField). All `null=True`, reversible, no backfill — `Trip.operator` stays NULL = shared for legacy rows.
- Seat check resolves effective stations → owned-station mappings work under `seat_check_operator or operator`.
- Admin dashboard trip form gains operator selector + optional own-station override + a "this shared trip affects N contracts" guardrail (warn, not block) on shared-trip edits; station form gains an owner field.
- Rollout is 4 independently-shippable phases (BE model+seatcheck → serializer resolution → AD forms+guardrail → optional FE display). FE deploy only needed for optional owned-station display.
- Full implementation plan: `~/.claude/plans/check-vault-and-be-tranquil-umbrella.md`.

## Related
- [[seat-availability-reseller-operator-gap]] — reseller `seat_check_operator` FK; same operator-scoping thread, reused for mapping resolution
- [[station-mapping-multi-operator-design]] — `OperatorStationMapping` per-operator external station IDs; owned stations resolve through it
- [[station-mapping-seat-api-visibility]] — station mapping admin UX
- [[adr-contract-soft-delete]] — Contract model conventions (is_actived/is_deleted invariant)
