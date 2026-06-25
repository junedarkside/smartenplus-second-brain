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
| **P2** | [[ota-sync-supabase-mirror]] — read-only Supabase→Django mirror | No | ✅ SHIPPED (deploy pending) |
| **P3a** | [[ota-magic-link-trip-view]] — magic-link auth + read-only trip portal | No | ✅ SHIPPED 2026-06-25 (status-only, no boarding tier) |
| **P3b** | [[ota-request-submit]] — request change/cancel (reuses P1 Ticket spine) | No* | **prereqs cleared — NEXT BUILD** ([[ota-link-delivery-and-p3b-plan]]) |
| **P3c** | [[ota-consent-comms-pii-gate]] — consent.records + Tier-1 comms + PII gate | **Yes** | awaiting-review (GATED) |

\* P3b needs the **P1 direct-slice** prereq (Ticket extension) to reuse the request spine.
P1 SHIPPED + this session shipped the OTA-guest seams (`Ticket.guest_email` + nullable `created_by`, migration `0005`) → P3b unblocked.

## ⚠️ Gap findings (2026-06-25, post-P3a-ship — big-view OTA-user + BD audit)

P3a built a working **window** but no **door**. Full gap analysis → [[ota-link-delivery-and-p3b-plan]]. Top blockers:

| # | Gap | Severity | Designed? | Built? |
|---|-----|----------|-----------|--------|
| **G1** | No link DELIVERY — nothing generates/sends magic link to OTA user. `make_ota_trip_token` callable only from Django shell. | BLOCKER (feature unusable) | Yes (P3a SES email) | ❌ send gated by P3c contract gate |
| **G2** | No admin "Send/Copy Trip Link" button — staff cannot operate feature at all | BLOCKER (staff can't operate) | **designed NOWHERE** | ✅ SHIPPED 2026-06-25 — admin-dashboard OTA Bookings tab + Copy Link button (`feat/command-centre-ota-copy-link`); BE `POST /api/cs/ota/trip-link/` + `GET /api/cs/ota/bookings/` (`feat/ota-trip-link-api`) |
| G3 | No OTA request-change (P3b) — trip view is read-only dead end | HIGH | Yes ([[ota-request-submit]]) | ❌ prereqs now cleared |
| G4 | Boarding info absent (pier/meeting-point/time) — core ferry value | HIGH | Yes (join-in tier) | ❌ no supplier feed in `CsOtaBooking` |
| G5 | Expired-link recovery copy is fictional (tells user to ask 12Go/Klook, who don't know the link) | MED | No | ❌ |
| G6 | Token = single booking only; 2 OTA bookings = 2 links. Email-scoped vs booking-scoped left OPEN in design, chosen silently | MED | left open | ⚠️ accidental, needs owner call |
| G7 | No rate-limit / throttle on `OtaTripView` (enumeration surface) | MED | Yes (PII gate) | ⚠️ partial (token+email-match only) |

**Keystone:** G2 admin copy-link is the cheapest unlock — ungated (copy-link needs no contract gate), lets staff paste links into existing OTA chats TODAY. See plan.

## Prerequisites (before any phase builds)
1. **P1 direct-slice** ([[booking-command-centre-decision]]): pin `tickets/serializers.py:55` explicit fields (103 `__all__` leak guard) + extend `tickets.Ticket` (`request_type`/`status`/`source`/`requested_value`). Required for P3b spine reuse.
2. **Contract gate (owner/legal):** confirm 12Go/Klook supplier contracts allow operator→traveler service contact. Blocks **P3c outbound comms only** (Tier-1 SMS/email proactively to OTA travelers). P2 + P3a + P3b do NOT need it.
3. **P0 measurement:** direct-rebooking ROI before Tier-3 marketing (P3c).

## Sequencing (non-gated path can start after P1)
P1 → P2 (sync) → P3a (trip view) → P3b (requests) → ⛔ contract gate → P3c (comms + consent).

## OTA-user capability matrix — what an OTA traveler CAN / CANNOT do

> **Hard boundary (recurring confusion point):** an OTA user does NOT create direct bookings,
> and does NOT self-execute any change. OTA bookings are owned by 12Go/Klook — SmartEnPlus
> **cannot mutate them** ([[booking-command-centre-decision]], [[ota-request-submit]]). Every change
> is a **request → staff → relay to OTA**. "Book direct" is NOT a booking feature — it is
> **Tier-3 marketing**, double-gated.

### Can / Cannot
| OTA user action | Allowed? | Mechanism | Phase / status |
|---|---|---|---|
| View own trip (status, route, date, passengers) | ✅ | magic-link `/my-trip?token=` | P3a — SHIPPED |
| Request **date change** | ✅ (later) | `Ticket source='ota'` → staff relay to OTA | P3b — planned |
| Request **passenger change** | ✅ (later) | same | P3b — planned |
| Request **cancellation** | ✅ (later) | same | P3b — planned |
| Request **other** (free-text) | ✅ (later) | same | P3b — planned |
| See own request status | ✅ (later) | OTA request cards on `/my-trip` | P3b — planned |
| See boarding info (pier/meeting-point/time) | ⚠️ | needs supplier feed — absent in `CsOtaBooking` | blocked (G4) |
| **Create a NEW direct booking from trip view** | ❌ | **not a feature — never designed** | — |
| **Self-execute** any change (change date themselves) | ❌ | violates universal request workflow | — by design |
| Receive Tier-1 service comms (reminders, confirmations) | ⚠️ | SES email / SNS SMS | P3c — GATED (contract) |
| Opt-in to WhatsApp/Line (Tier-2) | ⚠️ | consent capture | P3c/P5 — gated |
| Get "book direct" marketing (Tier-3) | ⚠️ | rebooking offer | **double-gated**: P0 rebooking ROI + contract gate |
| Upgrade to full SmartEnPlus account | ⚠️ | `is_guest`→full | deferred — stateless-on-email for now |

### Why "book direct" is gated, not a button
- It is the **real poaching risk** vs the OTA — kept separate from defensible service comms ([[cs-consent-gdpr-model]]).
- Unlocked only after **P0 rebooking measurement** proves ROI ([[cs-p0-measurement-protocol.md]]) **and** the contract gate clears.
- When live, the user does NOT "convert" their OTA booking — they enter the normal SmartEnPlus
  booking flow as a fresh direct customer. No mutation of the OTA booking ever happens.

### Request taxonomy (shared with direct bookings)
`tickets.Ticket.REQUEST_TYPE_CHOICES`: `date_change` · `pax_change` · `cancellation` · `other`.
OTA requests reuse this exact set ([[ota-request-submit]]) — `source='ota'` distinguishes channel.
No OTA-specific type today; add only if OTA needs one direct lacks (e.g. "vehicle type change" — confirm before adding).

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
