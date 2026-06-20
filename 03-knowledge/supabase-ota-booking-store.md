---
name: supabase-ota-booking-store
description: Standalone Supabase datastore of OTA (12Go) bookings + traveler profiles, populated by parsing OTA confirmation emails — source-verified 2026-06-20 via live REST API
metadata:
  type: knowledge
  status: active
  date: 2026-06-20
  source: source-verified (live REST API, 2026-06-20)
---

# Supabase OTA Booking Store

> ✅ **Source-verified 2026-06-20** via live Supabase REST API (`gmail12go.Information`). Schema, record count, date range, and field samples confirmed directly.

## Summary

Standalone **Supabase** system stores OTA bookings + traveler profiles, populated by **parsing OTA booking-confirmation emails**. Current data is **12Go** bookings only (all `Booking_ID` values have `12GO` prefix). Purpose is **operational**: one place for all bookings, track status, check who travels on a given date. **Disconnected** from Django backend.

## Verified Schema

**Project:** `npehhtcobshckhefrqhw.supabase.co`
**Schema:** `gmail12go`
**Table:** `Information`
**Endpoint:** `GET /rest/v1/Information?select=*` + `Accept-Profile: gmail12go` header
**Auth:** anon JWT key (stored separately — do not commit)

| Column | Type | Notes |
|---|---|---|
| `Date` | date | Travel date |
| `Time` | time | Departure time |
| `Arrival` | time | Arrival time |
| `Name` | text | Lead traveler name |
| `Gmail` | text | Lead traveler email |
| `Phone` | text | Lead traveler phone |
| `Destination` | text | Route (e.g. `Kuah Jetty Langkawi-Koh Lipe Immigration point`) |
| `Operator` | text | `Smart En Plus` (some dirty: `ensure plus`, trailing `\r\n`) |
| `Class` | text | Service type: Ferry, Van 9pax, Speedboat, etc. |
| `Status` | text | `✅Confirmed` / `❎Canceled` |
| `Set-Logs` | text | `SENT` (54/58) or empty (4/58) — notification sent flag |
| `Booking_ID` | text | OTA ref — all `12GO` prefix (e.g. `12GO29980150`) |
| `Passengers` | text | Formatted pax count (Adult/Child/Infant emoji string) |
| `PassengerNames` | text | Bullet list of all passenger names |
| `Notify` | text | `NOTIFY` (32/58) or empty — secondary notify flag |
| `Created At` | date | Record ingestion date |

## Live Stats (as of 2026-06-20)

- **Total records:** 58
- **Travel date range:** 2026-02-19 → 2027-01-02 (one `5000-08-02` outlier — data entry error)
- **Ingestion range:** 2025-10-30 → 2026-06-15
- **Status:** 2 values — `✅Confirmed` / `❎Canceled`
- **Set-Logs:** 54 SENT, 4 empty
- **Notify:** 32 NOTIFY, 26 empty
- **OTA source:** 12Go only (all `Booking_ID` = `12GO*`)
- **Top routes:** Langkawi↔Koh Lipe (dominant), Koh Lipe↔Telaga Harbour, scattered inland

## Coverage Gap

Only 12Go confirmed (all 58 records have `12GO*` `Booking_ID` prefix). Klook and Bookaway mentioned by owner as also present — **not verified** — may live in separate schemas (anon key blocked from schema catalog; `service_role` key needed to discover). Possible: separate table per OTA, or not yet ingested.

## Data Quality Issues (fix before sync)

- `Operator` field has dirty values: `'ensure plus'` (should be `'Smart En Plus'`), `'Smart En Plus\r\n'` (trailing CRLF). Normalise before read-sync.
- One `Date` = `'5000-08-02'` — data entry error, outlier.

## Gaps for CS Centralization (owner to add)

| Field | Purpose | Priority |
|---|---|---|
| `Source` | OTA identifier (`12go` / `klook` / `bookaway`) — currently inferred from `Booking_ID` prefix only | P0 |
| `marketing_consent` boolean | Unlock for marketing comms; captured at P1b service-comms touchpoint | P1 |
| `consent_date` date | Legal record of when opt-in captured | P1 |
| `smarten_order_id` | Django `Order` linkage for cross-system identity merge (nullable) | P2 |

## Why it matters

Traveler-contact asset r2 ([[r2-skeptic-review]]) assumed didn't exist. r2 killed conversion thesis ("dead at data layer") because Django's only PII is `Order.email` = booker (often agency), and `BookingPassengerDetail` has no contact field. Supabase fills that gap — real traveler email/phone for 12Go bookings confirmed — so conversion mechanic r2 called "unsolvable" **already runs** as ops tool. Conversion thesis **reopened** (see thesis Summary note).

## Gaps / risks (r2 findings that still stand)

- **Disconnected island** — data is not in the customer platform; a read-sync is needed to use it for identity/comms.
- **No marketing consent** — raw contact only. Service messages are safe; marketing needs an explicit opt-in.
- **OTA-origin data** — parsed from OTA confirmation emails = OTA-sourced. Marketing to it is still the **channel-conflict / supplier-poaching** risk r2 flagged; service-only-by-default still applies until opt-in is captured.
- **Cross-system identity merge** — joining Supabase keys to Django identity is the probabilistic-merge problem r2 named.
- **Rebooking economics unmeasured** — having contacts ≠ proven direct rebooking. This is the real open question now.

## Planned role (CS Centralization — [[cs-centralization-stack]])

Per owner decision: **keep Supabase separate, sync to platform** (reuse-first, no migration, no prod impact).

### Dual-schema role (validated 2026-06-21)

Same Supabase project (`npehhtcobshckhefrqhw`) serves two distinct purposes:

| Schema | Table(s) | Purpose | Access |
|---|---|---|---|
| `gmail12go` | `Information` (58 records, 16 cols) | OTA booking store — traveler identity seed | Django reads via REST API (anon key) |
| `cs` *(planned P1b)* | `cs.conversations`, `cs.messages` | CS message relay — Django→Supabase write, CS Dashboard Realtime push | Django writes (service_role key); CS Dashboard subscribes (anon key, Realtime only) |

### CS Dashboard Realtime (Option B — P1b)

CS Dashboard (admin-dashboard) subscribes to `cs.messages` Supabase Realtime channel using anon key (browser WebSocket). When Django→Celery writes a new message to `cs.messages`, Supabase Realtime pushes the INSERT event to the CS Dashboard browser (<1s). No NextAuth↔Supabase JWT bridge needed — anon key is for Realtime event push only, not row reads.

```js
// admin-dashboard: Realtime subscription pattern
supabase.channel('cs-messages')
  .on('postgres_changes', { event: 'INSERT', schema: 'cs', table: 'messages' }, handleNewMessage)
  .subscribe()
```

Staff reads message history via Django API (NextAuth-authenticated), not directly from Supabase.

### Identity seed (P1a)
- Supabase stable key + profiles from `gmail12go.Information` seed the Customer roll-up (read-sync via REST API).
- Read-only; no Django schema change; Supabase stays standalone.

### Service-comms + consent (P1b)
- Booking confirmations / trip reminders sent from synced Supabase data.
- Natural place to **add a consent opt-in** (owner confirmed yes) → `marketing_consent` field → unlocks later marketing.

### Revised P0
Stop measuring "can we capture contacts" (answered: yes, 80%+ in Supabase). Measure "do captured travelers who get a Smarten touchpoint **rebook direct**."

## Related

- [[smarten-customer-os-thesis]] — decision this reopens
- [[r2-skeptic-review]] — the data blocker this overturns
- [[cs-centralization-stack]] — reuse-first stack (Supabase read-sync added)
- [[accounts]] — Django Customer-identity base this would seed
