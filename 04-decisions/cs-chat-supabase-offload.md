---
name: cs-chat-supabase-offload
description: Prepared flip-path ADR — decouple CS chat message path to Supabase Realtime (customer widget + admin-dashboard staff inbox) with batch archive sync back to Django. Draft; activates at the cs-architecture-decision flip trigger. Does NOT supersede the polling ADR today.
metadata:
  type: decision
  status: draft
  date: 2026-07-05
  parent: cs-architecture-decision
---

# CS Chat → Supabase Realtime Offload (Prepared Path)

> **Status: DRAFT / prepared path — do NOT build yet.** [[cs-architecture-decision]] (both-sides-poll-Django) remains the accepted transport. This ADR is the pre-designed answer to that ADR's own flip trigger, so activation is a status flip + build, not a new design debate.

## Summary

When chat load justifies it, move the **entire chat message path** (send + receive, customer AND staff) to Supabase (Postgres + Realtime WebSockets). Django exits the hot path; it receives a **batch archive sync** (Celery beat ~15 min, reusing the `sync_ota_bookings` PostgREST pattern, plus a manual admin trigger). Django copy = archive/reporting/PDPA record — **not** source of truth.

This is NOT the rejected Option B. Option B kept Django in the write path and pushed only to the 5-staff side via per-message Celery dual-write. This design is full decoupling: single write path (Supabase), push on the high-cardinality **customer** side — exactly the direction the accepted ADR prescribed ("add push on the CUSTOMER side, not staff").

## Activation trigger (from [[cs-architecture-decision]], unchanged)

Sustained widget polling **>~30 req/s** (half of the ~50-60 req/s Gunicorn ceiling) ≈ hundreds of concurrent open widgets. Secondary trigger: committing to build the staff inbox UI (none exists today — staff use Django admin) — building it Supabase-backed from day one avoids building it twice.

Current volume (2026-07-05): tens of widgets. **Trigger not met.**

## Why the recorded rejections don't apply here

| Old risk ([[cs-architecture-decision]]) | Fate under full decoupling + batch sync |
|---|---|
| **R1** per-message Django→Celery→Supabase write rides the single worker (`--concurrency=1`, behind 9-min `sync_pending_charges`) | Gone. No per-message hop. One batch pull task every ~15 min — same footprint as the existing `sync_ota_bookings` beat task. |
| **R2** two-write, no reconciliation → ghost messages | Gone. Single write path (Supabase). Django copy is a lagged archive **by design**; cursor-based batch pull (`WHERE id > last_synced_id`) is idempotent. |
| **R3** anon-key open-SELECT RLS = PII leak | Solvable, not free. RLS keyed on JWT claims; **Django mints Supabase-compatible JWTs** (HS256, signed with the Supabase JWT secret) at conversation open — for authenticated users AND guests (guest OTP flow unchanged, token swapped for a Supabase JWT scoped to one conversation). Anon key alone grants nothing. This also dissolves the recorded "NextAuth JWT ≠ Supabase JWT" objection from [[cs-centralization-stack]]. |
| **256MB box can't hold WS** ([[prod-capacity-celery-audit]]) | N/A — WebSockets terminate at Supabase, not EC2. nginx never sees a WS upgrade. |

Bonus: eliminates the **guest-storm failure mode** entirely ([[cs-guest-storm-investigation]] — 100 guests @5s poll = 2× Gunicorn ceiling). Under this design 100 concurrent guests = 100 Supabase WS connections + zero Django requests until the next batch sync.

## Architecture

- **Source of truth (hot):** Supabase tables `cs_conversations` / `cs_messages` (mirror Django `cs.Conversation`/`cs.Message` fields; explicit columns, no extras).
- **smartenplus-frontend** (customer widget): `@supabase/supabase-js` — Realtime subscribe on own conversation (`postgres_changes` INSERT filter `conversation_id=eq.X`), send = direct insert. Replaces `useChatPolling.js`.
- **admin-dashboard** (staff inbox — new build): same SDK, same tables. Staff JWT carries `role: staff` claim → RLS grants all-conversations read/write. Both repos share one Supabase project; customer types → staff sees instantly, and vice-versa.
- **Django:** exits message path. Keeps: conversation lifecycle authority optional (status open/closed can live in Supabase too), OTP flow, JWT-mint endpoint (`POST /api/cs/supabase-token/`), batch archive sync, PDPA erasure.
- **Kill switch:** `cs_chat` FeatureFlag retained ([[feature-flag-kill-switch-pattern]]). Rollback = flip widget back to the Django polling path, which stays intact in code.

## Auth / RLS design sketch

- Supabase JWT minted by Django, short-lived (≤24h, match guest-token TTL), HS256 with `SUPABASE_JWT_SECRET` (server-side env, like the existing `SUPABASE_ANON_KEY` handling).
- Claims: `sub` (django user id or `guest:<conversation_id>`), `role: authenticated`, custom `conversation_id` (customer/guest) or `app_role: staff` (staff).
- RLS: customers/guests → SELECT/INSERT only where `conversation_id = jwt.conversation_id`; staff → all rows via `app_role = 'staff'`; sender column enforced by policy (customer can only insert `sender='customer'`) — preserves the [[chat-sender-session-bleed]] guarantee.
- Anon key without a minted JWT: no table access at all.

## Batch archive sync (Django ← Supabase)

- Celery beat task, ~15 min, clone of `cs/tasks.py::sync_ota_bookings` (server-side PostgREST HTTP, no SDK) — pulls `cs_messages WHERE id > last_synced_id`, bulk-inserts into `cs_message`, records cursor. Idempotent, single task, fits the 1-concurrency worker.
- Manual trigger: Django admin action ("Sync chat now") for staff — satisfies the "manually by admin or staff or by time" requirement.
- Purpose of the Django copy: reporting, booking cross-links, PDPA export/erasure source, cold history. **Never read by live chat UIs** (lag up to 15 min by design).

## New risks / costs (honest ledger)

1. **Staff client coupling** — staff cannot work from the lagged Django copy; the staff inbox MUST be Supabase-backed. Cheap today only because no staff inbox UI exists yet; if a Django-polling inbox ships first, this migration doubles that work. Sequence accordingly.
2. **PDPA/GDPR** — chat PII resident in Supabase (US/SG region per project). Retention + erasure sweeps must run against Supabase too. Precedent: [[cs-consent-gdpr-model]] already drafts a Supabase two-store; 9 legal questions there remain OPEN and gate this too.
3. **New deps:** `@supabase/supabase-js` in two frontends (accepted ADR explicitly kept it out — activation consciously reverses that line), JWT-mint endpoint, RLS policies (must be reviewed — R3 only stays dead if RLS is right), Supabase JWT secret in Django env.
4. **Free-tier limits** — verify at activation time: concurrent Realtime connections, messages/month, Realtime rows-per-second on the current Supabase project (shared with OTA store [[supabase-ota-booking-store]]). If limits bind, chat gets its own project.
5. **Vendor coupling** — chat availability now = Supabase availability. Mitigation: kill switch falls back to Django polling path (kept intact).

## Free-tier limits verdict (added P1, 2026-07-05)

Checked against supabase.com/pricing + supabase.com/docs/guides/realtime/limits:

| Metric | Free tier | Pro tier |
|---|---|---|
| Concurrent peak connections | **200** | 500 |
| Messages / month | **2M** | custom |
| Messages / second (project-wide) | **100** | 500 |
| Channel joins / second | 100 | 500 |

Current CS chat load: tens of concurrent open widgets — safely under limits.
Projected load at trigger (>30 req/s polling → cutover): hundreds of concurrent widgets → **hits the 200-connection cap**.

**Decision: dedicated Supabase project for CS chat** before cutover activation. Do NOT share with the OTA store project ([[supabase-ota-booking-store]]). Provision the dedicated project at P6 (backfill + cutover), not before.

## Decision

Adopt as the **prepared flip path**. No build now. At trigger: flip this ADR to `accepted`, add `supersedes` banner on the transport section of [[cs-architecture-decision]], execute [[chat-supabase-migration-plan]].

## Related

- [[cs-architecture-decision]] — accepted polling ADR + the flip trigger this ADR answers
- [[chat-supabase-migration-plan]] — phased execution plan (01-projects)
- [[prod-capacity-celery-audit]] — the 256MB/2-slot/1-worker constraints
- [[cs-guest-storm-investigation]] — the failure mode this eliminates
- [[supabase-ota-booking-store]] · [[ota-sync-supabase-mirror]] — existing Supabase role + the PostgREST sync pattern to clone
- [[cs-consent-gdpr-model]] — PDPA two-store precedent, open legal gates
- [[feature-flag-kill-switch-pattern]] — rollback lever
- [[chat-sender-session-bleed]] — sender-integrity guarantee to preserve in RLS
