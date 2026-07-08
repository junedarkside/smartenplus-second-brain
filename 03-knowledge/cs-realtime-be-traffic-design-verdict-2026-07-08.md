# CS Realtime Chat — BE Traffic Design Verdict

**Date:** 2026-07-08  
**Verdict:** ✅ Correct design for current stack constraints. No redesign needed.  
**Context:** Reviewed during identity-switch manual test session. User questioned why Django still gets hit in realtime mode.

---

## Stack Constraints That Drive Design

| Constraint | Rules out | What we use instead |
|-----------|-----------|---------------------|
| 2-slot Gunicorn (1 vCPU EC2) | Long-poll / Django Channels / WebSocket on BE (holds slot, box dead at 3 concurrent users) | Supabase handles all persistent connections |
| 256MB RAM | Daphne + Channels in-process, Redis pubsub | Supabase free tier handles realtime |
| 1-concurrency Celery | Per-message sync tasks (queue backs up under load) | Batch cursor sync every ~15 min via periodic task |
| No SaaS budget | Stream Chat (~$500+/mo), bigger EC2 | Supabase free tier (200 realtime connections ceiling) |
| Django owns users/bookings | Supabase Auth (can't replicate Django user model) | BE-minted HS256 JWT + `accessToken` callback — Supabase's official third-party-auth pattern |

---

## Division of Labor (authoritative)

**Supabase = message transport only**
- INSERT (FE widget → `cs_messages` via RLS-gated anon client)
- SELECT history (AD `useStaffChatRealtime` on conv select)
- Realtime channel (postgres_changes INSERT publication)

**Django = everything else**
- Auth authority: mints 15-min Supabase JWT (`/api/cs/supabase-token/`)
- Conversation lifecycle: create, status change, close
- Read state: `cs_last_read_at` on Django `Conversation` model (only place it lives)
- Mark-read: `POST /api/cs/conversations/<id>/mark-read/`
- Periodic archive: `sync_chat_messages` Celery task (Supabase → Django `cs_message` table)

---

## Expected BE Traffic in Realtime Mode (not bugs)

| BE call | Trigger | Frequency |
|---------|---------|-----------|
| `POST /api/cs/supabase-token/` | Token mint at conv open + 14-min refresh | ~4–8/hr per active user |
| `POST /api/cs/conversations/<id>/mark-read/` | New customer message arrives while staff has conv open + tab visible | 1× per incoming customer msg |
| `GET /api/cs/conversations/` | Page load + filter change (SideList) | Low |
| `GET /api/cs/messages/` | Conv select in ConversationDetail (redundant in RT mode — fires once, `pollingInterval:0`) | 1× per conv select |

Idle rate: ~8 BE requests/hr. Polling mode equivalent: ~700–1200/hr.

---

## Why Mark-Read Still Hits Django

`cs_last_read_at` lives only in Django DB. Supabase has no concept of it. To maintain read-state (unread badge counts per staff member), mark-read must write to Django. This is by design — Supabase is message transport only, not user state.

**One POST per incoming customer message while conv is open** = correct behavior post `ed1aa0a`. Not a polling loop.

---

## Remaining Gaps (operational, not design flaws)

| Gap | Risk | Fix |
|----|------|-----|
| `sync_chat_messages` Celery beat **not scheduled** | Messages exist only in Supabase — no Django archive, no backup | Register task in `CELERY_BEAT_SCHEDULE`. Config task, not code. |
| Supabase free tier 200 realtime connections ceiling | OK at current scale; ~10 staff + ~50 concurrent customers well within limit | Flip to dedicated Supabase project when concurrent connections approach 150. ADR already written. |
| Redundant `GET /api/cs/messages/` on conv select | Cosmetic — 1 extra GET per click, results unused in RT mode | Add `skip: USE_REALTIME` to `useGetMessagesQuery` in `ConversationDetail.js`. Optional cleanup. |

---

## Linked

- [[ota-chat-realtime-impl-2026-07-08]] — full impl details
- [[ota-chat-auth-switch-analysis-2026-07-08]] — identity switch test scenarios
- [[cs-guest-identity-best-practices]] — guest token security patterns
- [[chat-supabase-migration-plan]] — scale-up trigger conditions
