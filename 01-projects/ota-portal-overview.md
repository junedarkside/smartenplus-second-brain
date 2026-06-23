---
name: ota-portal-overview
description: Overview + review spine for the OTA (12Go/Klook) data sync + OTA-traveler self-service portal — phases P2–P3 of the Booking Command Centre. Status: AWAITING TEAM REVIEW before implementation.
metadata:
  type: project
  status: awaiting-review
  date: 2026-06-23
  parent: booking-command-centre-decision
---

# OTA Portal — Phased Plan (awaiting review)

## Summary
Breaks the Supabase OTA-sync + OTA-traveler portal ([[booking-command-centre-decision]] P2–P3) into small, independently-reviewable build phases. **No implementation until a review team signs off each phase.** This note is the spine — read it first, then drill into the phase notes below.

## Context
Owner goal: ONE command centre controlling OTA (Supabase) + direct (Django) bookings; OTA travelers self-serve (view trip, request change/cancel) without a SmartEnPlus account. OTA = **Online Travel Agency** (12Go/Klook/Bookaway), not over-the-air. Supabase already holds 561 OTA bookings + traveler PII ([[supabase-ota-booking-store]]); it is a **disconnected island** until read-synced, and OTA travelers have **no account + are the OTA's customer** → need magic-link auth + consent-bounded comms.

## Verified code state (2026-06-23)
- ✅ Built: `cs/` app (`Conversation`/`Message`/`CSOtp`/`FeatureFlag`, 8 endpoints), `cs/tokens.py` signing primitive, `Order.source` (`orders/models.py:441`), `IsAdminOrIsStaff`, `tickets.Ticket`, `dialogue/` GenericFK, `boto3` (SES+SNS), `requests`, `pyotp`.
- ❌ Greenfield: `CsOtaBooking`, `sync_ota_bookings`, Supabase REST config, OTA trip endpoint, `is_guest`, OTA magic-link auth, `consent.records`.
- ⚠️ No `@supabase/supabase-js` anywhere — OTA sync = server-side `requests` → PostgREST (no SDK, no new dep).

## Phases (each = one reviewable note)
| Phase | Note | Gated? | Status |
|---|---|---|---|
| **P2** | [[ota-sync-supabase-mirror]] — read-only Supabase→Django mirror | No | awaiting-review |
| **P3a** | [[ota-magic-link-trip-view]] — magic-link auth + read-only trip portal | No | awaiting-review |
| **P3b** | [[ota-request-submit]] — request change/cancel (reuses P1 Ticket spine) | No* | awaiting-review |
| **P3c** | [[ota-consent-comms-pii-gate]] — consent.records + Tier-1 comms + PII gate | **Yes** | awaiting-review |

\* P3b needs the **P1 direct-slice** prereq (Ticket extension) to reuse the request spine.

## Prerequisites (before any phase builds)
1. **P1 direct-slice** ([[booking-command-centre-decision]]): pin `tickets/serializers.py:55` explicit fields (103 `__all__` leak guard) + extend `tickets.Ticket` (`request_type`/`status`/`source`/`requested_value`). Required for P3b spine reuse.
2. **Contract gate (owner/legal):** confirm 12Go/Klook supplier contracts allow operator→traveler service contact. Blocks **P3c outbound comms only** (Tier-1 SMS/email proactively to OTA travelers). P2 + P3a + P3b do NOT need it.
3. **P0 measurement:** direct-rebooking ROI before Tier-3 marketing (P3c).

## Sequencing (non-gated path can start after P1)
P1 → P2 (sync) → P3a (trip view) → P3b (requests) → ⛔ contract gate → P3c (comms + consent).

## Cross-cutting principles (all phases)
- **Supabase = read-only source.** Django reads; never writes back. Identity link lives in Django.
- **No new deps.** `requests` for PostgREST, `boto3` for SES+SNS, `django.core.signing` for magic-links (reuse `cs/tokens.py`).
- **Consent-bounded.** OTA travelers are the OTA's customers — service comms only by default; marketing gated ([[cs-consent-gdpr-model]]).
- **Explicit serializers.** No `__all__` ([[cs-api-contract]]). P1 pin is the hard precondition.

## Review focus (for the review team)
- Is 4-phase split correct, or should P2/P3a merge (sync + read-view are tightly coupled)?
- Is stateless magic-link (no Account) the right OTA-auth posture, or thin `is_guest` Account from the start?
- Is the contract-gate boundary drawn correctly (P2/P3a/P3b ungated, P3c gated)?
- Any missed reuse (existing endpoints/components) that shrinks scope?

## Open questions (owner/legal — batched)
1. Contract gate verdict (12Go/Klook operator→traveler service contact allowed?).
2. Consent wording + Privacy Policy URL + Thai PDPA review ([[cs-consent-gdpr-model]] Q1–Q9).
3. P0 rebooking threshold for Tier-3 unlock.
4. Sync cadence confirmation: manual batch first (this plan's default) vs Beat task?

## Related
[[booking-command-centre-decision]] (parent) · [[supabase-ota-booking-store]] · [[cs-api-contract]] · [[cs-consent-gdpr-model]] · [[cs-centralization-stack]] · [[ota-sync-supabase-mirror]] · [[ota-magic-link-trip-view]] · [[ota-request-submit]] · [[ota-consent-comms-pii-gate]]
