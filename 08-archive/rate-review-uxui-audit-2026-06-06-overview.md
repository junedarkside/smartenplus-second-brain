# /rate-review UX/UI Audit — 2026-06-06

## Summary

4-specialist adversarial audit of the SmartEnPlus `/rate-review` flow (list, detail, submit-review pages) — 52 raw findings across 3 specialists, 34 unique actionable findings after skeptic deduplication, 3 P0 and 10 P1 confirmed.

## Status

> ✅ **Re-verified 2026-06-24** — full code check of r2-skeptic Top-5 + key P1s vs current `smartenplus-frontend` + backend: **8 of 9 resolved / not-a-bug**. FE-01 XSS `DOMPurify` ([reviewSlug].js:137), FE-03 parseISO null guards (BookingReviewList.js:41-42/110), FE-14 `next/router` import + no relative pushes, UX-10 `maskEmail(user_info.email)` (ReviewList.js:55), FE-02 `role="radiogroup"`/`radio`+`aria-checked` (RateAndReviewForm.js:129-134), UX-14 `router.push('/rate-review')` (submit-review:152), FE-09/UX-17 `getSiteUrl()` dynamic canonical — all fixed in code. **FE-22 resolved as NOT-a-bug:** backend `ReviewViewSet.get_object` (`dialogue/views.py:1057-1059`) resolves by `booking_item__slug` — exactly the field the redirect pushes (`submit-review/[...slug].js:78`); frontend + backend designed together 2024-12-14 (`2c1fa39e`/`adf89b83`), r2-skeptic's "API-shape unverified" concern answered. **1 residual:** UX-03 (P2) — `useState(5)` default (RateAndReviewForm.js:22); `handleSubmit` l.55-65 appends `rating` with no explicit-selection validation; submit gate l.328 lacks `rating===0` → users who skip the stars submit 5 by default (rating inflation). Audit ~95% implemented.

**COMPLETED** (R1 + Sprint 1 shipped, verified 2026-06-24).

~~IN PROGRESS — Release 1 shipped (P0-1/P0-2/P0-3 + P1-1/P1-2). Sprint 1 (P1-3 through P1-9) pending. FE-22 deferred (API shape unverified).~~

## Key Files

- `r1-ux.md` — UX & Conversion (18 findings)
- `r1-visual.md` — Visual Design (13 findings)
- `r1-frontend.md` — Frontend & Accessibility (22 findings)
- `r2-skeptic.md` — Skeptic debate (34 confirmed/upgraded, 3 dropped, 6 merged/deduplicated)
- `r3-leader-synthesis.md` — Final synthesis & action plan
- `r4-scrutinize.md` — Outsider verification pass (4 corrections to r3)
- `r5-implementation-plan.md` — Release 1 fix spec with exact code + Sprint 1 backlog

## Top P0 Issues

- **Stored XSS**: `pages/rate-review/[reviewSlug].js:455` — `dangerouslySetInnerHTML` without DOMPurify on user-submitted review text. All other review components in the codebase already use DOMPurify. One-line fix.
- **Page crash on null date**: `components/review/BookingReviewList.js:43-45,110` — `parseISO(null)` in sort comparator and render crashes the entire Rate & Review page when any booking has a null `traveling_date`. Two-line fix.
- **Star rating inaccessible to screen readers**: `components/RateAndReview/RateAndReviewForm.js:111-147` — `aria-pressed={value <= rating}` causes multiple simultaneous "pressed" announcements for a single rating. Fix: `radiogroup` + `role="radio"` + `aria-checked={value === rating}`.

## Related

- [[activities-pagination-ux-audit-2026-06-05]]
- [[homepage-uxui-audit-2026-05-31]]

## Orphan Link-Backlog (Linked 2026-06-13)
- [[rate-review-css-audit]] — Rate-review CSS consistency audit (sibling audit; overview is umbrella)
- [[rate-review-page-shell-pattern]] — Rate-review page shell pattern (sibling atomic pattern)
