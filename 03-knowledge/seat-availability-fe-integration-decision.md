---
name: seat-availability-fe-integration-decision
description: Debate + recommendation on whether the 25-40s check_seat_availability call should reach customer-facing FE (contract list / product detail). Recommendation — product detail only, on-demand, gated by a cheap BE flag; not contract list.
metadata:
  type: decision
---

# Seat Availability — FE Integration Decision

> **STATUS: RECOMMENDATION ONLY, 2026-09-19.** No code shipped. FE has zero references to `check_seat_availability` today — confirmed greenfield.

## Question

Should `check_seat_availability` (admin-dashboard-only today) get surfaced on smartenplus-frontend — contract list and/or product detail pages? First blocker: FE needs to know *which contracts even qualify* before any integration design makes sense, since the call takes 25-40s.

## Which contracts qualify

Only contracts clearing all three gates in `ContractViewSet.check_seat_availability` (`smartenplus-backend/operators/views.py:1019-1172`) ever reach the slow external call:

1. `contract.trip` is set (transport contracts only — `NO_TRIP` 400 otherwise)
2. Resolved operator (`contract.seat_check_operator or contract.operator`) has `seat_availability_api_url` configured
3. `OperatorStationMapping` exists for both departure + arrival stations under that resolved operator

Most of the catalog (SmartEnPlus's own "Model A" contracts) fails gate 2 and should exit instantly with `available: null`. Only reseller contracts (currently Lomprayah-sourced, via `seat_check_operator`, see [[seat-availability-reseller-operator-gap]]) reach the live 25-40s n8n call. A known unfixed order bug ([[seat-check-mapping-before-apiurl-order-bug]]) means gate 3 is checked before gate 2, so some non-qualifying contracts currently get a misleading `MAPPING_NOT_FOUND` instead of the intended graceful null.

## The debate

**Option A — contract list, auto-check on load:** rejected. N visible cards × 25-40s each, concurrent load against one external webhook already prone to timeout drift ([[n8n-seat-search-response-contract]]). Most of those N calls would return null anyway if gates were checked first — no reason to spend the round trip.

**Option B — product detail, on-demand, gated:** recommended. FE checks a cheap gate flag (see below) before ever showing the affordance; if shown, one button click = one call for the one contract the customer already committed to viewing. Async UX pattern already exists in `hooks/useQRPolling.js` (interval polling + `shouldStopPolling` guard, used for payment status) — reusable here instead of inventing a new pattern.

**Option C — hold, fix BE first:** treated as a prerequisite to B, not a competing option. Two issues should land before FE wiring: the order bug above, and the fact that the 40s timeout has already been raised twice in ~2 months as measured latency climbed ([[n8n-seat-search-response-contract]]) — an unstable SLA to build customer-facing UX against without a graceful-timeout fallback.

## Recommendation

Ship B, gated by C:

- **BE adds** a cheap boolean on the existing contract/trip response — e.g. `has_live_seat_check` — computed from gates 1-3 without calling n8n. FE gates the button on this field, never on a timed-out request.
- **BE fixes** the order bug so a non-qualifying contract returns `available: null` cleanly.
- **FE renders** the "Check live seats" affordance only on product detail, only when `has_live_seat_check` is true. Never on contract list.
- **FE reuses** the `useQRPolling`-style async pattern (explicit loading state, no page block, 40s-matched timeout) plus `ListSkeleton` for the loading state.
- **FE degrades** on timeout/error to "Couldn't confirm live availability — contact us," not a stuck spinner.

## Addendum — funnel placement, 2026-09-19

User proposed a concrete flow: trip detail page shows realtime seats as user browses calendar dates, then checkout should definitively confirm bookability before payment. This splits into two asks that pull in different directions:

- **Calendar-browse-time check (rejected):** `SlideCalendar2.js` date selection is 100% client-side/Redux today (`selectHandler`, no network call; `fareCalendar` is a local `useMemo` over an already-fetched date-agnostic `ratecard`). Wiring a 25-40s live check to fire on every date tap means repeated waits on a page users skim before committing — worse than the on-demand-button plan above, not better. Recommendation stands: do not touch calendar browsing.
- **Checkout-time check (adopted, refines Option B):** today's checkout (`pages/checkout/index.js`) re-validates advance-hour, stop-sale-date, and passenger-count-vs-capacity (`validateCartCapacity()`), but has **zero live stock/seat check** — confirmed via FE trace. Moving the on-demand check to fire once at checkout, gating the pay button, satisfies the user's actual goal ("don't let user pay then find out it's unavailable") at the one point in the funnel where a 25-40s wait is proportionate to intent. Reuses the same `has_live_seat_check` gate flag and `useQRPolling`-style async pattern already recommended above — this addendum only relocates *where* the on-demand trigger fires (checkout pay-button gate, not a product-detail standalone button), it does not change the prerequisite BE fixes (order-bug, gate flag) or the rejection of contract-list/calendar auto-checks.

Stakeholder-facing Thai visual summary of this addendum: artifact `seat-check-thai-demo.html` (published this session).

## Addendum 2 — exact trigger point + abandoned cart, 2026-09-19

Two follow-up questions sharpened "checkout" into a precise mechanism:

**Q1: does the check fire at checkout page load / cart-has-item, or on submit?**

> **REVISED 2026-09-19** — first answer below ("gate the Pay button click") was wrong; user correctly flagged it. Kept for the record, corrected version follows.
>
> ~~Fires as a gate on the final "Pay" action, not on checkout mount or cart-has-item.~~ Problem: binding the 25-40s check to the literal pay-click conflates seat-verification with payment-session start. Two concrete issues: (1) payment gateway session/timing risk — providers expect the pay action to start a payment session promptly (see CLAUDE.md payment gotchas, `useQRPolling`, `expirePendingCharge`); bolting a 25-40s pre-check onto that click either delays session creation by up to 40s or leaves the button looking hung; (2) conflated UX state — a spinner after "Pay" is ambiguous (processing payment, or still checking seats?), and a sold-out result after the click reads as a failed payment even though none was attempted.

**Corrected (round 2):** a manual "Confirm your seat" button (round-1 fix) was also rejected by user — booking flows shouldn't add a click users didn't ask for. Final model: the check fires **automatically**, no user action, the moment the user reaches the final checkout step with passenger details already complete (i.e., on arrival at the payment section, before the Pay button is shown as active). While it runs (25-40s), the Pay button is visible but disabled/loading with a "กำลังยืนยันที่นั่ง…" (confirming your seat) state — user can still review their order, nothing blocks them, but Pay itself only activates once the check resolves. If sold out, Pay never activates and the user is told to remove/rebook before any payment session starts.

This still separates seat-verification from payment-session-start (avoiding the original payment-gateway-timing bug) — it just removes the manual trigger in favor of an automatic one that starts as soon as it's safe to (details finalized, before Pay is clickable), rather than waiting for a click that doesn't exist. Core recommendation unchanged (late in checkout, once, qualifying contracts only, gated by `has_live_seat_check`).

**Q2: user adds to cart, reaches checkout, doesn't pay, returns days later — what should happen?**
New research this session confirmed a real, previously undocumented gap: **carts never expire.** `Cart` model (`carts/models.py:8-14`) has no TTL/expiry/status field; no Celery Beat job cleans up unpaid carts (the only cart task, `cleanup_orphaned_cart_items` in `carts/tasks.py:586-727`, is unregistered and only touches already-**paid** order leftovers). `Order` STATUSES (`orders/models.py:164-173`) has no `abandoned`/`expired` state — an order stuck in `ordering` stays there forever.

Given that, returning to a stale cart today re-runs the same static gates that were true when the item was added (`is_actived`, advance-hour, stop-sale — all re-checked client-side on every mount, `checkout/index.js:280-296,656-668,836`; same set again server-side at booking creation, `carts/utils.py:62`) but **never re-confirms seat availability**, regardless of how old the cart is.

**Because the recommended design gates the check on the pay action rather than cart age or mount, this is self-healing by construction** — no separate "abandoned cart" handling is needed for seat-availability specifically. Whether the user reaches the pay button in the same session or 10 days later, the check fires fresh at that exact moment either way.

**Gap surfaced but out of scope for this decision:** cart price is silently recomputed live from current `contract_ratecard.selling_rate` on every checkout mount, with no "price changed since you added this" warning. This is a real issue for the same "returns days later" scenario, but is a pricing-cache/UX concern unrelated to seat availability — flagged here for a separate follow-up, not folded into this decision.

## Related

[[seat-availability-reseller-operator-gap]] · [[n8n-seat-search-response-contract]] · [[seat-check-mapping-before-apiurl-order-bug]] · [[master-state]]
