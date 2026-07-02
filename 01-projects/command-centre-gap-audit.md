# Command Centre Gap Audit (3-Agent BE/FE/Integration)

## Summary
2026-07-02 failure-mode audit of Booking Command Centre across all 3 repos. 3-agent team (Backend / Admin FE / Integration). **7 CRITICAL, 9 HIGH** findings. Core theme: large parts of the designed workflow (SLA, emergency notify, operator manifest, resolution emails for direct customers) are **dead code that looks alive** — UI renders, models have fields, tasks exist, but nothing wires them together. Top CRITICAL claims verified against live code by leader (no hallucinated refs).

## Context
Follows [[command-centre-ticket-booking-flow]] (2026-06-24 audit) and [[cs-centralization-audit-2026-06-29]]. Known issues excluded from this audit: resolve-doesn't-apply-change disconnect, public order-detail endpoint, ignored `is_emergency`/`admin_initiated` query params (chips removed + commit `ce873f9` same day).

## CRITICAL

### C1 — PUT bypasses request_status state machine ✅verified
`tickets/views.py:243` — `RequestStatusViewSet(GenericViewSet, UpdateModelMixin)` overrides only `partial_update`; `PUT` falls through to default DRF update: no `VALID_REQUEST_TRANSITIONS` check, no `clean()`. `TicketSerializer` has **no `read_only_fields`** — `request_status`, deadlines, `resolved_by` all writable. Same hole on `TicketViewSet` PUT. Resolved tickets re-openable, audit fields forgeable.
**Fix:** `http_method_names=['patch']` + mark workflow fields read-only.

### C2 — Entire SLA machinery is dead ✅verified
`tickets/models.py:189` `calculate_sla_deadlines()` has **zero callers** outside tests (grep verified). All 4 deadlines permanently NULL. `resolution_stage` never advanced — stuck at `'ack'` forever. Cascade: `check_sla_breaches` beat task matches nothing → SLA alerts never fire; admin SLA countdown UI (built 2026-07-02) always falls back to raw age; customer `SLAProgress` never renders.
**Fix:** call `calculate_sla_deadlines()` in all 4 ticket-creation paths; advance `resolution_stage` on transitions.

### C3 — Guest chat token minted with zero verification ✅verified
`cs/views.py:91-108` `ConversationCreateView` (AllowAny): POST any email → returns valid `guest_token` for that email's existing conversation, **no OTP**. Attacker reads any guest's support history + sends messages as them. OTP flow exists but this endpoint bypasses it.
**Fix:** no token for pre-existing conversation without OTP.

### C4 — No email backend configured; every ticket email silently no-ops ✅verified
No `EMAIL_BACKEND`/`EMAIL_HOST` in settings (grep verified) → Django defaults to SMTP localhost:25. All ticket sends use `fail_silently=True` + `print()`. Admin-initiated, resolution, SLA, emergency emails all vanish. (CS OTP works — calls boto3 SES directly, bypassing Django mail.)
**Fix:** SES-backed `EMAIL_BACKEND`; drop `fail_silently`, log failures.

### C5 — "Resend magic link" never sends anything ✅verified
`cs/views.py:665-683` `OtaResendMagicLinkView` mints link and **returns it in the response**; zero `send_mail` in the cs app. Admin FE (`command-centre/index.js:518-524`) discards response body, shows green success. Staff tells customer "sent"; customer gets nothing.
**Fix:** send server-side, or surface `trip_link` for manual copy.

### C6 — OTA resolve gate unconditionally bypassed + no audit trail
FE sends `ota_manually_confirmed: true` on **every** OTA resolve (`command-centre/index.js:139`); backend `_ota_manually_confirmed` is transient, never persisted — no record of who claimed manual confirmation. Supabase resolve-block guard (Blocker 1) is dead code for command-centre workflow.
**Fix:** persist `ota_manually_confirmed_at/by`; FE explicit checkbox, not hidden flag.

### C7 — Admin-initiated direct tickets invisible to customer in-app
`cs/views.py:903-916` creates ticket with `created_by=admin`; customer feed filters `created_by=request.user` (`tickets/views.py:196`) → never matches. Customer FE `AdminInitiatedBanner` is dead UI for direct bookings. Only signal is one plain-text email — which doesn't send (C4).
**Fix:** customer queryset filter on booking ownership, not `created_by`.

## HIGH

- **H1 — `ticket_number` not unique, not indexed** (`models.py:40`) yet is `lookup_field` on 3 viewsets. Duplicate → `MultipleObjectsReturned` 500; every lookup seq-scans.
- **H2 — Zero concurrency control.** No `select_for_update`/`transaction.atomic` anywhere in tickets/cs. Two staff resolve same ticket → double side-effects, duplicate emails.
- **H3 — One-open-ticket guard TOCTOU-only.** `clean()` `exists()` check, no conditional `UniqueConstraint`. Double-submit → two open tickets per booking.
- **H4 — Emergency notify task never dispatched** (grep: zero `.delay()` callers ✅verified). Toggle sets boolean, nothing else. NEW-4 Part D unimplemented.
- **H5 — Operator manifest push is `print()` placeholder** (`signals.py:100-103`; `tasks.py` send commented out). Resolved pax/cancel changes never reach operators. Also fires on every save of resolved ticket, not on transition — will spam once wired.
- **H6 — Resolution email re-sent on every terminal-ticket save** (`signals.py:113` checks state not transition). Note edit on resolved ticket → duplicate "Cancellation Confirmed" (once C4 fixed).
- **H7 — Direct customers never get resolution email even with backend fixed.** `signals.py:116-121` recipient = `guest_email` (never set for direct) → `content_object.email` (BookingItem has none) → silent return. `created_by.email` never consulted.
- **H8 — OTA my-trip never shows `resolution_note`.** `OtaTripView` `tickets_data` omits it (`cs/views.py:522-536`); customer FE renders it when present — dead. Rejected = "Not Approved" with no reason.
- **H9 — Admin ticket detail reads `latest_ota_event_at` — field doesn't exist anywhere in backend** (grep: zero hits). "No Supabase events yet." always shown → staff pushed toward C6 bypass.

## Admin FE (session/scale/UX)

- **FE-C1 — Hard refresh bounces staff to sign-in.** `useSession()` null during `loading`; page redirects before session resolves (`command-centre/index.js:1000-1007`). Deep links unusable.
- **FE-C2 — All 3 tabs fetch unpaginated full tables** (`Ticket.objects.all()`, `BookingItem.objects.all()`, N+1 nested serialization, no virtualization). Freezes at production scale.
- **FE-C3 — Ticket detail blank page on any fetch failure** (`[id].js:110-121` — catch → `return null`).
- **FE-H1 — Cross-slice cache gap:** `csApi` mutations touch Ticket data but can't invalidate `ordersApi`'s `'Ticket'` tag (separate slices). Created ticket invisible in Direct Requests until full reload (tabs use `display:none` — never remount).
- **FE-H2 — No polling + SLA countdown frozen** (computed once per render, no tick). Two staff → stale queue, duplicate work.
- **FE-H3 — `resolutionNote` leaks across tickets** (not cleared on ConfirmDialog close / Open Editor path) and is sent on non-terminal transitions — wrong customer-visible text on wrong ticket.
- **FE-M1 — Emergency `pending→resolved` fast-path unreachable from UI** (FE `VALID_TRANSITIONS` lacks it; BE allows when `is_emergency`).

## Medium (selected)
- `resolved_by` never set — audit field permanently null.
- `TicketSetStatusViewSet` accepts arbitrary `ticket_status` strings; exposes full ModelViewSet surface.
- `Ticket.clean()` skipped by `TicketViewSet.create`, `TicketSetStatusViewSet`, all PUTs, Django admin.
- SLA task: no retry, no dedup (re-alerts hourly forever), no terminal-status exclusion, `except: print()`.
- `admin_contacted_ota_at` client-supplied + never mandatory before `awaiting_ota_update`.
- `OtaChangeRequestView` skips `is_magic_link_valid` gate — stale tokens create tickets on past bookings.
- Reopen via `ticket_status: 'Active'` desyncs from request workflow — reopened ticket can never transition.
- Magic-link token in URL query string → server logs/history; signed not encrypted; no revocation.
- OTP verify issues full-scope JWT ("chat-only" comment is false).
- FE: mutations have no 401 re-auth handling; notification delete has no confirm.

## Recommended fix order
1. **Security triad:** C3 (guest token), C1 (PUT bypass), C6 (bypass audit trail)
2. **Email foundation:** C4 (backend config) — unblocks C5, C7, H6, H7 fixes
3. **SLA wiring:** C2 + resolution_stage advancement (makes today's SLA UI real)
4. **Scale:** FE-C2 pagination before ticket volume grows
5. **Data integrity:** H1 unique constraint, H2 locking, H3 constraint — one migration batch

## Related
[[command-centre-ticket-booking-flow]] · [[booking-command-centre-decision]] · [[cs-workflow-revised-2026-06-27]] · [[cs-centralization-audit-2026-06-29]] · [[command-centre-direct-notify-redesign]]
