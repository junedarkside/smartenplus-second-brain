---
name: r1-tech-feasibility
description: R1 specialist review — technical feasibility of the Smarten Customer OS thesis against the real backend.
metadata:
  type: r1-specialist
  role: tech-feasibility
  scope: thesis
  date: 2026-06-20
  parent: customer-os-thesis-review
---

# R1-Tech-Feasibility — Smarten Customer OS Thesis

## Summary

The thesis is **buildable but not as planned.** The backend is greener than the pre-scan claimed yet less green than a cold start: Channels, Celery, and Redis are *installed and configured*, and a one-way Telegram bot pipeline already exists. But realtime is *not activated* (WSGI/Gunicorn in prod, WebSocket branch commented out in `Smartenplus/asgi.py`, no Daphne), and there is no Customer/Conversation/Message/ChatSession model. The phase-1 timeline (2-3 months for 6 greenfield-ish deliverables on an unactivated realtime stack) is **unrealistic as written** — the realistic critical path is the realtime activation + ASGI migration alone. Tech verdict: **BUILDABLE-REVISED**.

## Context

Reviewed `Smartenplus/settings.py`, `Smartenplus/asgi.py`, `Smartenplus/routing.py`, `Smartenplus/celery.py`, `accounts/models.py`, `bookings/models.py`, `orders/models.py`, `billings/models.py`, `tickets/models.py`, `dialogue/models.py`, `dialogue/signals.py`, `carts/consumers.py`, `carts/utils.py`, `orders/notifications.py`, `requirements.txt`. The thesis proposes a 5-phase Customer OS: unified Customer DB, Booking DB, Website Chat (WebSocket), Telegram bridge, omnichannel WhatsApp/LINE/Email, AI Copilot. This note scores only the technical feasibility of realizing each.

Pre-scan corrections (pre-scan was wrong on infra):
- Pre-scan said NO Channels/Celery/Redis/Daphne. **Reality:** `channels==4.0.0`, `channels-redis==4.1.0`, `celery==5.3.1`, `django-redis==5.4.0`, `redis==4.5.4` all in `requirements.txt`; `CHANNEL_LAYERS` configured to an AWS ElastiCache cluster (`settings.py:~190`); `CELERY_BROKER_URL` set (`settings.py:~560`); beat schedule live in `Smartenplus/celery.py`. **Daphne IS absent** and prod runs `gunicorn==21.2.0` (WSGI) — so infra is provisioned but the realtime path is dormant.
- Pre-scan said NO Telegram integration. **Reality:** a one-way Telegram bot→group notifier exists — `send_telegram_message()` in `carts/utils.py` (hits `https://api.telegram.org/bot{token}/sendMessage`), invoked from order/payment events (`orders/notifications.py`). It is out-bound only, fire-and-forget. The thesis proposes a *bidirectional* bridge (bot reads group replies, proxied back to website chat) — that does not exist.

## Problem

The thesis treats realtime chat, omnichannel messaging, and a CS system as if they were additive features on a stack that already supports them. They are not: the support layer is installed-but-off, the data model has no conversation concept, and the one messaging integration that exists is a one-way notifier, not a sync bridge. The core technical problems are (1) activating realtime without destabilizing a WSGI prod, (2) building a conversation/message model from scratch, and (3) making a Telegram bot reliably bridge bidirectionally (message ordering, dedup, staff attribution) — and later omnichannel sync, which is the genuinely hard part.

## Details

### 1. Reuse table (Phase-1 module → existing app/field → Extend | Greenfield)

| Thesis module | Existing backend evidence | Verdict |
|---|---|---|
| **Customer (unified profile)** | `accounts.Account` (`accounts/models.py`) is the auth user; guests have NO Account — they live as `billings.BillingProfile` (`user` nullable + `guest_email`, `billings/models.py`) and `Order.email`/`phone_number` (`orders/models.py`). `FamilyAndFriend` exists. | **Extend** — Customer = alias/roll-up view over `Account` + guest `BillingProfile` keyed by email. Reuse, don't fork. |
| **Booking DB** | Already exists & mature: `bookings.BookingItem` (`bookings/models.py`) with status machine `VALID_BOOKING_TRANSITIONS`, `BookingPassengerDetail`, `BookingItemAddon`, `BookingRateCard`, linked to `orders.Order`. | **Reuse as-is** — greenfield not needed; this is the strongest existing asset. |
| **Conversation / Message / ChatSession** | None. `dialogue` app is a *forum/blog engagement* layer (`Thread`/`Post`/`Comment`/`Review`/`Reaction`/`Bookmark`/`Notification`, `dialogue/models.py`) — wrong shape for 1:1 chat, no realtime. | **Greenfield.** Reuse only the `Notification` model pattern, not the entities. |
| **CS Ticket** | Already exists: `tickets.Ticket` (`tickets/models.py`) has `ticket_number`, `assigned_to`, `is_resolved`, `ticket_status` (Active/Pending/Completed), `closed_date`, `history` (simple_history), and a `GenericForeignKey` so it can attach to a `BookingItem` (already wired: `bookings/models.py` has `ticket = GenericRelation(Ticket)`). | **Extend** — strong existing scaffold; add `Conversation` FK + status reasons. |
| **Booking-link in chat** | `BookingItem` FK is the join; `tickets.Ticket` already attaches to it generically. | **Reuse** — the GenericRelation pattern is the integration point. |

Net: of 6 phase-1 deliverables, **2 reuse as-is** (Booking DB, Booking-link), **2 extend** (Customer, CS Ticket), **only 2 are greenfield** (Conversation/Message/Session, Realtime layer). The pre-scan overstated greenfield scope.

### 2. Realtime infra build cost (the real critical path)

Current state: `requirements.txt` has Channels/Celery/Redis; `settings.py` has `ASGI_APPLICATION` + `CHANNEL_LAYERS` pointed at ElastiCache; `Smartenplus/routing.py` defines `ws/test/`; `carts/consumers.py` is a `TestConsumer` echo stub. **But** `Smartenplus/asgi.py` ships the websocket branch *commented out* (`asgi.py` ProtocolTypeRouter has only `"http"`), and prod serves via Gunicorn (WSGI) per `requirements.txt:91`. So: infra installed, path wired in code, **not activated in deployment**.

| Item | Effort | Risk |
|---|---|---|
| ASGI migration (Gunicorn→Daphne or gunicorn+uvicorn worker) | **L** | High — prod is single-vCPU burstable (see `Smartenplus/celery.py` note); ASGI worker model + connection handling on that box is a real capacity risk. |
| WebSocket auth (JWT over WS) | M | Med — must mirror `rest_framework_simplejwt`; `AuthMiddlewareStack` is session-based, not JWT. |
| Consumer + group layer for chat rooms | M | Med — `channels_redis` already in place reduces this. |
| Prod observability (broker/worker/ASGI monitoring) | M | Med — none today for WS. |
| **Overall realtime** | **XL** | This alone can consume a phase-1 cycle. |

### 3. Messaging integration cost (per channel)

| Channel | Rating | Notes |
|---|---|---|
| **Telegram bridge (bidirectional)** | **M–H** | One-way *out* already works (`carts/utils.py`). Bidirectional needs bot `getUpdates`/webhook polling, group-reply capture, **message ordering** (Telegram does not guarantee strict order under load), **staff attribution** (which staff replied?), and **dedup** (same conversation via WS + Telegram). Achievable but not a weekend. |
| **WhatsApp Business API** | **H–XL** | **24-hour customer-service window** breaks async CS — after 24h you can only send approved *template* messages, so a customer replying on day 3 silently fails unless templated. Bidirectional + dedup compounds. |
| **LINE Messaging API** | **M–H** | LINE OAuth provider already configured (`settings.py` `allauth.line`) — reduces identity work. But Messaging API has quota tiers + per-message fees; reply-vs-push distinction matters for async. |
| **Omnichannel sync + dedup** | **XL** | The genuinely hard part — unified thread identity across N channels, idempotent inbound, ordering. This is a multi-quarter capability, not a phase-3 deliverable. |

### 4. Phase-1 timeline realism

2-3 months for: Customer DB + Booking DB + Website Chat + Telegram Integration + Conversation History + CS Dashboard + Ticket System. Verdict: **NOT REALISTIC AS WRITTEN.** Booking DB and Ticket already exist (near-free). That leaves realtime activation (XL), Conversation/Message model (M-L), bidirectional Telegram bridge (M-H), and a CS dashboard (M) inside one cycle on a *single-vCPU prod that has never run ASGI*. Realistic: split phase-1 into **1a (data model + ticket extension, ~6-8 wks)** and **1b (realtime activation + website chat, ~8-12 wks)**. Telegram bridge becomes phase-2.

### 5. Stack fit

Proposed stack (Next.js + Django/DRF + Channels + Celery + Redis + PostgreSQL + S3) matches current (`requirements.txt`, `settings.py`). Channels/Celery/Redis are *standard* but add **net-new ops burden** the team does not currently operate: a broker HA story, a worker process, an ASGI server, and monitoring — none of which have run in prod here. S3 + PostgreSQL + Celery-beat are already battle-tested in this repo; the new surface is purely the realtime layer.

### Scoring per thesis claim

| Claim | Validity | Feasibility | Impact | Sequencing-realism |
|---|---|---|---|---|
| Unified Customer DB | High | High | High | Realistic |
| Booking DB | High | High (exists) | Med | Realistic |
| Website Chat (WS) | Med | Med (XL ops) | High | **Optimistic** |
| Telegram bidirectional bridge | Med | Med-H | High | Optimistic |
| Omnichannel WA/LINE/Email sync | Low-Med | Low (24h rule, dedup) | High | **Not in phase-3** |
| AI Copilot grounded on Booking DB | Med | Med | High | Phase-5 ok (far out) |

## Decision

**BUILDABLE-REVISED.** Proceed, but with three corrections: (1) phase-1 must split into a data-model phase and a realtime-activation phase because the WebSocket path is dormant and the prod box is single-vCPU; (2) the existing `tickets.Ticket`, `accounts.Account`/`billings.BillingProfile`, and `bookings.BookingItem` are the reuse spine — do not greenfield them; (3) drop WhatsApp/LINE omnichannel from phase-3 — the 24-hour window and cross-channel dedup make it a standalone multi-quarter capability, not a phase line-item. The one-way Telegram notifier that exists is a useful *out-bound* primitive but is not the bidirectional bridge the thesis needs.

## Tradeoffs

- **Reuse Customer (Account+BillingProfile) vs new Customer model:** reuse is faster and preserves payment/billing joins, but guest→authenticated identity merge is fuzzy (email-keyed, see `BillingProfileManager.get_or_new` in `billings/models.py`). Acceptable; document the merge rules.
- **Activate Channels vs add a separate realtime service (e.g. a small Node/WS gateway):** Channels keeps it in-Django (one auth/ORM), but couples realtime scaling to the single Django box. A sidecar WS service is cleaner operationally but doubles deploy surface. Recommend Channels-first given existing investment.
- **Telegram bridge vs full omnichannel first:** bridge is the cheapest credible "live chat" demo (group already receives order alerts); defer true omnichannel.

## Consequences

- Realtime activation touches deployment (`Dockerfile`, `nginx.conf`, prod process model) — not just code; it will require an infra change-window and load testing on the single-vCPU box.
- Any new Conversation/Message model must be designed for multi-channel identity from day one (channel + external_id), or omnichannel becomes a rewrite later.
- Extending `tickets.Ticket` (rather than new model) means a migration + careful handling of the existing `GenericRelation` from `BookingItem`.
- WhatsApp 24-hour window, if promised to customers in phase-3, is a *contractual* failure mode, not just a technical one — set expectations now.

## Related

[[customer-os-thesis-r3-leader-synthesis]] · [[customer-os-thesis-grill-audit]] · [[accounts]] · [[tickets]] · [[backend-architecture]]
