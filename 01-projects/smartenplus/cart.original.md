# Cart — Shopping Cart

## Summary
Shopping cart. `Cart` (UUID) → `CartItem` → `Contract` + `TimeSlot` + passengers. `CartItemCheckoutInfo` stores traveler form data (Phase 2 backend checkout persistence, 2026-02-17). Cart converts to `Order` + `BookingItem` via `finalize_payment()`.

---

## Models

### Cart
UUID primary key. `version` field for optimistic locking. One-to-one `NumberPassenger`, many `Passenger`, many `CartItem`.

### NumberPassenger
Passenger count container. One-to-one FK to Cart. Fields: `passenger` (total), `mobile`, `email`.

### Passenger
Individual passenger. FK to Cart. Fields: `first_name`, `last_name`, `date_of_birth`.

### CartItem
Item in cart. FK to Cart, FK to Contract, FK to `operators.TimeSlot` (optional, for tours), FK to User (nullable for guest).

Fields: `traveling_date`, `adult`/`child`/`infant` (defaults 1/0/0), `is_active`, `cartitem_contract_ratecard` (M2M through `CartItem_Contract_RateCard` with `quantity`).

`addons` relation → `CartItemAddon`.

### CartItem_Contract_RateCard
Through table: CartItem ↔ Contract_RateCard. `quantity` field (passenger count per rate type). `is_active`.

### CartItemAddon
Add-on selected for cart item. FK to `operators.ContractAddon`. `price_at_booking` frozen at time of adding to cart. `quantity`. `subtotal` property: `price_at_booking × quantity`.

Unique constraint: `(cart_item, addon)`.

### CartItemCheckoutInfo
Phase 2 backend checkout persistence (2026-02-17). Stores traveler form data per cart item. One-to-one FK to CartItem, FK to User.

**Fields:**
- Trip info: `pickup_point`, `pickup_time`, `dropoff_point`, `dropoff_time`
- Flight: `arrival_airline`, `arrival_flight_number`, `arrival_flight_time`, `departure_airline`, `departure_flight_number`, `departure_flight_time`
- `remark`
- `passengers` (JSON) — `[{uuid, firstname, lastname, birthDate, idNumber, sourceMemberId}]`
- `passenger_assignments` (JSON) — `{"item-id": ["uuid-1", "uuid-2"]}` mapping
- `contact_email`, `contact_phone`

`trip_info` property returns structured dict for API responses.

Indexes: `(user, cart_item)`, `updated_at`.

---

## Cart-to-Order Conversion

1. `POST /api/orders/` — creates `Order` with `status=ordering`
2. `POST /payments/order-charge/` — initiates payment
3. Payment confirmed — `finalize_payment(order)` → `confirm_booking_items_for_order()`:
   - `CartItem` → `BookingItem` (with denormalized route/operator/departure/arrival/time fields)
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