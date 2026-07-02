---
name: supabase-ota-booking-store
description: Standalone Supabase datastore of OTA (12Go + Klook) bookings + traveler profiles, unified via public.view_information — source-verified 2026-06-20 via live REST API; schema updated 2026-06-22
metadata:
  type: knowledge
  status: active
  date: 2026-06-22
  source: source-verified (live REST API 2026-06-20; view_information SQL 2026-06-22)
---

# Supabase OTA Booking Store

> ✅ **Source-verified 2026-06-20** via live Supabase REST API. **Schema updated 2026-06-22** from `public.view_information` SQL (confirmed `gmailklook` schema + unified view).

## Summary

Standalone **Supabase** system stores OTA bookings + traveler profiles, populated by **parsing OTA booking-confirmation emails**. Two OTA schemas confirmed: **12Go** (`gmail12go`) + **Klook** (`gmailklook`). Unified via `public.view_information` UNION ALL. Purpose is **operational**: one place for all bookings, track status, check who travels on a given date. **Disconnected** from Django backend.

## Unified View

**View:** `public.view_information` (read-only, UNION ALL of both schemas)
**Project:** `npehhtcobshckhefrqhw.supabase.co`
**Auth:** anon JWT key (stored separately — do not commit)

| Column (view) | 12Go source | Klook source | Notes |
|---|---|---|---|
| `source` | `'12go'` (hardcoded) | `'klook'` (hardcoded) | OTA identifier — solved in view |
| `booking_id` | `Booking_ID` | `Booking_ID` | OTA ref (e.g. `12GO29980150`) |
| `booking_date` | `Date` | `Date` | Travel date |
| `booking_time` | `Time` | `Time` | Departure time |
| `customer_name` | `Name` | `Name` | Lead traveler name |
| `gmail` | `Gmail` | `Gmail` | Lead traveler email |
| `phone` | `Phone` | `Phone` | Lead traveler phone |
| `destination` | `Destination` | `Destination` | Route string |
| `status` | `Status` | `Status` | `✅Confirmed` / `❎Canceled` |
| `created_at` | `Created AT` | `Created AT` | Record ingestion date |
| `arrival` | `Arrival` | `null` | Arrival time — 12Go only |
| `class_type` | `Class` | `null` | Service type (Ferry, Van, etc.) — 12Go only |
| `passengers` | `Passengers` | `null` | Pax count emoji string — 12Go only |
| `passenger_names` | `PassengerNames` | `PassengerNames` | All passenger names |
| `participant` | `null` | `Participant` | Lead participant — Klook only |
| `participant_names` | `null` | `ParticipantNames` | All participant names — Klook only |
| `vehicle_type` | `null` | `VehicleType` | Vehicle type — Klook only |
| `set_logs` | `Set-Logs` | `Set-Logs` | Notification sent flag |

## Schema Differences (12Go vs Klook)

Klook uses different passenger model — tour participants + vehicle type vs ferry class + arrival time. Read as `null` cross-schema; Django sync must handle nullable columns.

## Live Stats (source-verified 2026-06-22)

| | `gmail12go` (12Go) | `gmailklook` (Klook) | Combined |
|---|---|---|---|
| **Records** | 58 | 503 | **561** |
| **Confirmed** | 42 | 457 | 499 |
| **Canceled** | 16 | 46 | 62 |
| **Email coverage** | ~93% (54/58 SENT) | **100% (503/503)** | ~99% |
| **Travel date range** | 2026-02-19 → 2027-01-02 | 2026-01-01 → (ongoing) | — |
| **Ingestion range** | 2025-10-30 → 2026-06-15 | 2025-02-01 → 2026-06-19 | — |
| **Top routes** | Langkawi↔Koh Lipe, Koh Lipe↔Telaga Harbour | Koh Lipe↔Langkawi (Kuah+Telaga), Hat Yai Airport Transfer | — |

**Klook `Date` outlier:** some records show `N/A` — data entry error (same pattern as 12Go `5000-08-02`). Exclude before sync.

Klook is the **dominant source** (503 vs 58) with **perfect email coverage** — far larger contact asset than previously known.

## Data Quality Issues (fix before sync)

- `Operator` field (12Go): dirty values `'ensure plus'` + `'Smart En Plus\r\n'` (trailing CRLF). Normalise before read-sync.
- One `Date` = `'5000-08-02'` — data entry error, exclude from sync.
- Cross-schema nulls: `arrival`/`class_type`/`passengers` null for Klook; `participant`/`vehicle_type` null for 12Go — handle in Django sync layer.

## Remaining Gap for CS Centralization

**None.** All gaps closed:

- `source` — solved in view (hardcoded `'12go'`/`'klook'`)
- `marketing_consent` / `consent_date` — dropped (owner decision 2026-06-22)
- `smarten_order_id` — dropped (wrong direction: Django is the platform, identity link belongs in Django not Supabase)
- Bookaway — same company as 12Go, bookings appear under `12GO*` prefix

**Supabase is read-only source.** Django reads from it. Any cross-system identity field lives in Django (e.g. `Customer.supabase_booking_id` matched via email), never written back to Supabase.

## Why it matters

Traveler-contact asset r2 ([[customer-os-thesis-r2-skeptic-review]]) assumed didn't exist. Supabase fills that gap — real traveler email/phone confirmed — so conversion mechanic r2 called "unsolvable" **already runs** as ops tool. Conversion thesis **reopened**.

## Gaps / risks (r2 findings that still stand)

- **Disconnected island** — read-sync to Django needed before use in platform.
- **OTA-origin data** — channel-conflict / supplier-poaching risk on outbound marketing; service comms safe.
- **Cross-system identity merge** — email-match probabilistic; `smarten_order_id` (P2) makes it deterministic.
- **Rebooking economics unmeasured** — contacts confirmed ≠ proven direct rebooking. See [[cs-p0-measurement-protocol]].

## Sync filter (architectural decision 2026-07-02)

Sync fetches only `Date >= today` (PostgREST `?Date=gte.{today}`). Past bookings excluded at fetch time — never land in Django mirror. Recovery requires full re-sync. Cutoff uses `gte` so today's departures are included. Command-centre OTA tab shows upcoming + today only; historical bookings permanently excluded from the mirror.

## Planned role (CS Centralization — [[cs-centralization-stack]])

Keep Supabase separate, read-sync to Django via REST API (anon key). Read-only; no Django schema change; Supabase stays standalone. Query `public.view_information` for unified cross-OTA data.

### Identity seed (P1a)
- `gmail12go.Information` + `gmailklook.Information` (via view) seed Customer roll-up.
- Read-only; no Django schema change.

### Revised P0
Contacts confirmed (80%+). Measure "do captured travelers rebook direct." See [[cs-p0-measurement-protocol]].

## Related

- [[smarten-customer-os-thesis]] — decision this reopens
- [[customer-os-thesis-r2-skeptic-review]] — the data blocker this overturns
- [[cs-centralization-stack]] — reuse-first stack (Supabase read-sync added)
- [[accounts]] — Django Customer-identity base this would seed
