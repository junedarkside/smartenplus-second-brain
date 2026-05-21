# Operators — Tour Service System

## Summary
Service providers, tour contracts, availability slots, add-ons, translations. `service_category` determines behavior: TRANSPORTATION uses `Contract_TranspotComposit` (vehicle-based), DAY_TOUR/MULTI_DAY_TOUR uses `TimeSlot`/`ContractAddon`/`ContractTranslation`.

## Models

### Operator
Service provider. `operator_name`, `contact_person`, `email`, `phone_number`, `address`, `country` FK, `logo_url`, `description`, `is_serviced`, `cancellation` M2M, `image`, `mapped_op_id` (legacy).

### Contract
Tour package. Central model.
- **Links:** `trip` FK, `operator` FK, `timeline`, `checkin_info` M2M
- **Type:** `JOIN` (per-person), `PRIVATE` (per-vehicle), `CHARTER` (per-vehicle)
- **Availability:** `operational_day` M2M, `start_date`, `end_date`, `advance_hr` (default 48h), `stop_sale_dates` M2M
- **Capacity:** `booked_count`, `daily_counter`, `Contract_TranspotComposit.vehicle_seat` (TRANSPORT); `TimeSlot.max_capacity` (tours)
- **Rate:** `ratecard` M2M via `Contract_RateCard` (`bar_rate`, `selling_rate`, `rate_date` nullable=default, `is_active`). Historical via `simple-history`.
- **Tour fields:** `service_category`, `tour_duration_days`, `tour_highlights`, `inclusions`, `exclusions`, `difficulty_level`, `age_restriction`, `what_to_bring`
- **Meeting point:** `meeting_point_type` (HOTEL_PICKUP/MEET_ON_LOCATION/SPECIFIC_POINT), `meeting_point_details`, `meeting_point_place` FK
- **Flags:** `instant_confirmation`, `mobile_ticket_enabled`

**Service categories:** TRANSPORTATION, DAY_TOUR, MULTI_DAY_TOUR, SPA_WELLNESS, EVENT_TICKET, ATTRACTION_TICKET, FOOD_DINING, ACCOMMODATION, TRANSFER, OTHER.

**Audit:** `created_by`/`updated_by` (Account FK), `history` (HistoricalRecords).

### Contract_RateCard
Pricing per rate type. `ratecard` FK → RateCard (ADULT/CHILD/INFANT/VEHICLE). `selling_rate` = customer price. `rate_date` nullable — null = default. Unique: `(contract, ratecard, rate_date)`.

### Contract_TranspotComposit
TRANSPORTATION contracts. Links Contract to TransportComposit (vehicle_type + class). `vehicle_seat`: max passengers (Van:7, Bus:40, Ferry:200). `qty = ceil(passengers / vehicle_seat)`.

**Admin fix (2026-05-19):** Frontend sends `id: -1` sentinel for new rows. Backend must branch `id > 0` before `get_or_create()`. New → `create()`. Existing → `get_or_create(id=...)`. Sentinel never as PK.

### TimeSlot
DAY_TOUR/MULTI_DAY_TOUR. Per-session availability.
- `start_time`, `end_time`, `display_name`
- `max_capacity`, `operational_days` M2M, `price_override`, `is_active`, `sort_order`
- `get_current_bookings(date)`, `is_available(date, people)`

### ContractAddon
Optional add-ons. `addon_type`: AUDIO_GUIDE, MEAL_UPGRADE, PHOTO_PACKAGE, EQUIPMENT_RENTAL, PRIVATE_GUIDE, TRANSPORTATION, TRAVEL_INSURANCE, EXTRA_LUGGAGE, VIP_UPGRADE, SKIP_LINE, OTHER. `price_type`: PER_PERSON, PER_GROUP, FLAT_FEE. `calculate_price(people)`.

### ContractTranslation
12 languages: en, th, zh, ja, ko, es, fr, de, ru, ar, ms, vi. Fields: `name`, `description`, `tour_highlights`, `inclusions`, `exclusions`, `what_to_bring`, `meeting_point_details`, `confirmation_message`.

### Asset Registry
`Asset`: canonical asset, SHA-256 dedup. `OperatorImageGallery`: operator images with soft-delete. `image_hash` (MD5), `is_deleted`, `deleted_at`. Admin hard-delete → S3 delete → `usage_count` atomic decrement.

## Capacity Calculation
**TRANSPORTATION:** `qty = ceil(passengers / vehicle_seat)`. **DAY_TOUR:** Check `TimeSlot.max_capacity` per session.

## Celery Beat Tasks
- `reset_daily_counter` — midnight. `daily_counter` → `booked_count`, reset.
- `soft_delete_expired_ratecards` — 1am. `is_active=False` where `rate_date < today`.

## Related
- [[backend-architecture]]
- [[bookings]]
- [[cart]]
- [[payment-system]]
