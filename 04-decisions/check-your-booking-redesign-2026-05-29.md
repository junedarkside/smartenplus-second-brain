# Check Your Booking — Redesign Decision

## Summary (v2 — CURRENT)

2-column reference-image layout adopted. Left branding panel (icon badge + headline + trust icons) / right form (visible labels + icon inputs + CTA + Order ID fallback link). 3-agent debate (FOR/AGAINST/JUDGE). Judge applied 4 modifications to reference image before implementing.

**v1 (centered card, warm-surface bg):** Rejected by user. Superseded by v2.

---

## v2 Decision (2026-05-29 session #4)

### Judge Ruling (4 modifications to reference image)

| Element | Reference Image | Adopted Value | Reason |
|---------|----------------|---------------|--------|
| CTA color | #4F46E5 indigo | `fb-blue` #1E40AF | Brand consistency — all other CTAs on site use fb-blue |
| Tab toggle | Removed (Booking ID only) | Removed UI, added text link "Have an Order ID?" below CTA | Preserves Order ID route without full toggle UI |
| Headline | "Manage Your Booking" | "Check Your Booking" | Feature is read-only retrieval, not true management |
| Trust icon gap | gap-6 | gap-4 | Prevents overflow on 13" laptops at 768–900px |

### v2 Implementation

- `MyBookingsSection.js` — 2-column (`lg:flex-row`), left branding panel, right form, footer security row
- `BookingRetrievalForm.js` — visible labels, icon suffixes in inputs, `useOrderId` boolean state + text link, `bg-fb-blue` CTA + arrow
- `pages/homepagev2.js` — skeleton updated to match 2-column layout, `max-w-[1000px]`

### v2 Debate Outcomes

**FOR won:** 2-column layout, visible labels (WCAG 2.4.6), icon badge, trust icon row, footer security row, icon suffixes in inputs

**AGAINST won:** Color kept as fb-blue, Order ID access preserved via text link, breakpoint raised to lg: (1024px), trust icon gap reduced

---

## v1 Decision (superseded)

### Context (v1)

- **Date:** 2026-05-29
- **Branch:** `260528-feat/header-redesign-2026`
- **Files changed:** `MyBookingsSection.js`, `BookingRetrievalForm.js`, `pages/homepagev2.js`
- **Trigger:** User-requested redesign to match Booking.com / Agoda / airline manage-booking aesthetic

## Problem

Original design felt like a customer support portal:
- 50/50 split: decorative travel photo (left) + icon+heading+small form (right)
- `ContentCard` wrapper with `rounded-md shadow-xl`
- `py-2` inputs (~36px) below WCAG 2.5.5 touch target minimum
- No visual hierarchy distinguishing this as a utility section vs browse section

## Decision

**Adopt the OTA utility card redesign with 2 judge-ordered modifications.**

### What Was Adopted

| Element | Old | New | Reason |
|---------|-----|-----|--------|
| Layout | 50/50 split w/ photo | Single centered 840px card | Photo signals "browse" not "retrieve" |
| Section bg | White (same as page) | `bg-warm-surface` (#FAFAF8) | Zone break for page scanners |
| Card | `ContentCard rounded-md shadow-xl` | Raw div `rounded-2xl shadow-md` | ContentCard can't be overridden; `rounded-2xl` scoped exception |
| Input height | `py-2` ~36px | `py-3` ~44px | WCAG 2.5.5 compliance |
| Input border | `border-gray-300 rounded-md` | `border-gray-200 rounded-xl` | Modern affordance, consistent radius language |
| Submit button | `py-2 rounded-md text-sm font-medium` | `py-3 rounded-xl text-base font-semibold` | Touch target + visual weight |
| Image import | `myBooking` JPEG imported | Removed entirely | Unused after redesign |

### What Was Modified (Judge's ruling)

1. **Eyebrow label removed.** Original spec included "Manage Your Trip" as an eyebrow above the headline. Judge ruled it adds ambiguity ("manage" implies cancel/modify scope) and a redundant reading step. Removed. Strong `text-2xl md:text-3xl` headline "Check Your Booking" is self-sufficient.

2. **Trust row copy fixed.** "✓ Instant confirmation" was misleading for a *retrieval* flow (not a new booking). Replaced with "✓ Find your ticket in seconds". Final trust row: "✓ Find your ticket in seconds ✓ Secure booking ✓ English support".

## Tradeoffs

### FOR (upheld by judge)
- Illustration removal correct — photo is already `hidden` on mobile, proving low utility
- 840px width appropriate — line length and cognitive focus improvement
- Warm surface background creates useful zone break without heavy visual device
- Input sizing is WCAG compliance fix regardless of broader design
- Trust row kept (with fixed copy) — returning users are highest-anxiety funnel moment; "English support" uniquely relevant for Thailand tourist platform

### AGAINST (upheld by judge)
- Eyebrow label "Manage Your Trip" too vague — removed
- "✓ Instant confirmation" misleading in retrieval context — replaced
- `rounded-2xl` is a design system exception — accepted as scoped, documented with inline comment, tracked as future design system token candidate

### AGAINST (rejected by judge)
- "720px input for 10 chars looks absurd" — misread; input width is about label/placeholder readability, not final value length
- "Breaks visual rhythm with 1200px sections" — warm-surface band + card centering is a standard content-in-band pattern; intentional differentiation is valid
- "Photo anchors brand" — logo/nav handle brand recognition; section-level illustration conflates two functions

## Final Implementation

```
components/FrontPage/MyBookingsSection.js — full rewrite
  - No more: Image, ContentCard, ConfirmationNumberOutlinedIcon
  - New: warm-surface outer section, 840px white rounded-2xl card
  - headline → trust row (no eyebrow)

components/FrontPage/BookingRetrievalForm.js — visual restyle only
  - Logic/routing: unchanged
  - Inputs: py-3 px-4 rounded-xl border-gray-200 focus:ring-fb-blue
  - Button: py-3 rounded-xl text-base font-semibold

pages/homepagev2.js — two targeted changes
  - Removed: import myBooking from '../public/assets/my-booking.jpeg'
  - Removed: myBooking prop from <MyBookingsSection />
  - Updated: skeleton loader matches new warm-surface card layout
```

## Related

- [[master-state]] — branch status
- [[header-redesign-2026-spec]] — broader homepage redesign context
