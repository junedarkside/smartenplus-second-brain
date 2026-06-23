---
name: smarten-customer-os-thesis
description: Decision on building the Smarten Customer OS — verdict PROCEED-REVISED, revised roadmap, re-evaluation triggers
metadata:
  type: decision
  status: under-review
  date: 2026-06-20
  parent: customer-os-thesis-review
---

# Smarten Customer OS Thesis — Decision

> 🔁 **RESCOPED 2026-06-23 → [[booking-command-centre-decision]].** Owner clarified the goal is bigger than this thesis's "CS-centralization spine": a **Unified Booking Command Centre** (control OTA+direct bookings + customer self-service requests + live trip info; chat = sub-channel). New build order (P0-P5, direct-slice first) + 3-tier consent model in the new note. This thesis's verdict (PROCEED-REVISED) + transport/OTA-store facts still hold — read with the rescope.

## Summary

> ⚠️ **Update 2026-06-20 — conversion thesis REOPENED.** The "demand-side broken at the data layer" basis for the rename/deflation is **superseded**: a standalone Supabase store ([[supabase-ota-booking-store]]) already holds **traveler email/name/phone** for ~80%+ of Klook/12Go/Bookaway bookings (parsed from OTA confirmation emails, reliable). The data r2 said didn't exist **does exist**. The make-or-break narrows from "no data" to **consent + channel-conflict + unproven rebooking economics**. The "CS Centralization" rename and CS-only deflation are **back under review**. Owner direction: keep Supabase separate + **read-sync** to the platform, **add a consent opt-in**. Details below are pre-Supabase and partially superseded where flagged.

Verdict: **PROCEED-REVISED** (spine), **scope-renamed**. Build the CS-centralization spine now (Customer roll-up, Ticket extension, Website Chat, CS Dashboard, Smart CS). Treat the "convert OTA travelers into brand users" demand-side ambition as a *measured hypothesis* (Phase 0), not an emergent outcome. **Rename the project externally AND internally to "CS Centralization"** — the r2 red-team ([[r2-skeptic-review]]) showed the demand-side conversion thesis is structurally broken at the data layer (no traveler PII; booker is often a travel agency) and P0 is a near-certain no, so "Customer OS"/"Trip Platform" overstates a moat that cannot be delivered; the spine is the real, independently-ROI-positive deliverable. The make-or-break risk is OTA-data-ownership + channel-conflict at 90%-of-volume OTA supply — NOT engineering. Reuse is **~45-55%** (r2-corrected down from ~55-60%; Customer identity, Conversation/Message, marketing-consent + source columns, the Telegram bridge, and ASGI activation are all greenfield — see [[r2-skeptic-review]], [[grill-audit]]).

## Context

Three independent specialist reviews ([[r1-strategy]], [[r1-tech-feasibility]], [[r1-product]]) of the Smarten Customer OS Thesis — a 5-phase roadmap to centralize the customer relationship OTAs (Klook/12Go/Bookaway) currently own. Demand-side complement to the supply-side [[business-development-unified-travel-wellness-thesis]]. Against the [[business]] reality: B2B supplier ~90% + B2C direct ~10%. This is the durable decision artifact; full reasoning lives in [[r3-leader-synthesis]].

## Problem

Whether to commit engineering to a 5-phase Customer OS when (a) the OTA→direct acquisition mechanic is unspecified, (b) channel conflict threatens 90% of volume, (c) the backend's realtime layer is installed-but-dormant, and (d) the phase ordering inverts identity and Customer DB. Decision needed before any build commitment.

## Details

### Corrected backend reality (good news)

Pre-scan overstated greenfield scope. Channels, Celery, Redis ARE installed+configured (`channels==4.0.0`, `celery==5.3.1`, `redis==4.5.4`, etc.; `CELERY_BROKER_URL` set; beat live). Realtime path is dormant (ASGI websocket branch commented in `asgi.py`, no Daphne) — an *activation* task, not from-scratch. ⚠️ **r2 infra corrections (verified vs source — [[r2-skeptic-review]]):** (a) ~~prod server is uWSGI / two conflicting deploy paths~~ **RESOLVED 2026-06-21 (owner-confirmed):** production = `docker-compose-rds.yml` → `gunicorn --bind :8000 --workers 1 --threads 2` (:13, `mem_limit 256m` :14). `scripts/run.sh:9` uwsgi:9000 is **dead** (nginx proxies `web:8000` only). No deploy-path ambiguity — see [[cs-architecture-decision]]. (b) `nginx.conf:2` proxies `web:8000` (matches the Gunicorn compose, NOT uWSGI `:9000`) and has no `Upgrade`/`Connection` ws headers. (c) `CHANNEL_LAYERS` hardcodes an ElastiCache hostname with no env switch (`Smartenplus/settings.py:203`), but the RDS prod path runs a LOCAL `redis:7.2-alpine maxmemory 100mb allkeys-lru` (`docker-compose-rds.yml:47-49`) — on WS activation the channel layer would talk to a *different, possibly decommissioned* redis. (d) co-resident `mem_limit`: web 256m, redis 150m — Daphne holding many persistent WS connections next to a 100MB LRU-evicting redis-as-channel-layer is a topology non-starter, and LRU eviction drops channel messages **silently** (no WS/broker observability exists). The commented `asgi.py` branch also uses `AuthMiddlewareStack` (Django session) while the API is JWT → WS auth is a rebuild, not activation. A one-way Telegram notifier exists (`send_telegram_message()` in `carts/utils.py`); the bidirectional bridge is greenfield. Reuse assets: `bookings.BookingItem` (mature status machine), `tickets.Ticket` (GenericFK to BookingItem, history — extend), `accounts.Account` (extend as Customer identity). ⚠️ `billings.BillingProfile` is NOT a safe Customer roll-up — its manager deactivates prior profiles per email on each checkout (`billings/models.py`), a churning payments identity, the opposite of "one customer"; Customer identity is effectively greenfield (see [[grill-audit]]). Greenfield: Conversation/Message/ChatSession + Customer identity. **Stack decision ([[cs-centralization-stack]]):** the realtime track ships **reuse-first** — website chat uses HTTP long-polling (reuse `hooks/useQRPolling.js`), Email-OTP uses `pyotp` + the live AWS SES, the Telegram bridge extends `send_telegram_message` + Celery. **Channels stays dormant** — none of the r2 WS work (Daphne, JWT WS auth, `CHANNEL_LAYERS` redis) is required for P1b. Net new dependency across the whole track: `pyotp` only.

### Revised roadmap (condensed)

| Step | Scope | ~Timeline | Gate |
|---|---|---|---|
| **P0** (revised — see [[supabase-ota-booking-store]]) | ~~Measure if we CAN capture OTA contacts~~ (answered: yes, 80%+ in Supabase). Now measure **do captured travelers who get a Smarten touchpoint rebook DIRECT** (the real ROI metric) + opt-in take-rate. | ~6 wks | ROI hinge |
| **P1a** | Account-lite (Google ✓ already wired / Apple new / Email-OTP via `pyotp`+SES — see [[cs-centralization-stack]]) + Customer identity (**less greenfield — Supabase stable key + profiles seed the roll-up via read-sync**, [[supabase-ota-booking-store]]) + extend `tickets.Ticket` + `source`/`origin` field migration on Order/BookingItem (grill). Draw service-vs-marketing line in data model. | 8-10 wks | — |
| **P2** | My Trip + Saved Travelers (identity-only dependency) | 4-6 wks | after P1a |
| ~~**INFRA GATE**~~ **DEFERRED** | Stack decision ([[cs-centralization-stack]]) ships P1b on **long-polling** → no Daphne/ASGI now. The r2 WS work (deploy-path conflict, `CHANNEL_LAYERS` redis, JWT WS auth, WS observability) is **deferred, not required**. Channels stays dormant. Revisit (Channels-activate vs sidecar) ONLY if measured chat volume proves polling insufficient — then it becomes its own gated project. | — | not on P1b critical path |
| **P1b** | **Website chat widget** (**polls Django every ~3-5s**, reuse `useQRPolling`) = customer channel for ALL types (direct + OTA). **CS Dashboard** (staff reply UI) **ALSO polls the same Django endpoint** (RTK `pollingInterval`) — **Postgres = single source of truth.** New Django `Conversation` + `Message` models. **Supabase is OUT of the message path** (~~Supabase Realtime `cs.messages` push · `sync_status` two-write · Django→Celery→Supabase `cs` schema · `@supabase/supabase-js` in admin~~ — all **superseded → [[cs-architecture-decision]] 2026-06-21**; the only load-bearing reason for push was a false long-poll/short-poll conflation). **Telegram = CS internal alert only** (new message/booking → staff group). **AWS SNS SMS** via `boto3` (same AWS account as SES) for trip reminders (day-before). Consent opt-in at first service-comms touchpoint. | 8-12 wks | after P2 (no infra gate) |
| **P4** | Smart CS: Quick Replies + Knowledge Base (after Ticket data matures) | — | after P1b |
| **DEFER P3** | Omnichannel (WA/LINE/Email) — per-channel only post-P0 + human WA 24h-scope decision | — | — |
| **DEFER P5** | AI Copilot — after KB has 3+ months real ticket data | — | — |
| **DROP** | WeChat, KakaoTalk (regulatory/cost vs current volume) | — | — |

### Core risk (make-or-break)

OTA-data-ownership + channel conflict. **(Supabase-revised — [[supabase-ota-booking-store]]):** the *data-existence* half of this risk is **removed** — traveler contact already exists at 80%+ via parsed OTA-confirmation emails. The conversion mechanic this ¶ said "must be designed before P1a freeze" **already runs** (email-parse → Supabase) for ops; it needs wiring to a customer touchpoint, not inventing. **What remains make-or-break:** (1) **consent** — the Supabase data is raw contact, no opt-in; (2) **channel conflict** — it is OTA-*origin* data (from their confirmation emails), so marketing to it is still supplier-poaching with delisting risk at 90% volume — **service-only-by-default still applies** until opt-in is captured at a Smarten touchpoint; (3) **rebooking economics** — having contacts ≠ proven direct rebooking, still unmeasured. Mitigation unchanged: OTA-sourced records service-only by default; marketing gated on explicit opt-in; never auto-sync to a marketing list.

## Decision

**PROCEED-REVISED.** Commit to P0 + P1a + P2 now. Build the CS-centralization spine regardless of the OTA-conversion outcome (CS-efficiency ROI is positive independently). Gate P1b/P3/P5 on Phase 0's measured OTA→account conversion rate. Reframe branding. Adopt service-only-by-default posture on OTA-sourced records. See [[r3-leader-synthesis]] for the full skeptic pass + conflict resolution.

## Tradeoffs

- **Honest branding ("Unified CS + Trip Platform") vs ambitious ("Customer OS"):** lower fundraising headline, higher delivery credibility. Chose honest.
- **Service-only-by-default vs aggressive conversion:** survival-correct but caps demand-side upside. Chose service-first; revisit if B2C direct % crosses threshold.
- **Phase 0 gate vs speed:** ~6 wks before the headline metric lands; prevents shipping a dormant Account feature on an unmeasured assumption. Chose gate.
- **Realtime transport (final — [[cs-centralization-stack]]):** neither Channels-on-box nor a sidecar now. Website chat ships on **HTTP long-polling, reusing `useQRPolling`** — free, no new process, no compose/nginx change, zero prod impact. Tradeoff: seconds-scale latency vs WS push, acceptable for CS chat. Channels left installed-but-dormant; a real-time-push need is the only trigger to revisit. (Sidecar e.g. Centrifugo was the best pure-realtime option but rejected as new infra under the no-over-engineering / no-prod-impact constraint.)
- **Identity-first vs Customer-DB-first:** adds auth scope to P1a but prevents a dedup-key rewrite. Chose identity-first.

## Consequences

- If P0 <3% OTA→account conversion: collapse scope to CS tooling (P1a/P1b/P4); kill the conversion objective and P5 AI ambition.
- If P0 5-10%: full thesis viable; expect OTA friction within 12 months — have contractual cover ready.
- Realtime activation is no longer a P1b dependency — the stack decision ([[cs-centralization-stack]]) ships P1b on **long-polling**, so the r2 failure modes (channel-layer/redis mismatch, 256MB cap + LRU redis) are sidestepped entirely until a measured real-time-push need reopens them. (Deploy-path ambiguity RESOLVED — `docker-compose-rds.yml` confirmed prod; see [[cs-architecture-decision]].)
- **Channel architecture (final):** customer chat = website widget (long-polling, all customer types); trip reminders = AWS SNS SMS (same `boto3`/AWS account, zero new dep); booking confirmation = SES email (already live); CS team = Telegram internal alert only. **WhatsApp rejected** for startup stage (BSP cost + Meta approval). Website widget = zero-friction customer channel (customer already on site).
- P1b requires two new Django models: `Conversation` + `Message` — the storage layer for website chat. Not greenfield from scratch: follows `tickets.Ticket` pattern.
- P1a field migrations (`source`/`origin`, `Conversation` FK) auto-leak through `'__all__'` serializers. **3-agent scan found 103 `fields='__all__'` serializers** (r2 estimated 16 — actual blast radius much larger). Pin explicit fields on `TicketSerializer` (`tickets/serializers.py:55`) — the **sole confirmed `__all__` example** — BEFORE any P1a migration. (D1 correction [[cs-centralization-doc-review]]: `OrderSerializer:94` is **already explicit fields**, not `__all__`; earlier text removed.) P1a is a **3-repo contract change**, not backend-internal.
- `dialogue/` app GenericFK pattern (`dialogue/models.py` Comment/Notification/Review) — reuse as template for `Message` model. Don't reinvent the FK structure.
- ~~`@supabase/supabase-js` enters **admin-dashboard only** when P1b builds.~~ **SUPERSEDED → [[cs-architecture-decision]] 2026-06-21:** both-sides-poll-Django means **no Supabase client in any repo** — both `smartenplus-frontend` widget AND admin-dashboard CS Dashboard poll Django. Net new FE dep on the message path = none.
- Frontend cost is INVERTED vs the original assumption: My Trip (`pages/bookings/`, `pages/orders/`), Saved Travelers (`PassengersList.js`), and 3-of-4 OAuth providers already ship → P2 ≈ rebrand-and-wire. Real frontend cost concentrates in **Email OTP** (greenfield both ends) + the **chat widget** (`useQRPolling` is not a reusable transport).
- Email-keyed Customer merge will be probabilistic (strategy expects 20-40% noise); document merge rules; do not promise deterministic "One Customer."

## Grill Audit Corrections (post-synthesis)

The grill pass ([[grill-audit]]) verified specialist backend claims against source and caught 3 material corrections the synthesis normalized away. These adjust P1a scope + estimates above:

1. **Service-only-by-default mitigation is unenforceable as written.** `Order` (`orders/models.py`) and `BookingItem` (`bookings/models.py`) have **no `source`/`origin` field** — nothing distinguishes an OTA booking from direct. The OTA-quarantine mitigation depends on a column that does not exist. → `source` migration + backfill is a required P1a deliverable (added to table above).
2. **`BillingProfile` cannot be the Customer roll-up.** Its manager deactivates prior profiles per email on each checkout = churning identity. Customer identity is greenfield, not extend. Real reuse drops to ~55-60%; P1a revised 6-8w → **8-10w**.
3. **`BookingPassengerDetail` has no email/phone** — the only contact PII lives on `Order.email` (the *booker*, frequently a travel agency), not the *traveler*. The OTA-acquisition gap is wider than every reviewer assumed: even captured passengers lack a contact channel. Re-opens the Phase-0 conversion-rate ceiling.

Consensus verdict (PROCEED-REVISED) **stands**; P1a is under-scoped, not wrong.

## Status

**Under review — PROCEED-REVISED, pending Phase 0 measurement.** P0 + P1a + P2 cleared to start. P1b ships on long-polling (no infra gate — see [[cs-centralization-stack]]). P3/P5 deferred pending P0.

## Re-evaluation Triggers

Revisit this decision when ANY of the following occurs (concrete + measurable):

1. **Phase 0 result** (~6 wks): OTA→account conversion <3% → collapse to CS tooling, defer P2 retention loop + P5. >5% → proceed to P3/P5 planning. (Set the exact threshold before P0 starts.)
2. **B2C direct % crosses ~20%** (from current ~10%): channel-conflict math changes; revisit service-vs-marketing posture.
3. **OTA data-sharing policy change** (Klook/12Go/Bookaway begin passing PII/consent, OR tighten anti-poaching terms): directly reopens or closes the demand-side thesis.
4. **After P1a ships**: validate Customer merge noise; if >40%, identity resolution becomes a P3 rewrite.
5. **Realtime gate fails load test**: re-evaluate Channels vs sidecar; may force P1b scope cut (ship Dashboard + Telegram, defer Website Chat).
6. **Any OTA contractual warning/delisting signal**: halt OTA-sourced retention outreach immediately; re-evaluate the entire demand-side track.

## Open Questions

Decisions only a human can make — resolve before/at the relevant gate:

1. **Branding** — ~~RESOLVED (r2): rename to "CS Centralization"~~ → **REOPENED (Supabase, [[supabase-ota-booking-store]]):** the rename was justified by "conversion undeliverable"; traveler data now exists at 80%+, so the moat case is live again. Re-decide once revised-P0 rebooking economics land.
2. **Channel-conflict appetite** — service-only-by-default (survival-correct) vs aggressive retention outreach (max conversion, delisting risk)?
3. **WhatsApp 24h customer-service-window scope** — which use cases are "service" (tolerated) vs "marketing" (forbidden after 24h)? Legal/product call before P3.
4. **Phase 0 metric threshold** — exact OTA→account conversion % that continues vs collapses the thesis (strategy suggests 3% floor / 5-10% go).
5. ~~**OTA identity-claim mechanic** — pick before P1a freeze?~~ **Largely ANSWERED (Supabase):** the capture pipeline already runs (OTA-email parse → Supabase, 80%+). Remaining: wire it to a customer touchpoint (service comms) + attach opt-in. Not "design from scratch."
6. **Supabase sync scope** — read-only mirror into the platform vs deeper integration? (Owner: keep separate + read-sync via Supabase REST/JS API. Confirm fields + refresh cadence + the Supabase↔Django identity merge key.)
7. **Consent step** — where/how to add the marketing opt-in on the service-comms touchpoint (owner: yes, add). Legal wording + storage of the consent flag.

## Related

- [[r1-strategy]] · [[r1-tech-feasibility]] · [[r1-product]] — specialist reviews
- [[r3-leader-synthesis]] — round-1 skeptic pass + ranking + verdict
- [[r2-skeptic-review]] — **round-2 4-agent red-team** (source of the rename + infra-gate rescope applied above)
- [[grill-audit]] — contradictions, fuzzy terms, edge cases
- [[r3-leader-synthesis]] — parent review synthesis
- [[business]] · [[business-development-unified-travel-wellness-thesis]] · [[business-development-thesis-2026-2029]] — strategic context
- [[accounts]] · [[tickets]] — backend reuse assets
- [[cs-centralization-stack]] · [[cs-architecture-decision]] · [[cs-consent-gdpr-model]] · [[cs-p0-measurement-protocol]] — CS-centralization children (build stack, transport ADR, consent model, P0 protocol)
- [[cs-centralization-review-2026-06-22]] — integrity review of this cluster
