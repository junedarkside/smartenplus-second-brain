---
name: seat-availability-reseller-operator-gap
description: Reseller contracts (SmartEnPlus reselling Lomprayah) can't seat-check because mapping lookup hardcodes contract.operator; fix = seat_check_operator FK on Contract.
metadata:
  type: project
---

# Seat-Availability — Reseller Operator Gap

> **STATUS: SHIPPED → develop 2026-07-22 (#260)** (both repos, pushed — BE `5baebe8`, AD `3fc14e0`). Migration `0069` (add `seat_check_operator`). All gotchas below folded in. **Follow-up shipped same session:** `Contract.seat_availability_api_url` override **REMOVED** (migration `0070`) — only 1/81 contracts used it, redundant now that `seat_check_operator` resolves the URL from the source operator. Resolution simplified to `api_url = (operator.seat_availability_api_url or '').strip() or None` (also strips whitespace → fixed a broken GET from a trailing-space URL). The `contract.seat_availability_api_url or ...` fallback references below are now historical. **Not on main yet** — E2E + deploy pending. See [[station-mapping-seat-api-visibility]].

## Summary

`check_seat_availability` resolves station mappings + external API against `contract.operator` only. A reseller contract (operator = SmartEnPlus, reselling Lomprayah's seats) has no Lomprayah mappings under `operator=SmartEnPlus` → returns `MAPPING_NOT_FOUND`, or sends SmartEnPlus's own IDs to Lomprayah's API → silent wrong result. Fix: add nullable `seat_check_operator` FK on `Contract`; resolution uses `contract.seat_check_operator or contract.operator`.

## Context

Two operator ownership models on the platform:

- **Model A — own transport + own API** (Lomprayah, Boon Siri, ~200 contracts). Own station IDs, own external seat-check API. Works today.
- **Model B — transport + agency at once** (SmartEnPlus, Silaphat, ~200 reseller contracts). A *separate* SmartEnPlus contract resells Lomprayah's seats and must check against **Lomprayah's** station IDs + API — not its own.

`Route` has NO operator field (`products/models.py:22`, pure geography: 2 Station FKs), so routes/stations are shareable across operators — a reseller contract can point at the same Route as the source.

## How It Works (easy mode)

A contract is one product staff sell. Two kinds re: live seat check:

- **No external API** — no live check. Seat checker returns `available: null` + "No availability API configured". Not an error, just no live data. Availability handled manually. Most contracts.
- **With external API** — "Check Operator Seat Availability" box on the admin contract page. Pick date → ask the operator's API "seats left?" → green (available) / red (sold out). Needs 3 things: station mapping (our pier → operator's pier ID), API URL, and a trip/route (from-station + to-station + time).

The gap: a **reseller** contract (SmartEnPlus selling Lomprayah) must ask **Lomprayah** using **Lomprayah's** pier IDs + API. Today the code always asks using the contract's OWN operator → SmartEnPlus has no Lomprayah IDs → fails. Fix = a "Seat Check Operator" dropdown: leave empty for own products, set to Lomprayah for resellers.

### Flow — the admin seat check

```
Staff opens contract → clicks "Check Seat Availability" (date)
        │
        ▼
  contract.trip exists?  ──no──►  NO_TRIP ("transport contracts only")
        │ yes
        ▼
  operator = contract.seat_check_operator OR contract.operator   ◄── the whole fix
        │        (set = reseller borrows source)  (empty = own product)
        ▼
  mapping (operator, dep_station) + (operator, arr_station) found?
        │
        ├── no ──►  MAPPING_NOT_FOUND ("configure in Station Mapping page")
        │
        ▼ yes
  api_url = contract.seat_availability_api_url OR operator.seat_availability_api_url
        │
        ├── none ──►  200  available:null  ("No API configured")   ◄── "without API" contract
        │
        ▼ has url
  GET  {api_url}?from={dep_id}&to={arr_id}&date=&time=
        │
        ├── network/HTTP fail ──►  502  OPERATOR_API_ERROR (+ debug_url)
        │
        ▼ ok
  parse data[0].seatStatus  →  "Sold Out" = red / else green / empty = warning
```

### Two contract types side by side

```
  WITHOUT external API                WITH external API (Model A own / Model B reseller)
  ────────────────────                ─────────────────────────────────────────────────
  seat_availability_api_url = ∅       seat_availability_api_url = set (or on source operator)
  seat_check_operator       = ∅       seat_check_operator = ∅ (A)  /  = Lomprayah (B)
  station mapping           = none    station mapping under the resolved operator
        │                                   │
        ▼                                   ▼
  check → available:null              check → live green/red from operator API
  (sell manually)                     (stop-sell on Sold Out)
```

## Impact on existing frontend (search + book) — NONE

Verified against `smartenplus-frontend`:
- Frontend has **zero** references to `check-seat-availability` / `seat_check_operator` / `checkSeatAvailability` (grep = 0). The seat check is an **admin-dashboard-only** tool; the public site never calls it.
- New field is **nullable, defaults NULL**. Every existing contract keeps identical behavior: `NULL or contract.operator` = `contract.operator`. Model A untouched.
- Booking guard gates on `contract.is_actived` (`carts/utils.py:62`), NOT on seat availability. Search/book never reads `seat_check_operator`.
- Migration = add-nullable-column (metadata-only ALTER), no data change, no read-path break.

Customers on smartenplus-frontend search + book exactly as before. The field only changes what the admin seat-check button resolves to.

## Problem

`operators/views.py:982` sets `operator = contract.operator` and uses it in three places:
- mapping lookup dep (`:991`), mapping lookup arr (`:999`)
- api_url fallback (`:1016` — `contract.seat_availability_api_url or operator.seat_availability_api_url`)

The contract-level `seat_availability_api_url` override (commit b1996c7) patched the **API side** for resellers, but the **station-mapping side stays bound to `contract.operator`**. `OperatorStationMapping.unique_together = (operator, our_station)` (`models.py:1203`) means Lomprayah's IDs live under `operator=Lomprayah`; a SmartEnPlus reseller can't reach them. Confirmed no existing `source_operator`/reseller field (grep = 0).

## Decision

**Keep `OperatorStationMapping`, add `seat_check_operator` FK on `Contract`.** Rejected "direct from/to IDs on contract" — at 400+ seat-checkable contracts over ~15 shared piers that's ~800 manual entries + 200× duplication vs ~30 mapping rows. FK is robust whether or not the reseller shares the source's route:
- shares Lomprayah route/stations → mapping `(Lomprayah, station)` hits directly
- own Station rows → add mappings under `(Lomprayah, that_station)` once; resellers still enter zero IDs

Resolution becomes `operator = contract.seat_check_operator or contract.operator` — one line covers both mapping lookups + api_url fallback.

## Implementation gotchas (from team review)

- **`ContractDetailViewSet.update()` is a manual field-by-field update** (`views.py:455-970`), NOT DRF default deserialization. A new FK is silently dropped on PATCH unless an explicit block is added (mirror the `operator`/`trip` blocks). This is the single most important trap — see [[api-mirroring-pattern-new-features]].
- **FE camel→snake conversion lives in one place:** `contractUtils.js transformContractFormValues` (~:82). Without adding `seat_check_operator` there, Django ignores the camelCase key.
- Serializer `ContractDetailSerializer` uses `fields='__all__'` — reads auto-covered as bare FK int; add `seat_check_operator = OperatorSerializer(read_only=True)` for nested name on GET.
- `Contract` uses `django-simple-history` → migration also touches `HistoricalContract`.
- Endpoint permission is `IsAuthenticated`, NOT admin-only, despite the `admin-dashboard-operators/` prefix.
- **Silent-misconfig:** `seat_check_operator` set but source operator lacks `seat_availability_api_url` (no contract override) → 200 `available: null`, not an error.

## Supabase multi-operator note

Supabase `RouteID` table (`npehhtcobshckhefrqhw.supabase.co/rest/v1/RouteID`) now has a live `Operator` column (shipped 2026-07-22), multi-operator, filterable — all current rows = **`Lomprayah`** (canonical name finalized by Supabase team; match the exact `Operator` model row when implementing). This is the **population source** for `OperatorStationMapping` (manual now → auto-sync now unblocked but unbuilt, see [[station-mapping-multi-operator-design]]). **Does NOT change this fix:** `seat_check_operator` resolves *which operator's* mappings to borrow; it's independent of *how* those mapping rows get filled (manual vs Supabase sync). Reseller staff still enter zero station IDs — they only pick the source operator.

## Tradeoffs

- FK approach = ~30 mapping rows, resellers add zero IDs, single source of truth; source renumber = edit 1 row. Cost: 1 new nullable FK + 1-line view change + manual `update()` block + FE select.
- Direct-on-contract (rejected) = zero mapping table, self-contained contract, no FK — but ~800 manual entries + 200× duplication at this scale.

## Related

[[station-mapping-multi-operator-design]] · [[admin-dashboard-contracts]] · [[api-mirroring-pattern-new-features]] · [[master-state]]
