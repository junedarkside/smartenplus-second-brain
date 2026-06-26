---
name: cs-workflow-revised-2026-06-27
description: Revised CS-Centralization workflow, stakeholders, data model, state machine, and frontend surfaces. Supersedes scattered CS notes for workflow detail. Post-team-meeting 2026-06-27.
metadata:
  type: decision
  status: fix-then-ship
  date: 2026-06-27
  parent: booking-command-centre-decision
---

# CS-Centralization — Revised Workflow (2026-06-27)

> Post-team-meeting revision. Owner-confirmed decisions locked via grill session. Supersedes workflow sections in [[booking-command-centre-decision]] and [[cs-architecture-decision]] where they conflict.

> **⚠️ Scrutinize pass 2026-06-27 (3-agent: arch + workflow + codebase-verify).** Verdict: **fix-then-ship.** 5 blockers + 7 majors found and corrected inline below (each tagged `[FIX B-n]` / `[FIX M-n]`). Status dropped `accepted → fix-then-ship` until blockers land in implementation. Full findings recorded at bottom (§Scrutiny Findings). Codebase fact-check: 1 doc claim REFUTED (OTA re-submit logic — see §Frontend Surfaces).

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
  → admin_initiated = True   [FIX M-1: replaced 3-value initiated_by enum]
  → Booking derived status → incomplete

  ┌─ OTA booking branch ──────────────────────────────────────────┐
  │ Admin contacts OTA → OTA updates → Supabase synced            │
  │ → Admin verifies → resolves Ticket                            │
  └───────────────────────────────────────────────────────────────┘
  ┌─ DIRECT / controlled-trip branch  [FIX B-4] ──────────────────┐
  │ NO Supabase, NO CsOtaBooking. Admin resolves directly.        │
  │ → Ticket resolution side-effect sets BookingItem.booking_status│
  │   directly (e.g. cancellation → 'Canceled') — no awaiting_ota  │
  │ → completeness derived from BookingItem.status, not CsOtaBooking│
  └───────────────────────────────────────────────────────────────┘

  → resolution_note explains what changed to customer
  → Booking → complete (or cancelled_complete if cancellation — see state machine)
```

> **[FIX M-6] Ticket collision (operator-cancel vs open customer request):** "one open ticket" rule would block Admin from creating a cancellation ticket while a customer change-request is open. Resolution: Admin can **supersede** the open customer ticket — it auto-transitions to `closed_no_action` with `resolution_note='Superseded by trip cancellation.'`, then the cancellation ticket is created. Customer sees the explanation, not a silent close.

### Trigger 3 — OTA-Initiated (OTA forwards customer request to SmartEnPlus)

```
OTA emails/contacts SmartEnPlus Admin about a customer's change request
  → Admin creates Ticket (created_by=admin)
  → admin_initiated = True   [FIX M-1]
  → Same resolution path as Trigger 2
```

> **[FIX M-7] Customer not surprised:** Trigger 3 (and any `admin_initiated` Trigger 2) opens a ticket the customer never requested. Polling alone fails for customers not viewing the portal. **An email fires on `admin_initiated` ticket create** notifying the customer a change is being handled on their booking. Resolution_note delivered same way. Without this, a Klook/12Go customer learns of a trip change only by chance.

> **Note on Trigger 2/3 distinction:** the two differ only in `created_by` reason; both produce `admin_initiated=True` + identical state path. Kept as separate narratives for ops clarity, but they are **one mechanism** in code.

---

## Booking Lifecycle State Machine

**Completeness is DERIVED — never stored as a flag.** Avoids sync bugs.
Cost note: derived completeness requires a Ticket join per booking load — acceptable at current volume (hundreds of OTA rows). Revisit with a cached flag only if booking-list queries show join cost at scale.

```
# [FIX B-3 + B-4] three terminal conditions, OTA and direct both covered:

complete           = booking active AND no open Ticket
                     where "booking active" = CsOtaBooking.status == 'confirmed'  (OTA)
                                            OR BookingItem.status == 'Confirmed'  (direct)
cancelled_complete = booking cancelled AND latest Ticket resolved
                     where "booking cancelled" = CsOtaBooking.status == 'canceled' (OTA)
                                               OR BookingItem.status == 'Canceled' (direct)
incomplete         = any Ticket with request_status IN [pending, in_review, awaiting_ota_update]
```

> **[FIX B-3]** A cancellation that resolves is NOT "complete/Approved ✓" — the trip is dead. It reaches `cancelled_complete`, shown to customer as **"Cancellation Confirmed"**, never "Approved ✓". Previously the formula made `complete` permanently false for cancelled bookings (status≠confirmed) while the diagram claimed resolved→complete — contradiction now closed.

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

Verified against `tickets/models.py`: current `request_status` is `max_length=10`, choices = pending/in_review/resolved/rejected. Ticket already has `created_by` (User FK), `source`, `requested_value`, and a **GenericFK** (`content_type`+`object_id`+`content_object`) whose Phase-2 comment maps it to CsOtaBooking.

```python
# [FIX B-1] WIDEN existing field — new values are 16 & 20 chars, max_length=10 truncates/errors:
request_status = CharField(max_length=25, choices=REQUEST_STATUS_CHOICES, ...)

# New status choices to add:
('awaiting_ota_update', 'Awaiting OTA Update'),   # 19 chars
('closed_no_action',   'Closed — No Action Needed'),  # 16 chars

# [FIX B-2] DO NOT add a concrete ota_booking FK — it duplicates the existing GenericFK
#   and breaks the "one open ticket" guard (guard queries GenericFK; new FK stays NULL on
#   tickets created via the existing API path). Use the GenericFK + a typed accessor:
@property
def ota_booking(self):
    return self.content_object if self.source == 'ota' else None

# [FIX M-1] replace 3-value initiated_by enum (overlapped created_by + source) with a boolean.
#   customer-initiated is derivable (created_by is non-staff). The only frontend need is
#   "show 'Update from SmartEnPlus' header" — a binary. Add operator/OTA split later if routing needs it.
admin_initiated   = BooleanField(default=False)

resolution_note   = TextField(null=True, blank=True)   # shown to customer
resolved_at       = DateTimeField(null=True, blank=True)
resolved_by       = FK(User, null=True, blank=True, on_delete=SET_NULL)
```

> **Resolution side-effects [FIX B-4]:** when `request_type='cancellation'` is resolved, the resolver sets the linked booking status directly — `CsOtaBooking.status='canceled'` (OTA, awaiting Supabase confirm) OR `BookingItem.booking_status='Canceled'` (direct, immediate, no Supabase). Without this the derived completeness is a lie (no open ticket + confirmed status = "complete" on a cancelled trip).

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
# [FIX N-2] note: globally unique across Klook AND 12Go Supabase tables — confirm Supabase
#   does not reuse row ids across source tables, else this rejects valid inserts.

# [FIX M-3] DROPPED previous_status + status_changed_at — they duplicate OtaBookingEvent.field_diffs
#   (the append-only source of truth). Storing the prior status twice creates a sync-bug path on
#   double webhook delivery. Expose via property instead:
@property
def previous_status(self):
    last = self.events.filter(field_diffs__has_key='status').order_by('-created_at').first()
    return last.field_diffs['status'][0] if last else None
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

    # [FIX M-5] enforce exactly one booking link — both-null (orphan) and both-set (ambiguous)
    #   are silently valid without this; portal queries then return nothing.
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(ota_booking__isnull=False, booking_item__isnull=True) |
                    models.Q(ota_booking__isnull=True,  booking_item__isnull=False)
                ),
                name='tripnotification_exactly_one_booking',
            )
        ]
```

Admin creates → fires SES email to customer → surfaces in portal as info card. No Ticket created. Booking stays `complete`.

> **[FIX N-7] Info-update vs Ticket boundary:** decision rule — if the change requires customer action or affects trip feasibility (date/time/cancellation) → **Ticket**. If advisory-only (meeting point moved 50m, weather note) → **TripNotification**. A pickup-point change that breaks the customer's plan is a Ticket, not a notification.

### New model: `OtaBookingEvent` (append-only audit log)

```python
class OtaBookingEvent(models.Model):
    ota_booking    = FK(CsOtaBooking, on_delete=CASCADE, related_name='events')
    trigger        = CharField(choices=['sync', 'webhook', 'manual'])
    field_diffs    = JSONField()       # {"status": ["confirmed","canceled"]}
    raw_payload    = JSONField(null=True)
    created_at     = DateTimeField(auto_now_add=True, db_index=True)
    # [FIX M-2] DROPPED matched_ticket — v1 uses MANUAL admin match (see §Sync). Nothing
    #   populates it; a dead nullable FK misleads future devs into thinking auto-match exists.
    #   Add in v2 migration when automated match detection is built.
```

Replaces `set_logs` (freeform CharField, verified `cs/models.py:138`) with structured history. Anchor for admin to see what changed on last sync.

---

## Sync Architecture

**Decision: Supabase webhook PRIMARY + Celery 15min periodic FALLBACK — CONTINGENT on Supabase plan (see B-5).**

> **[FIX B-5] Blocker:** webhook-primary depends on Supabase Database Webhooks (`pg_net`), which the **free tier does not support**. Until the Supabase plan is confirmed (OQ-1), this framing is unvalidated. If free tier: **Celery becomes primary** (drop interval to ~2-5min) and webhook is a future upgrade. Do not build the webhook endpoint before confirming the plan supports it.

| Method | Role | Latency |
|---|---|---|
| Supabase Database Webhook → `/api/cs/ota-webhook/` (does NOT exist yet — verified `cs/urls.py`) | Primary *if plan supports pg_net* | ~1s |
| `sync_ota_bookings` Celery beat (verified exists `cs/tasks.py:68`) | Gap-fill, or PRIMARY if free tier | ≤15min |

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
| One ticket ever (OTA) — **BUG, verified** | `my-trip/index.js:54-58` gates on `existingTickets.length === 0` (blocks re-submit even after a ticket resolves). Fix to filter by OPEN status: `existingTickets.filter(t => ['pending','in_review','awaiting_ota_update'].includes(t.request_status)).length === 0` | High |
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
| `resolved` (change) | "Approved ✓" + resolution_note | |
| `resolved` (cancellation → `cancelled_complete`) | "Cancellation Confirmed" + resolution_note | **[FIX B-3]** never "Approved ✓" on a dead trip |
| `rejected` | "Not Approved" + resolution_note | Must show note |
| `closed_no_action` | "No Change Needed" + resolution_note | Distinct from Approved |

---

## Open Questions (Re-tiered by scrutiny pass)

| # | Question | Severity | Blocks |
|---|---|---|---|
| OQ-1 | Supabase plan tier — supports Database Webhooks (pg_net)? Free tier does NOT. | **BLOCKER** (was "open") | Sync architecture — see [FIX B-5] |
| OQ-4 | Direct-booking cancellation — Ticket resolution sets `BookingItem.status='Canceled'`? | **RESOLVED** → [FIX B-4] (direct branch added) | — |
| OQ-3 | `awaiting_ota_update` timeout SLA — how long before admin alerted? No bound = customer stuck indefinitely. | **MAJOR** (was minor) | Celery schedule + customer ETA |
| OQ-5 | `quarantined` OTA booking + customer submits request — allowed or blocked? Valid likely state, no guard. | **MAJOR** (was minor) | Ticket creation guard |
| OQ-6 | Magic link expiry — admin regenerate from dashboard? Expired link = customer can't see resolution of an admin-opened ticket. | **MAJOR** (was minor) | OTA guest UX |
| OQ-2 | SMS provider for trip-day reminder — Twilio, SNS, none? | Minor (correct) | TripNotification delivery (additive) |
| OQ-7 | Request feasibility validation — does API reject impossible requests (past date, sold-out) at create, or let admin reject manually? | MAJOR (new, from workflow trace) | Ticket creation path |

---

## Scrutiny Findings (3-agent pass, 2026-06-27)

Verdict: **fix-then-ship.** All blockers + majors below corrected inline above (tagged `[FIX …]`). Recorded for audit.

**Blockers**
- **B-1** `request_status max_length=10` truncates new 16/20-char statuses → DB error. Widen to 25.
- **B-2** proposed `ota_booking` FK duplicates existing GenericFK → breaks "one open ticket" guard. Use GenericFK + property.
- **B-3** cancellation: `status=canceled` makes `complete` permanently false, but diagram showed resolved→complete; "Approved ✓" on dead trip. Added `cancelled_complete` + "Cancellation Confirmed".
- **B-4** direct/controlled-trip cancellation had no state path (model is OTA-centric). Added direct branch + resolution side-effect on BookingItem.
- **B-5** webhook-primary unvalidated — Supabase free tier lacks pg_net. Marked contingent; Celery-primary fallback.

**Majors**
- **M-1** `initiated_by` 3-enum overlapped `created_by`+`source` → replaced with `admin_initiated` boolean.
- **M-2** `OtaBookingEvent.matched_ticket` dead in v1 (manual match) → removed, defer to v2.
- **M-3** `previous_status`/`status_changed_at` duplicate `field_diffs` → dropped, property instead.
- **M-5** `TripNotification` "exactly one FK" unenforced → CheckConstraint added.
- **M-6** ticket collision (operator-cancel vs open customer ticket) → admin supersede → `closed_no_action`.
- **M-7** customer not notified of admin-opened ticket (silent change) → email on `admin_initiated` create.
- **M-8** OQ-3/5/6 mislabeled minor → re-tiered MAJOR.

**Codebase fact-check (Explore agent, all cited)**
- Claim REFUTED: doc implied OTA re-submit blocked by status; actual `my-trip/index.js:54-58` blocks on `length===0` (any ticket ever) — a BUG to fix, noted in §Frontend Surfaces.
- Confirmed: `ChangeRequestsSection` 60s poll (`:83`); `useGetOtaTripQuery` no poll (`otaApi.js:10-13`); 3 proposed components don't exist; endpoints `/api/cs/ota/trip/` + `/change-request/` exist, `/ota-webhook/` does not; `sync_ota_bookings` exists (`tasks.py:68`); Ticket GenericFK exists (`tickets/models.py:48-50`); none of the proposed Ticket fields exist yet; `set_logs` is CharField (`cs/models.py:138`).

**Nits (not yet applied — owner call)**
- **N-1** `Ticket.ticket_status` (Active/Completed/Pending) parallel to `request_status` — clarify if abandoned or mapped.
- **N-3** `awaiting_ota_update` SLA as per-ticket field vs Celery constant (ties to OQ-3).
- Trigger 2/3 could collapse to one documented mechanism (~30% doc surface) — kept separate for ops clarity (noted inline).

---

## Related

[[booking-command-centre-decision]] (parent) · [[cs-architecture-decision]] · [[cs-api-contract]] · [[cs-consent-gdpr-model]] · [[cs-centralization-stack]] · [[supabase-ota-booking-store]] · [[cs-guest-storm-investigation]]
