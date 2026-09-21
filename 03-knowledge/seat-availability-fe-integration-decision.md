---
name: seat-availability-fe-integration-decision
description: Debate + recommendation on whether the 25-40s check_seat_availability call should reach customer-facing FE (contract list / product detail). Recommendation — product detail only, on-demand, gated by a cheap BE flag; not contract list.
metadata:
  type: decision
---

# Seat Availability — FE Integration Decision

> **STATUS: RECOMMENDATION ONLY, revised 2026-09-21 (see Revision below).** No code shipped. FE has zero references to `check_seat_availability` today — confirmed greenfield. **The Addendum 2 trigger point below (checkout-time, gate the Pay button) is SUPERSEDED — read the Revision section first, it changes the trigger to Passengers-step + timer-gated Payment recheck, and flags 3 ship-blockers not covered in the original debate.**

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

## Revision — 2026-09-21, trigger point moved to Passengers step + timer

3-lens (BD/UX/SWE, opus) stress-test of the original Addendum-2 recommendation, then two rounds of user-driven revision. Session ran in `smartenplus-frontend`, code-only exploration (no code shipped) — see `~/.claude/plans/check-vault-and-fe-fluttering-frog.md` in that repo's Claude Code history for full working detail; this section is the durable summary.

**Factual correction to the original debate:** "gate the Pay button, fires before any payment session starts" was wrong on one fact — arrival at the payment step already creates a backend Order+Booking (`usePaymentInitialization.js:186-214`, `getOrderAndBilling → getCreateBooking`). No money moves at that point, but a record exists. This matters because the original design's implicit safety claim (nothing has happened yet) was false at the moment it mattered most.

**Trigger point moved: Passengers step (formStep 1), not Payment step.** Confirmed via code trace: the endpoint (`check_seat_availability`) is headcount-independent — query params are `from`/`to`/`date`/`time` only, no passenger count — so a Passengers-step check isn't premature on the headcount axis. And critically, item-removal is cheap and UI-available at the Passengers step (`canDeleteItem = formStep < 3`) but **locked** at the Payment step (delete button replaced by a "cart locked" icon) — so "notify + let user remove" (the actual product goal) is only buildable at Passengers step, not Payment step as originally recommended.

**Final mechanism (user-confirmed, 2026-09-21):**
1. Check fires automatically on arrival at Passengers step (not on Next-click) — Next button disabled until it resolves. Scoped only to cart items with `has_live_seat_check === true`.
2. A per-item elapsed-time counter starts at that check. If the user reaches Payment step before the counter expires (working assumption: 10-15 min, not yet finalized), the cached result is trusted — no second network call. If expired, a silent recheck fires at Payment-step arrival, hidden behind the existing order-creation loading wait, gating only the Pay button (not Next again).
3. Three-way result handling throughout: confirmed sold-out → block + remove-item affordance; confirmed available → proceed; anything else (timeout, 502, null, any error) → **fail open**, proceed with a soft advisory. This fail-open default is load-bearing — see blockers below.

**3 ship-blockers found in a follow-up architecture-review pass, not in the original debate:**
1. **Guest checkout breaks this silently.** `check_seat_availability` is `IsAuthenticated`-gated; guest checkout is a live path in this app. Every guest gets a 401, which — because of fail-open — is indistinguishable from "available." Feature would ship 100% dead for guests with zero signal. Must be resolved (either open the endpoint + rate-limit, or explicitly scope to logged-in users) before any frontend work starts.
2. **A 400 error path unconditionally leaks internal infra** — the operator's live upstream API URL and full station-mapping table — into the response body. Fine when admin-only; becomes visible in every customer's Network tab once called from checkout. One-line fix (gate behind the existing `debug_on` flag, already used correctly on the other response paths) — same PR as `SEAT-CHECK-MAPPING-ORDER-BUG`.
3. **The Payment-step "let user remove a sold-out item" design is architecturally impossible as specified** — delete UI is already replaced by a lock icon at that step in the existing codebase. Fix: don't build new UI, reuse the existing `CONTRACT_INACTIVE` pattern (advisory + redirect back to cart-review step where delete already works).

Also flagged, not blockers but real: the tri-state `available` field means a soft "don't know" (`null`, arrives as HTTP 200) must never be treated as a hard "no" — a one-character bug (`!data.available` vs `data.available === false`) would wrongly block paying customers on ordinary network hiccups; zero observability currently planned (a production complaint would be undiagnosable — minimum fix is one server-side log line per check, no frontend work needed); a kill switch already exists for free (`has_live_seat_check` / `seat_availability_api_url` can be flipped per-contract/operator with zero deploy) but isn't documented as the rollback procedure anywhere.

**Prerequisite backend work, independent of frontend, ship first:** `SEAT-CHECK-MAPPING-ORDER-BUG` gate-order fix + the debug-leak fix above, in the same PR. Endpoint stays admin-only until both land — zero risk in the meantime.

## Related

[[seat-availability-reseller-operator-gap]] · [[n8n-seat-search-response-contract]] · [[seat-check-mapping-before-apiurl-order-bug]] · [[master-state]]
