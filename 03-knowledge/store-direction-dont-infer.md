# Store direction explicitly — don't infer from which field is filled

**Principle:** when a booking/record has a directional meaning (airport→address vs address→airport, pickup vs dropoff), store direction as ONE explicit enum field at the point of intent. Do NOT re-derive it downstream from "which of pickup/dropoff is populated."

**Why the infer pattern is an anti-pattern (SmartEnPlus airport-transfer, #283):**
- Ambiguous edges: both-filled or both-empty = undefined direction. A contract with both `pickup_point` + `dropoff_point` info_fields leaves empty strings → inference guesses wrong.
- Implicit coupling: every consumer (checkout card, confirmation, sidebar, BE booking, ops/driver dispatch) must independently re-implement the same "if dropoff filled → airport-first" rule. Miss it once → wrong direction → driver sent to the wrong end. Payment/ops-adjacent, invisible to unit tests.
- No single source of truth.

**How it manifested here:** zone pricing encoded direction ONLY by which coord slot was filled — FE Redux `tripInfo` (pickupPoint vs dropoffPoint) AND BE `CartItemCheckoutInfo` (pickup_point vs dropoff_point). `resolve-zone` is direction-agnostic (airport+lat/lng only). Contract trip is fixed airport↔X. So direction was a purely-derived concept with no stored field anywhere.

**The fix (best practice):** one `direction` CharField enum (`airport_to_address` / `address_to_airport`), captured at Book:
- FE: `ZonePriceBox.stashTripInfo` writes `direction` into Redux `tripInfo` (alongside the coord slot, kept for backward compat).
- BE: `CartItemCheckoutInfo.direction` (checkout display truth) + **`InfoFields.direction`** (the BOOKING record = ops/driver source of truth). Persisted in BOTH write paths (`carts/views.py` autosave loop + `carts/utils.py` cart→booking create). Migrations carts 0017 + bookings 0048.
- Read it, don't re-infer. Guard truthy fallback to old point-presence only for legacy rows without the field: `tripInfo.direction ? direction === 'airport_to_address' : !!tripInfo.dropoffPoint`.

**Companion — identify the airport end structurally, not by string-match:** to frame ANY airport transfer as "Hatyai Airport (HDY) → X" (even route-list bookings with no typed address), expose `station_type` + `iata_code` on the trip serializer (fields already on Station model). FE `helpers/airportTransfer.js getAirportEnd(trip)` → `{airportName, airportIata, otherName, isAirportDeparture}` if either end `station_type==='airport'`. Do NOT string-match name contains "AIRPORT" (fragile, i18n-breaking, fails on "ANY HOTEL" ends).

**Card display priority (checkout):** zone typed-address > airport-framed (route-list) > raw station route > trip name. Degrades safe: no station_type from BE → getAirportEnd null → current behavior, no crash.

Related: [[checkout-zone-transfer-card-spec]] · [[station-type-airport-first-class-iata-restriction]] · [[adr-airport-transfer-zone-pricing]]
