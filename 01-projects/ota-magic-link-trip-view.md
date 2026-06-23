---
name: ota-magic-link-trip-view
description: P3a — magic-link auth (reuse cs/tokens.py signing) + read-only trip portal for OTA travelers (no SmartEnPlus account). Stateless-on-email. Awaiting review.
metadata:
  type: project
  status: awaiting-review
  date: 2026-06-23
  parent: ota-portal-overview
---

# P3a — OTA Magic-Link + Read-Only Trip View

## Summary
An OTA traveler clicks a signed-token link and sees their trip (boarding info, status) — **without a SmartEnPlus account**. Stateless-on-email: token resolves to read-only trip view; no Account created. Escalation to guest `Account(is_guest=True)` deferred to P3b (request submit). Unfakeable proof — strictly better than the bare-email gate (loose-end CS-GUEST-EMAIL-GATE).

## Context
OTA travelers (12Go/Klook) are the OTA's customers with no SmartEnPlus account. They need to view their trip + (later) request changes. Magic-link avoids account friction + enumeration risk.

## Approach
### Magic link (reuse `cs/tokens.py` pattern)
- New salt `cs-ota-trip` via `django.core.signing.dumps({'email':..., 'exp':...})`. Reuse existing `make/load_guest_token` shape (`cs/tokens.py:1`). TTL 24h (match guest token).
- Entry: a Tier-1 service email (SES) carries the link → `pages/my-trip/?token=...`.
- Server validates token → loads `CsOtaBooking` rows for that email (P2 mirror).

### Auth posture (stateless-first)
- **Stateless-on-email first:** token = read-only trip view. Do NOT mass-create Accounts.
- Escalate to guest `Account(is_guest=True)` ONLY when the user submits a request (P3b reuses existing guest-token + `Conversation.guest_email` flow). Minimizes account sprawl.

### Trip info (tiered — [[booking-command-centre-decision]])
- **Controlled tier** (private/charter): GPS/car-reg/boarding/location — SmartEnPlus-controlled. **Data source unverified** (vault P5) → defer.
- **Join-in tier** (bus/ferry): boarding-info-only, supplier-fed.
- OTA volume = mostly **join-in ferries (Langkawi↔Koh Lipe)** → ship **boarding-info tier first**.

### OTA trip-read endpoint
- New `GET /api/cs/ota/trip/` (auth = signed token in `Authorization: Bearer <ota-token>`, NOT session). Returns tiered trip-info serializer. Explicit fields only ([[cs-api-contract]]).

## Files
- **BE new:** `cs/tokens.py` (ota-trip salt + make/load), `cs/views.py` (`OtaTripView`), `cs/serializers.py` (tiered trip serializer), `cs/urls.py` (route).
- **FE new:** `pages/my-trip/index.js` (token resolve + OTA trip view), trip-info component.

## Risks / tradeoffs
- **Magic-link TTL vs UX** — 24h link; re-issue on expiry (re-send). Token in URL = shareable; mitigate via email-scoped data only (no cross-customer leak).
- **Tiered data gaps** — join-in ferry boarding info depends on supplier feed that may not exist yet; portal could show partial data initially.
- **Stateless vs account** — deferring accounts simplifies P3a but P3b needs an escalation path; keep the bridge clean.

## Review focus
- Stateless-on-email vs thin `is_guest` Account from the start — which posture? (Plan recommends stateless-first.)
- Is email-scoped token data exposure acceptable, or should the token bind to a single `booking_id` (less data, more links)?
- Does the join-in boarding-info data source actually exist today, or is P3a blocked on a supplier feed? **Verify before build.**

## Verification
- Generate token → `/my-trip?token=` loads correct OTA booking(s) by email.
- Tampered/expired token → rejected (no data leak).
- PII hidden until valid token (closes CS-GUEST-EMAIL-GATE).
- Token bound to email only → no cross-customer bleed.

## Related
[[ota-portal-overview]] · [[ota-sync-supabase-mirror]] (data source) · [[cs-api-contract]] · [[cs/tokens.py]]
