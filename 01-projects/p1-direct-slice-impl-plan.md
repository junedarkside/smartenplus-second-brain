---
name: p1-direct-slice-impl-plan
description: STATUS NOTE — P1 direct vertical slice is SHIPPED (session #164, 2026-06-24). Ticket request spine, customer + staff endpoints, FE Request-Change modal, and admin command-centre queue all built, wired, and merged. This note records what exists (with file:line) + the small post-P1 items still open. NOT a build plan — P1 is done.
metadata:
  type: project
  status: shipped
  date: 2026-06-24
  shipped_session: 164
  parent: booking-command-centre-decision
---

# P1 — Direct Vertical Slice: STATUS (SHIPPED)

> ⚠️ **This is a status note, not a build plan.** P1 was built + merged in session #164 (2026-06-24).
> An earlier draft of this file described P1 as future work — that was wrong (written from the
> decision-doc roadmap without reading `tickets/` code). Two `/scrutinize` passes against live
> code corrected it. If you opened this to "start building P1", stop — it already exists.

Decision authority: [[booking-command-centre-decision]] (2026-06-23).

---

## Goal (achieved)

Staff command centre receives direct-booking change/pax/cancel requests via a unified queue.
Direct customers submit via "Request Change" on the booking detail page. Full loop works:
customer submits → staff transitions (`pending → in_review → resolved/rejected`) → terminal
state auto-closes ticket. **Direct bookings only** (OTA = P3).

---

## What exists (verified 2026-06-24)

### Backend (`smartenplus-backend/tickets/`)

| Piece | Location |
|---|---|
| Request fields on `Ticket` (`request_type`, `request_status`, `source`, `requested_value`) | `models.py:52-57` |
| Migration | `migrations/0004_add_request_fields_to_ticket.py` |
| `TicketSerializer` explicit fields (no `__all__` leak) | `serializers.py:54-62` |
| `CustomerTicketViewSet` — customer create + list (own only, `booking_id` filter) | `views.py:183-226` |
| `RequestStatusViewSet` — staff transition | `views.py:229-260` |
| `VALID_REQUEST_TRANSITIONS` state machine | `views.py:173-178` |
| Terminal auto-close (`resolved`/`rejected` → `ticket_status=Completed`, `is_resolved=True`) | `views.py:252-254` (commit `e7d2e03`) |
| Routes (`customer-requests`, `request-status`) | `tickets/urls.py` |

### Frontend (`smartenplus-frontend/components/bookings/`)

| Piece | Location |
|---|---|
| `RequestChangeModal.js` — type selector + note, submits via RTK | built + wired |
| `ChangeRequestsSection.js` — customer-facing status cards (60s poll) | built + wired |
| "Request Change" button | `BookingDetailMain.js:168-192` |
| Modal + section wired into booking detail | `BookingDetailMain.js:12-13, 211, 237` |
| RTK endpoints (`useSubmitChangeRequestMutation`, `useGetCustomerRequestsQuery`) | `store/api/bookingsApi.js:90-101` |

### Admin Dashboard (`admin-dashboard`)

| Piece | Location |
|---|---|
| Command-centre queue (request_status filter, confirm dialog, lifecycle) | `pages/dashboard/command-centre/index.js`, branch `feat/p1c-command-centre-admin` + `feat/command-centre-confirm-dialog` |

### Canonical vocab (as shipped — use these, not the earlier draft's invented values)

- **`request_type`:** `date_change` · `pax_change` · `cancellation` · `other`
- **`request_status`:** `pending` · `in_review` · `resolved` · `rejected`
- **`source`:** `direct` (default). OTA values added in P2/P3.

---

## Real open items (post-P1 — none block P1)

| Item | Phase | Status | Note |
|---|---|---|---|
| **SES notify on request events** | P4 | NOT built | Zero email refs in `tickets/`. Decision doc puts "notify on resolve" in P4 (`booking-command-centre-decision.md:41`). Optionally pull forward to P1.5 if staff want customer emails sooner. |
| **Reopen + rate-limit guard** | P4 | NOT built (by design) | `VALID_REQUEST_TRANSITIONS` terminal `[]` is intentional. Reopen = P4 hardening once ops validate the taxonomy. |
| **Nullable GenericFK** | P3 | NOT built (not needed for P1) | `content_type`/`object_id` non-nullable. P1 only attaches to `BookingItem` (always present). Needed only when account-level (booking-less) tickets land in P3. |

---

## Next genuine CS work (not P1)

1. **P2 OTA sync** — already built (`CsOtaBooking`, `sync_ota_bookings`, 563 rows). Needs prod migrate + Celery beat schedule. See master-state deploy queue.
2. **P3a OTA magic-link trip view** — [[ota-magic-link-trip-view]].
3. **P3b OTA request submit** — reuses this P1 spine. [[ota-request-submit]].

---

## Related

[[booking-command-centre-decision]] (parent) · [[tickets]] (model doc) · [[cs-api-contract]] (CS chat — separate) · [[ota-request-submit]] (P3b reuses this spine)
