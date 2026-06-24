# Command Centre — Ticket Reason & Booking-Update Flow

## Summary

The admin-dashboard `/dashboard/command-centre` queue originally hid the customer's requested change (now surfaced in the Review dialog as of 2026-06-24) and still does NOT apply that change on resolve. Two disconnected ticket-update systems exist; only the legacy `/tickets/[id]` page actually mutates bookings.

## Context

Investigated two operational questions: (1) how does staff see the *reason* of each request on command-centre, (2) when staff wants to update a booking, what's the flow and how does the backend handle it. Findings span admin-dashboard frontend + smartenplus-backend (`tickets`, `bookings`, `orders` apps). Verified by reading source, not inferred.

## Problem

Customer files a change request → ticket created → staff opens command-centre → marks "Resolve" → **booking stays unchanged.** The queue tracks `request_status` only; it is not wired to the booking-mutation logic that lives on a separate page (`/tickets/[id]`). Staff can now *see* the requested change in the dialog (2026-06-24 fix) but still must apply it manually elsewhere.

---

## Details

### Q1 — Reason visibility: HIDDEN on command-centre

- The reason lives in `Ticket.description` (TextField) — `tickets/models.py:37`. Structured request payload (e.g. new date) lives in `requested_value` (JSONField).
- API `/admin-dashboard-tickets/tickets/` **does return** `description` + `requested_value` — `tickets/serializers.py:55-61`.
- **Correction (2026-06-24):** `description` and `requested_value` are NOT independent. Request-typed tickets are created only at `tickets/views.py:194-219`, where `description = str(requested_value)` (line 210). So `description` is just the stringified JSON dict (`"{'new_date': '2026-07-01'}"`) — redundant noise, not a separate freeform reason. There is no human-written "message" field for command-centre tickets. The real signal = `requested_value` (structured JSON) + `request_type`.
- **RESOLVED (2026-06-24):** quick win shipped — command-centre Review `ActionDialog` now flattens `requested_value` into `{label, value}` rows (`requestedValueRows()` helper, `pages/dashboard/command-centre/index.js`). `description` deliberately NOT shown. Commit `4dee15c` on `feat/command-centre-confirm-dialog`.
- Note: the legacy page `/tickets/[id]` still shows/edits the raw `description` field.

### Q2 — Booking update: TWO DISCONNECTED SYSTEMS

**System A — legacy `/tickets/[id]` (functional; mutates real booking)**
- UI: `UpdateTrip`, `UpdatePassenger`, `CancelBooking` components.
- Endpoint: `PATCH /admin-dashboard-tickets/tickets/<ticket_number>/`
- Backend: `TicketViewSet.partial_update` — `tickets/views.py:52-115`. Calls `update_booking_item()` → writes `traveling_date` + `booking_status` to BookingItem; `editPassenger` toggles `BookingPassengerDetail.confirm`.
- **Only path that changes travel date / passengers.**

**System B — new `/dashboard/command-centre` (status flag only)**
- UI: Review → ActionDialog → pick next `request_status`.
- Endpoint: `PATCH /admin-dashboard-tickets/request-status/<ticket_number>/`
- Backend: `RequestStatusViewSet.partial_update` — `tickets/views.py:~231-249`. Sets `request_status` only. **Zero booking side effects.** No signal/hook bridges resolve → booking change (`tickets/signals.py` does not exist).

**Direct booking/order mutations (no ticket)**
- `PATCH /admin-dashboard/bookings-item-update/<id>/` — exposes only `confirm` + `booking_status` (`bookings/serializers.py:280-283`). Cannot change date/passengers.
- Order page `/orders/[slug]` — cancel booking + record refund via direct axios (`components/utils/callApis.js`).
- `PATCH /admin-dashboard-orders/order-detail/` — order status refund/cancel.

### Capability matrix

| Field / action | System A ticket | bookings-item-update | order page |
|---|---|---|---|
| Travel date | ✅ | ❌ | ❌ |
| Passenger info | ✅ | ❌ | ❌ |
| Booking status | ✅ | ✅ (confirm + status) | ❌ |
| Cancel + refund | via status | — | ✅ |
| Order status (refund/cancel) | ❌ | ❌ | ✅ |
| Command-centre resolve applies any of these | ❌ — status flag only |||

### Auth

- Ticket + `bookings-item-update` endpoints: `IsAdminOrIsStaff`.
- `/admin-dashboard-orders/order-detail/`: **no permission class — public.** Security debt.

---

## Decision / Gap

The command-centre queue (System B) was added as a request-triage view but never connected to the booking-mutation path (System A). Resolving a request is cosmetic at the data level — the actual change still requires a separate manual edit on `/tickets/[id]`. Staff also can't see the request reason without leaving command-centre.

## Recommendations (not yet implemented)

1. ~~**Quick win** — show `description` + `requested_value` in dialog.~~ **DONE 2026-06-24** — shipped `requested_value` only (flattened to rows); `description` excluded as redundant (`str(requested_value)`). Original "description + requested_value" wording was wrong; scrutiny caught it. Commit `4dee15c`.
2. **Real fix** — wire command-centre resolve to apply the requested booking change (bridge B→A logic), OR link each row to `/tickets/[id]` for the functional edit.
3. **Security** — add `IsAdminOrIsStaff` to `/admin-dashboard-orders/order-detail/`.

## Tradeoffs

- Bridging B→A risks double-edit if staff also uses the legacy page; need single source of truth for "applied" state. Linking rows to `/tickets/[id]` is lower-risk but keeps two pages.

## Related

- [[admin-dashboard-contracts]]
- [[admin-dashboard-component-patterns]]
