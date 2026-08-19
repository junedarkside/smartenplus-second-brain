# Zone Pricing — General Transfer Extension

## Summary
Extends the existing airport-transfer zone-pricing system ([[adr-airport-transfer-zone-pricing]]) to any transportation contract — point-to-point (e.g. Koh Lipe Pier → any Hatyai hotel), not just airport-anchored. Adds a required pickup/dropoff step at checkout for zone-priced contracts booked without a pre-picked address, and a two-zone rule for routes spanning two different coverage areas.

## Context
The shipped zone system (`TransferZone`/`ZoneContract`/`ZoneAirport`, all in `stations/models.py`) already lets any polygon price any `Contract` via `ZoneContract` — that FK was already generic at the DB layer. But two things kept it airport-transfer-only in practice:
1. `ZoneAirport.airport` hard-requires `station_type='airport'` — a pier, bus terminal, or other fixed station can't anchor a zone.
2. The only entry flow is `/airport-transfer`'s `ZonePriceBox.js` — address picked **before** add-to-cart, checkout just displays it read-only.

User's actual requirement (confirmed across multi-turn clarification, planning session 2026-08-18): a general transportation contract (e.g. Koh Lipe → any Hatyai hotel, or fully point-to-point) should reuse the same drawn polygons, but:
- Booking happens with **no address picked first** — contract has its own normal `Contract_RateCard` price, unchanged.
- **At checkout**, if the contract is zone-priced, two required fields (Pickup Point + Dropoff Point) must be filled and each independently resolved against zone polygons before payment can proceed. This is a **serviceability gate**, never a pricing mechanism — matched zones don't change price.
- Pickup and dropoff can resolve to **different** zones (e.g. Hatyai zone + Songkhla zone) — the contract must be explicitly linked to both; a point matching a zone the contract *isn't* linked to counts as unmatched.
- From/To search/listing pages (`TripItem.js`, `TransportationSearch.js`) stay **completely untouched** — zone logic is checkout-time only, never search/browse-time.

## Decision
Full technical plan (backend/admin/frontend file-by-file, verification steps): `/Users/charuwatnaranong/.claude/plans/check-vault-and-all-eager-octopus.md` (session plan file — copy key sections here if that file is cleared).

Core pieces:
- **New field** `Contract.requires_zone_pricing` (BooleanField) — explicit staff opt-in, not inferred from `ZoneContract` link existence.
- **`ZoneAirport.airport`** — drop `limit_choices_to={'station_type':'airport'}` so any `Station` type (pier, bus terminal) can anchor a zone. No DB migration needed (form-validation-only constraint).
- **`ResolveZoneView`** — `airport` param becomes a generic `station` param (kept as backward-compatible alias, zero change to `/airport-transfer`); adds a two-zone check — each point's resolved zone must be in the *specific contract's* linked-zone set, not just "any active zone."
- **New FE component** `ZonePickupDropoffFields.js` — two required `PlacePicker` fields at checkout, gated `requires_zone_pricing && !isZoneBooking` (the `!isZoneBooking` guard is load-bearing: prevents double-prompting a traveler who already has an address via the existing `/airport-transfer` flow).
- **Checkout `stepValidations`** (`pages/checkout/index.js`) extended to block step-advance until both points resolve.

## Key gotcha (side-effect risk)
A contract reached via `/airport-transfer` already has `tripInfo.pickupPoint`/`dropoffPoint` in Redux before checkout. If that same contract also carries `requires_zone_pricing=True`, checkout must render the **existing** `ZoneTransferRoute` (read-only), never the new required-fields prompt. Precedence: `isZoneBooking` always wins over `requires_zone_pricing`. Missing this guard would double-prompt or conflict — this is the one real regression risk in the whole plan.

## 3 admin linking cases
1. **Airport-transfer** (existing, unchanged): zone + one station pin → checkout shows 1 field.
2. **General transfer** (new): zone, no station pin, contract may link 2+ zones → checkout shows 2 required fields, each checked independently.
3. **Same zone, both**: one polygon linked to two separate `ZoneContract` rows (one pinned, one not) — no redrawing, checkout behavior differs per contract, not per zone.

## Status
**Planned, not yet built.** Plan approved by user 2026-08-18, implementation not started this session. Visual demo (interactive HTML walkthrough) built and iterated across ~15 turns of clarification — covers flow overview, zone-drawing steps, 3 linking cases, Koh Lipe worked example, AD/BE/FE file breakdown, checkout states, out-of-zone alert.

## Related
[[adr-airport-transfer-zone-pricing]] — the original system this extends, Accepted/shipped through §9.
[[airport-transfer-rate-dynamic-pricing]] — resolveZone price vs cart price gap, relevant to date-aware ratecard lookups this plan also touches (`ResolveZoneView`'s date filtering, unchanged by this plan).
