---
name: ota-portal-review
description: 3-agent team review of the OTA portal phased plan (P2–P3c). Backend + Frontend + Architect specialists. Verdicts, blockers, open Qs, and per-phase approval status. Produced 2026-06-23.
metadata:
  type: review
  status: complete
  date: 2026-06-23
  parent: ota-portal-overview
---

# OTA Portal — Team Review (2026-06-23)

3-agent read-only review of [[ota-portal-overview]] + 4 phase notes. No implementation started. Findings below feed the owner decision on what needs resolving before build begins.

---

## Backend Review (P2 + P3b)

### P2 — OTA Sync: Supabase Mirror

**Verdict: Needs clarification** — upsert key must be confirmed before migration is written; see Q1 below.

**Risks missed by the plan:**
- **PostgREST pagination** — bare `?select=*` returns Supabase's default page limit (typically 1,000 rows). 561 rows safe today; silent truncation at scale. Sync task needs pagination loop or assertion `len(fetched) < SUPABASE_PAGE_LIMIT`.
- **Anon-key rotation path** — no documented remediation if key is compromised (cache bust, worker restart, health-check).
- **View schema drift** — `view_information` is a view, not a table. Column additions/renames silently corrupt the upsert. Assert sentinel fields (`booking_id`, `source`) present on every row before persisting.
- **Concurrent invocation** — parallel workers racing on `(source, booking_id)` = misleading log counts. One-line `cache.add` lock or `SELECT FOR UPDATE SKIP LOCKED` sentinel.
- **Unknown `status` strings** — plan normalizes `✅Confirmed` / `❎Canceled` but Klook/12Go likely have `Pending`, `Refunded`, empty. Unknown values land with null `status` silently. Add a quarantine path.
- **No staleness signal** — silent sync failure leaves stale mirror with no alert. Write last-success timestamp to `CsSyncLog` (single-row upsert).
- **Field naming** — `supabase_ingested_at` is ambiguous. Rename to `django_synced_at`.

**Q1 — Upsert key: `(source, booking_id)` or `booking_id` alone?**
`(source, booking_id)` is correct. Bookaway shares the `12GO*` prefix with 12Go — `booking_id` alone is not globally unique across sources. Use `unique_together = ('source', 'booking_id')` as planned.

**Q2 — Manual batch vs Beat from day 1?**
Manual batch first. With 561 records and no SLA on freshness (no customer-facing surface until P3a), Beat is overhead with no return. Write the Celery task now so Beat can be enabled with one `CELERY_BEAT_SCHEDULE` entry later. No refactor needed.

**Q3 — Standalone `CsOtaBooking` vs denormalize into `Order`?**
Standalone. OTA bookings have a different state machine (SmartEnPlus cannot mutate them). Denormalizing into `Order` contaminates the direct-order state machine and makes the quarantine boundary invisible.

**Blockers before P2 build:**
1. Confirm anon-read RLS on `view_information` is active — verify with a `curl` against anon key before any code is written.
2. Decide pagination strategy (loop vs assertion) before `sync_ota_bookings` is written.

**Approved:** `(source, booking_id)` unique constraint · standalone `CsOtaBooking` · data-quality exclusions (`N/A`, `5000-08-02`, CRLF strip) · `email db_index=True` · no write-back to Supabase · management command + Celery task dual entry · probabilistic merge documented as 20–40% with no deterministic promise.

---

### P3b — OTA Request Submit

**Verdict: Blocked** — `Ticket.created_by` is a non-nullable FK to `User`; OTA-guest requests have no valid attachment point until this is resolved in P1.

**Risks missed by the plan:**
- **`requested_value` free-text is wrong for staff relay.** Staff copy/paste to OTA portal needs machine-readable fields per `request_type` (`{"new_date": "...", "pax": 3}`). Decide JSON schema per type before serializer is written.
- **`Ticket` OTA FK tension.** If P1 adds `order = FK(Order, null=False)`, OTA requests cannot reuse the model without making `order` nullable or adding `ota_booking = FK(CsOtaBooking, null=True)`. Flag to P1 author now — retrofitting after migration is expensive.
- **`relay-to-OTA` state has no defined terminal.** After staff relay, the ticket sits in `relay-to-OTA` until staff manually resolves. Define the post-relay state (e.g., `pending-ota-confirmation → resolve`).
- **Email on every transition = noise.** Internal staff-to-staff steps should not trigger traveler emails. Add `notify_traveler: bool` per transition in `VALID_TRANSITIONS`.
- **OTA-guest duplicate request abuse.** Reopen abuse-guard ties to account history; OTA guests identified by magic-link only. Guard must check for open request on the same `CsOtaBooking`, not account-level history.
- **Guest sender model undefined.** When no `Account` exists, what Django model is the OTA-guest sender on the Ticket? Ephemeral object, `GuestProfile` FK, or resolved-to-`Account` on email match only? Must be decided.

**Q4 — OTA request types P1 taxonomy doesn't cover?**
P1's three types (change-date, change-pax, cancel) are insufficient. Confirmed gaps: `change-vehicle-type` (12Go `vehicle_type` field confirmed in P2 model), `change-pickup-point`, `general-inquiry` (catch-all), `refund-request`. Recommendation: confirm with ops which types staff actually receive today via email/WhatsApp, then add only those. Minimum add: `change-vehicle-type` + `general-inquiry`.

**Q5 — Sender-resolution = new auth surface?**
No new surface IF P3a uses `cs/tokens.py` HMAC signing. Action: read P3a token-generation code before P3b build and confirm primitive is identical. If different, require P3a to expose `resolve_sender(token) → sender_identity` utility. Do not reimplement token parsing in P3b.

**Q6 — Manual relay acceptable for v1?**
Yes. YAGNI applies at current OTA volume. Constraint: command-centre UI must show all relay fields (OTA booking ref, traveler name, requested change, OTA portal URL) in one view. No second lookup for staff.

**Blockers before P3b build:**
1. **P1 `Ticket.created_by` nullability + guest sender model** — highest-priority fix in the entire plan.
2. **`requested_value` JSON schema per `request_type`** — must be specced before serializer is written.
3. **P1 must be stable in staging** with full lifecycle (create → accept → resolve) verified before P3b touches it.

**Approved:** `source='ota'` reuse of P1 spine · no customer self-execution · sender resolved server-side from token · manual relay per YAGNI · Tier-1 SES for status-change notifications · `CsOtaBooking` FK for staff queue context.

---

## Frontend Review (P3a + P3c)

### P3a — OTA Magic-Link + Read-Only Trip View

**Verdict: Needs clarification** — directionally sound, but two hard deps are unverified: `CsOtaBooking` doesn't exist yet (P2 must complete first) and join-in boarding-info supplier feed is unconfirmed.

**Risks missed by the plan:**
- **Token-in-URL leaks into server/CDN logs and `document.referrer`.** After token validation, call `router.replace('/my-trip', undefined, { shallow: true })` to strip `?token=` before rendering PII. Plan omits this.
- **No re-issue flow spec.** "Resend on expiry" needs: who triggers it, what endpoint, rate-limit to prevent email enumeration/spam. Unauthenticated re-issue endpoint is a risk without rate-limiting.
- **RTK Query OTA token injection is non-trivial.** Existing `apiSlice.prepareHeaders` attaches `session.accessToken`. New `OtaTripView` needs `Authorization: Bearer <ota-token>` — different credential. Requires a dedicated RTK Query API slice or custom `baseQuery` variant. Plan is silent on API client layer.
- **No loading/error state spec.** Need skeleton state, empty-state message ("boarding info not yet available"), and "load error" vs "data unavailable" distinction for a greenfield page.
- **CORS for new unauthenticated endpoint.** `GET /api/cs/ota/trip/` + `AllowAny` needs explicit CORS confirmation (precedent exists in `ConversationCreateView`).

**Q7 — Stateless-on-email vs `is_guest=True` Account from P3a start?**
Stateless-first approved. Codebase precedent: `Conversation.guest_email` with no Account row. Guest Account creation belongs at P3b request-submit (lazy escalation). Stateless avoids account sprawl for one-way travelers.

**Q8 — Token bound to email vs single `booking_id`?**
Email-scoped token acceptable for read-only trip view, with conditions: explicit serializer field allowlist (already planned), tight `CsOtaBooking` FK (not soft text match), response never includes payment PII. If/when token is elevated to write-access in P3b, bind to `booking_id`. For P3a read-only, email-scope is approved.

**Q9 — Boarding-info supplier feed confirmed?**
**Not confirmed — P3a is blocked on this.** No `boarding_info`, `supplier_feed`, or join-in data model exists anywhere in the backend. If feed is absent, P3a MVP = status + booking reference only. Must be verified before any FE build starts. If feed absent, scope P3a accordingly (still valuable as a PII gate but not a "trip view").

**Q10 — Token as query param (`/my-trip?token=`) in Pages Router?**
Acceptable. Query params are the correct conveyor for ephemeral credentials in the Pages Router. Route segment (`/my-trip/[token]`) is wrong here — it would trigger ISR/SEO crawls with invalid tokens. Use `getServerSideProps` + `context.query.token` for SSR validation (avoids client-side waterfall). After token resolved, call `router.replace('/my-trip', ...)` to strip from URL.

**Blockers before P3a build:**
1. P2 `CsOtaBooking` must exist and be migrated.
2. Join-in boarding-info supplier feed confirmed live (or P3a MVP scope explicitly reduced).
3. RTK Query API slice for OTA token designed before FE sprint starts.

**Approved:** `cs-ota-trip` salt separate from `cs-guest-token` · `django.core.signing` reuse · 24h TTL matching guest token · stateless-first · email-scoped explicit serializer · `Authorization: Bearer` (not session cookie) · tiered data model with join-in first.

---

### P3c — OTA Consent, Comms & PII Gate (GATED)

**Verdict: Needs clarification** — gate boundary is correct; 3 blockers before build: SNS unconfirmed, `Order.source` missing, consent UI has no design spec.

**Risks missed by the plan:**
- **`ConsentRecord`, `consent_versions.py`, `MarketingConsentManager` don't exist** — all net-new. Migration complexity for Supabase→Django bridge (Celery task + service_role client + idempotency) is unscoped.
- **`@supabase/supabase-js` not in frontend.** If consent UI inserts directly to Supabase, adds new dep + `NEXT_PUBLIC_` env var exposure. Better: proxy via a Next.js API route (see Q13).
- **`Order.source` is payment-source (`OMISE`/`STRIPE`) not booking-channel.** `MarketingConsentManager` enforcement on `source=ota` has no anchor. Migration to add booking-channel field is unscoped prerequisite.
- **Celery Beat not confirmed running in production.** Day-before SMS requires Beat scheduler process + persistent beat schedule storage. Verify before scoping the task.
- **Probabilistic email merge = potential PDPA violation.** False merge attaches consent to wrong Account. Bridge must require exact email match + timestamp check. Flag high-confidence vs low-confidence merges as boolean on `ConsentRecord`.
- **Thai PDPA DPO sign-off path not defined.** Thai PDPA may require DPO and explicit controller ID in consent strings. Add legal checklist item before any consent string goes to production.
- **Consent toggle error state undefined.** Silent INSERT failure = user believes they opted in but record not stored. Must have error state in UI.

**Q11 — RLS anon INSERT-only sufficient, or needs rate-limit/CAPTCHA?**
Not sufficient alone. Add rate-limiting via a Next.js API route (`/api/consent/record`) that proxies the Supabase INSERT with IP-based rate-limit (Redis counter or `next-rate-limit`). Keeps Supabase anon key off client entirely. CAPTCHA is overkill; rate-limit is mandatory.

**Q12 — AWS SNS SMS confirmed enabled?**
Not confirmed — assume only. SNS requires: region enabled (`ap-southeast-1`), SMS sandbox exit, spending limit increase, IAM policy update. 1–3 day unblocking task with AWS Support if in sandbox. Do not build Celery beat task until SNS production access confirmed.

**Q13 — Erasure (GDPR Art 17) in P3c or split?**
Split to its own note (P3d or equivalent). Erasure = `DataErasureRequest` model + 2 Celery tasks (Django anon + Supabase service_role anon) + 30-day window SLA + audit log. Burying it in P3c risks under-scoping. Let P3c ship consent capture + PII gate; add TODO comment in consent model pointing at unimplemented erasure.

**Q14 — Build consent infra + PII gate before gate clears?**
Approved with condition. PII gate is unconditional (live privacy exposure — close CS-GUEST-EMAIL-GATE). Consent storage infra (`consent.records` table, RLS, `ConsentRecord` model) is low-risk regardless of gate outcome. **Gate condition: defer SNS task + Celery Beat config until contract gate clears.** Use existing `FeatureFlag` model (`cs/`) defaulting `False`; activation = explicit admin action, not code deploy.

**Q15 — Tier-2 consent toggle UX?**
No design spec exists. **Blocker.** Required before FE build: checkbox vs toggle vs modal spec, position on My-Trip page, consent string text (needs legal sign-off before versioning), confirmed vs unconfirmed visual. Structural issue: anon INSERT-only = FE cannot read back previous consent. Options: (a) `localStorage` flag after successful INSERT (UI hint only), (b) OTA trip endpoint returns `has_tier2_consent` boolean from service_role read (cleanest), (c) always show toggle + idempotent INSERT (requires unique email constraint on `consent.records`). **Recommend option (b).**

**Blockers before P3c build:**
1. AWS SNS SMS production access confirmed.
2. Design spec + consent string + legal sign-off for Tier-2 toggle.
3. `Order.source` / `BookingItem` OTA-channel field migration scoped and in P1.
4. Thai PDPA / consent wording legal sign-off.
5. `NEXT_PUBLIC_` Supabase env vars + security review (or Next.js proxy route decision).

**Approved:** 3-tier consent structure (no-opt-in Tier-1, opt-in Tier-2, gated Tier-3) · split identity storage Supabase/Django with migration bridge · `CURRENT_CONSENT_VERSION` from API · anon INSERT-only RLS baseline · `migrated_from_supabase=True` audit flag · gate structure (contract + legal as non-engineering gates) · Tier-3 gated on P0 measurement · day-before SMS as Tier-1 (legitimate interest).

---

## Architect Review (Sequencing + Gates)

### Phase Split Verdict

**Keep P2/P3a separate.** P2 produces independent staff-side value (OTA queue in command centre). P3a has two hard data-availability checks that must precede FE build. Blast radius of a bad migration is contained when sync is isolated. The coupling is a sequencing dependency, not a merge reason. **Add formal gate: P3a build does not start until P2 sync is run and validated (~561 upserts, idempotent re-run, boarding-info feed confirmed).**

P3b/P3c split is correct. P3b is ungated + mechanically distinct. P3c is gated on contract/legal; merging would block working code behind a legal hold.

### Gate Logic Verdict

**Boundary correct on paper; one leak.** P2/P3a/P3b are legitimately ungated (internal tooling or customer-initiated). P3c is correctly gated. **Leak:** P3b's "Tier-1 email on status change" (request response notifications) is quietly proactive outbound to OTA traveler inbox. Defensible as "contract performance" (traveler initiated), but legal must explicitly confirm this is in scope of P3b's ungated posture — or move to P3c gate.

### Sequencing Gaps

**Gap 1 — P1 prereq scope is understated.**
- `tickets/serializers.py` has `fields = '__all__'` on `InfoFieldsSerializer` (line 10) AND `BookingItemSerializer` (line 31) in addition to `TicketSerializer` (line 55). All three need explicit-field pins. P1 scope underestimates this.
- `Ticket.created_by` is a hard non-nullable FK to `User`. OTA-guest requests in P3b have no valid attachment point. Either P1 makes `created_by` nullable + adds `guest_email`, or a thin `Account(is_guest=True)` is created at request-submit. Neither is designed. **Highest priority fix in the plan.**
- `VALID_TRANSITIONS` in `cs/views.py` is `Conversation.status` scoped, not `Ticket` scoped. P1 must define a Ticket-specific transition graph. P3b's "reuse P1 `VALID_TRANSITIONS`" claim is currently imprecise.

**Gap 2 — `Order.source` does not exist as a booking-channel field.**
`orders/models.py:441` is `WebhookEvent.source` (Omise/Stripe enum). `Order` has no booking-channel `source` field. `MarketingConsentManager` enforcement on `source=ota` has no anchor. Requires a migration before P3c can function. Should be scoped in P1.

**Gap 3 — Boarding-info supplier feed unverified.**
P3a flags this as "defer" but doesn't formally block on it. If feed is absent, P3a ships an empty portal for dominant OTA volume (Langkawi↔Koh Lipe ferries). Make this a formal prerequisite check.

**Gap 4 — SNS SMS not confirmed on AWS account.** (See Q12 above.)

**Gap 5 — `SUPABASE_SERVICE_ROLE_KEY` env var not listed.** P3c `consent.records` migration bridge requires service_role write. Only `SUPABASE_ANON_KEY` is listed in P2. Add `SUPABASE_SERVICE_ROLE_KEY` to env inventory now.

**Gap 6 — Admin-dashboard not in any phase's file inventory.** Each phase may touch admin queue views in `admin-dashboard`. No phase note names admin-dashboard files or its review requirement. Cross-repo check (CLAUDE.md policy) is missing.

### Cross-Cutting Risks

**Risk A — Probabilistic email merge (20–40% noise) poisons multiple phases.**
P2 accepts it for ops; downstream impact untraced: P3a token resolves wrong person's trip data; P3c consent migrates to wrong Account; P3b request queue misattributes context. Add visible merge-confidence warning in admin UI and a dispute path before P3a ships.

**Risk B — Email-scoped token exposes multi-booking PII in booker≠traveler cases.**
Group travel and booker≠traveler scenarios hit this (same 20–40% noise). Token exposes all email-linked bookings. For P3b elevated write-access, bind token to `booking_id`. For P3a read-only, email-scope is acceptable with explicit serializer allowlist (see Frontend Q8).

**Risk C — Guest Account escalation seam between P3a and P3b is undefined and sharp.**
P3a stateless. P3b needs `Ticket.created_by` = a `User`. `is_guest` field doesn't exist on `Account` model; creation flow not designed. If P3b ships before this is resolved, emergency patch required. `is_guest` migration belongs in P1 prep — not P3b.

**Risk D — Anon INSERT-only on `consent.records` without rate-limit is a spam surface.** (See Q11.)

**Risk E — Four-repo change surface uncaptured per phase.** Each phase touches BE + FE + Supabase DDL. P3c additionally touches `admin-dashboard`. No phase note lists admin-dashboard files.

### Missed Reuse

- **`_resolve_guest_token` in `cs/views.py` should be extracted before P3a.** P3a needs the same header-parse + error-return guard. Extract a generic `_resolve_signed_token(request, header, loader_fn)` helper in P1/P2 prep. Plan doesn't call this out.
- **`dialogue/` GenericFK already exists.** P3b can point `Ticket` at `CsOtaBooking` via existing GenericFK rather than a new concrete FK column. Keeps Ticket model booking-source-agnostic.
- **`IsAdminOrIsStaff` reusable for all OTA admin endpoints** — already imported in `cs/views.py`. No new permission class needed.
- **`boto3` SES pattern in `cs/views.py` reusable for P3b status-change emails** — no new email abstraction needed. P3c SNS is additive (`boto3.client('sns', ...)`).

### Can phases run in parallel?

P2 BE (sync + admin queue) and early P3a FE scaffolding (route, token parse, loading states shell) are partially parallelisable after P1 ships — P3a FE shell doesn't need real data. Full P3a integration testing requires P2 complete. P3b + P3c spec/legal work can run in parallel with P3a build. No other safe parallelism given the dependency chain.

---

## Consensus: Open Questions for Owner

| # | Question | Blocks |
|---|---|---|
| OQ-1 | Contract gate verdict — do 12Go/Klook contracts permit operator→traveler service contact? | P3c (send activation) |
| OQ-2 | Are P3b request-response emails (inbound-initiated) confirmed in scope of ungated posture, or do they move to P3c gate? | P3b build start |
| OQ-3 | Boarding-info supplier feed — does it exist today? Verify with ops before P3a FE build. | P3a build start |
| OQ-4 | Sync cadence — manual batch confirmed as default v1? Or Beat from day 1? (Recommend: manual batch) | P2 build |
| OQ-5 | AWS SNS SMS — sandbox or production? Spending limit set? IAM policy in place? | P3c beat task |
| OQ-6 | Consent string wording + Thai PDPA DPO review + Privacy Policy URL — owner/legal to supply before `consent_versions.py` is written. | P3c UI + legal |
| OQ-7 | P0 rebooking measurement threshold for Tier-3 unlock — set the number before P3c spec is finalized. | P3c Tier-3 |
| OQ-8 | Erasure (GDPR Art 17) — confirm split to P3d/own note rather than include in P3c. | P3c scope |

---

## Verdict Per Phase

| Phase | Verdict | Key reason |
|---|---|---|
| **P2** | **Needs clarification** | Confirm: (1) anon-read RLS on `view_information` active; (2) pagination strategy; (3) sync cadence (OQ-4). All resolvable quickly. Unblocked after. |
| **P3a** | **Blocked** | (1) Boarding-info supplier feed unconfirmed (OQ-3) — P3a content empty without it; (2) P2 must complete first; (3) RTK Query OTA-token API slice not designed. |
| **P3b** | **Blocked** | `Ticket.created_by` non-nullable FK to `User` — OTA-guest request has no attachment point. Requires P1 schema decision. Also: `requested_value` JSON schema unspecced; P1 Ticket-scoped `VALID_TRANSITIONS` not yet written. |
| **P3c** | **Needs clarification** | Gate boundary correct. Resolve: SNS production access (OQ-5), consent UI design spec + legal sign-off (OQ-6), `Order.source` booking-channel migration, erasure scope decision (OQ-8). Build PII gate + consent infra now; defer SNS send activation until contract gate clears. |

---

## Related
[[ota-portal-overview]] · [[ota-sync-supabase-mirror]] · [[ota-magic-link-trip-view]] · [[ota-request-submit]] · [[ota-consent-comms-pii-gate]] · [[booking-command-centre-decision]] · [[cs-api-contract]] · [[cs-consent-gdpr-model]] · [[supabase-ota-booking-store]]
