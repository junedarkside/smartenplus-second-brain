# Command-Centre Direct-Notify Redesign

## Summary
**Decision: HYBRID (Debater 3).** Extract one shared `NotifyDialog` reused by both call sites; mount it on the command-centre ticket-review dialog so direct bookings with an active CS ticket become notifiable inline. Backend already supports both endpoints; **no backend change required** — direct-ticket `content_object.id` (the BookingItem PK) is already serialized.

## Context
Admin "Notify customer" (send trip update) is split across two surfaces in `admin-dashboard`:
- **Command-centre** `/dashboard/command-centre` → `OtaBookingsTab` "Notify" button → `sendTripNotification` (`store/api/csApi.js:114`) → `POST /api/cs/ota/<pk>/notify/`. **OTA only.**
- **Direct booking detail** `/bookings/[slug]` → "Send Trip Update" → `sendBookingItemNotification` (`csApi.js:149`) → `POST /api/cs/bookings/<pk>/notify/`. **Direct only.**

Goal: let command-centre notify DIRECT bookings too. Shared `TripNotification` model + shared PATCH/DELETE already exist. Pure admin-dashboard architecture + UX question.

## Problem
Two near-byte-identical notify dialogs (~98 lines each) live in parallel:
- `pages/dashboard/command-centre/index.js:713-810` (OTA) + handlers `:459-507` + `NOTIFY_CATEGORIES :442-448`.
- `pages/bookings/[slug].js:421-518` (direct) + handlers `:121-147`.

Same categories, same handlers, same JSX, same Markdown-helper text. The API layer already accepts `booking_type: 'ota'|'direct'` on update/delete purely for cache-tag routing (`csApi.js:126-148`, comments at `:127`, `:139`) — the API was designed for a unified UI that never followed.

## Verified Facts (load-bearing, read in real code)
1. **Command-centre lists NO direct bookings.** `DirectRequestsTab` (`command-centre/index.js:81`) queries `useGetCustomerRequestsQuery` (`ordersApi.js:190` → `/admin-dashboard-tickets/tickets/`) = CS **tickets**, filtered `t.request_type` (`:146`). `OtaBookingsTab` (`:450`) is OTA-only via `useGetOtaBookingsQuery`. Notify button exists only in OTA tab (`:696-707`). So "direct notify from command-centre" can only attach to **direct tickets**, not a direct-bookings list.
2. **Direct-ticket `content_object.id` IS exposed** (the deciding factor). `TicketSerializer.get_content_object` (`tickets/serializers.py:48-50`) returns full `BookingItemSerializer(...).data` for direct bookings; `BookingItemSerializer.Meta.fields = '__all__'` (`:19-32`) → `id` included. `sendBookingItemNotification({ booking_pk: ticket.content_object.id })` works as-is. (OTA branch returns a trimmed dict `:51-58` — fine, OTA notify uses its own booking list's PK.) Direct tickets also expose `slug` and `order_id` (used at command-centre `:221`, `:310`, `:390`).
3. **`booking_type` cache routing confirmed** (`csApi.js:126-148`); `bookings/[slug].js:136,144` already passes `booking_type:'direct'`.

## The 3 Stances (compressed)
- **UNIFY (D1, 8/10):** Extract shared `NotifyDialog`, mount on command-centre direct rows. Correctly identified the duplication and API readiness. Left endpoint routing vague and flagged an unverified `content_object.id` blocker — **blocker now dissolved by Fact 2.**
- **ISOLATE (D2, 8/10):** Keep direct notify at `/bookings/[slug]`; command-centre deep-links out (`/bookings/<slug>?notify=1`). Correctly identified the **load-bearing finding** (Fact 1: no direct-booking row exists). Zero new queries — ticket `slug` already present. ~12 lines, 2 files. Cost: context-switch + OTA/direct parity gap.
- **HYBRID (D3, 9/10):** Extract ONE shared `NotifyDialog` for BOTH pages, internal endpoint router on `booking_type`. Quantified the duplication, cited the API-layer signal, declared both mutation hooks unconditionally (RTK rule), kept component <200 lines. Strongest framing; converges with D1 on extraction.

## Decision + Why
**Hybrid wins cleanly.** The deciding factor is Fact 2: because `content_object.id` is already on the direct ticket, the shared `NotifyDialog` mounts in `DirectRequestsTab` with **zero backend change** and zero new data source. D1 and D3 converged on extraction — this is REUSE FIRST applied to code that *already exists twice*, not speculative abstraction. Net repo delta negative (~−100 lines) → simpler total system, satisfies NO OVER-ENGINEERING.

**Where the dialog mounts (grafted from D2):** not a new tab/list — a "Notify Customer" utility action on the existing ticket-review `ActionDialog` (`command-centre/index.js:365-396`), as a sibling to the existing "View Order" direct-only action (`:387-395`). Gated on `source !== 'ota' && content_object.id`. This respects the tab's own pattern and the 200-line ceiling.

**D2 retained as fallback:** if the shared-component regression surface proves brittle, Isolate's `?notify=1` deep-link (needs only `slug`, already present) is the rollback path — keep it documented.

## Tradeoffs
- **Pro:** kills ~196 lines of verbatim duplication; one notify hub; API layer finally matches UI; OTA inline + direct inline reach parity; net negative LOC.
- **Con:** 5 props on the dialog (exceeds "3 params" letter — but that rule targets helper **functions**, not MUI dialog components, which legitimately take 4-8); coupled regression surface (a bug in `NotifyDialog` breaks both pages → smoke test both); two mutation hooks declared per render, one unused (negligible, lazy).
- **Coverage caveat (honest, from D2):** command-centre direct notify reaches only direct bookings that have an **active CS ticket with a `request_type`** (`command-centre/index.js:146`). Ticketless direct bookings remain unreachable from command-centre — equally true under all three stances unless a new direct-bookings tab is built. That is a **Phase 2** scope question, not Phase 1.

## Implementation Sketch (paths + deltas, no code)
1. **NEW** `components/cs/NotifyDialog.jsx` (~170 lines). Props: `open`, `onClose`, `bookingType` (`'ota'|'direct'`), `bookingPk`, `titleDetails`. Declares send/update/delete + the matching notifications-list query **unconditionally** (RTK rule); one router `booking_type === 'direct' ? sendDirect : sendOta`. Owns `NOTIFY_CATEGORIES` (single source — delete both copies). Internal funcs ≤30 lines. Wraps the existing `ActionDialog` shell.
2. **`pages/dashboard/command-centre/index.js`** (now 875 lines → ~750):
   - `OtaBookingsTab`: delete inline dialog `:713-810`, handlers `:475-507`, notify state `:459-465`, `NOTIFY_CATEGORIES :442-448` → `<NotifyDialog bookingType="ota" bookingPk={notifyTarget?.id} ... />` (~−135 lines).
   - `DirectRequestsTab`: add one `utilityActions` entry "Notify Customer" (gated `source !== 'ota' && dialogTicket?.content_object?.id`) + `<NotifyDialog bookingType="direct" bookingPk={dialogTicket?.content_object?.id} ... />` (~+15 lines).
3. **`pages/bookings/[slug].js`** (now 524 lines → ~390): delete inline dialog `:421-518`, handlers `:121-147`, notify state → `<NotifyDialog bookingType="direct" bookingPk={booking?.id} ... />` (~−140 lines).

## Risks
- **Coupled regression:** a single bug in `NotifyDialog` breaks both OTA and direct notify paths. Mitigation: smoke test BOTH pages after extraction (send / edit / delete / list-render); the `booking_type` router is the highest-risk line.
- **`notifyTarget`/`dialogTicket` lifecycle:** the dialog must clear local state on close exactly once — both current sites have subtle `onClose` resets that must move into the shared component.
- **Coverage gap misread as bug:** staff may expect to notify *any* direct booking from command-centre; only ticket-bearing ones are reachable (Phase 2: a direct-bookings tab).

## Open Questions for Owner
1. **Phase 2 scope:** is reaching ticketless direct bookings from command-centre wanted? If yes → new `DirectBookingsTab` (new query + column); if no → document the ticket-only reach as intended.
2. **Notify from a *closed* ticket:** should the "Notify Customer" utility action be hidden when `dialogReadOnly` (terminal status)? Currently proposed as always-available for direct — confirm with CS workflow.
3. **`NOTIFY_CATEGORIES` home:** inline in `NotifyDialog.jsx` (NO OVER-ENGINEERING, single consumer) vs `constants/csConstants.js` if a second consumer appears later. Recommend inline for now.

## Related
[[cs-centralization-audit-2026-06-29]] · [[admin-dashboard-cs-centralization-plan]] · [[command-centre-ticket-booking-flow]] · [[cs-manual-test-flows-b7-e-2026-06-30]]
