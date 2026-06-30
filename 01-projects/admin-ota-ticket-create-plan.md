# Admin-Initiated OTA Ticket Creation — Implementation Plan

## Summary
Admin creates change/cancel tickets for OTA bookings (12Go/Klook) without guest action. Guest sees ticket on `/my-trip` portal automatically.

## Context
Emergency ops scenario: operator contacts guest by phone, needs to log cancellation/change immediately without waiting for guest to self-serve via magic link portal. Also covers no-email OTA bookings where guest portal is disabled.

## Problem
OTA Bookings tab in command-centre only has "Copy Link" + "Resend Email". No admin-initiated ticket creation. Forces guest action for every request — unworkable in emergency (weather cancel, same-day change).

## Decision
Build `AdminOtaTicketCreateView` — minimal delta (~27 BE lines, ~70 admin FE lines, ~5 FE lines). No migrations. `admin_initiated` field already exists on `Ticket` model (`tickets/models.py:92`). `AdminInitiatedBanner` already exists in `TicketStatusBanner.js:169`.

## Details

### BE — `smartenplus-backend`

**New view** `AdminOtaTicketCreateView` in `cs/views.py` (after `OtaChangeRequestView` ~line 605):
- `permission_classes = [IsAdminOrIsStaff]`
- URL: `POST /api/cs/ota/<int:pk>/ticket/`
- Accepts: `{ request_type }` (date_change / pax_change / cancellation / other)
- Looks up `CsOtaBooking` by `pk` via `get_object_or_404`
- Reuses exact Ticket construction from `OtaChangeRequestView:585-603`
- Sets `admin_initiated=True`, `created_by=request.user`, `source=Ticket.SOURCE_OTA`
- Calls `ticket.full_clean()` → 400 if open ticket exists (one-open-ticket guard fires correctly — no bypass)
- Add `from django.shortcuts import get_object_or_404` to imports

**New URL** in `cs/urls.py`:
```python
path('ota/<int:pk>/ticket/', AdminOtaTicketCreateView.as_view(), name='ota-admin-ticket-create'),
```

### Admin FE — `admin-dashboard`

**`store/api/csApi.js`** — new mutation:
```js
createAdminOtaTicket: builder.mutation({
  query: ({ booking_pk, request_type }) => ({
    url: `/api/cs/ota/${booking_pk}/ticket/`,
    method: 'POST',
    body: { request_type },
  }),
  invalidatesTags: ['OtaBooking'],
}),
```

**`pages/dashboard/command-centre/index.js`** — in `OtaBookingsTab`:
- State: `createTarget` (booking) + `createType` (request_type string)
- Handler `handleCreateTicket`: calls mutation, shows error on 400 (open ticket exists), clears state on 201
- New table column **"Create Request"** button — disabled when `!booking.email` (same gate as Copy Link at line 474)
- `ActionDialog` (already imported) with `<Select>` for request_type as `extraContent`
- Options: `date_change` / `pax_change` / `cancellation` / `other`

### Guest FE — `smartenplus-frontend`

**`components/bookings/TicketStatusBanner.js`** — 2 fixes:

1. **Line 12-13** — override `pending` label when `ticket.admin_initiated`:
   - `"Waiting for Review"` → `"Being Processed"` (guest didn't submit, admin did)

2. **`RequestedDetails` component** — gate: `if (ticket.admin_initiated) return null`
   - Hides "Your request:" section — guest made no request

`AdminInitiatedBanner` (line 169) already shows "Update from SmartEnPlus" orange banner. ✅

## Flow After Build

1. Admin → Command Centre → OTA Bookings tab → find booking → **"Create Request"** → pick type → Submit
2. Ticket: `pending`, `admin_initiated=True`, `source='ota'`
3. Guest opens `/my-trip` → orange "Update from SmartEnPlus" banner + "Being Processed" status pill
4. Guest form hidden (`showForm=false` — open ticket exists, `index.js:68`)
5. Admin: pending → in_review → awaiting_ota_update (waiting for 12Go/Klook)
6. **Emergency bypass:** admin toggles Emergency ON → resolves without OTA wait

## Tradeoffs
- One-open-ticket guard fires for admin too → correct, prevents duplicate open tickets
- No guest consent artifact → acceptable for admin-ops scenarios; `admin_initiated=True` is the audit trail
- Guest sees "Being Processed" not "Waiting for Review" — clearer intent

## Branch
`feat/admin-ota-ticket-create` off develop (all 3 repos)

| Repo | Files | ~Lines |
|------|-------|--------|
| BE | `cs/views.py`, `cs/urls.py` | 27 |
| admin | `store/api/csApi.js`, `command-centre/index.js` | 70 |
| FE | `TicketStatusBanner.js` | 5 |

## Related
- [[cs-centralization-audit-2026-06-29]] — `admin_initiated` field listed as dead weight; this activates it
- [[ota-flow-e2e-scan-2026-06-30]] — B7-5 emergency bypass (requires ticket to exist first)
- [[admin-dashboard-cs-centralization-plan]] — Phase 2-3 pending
