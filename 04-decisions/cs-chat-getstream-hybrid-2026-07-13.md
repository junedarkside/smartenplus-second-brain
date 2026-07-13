---
name: cs-chat-getstream-hybrid-2026-07-13
description: ADR — migrate CS chat hot path to GetStream Build (free tier) with hybrid scope. New conversations route through GetStream; old conversations stay on Django. Supabase retained for OTA mirror. Other team audits before implementation.
metadata:
  type: decision
  status: audit-conditional
  date: 2026-07-13
  parent: cs-architecture-decision
  supersedes: cs-chat-supabase-offload (for chat only; OTA mirror continues on Supabase)
  debate: getstream-migration-debate-2026-07-13
  plan: cs-chat-getstream-migration/implementation-plan-2026-07-13
---

# CS Chat → GetStream Hybrid (2026-07-13)

## Summary

Migrate CS chat hot path from current stack (Django + Supabase Realtime + custom JWT + Channels-dormant) to **GetStream Build free tier** with **hybrid scope** (new convs on GetStream; old convs stay on Django). Decision driven by user-reported pain (reconnect/gap-fill bug, token refresh silent fail, OTA auth-switch race, image-send broken, no prod notification, FE/AD history display broken) and in-house fix cost (3-6 sprints). Free tier = $0/mo, 1k MAU, 100 concurrent — sufficient for current + 12-18mo growth.

**Status:** CONDITIONAL (audit-complete 2026-07-13, session #242). See [[audit-2026-07-13]]. No code shipped. 4 blockers (B1–B4) + Python 3.9↔SDK≥3.10 conflict must clear before Phase 1.

## Decision

**Hybrid migration** with these explicit choices:

| Axis | Choice | Rationale |
|---|---|---|
| Vendor | **GetStream Build (free tier)** | $0/mo, sufficient for current volume, ships all features needed |
| Scope | **Hybrid** (new convs only) | Avoids backfill cost; old convs stay readable on Django |
| Supabase | **Retained for OTA mirror only** | `CsOtaBooking` sync still needs Supabase Realtime |
| Auth flow | **3 tiers unchanged** (Bearer / OTA / OTP-guest) | Stream JWT minted server-side, mirrors existing Supabase token endpoint |
| Sender-integrity | **Stream server-side auth + webhook trusts `event.user.role`** | Preserves [[chat-sender-session-bleed]] pattern |
| Image pipeline | **Django S3 presigned + Stream `custom_data` field** | Preserves PDPA posture (private ACL, no Stream CDN exposure) |
| Cutover | **FeatureFlag `cs_chat_transport`** | Per-conv `transport` field; reversible to `'legacy'` |
| Rollback | **Flip flag to `'legacy'`** | Zero data loss; Django polling fallback kept in code 6mo warm |

## Context

### Current pain (user-reported 2026-07-13)

1. Reconnect / gap-fill bug (L1 fix shipped `88e845de` but flaky)
2. Token refresh / 401-403 silent fail (Supabase JWT mint fails → realtime dies without recovery)
3. OTA guest / auth-switch race (wrong conv shown on identity change)
4. Image-send broken (just-shipped `53f30576`, deploy pending)
5. **No prod notification** when new message arrives
6. **FE + AD chat history display broken** (messages don't render properly)

In-house fix cost estimated at 3-6 sprints of careful rework.

### Debate verdict (2026-07-13)

[[getstream-migration-debate-2026-07-13]] — 4-agent structured debate (FE/BE/ops-cost/vendor-lockin). Vote 2 STAY / 2 CONDITIONAL / 0 MIGRATE. Original verdict was STAY TODAY, anchored on trigger-not-met + cheaper prepared Supabase-offload alternative.

**REVERSAL:** User decision overrides debate verdict on grounds of:
- Current malfunction = urgent operational pain (not theoretical trigger)
- In-house fix cost (3-6 sprints) ≈ migration cost (~6.5 sprints)
- Migration ships features (moderation, presence, typing, read-receipts) for free. ⚠️ **audit B3:** "staff inbox" already EXISTS (MUI, `pages/cs/index.js`) — migration swaps transport under it, doesn't build from scratch. Partially weakens this reversal driver.

## Architecture

```
┌─────────────────┐
│  NEW CONV       │──GetStream──AD/Staff real-time WS
│  (after cutover)│              ↓ webhook archive
└─────────────────┘              ↓
                          Django cs.Message (archive)
                          ↓
                          Supabase cs_messages (OTA sync mirror only)

┌─────────────────┐
│  OLD CONV       │──Django polling (useChatPolling.js)
│  (pre-cutover)  │──or Supabase Realtime fallback
└─────────────────┘
```

**Conv switch:** `Conversation.transport` field — `'legacy'` | `'stream'`. Widget dispatches per-conv.

**Source of truth:** Django `cs.Message` (always). Stream = hot path; archive mirror via webhook.

**Auth flow:** Existing 3 tiers preserved.
- New endpoint: `POST /api/cs/stream-token/` — mints GetStream JWT (HS256, 24h TTL) scoped to one conv (customer/guest) or unscoped (staff with `app_role='staff'`)
- Old endpoint `POST /api/cs/supabase-token/` retained for OTA-mirror auth (different purpose, NOT deprecated)

## Tier qualification (BLOCKING before Phase 1)

| Tier | Price | MAU | Concurrent | Eligibility |
|---|---|---|---|---|
| **Build** | **$0/mo** | **1,000/mo** | **100** | Free dev tier, hard-capped ("Limits Apply") — SmartEnPlus uses this |
| Maker | $0 + $100 credit | n/a (account type) | n/a | Separate free ACCOUNT type, <5 team + <$10k/mo rev — SmartEnPlus ineligible, **red herring** |
| Start 10K | **$499/mo** ($5,988/yr list) | 10,000 | 500 | Paid — only path past Build hard cap (no Build-tier paid overage) |
| Enterprise | Custom | 1M+ | Custom | SLA + 24/7 |

**BLOCKING CHECKS before Phase 1 (audit-2026-07-13 status):**
1. ✅ Sign up Build plan = $0, no CC — CONFIRMED (getstream.io/chat/pricing)
2. ✅ Maker NOT required — Build is the free tier; Maker is a red herring (SmartEnPlus ineligible anyway)
3. ⚠️ MAU counter definition — still verify in Phase 0
4. ✅ Message retention = indefinite ("as long as plan active") — CONFIRMED
5. ⚠️ Webhook on Build — public docs don't state tier; stays Phase-0 empirical POC gate
6. ✅ PDPA region: **Singapore selectable on Build at provisioning** (default us-east must NOT be left) — CONFIRMED not paid-gated. Remaining: sign DPA, lock SG region, draft Sec 29 SCC

**If any check fails → STOP, escalate.**

## Implementation phases

See [[cs-chat-getstream-migration/implementation-plan-2026-07-13]] for full detail.

- **Phase 0** (1 sprint): Spike + tier qualification + POC
- **Phase 1** (1 sprint): Backend token + webhook
- **Phase 2** (2 sprints): Frontend Stream hook
- **Phase 3** (1 sprint): Admin staff hook
- **Phase 4** (1 sprint): Image pipeline parity
- **Phase 5** (0.5 sprint): Cutover flag + monitoring
- **Phase 6** (4-6 weeks): Shadow parallel-run + cutover

**Total: ~6.5 sprints + 4-6 weeks shadow** ≈ 3 months calendar

## Cost

| Item | Cost |
|---|---|
| GetStream Build | $0/mo (hard-capped: 1k MAU / 100 concurrent — **rate-limits/errors on exceed, NOT paid overage**) |
| Paid overage ($0.09/user, $0.99/concurrent) | Applies only AFTER upgrading to Start ($499/mo) — NOT on Build |
| Engineering | 6.5 sprints (audit: likely understated — AD Phase 3 + FE transport-field work) |
| Vendor count after | 2 (Supabase + GetStream) |

## Risk

| Risk | Mitigation |
|---|---|
| Build tier MAU cap (1k) hit | Overage rates known; CloudWatch alarm; quarterly tier review |
| Webhook drops | Idempotency on `stream_id`; nightly reconcile task |
| PDPA data region = US/EU (not APAC) | SOFT-BLOCK (audit): Singapore selectable on Build; sign DPA + lock SG + Sec 29 SCC before Phase 1 |
| Sender-spoof | Stream server-side auth + role-based perms; webhook trusts `event.user.role` only |
| Free tier auto-bump | NO Stripe on signup; quarterly tier review |
| Django schema divergence | `Message.stream_id` canonical join; `custom_data` JSON field |
| React 18 compat | Verify in Phase 0 spike |
| Tailwind styling override | Custom `<MessageInput>` + custom message bubble |

## What would change this verdict

- Leadership commits to full vendor consolidation (drop Supabase too) → out of scope here, separate project
- Build tier gets discontinued by GetStream → re-evaluate paid tier or alternative (Ably, Pusher, Apache Kafka)
- PDPA cross-border consent fails for any region → BLOCKED, must resolve before any code
- In-house fix budget approved (3-6 sprints) + dedicated engineer → STAY verdict may return

## Related

- [[getstream-migration-debate-2026-07-13]] — parent debate verdict (now partially overridden by this ADR)
- [[cs-architecture-decision]] — grandparent ADR; transport decision lineage
- [[cs-chat-supabase-offload]] — superseded for chat only (OTA mirror continues on Supabase)
- [[cs-chat-getstream-migration/README]] — project overview
- [[cs-chat-getstream-migration/implementation-plan-2026-07-13]] — audit-ready plan
- [[chat-image-send-server-convergence]] — image pipeline this plan replaces
- [[chat-sender-session-bleed]] — sender-integrity pattern preserved
- [[cs-realtime-be-traffic-design-verdict-2026-07-08]] — BE traffic design constraint (binding until cutover)
- [[cs-guest-storm-investigation]] — scaling-trigger evidence (touched by this migration)
- [[prod-capacity-celery-audit]] — EC2 capacity constraints (resolved by this migration)

## Critical files

### Backend (`smartenplus-backend`)
- `cs/views.py:1334-1406` — `SupabaseTokenView` pattern (mirror for `StreamTokenView`)
- `cs/supabase_jwt.py` — `mint_supabase_jwt()` pattern (mirror for `mint_stream_jwt`)
- `cs/models.py` — `Conversation`, `Message` schemas
- `cs/tasks.py` — `sync_chat_messages` Celery pattern
- `cs/urls.py` — route registration
- `cs/serializers.py` — conversation list/detail serializer

### Frontend (`smartenplus-frontend`)
- `components/chat/ChatWidget.js` — dispatcher (branch on `conv.transport`)
- `hooks/useChatRealtime.js` — current realtime hook (replaced by `useGetStreamChat`)
- `hooks/useChatPolling.js` — fallback path for old convs (kept)
- `helpers/supabaseClient.js` — current client pattern (mirror for Stream)

### Admin (`admin-dashboard`)
- `hooks/useStaffChatRealtime.js` — staff realtime hook (replaced)
- `hooks/useStaffInboxRealtime.js` — inbox realtime (swap Supabase source → Stream)
- `store/api/csApi.js` — add `getStreamToken` mutation

## Status timeline

- **2026-07-13:** ADR drafted, plan written, audit-pending
- **2026-07-13 (session #242):** 6-agent audit COMPLETE — **VERDICT: CONDITIONAL** (see [[audit-2026-07-13]]). 4 blockers (B1 FeatureFlag cutover, B2 AD system-msg path, B3 staff-inbox value-prop, B4 pricing-table) + Python 3.9↔SDK≥3.10 conflict. Sign-off gate met conditionally (2 eng + ops + legal/PDPA). Clear blockers + Phase-0 POC → Phase 1.
- **TBD:** Phase 0 spike start (after blockers cleared)
- **TBD:** Phase 6 cutover (if Phase 0-5 succeed)