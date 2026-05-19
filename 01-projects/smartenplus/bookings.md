# Bookings — Reservation System

## Summary
Booking system. `BookingItem` is central — represents one booked trip/service. Created from `CartItem` on order. `finalize_payment()` → `confirm_booking_items_for_order()` sets items to Confirmed. Add-on pricing frozen at booking time.

---

## Models

### BookingItem
One booked service per order. Links to Order, Contract, CartItem, TimeSlot.

**Statuses (VALID_BOOKING_TRANSITIONS):**
- `Pending → {Confirmed, Canceled}`
- `Confirmed → {No Show, Partially Refund, Fully Refund, Canceled}`
- `No Show`, `Partially Refund`, `Fully Refund`, `Canceled` — terminal (empty transition set)

**Status machine:** enforced in `clean()` only (admin saves). Direct `.save()` bypasses guards.

**Fields:**
- `slug` — auto-generated via `pre_save_slug_field`. Unique.
- `traveling_date`, `selected_time_slot` (FK to `operators.TimeSlot`)
- `adult`/`child`/`infant` — passenger counts
- `confirm` — boolean (separate from `booking_status`)
- `operator`, `contract_name`, `route_name`, `departure_station`, `arrival_station`, `departure_time`, `arrival_time` — denormalized at booking time
- `note`
- `booking_status` — default `Pending`
- `review_invited` — whether review email sent (for `send_review_invitation_emails` task)
- `passenger_ids` (JSON) — list of assigned passenger IDs
- `passenger_details` (JSON) — denormalized `{firstname, lastname, age_category}` for templates
- `rate_cards` — M2M to `Contract_RateCard` via `BookingItem_Contract_RateCard`
- `addons` — M2M to `ContractAddon` via `BookingItemAddon` (frozen pricing)
- `info_fields` — FK to `InfoFields` (flight/pickup/dropoff)
- `ticket` — GenericRelation to Ticket
- `history` — HistoricalRecords audit trail

**Key property:** `total` — cached sum of `quantity × selling_rate` from `BookingItem_Contract_RateCard` entries.

**Confirmation flow:** `finalize_payment()` → `confirm_booking_items_for_order()` → sets `booking_status='Confirmed'`, `confirm=True`.

### BookingItem_Contract_RateCard
Links BookingItem to Contract_RateCard. Stores `quantity` (passenger count per rate type) and `is_active`. Rate card snapshot — frozen at booking time.

### BookingItemAddon
Frozen add-on pricing. Links BookingItem to `operators.ContractAddon`. Stored fields: `addon_name`, `addon_type`, `quantity`, `price_at_booking`, `price_type`. `@property subtotal` — `price_at_booking × quantity`.

### BookingRateCard
Rate snapshot per booking. Fields: `attribute` (rate type), `bar_rate`, `selling_rate`, `currency` (default THB), `currency_rate` (default 1), `quantity`.

### InfoFields
Flight/pickup/dropoff info per booking item. Fields: `departureairline`, `departureflightnumber`, `departureflighttime`, `arrivalairline`, `arrivalflightnumber`, `arrivalflighttime`, `pickuptime`, `pickuppoint`, `dropofftime`, `dropoffpoint`, `extrainfo`.

### BookingPassengerDetail
Passenger data per booking. Fields: `first_name`, `last_name`, `passportid`, `nationality`, `datofbirth`, `confirm`. Links to BookingItem.

### ExtraItem
Extra items per order (e.g., extra baggage, upgrades). `extra_item_status`: Confirmed, Pending, No Show, Canceled Partially Refund, Canceled Fully Refund, Canceled None Refund. M2M to BookingItem via `booking_items`. Slug auto-generated.

---

## Lifecycle

1. **Cart** — user builds cart (`CartItem` with add-ons)
2. **Order submitted** — `POST /api/orders/`, `Order` created with `status=ordering`
3. **Payment** — `POST /payments/order-charge/`, charge created
4. **Payment confirmed** — `finalize_payment(order)` → `confirm_booking_items_for_order()` → creates `BookingItem` from `CartItem`, sets `booking_status='Confirmed'`, `confirm=True`, clears cart
5. **Post-confirmation** — `send_booking_confirmation_email`, Telegram notification, `send_booking_data` to dispatch endpoint

---

## Celery Tasks

- **`send_review_invitation_emails`** — sends review invite for `traveling_date = yesterday`. Deduplicates by `slug`. Uses `@log_email_event(email_type='review')` guard.

---

## Related
- [[backend-architecture]]
- [[operators]] (Contract, TimeSlot, ContractAddon)
- [[cart]] (CartItem → BookingItem conversion)
- [[payment-system]] (finalize_payment → confirm_booking_items_for_order)