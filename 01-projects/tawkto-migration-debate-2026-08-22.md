---
name: tawkto-migration-debate-2026-08-22
description: 3-role debate (Business Dev + Backend SWE Django + Frontend SWE Next.js) on replacing custom CS chat (Django+Supabase, 3 repos) with tawk.to. Read-only vault+code audit, no code changed.
metadata:
  type: decision
  status: active
  date: 2026-08-22
  parent: cs-architecture-decision
---

# Tawk.to Migration Debate — 2026-08-22

> Read-only session. Vault + FE/BE/AD code audited first, then 3-role debate run inline (no subagents spawned — full context already in hand from audit). No code changed.

## What exists today (ground truth, code-verified)

Custom CS system, NOT a simple chat widget — a customer-ops platform spanning 3 repos:

| Layer | Size | What it does |
|---|---|---|
| FE (`smartenplus-frontend`) | `ChatWidget.js` 375L, `ChatPanel.js` 295L, `useChatPolling.js` 95L | Widget state machine (15 named states), guest OTP gate, optimistic send, design-system tokens (WCAG AA verified) |
| BE (`smartenplus-backend`) | `cs/models.py` 308L, `cs/views.py` 1425L | `Conversation`/`Message`/`CSOtp` models, HOTP email-OTP auth, signed guest tokens, SLA breach tasks, ticket workflow (`RequestStatusViewSet`), OTA booking sync (`CsOtaBooking`), emergency escalation, GenericFK ticket/order linking |
| AD (`admin-dashboard`) | `ConversationDetail.js`, `useStaffChatRealtime.js` | Staff inbox, unread badges (Supabase Realtime, client-authoritative), SLA countdown, resolution notes, admin-initiated flow |

**Deployed to prod** 2026-07-03 (`CS-CENTRALIZATION-DEPLOY`, all 3 repos). Not a prototype — live, in active iteration (5+ bugfix rounds: guest-403 r2-r5).

**Transport history:** Django polling + Supabase Realtime (current) → GetStream migration proposed 2026-07-13 (4-agent debate: 2 STAY/2 CONDITIONAL, verdict STAY) → reversed same day after user pain report (reconnect bugs, silent 401, no prod notification) → 6-agent audit → **CONDITIONAL, 4 blockers, no code shipped, stalled at audit stage.** Tawk.to never evaluated in any prior session — genuinely new comparison point.

**No mention of tawk.to anywhere in vault or codebase** — confirmed via grep across all 3 repos + vault.

## Framing the actual question

Not "build vs tawk.to" (that ship sailed 2026-06-21). It's: **rip out a deployed, deeply-integrated, business-logic-bearing system and replace it with a 3rd-party embed** whose product category is fundamentally different (visitor-engagement widget, not ticketing/OTA-sync platform).

---

## Role 1 — Business Development

**Position: AGAINST full replacement. Conditional support for tawk.to as an *additive* channel, not a swap.**

- Tawk.to's value prop (free, instant-setup live chat, canned responses, visitor monitoring) targets pre-sales/lead-gen — SmartEnPlus's pain points are *post-booking* (SLA tracking, OTA guest identity, ticket-linked change requests, emergency escalation). Tawk.to has none of these primitives; they'd need to be rebuilt as custom fields/integrations bolted onto tawk.to's API, which is thinner than what's already built in-house.
- Cost frame is backwards: tawk.to is "free" as a headline but the migration cost is the *loss* of ~2,500 lines of working, tested, prod-hardened domain logic (OTA sync, SLA, emergency flag, resolution notes) that would need bespoke tawk.to-side reconstruction via their REST API/webhooks — a rebuild, not a swap.
- Brand/UX control: current widget is pixel-matched to design system (WCAG AA audited, brand tokens). Tawk.to widget is an iframe — visually off-brand unless paid tier (still limited), and Thai/multi-market microcopy control is weaker.
- Where tawk.to *does* win: zero-maintenance uptime, mobile agent app, canned-response/proactive-trigger features SmartEnPlus never built. Real gap: **pre-sales chat on marketing pages** (`/trips`, `/activities` browse) where no chat currently exists at all — that's a legitimate greenfield slot for tawk.to, separate from the post-booking CS system.
- Recommendation: pilot tawk.to on **top-of-funnel pages only** (before booking/login) as a lead-capture layer; leave post-booking CS (ticket/order-linked) on the current system. Any full swap needs a cost model comparing engineering-hours-to-rebuild-parity against tawk.to's paid-tier cost (agent seats, ticketing add-on) at current+projected volume — not built yet, don't decide without it.

## Role 2 — Backend SWE (Django)

**Position: AGAINST. Migration cost >> claimed savings; parity is not achievable without reinventing tawk.to on top of tawk.to.**

- `cs/models.py`/`views.py` (1733 lines) encode business rules with no tawk.to equivalent: `RequestStatusViewSet` ticket-status transitions, `CsOtaBooking`/`OtaBookingEvent` sync guard chain (BE-B1..B5 gap history shows this is already fragile — adding a 3rd vendor makes it worse, not better), SLA breach Celery tasks, emergency-flag notification routing, GenericFK linking chat threads to tickets/orders. None of this maps to tawk.to's data model (visitor + agent + department tags only).
- Auth model conflict: current system uses signed guest tokens (`django.core.signing`) + HOTP OTP tied to `Conversation`/email identity, reconciled against OTA guest bookings. Tawk.to visitor identity is anonymous-by-default (session-based); bridging it to an authenticated `session?.id` / guest-OTA identity would require a custom Django webhook consumer translating tawk.to events into the existing `Message`/`Conversation` schema — i.e., building an adapter layer *in addition to* keeping the current backend, not replacing it.
- Losing server-side source of truth: today Django `cs.Message` is canonical (even the shelved GetStream plan kept this — "Source of truth: Django `cs.Message` (always)"). Tawk.to's canonical store is tawk.to's own cloud; exporting is limited (their API only, rate-limited, no guaranteed real-time webhook parity per their docs) — this reintroduces exactly the vendor-lock-in problem the GetStream audit flagged (B_vendor from `getstream-migration-debate-2026-07-13`), except with a product that doesn't even try to serve this use case.
- SLA/ticket automation (`check_sla_breaches`, emergency escalation) currently runs server-side against Django models with direct DB access. Tawk.to has no comparable scriptable backend hook system (webhooks only, coarse-grained: chat started/ended, not domain events like "resolution_note added").
- Verdict: full swap = throw away 1733 lines of working domain logic + rebuild an integration adapter that's *more* code than what exists today, to gain a UI vendor doesn't need. If evaluating at all, scope to marketing-page pre-sales chat (BD's carve-out) where zero backend integration is needed — tawk.to's own hosted backend suffices for that narrow case.

## Role 3 — Frontend SWE (Next.js)

**Position: AGAINST for the CS widget; NEUTRAL-TO-POSITIVE for a separate marketing-page chat.**

- Current widget (`ChatWidget.js` + `ChatPanel.js`, 670 lines) is a `dynamic(ssr:false)` island already optimized for the "most users never open it" case (verdict F1 from `cs-gap-debate-verdicts.md`) — bundle cost is already minimal. Tawk.to's embed script is a 3rd-party `<script>` tag loaded on every page — worse for Core Web Vitals (SmartEnPlus is Core-Web-Vitals-sensitive per multiple vault CWV audit entries) unless lazy-loaded identically, at which point the "just drop in a script tag" simplicity argument for tawk.to evaporates anyway.
- State/UX regressions: current widget has optimistic send, 15-state inventory (`error-send-failed` retry, `offline-no-network` draft preservation, `reply-received` auto-scroll), guest-identity localStorage bridge, mobile bottom-sheet pattern matching `ProfileBottomSheet.js`. Tawk.to widget UI is a fixed iframe with its own (non-brand) states — losing this is a UX downgrade for the exact flows the design-concept doc spent a full audit pass hardening (WCAG AA fixes, G-01..15 token gaps).
- Auth bridging is the same wall BE hit: tawk.to visitor JS API (`tawk_setAttributes`) can pass name/email as *display metadata* but has no way to authenticate against SmartEnPlus's NextAuth session or gate on OTA guest identity — the widget would need a custom wrapper re-deriving identity state anyway, undercutting the "no more custom widget code" pitch.
- Where it's a clean fit: a `/trips`, `/activities` marketing-page-only tawk.to embed, gated to unauthenticated/pre-checkout routes, with zero integration into `cs.Conversation` — genuinely additive, near-zero engineering cost (script tag + route-based conditional mount), no state machine to build.
- Verdict: don't touch the CS widget. If BD wants marketing-chat coverage, that's a half-day FE task (conditional script injection by route), fully decoupled from `cs/` app — no backend change needed.

---

## Synthesis / Recommendation

**Do not replace the CS system with tawk.to.** All 3 roles converge independently on the same split:

1. **Keep current Django+Supabase CS system as-is** for post-booking flows (ticket-linked chat, OTA guest support, SLA/emergency escalation) — it's deployed, working, and encodes business logic tawk.to has no model for. The GetStream conditional-migration path (audited, 4 blockers, stalled) remains the only live alternative under consideration for *this* system, and that's a transport swap (polling reliability), not a product swap.
2. **If BD wants pre-sales/lead-gen chat on marketing pages**, tawk.to is a legitimate low-cost pilot — script-tag only, gated to unauthenticated browse routes (`/trips`, `/activities`), zero backend integration, ~half-day FE task. This is additive, not a replacement.
3. **Decision gate before any spend**: BD to define what metric a marketing-chat pilot would move (lead capture rate? pre-booking question volume?) before greenlighting even the small pilot — same discipline as S6 in `cs-gap-debate-verdicts.md` (pre-commit metric before shipping).

## Related
- [[cs-chat-getstream-migration/README]] — parallel transport-only migration path (conditional, stalled)
- [[getstream-migration-debate-2026-07-13]] — prior 4-agent debate precedent this one follows format-wise
- [[cs-subsystem-weakpoints]] — current-state fragility (reason NOT to add a 4th vendor surface on top)
- [[cs-gap-debate-verdicts]] — original build verdicts, OTP/guest-auth/SLA architecture referenced above
- [[cs-centralization-design-concept]] — UX spec the tawk.to swap would discard
