---
name: cs-centralization-gap-report-2026-06-27
description: Cross-layer implementation gap report for CS-Centralization. Compares actual codebase state (BE/FE/admin) against cs-workflow-revised-2026-06-27. Written by 3-agent deep analysis + synthesis. Single source of truth for what's built vs what must ship.
metadata:
  type: project
  status: active
  date: 2026-06-27
  parent: cs-workflow-revised-2026-06-27
---

# CS-Centralization — Implementation Gap Report (2026-06-27)

> **3-agent deep analysis** (backend explorer + frontend explorer + vault analyst). Ground-truth from reading actual code, not the workflow doc's claims. Every BUILT/MISSING below is source-verified.

> **Reference:** [[cs-workflow-revised-2026-06-27]] (fix-then-ship, 4 blockers gating go-live). [[cs-centralization-blockers-implementation]] (31/31 tests passing, merged main).

---

## Summary

Backend is in excellent shape — all 4 workflow blockers implemented, 31/31 tests passing, 5 migrations applied. The **critical gap cluster is in the frontend OTA guest path** (`/my-trip`) and **2 missing BE endpoints** (on-demand sync + resend magic link). Admin dashboard Phase 1 was shipped in the previous session (branch `feat/cs-workflow-revised-gaps`). Three "built" items from the workflow doc are **not yet in the backend** (CsOtaBooking magic link fields + supabase_row_id). OTA sync task exists but **does not yet create OtaBookingEvent records** — admin verifying blind.

**Overall readiness: ~65%. Backend models ✅ · Backend endpoints PARTIAL · Frontend auth ✅ · Frontend OTA ❌ · Admin PARTIAL**

---

## Layer 1 — Backend (Django)

### Built ✅

| Item | Location | Notes |
|---|---|---|
| `Ticket.request_status` max_length=25 | `tickets/models.py:60-61` | All 6 values incl. `awaiting_ota_update`, `closed_no_action` |
| `Ticket.admin_initiated` BooleanField | `:92` | Replaces 3-value `initiated_by` [FIX M-1] |
| `Ticket.resolution_note` TextField | `:95` | null/blank |
| `Ticket.resolved_at/resolved_by` | `:98-101` | FK to User SET_NULL |
| `Ticket.admin_contacted_ota_at/note` | `:66-67` | NEW-1 resolve-block tracking |
| `Ticket.status_changed_at` | `:68` | Auto-set on status change |
| SLA fields (ack/operator/ota/resolution_deadline) | `:71-74` | All 4 DateTimeFields |
| `Ticket.resolution_stage` CharField | `:75-84` | choices: ack/operator_check/ota_update/ready_to_resolve |
| `Ticket.operator_response`, `ota_response` | `:85-86` | |
| `Ticket.is_emergency` BooleanField | `:89` | Emergency path bypass [NEW-4] |
| GenericFK (`content_type`+`object_id`+`content_object`) | `:53-55` | [FIX B-2] no duplicate ota_booking FK |
| `Ticket.ota_booking` property | `:219-223` | Returns content_object when source='ota' |
| `Ticket.clean()` resolve-block guard | `:108-170` | [NEW-1] 3-check logic: OtaBookingEvent exists / OTA contact timing / emergency override |
| `Ticket.clean()` `closed_no_action` resolution_note required | `:157-162` | [NEW-14] |
| `Ticket.calculate_sla_deadlines()` | `:185-216` | Auto-calc all 4 deadlines on create |
| `TripNotification` model + CheckConstraint | `cs/models.py:206-258` | `tripnotification_exactly_one_booking` [FIX M-5] |
| `OtaBookingEvent` model (no `matched_ticket`) | `cs/models.py:171-203` | [FIX M-2] — trigger/field_diffs/raw_payload/created_at(indexed) |
| `CsOtaBooking.previous_status` property | `:160-168` | Reads from OtaBookingEvent history [FIX M-3] |
| `check_sla_breaches` Celery task | `tickets/tasks.py:120-177` | Alerts on operator_deadline + ota_deadline breach |
| `send_emergency_customer_notifications` Celery task | `tickets/tasks.py:8-74` | Notifies ALL pax on trip [NEW-4] |
| Signal: `send_admin_initiated_notification` | `tickets/signals.py:9-55` | Email fires on admin_initiated create [FIX M-7] |
| Signal: `push_manifest_on_resolution` | `tickets/signals.py:58-107` | Manifest push to operator on resolve [NEW-10] |
| Signal: `send_resolution_notification` | `tickets/signals.py:110-157` | Customer email on terminal status |
| `POST /api/tickets/customer-requests/` | `tickets/urls.py:10` | Direct customer ticket create |
| `POST /api/cs/ota/change-request/` | `cs/urls.py:31` | OTA guest ticket create |
| `GET /api/cs/ota/trip/` | `cs/urls.py:29` | OTA trip read view |
| `sync_ota_bookings` Celery task exists | `cs/tasks.py:68` | Celery beat, 15min |

---

### Missing — BLOCKER ❌

**BE-B1 — `CsOtaBooking` magic link fields all absent**

The workflow doc (OQ-6) specifies 4 fields + 1 property on `CsOtaBooking`. None exist in the model:

```python
# MISSING — must add:
magic_token = CharField(max_length=100, unique=True)
magic_token_generated_at = DateTimeField(null=True, blank=True)
auto_send_magic_link = BooleanField(default=True)
is_magic_link_valid  # property: trip_date + 7d window

# Also missing:
supabase_row_id = CharField(max_length=100, null=True, unique=True)
```

Blocking: without `magic_token`, admin cannot generate/resend a magic link. The "Copy Link" + "Resend email" buttons in admin (already FE-built) have no data to work with.

---

**BE-B2 — `POST /api/cs/ota/sync/` missing**

Admin "Sync Now" button (built in admin FE) calls this endpoint. It does not exist in `cs/urls.py`. No `OtaSyncView`.

Workaround: Celery beat runs every 15min. On-demand sync requires this endpoint.

---

**BE-B3 — `POST /api/cs/ota/resend-magic-link/` missing**

Admin "Resend Email" button calls this endpoint. No `ResendMagicLinkView` in `cs/urls.py`. Without `magic_token` field (BE-B1) this also can't function.

---

**BE-B4 — `PATCH /admin-dashboard-tickets/request-status/{ticket_number}/` doesn't accept blocker fields**

Route exists (`tickets/urls.py:11` → `RequestStatusViewSet`). But `partial_update` in `tickets/views.py:236-260` only processes `request_status`. Does NOT accept:
- `admin_contacted_ota_at`
- `admin_contacted_ota_note`
- `is_emergency`

The admin FE (built last session) PATCHes these fields but backend silently ignores them. The resolve-block guard can never be satisfied because `admin_contacted_ota_at` can never be set via API.

---

**BE-B5 — `sync_ota_bookings` does not create `OtaBookingEvent` records**

`cs/tasks.py:68` exists and upserts `CsOtaBooking` via `update_or_create`. But it does **not** create `OtaBookingEvent` records on field changes. Without these records:
- `Ticket.clean()` resolve-block guard (NEW-1) can never pass — the guard checks `OtaBookingEvent.objects.filter(ota_booking=..., created_at__gte=status_changed_at).exists()` and will always fail
- Admin sees no sync history banner
- `previous_status` property returns None always

This makes the entire resolve-block guard (the #1 BLOCKER) non-functional end-to-end despite being built.

---

### Missing — MAJOR ⚠️

**BE-M1 — `CsOtaBooking.set_logs` not replaced**

`cs/models.py:139`: `set_logs = CharField(max_length=100, null=True, blank=True)` still present. Spec says replace with `OtaBookingEvent` (append-only log). OtaBookingEvent model exists but `set_logs` is still the only thing sync task writes. Until `sync_ota_bookings` creates OtaBookingEvent records (BE-B5), this stays as fallback.

**BE-M2 — No `calculate_business_deadline()` verified**

`Ticket.calculate_sla_deadlines()` presumably calls some business-hours helper. Spec says deadlines skip 10pm–9am. Working hours confirmed 6am–10pm (team is everyday flexible). Need to verify the actual deadline calculation matches the confirmed SLA matrix:
- Cancellation: 12h operator + 24h OTA = 36h total
- Date/pax change: 24h operator + 48h OTA = 72h total
- Other: 24h (no OTA)

**BE-M3 — NEW-3 SES transition emails not fully specified**

`send_resolution_notification` signal fires on terminal status. But which transitions fire SES? Spec (NEW-3) says specify all — `pending→in_review`, `in_review→awaiting_ota_update`, `awaiting_ota_update→resolved` each need customer emails. Only resolution is confirmed wired.

**BE-M4 — OQ-7 feasibility validation not built**

Request feasibility (reject impossible dates, past-dates) not in ticket create views. Manual admin rejection still required for infeasible requests.

**BE-M5 — OQ-5 quarantined booking + customer request guard missing**

If `CsOtaBooking.status='quarantined'`, customer can submit a ticket. No guard at ticket create. Edge case but can produce confusing state.

---

### Missing — Post-Launch

- NEW-12: Bulk close endpoint for group cancellation
- NEW-15: Escalation Celery task when ticket stalls N days
- i18n (NEW-7): API locale negotiation not required yet (product decision)

---

## Layer 2 — Frontend Customer Surfaces

### Built ✅

| Item | Location | Notes |
|---|---|---|
| `TicketStatusBanner` component | `components/bookings/TicketStatusBanner.js` | 632 lines. Includes AdminInitiatedBanner + ResolutionNote + SLAProgress + AwaitingOTAMessage sub-components |
| `AdminInitiatedBanner` in TicketStatusBanner | `:166-181` | "Update from SmartEnPlus" header when `ticket.admin_initiated` |
| `ResolutionNote` in TicketStatusBanner | `:183-195` | Renders `ticket.resolution_note` |
| `SLAProgress` in TicketStatusBanner | `:79-136` | Stage stepper (RequestProgressStepper equivalent) |
| `AwaitingOTAMessage` in TicketStatusBanner | `:138-164` | "We've contacted Klook/12Go. Waiting…" |
| `TicketStatusBanner` used in auth booking | `components/bookings/ChangeRequestsSection.js:31` | Maps tickets → TicketStatusBanner |
| `ChangeRequestsSection` in auth booking detail | `components/bookings/BookingDetailMain.js:211-214` | 60s poll via `ChangeRequestsSection` |
| `POST /api/tickets/customer-requests/` wired | Auth booking request modal | Direct customer ticket submission |

---

### Missing — BLOCKER ❌

**FE-B1 — my-trip re-submit bug NOT fixed**

`pages/my-trip/index.js:58`:
```javascript
const showForm = existingTickets.length === 0 && !localSubmitted
// BUG: blocks re-submit even after ticket resolves
```

Spec fix (verified refuted from codebase by Explore agent in original scrutiny pass):
```javascript
const openTickets = existingTickets.filter(t =>
  ['pending','in_review','awaiting_ota_update'].includes(t.request_status)
)
const showForm = openTickets.length === 0 && !localSubmitted
```

**Impact:** OTA guest who had a ticket resolved can never submit a new request. Permanently locked.

---

**FE-B2 — No polling on OTA trip query**

`store/api/otaApi.js:10-13`:
```javascript
getOtaTrip: builder.query({
  query: (token) => `/api/cs/ota/trip/?token=${encodeURIComponent(token)}`,
  providesTags: ['OtaTrip'],
  // ← no pollingInterval
}),
```

OTA guest sees stale ticket status unless they manually refresh. Spec: add `pollingInterval: 60000`.

---

**FE-B3 — `OtaRequestCard` missing resolution_note + admin_initiated**

`components/bookings/OtaRequestCard.js`: does not accept or render `resolution_note` or `admin_initiated`. OTA guest sees no outcome note after resolution, and no "Update from SmartEnPlus" header for admin-initiated tickets.

`TicketStatusBanner` has both — but is not used in `/my-trip` flow (uses `OtaRequestCard` instead).

---

**FE-B4 — No polling on auth booking detail**

`store/api/bookingsApi.js:76-85`: `useGetBookingDetailQuery` has no `pollingInterval`. Spec: conditional `pollingInterval: 120000` when booking has an active ticket.

---

### Missing — MAJOR ⚠️

**FE-M1 — `InfoUpdateNotice` component not built**

`TripNotification` model exists on BE. No FE component to surface it. Functionality partially embedded in `AwaitingOTAMessage` inside `TicketStatusBanner` but for a different purpose (OTA wait message, not admin info-push). Admin info updates (boarding point, weather) won't show to customer.

**FE-M2 — `TicketStatusBanner` not in `/my-trip` flow**

`/my-trip/index.js` uses `OtaRequestCard` — the simpler, feature-incomplete component. `TicketStatusBanner` (with all its sub-components) is never rendered for OTA guests. Fix = replace `OtaRequestCard` with `TicketStatusBanner` in my-trip, or extend `OtaRequestCard` to parity.

Recommended: replace with `TicketStatusBanner` — it already has all required sub-components.

**FE-M3 — No conditional polling wiring in `/bookings/[id]`**

Even when `ChangeRequestsSection` uses `TicketStatusBanner` correctly, the booking detail query doesn't auto-refresh. Customer must reload page to see status change.

---

### Missing — Post-Launch

- i18n: `/my-trip` English-only (NEW-7)
- NEW-9: No-upsell policy enforcement (owner decision, not engineering)

---

## Layer 3 — Admin Dashboard

### Built (previous session, branch `feat/cs-workflow-revised-gaps`) ✅

| Item | File |
|---|---|
| `VALID_TRANSITIONS` extended: `in_review → awaiting_ota_update, closed_no_action` | `command-centre/index.js` |
| `awaiting_ota_update`, `closed_no_action` in status filter + STATUS_COLOR | `command-centre/index.js` |
| OTA-aware ActionDialog labels for new transitions | `command-centre/index.js` |
| `SupabaseSyncBanner` (last event time + stale warning + Sync Now button) | `tickets/[id].js` |
| OTA contact record form (admin_contacted_ota_at + note) | `tickets/[id].js` |
| SLA deadline display (all 4 fields + resolution_stage chip) — null-safe | `tickets/[id].js` |
| `admin_initiated` header variant: "Update from SmartEnPlus" | `tickets/[id].js` |
| `resolution_note` display (OTA + direct) — parseOutcome fallback retained | `tickets/[id].js` |
| `is_emergency` checkbox toggle | `tickets/[id].js` |
| `csApi.js`: `resendMagicLink`, `syncOtaBookings`, `recordOtaContact` mutations | `store/api/csApi.js` |
| "Resend Email" column in OTA Bookings tab | `command-centre/index.js` |
| `REQUEST_STATUS_COLOR` extended with new statuses | `tickets/[id].js` |

### Still Missing ⚠️

| Item | Severity | Notes |
|---|---|---|
| NEW-11: Supersede confirmation modal | MAJOR | Before `closed_no_action` on open customer ticket — no BE endpoints exist yet for supersede signal |
| NEW-12: Bulk close UI | MAJOR | Multi-ticket select + close for group cancellation |
| `SupabaseSyncBanner` non-functional until BE-B2 + BE-B5 built | BLOCKER | Sync Now button has no endpoint; event history is always empty |
| Admin "Record Contact" non-functional until BE-B4 fixed | BLOCKER | PATCH endpoint ignores `admin_contacted_ota_at` + note fields |
| "Resend Email" non-functional until BE-B1 + BE-B3 built | BLOCKER | No magic_token field + no endpoint |
| Emergency toggle non-functional until BE-B4 fixed | BLOCKER | PATCH ignores `is_emergency` |
| `admin-dashboard-cs-centralization-plan.md` 4-phase plan | In progress | Phase 1 done; Phases 2-4 pending |

---

## Vault Doc Status

| Doc | Status | Verdict |
|---|---|---|
| `cs-workflow-revised-2026-06-27` | ✅ CURRENT | North star. All blockers locked. |
| `booking-command-centre-decision` | ✅ CURRENT | Rescope confirmed. P1 SHIPPED. |
| `cs-architecture-decision` | ✅ CURRENT | Both-poll confirmed. Supabase OUT. |
| `cs-api-contract` | ✅ CURRENT | 7 endpoints. Polling. Status=draft (should bump to accepted). |
| `cs-centralization-blockers-implementation` | ✅ CURRENT | 31/31 tests, merged. FE TicketStatusBanner built. |
| `supabase-ota-booking-store` | ✅ CURRENT | 561 OTA records. Read-only seed. |
| `cs-guest-storm-investigation` | ✅ CURRENT | Kill switch + 5-layer mitigation. FeatureFlag model built. |
| `cs-centralization-review-2026-06-22` | ✅ CURRENT | Edits applied. Bucket-C decisions still open (some now CLOSED per revised workflow). |
| `cs-consent-gdpr-model` | ✅ CURRENT | OQ-8 CLOSED per revised workflow (PDPA §24(3) applies). |
| `cs-design-tokens-audit` | ✅ CURRENT | 3 tokens fail WCAG. Design-system issue, CS consumes fix. |
| `cs-centralization-stack` | ⚠️ STALE (partial) | Transport section SUPERSEDED by cs-architecture-decision. Rest (OTP/SNS) valid. |
| `command-centre-ticket-booking-flow` | ⚠️ STALE (partial) | Quick-win Q1 DONE. Q2 (resolve→booking apply) still OPEN. `RequestStatusViewSet` still does not apply changes. |
| `admin-dashboard-cs-centralization-plan` | ⚠️ IN PROGRESS | Phase 1 done (prev session). Phases 2-4 pending. Should update status. |
| `cs-gap-debate-verdicts` | ✅ CURRENT | Verdicts finalized. Build order 1-8 partially executed. |
| `ota-portal-overview` + sub-plans | ✅ CURRENT | P3a SHIPPED. P3b request submit — FE partially built (OtaRequestCard), has blocker gaps above. |

---

## Recommended Next Steps (by severity)

### Immediate — unblock end-to-end functionality

| # | Task | Owner | Est | Unblocks |
|---|---|---|---|---|
| 1 | **BE: Add `CsOtaBooking` magic token fields** (magic_token, magic_token_generated_at, auto_send_magic_link, supabase_row_id) + migration | BE | 2h | OQ-6 end-to-end, admin Resend Email |
| 2 | **BE: Add `POST /api/cs/ota/sync/`** `OtaSyncView` → queues `sync_ota_bookings.delay()` async, returns task_id | BE | 1h | Admin Sync Now button, SupabaseSyncBanner |
| 3 | **BE: Add `POST /api/cs/ota/resend-magic-link/`** `ResendMagicLinkView` → regenerates token + fires SES | BE | 2h | Admin Resend Email button |
| 4 | **BE: Extend `RequestStatusViewSet.partial_update`** to accept + save `admin_contacted_ota_at`, `admin_contacted_ota_note`, `is_emergency` | BE | 1h | Resolve-block guard functional, emergency toggle |
| 5 | **BE: `sync_ota_bookings` task — add `OtaBookingEvent` creation** on field changes | BE | 2h | Resolve-block guard can pass, admin sync history |
| 6 | **FE: Fix my-trip re-submit bug** `pages/my-trip/index.js:58` — filter by open status, not length | FE | 30min | OTA re-submit after resolve |
| 7 | **FE: Add pollingInterval to `useGetOtaTripQuery`** in `otaApi.js` | FE | 15min | OTA guest sees live status |
| 8 | **FE: Replace `OtaRequestCard` with `TicketStatusBanner`** in `/my-trip`** — or extend OtaRequestCard to match TicketStatusBanner feature parity (resolution_note + admin_initiated) | FE | 2h | OTA guest sees full ticket state |
| 9 | **FE: Add conditional pollingInterval to `useGetBookingDetailQuery`** | FE | 30min | Auth booking auto-refreshes |

### Near-term — pre-launch quality

| # | Task | Owner | Est |
|---|---|---|---|
| 10 | Verify `calculate_business_deadline()` uses confirmed SLA matrix (36h cancel / 72h change / 24h other) | BE | 30min |
| 11 | Spec + implement NEW-3 SES on all ticket transitions (pending→in_review, in_review→awaiting, awaiting→resolved) | BE + Product | 4h |
| 12 | NEW-11 Supersede confirmation modal (admin closes live customer request) | FE | 2h |
| 13 | `InfoUpdateNotice` FE component — surfaces TripNotification records in /bookings + /my-trip | FE | 3h |
| 14 | `cs-api-contract.md` status: bump draft → accepted | Vault | 5min |

### Post-launch

- NEW-12 Bulk close (FE+BE)
- NEW-7 i18n plan (product decision)
- NEW-15 Escalation path for stalled tickets
- `set_logs` field removal after OtaBookingEvent is fully wired

---

## Related

[[cs-workflow-revised-2026-06-27]] · [[cs-centralization-blockers-implementation]] · [[booking-command-centre-decision]] · [[cs-architecture-decision]] · [[cs-api-contract]] · [[admin-dashboard-cs-centralization-plan]] · [[command-centre-ticket-booking-flow]] · [[ota-portal-overview]]
