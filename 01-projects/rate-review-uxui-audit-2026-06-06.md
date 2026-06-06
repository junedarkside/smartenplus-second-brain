# /rate-review UX/UI Audit — 2026-06-06

## Summary

4-specialist adversarial audit of the SmartEnPlus `/rate-review` flow (list, detail, submit-review pages) — 52 raw findings across 3 specialists, 34 unique actionable findings after skeptic deduplication, 3 P0 and 10 P1 confirmed.

## Status

IN PROGRESS — Release 1 shipped (P0-1/P0-2/P0-3 + P1-1/P1-2). Sprint 1 (P1-3 through P1-9) pending. FE-22 deferred (API shape unverified).

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
