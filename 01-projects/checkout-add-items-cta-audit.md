# Checkout — Add Items CTA Audit

## Summary

Add a "Add another trip" CTA button to Step 0 of checkout (`Itineraries.js`) that opens the existing `SearchDialog`. Supports mid-checkout cart augmentation without navigation away. Both UX and UI findings are green. Recommend shipping with one mitigation: a custom dialog title to reduce abandonment risk.

## Context

- **Platform:** SmartEnPlus travel booking — multi-step checkout (Step 0 = itinerary review)
- **Component in scope:** `Itineraries.js` (Step 0 render), `SearchDialog` (existing, reused as-is)
- **Trigger:** Users want to add trip items mid-checkout without losing checkout state
- **Date audited:** 2026-08-16
- **Audit team:** UX Reviewer + UI Designer + Business/Design Director

## Problem

Users reach Step 0 of checkout and realize they want additional trips. Current path: navigate back to search, losing partial checkout state. This causes abandonment. The fix is a low-friction in-context CTA that opens `SearchDialog` as a modal overlay, preserving all checkout state underneath.

## UX Findings

**CTA Placement:**
- 1+ items state: below the last `EnhancedTripCard` in the `flex flex-col gap-3` container, `mt-2` gap
- 0 items state: replace "No items found." with a prominent hero CTA — same location, upgraded prominence

**Micro-copy:**
- 1+ items: `+ Add another trip`
- 0 items: `Search for a trip`

**State Visibility Rules:**

| State | CTA Behavior |
|---|---|
| `formStep === 0`, 1+ items | Outlined CTA below list |
| `formStep === 0`, 0 items | Prominent hero CTA replaces "No items found." |
| `formStep > 0` | Hidden entirely |
| `isLoading === true` | Hidden |
| `invalidItems` present | Shown — user may want to add a replacement trip |

**Post-add flow:** Dialog auto-closes → `refetchCart()` fires → new card appears. No toast needed; card appearance is the confirmation.

**Mobile assessment:** Medium risk. `SearchDialog` already handles mobile via MUI `fullScreen={isSmDown}`. Checkout state is preserved (modal overlay, not navigation). Main risk: fee flicker during `refetchCart()` — accepted known tradeoff.

**Top UX risks:**
1. **Search rabbit hole → abandonment.** User opens dialog and forgets they were in checkout. Mitigation: pass `title="Add a trip to your booking"` to `SearchDialog` — contextualizes the action.
2. **Invalid-item confusion.** User may think adding a new trip fixes existing invalid items. No special handling needed — `refetchCart()` re-derives the alert state correctly.
3. **Fee state desync.** `setFee(0)` fires during refetch, causing a fee flicker. Accepted; no architectural change needed.

## UI / Visual Findings

**Button variant:** Dashed-border outlined. Not filled (would compete with "Continue" primary CTA). Not secondary gray (reads as cancel/dismiss).

**Visual spec (DS-compliant):**

| Token / Class | Value |
|---|---|
| Border | `2px dashed` + `border-brand-primary` (`#3b5998`) |
| Background | `transparent` |
| Text color | `text-brand-primary` |
| Border radius | `rounded-md` (`BORDER_RADIUS_CLASSES.button`, 6px) |
| Min height | `min-h-[44px]` (`TOUCH_TARGET.minHeight`) |
| Font weight | `font-medium` (500) |
| Font size | `text-sm sm:text-base` |
| Hover state | `bg-[#EFF6FF]` + `border-solid` |
| Transition | `duration-150` |
| Width | `w-full` |

**Icon:** MUI `AddIcon` size 18, left of label. Already available in `EnhancedTripCard`'s MUI import set — no new dependency.

**DS compliance notes:**
- `Itineraries.js` is clean — no existing violations to work around
- Do NOT use hardcoded hex colors (except approved hover bg `#EFF6FF`)
- Do NOT use `rounded-lg` (wrong radius token for buttons)
- Do NOT use inline `px` heights — use `min-h-[44px]`
- Dark mode: not implemented in checkout — skip for now

**SearchDialog changes:** Pass `title="Add a trip to your booking"` only. No other prop changes needed — fullscreen mobile behavior is already correct.

## Director Recommendation

**Ship it.**

**Conversion hypothesis:** A non-trivial percentage of checkout starts abandon at Step 0 not because they don't want to book, but because the cart is incomplete. Adding a zero-navigation path to search directly from the itinerary review screen removes that exit point. Expected effect: Step 0 → Step 1 progression rate improves. Secondary: reduces "incomplete cart" support tickets.

**Biggest risk:** Search rabbit hole → abandonment. The custom dialog title (`"Add a trip to your booking"`) is the minimum viable mitigation. If post-ship data shows dialog-open → checkout-abandon correlation, the next lever is a sticky "Return to checkout" affordance inside the dialog — but don't build that speculatively.

**Why dashed-border matters:** The visual treatment signals "optional / additive" rather than "required action." Users who don't need to add a trip will naturally skip it. If it were filled/primary, it would compete with the Continue CTA and create decision paralysis. This is the correct choice.

**What this is not:** This is not a upsell surface. Do not add promotional copy, trip suggestions, or pricing nudges to this CTA or dialog. The job is frictionless addition, not conversion optimization at that moment.

## Decision

**Status:** Recommended — pending implementation

**Implementation owner:** Frontend dev (TBD)

**Files to change:**
- `src/components/checkout/Itineraries.js` — add CTA after `items.map()` block, gate on `formStep === 0`
- No changes to `SearchDialog` internals — pass `title` prop only

**Files NOT to change:**
- `SearchDialog.js` internals
- Any Redux slice (cart refetch uses existing `refetchCart()`)
- `useOmisePayment.js` (see CRITICAL GOTCHA: cart reset location)

## Tradeoffs

| Tradeoff | Accepted? | Notes |
|---|---|---|
| Fee flicker during `refetchCart()` | Yes | Known, pre-existing behavior. Not new debt. |
| Search rabbit hole risk | Yes, with mitigation | Custom dialog title reduces but doesn't eliminate. Monitor abandonment rate. |
| MUI `AddIcon` import | Yes | Already in tree via `EnhancedTripCard` — no bundle delta. |
| No toast on add | Yes | Card appearance is sufficient confirmation. Toast would add noise. |
| No dark mode | Yes | Checkout has no dark mode — consistent with existing pattern. |

## Consequences

**If shipped:**
- Step 0 → Step 1 funnel improves (hypothesis — measure via existing checkout funnel analytics)
- Checkout abandonment from "I need to add something" exits eliminated
- Zero new dependencies, zero new Redux state, zero changes to payment flow

**If not shipped:**
- Status quo: users navigate away, lose checkout state, may not return
- No downside to shipping — change is additive, fully gated on `formStep === 0`, hidden otherwise

## Related

- `src/components/checkout/Itineraries.js` — primary change file
- `src/components/search/SearchDialog.js` — reused as-is
- `docs/operations/CHECKOUT.md` — SSR/logout/sessionStorage rules (no changes needed)
- CLAUDE.md CRITICAL GOTCHAS: cart reset location (`cartActions.resetCart()` on order pages ONLY, not in payment hooks)
- Payment state machine: `smartenplus-backend/docs/technical/PAYMENT_SYSTEM.md`
