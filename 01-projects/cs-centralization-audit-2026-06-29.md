# CS-Centralization Deep Audit — 2026-06-29

> **Status:** AUDIT COMPLETE · 10 new criticals found · gap report 2026-06-27 SUPERSEDED
> **Readiness verdict:** NOT PRODUCTION-READY — 10 Tier-1 blockers, signals dead, beat absent
> **Related:** [[cs-centralization-gap-report-2026-06-27]] (superseded) · [[cs-workflow-revised-2026-06-27]]

---

## 1. Summary

**Method:** 6 Explore agents (2 passes × 3 repos) + 6 direct file reads (`tickets/apps.py`, `celery.py`, `tasks.py`, `views.py`, `cs/urls.py`, `cs/admin.py`). All claims source-verified with `file:line`.

**4 ways the 2026-06-27 gap report is stale:**
1. Chat (Surface 1) + Email-OTP (Surface 3) built 2026-06-23 — unreported
2. BE-B2/B4/B5 shipped between gap-report and this audit — were "MISSING BLOCKER"
3. NEW-1 resolve-block guard now functional via API — was listed as "dead code"
4. 3 of 4 admin mutations now backed by BE (Sync Now, Record OTA Contact, Emergency toggle)

**10 new criticals found** (missed entirely by gap report — below).

---

## 2. Tier 1 — Critical / Blocker

| # | Finding | File:line | Spec ref |
|---|---------|-----------|----------|
| 1 | **Resend emits dead token.** `OtaResendMagicLinkView` builds `?token={booking.magic_token}` (raw UUID); `OtaTripView` validates via `load_ota_trip_token` (HMAC-signed) → always `TOKEN_INVALID`. `OtaTripLinkView` (Copy Link) uses `make_ota_trip_token` correctly — only Resend is broken. Test `test_cs_gaps.py:150-156` locks in bug (asserts UUID, never validates it). | `cs/views.py:595` vs `:464`; `cs/tokens.py:34-47` | OQ-6 |
| 2 | **No one-open-ticket guard.** `CustomerTicketViewSet.create` + `OtaChangeRequestView.post` both create unconditionally. `Ticket.clean()` has no dup check; neither create view calls `full_clean()`. Customer can open multiple tickets per booking. | `tickets/views.py:203-230`; `cs/views.py:527-567` | FIX B-2 / M-6 |
| 3 | **`tickets/signals.py` never imported.** `tickets/apps.py` has no `ready()` method — all signal handlers (email on resolve/reject/closed_no_action, manifest push, admin-initiated email) are dead code. Every other app (`products`, `operators`, `bookings`, `dialogue`, `orders`) has `ready()`. Zero customer emails ever fire. | `tickets/apps.py:1-7` | M-7, NEW-3, NEW-10 |
| 4 | **Magic link fixed-7d, not trip-date based.** `OTA_TRIP_TOKEN_MAX_AGE=604800`. No `is_magic_link_valid`, `magic_token_generated_at`, or `auto_send_magic_link` on model. Link issued Day 1 for a trip on Day 50 = dead link 7 days in. Admin email template literally reads "expires in 7 days". | `cs/tokens.py:7`; `cs/models.py:105-162` | OQ-6 BLOCKER |
| 5 | **Resolution side-effect absent.** Resolving a cancellation ticket sets `ticket_status='Completed'` but never sets `BookingItem.booking_status='Canceled'` (direct) or `CsOtaBooking.status='canceled'` (OTA). Every resolved cancellation is a data lie; `cancelled_complete` state unreachable. | `tickets/views.py:278-281` | FIX B-4 |
| 6 | **`trip_id` missing on `CsOtaBooking`.** Emergency fanout (`send_emergency_customer_notifications`) + manifest push (`push_manifest_on_resolution`) both do `getattr(...,'trip_id',None)` → None → silent no-op on every OTA ticket. | `cs/models.py:105-160`; `tickets/tasks.py:19`, `signals.py:67` | NEW-4, NEW-10 |
| 7 | **Beat schedule missing both CS tasks.** `beat_schedule` has only products/bookings/payments tasks. `sync_ota_bookings` (≤15min spec) and `check_sla_breaches` (hourly) never run. Only on-demand Sync Now works. | `Smartenplus/celery.py:24-58` | Sync § |
| 8 | **`closed_no_action` unreachable via API.** `RequestStatusViewSet.partial_update` never reads `resolution_note` from request body; `Ticket.clean()` requires it for `closed_no_action`. Test masks this by pre-seeding the note directly on the instance. | `tickets/views.py:243-245` | NEW-14 |
| 9 | **OTP grants full-account JWT.** `OtpVerifyView` issues `RefreshToken.for_user` → 24h access + 7d refresh token for the WHOLE site, not chat-scoped. Throttle is coarse (5/hr, no spec'd 60→120→300s backoff). OTP-blasting a known email = easiest account takeover path. | `cs/views.py:312-318`; `settings.py:420` | security / NEW-3 |
| 10 | **`requested_value` accepts unbounded arbitrary JSON.** No per-`request_type` schema, no size cap. Raw value stringified into `description` and echoed into operator emails via (dead) manifest signal. | `tickets/views.py:219,227`; `cs/views.py:556,565` | data-model § |

---

## 3. Tier 2 — Major

| Finding | Evidence |
|---------|----------|
| `cs_chat` FeatureFlag not seeded; fail-open both layers (`get_or_create` default-True; `useFeatureFlag.js` fail-open). Kill switch inert without manual DB PATCH. | `cs/views.py` FeatureFlagView; `hooks/useFeatureFlag.js` |
| `check_sla_breaches` runtime NameError: `ticket_number` (singular) undefined, `if 1` always-truthy; outer try/except swallows → silent fail every run. | `tickets/tasks.py:141,165` |
| `calculate_sla_deadlines()` has zero production callers (tests only). SLA fields always NULL → ETA display broken. No business-hours logic (6am-10pm); SLA is wall-clock 24/7. | `tickets/tasks.py` |
| `in_review → resolved` bypasses resolve-block guard. Guard only fires on `awaiting_ota_update → resolved`. Direct resolve from `in_review` has no OTA-contact check. | `tickets/views.py:258-275` |
| `OtaResendMagicLinkView` sends no email (misnamed). NEW-6 magic-link email template (Klook branding + WhatsApp footer) absent entirely. | `cs/views.py:590-600` |
| `ConversationCreateView` broken for authed users — `get_or_create` + `MultipleObjectsReturned` 500 risk if ≥2 open/pending convs exist. No test covers authed branch. | `cs/views.py` |
| `supabase_row_id` not `unique=True`. Spec requires global uniqueness; latent dup risk once a writer populates it. | `cs/models.py` |
| OQ-8 PII housekeeping entirely missing: no `pii_purge_after`, no purge task, no portal privacy notice. | — |
| `OtaBookingEvent` + `TripNotification` unregistered in Django admin → audit log + notifications invisible to operators. | `cs/admin.py:1-43` |
| NEW-11 supersede modal + NEW-12 bulk close confirmed absent in admin-dashboard. | `pages/cs/` |
| FE: `InfoUpdateNotice` (FE-M1) missing; chat a11y gaps (no `role=dialog`, `aria-live`, focus-trap, `aria-expanded`); OTP missing `autocomplete="one-time-code"`; i18n zero. | FE `components/cs/` |
| WCAG: admin status chips color-only (design-concept violation); `OtaPdpaGate.js:53` + `ChatPanel.js:64` use `gray400` as body text (fails AA). | admin `components/cs/`; FE |

---

## 4. Tier 3 — Quality / Ops

- `ticket_status` (Active/Completed/Pending) still written in parallel to `request_status` — real dual-systems bug, not legacy artifact.
- `set_logs` CharField never removed → double-logging with `OtaBookingEvent`; `max_length=100` truncates.
- N+1 on Ticket list: GenericFK `content_object` fetched per row, no `prefetch_related`.
- `OtaBookingListView` unpaginated (returns all rows). `sync_ota_bookings` full-table fetch every run (no since-cursor → Supabase egress cost). Celery concurrency=1 + 840s soft-time-limit blocks only worker.
- `seed_ota_fake_data` calls `CsOtaBooking.objects.all().delete()` — orphans GenericFK-linked tickets.
- `CustomerTicketViewSet.create` never calls `clean()` — future paths with client-supplied status skip validation.
- Tests: signals / SLA-breach / SLA-on-create / cancellation-side-effect all untested (consistent with being dead/absent).

---

## 5. Layer Map — BUILT vs MISSING

### Backend (BE)

| Component | Status |
|-----------|--------|
| Ticket model + 6 statuses + GenericFK | ✅ BUILT |
| OtaBookingEvent (append-only audit log) | ✅ BUILT |
| TripNotification model | ✅ BUILT |
| CsOtaBooking + Supabase sync task | ✅ BUILT |
| HMAC magic-link tokens (`make/load_ota_trip_token`) | ✅ BUILT |
| RequestStatusViewSet (admin fields: emergency, OTA contact) | ✅ BUILT |
| HOTP OTP (CSOtp model, verify endpoint) | ✅ BUILT |
| Resolve-block guard in clean() | ✅ BUILT |
| `tickets/signals.py` handlers | ✅ BUILT but DEAD (no `ready()`) |
| SLA deadline calculation | ✅ BUILT but NEVER CALLED in prod |
| Celery beat — CS tasks | ❌ MISSING |
| Resolution booking-status side-effect | ❌ MISSING |
| One-open-ticket guard | ❌ MISSING |
| Magic link trip-date TTL | ❌ MISSING |
| `trip_id` field on CsOtaBooking | ❌ MISSING |
| PII purge task | ❌ MISSING |

### Frontend (FE)

| Component | Status |
|-----------|--------|
| ChatWidget + useChatPolling (Surface 1) | ✅ BUILT |
| Email-OTP login chat-login.js (Surface 3) | ✅ BUILT |
| OtaPdpaGate | ✅ BUILT (exceeds spec) |
| TicketStatusBanner + my-trip integration | ✅ BUILT |
| /my-trip conditional poll (60s gate) | ✅ BUILT |
| OtaRequestCard | ✅ DELETED (dead code removed) |
| InfoUpdateNotice (FE-M1) | ❌ MISSING |
| chat a11y (role/aria-live/focus-trap) | ❌ MISSING |
| OTP `autocomplete="one-time-code"` | ❌ MISSING |
| i18n (all CS strings hard-coded EN) | ❌ MISSING |

### Admin Dashboard

| Component | Status |
|-----------|--------|
| ConversationList + ConversationDetail (chat inbox) | ✅ BUILT |
| Command Centre (SupabaseSyncBanner, SLA display) | ✅ BUILT |
| Emergency toggle → `request-status/` | ✅ BUILT (fixed #186) |
| Record OTA Contact mutation | ✅ BUILT |
| Sync Now → `ota/sync/` | ✅ BUILT |
| Resend Email | ❌ BROKEN (Tier-1 #1: dead token) |
| Supersede modal (NEW-11) | ❌ MISSING |
| Bulk close (NEW-12) | ❌ MISSING |
| OtaBookingEvent visible in admin | ❌ MISSING (not registered) |
| TripNotification visible in admin | ❌ MISSING (not registered) |

---

## 6. Cross-Layer Reconciliation

**Admin ↔ BE dependency map (post-#186):**

| Admin button | BE endpoint | Status |
|---|---|---|
| Sync Now | `POST ota/sync/` | ✅ Working |
| Record OTA Contact | `PATCH request-status/{id}/` | ✅ Working |
| Emergency toggle | `PATCH request-status/{id}/` via `setEmergencyFlag` | ✅ Working (#186 fixed) |
| Resend Email | `POST ota/resend-magic-link/` | ❌ Returns dead UUID token |

**Resolve-guard end-to-end trace:**
1. `RequestStatusViewSet.partial_update` → calls `instance.clean()` ✅ (#186 wired)
2. `clean()` checks `awaiting_ota_update → resolved`: OTA-contact timing guard ✅ FUNCTIONAL
3. `clean()` on `in_review → resolved`: **NO guard** — bypass hole exists
4. On resolve: customer email → signal handler → **NEVER FIRES** (signals dead, Tier-1 #3)
5. On resolve cancellation: booking status → **NEVER UPDATES** (Tier-1 #5)

---

## 7. Security Findings

| Risk | Finding | Severity |
|------|---------|----------|
| Account takeover | OTP verify issues full-site JWT (access+refresh) for any email address known to attacker | HIGH |
| Data injection | `requested_value` accepts unbounded freeform JSON echoed into emails | MEDIUM |
| Duplicate tickets | No one-open-ticket guard → state confusion, audit trail corruption | MEDIUM |
| Stale portal access | Magic link never expires based on trip date → guest accesses booking data forever | MEDIUM |
| Kill-switch inert | `cs_chat` FeatureFlag fail-open — cannot disable chat without DB access | LOW |

---

## 8. Reconciliations + Extras

**What the gap report got wrong:**
- Declared admin mutations "DEAD UI" for Sync Now / Record OTA Contact / Emergency toggle — all 3 now functional (#186)
- Missed all 10 Tier-1 criticals above
- Declared NEW-1 resolve-guard "dead code" — it's functional via API (#186 wired)
- Chat inbox FE "NOT FOUND": gap report agent searched wrong repo. Chat inbox lives in **admin-dashboard** (`pages/cs/`, `components/cs/ConversationList.js`, `ConversationDetail.js`). End-to-end functional.

**Code that exceeds spec:**
- `OtaPdpaGate`: full PDPA consent gate with once-per-token localStorage (spec had one-liner)
- `useChatPolling`: backoff/jitter/429-handling/page-visibility resilience
- Chat kill-switch: graceful degrade + duplicate-open guard
- Emergency ticket UI: full toggle + banner

---

## 9. Recommended Fixes (reuse-first, scoped)

Fix philosophy: root cause only, simplest change, reuse existing code, zero blast radius.

| Priority | Fix | Approach | Files | Blast radius |
|----------|-----|----------|-------|--------------|
| P0 | Resend dead token | Call existing `make_ota_trip_token(booking)` instead of `booking.magic_token`; fix test assertion | `cs/views.py:595`, `cs/tests/test_cs_gaps.py:150-156` | 1 view + 1 test |
| P0 | Signals dead | Add `ready()` to `TicketsConfig` importing `tickets.signals` — mirrors `products/apps.py:8` pattern | `tickets/apps.py` (+2 lines) | Registers existing handlers only |
| P0 | Beat schedule absent | Add `cs.sync_ota_bookings` (15min) + `tickets.check_sla_breaches` (hourly) to existing `beat_schedule` dict | `Smartenplus/celery.py` (+6 lines) | Config only; tasks already idempotent |
| P0 | SLA NameError | Replace `ticket_number if 1 else …` with already-defined `ticket_numbers` var | `tickets/tasks.py:141,165` | 2 lines |
| P1 | `closed_no_action` unreachable | Extract `resolution_note` from request body — same pattern as existing `admin_contacted_ota_*` extraction | `tickets/views.py` (+1 line) | 1 view |
| P1 | One-open-ticket guard | Add check to existing `Ticket.clean()`; call `full_clean()` in both create views; reuse GenericFK already on model | `tickets/models.py`, `tickets/views.py:203`, `cs/views.py:527` | Additive guard; no valid flow broken |
| P1 | Resolution side-effect | On `resolved`+`cancellation`, set booking status via existing `ticket.ota_booking` property (OTA) or `content_object` (direct), null-safe | `tickets/views.py:278` | 1 guarded branch |
| P1 | Magic link trip-date TTL | Add `is_magic_link_valid` property reusing existing `booking_date` field (trip_date+7d); `OtaTripView` checks after HMAC | `cs/models.py` (+property), `cs/views.py:464` (+1 guard) | No token-format change |
| P2 | `requested_value` validation | One `validate_requested_value(request_type, value)` helper; called in both create views | new helper + 2 views | Additive; rejects invalid only |
| P2 | OTP JWT scope | Drop 7d refresh token from `OtpVerifyView` — minimal exposure cut (full scope-down = product decision) | `cs/views.py:312-318` | 1 view; reduces token lifetime only |
| P2 | `trip_id` field | Add nullable `trip_id` + migration; fanout/manifest tasks already guard None | `cs/models.py`, migration | Additive nullable field |

**Deferred (needs product decision, not code):** NEW-6 email template, NEW-11 supersede modal, NEW-12 bulk close, NEW-7 i18n, FeatureFlag seeding, auto-send-magic-link, chat↔ticket cross-link.

---

## 10. Related

- [[cs-centralization-gap-report-2026-06-27]] — superseded by this audit
- [[cs-workflow-revised-2026-06-27]] — north-star spec; partially closed, new defects found
- [[admin-dashboard-cs-centralization-plan]] — Phase 1+4 on develop; Phase 2-3 pending
- [[cs-centralization-blockers-implementation]] — #186 implementation record
- [[django-signals-ready-import-gotcha]] — atomized lesson (Tier-1 #3)
- [[genericfk-one-open-ticket-guard]] — atomized pattern (Tier-1 #2)
