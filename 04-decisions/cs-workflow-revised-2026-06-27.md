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

> **📋 Audit 2026-06-29:** Cross-layer deep audit completed. BE-B2/B4/B5 closed (#186). NEW defects found: 10 Tier-1 criticals (signals dead, beat absent, resend dead token, one-open-ticket missing, magic-link TTL, resolution side-effect, trip_id missing, closed_no_action unreachable, OTP JWT scope, requested_value unbounded). See [[cs-centralization-audit-2026-06-29]].

> **[UPDATE 2026-06-27]** NEW-2 (`partner_case_id` field) CLOSED. Not needed — `(source, booking_id)` on `CsOtaBooking` already provides OTA case tracking. `Ticket.content_object` → `CsOtaBooking` links tickets to OTA bookings.

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

**Decision: Django fetches FROM Supabase via Celery 15min periodic + on-demand admin. No webhook needed.**

> **[OQ-1 CLOSED 2026-06-27]** User confirmed n8n NOT the path. Django polls Supabase directly. `sync_ota_bookings` Celery task exists (`cs/tasks.py:68`) — upserts by `(source, booking_id)`. On-demand admin trigger to be added: `POST /api/cs/ota/sync/`. Supabase pg_net (Database Webhooks) never required.

| Method | Role | Latency |
|---|---|---|
| `sync_ota_bookings` Celery beat (verified exists `cs/tasks.py:68`) | **PRIMARY** — automatic background sync | ≤15min |
| `POST /api/cs/ota/sync/` (to be built) | **On-demand** — admin triggers immediately | ~5s (queues Celery task) |

**Celery task logic:**
- Idempotent upsert by `(source, booking_id)`
- Create `OtaBookingEvent(trigger='sync', field_diffs=...)` per changed row
- Field mapping: `Date`→booking_date, `Status`→normalized, `PassengerNames`→passenger_names, etc. (already built)
- No automatic match detection — admin resolves manually (v1)

**On-demand endpoint (`OtaSyncView` — to be built):**
- Auth: `IsAdminOrIsStaff` permission class
- POST → queues `sync_ota_bookings.delay(source=source)` async
- Returns `{"status": "queued", "task_id": "..."}`
- No inline sync — always async via Celery

**15min sync acceptable for:** future-day changes, routine data sync, new bookings appearing.
**NOT acceptable for:** same-day cancellations, emergency changes — requires emergency fast-track path (NEW-4 + NEW-10).

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

## Stakeholder Meeting — PM Summary (2026-06-27)

**Format:** 5-voice simulation (Customer · OTA Passenger · Admin/CS · OTA Staff · Operator Staff). Each read the full doc cold and gave unfiltered feedback. PM synthesis below. All voices available in full above this section.

---

### Cross-Cutting Themes (all 5 voices raised)

| Theme | Who raised it | Current doc status |
|---|---|---|
| **No SLA on `awaiting_ota_update`** | Customer, OTA Passenger, Admin, OTA Staff | OQ-3 MAJOR — UNRESOLVED |
| **Magic link expiry = customer dead-end** | Customer, OTA Passenger, Admin, OTA Staff | OQ-6 MAJOR — UNRESOLVED |
| **Supabase sync lag visible to everyone** | Customer, OTA Staff, Admin | OQ-1 BLOCKER — UNRESOLVED |
| **No notification channel defined** | OTA Passenger, Operator, OTA Staff | M-7 added but email copy + channel unspecified |
| **Emergency/urgent cancellation path** | Operator, Admin, Customer | NOT IN DOC — new gap |

---

### Voice Summaries

#### 🧑 Customer (Nanthawan — direct, Thai professional)
**Core complaint:** "Waiting for Review" and "Being Reviewed" feel identical. No ETA. No escalation path. `awaiting_ota_update` = indefinite limbo with no customer recourse.

**New gaps surfaced:**
- `closed_no_action` label "No Change Needed" implies request was ignored — resolution_note must be mandatory here, not optional.
- No confirmation that request was received (OTA portal has no polling bug confirmed — still not fixed in UX experience).
- No escalation path if status doesn't move in N days.

**Highest priority ask:** Mandatory expected-response-time shown at ticket submission. Ties directly to OQ-3.

---

#### ✈️ OTA Passenger (Yuki — Klook booker, Japan)
**Core complaint:** The magic link email looks like phishing. No SmartEnPlus brand trust established. If link expires, complete dead-end.

**New gaps surfaced:**
- Email must state "You booked [Trip] through Klook — this is the operator portal" in line 1. Without this, open rate is near zero for non-Thai travellers.
- No fallback contact (WhatsApp/LINE number) in magic link email footer — customer has nowhere to go on expiry.
- "Cancellation Confirmed" in portal before Klook refunds creates credibility conflict — customer believes Klook, not SmartEnPlus portal.
- **i18n completely absent from doc** — English-only portal excludes large OTA customer segments (Thai, Japanese, Korean, Russian).

**Highest priority ask:** Magic link email redesign — trust context + fallback contact in first/last lines. Predates any feature work.

---

#### 🎧 Admin/CS Agent (Nong — CS Lead, 40-60 tickets/day)
**Core complaint:** 8 manual steps per OTA ticket. No push when Supabase updates. Admin can resolve ticket before Supabase actually reflects the change — creates data lie in customer portal with no recovery path.

**New gaps surfaced:**
- **`awaiting_ota_update` must block resolve until at least one `OtaBookingEvent` is created after ticket entered that status.** Without this guard, admin can click Resolve on Klook's verbal confirmation before the sync lands — customer sees "Approved" on stale data.
- Supersede (M-6) needs a confirmation modal UI spec — one wrong click closes a live customer request permanently.
- No "Supabase last synced + field diff" banner on ticket detail = admin verifying blind.
- Automated SES emails: doc only specifies M-7 trigger. All other transitions (pending→in_review→awaiting→resolved) are silent to customer unless admin emails manually. This must be specified.
- Bulk close needed for multi-ticket group cancellation events.
- Saved queue filters needed: "Awaiting OTA > 24h", "Pending not yet reviewed", "Admin-initiated unseen by customer".

**Highest priority ask:** `OtaBookingEvent` banner on ticket detail + resolve-block guard. Without this the manual verification step is theatre.

---

#### 🏢 OTA Staff (Klook, Operator Relations Manager)
**Core complaint:** No structured forwarding channel for Trigger 3 (OTA→SmartEnPlus). No Klook case ID field on Ticket = no deduplication when customer contacts both. Sync lag means "Approved" can appear before Klook actually processed the change.

**New gaps surfaced:**
- **`partner_case_id` field on Ticket** (free-text, OTA case ref) — deduplication for Trigger 3, audit trail for disputes. 5-minute model change, prevents most common Trigger 3 failure.
- Dedicated OTA forwarding channel needed with acknowledgment receipt + SLA (proposed: 2h business hours).
- ~~Data processing agreement required~~ — **CLOSED (2026-06-27 PM review).** Klook sends booking data TO SmartEnPlus as the hired operator. Storage in Django = same data, same service purpose, different DB. Contract performance basis (PDPA §24(3)) applies. No separate DPA required. Housekeeping only: check operator agreement for marketing-use restrictions, add PII retention/purge, add one-line privacy notice in portal.
- **Channel conflict check required** — `/my-trip` must NOT show account creation prompt, newsletter opt-in, or "book direct" CTA. Written confirmation needed.
- Resolution authority ambiguity — "Approved" in SmartEnPlus before OTA processes = premature confirmation. `awaiting_ota_update` is the right guard; the risk is admin bypassing it. Ties to Admin's resolve-block gap above.

**Highest priority ask:** `partner_case_id` field + data processing agreement signed before launch.

---

#### ⛵ Operator Staff (Andaman Sea Transport — join-in ferry/speed boat)
**Core complaint:** Emergency cancellation (4:30am, weather, 90min to departure) is completely unaddressed. The full ticket state machine cannot execute in 90 minutes across 4 human handoffs. Mixed OTA+direct bookings on same boat = doc treats them as separate tracks but they are one physical departure.

**New gaps surfaced:**
- **No duty contact/emergency channel specified** — biggest real-world failure mode. Admin may be unreachable at 4:30am. Who is on call?
- **Fast-track emergency cancellation path** needed — bypasses full state machine, fires SES to all affected pax immediately without waiting for Supabase sync.
- **Manifest push to operator** when any seat-count-affecting Ticket resolves — operator currently receives nothing. Running departures on stale manifests is a safety issue.
- Supersede (M-6) invisible to operator — if admin hesitates on supersede because they don't know the rule, emergency resolution stalls.
- Mixed-booking cancellation (Klook + direct pax on same boat) requires simultaneous coordination with SmartEnPlus AND Klook ops — doc ignores this split-responsibility case.

**Highest priority ask:** Single-page emergency ops card (duty phone + fast-track cancellation steps) before any code ships to production.

---

### PM-Identified New Action Items

These gaps were NOT in the doc before this meeting and require resolution:

| # | Gap | Raised by | Severity | Owner |
|---|---|---|---|---|
| **NEW-1** | `awaiting_ota_update` must block Resolve until `OtaBookingEvent` exists after ticket entered status | Admin | **BLOCKER** (data integrity) | BE |
| **NEW-2** | ~~`partner_case_id` field on Ticket (OTA case ref)~~ → **CLOSED** (not needed — `(source, booking_id)` on `CsOtaBooking` already provides linking) | OTA Staff | MAJOR → CLOSED | — |
| **NEW-3** | Automated SES on ALL ticket status transitions (not just M-7 trigger) — spec which ones | Admin, Customer | MAJOR | BE + product |
| **NEW-4** | Emergency cancellation fast-track path — compresses state machine for same-day/weather cancel | Operator | MAJOR | Product + BE |
| **NEW-5** | Duty/on-call contact specification — who operator reaches at 4:30am | Operator | MAJOR | Ops/product |
| **NEW-6** | Magic link email redesign — trust context (booking source + trip name) + fallback contact in footer | OTA Passenger | MAJOR | FE + comms |
| **NEW-7** | i18n plan — English-only portal excludes major OTA customer segments | OTA Passenger | MAJOR | Product decision |
| **NEW-8** | ~~Data processing agreement blocker~~ → **CLOSED** — Klook sends data TO SmartEnPlus as operator. Contract performance basis (PDPA §24(3)). Housekeeping only: check contract clause, add retention/purge, add privacy notice in portal. | OTA Staff persona | ~~BLOCKER~~ → CLOSED | Legal/owner (housekeeping) |
| **NEW-9** | Channel conflict — no upsell/account-creation in `/my-trip` | OTA Staff | MINOR (was MAJOR) | Owner policy decision |
| **NEW-10** | Manifest push to operator on resolved seat-count ticket | Operator | MAJOR | BE + ops |
| **NEW-11** | Supersede (M-6) confirmation modal spec — prevent misclick closing live customer request | Admin | MAJOR | FE + UX |
| **NEW-12** | Bulk close for group cancellation events (multi-ticket supersede) | Admin | MAJOR | FE + BE |
| **NEW-13** | Dedicated OTA forwarding channel + acknowledgment receipt + SLA (Trigger 3) | OTA Staff | MAJOR | Ops/product |
| **NEW-14** | `resolution_note` mandatory (not optional) on `closed_no_action` | Customer | MAJOR | BE validation |
| **NEW-15** | Escalation path for customer when status stalls (N days with no movement) | Customer | MAJOR | Product |
| **NEW-16** | Mixed-booking cancellation coordination (direct + OTA pax on same physical boat) | Operator | Open | Product |

---

### Updated Open Questions (post-meeting, re-tiered 2026-06-27)

> **Re-tier rationale:** OQ-8 raised as blocker by OTA Staff persona (Klook) — but Klook already SENDS booking data to SmartEnPlus as the operator they hired. Storage in Django is same data, same purpose, different DB. Contract performance basis (PDPA §24(3)) applies. No separate DPA needed. Klook's concern is valid for MARKETING use — not for SERVICE operations. OQ-8 downgraded to housekeeping items only. Same logic applied to OQ-9 (channel conflict) and NEW-9 below.

| # | Question | Severity | Owner | Notes |
|---|---|---|---|---|
| OQ-1 | Supabase plan — supports pg_net webhooks? | **CLOSED** | — | Celery fetch confirmed. Django polls Supabase directly. No webhook needed. |
| OQ-3 | SLA for `awaiting_ota_update` — define timeout + surface ETA to customer at submit | **BLOCKER** | Product | All 5 voices raised this. No bound = customer stuck forever. |
| OQ-6 | Magic link expiry — admin regenerate + self-serve re-request path | **BLOCKER** | BE + FE | OTA guest can't see resolution if link expired |
| NEW-1 | `awaiting_ota_update` resolve-block until `OtaBookingEvent` exists after status set | **BLOCKER** | BE | Prevents admin creating "Approved" lie on stale data |
| OQ-7 | Request feasibility validation at API — reject impossible requests or let admin reject? | MAJOR | BE | Ops load question |
| OQ-5 | Quarantined booking + customer request — block or allow? | MAJOR | BE | Guard missing |
| NEW-4 | Emergency cancellation fast-track — bypasses state machine for weather/same-day | MAJOR | Product + BE | 90min to departure, 4 handoffs won't work |
| NEW-5 | Duty/on-call contact — who operator reaches at 4:30am | MAJOR | Ops | Ops SLA, not engineering |
| NEW-6 | Magic link email redesign — "You booked [Trip] via Klook" line 1 + fallback contact footer | MAJOR | FE + comms | Near-zero open rate without this for non-Thai pax |
| NEW-7 | i18n plan — English-only excludes Thai, Japanese, Korean, Russian OTA customers | MAJOR | Product decision | Scope + priority call |
| NEW-10 | Manifest push to operator on resolved seat-count ticket | MAJOR | BE + ops | Safety issue — stale manifests |
| NEW-13 | Dedicated OTA forwarding channel (Trigger 3) + ack receipt + SLA | MAJOR | Ops/product | Currently "email admin" with no SLA |
| **OQ-8** | ~~PDPA DPA required before storing Klook PII in Django~~ | ~~BLOCKER~~ → **CLOSED** | — | **Lawful as-is.** Klook sends data TO SmartEnPlus (operator). Contract performance basis (PDPA §24(3)). Same data already in Supabase. Django = same purpose, better system. Three housekeeping items only (see below). |
| NEW-9 | Channel conflict — no upsell/account-creation in `/my-trip` | MINOR (was MAJOR) | Owner | Owner confirms intent. Simple policy decision, not a launch gate. |
| NEW-2 | ~~`partner_case_id` field on Ticket~~ | **CLOSED** | — | NOT NEEDED. Already track via `(source, booking_id)` on `CsOtaBooking`. `Ticket.content_object` → `CsOtaBooking` provides linking. No separate case ID field needed. |
| NEW-3 | Automated SES on all ticket transitions — spec which fire | MAJOR | BE + product | Tied to OQ-3 SLA |
| NEW-11 | Supersede (M-6) confirmation modal | MAJOR | FE + UX | One misclick closes live customer request |
| NEW-12 | Bulk close for group cancellation | MAJOR | FE + BE | Ops efficiency |
| NEW-14 | `resolution_note` mandatory on `closed_no_action` | MAJOR | BE validation | Easy — add `blank=False` when status = this |
| NEW-15 | Escalation path if status stalls N days | MAJOR | Product | Ties to OQ-3 |
| NEW-16 | Mixed-booking cancellation (direct + OTA pax on same boat) | Open | Product | Harder ops problem, deferred |
| OQ-2 | SMS provider (Twilio/SNS)? | Minor | Infra | Additive, not blocking |

---

### OQ-8 Housekeeping Items (not blockers, do before prod at scale)

| Item | Action | Who |
|---|---|---|
| Check Klook operator agreement for any secondary-storage restriction clause | Read signed contract — most restrict MARKETING not SERVICE | Owner |
| PII retention + purge | Add `pii_purge_after` date field on `CsOtaBooking` or scheduled task (trip_date + 90 days) | BE |
| Privacy notice in `/my-trip` | One sentence: "Your booking data was shared by [OTA] to enable your trip service" | FE |
| Confirm `CsOtaBooking` not exposed via public API | Check `cs/urls.py` — all endpoints require `IsAdminOrIsStaff` | BE audit |
| OQ-9 (new) | i18n scope for `/my-trip` portal — which languages, when? | MAJOR | Product |
| OQ-10 (new) | Emergency duty channel — on-call policy and contact for operators? | MAJOR | Ops |
| OQ-11 (new) | Channel conflict policy — written confirmation no upsell in OTA guest portal? | MAJOR (commercial) | Owner |

---

### Stakeholder Meeting #2 — Post-Sync-Decision (2026-06-27)

**Trigger:** User requested 4-persona re-discussion after confirming sync approach (Django fetches FROM Supabase via Celery 15min + on-demand admin; n8n/webhook dropped).

**Participants:** Staff (Nong — CS Lead), OTA (Klook Relations Manager), Operator (Andaman Sea Transport), Customer (Yuki — Japanese tourist via Klook).

**Verdict:** UNANIMOUS convergence on 3 BLOCKERS that must gate go-live. All 4 voices raised the same issues independently.

---

### Cross-Blocker Summary (All 4 Personas)

| # | Blocker | Raised by | Why unanimous |
|---|---|---|---|
| **NEW-1** | Resolve-block guard on `awaiting_ota_update` | Staff, OTA, Customer | Admin can mark "Approved" before Supabase updates → credibility gap |
| **OQ-3** | SLA defined + displayed to customer | Staff, OTA, Customer | "Waiting for Review" with no ETA = infinite limbo |
| **Emergency Path** | Manifest push + duty contact + fast-track spec | Operator (safety), Staff (ops) | 15min sync unacceptable for same-day; stale manifests = safety issue |

---

### Detailed Blocker Specs (Added 2026-06-27)

#### NEW-1 — `awaiting_ota_update` Resolve-Block Guard + Process Visibility

**Current broken flow:**
```
Ticket awaiting_ota_update → Admin clicks Resolve → "Approved ✓" shown
→ Supabase hasn't synced yet (15min gap)
→ Customer calls Klook → Klook says "not processed"
→ Customer escalates with SmartEnPlus screenshot
```

**Root problem:** Guard alone blocks resolve but provides ZERO visibility into:
- Whether admin actually contacted OTA
- When Supabase last synced
- What customer sees (just "Update in Progress" with no context)
- When it's safe to resolve (OTA contact time + no response)

**Required implementation (3 parts):**

---

**Part A — Ticket model fields to track admin work:**

```python
# tickets/models.py

class Ticket(models.Model):
    # Existing fields...

    # NEW-1 additions
    admin_contacted_ota_at = models.DateTimeField(null=True, blank=True)
    admin_contacted_ota_note = models.TextField(null=True, blank=True)
    status_changed_at = models.DateTimeField(null=True, blank=True)
```

---

**Part B — Smarter guard logic with time-based overrides:**

```python
# tickets/models.py

def clean(self):
    from django.core.exceptions import ValidationError
    from django.core.exceptions import ValidationError
    from cs.models import OtaBookingEvent
    from datetime import timedelta

    # Block/allow resolve from awaiting_ota_update based on actual evidence
    if self._state_has_changed('request_status'):
        old_status = Ticket.objects.get(pk=self.pk).request_status if self.pk else None
        new_status = self.request_status

        if old_status == 'awaiting_ota_update' and new_status == 'resolved':
            # Check 1: Has Supabase updated since we entered awaiting? (Ideal path)
            if self.source == 'ota' and self.content_object:
                if OtaBookingEvent.objects.filter(
                    ota_booking=self.content_object,
                    created_at__gte=self.status_changed_at
                ).exists():
                    return  # Good to resolve - Supabase updated

            # Check 2: Admin contacted OTA recently (<4h ago) → too soon to give up
            if self.admin_contacted_ota_at:
                hours_since_contact = (now() - self.admin_contacted_ota_at).total_seconds() / 3600
                if hours_since_contact < 4:
                    raise ValidationError({
                        'request_status': f'OTA contacted {int(hours_since_contact)}h ago. '
                                          f'Too soon to resolve. Wait at least 12h for response or click "Sync Now".'
                    })

                # Check 3: Admin contacted OTA 4-12h ago → may still be processing
                if hours_since_contact < 12:
                    raise ValidationError({
                        'request_status': f'OTA contacted {int(hours_since_contact)}h ago, '
                                          f'no Supabase update yet. Contact OTA again or wait longer?'
                    })

                # Check 4: 12h+ since OTA contact with no response → allow resolve (override)
                # This handles non-responsive OTA edge case
                return

            # No OTA contact recorded + no Supabase update → block resolve
            raise ValidationError({
                'request_status': 'Cannot resolve awaiting OTA ticket. '
                                  'No Supabase update since awaiting started, and no OTA contact recorded. '
                                  'Either: (1) Click "Sync Now" and wait for Supabase update, '
                                  '(2) Contact OTA and record it below, or (3) Wait 12h after contact.'
            })

def save(self, *args, **kwargs):
    if self._state_has_changed('request_status'):
        self.status_changed_at = now()
    super().save(*args, **kwargs)
```

---

**Part C — Customer-facing visibility:**

```jsx
// TicketStatusBanner.jsx (FE component)

{ticket.request_status === 'awaiting_ota_update' && (
  <AwaitingMessage>
    <Text>We've contacted Klook/12Go. Waiting for them to process.</Text>
    {ticket.admin_contacted_ota_at && (
      <Text>
        Last contact: {formatDate(ticket.admin_contacted_ota_at)} at {formatTime(ticket.admin_contacted_ota_at)}
        {ticket.admin_contacted_ota_note && ` — ${ticket.admin_contacted_ota_note}`}
      </Text>
    )}
    <SLA>Expected response: within 24 hours</SLA>
    <ContactIfStuck>
      No response by {formatSLADeadline(ticket.sla_deadline)}? 
      <ContactLink>Contact us</ContactLink>
    </ContactIfStuck>
  </AwaitingMessage>
)}
```

---

**Part D — Admin sync banner (visibility):**

```jsx
// SupabaseSyncBanner.jsx (FE component in admin ticket detail)

{ticket.source === 'ota' && (
  <Banner>
    <Text>Last Supabase sync: {formatRelative(latestEvent.created_at)}</Text>
    {latestEvent.created_at < ticket.status_changed_at && (
      <Warning>
        ⚠️ Supabase hasn't updated since ticket entered awaiting state ({formatRelative(ticket.status_changed_at)})
      </Warning>
    )}
    <Button onClick={handleSyncNow}>Sync Now</Button>
  </Banner>
)}
```

---

**Use case this solves:**

```
T+0: Customer submits cancellation → Ticket: awaiting_ota_update
T+5: Admin calls Klook → sets admin_contacted_ota_at=now, admin_contacted_ota_note="Spoke to John, case #12345"
T+5: Customer sees "We contacted Klook at 10:05am. Waiting for them to process."
T+10: Admin tries to resolve → error "Too soon (5h ago). Wait 12h."
T+60: Klook processes → Supabase sync → OtaBookingEvent created
T+61: Admin clicks Resolve → validation checks OtaBookingEvent.exists() → succeeds
T+62: Customer sees "Cancellation Confirmed"
```

**Cost:** 3 hours BE (model + guard) + 2 hours FE (banner + customer status) + 1 hour test

**Cost:** 2 hours BE (model + tests) + 1 hour FE (admin error display)

---

#### OQ-3 — SLA Definition + Customer Display (Sequential Dependency)

**Current broken flow:**
```
Customer submits request → "Waiting for Review" → no ETA
→ 2 days pass, no movement
→ Customer: re-book? call? wait? No escalation path.
```

**Actual workflow (sequential dependency):**
```
Customer requests date change → Admin asks Operator first (can we change?)
→ Operator responds (24h) → IF yes, Admin contacts OTA (48h)
→ OTA updates → Supabase sync → Admin resolves
```

**Confirmed by user:**
- Stage 1 (Operator check): **24 hours**
- Stage 2 (OTA update): **48 hours**  
- Total worst case: **72 hours**
- **If Operator says "no" at any point → immediate rejection** (don't wait for OTA)

---

**Required implementation (4 parts):**

**Part A — Two-stage SLA model:**

```python
# tickets/models.py

class Ticket(models.Model):
    # SLA tracking per stage
    ack_deadline = models.DateTimeField(null=True, blank=True)  # 4h (acknowledgment)
    operator_deadline = models.DateTimeField(null=True, blank=True)  # 24h (Stage 1)
    ota_deadline = models.DateTimeField(null=True, blank=True)  # 48h (Stage 2)
    resolution_deadline = models.DateTimeField(null=True, blank=True)  # 72h total
    
    # Which stage we're in
    resolution_stage = models.CharField(
        max_length=20,
        choices=[
            ('ack', 'Acknowledgment'),
            ('operator_check', 'Operator Check'),
            ('ota_update', 'OTA Update'),
            ('ready_to_resolve', 'Ready to Resolve'),
        ],
        default='ack'
    )
    
    # Operator response (what they said)
    operator_response = models.TextField(null=True, blank=True)  # "Confirmed availability" or "Cannot accommodate"
    
    # OTA response (what they said)
    ota_response = models.TextField(null=True, blank=True)  # "Processed, email sent" or "Policy doesn't allow"
```

**Part B — SLA calculation by request type:**

```python
def get_resolution_hours(source, request_type):
    """Return resolution SLA based on source + type."""
    # Sequential: Operator + OTA
    if request_type == 'cancellation':
        return 36  # 12h operator + 24h OTA (faster for refunds)
    if request_type in ['date_change', 'pax_change']:
        return 72  # 24h operator + 48h OTA (changes take longer)
    return 24  # other (no OTA needed)

def create_ticket(request):
    # Acknowledgment always 4h
    ack_deadline = calculate_business_deadline(hours=4, from_time=now())
    
    # Resolution depends on type
    resolution_hours = get_resolution_hours(
        source=request_data['source'],
        request_type=request_data['request_type']
    )
    resolution_deadline = calculate_business_deadline(
        hours=resolution_hours,
        from_time=now()
    )
    
    # Stage deadlines
    if request_type in ['date_change', 'pax_change', 'cancellation']:
        operator_hours = 12 if request_type == 'cancellation' else 24
        operator_deadline = calculate_business_deadline(hours=operator_hours, from_time=now())
        
        ota_hours = 24 if request_type == 'cancellation' else 48
        ota_deadline = calculate_business_deadline(hours=ota_hours, from_time=now())
    
    ticket = Ticket.objects.create(
        ack_deadline=ack_deadline,
        operator_deadline=operator_deadline,
        ota_deadline=ota_deadline,
        resolution_deadline=resolution_deadline,
        resolution_stage='ack',
        ...
    )
```

**Part C — Customer display (two-stage visibility):**

```jsx
// RequestConfirmation.jsx (after date change submit)

<SLAInformation>
  <AckSLA>✓ We'll review within 4 hours</AckSLA>
  
  <ProcessTimeline>
    <Stage1>
      <Step>Step 1: Operator check (24h)</Step>
      <Text>We'll ask the operator if this change is possible</Text>
      <Expected>Expected: {formatSLADeadline(ticket.operator_deadline)}</Expected>
    </Stage1>
    
    <Stage2>
      <Step>Step 2: OTA update (48h)</Step>
      <Text>If operator agrees, we'll contact Klook/12Go to update</Text>
      <Expected>Expected: {formatSLADeadline(ticket.ota_deadline)}</Expected>
    </Stage2>
    
    <TotalSLA>Total: 72 hours worst case</TotalSLA>
  </ProcessTimeline>
</SLAInformation>
```

**Part D — Status display (which stage):**

```jsx
// TicketStatusBanner.jsx

{ticket.resolution_stage === 'operator_check' && (
  <InReview>
    <Text>Being Reviewed — Checking with operator</Text>
    <SLA>Expected response: {formatSLADeadline(ticket.operator_deadline)}</SLA>
  </InReview>
)}

{ticket.resolution_stage === 'ota_update' && (
  <AwaitingOTA>
    <Text>Operator confirmed — Waiting for OTA to update</Text>
    <SLA>Expected OTA response: {formatSLADeadline(ticket.ota_deadline)}</SLA>
    <SyncStatus>Last Supabase sync: {formatRelative(latestEvent.created_at)}</SyncStatus>
  </AwaitingOTA>
)}
```

**Part E — Immediate rejection if Operator says no:**

```python
# tickets/views.py (admin response)

def record_operator_response(ticket_id, response_text, can_proceed):
    """Admin records Operator response."""
    ticket = Ticket.objects.get(pk=ticket_id)
    ticket.operator_response = response_text
    
    if can_proceed:
        # Operator said yes → proceed to OTA stage
        ticket.resolution_stage = 'ota_update'
    else:
        # Operator said no → reject immediately (don't wait 48h for OTA)
        ticket.request_status = 'rejected'
        ticket.resolution_note = f"Operator cannot accommodate: {response_text}"
    
    ticket.save()
```

**Part F — SLA breach alerts (per stage):**

```python
# tickets/tasks.py

@shared_task
def check_sla_breaches():
    # Stage 1 breach: Operator not responding
    operator_overdue = Ticket.objects.filter(
        resolution_stage='operator_check',
        operator_deadline__lt=now()
    )
    for ticket in operator_overdue:
        slack_send(f"🚨 OPERATOR NOT RESPONDING: Ticket #{ticket.ticket_number}")
    
    # Stage 2 breach: OTA not responding
    ota_overdue = Ticket.objects.filter(
        resolution_stage='ota_update',
        ota_deadline__lt=now()
    )
    for ticket in ota_overdue:
        slack_send(f"🚨 OTA NOT RESPONDING: Ticket #{ticket.ticket_number}")
```

**Cost:**
- BE: 6 hours (model + two-stage SLA calc + alerts + rejection logic)
- FE: 3 hours (two-stage display + status banner)
- Product: 1 hour (confirm SLA values)
**Total:** 10 hours

---

**Working hours:** 9am-10pm daily (13h/day). SLA calculations skip 10pm-9am.

**SLA matrix (confirmed):**
- Cancellation: 12h Operator + 24h OTA = 36h total
- Date/pax change: 24h Operator + 48h OTA = 72h total
- Other: 24h (no OTA needed)

---

#### Emergency Path (NEW-4 + NEW-5 + NEW-10)

**Confirmed reality:**
- **Team hours:** 6am-10pm daily (16h everyday, no weekends off)
- **Flexible hours:** Serious situations → team stays as long as needed
- **Proactive monitoring:** Team monitors conditions (weather, traffic, etc.) and updates operators directly
- **Operator contact:** WhatsApp or phone ONLY (no email)
- **Auto-acknowledgment:** NOT needed (manual response at 6am preferred)
- **Early departures:** No special SLA for 6am-7:30am departures (treated same as normal)

---

**Required implementation (3 parts):**

**Part A — Working hours config (NEW-5):**

```python
# ops/contact.py

TEAM_START_HOUR = 6  # 6am daily
TEAM_END_HOUR = 22    # 10pm daily
TEAM_DAYS = 'everyday'  # 7 days/week
```

**Product decision:** Document that team works flexible hours for emergencies — not rigid 6am-10pm.

**Part B — Emergency fast-track (NEW-4):**
```python
# tickets/models.py

class Ticket(models.Model):
    is_emergency = BooleanField(default=False)

    def clean(self):
        if self.is_emergency:
            # Emergency tickets bypass awaiting_ota_update
            # Must go straight to resolved (manual reconciliation later)
            if self.request_status not in ['pending', 'resolved']:
                raise ValidationError('Emergency tickets must skip to resolved')
```

**Part C — Manifest auto-push (NEW-10):**
```python
# tickets/signals.py

@receiver(post_save, sender=Ticket)
def push_manifest_on_resolution(sender, instance, created, **kwargs):
    if instance.request_status == 'resolved' and instance.request_type in [
        'cancellation', 'pax_change', 'date_change'
    ]:
        if instance.source == 'ota':
            push_manifest_to_operator(instance.ota_booking.trip_id, instance.ota_booking)
        else:
            push_manifest_to_operator(instance.booking_item.trip_id, instance.booking_item)

def push_manifest_to_operator(trip_id, booking):
    # v1: email fallback
    send_operator_manifest_email(
        trip_id=trip_id,
        manifest_pdf=generate_manifest_pdf(trip_id),
        change_details={'booking_id': booking.booking_id, 'change_type': instance.request_type}
    )
```

**Part D — Emergency SES:**
```python
# tickets/tasks.py

@shared_task
def send_emergency_customer_notifications(ticket_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    if ticket.is_emergency:
        # Send to ALL customers on this trip, not just ticket creator
        bookings = CsOtaBooking.objects.filter(trip_id=ticket.ota_booking.trip_id)
        for booking in bookings:
            send_ses_email(template='emergency_cancellation', to=booking.email, ...)
```

**Cost:**
- NEW-5 (working hours): 30min config (team already knows schedule)
- NEW-4 (emergency model): 4h BE
- NEW-10 (manifest push): 6h BE
- Emergency SES: 3h BE
**Total:** 13h BE (reduced from 18h because no 24/7 auto-ack needed)

**Key changes from earlier draft:**
- No auto-acknowledgment (manual response preferred)
- Everyday schedule (not weekdays only)
- Flexible hours documented (team stays late for emergencies)
- No special SLA for early departures

---

#### Magic Link Blockers (OQ-6 + NEW-6)

**Current broken flows:**

**Broken flow A (7-day expiry):**
```
Day 1: Customer books via Klook → Email: "Access here: [magic link]"
       → Link expires in 7 days

Day 10: Customer clicks link
       → Screen: "Link expired"
       → No regeneration button
       → No "request new link" option
       → No contact info in email
       → CUSTOMER DEAD END
```

**Broken flow B (phishing email):**
```
Subject: Your SmartEnPlus Trip

Hello,

Access your booking here:
[Link]

Thanks,
SmartEnPlus Team
```

**Problem:** No Klook branding context → Japanese tourist deletes email → never sees link.

---

**Confirmed reality:**
- **Link expiry:** Trip-date based, NOT 7-day timer
  - Valid until trip date + 7 days (post-trip feedback period)
  - No auto-expiry based on time
  - If trip is Day 50, link valid until Day 50
- **Delivery:** Admin manually sends (primary) + optional auto-send (secondary)
  - Admin copies link from admin panel → pastes into WhatsApp/chat
  - Admin clicks "Resend email" button → sends fresh email
  - Optional: System auto-sends when booking created (toggle per booking)
- **NO post-resolution send:** When ticket updated, no magic link email sent (v2 feature)

---

**Required implementation (3 parts):**

**Part A — Trip-date expiry logic (OQ-6):**

```python
# cs/models.py

class CsOtaBooking(models.Model):
    # Magic token properties
    magic_token = models.CharField(max_length=100, unique=True)
    magic_token_generated_at = models.DateTimeField(null=True, blank=True)
    
    @property
    def is_magic_link_valid(self):
        """Link valid if trip hasn't happened yet or within 7 days post-trip."""
        if not self.booking_date:
            return False
        
        # Valid if trip date is in future
        if self.booking_date > now().date():
            return True
        
        # After trip date, valid for 7 days (for feedback/reviews)
        days_since_trip = (now().date() - self.booking_date).days
        return days_since_trip <= 7
```

**Part B — Admin manual send (primary methods):**

**Admin panel UI:**
```jsx
// AdminBookingDetail.jsx

<MagicLinkSection>
  <Label>Customer magic link:</Label>
  <CopyButton onClick={copyMagicLink}>
    {magicLink}
  </CopyButton>
  
  <ResendEmailButton onClick={resendEmail}>
    📧 Resend magic link email
  </ResendEmailButton>
</MagicLinkSection>
```

**API endpoint:**
```python
# cs/views.py

class ResendMagicLinkView(APIView):
    permission_classes = [IsAdminOrIsStaff]
    
    def post(self, request):
        booking_id = request.data.get('booking_id')
        
        booking = CsOtaBooking.objects.get(id=booking_id)
        
        # Regenerate token
        new_token = generate_magic_token()
        booking.magic_token = new_token
        booking.magic_token_generated_at = now()
        booking.save()
        
        # Send email with NEW template (NEW-6)
        send_magic_link_email(booking, new_token)
        
        return Response({
            'status': 'sent',
            'link': build_magic_link(new_token)
        })
```

**Part C — Optional auto-send (NEW-6 email redesign):**

**Email template (NEW-6):**
```
Subject: You booked [Trip Name] via Klook

Hello [Customer Name],

You booked [Trip Name] through Klook.
SmartEnPlus is your tour operator.

Access your booking details and make changes:
[Magic Link]

What you can do:
• View booking status
• Request date changes or cancellations
• Track request progress

Questions?
WhatsApp: +66812345678
LINE: @smartenplus
```

**Auto-send logic (optional feature):**
```python
# cs/models.py

class CsOtaBooking(models.Model):
    auto_send_magic_link = models.BooleanField(default=True)  # NEW: optional auto-send
    
    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)
        
        # Auto-send magic link email when booking created
        if is_new and self.auto_send_magic_link:
            send_magic_link_email(self, self.magic_token)
```

**Admin control:**
```python
# cs/admin.py

class CsOtaBookingAdmin(admin.ModelAdmin):
    list_display = ['booking_id', 'customer_name', 'auto_send_magic_link']
    list_editable = ['auto_send_magic_link']  # Admin can toggle per booking
```

---

**Use cases:**

**Manual WhatsApp (primary):**
```
Day 1: Booking created → Admin toggles OFF auto-send
       → Admin WhatsApps: "Welcome! Your trip access: [magic link]"
       
Day 40: Customer wants to cancel → Admin copies link → WhatsApps to customer
       → Customer accesses portal → submits cancellation
```

**Auto email (optional):**
```
Day 1: Booking created → auto_send_magic_link = True (default)
       → System auto-sends email immediately
       
Day 10: Customer lost email → Admin clicks "Resend email" → Fresh email sent
```

**No post-resolution send (confirmed by user):**
- Ticket resolved → NO magic link email sent (that's v2)
- Customer sees resolution via portal, not via new magic link

---

**Cost:**
- OQ-6 (trip-date expiry + manual send): 1h BE + 0.5h FE (copy button)
- NEW-6 (email redesign): 1h FE + 30min comms
- Auto-send (optional): 1h BE + 1h FE (toggle UI + send logic)
- **Base total (manual only):** 2.5h
- **With auto-send:** 4.5h

---

### Updated Open Questions (Post-Meeting #2)

| # | Question | Severity | Owner | Notes |
|---|---|---|---|---|
| **NEW-1** | Resolve-block guard on `awaiting_ota_update` — implemented? | **BLOCKER** | BE | All 4 personas raised. Prevents "Approved" lie. |
| **OQ-3** | SLA defined + surfaced to customer at submit | **BLOCKER** | Product + BE | All 4 personas raised. No ETA = infinite limbo. |
| **Emergency Path** | NEW-4 fast-track + NEW-5 duty contact + NEW-10 manifest push | **BLOCKER** | Ops + BE | Operator safety gate. 15min sync unacceptable for same-day. |
| OQ-1 | Supabase plan — supports pg_net? | **CLOSED** | — | Celery fetch confirmed. No webhook needed. |
| OQ-6 | Magic link trip-date expiry + admin manual/optional auto-send | **BLOCKER** | BE + FE | Link expires based on travel date, not 7-day timer. Admin sends via WhatsApp/email. |
| NEW-6 | Magic link email trust context (Klook branding + fallback contact) | **MAJOR** | FE + Comms | Near-zero open rate without this for non-Thai pax |
| NEW-2 | `partner_case_id` field on Ticket | **MAJOR** | BE — easy | 5-min model change, prevents Trigger 3 dedup failure |
| NEW-3 | Automated SES on all ticket transitions | **MAJOR** | BE + Product | Spec which ones fire |
| NEW-7 | i18n plan for /my-trip portal | **MAJOR** | Product | English-only excludes major OTA customer segments |
| NEW-9 | Channel conflict — no upsell in /my-trip | **MINOR** | Owner | Policy decision, not engineering |
| OQ-2 | SMS provider (Twilio/SNS)? | Minor | Infra | Additive, not blocking |

---

### PM Verdict After Meeting #2

**Status stays `fix-then-ship`.** 3 BLOCKERS confirmed by all 4 personas. These must gate go-live.

**Launch sequence (priority order):**

1. **NEW-1** (resolve-block guard) — 3 hours BE+FE
2. **OQ-3** (SLA + display) — 10 hours total (sequential 24h+48h)
3. **Emergency path** (NEW-4 + NEW-5 + NEW-10) — 13.5 hours total
4. **OQ-6** (magic link manual + optional auto) — 2.5h base, 4.5h with auto-send
5. **NEW-6** (magic link email redesign) — 1.5h total (email template + comms)

**Can ship incrementally (post-launch):**
- ~~NEW-2 (partner_case_id)~~ — CLOSED (not needed, already tracked via `CsOtaBooking.(source, booking_id)`)
- NEW-3 (SES spec) — 4-8 hours BE
- NEW-7 (i18n) — product scope decision
- NEW-12 (bulk close)
- NEW-15 (escalation path)

**What can ship NOW (no new blockers):**
- CS chat widget (pending `cs_chat` FeatureFlag seed)
- P3a OTA portal (read-only trip view, deployed)
- Existing ticket queue in admin

---

## Related

**OQ-8 CLOSED — PM rationale:** Klook/12Go send booking data TO SmartEnPlus as the hired transport operator. This data sharing already happens today (email → Supabase). Mirroring to Django = same data, same operational purpose, better system. PDPA §24(3) contract-performance basis applies. No DPA needed. Three housekeeping items only (contract clause check, PII retention/purge, portal privacy notice) — none block go-live.

**What can ship now (already built, no new blockers):** CS chat widget (pending `cs_chat` FeatureFlag seed), P3a OTA portal (read-only trip view, already deployed), existing ticket queue in admin.

---

## Related

[[booking-command-centre-decision]] (parent) · [[cs-architecture-decision]] · [[cs-api-contract]] · [[cs-consent-gdpr-model]] · [[cs-centralization-stack]] · [[supabase-ota-booking-store]] · [[cs-guest-storm-investigation]]
