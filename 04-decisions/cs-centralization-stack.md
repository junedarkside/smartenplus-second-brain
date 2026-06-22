---
name: cs-centralization-stack
description: Reuse-first build-stack for CS Centralization — both-sides-poll-Django (Supabase OUT of message path), pyotp/SES OTP, AWS SNS SMS reminders, Telegram internal alert, Channels dormant
metadata:
  type: decision
  status: accepted
  date: 2026-06-20
  updated: 2026-06-21
  parent: smarten-customer-os-thesis
  superseded_transport_by: cs-architecture-decision
---

# CS Centralization — Build Stack

> ⚠️ **Transport REVERSED 2026-06-21 → [[cs-architecture-decision]].** This doc originally specified Option B (CS Dashboard Supabase Realtime push). That was **reversed to both-sides-poll-Django** — Supabase OUT of the message path. Net-new dep dropped to **`pyotp` only** (no `@supabase/supabase-js`, no `cs` schema, no `sync_status`). The "Supabase Realtime Layer" section below + the Option-B mentions in the Decision table are **SUPERSEDED — kept for the reasoning trail**. Everything else (channels, OTP, SNS SMS, Telegram-internal, Supabase-as-OTA-read-store) stands.

## Summary

The CS Centralization messaging track ships on **what is already installed**, plus **one** new dependency (`pyotp`, backend). Customer chat = **website widget via HTTP short-polling ~5s** (reuse `useQRPolling.js`). **CS Dashboard (admin staff) ALSO polls Django** (RTK `pollingInterval`) — NOT Supabase Realtime (see [[cs-architecture-decision]]; small prod box makes short-poll the only viable transport). Trip reminders = **AWS SNS SMS** (same `boto3`/AWS account as SES — zero new service). Email-OTP = **`pyotp` + AWS SES**. **Telegram = internal CS team alerts only** (not customer-facing). **Django Channels stays dormant**. Net effect: zero new infra, zero compose/nginx change, no production impact until P1b is built.

> **Transport decision (both-sides-poll) — [[cs-architecture-decision]] 2026-06-21.** Prod (`docker-compose-rds.yml`, confirmed) = `--workers 1 --threads 2` + 256MB cap + celery `--concurrency=1`. Short-poll releases a slot in ~20ms (5 CS staff = ~1.6 req/s, negligible). WebSocket would blow the 256MB cap; Supabase two-write would block the single celery worker. So BOTH customer widget and CS Dashboard poll one cheap Django endpoint; Postgres = single source of truth.

## Channel Architecture

| Touch point | Channel | Direction | Notes |
|---|---|---|---|
| Customer needs help | **Website chat widget** (long-polling) | Customer ↔ CS | All customer types: direct + OTA (12Go/Klook/Bookaway) |
| Trip reminder (day before) | **AWS SNS SMS** via `boto3` | Platform → traveler | 100% phone reach, same AWS account as SES |
| Booking confirmation | **Email / AWS SES** | Platform → traveler | Already live |
| CS team alert | **Telegram bot** | Platform → CS staff | Internal only — new message arrived, new booking, ops |

**WhatsApp** — rejected for startup stage: Meta template approval (days/weeks), 24h session window, $11-52/mo BSP cost. Revisit at 500+ bookings/month.

## Context

r2 red-team ([[r2-skeptic-review]]) showed the originally-implied realtime path (Daphne/Channels in-process) is not committable as scoped: a 256MB co-resident memory cliff, a `CHANNEL_LAYERS` host that points at a different redis than prod, and a session-based WS auth scheme while the API is JWT. A first research pass recommended a Centrifugo sidecar. **User constraints override that:** no over-engineering, reuse existing components/functions/modules, must not affect existing functionality or production, free/low-cost. A new Go process + compose service + nginx ws-route fails the "no new infra / no prod impact" bar. This ADR records the reuse-first stack instead.

## Decision

| Component | Choice | Reuses | Net new |
|---|---|---|---|
| Customer chat transport | HTTP short-poll ~5s | `hooks/useQRPolling.js` (interval `axios.get`) | none |
| Chat widget (FE) | Poll client, lazy-mounted `dynamic(ssr:false)` | `useQRPolling` pattern | none |
| Django chat models | `Conversation` + `Message` models (new) — ~~`sync_status`~~ dropped (no Supabase write) | `tickets.Ticket` pattern, `dialogue/` GenericFK pattern | new models (P1b) |
| CS Dashboard transport | **Polls Django** (RTK `pollingInterval`) — ~~Supabase Realtime~~ REVERSED → [[cs-architecture-decision]] | `store/api/ordersApi.js` RTK pattern | none (~~`@supabase/supabase-js`~~) |
| CS Dashboard UI | React page (CS staff reply, conversation list) | existing admin-dashboard patterns, `store/api/ordersApi.js` RTK pattern | new page (P1b) |
| Email-OTP | `pyotp` + AWS SES | `boto3==1.26.70`, `AWS_SES_REGION_*` (`settings.py:400`), `DEFAULT_FROM_EMAIL` (`:348`); FE `next-auth ^4.18.8` | `pyotp` (BE) |
| Trip reminders (SMS) | **AWS SNS** via `boto3` | same `boto3` + AWS account as SES — zero new service/account | none |
| Telegram (CS internal alert) | Outbound alert only — new message/booking → Telegram group | `send_telegram_message` (`carts/utils.py:690`), `celery==5.3.1` | none |
| Telegram inbound (optional) | Celery `getUpdates` poll → CS dashboard relay | `celery==5.3.1` | none (queue config) |
| OTA traveler identity seed | **Supabase read-sync via REST/JS API** ([[supabase-ota-booking-store]]) — `gmail12go.Information` table, 16 fields, HTTP read-only | existing Supabase REST/JS API | thin HTTP call only |

**Net new dependency: `pyotp` (backend) only** (reversed from Option B — no `@supabase/supabase-js`, see [[cs-architecture-decision]]). SMS = `boto3` already installed. Supabase = existing project, existing REST API (OTA read-store role only).

## Reuse map

- **Polling, not WS** — `useQRPolling.js` already does interval `axios.get` with ref-held `setInterval`; chat client = same shape polling `/messages?since=`. No socket client, no `_app.js` persistent connection.
- **AWS SNS SMS** — same `boto3==1.26.70` + AWS account already wired for SES (`settings.py:400`). `boto3.client('sns')` call only; no new account, no new service contract.
- **SES already live** — OTP email + booking confirmations ride existing `boto3`/SES config.
- **Telegram = internal only** — `send_telegram_message` (`carts/utils.py:690`) already outbound; use for CS staff alerts (new chat message, new booking). NOT customer-facing. Customer talks via website widget only.
- **Celery already live** — optional inbound Telegram relay = one more beat task; outbound reuses existing helper.
- **Channels stays dormant** — `channels==4.0.0` + `channels-redis==4.1.0` stay in `requirements.txt`, `carts/consumers.py` stays `TestConsumer` stub. Not removed, not activated.
- **Supabase = OTA read-store ONLY** — ([[supabase-ota-booking-store]]): `gmail12go.Information` table (source-verified: 16 cols, 58 records, 12Go bookings) — read-only identity seed. ~~(2) `cs` schema CS message relay~~ **REVERSED** — Supabase is OUT of the message path ([[cs-architecture-decision]]); no `cs` schema, no Django→Supabase write, no Realtime. Django/Postgres is the sole message store.
- **`IsAdminOrIsStaff` permission** — `accounts/permissions.py:4-14` already exists; reuse for CS endpoints. No new permission class needed.
- **`dialogue/` GenericFK pattern** — `dialogue/models.py` Comment/Notification/Review models use GenericFK; reuse as template for `Message` model structure.

## Supabase Realtime Layer (CS Dashboard only) — ⚠️ SUPERSEDED

> 🛑 **SUPERSEDED 2026-06-21 → [[cs-architecture-decision]].** This entire section described Option B (CS Dashboard Supabase Realtime push), which was REVERSED to both-sides-poll-Django. Supabase is OUT of the message path. Section kept below for the reasoning trail only — **do not implement.**
>
> **D4 + D6 ([[cs-centralization-doc-review]]) are MOOT post-reversal:** D4 (anon-key RLS would expose `cs.messages` REST reads of CS PII) and D6 (`sync_status`+retry ≠ consistency, needs reconciliation) both only applied to the Supabase relay — which no longer exists. No `cs` schema is written, so no RLS exposure and no two-write consistency gap. Recorded here, not silently dropped.
>
> _Original (validated 2026-06-21 via 3-agent investigation, then reversed same day after the polling-ceiling re-analysis):_

### Why Supabase Realtime (not pure polling for CS Dashboard)

Source-verified: `docker-compose-rds.yml:13` = `--workers 1 --threads 2` = **2 concurrent requests max**. Pure polling for the CS Dashboard would hold both Gunicorn threads → deadlock at 2 concurrent CS users. Supabase Realtime bypasses Django entirely for push delivery.

### Option B data flow

```
POST /api/cs/messages/  (customer or staff)
  → Django saves to DB
  → Celery task: write_message_to_supabase(message_id)
      → POST /rest/v1/messages (Supabase, service_role key)
      → Supabase Realtime: INSERT event → push to CS Dashboard
  → CS Dashboard receives push <1s (browser WebSocket, anon key)
  → staff reads history via Django API (NextAuth session)
```

### No JWT bridge needed

NextAuth JWT ≠ Supabase JWT (different signers, different `aud`). CS Dashboard uses anon key **only** for Realtime channel subscription — channel event push, zero row reads via anon. All data reads go through Django API. Auth bridge complexity = avoided.

### Two-write consistency + `sync_status`

`Message.sync_status` tracks Celery→Supabase write state:

| Value | Meaning |
|---|---|
| `pending` | Saved Django DB, Celery queued |
| `synced` | Supabase write succeeded, `supabase_id` saved |
| `failed` | Max retries (5) exhausted |
| `retrying` | Backoff in progress |

Retry: `max_retries=5`, `countdown=120 * (2 ** retry)` — copy `products/tasks.py:90` pattern (D3 correction [[cs-centralization-doc-review]]: line is `:90`, not `:35`).

### Dependency scope

`@supabase/supabase-js` → **admin-dashboard `package.json` only**. Frontend (`smartenplus-frontend`) has zero Supabase client. Customer widget polls Django.

## Tradeoffs

- **Short-poll latency (both sides) vs WS push:** 0-5s latency for a reply to surface. Acceptable for support chat. Zero new infra, zero prod risk. (Both widget AND CS Dashboard poll Django — [[cs-architecture-decision]].)
- **Polling-safe caveat (D5 [[cs-centralization-doc-review]] — STILL LIVE):** the 2 Gunicorn slots are shared with ALL site traffic and degrade to 1 under slow requests. Mitigate: client uses **`setTimeout`-recursion (not `setInterval`)** so a slow response can't stack requests, plus **tab-idle backoff** (slow/stop polling on hidden tab). This is a real implementation constraint for both-poll, not superseded.
- ~~**Supabase Realtime (CS Dashboard):** <1s push, two-write + `sync_status` + `@supabase/supabase-js`.~~ **REVERSED** — see [[cs-architecture-decision]]; small prod box (256MB / celery concurrency=1) makes this net-negative.
- **Deferring Channels:** avoids r2 256MB-cliff / redis-mismatch / WS-auth work entirely. Channels stays dormant. If measured chat volume later needs true real-time on the widget side, that becomes a gated project.
- **`pyotp` add:** one small pure-python lib, no service. Lowest-footprint OTP option.

## Consequences

- `pyotp` enters backend `requirements.txt` when P1a builds. **No frontend or admin-dashboard dep added** (reversed — no `@supabase/supabase-js`). No `docker-compose*` service added. No `nginx.conf` change.
- AWS SNS SMS = zero new dep (same `boto3`); zero new service account.
- Prod (`docker-compose-rds.yml`, confirmed) = `--workers 1 --threads 2` + 256MB cap + celery `--concurrency=1`. **Both** widget and CS Dashboard short-poll Django (fast non-blocking GET, slot released ~20ms). WebSocket/long-poll would blow the box; Supabase two-write would block the single celery worker. See [[cs-architecture-decision]].
- P1b requires two new Django models: `Conversation` + `Message` (no `sync_status` — Postgres is sole store, no Supabase write). Follows `dialogue/` GenericFK pattern (FK NOT nullable).
- 103 `fields='__all__'` serializers exist in backend (3-agent scan — r2 estimated 16). P1a migrations adding new FKs auto-leak through all of them. **Must pin explicit fields on `TicketSerializer` (`tickets/serializers.py:55`) BEFORE any P1a migration** to avoid 3-repo contract drift. (D1 correction [[cs-centralization-doc-review]]: `OrderSerializer:94` is **already explicit fields**, not `__all__` — earlier "+ OrderSerializer" claim removed.)
- Telegram stays internal-ops only — never customer-facing in this architecture.
- Channels left dormant — no Daphne process, no ASGI migration, no `CHANNEL_LAYERS` redis fix required for P1b.
- The r2 "INFRA GATE" WS work (Daphne, JWT WS auth, channel-layer redis) is **deferred, not required** — P1b ships both-sides-poll.
- A future "real-time push" need on the **customer-widget** side (hundreds of concurrent widgets) is the only trigger to revisit Channels vs sidecar.

## Rejected alternatives

- **Centrifugo / Soketi sidecar** — new process + compose service + nginx ws-route + ops/monitoring surface. Over-engineering vs the reuse-first + no-prod-impact constraint, despite being the best pure-realtime option.
- **Bare Daphne / Channels-in-process activation** — the r2 failure mode: 256MB co-resident cliff, channel-layer/redis mismatch, session-vs-JWT WS auth. Prod risk now for no measured benefit.
- **Supabase Realtime for customer widget** — NextAuth JWT ≠ Supabase JWT (`aud` mismatch, different signers). No auth bridge without significant new complexity. Widget polls Django instead (simpler, works with current NextAuth session).
- **Twilio Verify / SendGrid for OTP** — new paid service; SES already covers email delivery.
- **WhatsApp for customer comms** — Meta Business API requires BSP ($5-40/mo), template approval (days/weeks), 24h session window. Rejected for startup stage. Revisit at 500+ bookings/month.
- **Telegram for customer chat** — Telegram adoption lower than WhatsApp for EU/US/Asia tourists; website widget = zero friction (customer already on site). Telegram stays internal.

## Related

- [[smarten-customer-os-thesis]] — the decision this stack serves
- [[cs-architecture-decision]] — transport reversal (both-sides-poll, supersedes the Supabase relay section)
- [[cs-centralization-doc-review]] — source-verification; D1-D6 corrections applied here
- [[cs-centralization-review-2026-06-22]] — cluster integrity review
- [[r2-skeptic-review]] — flagged the realtime track; source of the constraints
- [[r3-leader-synthesis]] — parent review synthesis

Research sources: [Centrifugo](https://github.com/centrifugal/centrifugo) · [Soketi](https://github.com/soketi/soketi) · [PyOTP](https://pyauth.github.io/pyotp/) · [SES OTP cost](https://prelude.so/blog/10-best-email-otp-providers-for-verification)
