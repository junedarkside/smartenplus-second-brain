---
name: cs-gap-debate-verdicts
description: CS Centralization gap debate verdicts — 3-agent (backend/frontend/skeptic) 2026-06-22. 12 implementation decisions + 6 skeptic corrections. Build reference for next session.
metadata:
  type: knowledge
  status: active
  date: 2026-06-22
  parent: cs-architecture-decision
---

# CS Centralization — Gap Debate Verdicts

> **3-agent debate 2026-06-22.** Backend-architect (B1-B6) + Senior-frontend (F1-F6) + Skeptic (S1-S6). All verdicts locked. **Start build from Step 1 in build order below.**

## Backend Verdicts

### B1 — App location
New `cs/` Django app. `dialogue/` = GenericFK forum/review (zero overlap). `accounts/` = auth identity. Clean boundary, own migrations, own URL namespace, one `INSTALLED_APPS` entry.

### B2 — DB index
One composite `(conversation_id, created_at)` only. Covers poll query: equality on `conversation_id` + range on `created_at` + ORDER BY. Single-column `created_at` redundant — skip.

### B3 — OTP type
**HOTP** (counter-based), not TOTP. TOTP requires clock sync — SES delivery latency + client drift = fragile. HOTP code valid until consumed or TTL expires. But see S2: store in PostgreSQL, not Redis.

### B4 — OTP rate limiting
Two layers:
- Issue: Redis `INCR cs:otp:issue:{email}` TTL=3600s cap 3 (per-email, not per-IP)
- Verify: `CSOtp.attempts` field cap 5, on 5th fail delete row (force re-request)
DRF IP throttle = first-pass only. See S2 for OTP storage correction.

### B5 — Guest sender auth
Signed token (`django.core.signing.dumps({'email', 'conversation_id'}, salt='cs-guest')` TTL=86400s). Issued at OTP verify. Sent in `Authorization: Bearer` header. `?email=` proof dropped — unfakeable signed token replaces it.

### B6 — Supabase normalisation
Celery Beat task every 15min. Normalise: NOTIFY/NOTIFIED→canonical, Participant type whitelist, Operator strip/trim, outlier dates exclude. Fetch only rows with `updated_at` in last 30min (not full scan). Store clean rows in local Django model. Dedicated `-Q sync` queue (see S5). Retryable with exponential backoff.

---

## Frontend Verdicts

### F1 — Chat widget state
Local state + axios + `useReducer` (not RTK slice). Widget = lazy `dynamic(ssr:false)` island. RTK = Redux coupling + boilerplate on every page load for most-users-never-open widget. `useReducer` for `{messages, conversationId, status, cursor}`.

### F2 — Polling hook
New `hooks/useChatPolling.js` with **setTimeout-recursion** (not setInterval — overlapping requests at fast intervals). Next tick fires only after response resolves. `visibilitychange` pause guard + AbortController cleanup per request. Reusable in CS Dashboard. **5-10s interval minimum** (see S1).

### F3 — Guest identity
`localStorage` with 24h TTL (`cs_guest_email` + `cs_guest_email_expires_at`). `sessionStorage` lost on tab close = bad UX for unresolved conversations. Clear on logout or expiry check on mount.

### F4 — CS Dashboard polling
RTK `pollingInterval` on `useGetConversationsQuery`. 5 staff × 0.2 req/s = ~1 req/s — trivial. One-line config, integrates with RTK cache, unmounts cleanly. Manual `refetch()` = reimplementing RTK for no gain.

### F5 — OTP auto-open chat after redirect
`sessionStorage.setItem('cs_open_after_login', '1')` before OTP redirect. Widget mount effect in `_app.js` reads + deletes flag. Wait for `useSession() status === 'authenticated'` before reading. URL params unreliable through NextAuth redirect chain.

### F6 — Admin middleware guard
Add both `/cs` and `/cs/:path*` to matcher array in `admin-dashboard/middleware.js:4-7`. Both needed: `:path*` matches one or more segments, not zero.

---

## Skeptic Corrections (all load-bearing — do not skip)

### S1 — Poll capacity math corrected
Previous "~150 widgets to saturate" = WRONG. Assumed 20ms service time. Realistic = 100-300ms. **Recalc: 2 slots / 200ms = 10 req/s usable. At 5s polling = ~50 safe concurrent widgets.** Fix: 5-10s interval floor, composite index, nginx 10s hard timeout on `/api/cs/` routes.

### S2 — OTP in PostgreSQL, not Redis
`allkeys-lru` 100MB Redis WILL evict OTP keys under memory pressure → `INVALID_OR_EXPIRED_OTP` with zero recourse. **Use `CSOtp` PostgreSQL model** (`email`, `secret`, `attempts`, `expires_at`). Add Beat cleanup task to delete expired rows. Overrides B3/B4 Redis assumption for OTP storage. Redis rate-limit counters (`cs:otp:issue:{email}`) still fine — loss of a counter = worst case one extra OTP issue, not lockout.

### S3 — Auto-reopen rate limit required
No limit = single customer can spam messages → infinite reopen loop → CS inbox flooded. **`Conversation.reopen_count` + `reopen_last_at`. Reject if `reopen_count >= 3` within 1h → 429 `REOPEN_RATE_LIMITED`.** Reset `reopen_count=0` when staff closes (clean slate on intentional close).

### S4 — Server-side cursor, not client timestamp
Client clock drift + DST + Thai device misconfiguration = guaranteed `since` timestamp bugs. Client 5min fast = silent message miss. **Response includes `next_cursor` = last message `id`. Client echoes `?cursor=` on next poll. Server: `Message.objects.filter(conversation=x, id__gt=cursor)`.** Zero clock dependency.

### S5 — Supabase sync needs dedicated queue
`sync_pending_charges` `time_limit=540s` blocks single Celery worker up to 9min. Sync task queued behind it = 9min stale. **Add `-Q sync` queue to sync task + second worker entry in `docker-compose-rds.yml`.** OR for P0 pilot: accept manual pre-send sync run (fire-and-forget acceptable for one-time batch).

### S6 — P0 MDE pre-commitment required
450 contacts ≠ automatically adequate. Depends on primary metric:
- Open rate ≥15% → 450 adequate
- Booking conversion ≥2% → need ~1,400 (underpowered)
**Owner must pre-commit metric + MDE before send.** Post-send analysis is uninterpretable without pre-committed threshold.

---

## Build Order (next session starts here)

1. **Django `cs/` app** — `Conversation` + `Message` + `CSOtp` models, composite index, migration
2. **7 API endpoints** — HOTP, PostgreSQL OTP, signed-token guest auth, server-side cursor, reopen rate limit
3. **`hooks/useChatPolling.js`** — setTimeout-recursion, 5-10s, visibilitychange, AbortController
4. **Customer chat widget** — lazy `dynamic(ssr:false)`, useReducer, localStorage guest identity
5. **Email-OTP login page** — reuse `login.js` shell, Formik+Yup, sessionStorage flag
6. **CS Dashboard** — RTK pollingInterval, middleware.js guard
7. **Supabase sync Celery task** — 15-min Beat, normalisation, `-Q sync` dedicated queue
8. **P0 pilot** — owner pre-commits metric+MDE → manual pre-send sync → send to ~450 Klook Confirmed

## Related
- [[cs-architecture-decision]] — transport decision (both-sides-poll-Django)
- [[cs-api-contract]] — 7 endpoints (updated with S1-S4 corrections)
- [[cs-centralization-design-concept]] — UX/visual spec for all 3 surfaces
- [[supabase-ota-booking-store]] — data source (561 records, schema verified)
- [[cs-p0-measurement-protocol]] — P0 pilot runbook (updated to ~450 sample)
