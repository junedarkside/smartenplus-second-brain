---
name: cs-workflow-revised-2026-06-27
description: Revised CS-Centralization workflow, stakeholders, data model, state machine, and frontend surfaces. Supersedes scattered CS notes for workflow detail. Post-team-meeting 2026-06-27.
metadata:
  type: decision
  status: accepted
  date: 2026-06-27
  parent: booking-command-centre-decision
---

# CS-Centralization — Revised Workflow (2026-06-27)

> Post-team-meeting revision. Owner-confirmed decisions locked via grill session. Supersedes workflow sections in [[booking-command-centre-decision]] and [[cs-architecture-decision]] where they conflict.

## Summary

CS-Centralization manages OTA and direct bookings through a unified Ticket-based request workflow. Three trigger types (customer / admin-operator / OTA-initiated) all funnel through the same state machine. Supabase is the OTA source of truth; Django is the operational system. Booking "completeness" is derived, not stored.

---

## Stakeholder Map

| Actor | Role | Initiates | Receives |
|---|---|---|---|
| **OTA Customer (guest)** | Travelled via Klook/12Go | Change/cancel request via `/my-trip?token=` | Status updates, resolution note, trip info updates |
| **Direct Customer (auth)** | Booked via SmartEnPlus.co.th | Change/cancel request via `/bookings/[id]` | Ticket status, booking status, resolution note |
| **Admin / CS Agent** | SmartEnPlus staff | Creates tickets (all 3 triggers), resolves, pushes info updates | Ticket queue, Supabase sync result, operator response |
| **Operator** | Runs controlled trip | Trip cancellations, pickup/date/time changes → informs Admin | Admin confirmation, booking manifest |
| **OTA (Klook / 12Go)** | Booking origin channel | Confirmation + change/cancel emails → Supabase; sometimes customer-initiated requests forwarded | Admin contact re changes |
| **Supabase** | OTA booking source of truth | Parsed OTA emails (INSERT/UPDATE on booking rows) | Polled by Celery + webhook to Django |

---

## Three Trigger Categories

All three produce a `Ticket`. All three share the same state machine. Actor who creates the Ticket differs.

### Trigger 1 — Customer-Initiated

```
Customer submits request (portal or chat)
  → POST /api/cs/ota/change-request/ (OTA guest, signed token)
  → POST /api/tickets/customer-requests/ (direct, session auth)
  → Ticket created: request_status='pending', created_by=customer

Admin reviews → transitions 'pending' → 'in_review'
Admin contacts OTA (Klook/12Go) or Operator

External party responds:
  OTA path: OTA emails → Supabase updated → webhook/sync → Django updated
  Admin verifies match manually → PATCH request_status='resolved', resolution_note="..."
  OR: admin rejects → 'rejected', resolution_note="why"
  OR: no action needed → 'closed_no_action', resolution_note="..."

Customer sees resolution + note in portal
Booking returns to complete (derived: no open Ticket)
```

### Trigger 2 — Admin/Operator-Initiated

```
Operator contacts Admin (call/email) → trip change (date, pickup, cancel)
  → Admin creates Ticket in command-centre (created_by=admin)
  → Ticket.source = booking origin ('ota' or 'direct')
  → initiated_by = 'admin_on_behalf_of_operator'
  → Booking derived status → incomplete

Admin contacts OTA to update if OTA booking
  → OTA updates → Supabase synced → Admin verifies → resolves Ticket
  → resolution_note explains what changed to customer
  → Booking → complete
```

### Trigger 3 — OTA-Initiated (OTA forwards customer request to SmartEnPlus)

```
OTA emails/contacts SmartEnPlus Admin about a customer's change request
  → Admin creates Ticket (created_by=admin)
  → Ticket.initiated_by = 'admin_on_behalf_of_ota'
  → Same resolution path as Trigger 2
```

---

## Booking Lifecycle State Machine

**Completeness is DERIVED — never stored as a flag.** Avoids sync bugs.

```
complete   = CsOtaBooking.status == 'confirmed' AND no open Ticket
incomplete = any Ticket with request_status IN [pending, in_review, awaiting_ota_update]
```

### Ticket State Machine

```
[Ticket created]
      │
   pending ──[admin reviews]──► in_review
                                    │
                     ┌──────────────┼──────────────────┐
              [contacts OTA]   [no action]       [rejects]
                     │              │                   │
           awaiting_ota_update  closed_no_action    rejected
                     │              │                   │
              [Supabase matches,    └───────────────────┘
               admin verifies]              │
                     │                 booking → complete
                  resolved
                     │
              booking → complete
```

**Status values:**
| Value | Meaning | Booking state |
|---|---|---|
| `pending` | Created, awaiting admin review | incomplete |
| `in_review` | Admin reviewing, contacting external party | incomplete |
| `awaiting_ota_update` | Admin contacted OTA, waiting for Supabase confirmation | incomplete |
| `resolved` | Change confirmed, Supabase matched, admin verified | complete |
| `rejected` | Request denied by admin | complete |
| `closed_no_action` | No change needed / already handled | complete |

**One open Ticket per booking at a time.** Block new submission if any Ticket in `[pending, in_review, awaiting_ota_update]`. Once `resolved / rejected / closed_no_action` → customer can re-submit.

---

## CsOtaBooking Status (Supabase truth)

Separate from Ticket. Tracks what OTA says about the booking.

```
confirmed ──[OTA cancels]──► canceled
confirmed ──[OTA changes]──► confirmed (fields updated, last_synced_at bumped)
pending   ──[OTA confirms]──► confirmed
*         ──[unknown status]──► quarantined
```

`quarantined` = internal admin state only. Customer sees "Pending Review."

---

## Data Model Changes Required

### `Ticket` — new fields

```python
# New status choices to add:
('awaiting_ota_update', 'Awaiting OTA Update'),
('closed_no_action',   'Closed — No Action Needed'),

# New fields:
ota_booking       = FK(CsOtaBooking, null=True, blank=True, on_delete=SET_NULL)
initiated_by      = CharField(choices=[
                       'customer', 'admin_on_behalf_of_operator', 'admin_on_behalf_of_ota'
                    ])
resolution_note   = TextField(null=True, blank=True)   # shown to customer
resolved_at       = DateTimeField(null=True, blank=True)
resolved_by       = FK(User, null=True, blank=True, on_delete=SET_NULL)
```

`requested_value` JSON schema normalized per request_type:
```json
date_change:   {"new_date": "2026-07-15"}
pax_change:    {"adults": 2, "children": 1}
cancellation:  {}
other:         {"note": "free text"}
```

### `CsOtaBooking` — new fields

```python
supabase_row_id  = CharField(max_length=100, null=True, unique=True)  # Supabase PK for webhook routing
previous_status  = CharField(max_length=20, null=True)                # before last sync
status_changed_at = DateTimeField(null=True)                          # when status last changed
```

### New model: `TripNotification`

For information updates (boarding, pickup point, weather) — NOT a Ticket, no state change.

```python
class TripNotification(models.Model):
    CATEGORY_CHOICES = ['boarding', 'pickup', 'weather', 'delay', 'other']

    ota_booking   = FK(CsOtaBooking, on_delete=CASCADE, null=True, blank=True)
    booking_item  = FK(BookingItem, on_delete=CASCADE, null=True, blank=True)
    category      = CharField(choices=CATEGORY_CHOICES)
    body          = TextField()
    sent_at       = DateTimeField(auto_now_add=True)
    sent_by       = FK(User, null=True, on_delete=SET_NULL)
    email_sent    = BooleanField(default=False)
```

Admin creates → fires SES email to customer → surfaces in portal as info card. No Ticket created. Booking stays `complete`.

### New model: `OtaBookingEvent` (append-only audit log)

```python
class OtaBookingEvent(models.Model):
    ota_booking    = FK(CsOtaBooking, on_delete=CASCADE, related_name='events')
    trigger        = CharField(choices=['sync', 'webhook', 'manual'])
    field_diffs    = JSONField()       # {"status": ["confirmed","canceled"]}
    raw_payload    = JSONField(null=True)
    created_at     = DateTimeField(auto_now_add=True, db_index=True)
    matched_ticket = FK(Ticket, null=True, blank=True, on_delete=SET_NULL)
```

Replaces `set_logs` (freeform CharField) with structured history. Anchor for admin to see what changed on last sync.

---

## Sync Architecture

**Decision: Supabase webhook PRIMARY + Celery 15min periodic FALLBACK.**

| Method | Role | Latency |
|---|---|---|
| Supabase Database Webhook → `/api/cs/ota-webhook/` | Primary | ~1s |
| `sync_ota_bookings` Celery beat (every 15min) | Gap-fill if webhook missed | ≤15min |

Webhook endpoint:
- Verify `X-Supabase-Signature` HMAC-SHA256
- Idempotent upsert by `(source, booking_id)`
- Create `OtaBookingEvent(trigger='webhook', field_diffs=...)`
- No automatic match detection — admin resolves manually (v1)

Periodic task unchanged in logic; just emits `OtaBookingEvent(trigger='sync')` per changed row.

---

## Information Update Workflow (Separate from Requests)

```
Admin sees trip change (e.g. new boarding point from operator)
  → Admin creates TripNotification in admin dashboard
  → SES email fired to customer
  → TripNotification surfaces in /my-trip and /bookings/[id] as InfoUpdateNotice card
  → No Ticket created, booking stays complete, no Supabase dependency
```

---

## Frontend Surfaces

### Existing — confirmed working
- `/bookings/[id]` — auth customer, `ChangeRequestsSection` (60s poll), `RequestChangeModal`
- `/my-trip?token=` — OTA guest, `OtaRequestForm` + `OtaRequestCard`

### Gaps to fix

| Gap | Fix | Priority |
|---|---|---|
| OTA guest: no polling after ticket submit | Add `pollingInterval: 60000` to `useGetOtaTripQuery` | High |
| One ticket ever (OTA) | Change to "one OPEN ticket" — allow re-submit after resolved/rejected | High |
| No resolution_note shown | Render `ticket.resolution_note` in `OtaRequestCard` + `RequestCard` | High |
| No admin-initiated ticket display | `initiated_by` field → different card header "Update from SmartEnPlus" | High |
| No info update surface | `InfoUpdateNotice` card above `Information.js` | Medium |
| No status progress stepper | `RequestProgressStepper` (Submitted → Under Review → Resolved) | Medium |
| Auth booking: no poll when ticket active | Add `pollingInterval: 120000` to `useGetBookingDetailQuery` when ticket open | Medium |

### New components

**`TicketStatusBanner`** — replaces `RequestCard` / `OtaRequestCard`
```
props: { ticket: { request_type, request_status, initiated_by,
                   resolution_note, date_created, resolved_at } }
Shows: different header if initiated_by='admin_*' ("Update from SmartEnPlus")
       RequestProgressStepper inline
       resolution_note on resolved/rejected/closed_no_action
```

**`InfoUpdateNotice`** — surfaces `TripNotification` records
```
props: { notifications: TripNotification[] }
Shows: dismissible banner per notification, category icon, body, sent_at
```

**`RequestProgressStepper`** — inline in TicketStatusBanner
```
Submitted → Under Review → [Resolved | Rejected | No Change Made]
    ●             ●                    ○
  date          date               pending
```

---

## Customer Status Vocabulary (Customer-Facing Labels)

| `request_status` | Customer sees | Notes |
|---|---|---|
| `pending` | "Waiting for Review" | |
| `in_review` | "Being Reviewed" | |
| `awaiting_ota_update` | "Update in Progress" | Hide internal OTA detail |
| `resolved` | "Approved ✓" + resolution_note | |
| `rejected` | "Not Approved" + resolution_note | Must show note |
| `closed_no_action` | "No Change Needed" + resolution_note | Distinct from Approved |

---

## Open Questions (Not Yet Decided)

| # | Question | Blocks |
|---|---|---|
| OQ-1 | Supabase plan tier — does it support Database Webhooks (pg_net)? Free tier may require workaround. | Sync architecture |
| OQ-2 | SMS provider for trip-day reminder — Twilio, SNS, or none? | TripNotification delivery |
| OQ-3 | `awaiting_ota_update` timeout SLA — how long before admin gets alerted? | Celery beat schedule |
| OQ-4 | Operator-trip cancellation (direct booking) — does Ticket resolution atomically set `BookingItem.status='Canceled'`? | Ticket→Booking link |
| OQ-5 | `quarantined` OTA booking + customer submits request — is that allowed or blocked? | Ticket creation guard |
| OQ-6 | Magic link expiry — can admin regenerate from dashboard? Customer dead-end without this. | OTA guest UX |

---

## Related

[[booking-command-centre-decision]] (parent) · [[cs-architecture-decision]] · [[cs-api-contract]] · [[cs-consent-gdpr-model]] · [[cs-centralization-stack]] · [[supabase-ota-booking-store]] · [[cs-guest-storm-investigation]]
