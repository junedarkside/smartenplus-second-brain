---
name: chat-supabase-migration-plan
description: Phased execution plan for the CS chat → Supabase Realtime offload. Document only — build gated on the cs-chat-supabase-offload ADR flipping to accepted (trigger in cs-architecture-decision).
metadata:
  type: project
  status: draft
  date: 2026-07-05
  parent: cs-chat-supabase-offload
---

# Chat → Supabase Migration Plan (gated, document-only)

> **Do not build until** [[cs-chat-supabase-offload]] flips to `accepted` (trigger: sustained widget polling >~30 req/s, or committed staff-inbox build). All phases branch off `develop` per branch policy — never main.

## Current state (what gets replaced / kept)

| Piece | Today | After |
|---|---|---|
| Customer receive | `hooks/useChatPolling.js` 5s→30s poll `GET /api/cs/messages/` | Supabase Realtime subscribe (replaced) |
| Customer send | `POST /api/cs/messages/send/` (`components/chat/ChatPanel.js:29`) | Supabase insert (replaced) |
| Staff UI | none — Django admin only | admin-dashboard Supabase inbox (new) |
| Auth | SimpleJWT / `X-CS-Guest-Token` HMAC / `IsAdminOrIsStaff` | unchanged for site; + Django-minted Supabase JWT for chat |
| Source of truth | Django `cs_conversation`/`cs_message` | Supabase; Django = batch archive |
| Kill switch | `cs_chat` FeatureFlag | kept — also the rollback lever |

## Phases

### ① Supabase schema + RLS (backend repo, SQL only)
- Tables `cs_conversations`, `cs_messages` mirroring `cs/models.py` fields (explicit columns). Index `(conversation_id, created_at)`.
- Enable Realtime on `cs_messages` INSERT.
- RLS per [[cs-chat-supabase-offload]] sketch: conversation-scoped customer/guest policies, `app_role: staff` full access, sender-column enforcement, zero anon-only access.
- Decide same-project vs dedicated project after checking free-tier Realtime limits (shared with OTA store [[supabase-ota-booking-store]]).

### ② Django Supabase-JWT mint endpoint
- `POST /api/cs/supabase-token/` — accepts SimpleJWT bearer OR guest token (OTP flow unchanged upstream); returns short-lived HS256 Supabase JWT (`SUPABASE_JWT_SECRET` env, no default — per [[ota-p2-impl-plan]] env rule).
- Staff variant: `IsAdminOrIsStaff` → `app_role: staff` claim.

### ③ Customer widget swap (smartenplus-frontend)
- Add `@supabase/supabase-js`. New hook `useChatRealtime` (subscribe + history select + insert) behind the `cs_chat` flag variant; `useChatPolling.js` stays in tree as rollback path.
- `ChatWidget.js` state machine unchanged; only transport layer swaps. Reuse existing conversation-open flow, then call mint endpoint.

### ④ Staff inbox (admin-dashboard)
- New inbox page: conversation list + thread panel, all-conversations Realtime subscribe, reply = insert. Staff JWT from ②.
- Ticket/booking context links stay on Django APIs — only the message thread talks to Supabase.
- Prerequisite for cutover: customers must have someone to talk to on the Supabase side.

### ⑤ Batch archive sync + manual trigger
- Celery task cloning `cs/tasks.py::sync_ota_bookings` (PostgREST, no SDK): pull `cs_messages` past cursor → bulk insert `cs_message` → advance cursor. Beat ~15 min (register in prod DB — DatabaseScheduler, per [[prod-capacity-celery-audit]]).
- Django admin action "Sync chat now" = same task, on demand (admin/staff manual sync requirement).
- PDPA erasure job extended to delete in Supabase too ([[cs-consent-gdpr-model]]).

### ⑥ Backfill + cutover
- One-off management command: existing `cs_message` rows → Supabase (idempotent upsert by original id).
- Cutover behind flag: enable Supabase transport for a small % / staff-tested conversation first, then all. Old polling endpoints stay live (throttled) during soak.

### ⑦ Rollback
- Flip flag → widget returns to `useChatPolling` + Django endpoints (never removed in this migration).
- Run archive sync once to pull any Supabase-only messages into Django before resuming Django-as-source.

## Verification (at build time)
- Two browsers (customer + staff inbox): message appears both directions <1s, no Django request in network tab during chat.
- RLS negative tests: anon key alone → 0 rows; guest JWT of conv A cannot read conv B; customer cannot insert `sender='cs'`.
- Sync idempotency: run task twice → row count unchanged; admin manual trigger works.
- Kill switch: flag off → widget reverts to polling, still functional.

## Related
[[cs-chat-supabase-offload]] · [[cs-architecture-decision]] · [[ota-sync-supabase-mirror]] · [[cs-guest-storm-investigation]] · [[feature-flag-kill-switch-pattern]]
