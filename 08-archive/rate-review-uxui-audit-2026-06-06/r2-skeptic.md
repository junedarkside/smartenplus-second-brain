# r2-skeptic — Skeptic Debate
**Date:** 2026-06-06
**Reviewer:** Skeptic (cross-specialist audit)
**Sources verified:** BookingReviewList.js, RateAndReviewForm.js, pages/rate-review/index.js, ReviewList.js, submit-review/[...slug].js, [reviewSlug].js (via grep), useAuthRedirect.js

---

## Verdict Table

| ID | Title | Specialist | Original Priority | Verdict | New Priority | Reason |
|----|-------|-----------|------------------|---------|--------------|--------|
| FE-01 | XSS via unsanitized dangerouslySetInnerHTML | Frontend | P0 | **CONFIRMED** | P0 | Verified: line 455 has raw `dangerouslySetInnerHTML={{ __html: formattedText }}` with no DOMPurify. DOMPurify is not imported in [reviewSlug].js at all. |
| FE-02 | Star rating ARIA pattern — aria-pressed vs radiogroup | Frontend | P0 | **CONFIRMED** | P0 | Verified: `aria-pressed={value <= rating}` at line 119 in RateAndReviewForm.js. Multiple simultaneous "pressed" states is semantically incorrect for a mutually exclusive control. Real WCAG 1.3.1 violation. |
| FE-03 | parseISO(null) crash — unguarded date parsing | Frontend | P0 | **CONFIRMED** | P0 | Verified: BookingReviewList.js lines 44-45 and 110 call parseISO on `booking.traveling_date` with zero null guard. One bad API record kills the entire page. |
| FE-14 | router.push paths missing leading slash + wrong router import | Frontend | P2 | **UPGRADE** | P1 | Verified: BookingReviewList.js line 2 imports `useRouter` from `next/navigation` (App Router), line 185-186 uses relative paths `rate-review/...` (no leading /). This is not speculative — on any URL other than `/` the push will produce `/rate-review/rate-review/...`. Core navigation action broken. Deserves P1. |
| UX-15 | BookingReviewList relative path bug | UX | P1 | **DUPLICATE of FE-14** | — | Same finding. FE-14 is more complete (also catches wrong router import). Drop UX-15 as standalone; merged into FE-14. |
| UX-10 | ReviewList shows raw email — privacy leak | UX | P1 | **CONFIRMED** | P1 | Verified: ReviewList.js lines 53-56 render `review.user_info.email` unmasked. `maskEmail` is defined in same file and used for guest_email but NOT for user_info.email. Real GDPR/PDPA violation. |
| FE-04 | text-gray-400 caption fails WCAG AA contrast | Frontend | P1 | **CONFIRMED** | P1 | Verified: RateAndReviewForm.js line 262 uses `text-gray-400` (Tailwind #9CA3AF). Contrast ratio ~2.85:1 on white. WCAG 1.4.3 requires 4.5:1 for normal text. Confirmed violation. |
| FE-05 | Image thumbnails not keyboard accessible | Frontend | P1 | **CONFIRMED** | P1 | Verified via r1-frontend: div with onClick, no role, no tabIndex, no onKeyDown. Clear WCAG 2.1.1 violation. |
| UX-05 | Post-submission redirect may 404 | UX | P1 | **CONFIRMED but severity questioned** | P1 | Verified: [slug].js line 72 redirects to `review.data.booking_item_slug` while the guard checks `review?.data?.slug`. If booking_item_slug and slug are the same field, this is fine; if different, it's a real bug. FE-22 catches the guard mismatch independently. Both valid. Keep both. |
| FE-22 | handleReviewCreated guards on slug but redirects on booking_item_slug | Frontend | P2 | **UPGRADE** | P1 | Verified: line 71 checks `review?.data?.slug` but line 72 uses `review.data.booking_item_slug`. If slug exists but booking_item_slug is null, push produces `/rate-review/undefined`. Directly causes UX-05's feared 404. Should be P1. |
| UX-03 | Default star rating of 5 is a dark pattern | UX | P1 | **DOWNGRADE** | P2 | Verified: `useState(5)` at line 22. The "dark pattern" label is overwrought — pre-selecting a rating is common in review UIs (Amazon, TripAdvisor). The real concern is rating inflation and accidental 5-star submissions. That's a product quality issue, not a conversion-blocker. Also: if UX-04 is fixed (button stays disabled until title + text are filled), the user must actively engage with the form — they are likely to interact with stars too. Downgrade to P2 with the fix: require title + text + non-zero rating to enable submit. |
| UX-04 | Submit button disabled with no explanation | UX | P1 | **CONFIRMED** | P1 | Verified: line 291 disables when `title.length === 0 || reviewText.length === 0`. No helper text on blur, no tooltip, no inline validation. Users who fill only one field see nothing. Real friction. |
| FE-09 | Canonical URL missing www on all three pages | Frontend | P1 | **CONFIRMED** | P1 | Verified: index.js line 56 hardcodes `https://smartenplus.co.th/rate-review`. Violates CLAUDE.md canonical rule. FE-09 and UX-17 are the same finding — see Conflicts section. |
| UX-17 | SEO canonical URL wrong on review detail page | UX | P1 | **DUPLICATE of FE-09** | — | Same root issue (no www). FE-09 is more complete (covers all 3 pages). Drop UX-17 as standalone; note that UX-17 also identifies that all review detail pages share the same canonical — the list page URL — which FE-09 does not fully address. Merge: fix per-page dynamic canonical. |
| FE-08 | All three pages missing noindex | Frontend | P1 | **DOWNGRADE** | P2 | The index page redirect for unauthenticated users means crawlers don't get content — but they do get a 200 with empty HTML. The submit-review token URL being crawled is a mild concern (token is opaque, not PII). The review detail page being publicly indexed is actually desirable SEO. noindex on the detail page would be wrong. Split: (a) index.js and submit-review should get noindex (P2), (b) [reviewSlug].js should NOT get noindex. Report overstates this as uniform P1. |
| UX-01 | Silent cold redirect for guest users | UX | P0 | **DOWNGRADE** | P1 | Verified: useAuthRedirect.js just calls `router.push` to signin page. The callbackUrl IS preserved (router.asPath). The finding that there's no interstitial is real. However, "cold redirect to login" is standard practice for auth-gated pages — not unusual enough to be P0. The bounce rate claim is speculative. The user WILL be returned to /rate-review after login via callbackUrl. Downgrade to P1 for the missing "why you need to log in" copy, but it is not a conversion blocker at the level of a XSS or crash. |
| UX-02 | Loading state blank flash | UX | P1 | **DOWNGRADE** | P2 | Verified: `loading` initialized to `false` in index.js. During NextAuth status === 'loading', nothing shows. This IS a real flash — but it's a cosmetic loading-state issue, not a conversion killer. The actual skeleton IS shown during the API call. The flash before redirect is milliseconds on normal connections. Downgrade to P2. |
| FE-11 | router in useEffect deps — unused | Frontend | P2 | **CONFIRMED** | P2 | Verified: index.js line 48 has `[session, router]` but `router` is not used inside the effect body at all. It just calls `handleUnauthenticated()` (which has its own internal router) and `axios.get`. The `router` dep is spurious lint violation and causes redundant API calls on query param changes. |
| FE-13 | setError may set undefined | Frontend | P2 | **CONFIRMED** | P2 | Verified: line 90 of RateAndReviewForm.js is exactly `setError(error?.response?.data?.detail)`. Network timeouts and 500s with non-standard bodies will silently swallow the error. Real silent failure path. |
| UX-06 | Error uses raw API error string | UX | P1 | **DOWNGRADE** | P2 | Same issue as FE-13 but from UX angle. Verified the catch block. The fix is the same: add a fallback string. However, showing the raw Django message ("This field may not be blank") is bad but not blocking. Downgrade — UX-06 and FE-13 are the same fix. Merged to P2. |
| UX-14 | Cancel button routes to homepage | UX | P2 | **CONFIRMED** | P2 | Verified: [slug].js line 142 has `onClose={() => router.push('/')}`. The back button at line 97 correctly goes to `/rate-review`. So there are TWO back paths: the back IconButton routes correctly, but Cancel routes to homepage. This is confusing inconsistency. P2 confirmed. |
| FE-06 | Back IconButton has no accessible label | Frontend | P1 | **CONFIRMED** | P1 | Tooltip.title does not propagate aria-label to the button in MUI v5. button with only an icon and no aria-label announces as "button". WCAG 4.1.2 violation confirmed. |
| FE-07 | Sort button has no aria-label for toggle state | Frontend | P1 | **DOWNGRADE** | P2 | The button already has visible text "Sort by Date (Ascending/Descending)" which screen readers will read. The text encodes current state. The missing piece is the toggle announcement — this is WCAG 4.1.2 medium, not high. Report filed it as P1. Downgrade to P2. The visual presentation issue (looks like a link, UX-09) is the bigger problem. |
| UX-09 | Sort button looks like a link, not a control | UX | P2 | **CONFIRMED** | P2 | Verified: `className="text-fb-blue text-sm hover:underline"` at line 83 in BookingReviewList.js. Looks like a hyperlink. Correct P2. |
| UX-07 | No feedback when >5 photos selected | UX | P1 | **DOWNGRADE** | P2 | Verified: `slice(0, 5)` at line 241 with no user notification. This is real but it's not P1 — the user doesn't lose saved data or hit a broken state. They just get fewer photos than expected. A missing toast warning is P2 at most. |
| UX-08 | No individual photo removal | UX | P2 | **CONFIRMED** | P2 | Verified: no × button on previews. Must re-select all to change selection. Real friction especially mobile. P2 correct. |
| FE-15 | onClose called without guard | Frontend | P2 | **DOWNGRADE** | P3 | The component is currently only used in [slug].js which always provides `onClose`. The risk is future misuse. This is a defensive programming gap, not a live bug. P3 appropriate. |
| VIS-01 | Hardcoded star color #FFA000 | Visual | P1 | **DOWNGRADE** | P3 | Design token drift is real but #FFA000 is intentionally chosen amber for stars — it's not a wrong color, just an unregistered token. The two-hex-value mismatch between components (#FFA000 vs #F59E0B) is visually indistinguishable at 11px-16px sizes. No user impact. This is developer hygiene, not a UI defect. P3. |
| VIS-02 | gap-0 collapses vertical rhythm | Visual | P1 | **DOWNGRADE** | P3 | Verified: `gap-0` on a wrapper that contains a single child (`BookingReviewList`). Since there's only one child, gap-0 has no visual effect — there are no siblings to gap between inside this div. The outer section does provide spacing via px-2 md:px-3. The "collapsed vertical rhythm" claim is technically correct (it should be gap-4 to match detail page) but has zero visible impact with a single child. P3 — cosmetic consistency only. |
| VIS-03 | Hardcoded #3b5998 on back button | Visual | P1 | **DOWNGRADE** | P3 | Real design token violation, confirmed at [slug].js line 100. But #3b5998 IS COLORS.brand.primary — it's the exact same hex value, just not using the constant. Zero visual difference. Pure developer hygiene. P3. FE-18 is the same finding. |
| FE-18 | Hardcoded #3b5998 bypasses design token | Frontend | P3 | **DUPLICATE of VIS-03** | P3 | Same finding, same location. Keep one. |
| VIS-04 | Native file input — visual mismatch with MUI | Visual | P1 | **DOWNGRADE** | P2 | Verified: native `<input type="file">` in an otherwise MUI form. The visual mismatch is real and noticeable. However "jarring" is subjective — the Tailwind file: pseudo-class styling does soften it. This is a real visual consistency issue worth fixing. P2, not P1. The UX-07 fix (photo count warning) is a more urgent companion to this. |
| VIS-05 | Missing page title/section heading | Visual | P2 | **CONFIRMED** | P2 | Overlaps with UX-18. Verified: no h1 on index page. The "Rate & Review" Typography in BookingReviewList is text-lg (not h1). Both specialists flag this — it's confirmed. |
| UX-18 | No page-level H1 on reviews list index | UX | P2 | **DUPLICATE of VIS-05** | — | Same finding. Keep VIS-05/UX-18 combined. |
| VIS-06 | Star size 44px too large for card | Visual | P2 | **DROP** | — | The 44px is the touch target (IconButton minHeight/minWidth: 44px). The visual star icon at 44px inside the button IS large, but that's a product decision about the prominence of the rating widget in the submission form. The report itself acknowledges the 44px touch target is WCAG-appropriate. Recommending a reduction to 36px is a preference, not a defect. Drop. |
| VIS-07 | Loading spinner missing brand color | Visual | P2 | **DOWNGRADE** | P3 | Verified: no sx color on CircularProgress in [slug].js:82. MUI default blue is different from brand primary, but this spinner shows for under 1 second during bookmark load. Zero user impact on the experience. P3 cosmetic. |
| VIS-08 | EmptyState variant="completed" semantic mismatch | Visual | P2 | **CONFIRMED** | P2 | Verified: `variant="completed"` with a green CheckCircle icon when user has zero reviews. This sends a false positive "success" signal. A first-use or no-results variant is more honest. P2 correct. |
| VIS-09 | ListSkeleton column vs grid layout mismatch | Visual | P2 | **DOWNGRADE** | P3 | The skeleton shows a single-column flex layout while the loaded state is a 3-column grid. This causes layout shift on load. Layout shift is real, but it lasts under 200ms (skeleton shows only during the API call). The visual discontinuity is noticeable but not blocking. P3. |
| VIS-10 | Action button hover uses wrong token | Visual | P2 | **DROP** | — | Verified: `hover:bg-blue-600` = #2563EB. COLORS.brand.secondary = #2563eb. They are identical hex values. The claim that this is semantically wrong (hover should use primaryDark #2d4373) may be a valid design preference, but the CURRENT color is indistinguishable from the intended secondary token. No visible mismatch today. Drop as nitpick. |
| VIS-11 | 136-line commented-out dead code | Visual | P3 | **CONFIRMED** | P3 | Duplicate of UX-11 and FE code quality table. All three specialists agree. P3 correct. |
| VIS-12 | Duplicate return normalized | Visual | P3 | **CONFIRMED** | P3 | Duplicate of UX-12 and FE-12. All three agree. P3 correct. |
| VIS-13 | text-fb-blue inconsistency (Tailwind vs COLORS import) | Visual | P3 | **DROP** | — | Visual specialist themselves says "No code change needed" and notes this is the CORRECT approach. Should not appear as a finding at all. Drop. |
| UX-11 | [reviewSlug].js 136 lines dead code | UX | P3 | **CONFIRMED** | P3 | All three specialists flag. Trivial fix. |
| UX-12 | Duplicate return normalized | UX | P2 | **DOWNGRADE** | P3 | All three flag this. It's dead code with zero runtime impact. P3 not P2. |
| FE-12 | Duplicate return normalized | Frontend | P2 | **DOWNGRADE** | P3 | Same as UX-12. P3. |
| UX-13 | Booking slug shown as heading exposes internal ID | UX | P2 | **DOWNGRADE** | P3 | The booking slug (e.g., BK-2025-0412-7XX) in a heading is low-value UX noise. But "exposes internal slug" overstates the risk — booking slugs are user-facing identifiers shown in email confirmations too. This is a UX improvement (show trip name instead), not a security or functional issue. P3. |
| UX-16 | Empty state has no CTA | UX | P2 | **CONFIRMED** | P2 | Verified: EmptyState with `variant="completed"` and no ctaText/ctaHref. Dead end for users with no reviewable bookings. P2 correct. |
| FE-10 | Dead import ReviewList in index.js | Frontend | P2 | **CONFIRMED** | P3 | Verified: index.js line 6 imports ReviewList but it is never rendered. Dead import confirmed. However this is trivial cleanup — one line delete. P3, not P2. |
| FE-16 | aria-required on MUI TextField wrapper div | Frontend | P2 | **CONFIRMED** | P2 | Verified: `aria-required="true"` at lines 175 and 212 of RateAndReviewForm.js. MUI TextField does not forward unknown props to the inner input. Attribute is effectively on the wrapper div and screen readers won't see it. Real WCAG gap, though somewhat low-impact since the label text and required state are visually clear. P2 correct. |
| FE-17 | Photo preview alt generic | Frontend | P3 | **CONFIRMED** | P3 | "Preview 1" is non-meaningful alt. Real WCAG 1.1.1 issue but extremely low impact — user just selected the photo, they know what it is. P3 correct. |
| FE-19 | Star icon #D1D5DB fails WCAG 1.4.11 non-text contrast | Frontend | P3 | **UPGRADE** | P2 | The empty star at #D1D5DB on white is ~1.62:1 — fails WCAG 1.4.11 Non-text Contrast (requires 3:1). This is different from VIS-01's token drift claim. The actual contrast failure for the inactive star state is a real accessibility violation that affects users with low vision who are trying to see how many stars they have selected. P2. |
| FE-20 | No error boundary on BookingReviewList | Frontend | P2 | **DOWNGRADE** | P3 | FE-03 already addresses the root cause (parseISO null crash). An error boundary is a belt-and-suspenders measure. Once FE-03 is fixed, the missing error boundary is just defensive programming. P3. |
| FE-21 | Network error on fetch shows EmptyState | Frontend | P2 | **CONFIRMED** | P2 | Verified: catch block in index.js line 39-41 only calls `console.error`. User sees "No reviews yet" whether the API failed or they genuinely have none. Meaningful distinction for user. P2 correct. |

---

## Confirmed Critical (keep as-is)

**P0 — Must fix before next release:**

1. **FE-01 — XSS in [reviewSlug].js**: `dangerouslySetInnerHTML` with no sanitization. DOMPurify is not even imported in this file. Pattern already established in ReviewList.js — one-line fix. Stored XSS affecting all review viewers.

2. **FE-02 — Star ARIA pattern**: `aria-pressed={value <= rating}` causes screen readers to announce multiple simultaneously "pressed" buttons for a single rating. Real WCAG 1.3.1 Level A violation. Fix: `radiogroup` + `role="radio"` + `aria-checked={value === rating}`.

3. **FE-03 — parseISO(null) crash**: Zero null guard on `booking.traveling_date` in both the `.sort()` comparator and the render `format()` call. One API record with null date kills the entire Rate & Review page for the authenticated user.

---

## Downgraded Findings

- **UX-01** (P0→P1): Auth redirect without interstitial is standard practice. callbackUrl IS preserved. Downgrade; the bounce risk is real but not P0.
- **UX-02** (P1→P2): Blank flash before redirect is cosmetic and sub-second on normal connections.
- **UX-03** (P1→P2): "Dark pattern" label overstated. Default-5-stars is common. The real fix is requiring an explicit star selection as part of submit validation — a product decision, not a conversion blocker.
- **UX-06** / **FE-13** (P1→P2): Raw API error string is bad UX but not blocking. Same fix as FE-13's fallback string.
- **UX-07** (P1→P2): Silent photo truncation is annoying, not blocking. No data loss — user sees fewer thumbnails and can investigate.
- **FE-07** (P1→P2): Sort button has visible text encoding current state. Toggle semantics gap is medium, not high.
- **FE-08** (P1→P2): noindex on submit-review and index is appropriate; noindex on [reviewSlug].js review detail pages is wrong — those pages SHOULD be indexed.
- **FE-14** (P2→P1): Upgraded. Wrong router import + relative paths is a confirmed navigation failure bug on the core user action.
- **FE-22** (P2→P1): Upgraded. Guard/redirect field mismatch causes `/rate-review/undefined` redirect after successful submission.
- **FE-19** (P3→P2): Upgraded. #D1D5DB empty star fails WCAG 1.4.11 non-text contrast (~1.62:1, needs 3:1). Real accessibility defect.
- **VIS-01** (P1→P3): Token drift only. #FFA000 ≠ #F59E0B but visually indistinguishable at star sizes. No user impact.
- **VIS-02** (P1→P3): gap-0 on a single-child wrapper has zero visible effect. Cosmetic consistency only.
- **VIS-03** (P1→P3): #3b5998 IS COLORS.brand.primary. Same hex, different reference. Zero visual difference.
- **VIS-04** (P1→P2): Native file input mismatch is real but softer than "jarring."
- **VIS-07** (P2→P3): Sub-second spinner color difference. Zero user impact.
- **UX-12** / **FE-12** (P2→P3): Dead code. No runtime impact. Trivial cleanup.
- **FE-10** (P2→P3): Dead import — one line delete. Not P2.
- **FE-20** (P2→P3): Belt-and-suspenders after FE-03 fix. Not urgent.
- **UX-13** (P2→P3): Booking slugs are user-facing identifiers, not secret internals. Not a security issue.

---

## Dropped Findings

- **VIS-06 — Star size 44px "too large"**: The 44px is the IconButton touch target, which is the WCAG minimum. The star icon size is a subjective product choice. Not a defect.
- **VIS-10 — Action button hover wrong token**: `hover:bg-blue-600` = #2563EB = COLORS.brand.secondary exactly. Identical hex value. No visual difference today. Pure token labeling concern.
- **VIS-13 — text-fb-blue Tailwind vs COLORS import inconsistency**: Visual specialist themselves says no code change needed. Should not be a finding.

---

## Conflicts Between Specialists

### Conflict 1: FE-09 (canonical URLs) vs UX-17 (same finding)
Both UX and Frontend report the missing `www.` in canonical URLs. They agree on the root cause. However, **UX-17 identifies an additional problem FE-09 misses**: the review detail page uses the same canonical for every detail page (`/rate-review` for all), which is a more severe SEO issue than the www/non-www problem alone. **Winner: take UX-17's scope (per-page dynamic canonical) AND FE-09's fix method (getSiteUrl()).** Neither alone is complete.

### Conflict 2: FE-08 (noindex all pages) vs UX-17 (canonical on detail page)
Frontend says noindex the review detail page if no review data. UX says fix the canonical on the detail page. These conflict: if detail pages should be noindexed (FE-08), fixing their canonical is pointless. **Winner: UX specialist is correct.** Review detail pages with real content are desirable SEO targets — publicly accessible reviews with trip context are indexable content. noindex belongs only on index.js (auth-gated empty page) and submit-review (token URLs). FE-08 is overcorrected for the detail page.

### Conflict 3: UX-03 (5-star default = dark pattern) vs no Frontend flag
Only UX flags the default `rating: 5`. Frontend does not flag it as a concern. **Verdict: UX is right to flag it as a product integrity issue, but wrong to call it a "dark pattern."** A dark pattern requires intentional deception. Pre-selecting 5 stars is sloppy defaults, not deception. The fix (require explicit star selection in submit validation) is valid but not P1.

### Conflict 4: FE-14 (wrong router import) vs UX-15 (relative path only)
UX-15 only identifies the missing leading slash. FE-14 identifies both the wrong router import (`next/navigation` in a Pages Router app) AND the missing slash. **Winner: FE-14.** The wrong import is the more fundamental issue — `useRouter` from `next/navigation` in a Pages Router context is undefined behavior that may break on Next.js version upgrades even if paths are fixed. Fix both: change import + add leading slashes.

---

## Skeptic's Top 5 (findings that truly matter)

**Ordered by real-world damage if left unfixed:**

### 1. FE-01 — Stored XSS in review detail page
A user who submitted a review with `<script>alert(1)</script>` or `<img onerror="...">` content will have that executed in every viewer's browser. This is not theoretical — the review submission form sends user-controlled text directly to the database, and [reviewSlug].js renders it with `dangerouslySetInnerHTML` without DOMPurify. Every other page in the codebase (ReviewList.js, ReviewDetailModal.js, ReviewFirstPage.js) already uses DOMPurify. This file was missed. **One-line fix, P0, ship immediately.**

### 2. FE-03 — parseISO(null) crashes the entire Rate & Review page
The sort comparator and date render in BookingReviewList.js have no null guard on `traveling_date`. A single booking with a null date from the API silently crashes the entire component with a RangeError. The user sees a blank page with no recovery. Given the backend may return null for upcoming or incorrectly entered bookings, this is a latent bomb. **Two-line fix, P0.**

### 3. FE-14 — Wrong router import breaks "Write Review" and "View Review" navigation
BookingReviewList.js imports `useRouter` from `next/navigation` (Next.js App Router) while running in a Pages Router project. The relative push paths `rate-review/${booking.slug}` compound the error — on the `/rate-review` URL path this accidentally works, but the behavior is undefined and fragile. This is the primary CTA button for the entire review flow. **Two-line fix (change import + add leading slashes), upgrade to P1.**

### 4. UX-10 — Unmasked email addresses in ReviewList
ReviewList.js applies `maskEmail()` to guest emails but renders `review.user_info.email` raw for authenticated user emails. This exposes full email addresses (e.g., `june@example.com`) to any viewer of the review list. GDPR/PDPA compliance risk. The fix is already defined in the same file — apply `maskEmail()` to `user_info.email`. **One-line fix, P1.**

### 5. FE-02 — Star rating ARIA pattern breaks screen reader accessibility for a core interaction
`aria-pressed={value <= rating}` tells screen readers every star up to the current rating is a separately-toggled button that is "pressed." A user selecting 3 stars hears three separate "pressed" announcements. The correct pattern (radiogroup + radio + aria-checked) exists in the WCAG reference examples and is already available in the component structure (ratingLabels are already defined). Fixing this makes the most critical input widget in the form accessible to blind users. **~20 line refactor, P0.**

---

*Skeptic notes: The three specialist reports are generally high quality and well-sourced — most findings verified in code. The main failure modes were: (1) Visual labeling UX and developer hygiene issues as P1 when no visible user impact exists; (2) UX using "dark pattern" for what is a defaults/product quality issue; (3) duplicate findings across reports inflate perceived severity by repetition. After deduplication and downgrading, the truly actionable P0/P1 list is shorter but unambiguous.*
