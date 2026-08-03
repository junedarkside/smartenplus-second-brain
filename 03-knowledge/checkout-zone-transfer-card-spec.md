# Checkout zone-transfer item card — 3-agent debate + spec

**Problem (user-reported 2026-08-03):** checkout cart item card for an airport-transfer ZONE booking shows `contract.trip.departure_station → arrival_station` + date (generic station route, "Hatyai Airport → George Town") instead of the user's TYPED address + the direction they chose (From⇄To swap). A directional lie on a pre-payment surface. 3 surfaces affected: `EnhancedTripCard.js:294-303` (cart card), `TripsConfirmation.js:13-15,66-70` (confirmation), `CartDetailDisplay.js:237-238` (sidebar). Address surfaces only as an editable field deep in Passengers step (`Passengers.js:1014-1030`), never as confirmed display. Team = UXUI (ux-research) + BD (business-analyst) + senior FE (code-reviewer).

## Data flow (verified)
- Book → `checkoutActions.saveTripInfo({itemId, tripData})` (`ZonePriceBox.js:71-91`) → Redux `state.checkout.tripInfo[itemId]` = `{pickupPoint OR dropoffPoint, +lat/lng}`. Selector `selectTripInfo(itemId)` (`checkout-slice.js:146`). **Card never calls it.**
- Discriminator: `selectTripInfo(item.id)` truthy pickup/dropoff → zone booking; else station route.
- Direction: tab0 airport-pickup → typed addr = `dropoffPoint` (airport→address); tab1 → `pickupPoint` (address→airport).

## Debate convergence (all 3)
Card MUST show, before pay: (1) typed address, (2) REAL direction, (3) vehicle+seats, (4) date, (5) fixed price. **Highest-ROI fix + biggest abandonment risk (unanimous) = DIRECTION INVERSION** — user who swapped to "Hotel→Airport" seeing "Airport→Hotel" won't pay. One ADAPTIVE card (branch only the route-display block; header/date/price/actions unchanged → 0 regression for normal trips). Klook/Welcome Pickups/Booking Taxi all treat the typed address as the booking identity, vehicle as secondary, and NEVER show the zone/route name to the customer.

## Senior-FE risk findings (design agents MISSED — load-bearing)
1. ✅ Redux `checkout` IS redux-persist'd (`store/index.js:173` whitelist) → works guest + auth same-session.
2. ⚠️ **BIGGEST REAL RISK — guest→auth cart merge changes `item.id`** (`carts serializers.py:739-866` makes new CartItem rows). `stashTripInfo` keyed to OLD id → `selectTripInfo(newId)=undefined` → card silently falls back to station route, address lost. Guests log in at checkout → hits real customers.
3. ⚠️ Address NOT on `CartItemSerializer` (fields = id/traveling_date/contract/ratecard/sub_total/user/pax). `CartItemCheckoutInfo` model HAS pickup/dropoff but only via `/carts/{id}/checkout-info/`, not on the item → Redux is the ONLY current FE source (not durable across merge/refresh-before-autosave).
4. ⚠️ Direction inference fragile: guard TRUTHY not mere presence (empty-string case). **Fix: stash explicit `direction` field in `ZonePriceBox` (1 line)** — deterministic.
5. ⚠️ `EnhancedTripCard` NOT memo'd → adding `useSelector` re-renders all cards on any checkout mutation. Add `React.memo`.
6. ⚠️ Refresh-before-autosave race: hard-refresh at checkout → backend-load overwrites Redux stash with `pickupPoint:''`. Card blanks.

## Spec (FE-only, ranked)
1. ★ Address + correct direction on `EnhancedTripCard` — `useSelector(selectTripInfo(item.id))`, `isZoneBooking = isTransportation && truthy(pickup||dropoff)`, branch route block: vertical From→To (airport pill UPPERCASE + address sentence-case 2-line clamp; `isAirportFirst = truthy dropoffPoint`), vehicle · seats, "Fixed price: THB X" (NOT "from"), date+year, dep_time if truthy, "Zone Transfer" chip, SUPPRESS zone route name. Fallback → station route if no tripInfo.
2. Explicit `direction` stash field (1 line, prereq for #1 robustness).
3. Same fix on `TripsConfirmation` (prop-thread from `Confirmation.js` which already reads Redux).
4. vehicle+seats+"Fixed price"+date-year+dep_time (all in `item.contract`).
5. `CartDetailDisplay` sidebar.
6. `React.memo` on `EnhancedTripCard`.

## Needs-BE (deferred, flagged — decision: FE now, log BE)
- **Durable address across guest→auth merge:** write address to backend at add-to-cart (PATCH `/carts/{id}/checkout-info/` in `ZonePriceBox.onSuccess`) + re-key `CartItemCheckoutInfo` on cart merge. Without it the Redux fix silently no-ops for the guest-login-at-checkout cohort. **S-M.**
- Expose pickup/dropoff (or `is_zone_contract` flag) on `CartItemSerializer` for a durable server read + fallback warning. **S.**
- `views.py:580-593` autosave loop drops coord fields (lat/lng), only saves point strings. **S.**

## DO-NOT (dark patterns)
Station→station as confirmed route w/o direction qualifier · bury address in expandable · "from THB X" on a fixed-price zone booking · infer direction from contract station order (read the stash / explicit field).

Related: [[airport-transfer-detail-conversion-spec]] · [[adr-airport-transfer-zone-pricing]] · plan `~/.claude/plans/check-vault-and-create-composed-pond.md`
