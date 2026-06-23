---
name: ota-request-submit
description: P3b — OTA traveler submits change/cancel/pax requests (reuses P1 Ticket request spine). Request-based workflow; no self-execution. Staff relays to OTA. Awaiting review. Requires P1 prereq.
metadata:
  type: project
  status: awaiting-review
  date: 2026-06-23
  parent: ota-portal-overview
---

# P3b — OTA Request Submit (change/cancel/pax)

## Summary
OTA traveler (authed via P3a magic-link) submits a request (change date, change pax, cancel) that lands in the staff command-centre queue. Staff review → **relay to OTA** (manual; OTA owns execution) → notify traveler. **No customer self-execution** ([[booking-command-centre-decision]] universal request workflow).

## Context
OTA bookings are owned by 12Go/Klook — SmartEnPlus cannot mutate them directly. Any change is a request → staff → OTA relay. This phase wires OTA guests into the same request spine P1 builds for direct bookings.

## Prerequisite
**P1 direct-slice must ship first** — extends `tickets.Ticket` with `request_type`/`status`/`source`/`requested_value` + `HistoricalRecords` + transition endpoints (ports `cs/` `VALID_TRANSITIONS` + reopen abuse-guard). This phase reuses that spine with `source='ota'`.

## Approach
- Request create endpoint: reuse P1 spine. Sender = OTA-guest (derived server-side from magic-link token, never client-trusted — same rule as `Message.sender` in [[cs-api-contract]]). `source='ota'` + OTA booking FK (`CsOtaBooking` from P2).
- Transition endpoints: reuse P1 `VALID_TRANSITIONS`. Staff actions: accept/reject/relay-to-OTA/resolve.
- FE "Request change" button on the OTA trip portal (P3a page) → request form (request_type + requested_value).
- Notify: traveler gets a Tier-1 service email (SES) on status change. **Inbound comms only here** — proactive outbound is P3c (gated).

## Files
- **BE:** reuse P1 request endpoints (no new models); add OTA-guest sender resolution + `CsOtaBooking` FK wiring.
- **Admin:** command-centre queue already shows OTA bookings (P2); add request row + relay-to-OTA action.
- **FE:** request form + button on `pages/my-trip`.

## Risks / tradeoffs
- **No self-execution** = slower UX but correct (OTA owns the booking). Communicate "request submitted, we'll confirm" clearly.
- **Relay is manual** — staff copy/paste to OTA portal initially; automation deferred (P5).
- **Reuse vs fork** — extending the P1 spine keeps one taxonomy; risks a later vocab reshuffle if OTA requests diverge (P4 harden).

## Review focus
- Does OTA need request types P1's taxonomy doesn't cover (e.g. "vehicle type change")? Confirm before reusing blindly.
- Is manual relay acceptable for v1, or block on even minimal OTA-API integration? (Plan: manual first per YAGNI.)
- Sender-resolution from magic-link token — same pattern as guest chat token; confirm no new auth surface.

## Verification
- OTA guest submits request → lands in staff queue with OTA booking context.
- Staff transitions (accept/reject/relay/resolve) → traveler notified (Tier-1 email).
- Reopen abuse-guard (P1 `VALID_TRANSITIONS`) applies to OTA requests too.
- Guest cannot self-execute any state change.

## Related
[[ota-portal-overview]] · [[ota-magic-link-trip-view]] (auth) · [[ota-sync-supabase-mirror]] (booking context) · [[booking-command-centre-decision]] (P1 spine) · [[cs-api-contract]]
