---
name: ota-link-delivery-and-p3b-plan
description: Build plan to make the shipped P3a OTA trip view actually usable — G2 admin copy/send-link (keystone, ungated) + P3b OTA request-submit (prereqs cleared). Closes the "window but no door" gap found 2026-06-25.
metadata:
  type: project
  status: planned
  date: 2026-06-25
  parent: ota-portal-overview
---

# OTA Link Delivery + P3b Request Submit — Build Plan

## Why

P3a shipped a working OTA trip view (`/my-trip?token=` + `OtaTripView`) 2026-06-25. But the
big-view audit ([[ota-portal-overview]] gap table) found it's a **window with no door**:
- **G2:** no way for staff to give an OTA user the link (`make_ota_trip_token` = Django-shell only).
- **G3:** trip view is read-only — no request-change, so no purpose once inside.

This plan closes both with the smallest ungated build. Automated email (G1) stays deferred
behind the P3c contract gate; this plan makes the feature usable WITHOUT it.

## Already shipped (do not rebuild)
- `OtaTripView` GET `/api/cs/ota/trip/?token=` — `cs/views.py:390`
- `make_ota_trip_token` / `load_ota_trip_token` — `cs/tokens.py:34`
- `Ticket.guest_email` + nullable `created_by` (migration `0005`) — P3b prereq, DONE
- FE `/my-trip` page + `otaApi.js` slice

---

## Phase 1 — G2 admin "Copy Trip Link" (KEYSTONE, ungated)

**Goal:** staff opens an OTA booking in command-centre → one click → signed `/my-trip` URL on
clipboard → paste into existing 12Go/Klook chat. No email, no contract gate.

### Backend
- New endpoint `POST /api/cs/ota/trip-link/` (admin-only, `IsAdminOrIsStaff`):
  - body `{ source, booking_id }` → look up `CsOtaBooking` → mint `make_ota_trip_token(email, booking_id, source)` → return `{ url: f"{FRONTEND_URL}/my-trip?token=..." }`
  - 404 if booking missing or has no email (can't issue link without email key)
- `FRONTEND_URL` already in env (ISR uses it) — reuse, no new config.
- Register in `cs/urls.py`.

### Admin Dashboard
- Command-centre OTA booking row → "Copy Trip Link" button → calls endpoint → `navigator.clipboard.writeText(url)` → toast "Link copied".
- Reuse existing command-centre table + confirm-dialog pattern (`feat/command-centre-confirm-dialog`).

**Gate status:** UNGATED. Copy-link is staff pasting into a channel the OTA already owns —
not SmartEnPlus proactively emailing. Contract gate covers *automated outbound*, not this.

---

## Phase 2 — G3 / P3b OTA request submit

**Goal:** OTA guest on `/my-trip` submits change/cancel/pax request → lands in command-centre
queue → staff transitions → (later) notify. Reuses P1 Ticket spine. Per [[ota-request-submit]].

### Backend — extend `CustomerTicketViewSet.create()` (`tickets/views.py:199`)
- Add OTA branch: accept an OTA trip token instead of session auth.
  - Resolve `email/booking_id/source` from token server-side (never client-trusted).
  - Verify `CsOtaBooking` ownership (email match) — same rule as `OtaTripView`.
  - Create `Ticket` with `created_by=None`, `guest_email=<token email>`, `source='ota'`,
    `content_type=CsOtaBooking`, `object_id=booking.pk`.
- Keep existing direct-booking branch untouched (session path). Branch on token presence.
- Add `'ota'` to `Ticket.SOURCE_*` constants (currently only `SOURCE_DIRECT`).

### Backend — `CsOtaBooking` needs a GenericFK target
- `Ticket.content_type`/`object_id` already GenericFK — point at `CsOtaBooking`. No model change
  to CsOtaBooking; just allow it as a content_type. Verify `TicketSerializer.get_content_object`
  handles `CsOtaBooking` (currently only branches on `BookingItem` — `serializers.py:47`). Add branch.

### Frontend — `/my-trip` request form
- Reuse `RequestChangeModal.js` pattern (already built for direct). Extract the form body or wrap
  it with an OTA mutation hook in `otaApi.js` (`submitOtaRequest(token, {request_type, requested_value})`).
- POST via `otaApi` (token auth), NOT `bookingsApi` (session). Add "Request a change" button on `/my-trip`.
- Show submitted requests + status (reuse `ChangeRequestsSection` card UI, OTA data source).

### Admin
- Command-centre queue already shows tickets by `request_status` (P1). OTA requests appear with
  `source='ota'` + booking context. Add a "relay to OTA" note/action (manual; copy to OTA portal).

---

## Explicitly NOT in this plan (deferred)
- **G1 automated SES email** — gated by P3c contract gate. Phase 1 copy-link replaces it for now.
- **G4 boarding info** — no supplier feed; status-only stays.
- **G5 expired-link self-reissue** — covered once email send exists (P3c); interim copy is the manual path.
- **G6 multi-booking token** — owner decision needed first (email-scoped vs booking-scoped). Keep booking-scoped until decided.
- **G7 throttle** — add DRF throttle to `OtaTripView` + trip-link endpoint as a small P4 hardening, not blocking.
- **G8 consent capture** — P3c, gated.

## Owner decisions needed before/during
1. **G6 token scope** — one link per booking (current) vs one link per email (all bookings)? Affects token payload + endpoint.
2. **Contract gate verdict** — unblocks G1 automated email + G8 consent comms.
3. **G5 expired-link copy** — what should the user do? (current text references 12Go/Klook re-issue = fictional).

## Verification
- Phase 1: staff clicks "Copy Trip Link" → valid `/my-trip?token=` URL → opens to correct booking.
- Phase 1: non-staff cannot call `trip-link` endpoint (403).
- Phase 2: OTA guest submits request via `/my-trip` → Ticket created with `guest_email`, `source='ota'`,
  no `created_by`, CsOtaBooking FK → appears in command-centre queue.
- Phase 2: token-email mismatch → request rejected (no cross-booking write).
- Phase 2: direct-booking request flow (session) unchanged — regression check.

## Related
[[ota-portal-overview]] (parent + gap table + **OTA-user capability matrix**: can request change/cancel via P3b, CANNOT create direct booking or self-execute; "book direct" = Tier-3 marketing, double-gated) · [[ota-magic-link-trip-view]] (P3a, shipped) · [[ota-request-submit]] (P3b spec) · [[ota-consent-comms-pii-gate]] (P3c, gated G1/G8) · [[booking-command-centre-decision]] (P1 spine)
