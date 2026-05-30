# Cart — Shopping Cart

## Summary
Shopping cart. `Cart` (UUID) → `CartItem` → `Contract` + `TimeSlot` + passengers. `CartItemCheckoutInfo` stores traveler form data (Phase 2 backend checkout persistence, 2026-02-17). Cart converts to `Order` + `BookingItem` via `finalize_payment()`.

---

## Models

### Cart
UUID PK. `version` for optimistic locking. One-to-one `NumberPassenger`, many `Passenger`, many `CartItem`.

### NumberPassenger
Passenger count. One-to-one FK → Cart. Fields: `passenger` (total), `mobile`, `email`.

### Passenger
Individual passenger. FK → Cart. Fields: `first_name`, `last_name`, `date_of_birth`.

### CartItem
Cart item. FK → Cart, FK → Contract, FK → `operators.TimeSlot` (optional, tours), FK → User (nullable, guest).

Fields: `traveling_date`, `adult`/`child`/`infant` (defaults 1/0/0), `is_active`, `cartitem_contract_ratecard` (M2M through `CartItem_Contract_RateCard` with `quantity`).

`addons` relation → `CartItemAddon`.

### CartItem_Contract_RateCard
Through table: CartItem ↔ Contract_RateCard. `quantity` (passenger count per rate type). `is_active`.

### CartItemAddon
Add-on per cart item. FK → `operators.ContractAddon`. `price_at_booking` frozen at add time. `quantity`. `subtotal`: `price_at_booking × quantity`.

Unique constraint: `(cart_item, addon)`.

### CartItemCheckoutInfo
Phase 2 checkout persistence (2026-02-17). Traveler form data per cart item. One-to-one FK → CartItem, FK → User.

**Fields:**
- Trip info: `pickup_point`, `pickup_time`, `dropoff_point`, `dropoff_time`
- Flight: `arrival_airline`, `arrival_flight_number`, `arrival_flight_time`, `departure_airline`, `departure_flight_number`, `departure_flight_time`
- `remark`
- `passengers` (JSON) — `[{uuid, firstname, lastname, birthDate, idNumber, sourceMemberId}]`
- `passenger_assignments` (JSON) — `{"item-id": ["uuid-1", "uuid-2"]}` mapping
- `contact_email`, `contact_phone`

`trip_info` property → structured dict for API responses.

Indexes: `(user, cart_item)`, `updated_at`.

---

## Cart-to-Order Conversion

1. `POST /api/orders/` → `Order` with `status=ordering`
2. `POST /payments/order-charge/` → payment
3. Payment confirmed — `finalize_payment(order)` → `confirm_booking_items_for_order()`:
   - `CartItem` → `BookingItem` (denormalized route/operator/departure/arrival/time fields)
   - `CartItemAddon` → `BookingItemAddon` (frozen pricing)
   - `CartItemCheckoutInfo` passengers → `BookingPassengerDetail`
   - `CartItem` deleted (cart cleared)
   - `Order.status = 'paid'`

---

## Related
- [[backend-architecture]]
- [[operators]] (Contract, TimeSlot, ContractAddon)
- [[bookings]] (BookingItem creation from CartItem)
- [[payment-system]] (finalize_payment clears cart)