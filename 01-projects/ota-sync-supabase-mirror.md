---
name: ota-sync-supabase-mirror
description: P2 — read-only mirror of Supabase public.view_information (12Go+Klook OTA bookings) into Django CsOtaBooking via server-side PostgREST. Manual batch first. Awaiting review.
metadata:
  type: project
  status: awaiting-review
  date: 2026-06-23
  parent: ota-portal-overview
---

# P2 — OTA Sync: Supabase → Django Mirror

## Summary
Read-only sync of OTA bookings from standalone Supabase (`public.view_information`, 561 records) into a new Django `cs.CsOtaBooking` model, so staff + the OTA portal can query them. Supabase stays source-of-truth; Django **never writes back**. Server-side `requests` → PostgREST (no SDK, no new dep).

## Context
Supabase is a disconnected island ([[supabase-ota-booking-store]]). Before staff or OTA travelers can act on OTA bookings, Django needs a local mirror. No customer-facing surface yet (P3a adds it) — this phase is the data foundation.

## Approach
### Config
- Env (backend `Smartenplus/settings.py`): `SUPABASE_URL` (`https://npehhtcobshckhefrqhw.supabase.co`), `SUPABASE_ANON_KEY` (owner-supplied, **never committed**).
- Thin client `cs/supabase_client.py`: `requests.get(f"{SUPABASE_URL}/rest/v1/view_information?select=*")` with `apikey` + `Authorization: Bearer <anon>` headers.

### `cs.CsOtaBooking` model
Mirror of view_information, normalized. `unique_together = ('source', 'booking_id')` (upsert key). Fields: `source` (12go/klook), `booking_id`, `booking_date`, `booking_time`, `customer_name`, `email` (`db_index` — merge + portal lookup), `phone`, `destination`, `status` (normalize `✅Confirmed`/`❎Canceled` → confirmed/canceled), `passenger_names`, `class_type`/`participant`/`vehicle_type` (nullable per schema), `created_at`, `supabase_ingested_at`.

### `sync_ota_bookings`
- Celery task + management command (`cs/management/commands/sync_ota_bookings.py`). **Manual batch first** (vault S5); Beat + `-Q sync` worker only if measured load demands it.
- Upsert by `(source, booking_id)`. Apply data-quality filters ([[supabase-ota-booking-store]]): exclude `Date='N/A'` (Klook) + `'5000-08-02'` (12Go); strip Operator CRLF; tolerate cross-schema nulls.
- Idempotent + logged (upserted/skipped/excluded counts).

### Staff OTA view
Drop OTA bookings into the **same command-centre queue** as direct (P1 spine). Read-only from mirror; relay-to-OTA actions stay manual (request-based workflow).

### Identity merge (probabilistic)
OTA `email` ↔ `Account.email`. 20–40% noise (booker ≠ traveler). Document merge rules; no deterministic promise; no write-back field on Supabase.

## Files
- **BE new:** `cs/models.py` (`CsOtaBooking`), `cs/migrations/`, `cs/tasks.py` (`sync_ota_bookings`), `cs/management/commands/sync_ota_bookings.py`, `cs/supabase_client.py`.
- **BE config:** `Smartenplus/settings.py` (`SUPABASE_*`).
- **Admin:** command-centre OTA queue view (drops into P1 queue).

## Risks / tradeoffs
- **Probabilistic merge** — 20–40% miss; acceptable for ops, not for "one customer" promises.
- **Manual sync lag** — bookings can be stale until next batch run; acceptable pre-portal-launch.
- **Anon-key exposure** — anon key stays server-side only; never ships to client (RLS on Supabase must permit anon read of `view_information` only).
- **Date filter at fetch layer (decision 2026-07-02)** — `?Date=gte.{today}` applied in `_fetch_schema()`. Past bookings excluded permanently from mirror; full re-sync needed to recover historical data. Intentional: command-centre OTA tab shows upcoming + today only.

## Review focus
- Is `(source, booking_id)` the correct upsert key, or should it be `booking_id` alone (Bookaway shares `12GO*` prefix)?
- Manual-batch-first vs Beat from day 1 — confirm cadence with owner.
- Should the mirror denormalize into `Order`/`BookingItem`, or stay a standalone `CsOtaBooking` (recommended — keeps OTA data quarantined from direct-order state machine)?

## Verification
- Run `sync_ota_bookings` → assert ~561 upserts, 0 dupes on `(source, booking_id)`, `N/A`/`5000-08-02` excluded, Operator CRLF stripped.
- Re-run → idempotent (0 new inserts).
- Anon key not present in any client bundle (grep).

## Related
[[ota-portal-overview]] · [[supabase-ota-booking-store]] · [[booking-command-centre-decision]] · [[cs-api-contract]]
