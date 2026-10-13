# Shared Transfer Seat Cap Fix

## Summary
FE only. `BookButton` no longer caps JOIN (per-person) bookings by the smallest leg's `vehicle_seat`. PRIVATE/CHARTER stay capped. Merged to FE `develop` 2026-10-13 (`20be3c87`), not deployed. Follow-ups (vehicle quantity, price row) below, also merged, not deployed.

## Context
Staff report "Multi-Vehicle Capacity for Shared Transfers": Koh Mook Any Hotel -> Koh Lipe, taxi leg 2 pax per vehicle + speedboat leg 75 seats. A 5-person JOIN booking was blocked because the smallest leg (taxi = 2) capped the whole booking.

## Problem
`findMinVehicleSeat(contract.transport_composit)` returns the minimum seat over all legs. `BookButton` compared total pax to it for every contract type. For JOIN the price is per person (ADULT/CHILD/INFANT ratecards), so a small leg must not cap pax.

## Decision
- JOIN: not capped. PRIVATE/CHARTER: capped as before (`total <= minSeat`).
- Dropped as over-engineering (user decision): "Boat seats left" hint, "Vehicles needed" line, overbooking guard. We do not control operator seat inventory. Ops do stop-sell, admin updates.
- BE work from the first attempt (`transport_availability.py`, TimeSlot availability) was reverted. BE tree == pre-feature `482e71e`.

## Details
- `helpers/transferSeats.js` -> `exceedsSeatLimit(contract, total, minSeat)`. Type = `contract.tour_type || contract.type` (same as `convertData`, keeps day-tour behaviour).
- `components/UI/BookButton.js:162` -> `if (!exceedsSeatLimit(contract, total, minSeat))`.
- Tests: `__tests__/components/UI/BookButton.test.js` (JOIN 5 pax adds, PRIVATE over cap toasts `alert seat is limit to book`, CHARTER within cap adds), `__tests__/helpers/transferSeats.test.js`. 6 pass. 39 FE suites fail identically on clean develop (pre-existing).

## Verification (local browser, 2026-10-13)
Leg `vehicle_seat` set to 2 temporarily, then restored to 10.
- Contract 1 (JOIN, slug `GV6BatJ8ld`), 4 adults, Mon 2026-10-19: item added, THB 3,960 (4 x 990).
- Contract 143 (PRIVATE), 4 pax on a 2-seat leg: toast `alert seat is limit to book`, cart unchanged.
- Oct 13-14 show "Not available for this date" (advance hours). UI max is 9 pax.

## Open
- Admin check: is the Koh Mook -> Lipe contract `type` JOIN? If PRIVATE/CHARTER the 2-pax cap still applies by design.
- Not tested: one contract with both a 2-seat taxi and a 75-seat boat (fix does not depend on leg count).

## Follow-up: PRIVATE/CHARTER quantity by vehicle + pax cap 30 (2026-10-13, merged, not deployed)
FE `feat/private-vehicle-quantity`: commit `7fd0e9f4`, merged to `develop` `01c47c98`. BE `fix/cart-merge-vehicle-quantity`: commit `fe13557`, merged to `develop` `35b9dc3`.
- BE already recomputed vehicle quantity (`calculate_vehicle_quantity_for_group_bookings`, first leg by `order`). Only FE blocked it.
- Rule: more than one vehicle only when all legs have the same `vehicle_seat` (`hasUniformVehicleSeats` in `helpers/transferSeats.js`). Mixed legs (taxi 2 + boat 75) keep the old cap, because the VEHICLE rate meaning (per trip or per leg) is unconfirmed.
- Pax cap: `MAX_PASSENGERS_TOTAL = 30` in `helpers/passengerCapacity.js` replaces JOIN 9 per type and picker total 9. Non-transport JOIN still respects `max_participants`.
- Cart line and checkout summary used `quantity: 1` for PRIVATE/CHARTER; now use the VEHICLE quantity. Also recommendation modal and checkout picker price.
- BE: login-merge path (`update_cartid`) now uses the first-leg function; before it took the last leg and could divide by zero. 3 new tests in `carts/tests.py`.
- Browser check (legs set to 2 seats, then restored to 10): contract 143 PRIVATE 4 pax = quantity 2, 2,400 THB; 12 pax = quantity 6, 7,200 THB, checkout not blocked. Contract 1 JOIN 12 adults added, 11,880 THB.
- Tests: 25 new/updated FE tests pass; FE 39 and BE carts 44 failing tests identical on clean develop.

## Follow-up: cart price row shows vehicles x rate (2026-10-13, merged, not deployed)
FE `fix/private-vehicle-price-row`: commit `d225892a`, merged `af42d193`. Checkout summary showed `Per Group THB 1,200.00` next to a 7,200 total for 6 vehicles.
- `components/cart/CartDetailDisplay.js`: new `GroupRateRows` (group branch extracted; main function was already over ESLint limits). Quantity > 1: `Vehicle / THB 1,200.00 per vehicle`, then `6 x THB 1,200.00  THB 7,200.00`. Quantity 1 or missing: unchanged `Per Group` row. `formatCurrency`, so a zero rate stays `THB 0.00`, not Free.
- UX, UI and SWE agent reviews; wording copies the JOIN row.
- 7 new tests in `__tests__/components/cart/CartDetailDisplay.test.js` (4 fail on old code). Full FE jest: 39 failing suites, same as clean develop.
- Browser check: 12 pax = 6 vehicles = 7,200; 2 pax = 1 vehicle unchanged. Local leg 87 restored to 10 seats.

## Not done (owner questions)
- Is the VEHICLE rate per whole trip or per leg on multi-leg contracts? Check prod admin for live PRIVATE/CHARTER contracts with different leg seats.
- PER_GROUP add-ons stay 1x for N vehicles. Operator email and voucher show no vehicle quantity (`bookings/email_context.py`).
- Should the pricing-type badges say `Per vehicle` instead of `Per Group` (`EnhancedTripCard.js:599`, `Passengers.js:1026`, `EditableCartItem.js:179`)? Left unchanged.
- Infants count toward seats (BE rule). Refund code not reviewed for quantity > 1. Is 30 the right cap?

## Related
[[checkout-flow]] [[cart]] [[bookings]]
