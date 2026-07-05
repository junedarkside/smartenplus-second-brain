---
name: cs-architecture-decision
description: CS Centralization message-transport ADR — both-sides-poll-Django chosen over Option B Supabase Realtime; supersedes the Supabase relay. Plus token-WCAG resolution (Approach A companion text-tokens).
metadata:
  type: decision
  status: accepted
  date: 2026-06-21
  parent: cs-centralization-stack
  supersedes: "cs-centralization-stack.md Supabase Realtime Layer section"
---

# CS Architecture Decision — Transport + Token WCAG

> **Gap-closure 2026-06-21** (architect, opus). Resolves the two decisions that blocked downstream gaps. **Supersedes** the "Supabase Realtime Layer (CS Dashboard only)" section of [[cs-centralization-stack]].

## Decision 1 — Message transport: BOTH-SIDES-POLL-DJANGO

**Chosen:** customer widget AND CS Dashboard both poll one cheap Django endpoint. Postgres = single source of truth. **Supabase OUT of the message path.**

**Rejected:** Option B (widget polls Django + CS Dashboard Supabase Realtime push).

### Why

The only load-bearing justification for Supabase-in-message-path was "Gunicorn 1w×2t = 2 slots → polling deadlocks the CS Dashboard." **That premise is false** — it conflated long-polling (holds a thread) with short-polling (releases in ~20ms). Polling-ceiling math: ~50-60 usable req/s; CS Dashboard at 5 staff = **~1.6 req/s**, three orders of magnitude below saturation. No deadlock.

Option B is also **inverted**: it puts push (the complexity-earning mechanism) on the low-cardinality side (5 staff) and leaves polling on the high-cardinality side (N customers). Push earns its cost where there are many clients — here it's bolted to the side with five.

Keeping Supabase in the message path is what *creates* 3 of the 6 risks from [[cs-centralization-doc-review]] — they don't exist independently:
- **R3 (High×High)** anon-SELECT RLS required for `postgres_changes` → `cs.messages` REST-readable by anyone with the public anon key = CS-conversation PII leak. **Remove Supabase → vanishes.**
- **R1 (High×High)** Django→Celery→Supabase write rides single worker, concurrency=1, behind `sync_pending_charges` (9-min `time_limit`). **Remove Celery hop → vanishes.**
- **R2 (High×Med)** two-write, no reconciliation → silent ghost messages. **Remove second write → vanishes.**

Against the standing constraints (no over-engineering / reuse / no prod impact / free): Option B adds `@supabase/supabase-js`, `cs` schema + RLS, service_role key, `sync_status` state machine, reconciliation sweep — to save 1.6 req/s the server doesn't notice. Both-sides-poll reuses `useQRPolling.js` (→setTimeout-recursion variant), RTK `createApi` (`ordersApi.js`), `IsAdminOrIsStaff` (`accounts/permissions.py:4-14`).

### What changes

| Concern | Outcome |
|---|---|
| Supabase in message path | **NO.** (gmail12go OTA identity-seed read-sync untouched — different role.) |
| `cs` Supabase schema | **NOT created.** Gap 2 collapses to N/A. |
| Celery chat queue | **NOT needed** (no async Supabase write). Celery keeps existing jobs + internal-only Telegram CS alert. |
| `Message.sync_status` field | **Dropped** from model. |
| Customer widget | polls `GET /api/cs/messages/?conversation=&since=` ~5s (setTimeout-recursion, AbortController, pause-on-hidden-tab). |
| CS Dashboard | polls same Django API via RTK `pollingInterval` ~3-5s. No WebSocket, no anon key, no browser SDK. |
| `@supabase/supabase-js` | **NOT added** to any repo. |

### Trigger to flip (concrete)

Sustained **concurrent customer widgets in the hundreds** — when widget polling alone consistently exceeds **~30 req/s** (half usable capacity). Then add push — **on the customer side, not staff.** Not today's volume (tens of widgets).

### EC2-too-small objection (answered — prod-verified)

> `docker-compose-rds.yml` = **CONFIRMED production** (owner-confirmed 2026-06-21). `scripts/run.sh` uwsgi:9000 is dead — nginx proxies `web:8000` only. No deploy-path ambiguity.

**Instinct:** prod box is small → adding polling load seems backwards.

**Resolution — held-connection vs short-poll.** The constraint is how long a request HOLDS a slot, not how many requests arrive.
- **Long-poll / WebSocket** holds a Gunicorn slot for SECONDS (waiting for a message). 2 users (`--workers 1 --threads 2`, :13) = both slots gone = site dead. Persistent WS connections also blow the **256MB `mem_limit`** (:14) — the r2 "256MB cliff" — and a channel-layer on the 100MB `allkeys-lru` redis (:49) would **silently evict** chat messages.
- **Short-poll** grabs a slot, runs an indexed `SELECT ... WHERE created_at > since`, releases in ~20ms.

**Prod numbers (from source):** 2 slots ÷ ~20ms ≈ **50-60 usable req/s**. CS Dashboard 5 staff = **~1.6 req/s** (negligible). Customer widgets saturate only at ~150+ simultaneous open (you have tens).

**Supabase made the small box WORSE, not better:**
- Two-write runs on the **single celery worker, `--concurrency=1`** (:57, `mem_limit 256m` :80) — ONE task at a time, behind `sync_pending_charges` (9-min `time_limit`). On this box R1 is **literal**, not theoretical.
- Option B still polled Django on the heavy **customer** side; Supabase only offloaded the trivial **1.6 req/s staff** side = push on the wrong side. Net: more work on the strained box (extra Celery task + outbound HTTPS per message) to relieve a load the box never felt.

**Real EC2 lever (orthogonal to transport):** 256MB + `workers 1` = **no RAM headroom to add workers via flag** (each Django gunicorn worker ≈ 80-150MB) → the real fix is **instance-size up**, not a config flag. Independent of that, keep each poll sub-ms: index `(conversation_id, created_at)`, tab-idle backoff, explicit-minimal serializer (no `__all__`). Both-poll is correct at the current size AND scales when the box grows.

**Conclusion:** the small prod box is the strongest argument FOR both-poll — short-poll is the only transport this box tolerates; WebSocket dies on memory, Supabase two-write dies on the single celery worker.

## Decision 2 — Token WCAG fix: APPROACH A (companion text-tokens)

3 design tokens + gray400 FAIL WCAG AA as text on white (see [[cs-centralization-design-concept]]). **Chosen: add companion text-tokens, leave existing hex for icons/dots/borders/badge-bg.** Rejected mutating existing hex (would dull every status icon/dot platform-wide for ~8-10 text sites).

| New token | Hex | Contrast on white |
|---|---|---|
| `COLORS.status.successText` | `#065F46` | 9.73:1 ✅ |
| `COLORS.status.errorText` | `#991B1B` | 6.30:1 ✅ |
| `COLORS.status.warningText` | `#92400E` | 9.73:1 ✅ |

`gray400` text → existing `gray500` (4.83:1) / `gray700` (8.59:1). No new token.

### Blast radius (measured grep, frontend)

41 `status.*` refs + 17 `gray400` refs. **Majority non-text** (MUI icons, SVG stroke/fill, dots, borders) — pass 3:1, do NOT change. **Genuine failing TEXT sites ~8-10:** `components/order/OrderDetail.js:310,311,319,320` · `components/activities/shared/UrgencyMessage.js:17,23` · `PricingDisplay.js:149` · `pages/bookings/[bookingId].js:70` · `components/auth/ProfileMenu.js:41,69`.

### Scope

**Separate platform design-token issue, NOT a CS-feature task.** All failing sites are non-CS (orders/bookings/profile); CS just surfaced it. File against `helpers/designSystem.js`; CS consumes new tokens once they land.

## Consequences

- Gap 1 (API contract) builds polling-only (no Supabase sync fields) — see [[cs-api-contract]].
- Gap 2 (Supabase `cs` schema) = N/A — documented, not built.
- [[cs-centralization-stack]] "Supabase Realtime Layer" section is superseded; the stack's Decision-table CS-Dashboard-realtime row + `@supabase/supabase-js` net-new dep should be corrected (D-correction).
- Token fix is a standalone follow-up issue, doesn't block CS build.

## Related
- [[cs-chat-supabase-offload]] — **prepared flip-path design (draft 2026-07-05)** for the trigger defined above: full decoupling to Supabase Realtime + batch archive sync. Pre-answers R1/R2/R3 for that architecture. This ADR stays accepted until the trigger fires.
- [[cs-centralization-stack]] — superseded transport section
- [[cs-centralization-doc-review]] — the 6 risks + polling-ceiling math
- [[cs-api-contract]] — built on this decision
- [[cs-centralization-design-concept]] — token WCAG source
- [[prod-capacity-celery-audit]] — prod EC2/Celery capacity constraints driving the polling decision (web 2-slot + celery 1-serial at floor)
