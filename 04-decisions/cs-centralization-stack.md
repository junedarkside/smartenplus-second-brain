---
name: cs-centralization-stack
description: Reuse-first build-stack for CS Centralization — long-polling chat widget, pyotp/SES OTP, AWS SNS SMS reminders, Telegram internal alert, Channels dormant
metadata:
  type: decision
  status: accepted
  date: 2026-06-20
  parent: smarten-customer-os-thesis
---

# CS Centralization — Build Stack

## Summary

The CS Centralization messaging track ships on **what is already installed**, plus exactly **one** new dependency (`pyotp`). Customer chat = **website widget via HTTP long-polling** (reuse `useQRPolling.js`). Trip reminders = **AWS SNS SMS** (same `boto3`/AWS account as SES — zero new service). Email-OTP = **`pyotp` + AWS SES**. **Telegram = internal CS team alerts only** (not customer-facing). **Django Channels stays dormant**. Net effect: zero new infra, zero compose/nginx change, no production impact until P1b is built.

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
| Customer chat transport | HTTP long-polling | `hooks/useQRPolling.js` (interval `axios.get`) | none |
| Chat widget (FE) | Poll client, lazy-mounted `dynamic(ssr:false)` | `useQRPolling` pattern | none |
| Django chat models | `Conversation` + `Message` models (new) | `tickets.Ticket` pattern | new models (P1b) |
| CS Dashboard | React page (CS staff) | existing admin patterns | new page (P1b) |
| Email-OTP | `pyotp` + AWS SES | `boto3==1.26.70`, `AWS_SES_REGION_*` (`settings.py:400`), `DEFAULT_FROM_EMAIL` (`:348`); FE `next-auth ^4.18.8` | `pyotp` (BE) |
| Trip reminders (SMS) | **AWS SNS** via `boto3` | same `boto3` + AWS account as SES — zero new service/account | none |
| Telegram (CS internal alert) | Outbound alert only — new message/booking → Telegram group | `send_telegram_message` (`carts/utils.py:690`), `celery==5.3.1` | none |
| Telegram inbound (optional) | Celery `getUpdates` poll → CS dashboard relay | `celery==5.3.1` | none (queue config) |
| OTA traveler identity seed | **Supabase read-sync via REST/JS API** ([[supabase-ota-booking-store]]) — `gmail12go.Information` table, 16 fields, HTTP read-only | existing Supabase REST/JS API | thin HTTP call only |

**Net new dependency across the whole track: `pyotp` only.** SMS = `boto3` (already installed). Supabase = HTTP call to existing API.

## Reuse map

- **Polling, not WS** — `useQRPolling.js` already does interval `axios.get` with ref-held `setInterval`; chat client = same shape polling `/messages?since=`. No socket client, no `_app.js` persistent connection.
- **AWS SNS SMS** — same `boto3==1.26.70` + AWS account already wired for SES (`settings.py:400`). `boto3.client('sns')` call only; no new account, no new service contract.
- **SES already live** — OTP email + booking confirmations ride existing `boto3`/SES config.
- **Telegram = internal only** — `send_telegram_message` (`carts/utils.py:690`) already outbound; use for CS staff alerts (new chat message, new booking). NOT customer-facing. Customer talks via website widget only.
- **Celery already live** — optional inbound Telegram relay = one more beat task; outbound reuses existing helper.
- **Channels stays dormant** — `channels==4.0.0` + `channels-redis==4.1.0` stay in `requirements.txt`, `carts/consumers.py` stays `TestConsumer` stub. Not removed, not activated.
- **Supabase = read-only sync** — ([[supabase-ota-booking-store]]) `gmail12go.Information` table (source-verified: 16 cols, 58 records, 12Go bookings). Read via existing Supabase REST/JS API to seed Customer identity. Stays standalone; no Django schema change. Consent opt-in captured at service-comms touchpoint = marketing unlock.

## Tradeoffs

- **Polling latency vs WebSocket push:** polling adds seconds-scale latency vs sub-second WS. Acceptable for CS chat (not a trading floor). Buys zero new infra + zero prod risk.
- **Deferring Channels:** avoids the r2 256MB-cliff / redis-mismatch / WS-auth work entirely *now*. Cost: if conversation volume later demands true real-time, Channels activation (or a sidecar) becomes a separate gated project — but only if measured need arises.
- **`pyotp` add:** one small pure-python lib, no service. Lowest-footprint OTP option.

## Consequences

- Only `pyotp` enters `requirements.txt` when P1a builds. No FE dep added. No `docker-compose*` service added. No `nginx.conf` change.
- AWS SNS SMS = zero new dep (same `boto3`); zero new service account.
- P1b requires two new Django models: `Conversation` + `Message` (the missing storage layer for website chat).
- Telegram stays internal-ops only — never customer-facing in this architecture.
- Channels left dormant — no Daphne process, no ASGI migration, no `CHANNEL_LAYERS` redis fix required for P1b.
- The r2 "INFRA GATE" WS work (Daphne, JWT WS auth, channel-layer redis) is **deferred, not required** — P1b ships polling-first.
- A future "real-time push" need is the only trigger to revisit Channels vs sidecar.

## Rejected alternatives

- **Centrifugo / Soketi sidecar** — new process + compose service + nginx ws-route + ops/monitoring surface. Over-engineering vs the reuse-first + no-prod-impact constraint, despite being the best pure-realtime option.
- **Bare Daphne / Channels-in-process activation** — the r2 failure mode: 256MB co-resident cliff, channel-layer/redis mismatch, session-vs-JWT WS auth. Prod risk now for no measured benefit.
- **Twilio Verify / SendGrid for OTP** — new paid service; SES already covers email delivery.
- **WhatsApp for customer comms** — Meta Business API requires BSP ($5-40/mo), template approval (days/weeks), 24h session window. Rejected for startup stage. Revisit at 500+ bookings/month.
- **Telegram for customer chat** — Telegram adoption lower than WhatsApp for EU/US/Asia tourists; website widget = zero friction (customer already on site). Telegram stays internal.

## Related

- [[smarten-customer-os-thesis]] — the decision this stack serves
- [[r2-skeptic-review]] — flagged the realtime track; source of the constraints
- [[customer-os-thesis-review]] — parent review

Research sources: [Centrifugo](https://github.com/centrifugal/centrifugo) · [Soketi](https://github.com/soketi/soketi) · [PyOTP](https://pyauth.github.io/pyotp/) · [SES OTP cost](https://prelude.so/blog/10-best-email-otp-providers-for-verification)
