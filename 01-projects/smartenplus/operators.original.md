# Operators — Tour Service System

## Summary
Operators app manages service providers, tour contracts, availability time slots, add-ons, and multi-language translations. `service_category` field determines behavior: TRANSPORTATION uses `Contract_TranspotComposit` (vehicle-based), DAY_TOUR/MULTI_DAY_TOUR uses `TimeSlot`/`ContractAddon`/`ContractTranslation`.

---

## Models

### Operator
Service provider. Fields: `operator_name`, `contact_person`, `email`, `phone_number`, `address`, `country` (FK), `logo_url`, `description`, `is_serviced`, `cancellation` (M2M via `Operator_Cancellation`), `image`, `mapped_op_id` (legacy ID mapping).

### Contract
Tour package. Central model. Fields:
- **Links:** `trip` (FK to Trip), `operator` (FK), `timeline`, `checkin_info` (M2M via `Contract_CheckinInfo`)
- **Type:** `JOIN` (per-person), `PRIVATE` (per-vehicle), `CHARTER` (per-vehicle)
- **Availability:** `operational_day` (M2M to `DaysOfTheWeek`), `start_date`, `end_date`, `advance_hr` (default 48h), `stop_sale_dates` (M2M)
- **Capacity:** `booked_count`, `daily_counter`, `Contract_TranspotComposit.vehicle_seat` for TRANSPORTATION; `TimeSlot.max_capacity` for tours
- **Rate:** `ratecard` (M2M to `RateCard` via `Contract_RateCard`). `Contract_RateCard` has `bar_rate`, `selling_rate`, `rate_date` (nullable for default), `is_active`. Historical tracking via `simple-history`.
- **Tour fields** (Phase 1): `service_category`, `tour_duration_days`, `tour_highlights`, `inclusions`, `exclusions`, `difficulty_level`, `age_restriction`, `what_to_bring`
- **Meeting point:** `meeting_point_type` (HOTEL_PICKUP/MEET_ON_LOCATION/SPECIFIC_POINT), `meeting_point_details`, `meeting_point_place` (FK to Place)
- **Flags:** `instant_confirmation`, `mobile_ticket_enabled`

**Service categories:** TRANSPORTATION, DAY_TOUR, MULTI_DAY_TOUR, SPA_WELLNESS, EVENT_TICKET, ATTRACTION_TICKET, FOOD_DINING, ACCOMMODATION, TRANSFER, OTHER.

**Slug:** auto-generated via `pre_save_slug_field` + `unique_slug1()`.

**Audit:** `created_by`/`updated_by` (Account FK), `history` (HistoricalRecords).

### Contract_RateCard
Pricing per rate type. `ratecard` FK → `RateCard` (ADULT/CHILD/INFANT/VEHICLE). `selling_rate` is the customer-facing price. `rate_date` nullable — null = default rate, non-null = date-specific override. `is_active` flag.

Unique constraint: `(contract, ratecard, rate_date)`.

### Contract_TranspotComposit
For TRANSPORTATION contracts. Links Contract to TransportComposit (vehicle_type + vehicle_class). `vehicle_seat` field: max passengers per vehicle (Van: 7, Bus: 40, Ferry: 200). Used in capacity calculation: `qty = ceil(passengers / vehicle_seat)`.

**Admin fix (2026-05-19):** Admin PATCH crashed with `IntegrityError duplicate key id=-1`. Frontend sends `id: -1` sentinel for new unsaved rows. Backend was passing it as PK into `get_or_create(id=-1)` → INSERT with id=-1 → UniqueViolation on any subsequent save.

Fix (`operators/views.py:739-774`): branch on `id <= 0` (new) vs positive id (existing). New rows → `create()` (Postgres assigns real PK). Existing rows → `get_or_create(id=..., contract=...)`. Sentinel never appended to keep-list.

**Pattern:** Frontend sentinel ids (negative or zero) must never be passed as PK lookup keys. Branch on `id > 0` before any `get_or_create()`.

### TimeSlot
For DAY_TOUR/MULTI_DAY_TOUR. Per-session availability with independent capacity.
- `start_time`, `end_time`, `display_name` (e.g., "Morning Tour")
- `max_capacity` — max participants per session
- `operational_days` (M2M to `DaysOfTheWeek`)
- `price_override` — override default contract price for this slot
- `is_active`, `sort_order`

`get_current_bookings(date)` — counts confirmed BookingItems for this slot on date. `is_available(date, people)` — checks capacity against current bookings.

### ContractAddon
Optional add-ons (insurance, luggage, equipment, etc.).
- `addon_type`: AUDIO_GUIDE, MEAL_UPGRADE, PHOTO_PACKAGE, EQUIPMENT_RENTAL, PRIVATE_GUIDE, TRANSPORTATION, TRAVEL_INSURANCE, EXTRA_LUGGAGE, VIP_UPGRADE, SKIP_LINE, OTHER
- `price_type`: PER_PERSON (price × people), PER_GROUP (flat price), FLAT_FEE (one-time)
- `calculate_price(people)` — returns total based on price_type
- `is_optional`, `max_quantity`, `display_order`

### ContractTranslation
Multi-language support. 12 languages: en, th, zh, ja, ko, es, fr, de, ru, ar, ms, vi.
Fields: `name`, `description`, `tour_highlights`, `inclusions`, `exclusions`, `what_to_bring`, `meeting_point_details`, `confirmation_message`.

One translation per (contract, language) pair.

### Stopsale_date
Contract-level blackout dates. `date` field. `Stopsale_date.contract` FK → Contract via `stopsale` related name.

### StopSaleDate
Global blackout dates (not per-contract). Used in `Operator.stop_sale_dates` M2M.

---

## Capacity Calculation

**TRANSPORTATION:** `qty = ceil(total_passengers / vehicle_seat)`. `vehicle_seat` from `Contract_TranspotComposit`.

**DAY_TOUR:** Check `TimeSlot.max_capacity` per session. `qty = ceil(passengers / min_participants)` (from `Contract.min_participants`).

---

## Asset Registry

Asset deduplication + soft-delete system.

### Asset
Canonical asset stored once, referenced by multiple gallery entries. SHA-256 dedup key.

Fields: `id` (UUID), `sha256` (unique, indexed), `storage_path`, `mime_type`, `width`, `height`, `file_size`, `usage_count`, `created_at`, `created_by` (Account FK).

### OperatorImageGallery
Operator image gallery with soft-delete.

Fields: `operator` FK, `image` (ImageField), `description`, `asset` FK (canonical Asset, nullable for migration), `image_hash` (MD5 for dedup), `file_size`, `width`, `height`, `is_deleted` (soft-delete flag), `deleted_at`, `deleted_by` (Account FK), audit trail (`created_at`, `created_by`, `updated_at`, `updated_by`).

**Indexes:** `[image_hash, is_deleted]`, `[operator, is_deleted]`.

**`save()` hook:** auto-calculates `image_hash` + dimensions if missing.

**Hard-delete rules:** Admin hard-delete → signal → S3 delete → `usage_count` atomic decrement. Never hard-delete without `validate-deletion` check.

---

## Celery Beat Tasks

- `reset_daily_counter` — midnight daily. Adds `daily_counter` to `booked_count`, resets counter.
- `soft_delete_expired_ratecards` — 1am daily. Sets `is_active=False` on `Contract_RateCard` where `rate_date < today`.

---

## Related
- [[backend-architecture]]
- [[bookings]] (BookingItem links to Contract)
- [[cart]] (CartItem links to Contract)
- [[payment-system]] (finalize_payment → confirm_booking_items_for_order)