---
name: getstream-migration-debate-2026-07-13
description: Debate verdict — should SmartEnPlus CS chat migrate to GetStream (React + Python SDKs) vs current Django + Supabase Realtime stack. 4-agent structured debate (FE / BE / ops-cost / vendor-lockin). Vote 2 STAY / 2 CONDITIONAL / 0 MIGRATE. Recommendation = STAY TODAY with GetStream kept as conditional candidate if scaling trigger or staff-inbox build commits.
metadata:
  type: decision
  status: draft
  date: 2026-07-13
  parent: cs-architecture-decision
  debate_date: 2026-07-13
  agents: 4
  verdict: STAY
---

# CS Chat → GetStream Migration Debate (2026-07-13)

## Summary

4-agent structured debate on migrating CS chat from current stack (Django + Supabase Realtime + 256MB EC2) to **GetStream Chat SDK** (React + Python). Verdict: **STAY TODAY**. Both Supabase-Realtime-offload path ([[cs-chat-supabase-offload]]) and GetStream path achieve the same architectural win (offload WS from EC2); GetStream adds ~$4.8k/yr OPEX for features the team has not committed to building (staff inbox, moderation, presence, typing). Activation trigger unchanged: >~30 req/s widget polling OR staff-inbox UI commit.

## Context

- Chat shipped 2026-07-03 ([[cs-centralization-stack]]); image-send shipped 2026-07-13 (deploy pending)
- Volume = tens of widgets today; flip trigger from [[cs-architecture-decision]] NOT met
- Supabase free tier (200 concurrent Realtime conns, 2M msg/mo) sufficient for current + projected growth
- EC2 = 256MB / 1 vCPU / 2-slot Gunicorn / 1-slot Celery — capacity-constrained ([[prod-capacity-celery-audit]])
- PDPA: 9 open legal gates from [[cs-consent-gdpr-model]] block ANY third-party PII vendor (GetStream or Supabase offload)

## Debate verdicts

### 1. frontend-architect — **CONDITIONAL** (high confidence)

**Pros:** native typing/read-receipts/presence replaces `useChatRealtime` + `useChatPolling` hooks + L1 gap-fill; out-of-box image CDN removes Django WebP pipeline + S3 presign + Supabase-mirror dance; 3-tier auth collapse kills ~200 lines of ChatWidget reducer branchy logic.

**Cons:** "No SaaS budget" constraint (vault) still binding; MAU spike during incident = surprise tier jump; backend stays source-of-truth for users/bookings → Django↔Stream sync required (the problem BE-minted Supabase JWT solved for free); Stream component theming fights Tailwind.

**Effort:** 3-4 sprints (15-20 dev-days). **Cost:** $0-24k/yr depending on MAU tier.

**Must-have-for-migration:** budget approval, Django mirror via webhook, theming strategy (custom wrappers vs headless hooks).

### 2. backend-architect — **STAY** (medium confidence)

**Pros:** managed realtime + out-of-box features kills sync_chat_messages / insert_cs_message / cursor bookkeeping + R3 PII-leak risk (RLS-on-anon-key); server-side token mint near drop-in for `mint_supabase_jwt`; WS terminate off-EC2 same as Supabase-offload ADR.

**Cons:** trigger NOT met; cheaper Supabase-Realtime path pre-answers R1/R2/R3 for ~$0 incremental; new paid vendor (~$499/mo floor); PDPA data-residency in 3rd-party US SaaS = re-open 9 legal gates; sender-integrity (`_resolve_message_sender`) must re-enforce via GetStream server-side roles.

**Effort:** 15-25 dev-days. **Cost:** +$6k/yr.

**Must-have-to-stay:** keep [[cs-chat-supabase-offload]] as the prepared cheaper next step.

### 3. ops-cost — **STAY** (medium confidence)

**Pros:** managed SDK removes Supabase-Realtime config + sync Celery + Postgres mirror + HS256 JWT + RLS policy review (R3 owner disappears); 99.999% SLA kills single-worker fragility; terminates WS off EC2 = guest-storm ceiling eliminated.

**Cons:** Maker free-tier likely fails (>$10k/mo revenue + >5 person team); Start tier $399/mo = ~$4.8k/yr for "tens of widgets" at $0 today; MAU pricing unbounded on guest/marketing-blast side; PDPA/erasure obligations span 3rd vendor.

**Effort:** 1.5-2 sprints. **Cost:** +$4.5-4.8k/yr.

**Must-have-to-stay:** ship 5-layer polling mitigation + `cs_chat` kill switch (cheap, removes immediate guest-storm risk without any vendor); reserve Supabase-offload as pre-costed flip path.

### 4. vendor-lockin-critic — **CONDITIONAL** (medium confidence)

**Pros:** managed infra absorbs connection storms (guest-storm evidence); mature channel/user/moderation model maps cleanly onto cs_messages; image attachments via built-in CDN with presigned URLs.

**Cons:** 2nd paid vendor on top of Supabase = doubled vendor-risk surface; data residency US/EU by default = Thailand PDPA cross-border consent + DPA BEFORE first message; lock-in structural (channel/member primitives not 1:1 with cs_messages); 18mo swap = dual-write shadow period + backfill ETL.

**Effort:** 3-4 sprints + 4-6wk shadow parallel-run. **Cost:** +$1.8-7.2k/yr.

**Must-have-for-migration:** signed DPA with cross-border clause, 18mo price-lock + 90-day exit, parallel-run shadow period, egress cost ceiling, GDPR/PDPA right-to-erasure verified end-to-end.

## Comparison matrix

| Axis | Current (Django + Supabase Realtime) | GetStream path | Supabase-offload path (prepared) |
|---|---|---|---|
| Annual OPEX | ~$0 marginal | +$4.8k-24k/yr | +$0-300/yr (free or $25/mo Pro) |
| Migration effort | — | 15-25 dev-days + 4-6wk shadow | ~10-15 dev-days (PostgREST clone pattern) |
| Staff inbox built | ❌ | ✅ via Stream | ❌ (build separately) |
| Presence / typing / read-receipts | ❌ | ✅ | ❌ |
| WS off EC2 | ❌ (channels dormant) | ✅ | ✅ |
| PDPA exposure | medium (Supabase DPA done) | high (3rd vendor, cross-border) | medium (same as today) |
| Vendor count | 1 (Supabase) | 2 (Supabase + GetStream) | 1 (Supabase) |
| Kill switch intact | ✅ (`cs_chat` flag) | requires parallel Django fallback | ✅ |
| Time-to-value | — | 2-3 months | 2-4 weeks |

## Recommendation: **STAY**

2 STAY + 2 CONDITIONAL + 0 MIGRATE = no consensus to migrate. Both STAY votes anchor on **trigger-not-met + cheaper prepared alternative**. Both CONDITIONAL votes anchor on **feature gap (staff inbox, presence, moderation)** that the team has NOT committed to building.

**GetStream is a defensible choice if and only if:**
1. Leadership commits to staff-inbox UI build in next 2 quarters → GetStream's batteries-included staff console saves more than $4.8k/yr of engineering
2. Volume crosses Supabase free-tier (200 concurrent Realtime conns / 2M msg/mo) → forced migration anyway, GetStream better-managed than Supabase-Pro
3. PDPA + cross-border DPA package executes BEFORE first message (legal gates cleared)

Until any of these three triggers fires: **[[cs-chat-supabase-offload]] remains the prepared next step.** Cost ~$0 marginal, reuses Supabase JWT mint + RLS pattern, achieves same scaling win.

## Implementation sequence IF activated (CONDITIONAL → MIGRATE)

Phase 1 (legal + procurement, 4-6 weeks): DPA, data-residency review, sub-processor list sign-off, 18mo price-lock contract with 90-day exit. **BLOCKING — no code until legal clears.**

Phase 2 (spike, 1 sprint): Stream POC in widget — typed components vs headless hooks decision; theming proof against Tailwind tokens; staff-inbox React SDK mock.

Phase 3 (mirror, 1 sprint): Django `Conversation`/`Message` stay canonical; webhook-driven archive sync `Stream → cs.Message` (replaces sync_chat_messages Celery task); server-side token endpoint for 3 auth tiers (staff app_role / authenticated customer / guest:conv_id).

Phase 4 (AD staff inbox, 2 sprints): replace `useStaffChatRealtime` + `useStaffInboxRealtime` with Stream `<ChannelList>` + `<Channel>`; remove supabaseClient.js for chat; csApi RTK mutations → Stream server-side message create.

Phase 5 (cutover, 1 sprint): parallel-run shadow period (4-6 weeks) dual-write cs_messages → GetStream + Django; verify; flip `cs_chat` flag.

Phase 6 (post-cutover): PDPA erasure job against GetStream API; archive sync becomes async only; remove Django WS fallback after 90 days warm.

**Effort estimate:** 6-8 sprints end-to-end (vs 15-25 dev-days for code-only). **Cost:** +$4.8-7.2k/yr OPEX.

## What would change this verdict

- Leadership commits to staff inbox → flip to CONDITIONAL-MIGRATE (Stream's console saves engineering)
- Supabase free-tier exhausted → forced migration; re-evaluate GetStream vs Supabase-Pro at that point
- PDPA cross-border consent + DPA executed → removes 2 of 4 lockin-critic must-haves → CONDITIONAL-MIGRATE becomes viable
- Engineering security-review bandwidth shortage (single-worker Celery + 256MB box is fragile) → ops-cost flips to CONDITIONAL (managed vendor = insurance)
- GetStream introduces usage-based pricing below $200/mo → cost case re-opens

## Related

- [[cs-architecture-decision]] — parent ADR; flip trigger source
- [[cs-chat-supabase-offload]] — cheaper prepared alternative path
- [[cs-centralization-stack]] — reuse-first build stack + constraint source
- [[cs-workflow-revised-2026-06-27]] — current CS workflow design
- [[cs-guest-storm-investigation]] — scaling-trigger evidence
- [[prod-capacity-celery-audit]] — EC2 capacity constraints
- [[cs-realtime-be-traffic-design-verdict-2026-07-08]] — current BE traffic design (2026-07-08 verdict still binding)
- [[chat-image-send-server-convergence]] — image pipeline that GetStream would obsolete
- [[multi-repo-gap-audit-methodology]] — debate-template pattern

## Critical files referenced

- `smartenplus-frontend/components/chat/ChatWidget.js`, `hooks/useChatRealtime.js`, `helpers/supabaseClient.js`
- `smartenplus-backend/cs/views.py`, `cs/models.py`, `cs/supabase_jwt.py`, `cs/tasks.py`
- `admin-dashboard/hooks/useStaffChatRealtime.js`, `useStaffInboxRealtime.js`

## Sources

- https://getstream.io/chat/docs/sdk/react/
- https://getstream.io/chat/docs/python/