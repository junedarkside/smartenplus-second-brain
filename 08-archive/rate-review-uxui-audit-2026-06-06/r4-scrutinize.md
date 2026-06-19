# r4-scrutinize — Outsider Verification Pass
**Date:** 2026-06-06
**Scope:** Verify r1-ux + r1-visual + r1-frontend + r2-skeptic + r3-leader-synthesis before implementation

---

## Verdict: FIX-THEN-SHIP

Audit quality is high. Core findings (XSS, parseISO crash, star ARIA, router import, email masking) all verified against source. Skeptic debate correctly pruned ~10 findings. 4 corrections needed before using r3 as implementation spec.

**Overall health score from r3 (4.5/10) is accurate given the P0 security issue and page-crash bug.**

---

## Verified Correct (source-checked)

| Claim | File:Line | Status |
|-------|----------|--------|
| XSS: `dangerouslySetInnerHTML` no DOMPurify | `[reviewSlug].js:455` | CONFIRMED — no DOMPurify import in file |
| DOMPurify SSR-safe pattern in codebase | `ReviewList.js:3,5,95` | CONFIRMED — copy target exists |
| Double `return normalized` | `[reviewSlug].js:231,233` | CONFIRMED |
| `parseISO(null)` no null guard | `BookingReviewList.js:43-45,110` | CONFIRMED |
| `aria-pressed={value <= rating}` wrong ARIA | `RateAndReviewForm.js:119` | CONFIRMED |
| Guard/redirect field mismatch | `[...slug].js:71-72` | CONFIRMED — guards `.slug`, redirects via `.booking_item_slug` |
| Unmasked `user_info.email` in ReviewList | `ReviewList.js:53-56` | CONFIRMED — `maskEmail()` defined same file, not applied |
| Wrong router import in BookingReviewList | `BookingReviewList.js:2` | CONFIRMED — `next/navigation` not `next/router` |
| Relative push paths missing `/` | `BookingReviewList.js:185-186` | CONFIRMED |
| `[reviewSlug].js` correctly uses `next/router` | `[reviewSlug].js:138` | CONFIRMED — not a problem here |
| Canonical missing `www.` | `[reviewSlug].js:249` | CONFIRMED — `https://smartenplus.co.th/rate-review` |

---

## Skeptic Drops — Verified Correct to Drop

- **VIS-06 (44px stars)**: Touch target is on `IconButton` wrapper (`minHeight/minWidth:44px`). Visual star at 44px inside is a product choice, not a WCAG violation. Drop correct.
- **VIS-10 (hover:bg-blue-600)**: `#2563EB` = `COLORS.brand.secondary`. Same hex value. No visible diff. Drop correct.
- **VIS-13 (text-fb-blue inconsistency)**: Visual specialist explicitly said "no code change needed." Should not have been a finding. Drop correct.

---

## Corrections to r3-leader-synthesis

### CORRECTION-01: P1-10 over-elevated (re-classify to P2)

**r3 places it:** P1 — "re-evaluated: real WCAG gap affecting form usability"
**Skeptic placed it:** P2 (confirmed FE-16 at P2)
**Scrutiny verdict:** Skeptic is correct. `aria-required` on the MUI TextField wrapper div doesn't prevent visual `required` asterisk from showing — most users are unaffected. The re-elevation from skeptic's P2 to leader's P1 is unsupported.

**Correction:** Move `aria-required` fix (FE-16) back to P2. The P1 slot is already full with higher-impact items.

---

### CORRECTION-02: FE-22 fix direction is ambiguous — verify API shape first

**r3 fix:** Change guard to `if (review?.data?.booking_item_slug)`, then redirect on same field.
**Problem:** The current guard checks `review?.data?.slug`. If the backend API response actually contains a `slug` field (not `booking_item_slug`) for the redirect target, the correct fix is to change the redirect from `booking_item_slug` to `slug` — NOT change the guard.

Two possible fixes depending on API:
- **If API returns `slug` for review detail route:** Change redirect: `router.push(\`/rate-review/${review.data.slug}\`)`
- **If API returns `booking_item_slug` for booking slug route:** Change guard: `if (review?.data?.booking_item_slug)`

**Action before implementing:** Check backend `/dialogue/reviews/` POST response shape. Look for both `slug` and `booking_item_slug` fields. Fix whichever is wrong.

---

### CORRECTION-03: P1-9 canonical — `reviewSlug` variable confirmed in scope

**r3 concern flagged in planning:** Is `reviewSlug` in scope at canonical definition?
**Verified:** `[reviewSlug].js:243` — `const { reviewSlug } = router.query` — variable IS in scope.
**Correct fix (confirmed):**
```js
// Inside the useMemo that builds the seo object
canonical: `${getSiteUrl()}/rate-review/${reviewSlug}`
```
This is valid because `reviewSlug` is available from `router.query` destructuring at line 243, before the `useMemo` seo config at line 246.

**No correction needed — just confirming implementation is clear.**

---

### CORRECTION-04: P0-3 (star ARIA) must ship in same release as P0-1/P0-2

**r3 implementation order:** XSS (step 1) → parseISO crash (step 2) → router import (step 3) → email masking (step 4) → canonical (step 5) → **star ARIA (step 6)**

**Problem:** Star ARIA is P0 but deferred to step 6, after 2 P1 fixes. Implementation order prioritizes P1s over a P0.

**Correction:** Star ARIA MUST ship in the same release as XSS + parseISO crash fixes, even if it's the last thing implemented in that batch. Mark steps 1, 2, 6 as "Release 1 — P0 batch." Mark steps 3-5 as "Release 1 — can include, small effort." Steps 7+ are "Release 2 / Sprint 2."

**Corrected release grouping:**
```
Release 1 (P0 fixes — must ship together):
  - P0-1: XSS DOMPurify fix
  - P0-2: parseISO null guard
  - P0-3: Star ARIA radiogroup refactor
  - P1-1: Router import + paths (XS effort, include in P0 batch)
  - P1-2: Email masking (XS effort, include in P0 batch)

Sprint 1 (P1 fixes):
  - P1-3 through P1-9 (minus P1-10 which moves to Sprint 2)

Sprint 2 (P2 fixes + demoted P1-10):
  - P2-1 through P2-13 + FE-16 (aria-required)
```

---

## No Issues Found In

- Skeptic's Top 5 ranking (order is correct by real-world damage)
- All 3 skeptic drops (VIS-06, VIS-10, VIS-13) — verified correct to drop
- All confirmed P0s (FE-01, FE-02, FE-03) — all verified in source
- P2-13 re-elevation from skeptic's P3 — defensible once H1 is added (P2-12 creates sibling that makes gap-0 visible)
- Duplicate deduplication (UX-15→FE-14, UX-17→FE-09, UX-18→VIS-05) — all correct merges

---

## Summary of Changes to Apply to r3

| # | Change | Affects |
|---|--------|---------|
| CORRECTION-01 | Move FE-16 (aria-required) from P1-10 → P2 | r3 P1 list, P2 list |
| CORRECTION-02 | Verify API response shape before implementing FE-22 fix | r3 P1-3 note |
| CORRECTION-03 | `reviewSlug` variable confirmed — no change needed | r3 P1-9 clarified |
| CORRECTION-04 | P0-3 must ship in Release 1, not after P1 fixes | r3 Implementation Order |
