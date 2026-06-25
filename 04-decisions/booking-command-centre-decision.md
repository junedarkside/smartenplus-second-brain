---
name: booking-command-centre-decision
description: Owner-confirmed rescope of CS Centralization → Unified Booking Command Centre. One command centre controls OTA(12Go/Klook)+direct bookings; customer self-service (view, request change/cancel, live trip info); chat=sub-channel. 4-advocate debate verdict = direct-only vertical slice first. Phased roadmap P0-P5 + 3-tier consent model. New authoritative build direction.
metadata:
  type: decision
  status: accepted
  date: 2026-06-23
  parent: smarten-customer-os-thesis
---

# Booking Command Centre — Decision (CS Centralization rescoped)

> **Rescope 2026-06-23 (owner-confirmed).** The vault's "CS Centralization" cluster framed the goal narrowly (CS chat widget + OTA identity seed + conversion pilot). The owner's ACTUAL goal is bigger — a **unified booking-operations command centre + customer self-service portal**. This note is the new authoritative build direction. CS-cluster docs remain accurate for chat-transport + OTA-store facts (see Relationship below).

## Summary

ONE command centre controlling BOTH external bookings (OTA: 12Go + Klook, data in Supabase) AND internal/direct bookings (Django Order/BookingItem). All customers (direct + OTA) self-serve: view booking, see live/updated trip info (car reg, location, boarding, time, weather), REQUEST changes (date, pax) or cancellation. Chat = one support sub-channel. Build order set by a 4-advocate debate: **direct-only vertical slice first**; OTA + magic-link layer on after.

## Context

Owner found the CS-Centralization feature "unclear for my goals." Q&A clarified the goal is a command centre, not a chat widget. Locked constraints:
- **Tiered ops model:** private/charter = SmartEnPlus-controlled (trackable, GPS feasible); join-in (bus/ferry) = supplier-operated (boarding-info-only, supplier-fed). OTA bookings mostly join-in ferries (Langkawi↔Koh Lipe).
- **Request-based workflow (universal):** no customer self-executes. Customer → request → staff review → execute (internal for controlled / relay-to-OTA for external) → notify → HISTORY/audit. Extends `tickets.Ticket`.
- **OTA access:** magic link → signed-token auth → auto-provisioned guest Account (reuses `cs/tokens.py` / `django.core.signing`).
- **Current state:** CS chat BUILT (`fix/cs-chat-perf`, deploy pending); OTA sync ZERO; direct "My Trip" view partial (`pages/orders`, `pages/bookings`).

## Decision — best first slice (4-advocate debate)

Debated 4 options (staff-centre / customer-portal / request-spine / OTA-sync) via parallel read-only advocates, judge-synthesized. **Verdict: direct-only vertical slice first** = staff command centre (unified request queue + execute + history) FOR DIRECT bookings + direct-customer "request change" button.

**Why:** zero external deps (no OTA sync, no magic-link, no legal exposure); ~80% of staff UI already exists (admin `UpdateTrip`/`UpdatePassenger`/`CancelBooking` + CS inbox + tickets embedded in `ordersApi`); solves stated staff pain (scattered email/chat/phone); creates the inbox customer requests land in; validates the request taxonomy on real ops BEFORE hardening (answers spine-YAGNI); proves the full loop on the safe slice.

**Rejected first-slices:** customer-portal-first (needs OTA sync + the legal-riskiest proactive OTA email, inverts thesis P1a→P2 sequencing); request-spine-first (backend-only, no user validates the state-machine, a 2-field stub serves the first iteration); OTA-sync-first (root of OTA dependency DAG but no visible value + YAGNI until a surface demands it).

## Phased roadmap

- **P0** — deploy built CS chat (USER action, prod); pin `TicketSerializer` explicit fields (103 `__all__` leak guard, hard precondition).
- **P1** ✅ **SHIPPED #164 (2026-06-24)** — direct vertical slice: `tickets.Ticket` extended (`request_type`/`request_status`/`source`/`requested_value`, migration `0004`); `CustomerTicketViewSet` + `RequestStatusViewSet` (`VALID_REQUEST_TRANSITIONS`, terminal auto-close); admin command-centre queue; FE "Request Change" modal + status cards wired on booking detail. **Direct only.** Status + file:line evidence: [[p1-direct-slice-impl-plan]]. Deferred (NOT P1): SES notify → P4; reopen guard → P4; nullable GenericFK → P3 (account-level tickets).
- **P2** — OTA sync: `cs.CsOtaBooking` mirror + `sync_ota_bookings` task (`requests`+PostgREST, manual batch first per S5, Beat+`-Q sync` only if load demands); `SUPABASE_ANON_KEY` env; staff OTA view drops into same queue; OTA↔Account email-merge (probabilistic).
- **P3** — customer portal (direct→OTA): magic-link (`cs/tokens.py` reuse); auto-provision guest Account; My Trip for OTA guests (tiered trip info); request submit; SERVICE email always (Tier 1); day-before trip-reminder SMS via AWS SNS (`boto3`, zero new dep); opt-in capture for WhatsApp/Line (Tier 2). **GATE:** confirm 12Go/Klook contracts allow operator→traveler service contact.
- **P4** — harden request spine from validated P1-P3 ops (`RequestEvent` trail, full transition dict, 6 endpoints); bind `cs.Conversation`→request (chat = sub-channel); notify on resolve.
- **P5** — tiered live-trip info (controlled-tier GPS/car/boarding — **verify data source first**, largest unknown); WhatsApp/Line channels (BSP provider, templates, 24h window); execution/relay automation; Smart CS quick-replies + KB.

## Consent model (3 tiers)

OTA travelers are 12Go/Klook's customers, contacted by SmartEnPlus as the **operator running their trip.**

| Tier | What | Basis | Opt-in |
|---|---|---|---|
| **1 Service** | booking confirm, boarding, how-to-travel, trip changes, **day-before reminder (SMS/email)**, request responses | contract performance + legitimate interest (GDPR/PDPA) | **No** — always |
| **2 Enhanced channel** | faster updates + ongoing support via WhatsApp/Line | consent | **Yes** |
| **3 Marketing** | rebooking offers, "book direct" | separate consent | **Yes** (gated on P0 rebooking measurement) |

**Recalibration:** service comms are defensible + necessary (NOT the high risk prior CS docs framed). Marketing/retention = the real poaching risk, kept separate + gated. **Hard gate:** confirm 12Go/Klook supplier contracts allow operator→traveler service contact — contract law, not privacy law, is the real constraint.

## Tradeoffs

- Direct-first = safe + validated, but leaves OTA (majority volume) manual longer.
- Request taxonomy built minimal (YAGNI) → harden in P4; risks a later vocab reshuffle.
- OTA email-merge probabilistic (20-40% miss); no deterministic link (`smarten_order_id` dropped).
- Live-trip info (P5) data source unverified — largest feasibility unknown.

## Consequences

- Supersedes the narrow CS-centralization build order; CS-cluster docs stay valid for transport + OTA-store facts.
- `tickets.Ticket` extension = the request-spine anchor (extend, not a new model).
- Pin `TicketSerializer` + audit `BookingItem.source` `__all__` leak BEFORE any field add (3-repo contract).
- P3 OTA outbound blocked on (a) contract check, (b) Phase 2 sync. Tier-3 marketing blocked on P0 measurement.

## Relationship to CS cluster

CS-cluster notes remain accurate for: chat transport (both-poll-Django, Supabase OUT — [[cs-architecture-decision]]), OTA store facts ([[supabase-ota-booking-store]]), API contract ([[cs-api-contract]]), gap-debate build reference ([[cs-gap-debate-verdicts]]), design ([[cs-centralization-design-concept]]). This note RESCOPES the goal + build order above them. Read [[smarten-customer-os-thesis]] with its rescope banner.

## Related

[[smarten-customer-os-thesis]] (parent) · [[cs-architecture-decision]] · [[cs-api-contract]] · [[supabase-ota-booking-store]] · [[cs-gap-debate-verdicts]] · [[cs-centralization-design-concept]] · [[cs-consent-gdpr-model]] · [[prod-capacity-celery-audit]] · [[cs-guest-storm-investigation]]

Approved plan (session-local): `.claude/plans/check-vault-for-cs-clever-bonbon.md`.
P1 impl plan: [[p1-direct-slice-impl-plan]] (created 2026-06-24, session #165).
