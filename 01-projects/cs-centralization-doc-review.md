---
name: cs-centralization-doc-review
description: 3-agent source-verification + architecture review of the session #141 Option B vault docs — finds 2 factual errors, 1 PII exposure, 1 silent-data-loss path, and an over-engineering inversion
metadata:
  type: review
  status: active
  date: 2026-06-21
  parent: cs-centralization-stack
---

# CS Centralization — Doc Review (Option B claims vs source)

> **3-agent review 2026-06-21.** Senior Django (backend-architect) + senior Next.js/admin (nextjs-fullstack-architect) source-verified every claim in the session #141 docs against the 3 live repos; senior architect (opus) stress-tested Option B soundness over their findings. Review of commit `18f64c8`.

## Summary Verdict

- **Docs ~85% factually accurate.** Most file:line + version claims CONFIRMED. **Two factual errors** (`OrderSerializer:94 __all__` is wrong; `dialogue` GenericFK is NOT nullable) + 2 minor line-number drifts.
- **Architecture: SOUND-WITH-GAPS.** The bones (Postgres = source of truth, async fan-out to a push channel) are legitimate. But the two claims that *justify choosing Supabase* are demolished by source: the "anon key = Realtime push only, no row reads" claim is **false** (RLS exposes REST reads of CS conversation PII), and the two-write path has **no reconciliation** (silent ghost messages on permanent Celery failure).
- **Over-engineering flag (matches user's standing constraint):** Option B puts Supabase Realtime push on the **5-staff side** and polls Django on the **N-customer side** — backwards from where push earns complexity. For 1-5 internal CS agents, Supabase + two-write + `sync_status` + new schema + new browser SDK does **not** earn its keep. Recommended: **both sides poll one cheap Django endpoint**, Postgres single source of truth. Removing Supabase from the message path eliminates R1, R2, and R3 below.

## Claims Table

| Claim (doc) | Verdict | Evidence | Note |
|---|---|---|---|
| Gunicorn `--workers 1 --threads 2` live prod (`docker-compose-rds.yml:13`) | ✅ CONFIRMED | `docker-compose-rds.yml:13` exact: `gunicorn --bind 0.0.0.0:8000 --workers 1 --threads 2 --timeout 30 ...` | `scripts/run.sh` uwsgi:9000 is DEAD/legacy; nginx proxies only `web:8000`. No deploy-path ambiguity in practice. |
| 103 `fields='__all__'` serializers | ⚠️ CONFIRMED (with caveat) | raw `grep` = 103 (incl 4 commented + 1 `ordering_fields` false positive); **~99 active** | Doc's 103 = raw grep number. Accurate as "grep count"; true active count ~99. |
| `TicketSerializer` `__all__` at `tickets/serializers.py:55` | ✅ CONFIRMED | line 55 exact | — |
| `OrderSerializer` `__all__` at `orders/serializers.py:94` | ❌ **WRONG** | `OrderSerializer` (line 70) uses **explicit fields**, not `__all__`. The `__all__` at line 181 = `PassengerDetailSerializer` | **Correction D1.** Use TicketSerializer as the example; OrderSerializer is already safe. |
| `IsAdminOrIsStaff` at `accounts/permissions.py:4-14` | ✅ CONFIRMED | lines 9-14: auth check + `is_admin or is_staff` | Sound reuse for CS endpoints. |
| `dialogue/` GenericFK = reuse template for Message | ✅ CONFIRMED (structure) | Comment/Notification/Review all use GenericForeignKey | Comment pattern sound template. |
| `dialogue/` GenericFK is **nullable** | ❌ **WRONG** | `content_type` + `object_id` are NOT NULL in Comment/Notification/Review | **Correction D2.** Decide Message FK nullability explicitly; don't inherit a false premise. |
| Retry pattern `products/tasks.py:35` | ⚠️ CONFIRMED (line drift) | actual: `products/tasks.py:90` `countdown=60*(2**retries)` | **Correction D3** (minor). |
| `payments/tasks.py:27` retry decorator | ✅ CONFIRMED | `@shared_task(bind=True, max_retries=3, default_retry_delay=60, time_limit=540)` | — |
| `send_telegram_message` `carts/utils.py:690` outbound HTTP template | ✅ CONFIRMED | `requests.post(url, json=payload)` — **no timeout set** | See R6: never copy the timeout-less idiom into chat sync. |
| OTP via Redis `cache.set(timeout=)` pattern exists | ✅ CONFIRMED | `stations/views.py:127` + others | — |
| `phonenumbers==8.13.2` present, `pyotp` absent, `boto3==1.26.70` present | ✅ CONFIRMED | `requirements.txt:59` / absent / `:8` | — |
| `useQRPolling.js` ref-held setInterval + unmount cleanup | ✅ CONFIRMED (caveat) | setInterval `:192`, cleanup `:169`/`:277-281`, `axios.get` | **Caveat R4:** setInterval (not setTimeout-chain) → async ticks OVERLAP if poll >3s. Tolerable at 10s payment poll; at 3s chat use setTimeout-recursion. |
| `react-toastify` present FE; `@supabase/supabase-js` absent both repos | ✅ CONFIRMED | FE `package.json:71` `^9.1.1`; supabase absent FE + admin | Consistent with doc. |
| NextAuth JWT ≠ Supabase JWT (no aud, can't use vs RLS) | ✅ CONFIRMED | `[...nextauth].js:358-403` — token carries only Django accessToken/id/profile, no `aud/role/iss` | Anon-key path genuinely necessary IF Supabase kept. |
| admin `ordersApi.js` RTK pattern + `middleware.js:4-7` protected routes | ✅ CONFIRMED | `createApi` confirmed; matcher list `:4-7`, `/cs/*` not present (add it) | — |
| `_app.js` `dynamic(ssr:false)` ChatWidget template | ✅ CONFIRMED | `_app.js:22` RefreshTokenHandler | Valid template. |
| Single celery worker, single queue, no task_routes | ✅ CONFIRMED | `docker-compose-rds.yml:55-57` `--concurrency=1 --prefetch-multiplier=1`; no `CELERY_TASK_ROUTES` | Foundation of R1. |
| "anon key = Realtime push only, no row reads" | ❌ **WRONG** | Supabase `postgres_changes` REQUIRES anon SELECT RLS or events silently drop; anon SELECT RLS also makes `cs.messages` REST-readable by anyone with the public anon key | **Correction D4 — security.** This is CS conversation PII. |
| "`sync_status` + retry gives two-write consistency" | ❌ OVERSTATED | retry alone leaves permanent divergence after max retries; no reconciliation sweep documented | **Correction D6.** See R2. |

## Architecture Risks (ranked, severity × likelihood)

| # | Risk | Sev×Like | Mitigation |
|---|---|---|---|
| **R3** | **Anon-key RLS = CS-conversation PII exposure.** Realtime-for-anon requires anon SELECT RLS → `cs.messages` becomes REST-readable by anyone with the public anon key (ships in browser). | **High × High** (if shipped) | Don't expose `cs.messages` to anon. Either authenticated Realtime (short-lived staff Supabase JWT), or **drop Supabase from read path** (preferred — R3 vanishes). |
| **R1** | **9-min Celery starvation.** Single worker, concurrency=1, shared queue; `sync_pending_charges` runs every 10min with `time_limit=540`. Chat sync queued behind it waits up to 9+ min. | **High × High** | Dedicated `chat` queue + second worker (`task_routes` + `-Q chat`), OR write Supabase **synchronously** in the Django request (one cheap REST call) and drop the Celery hop, OR (preferred) drop Supabase entirely. |
| **R2** | **Silent-ghost two-write.** Permanent Celery→Supabase failure → Postgres has the row, Supabase never does, dashboard (Supabase-only read) never shows it. No reconciliation. | **High × Med** | Reconciliation sweep (beat, 1-2min: re-push `sync_status in [failed,pending]`) + give dashboard a Django fallback read so it's never solely Supabase-dependent. (Vanishes if Supabase dropped.) |
| **R4** | **setInterval overlap at 3s.** Poll >3s (exactly when Django slot-starved) stacks overlapping requests → positive-feedback load amplification. | **Med × Med** | setTimeout-recursion (schedule next only after prev resolves) + AbortController + pause on hidden tab. Cheap, just do it. |
| **R5** | **`__all__` on hot path.** A heavy serializer holding a slot for seconds steals 1 of 2 slots, halving throughput. | **Med × Low-Med** | New CS message serializer = explicit minimal fields (id, body, sender, created_at, conversation_id) + index `(conversation_id, created_at)`. Never inherit `__all__`. |
| **R6** | **No-timeout outbound HTTP.** Copying `send_telegram_message`'s timeout-less `requests.post` → a hung Supabase write blocks the concurrency=1 worker indefinitely (turns R1 from 9min into unbounded). | **Med × Low** | Mandate `timeout=(3,10)` on every chat-path HTTP call. |

## Polling-Ceiling (honest math)

Polls = fast non-blocking GETs (thread released in ms), so it's a **req/s** question, not held-connections.
- Capacity: 2 concurrent slots ÷ ~20ms service time ≈ ~100 req/s theoretical, **~50-60 req/s usable** before tail latency knees up.
- Customer demand: 1 widget polls every 3s = 0.33 req/s. **~150-180 concurrent open widgets** to saturate chat-alone.
- **Catch:** the 2 slots are SHARED with all site traffic and drop to 1 slot whenever a slow request holds a thread (then usable halves to ~25-30 req/s). Polling demand is constant + uncorrelated with load → most expensive exactly when you can least afford it.
- **Verdict:** customer-widget→Django polling is **safe at support volumes** (tens, not hundreds, of simultaneous widgets); it does NOT reintroduce a hard bottleneck. Make it graceful: 5s interval, backoff on hidden tab, dedicated index-covered endpoint that can never hit `__all__`.
- **CS Dashboard polling load = trivial:** 5 agents × 0.33 req/s = ~1.6 req/s vs 50-60 usable. Negligible. (This is the math that kills the case for Supabase push on the staff side.)

## Over-Engineering Verdict

**Drop Supabase from the message path. Both sides poll one cheap Django endpoint. Postgres = single source of truth.**

Option B puts push (Supabase Realtime) on the **low-cardinality side (5 staff)** and polling (Django) on the **high-cardinality side (N customers)** — the inversion is the tell that Supabase is here for its own sake. The customer widget polls Django *anyway* in Option B, so Supabase isn't offloading the heavy side at all.

Removing Supabase:
- **R1, R2, R3 all vanish or shrink** (they exist *only because* Supabase is in the path).
- No two-write, no `sync_status` state machine, no `cs` schema + RLS, no service_role key handling, no `@supabase/supabase-js`, no JWT-bridge question (already moot), no second Celery queue strictly needed.
- **Reuse-first:** `useQRPolling` (→setTimeout variant) + RTK `createApi` (`ordersApi.js`) + `IsAdminOrIsStaff` already exist and are battle-tested here.
- Cost of all-polling = ~1.6 req/s from the CS team. Negligible.

**Only legitimate reason to keep Supabase:** if concurrent *customer* widgets later cross into the hundreds AND you want to offload that read load — and even then, put push on the **customer** side, not staff. Not today's scale.

## Required Doc Corrections

| # | Doc | Fix |
|---|---|---|
| D1 | `cs-centralization-stack`, `smarten-customer-os-thesis` | Remove `OrderSerializer:94 __all__` — it's explicit fields. Use `TicketSerializer` (`tickets/serializers.py:55`) as the sole confirmed `__all__` example to pin. |
| D2 | `cs-centralization-stack` | `dialogue/` GenericFK is **NOT nullable**. Fix the Message-template note; decide FK nullability explicitly. |
| D3 | `cs-centralization-stack` | Retry pattern line: `products/tasks.py:90` (not :35). |
| D4 | `cs-centralization-stack`, `supabase-ota-booking-store`, `smarten-customer-os-thesis` | "anon key = Realtime only, no row reads" is **false**. Anon Realtime requires anon SELECT RLS → exposes `cs.messages` REST reads to anyone with the public anon key. Either authenticated Realtime or drop Supabase. ("anon key safe to ship" is true but not the point — RLS exposure is.) |
| D5 | `cs-centralization-stack` | Qualify the "polling is safe" claim: 2 slots are shared with all site traffic, degrade to 1 under slow requests; require setTimeout-recursion + tab-idle backoff. |
| D6 | `cs-centralization-stack` | `sync_status`+retry ≠ consistency. Document reconciliation sweep + dashboard Django-fallback, OR remove two-write by dropping Supabase. |

## Recommendation

1. **Apply D1-D6 to the vault docs regardless** (factual hygiene).
2. **Re-decide Option B vs all-polling** before any P1b build. Architect recommendation = all-polling (simpler, reuse-first, kills 3 of 6 risks, matches the no-over-engineering constraint). Supabase's existing OTA-store role (`gmail12go` schema, read-sync) is unaffected — this only concerns the *message relay* path.

## Related

- [[cs-centralization-stack]] — the reviewed stack ADR (D1-D6 apply)
- [[smarten-customer-os-thesis]] — P1b row (D1, D4 apply)
- [[supabase-ota-booking-store]] — dual-role section (D4 applies to cs-schema relay only; gmail12go OTA store unaffected)
- [[r2-skeptic-review]] — prior red-team
