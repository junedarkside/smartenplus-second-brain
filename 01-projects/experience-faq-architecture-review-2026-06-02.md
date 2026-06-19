# Experience FAQ — Architecture Review & Single Source of Truth

**Status:** Decision recorded, not yet implemented
**Date:** 2026-06-02
**Reviewer:** Senior Staff Engineer (AI session #32)
**Repos affected:** smartenplus-frontend, admin-dashboard (backend: zero changes)

---

## Summary

FAQ section on experience detail page is partially hardcoded. Two items always render regardless of operator data. One hardcoded item is factually incorrect for strict-policy operators (legal/trust risk). One assumed API field (`cancellation_policy.description`) does not exist. `age_restriction` is editable in Django admin but missing from the Next.js admin dashboard.

**Follow-up:** [[not-suitable-for-section-2026-06-18]] surfaces these eligibility constraints as a dedicated operator-authored section (not buried in FAQ), adds admin multi-select, JSONField enum on Contract.

---

## Current State Cross-Repo Map

| FAQ Item | Backend | API | Admin Dashboard | Frontend |
|----------|---------|-----|-----------------|----------|
| "What should I bring?" | `what_to_bring` TextField ✅ | Exposed ✅ | Editable ✅ | Rendered ✅ |
| "Are there age restrictions?" | `age_restriction` CharField ✅ | Exposed ✅ | **MISSING ❌** | Rendered ✅ |
| "How difficult is this?" | `difficulty_level` ✅ | Exposed ✅ | Editable ✅ | Mapped locally ✅ |
| "Can I cancel?" | `cancellation_policies.cancellation_details[]` ✅ | Structured object ✅ | Editable (FK selector) ✅ | **HARDCODED string ❌** |
| "Is this suitable for first-time?" | **Does not exist** ❌ | N/A | N/A | **Generic filler ❌** |

---

## Critical Issues (Blockers)

### 1. Hardcoded cancellation text is a legal/trust liability

"Many of our experiences offer free cancellation up to 24 hours" is factually wrong for any operator with a stricter policy. A traveler reading this, cancelling 25hrs before, then getting charged full price will dispute. This cannot remain as a fallback without qualification ("See your specific policy terms").

### 2. `cancellation_policy.description` does not exist

The proposal assumed a `description` text field on the cancellation policy object. It does not exist. The actual structure is:
```js
cancellation_policies: {
  id, name,
  cancellation_details: [
    { priority, refund_percentage, fixed_amount, condition_hours }
  ]
}
```
Wiring `.description` silently renders `undefined`, falls back to hardcoded text — bug invisible in testing.

### 3. `DayTripContent.js` is a ghost component

Renders `age_restriction` as a blue info box but is never imported in `DayTripDetailPage.js`. Causes confusion — next developer may re-introduce it, creating double render. Must be deprecated/deleted.

---

## Team Debate: Should We Build a Generic `ContractFAQ` Model?

| Approach | Pros | Cons |
|----------|------|------|
| Generic `ContractFAQ` DB model | Operators write custom Q&A per tour | Django migration + serializer + admin UI + frontend mapper = 4 repos, High complexity |
| Use existing fields as FAQ source (recommended) | Zero new models, already in API | Fixed FAQ set, no custom operator Q&A |

**Resolution: Do NOT build `ContractFAQ` today.** Conditions not met:
- No operators requesting custom FAQ authoring
- < 50 active contracts, no per-contract FAQ divergence observed
- Existing structured fields cover all real use cases

**Trigger for migration:** An operator needs a FAQ item that cannot be derived from any existing contract field. Until that happens, the `buildExperienceFAQItems(contract)` utility pattern is correct.

---

## Recommended Architecture

```
contract fields (API data)
       |
       v
buildExperienceFAQItems(contract)   ← pure function, testable, single place to change
       |
       v
ExperienceFAQ({ items })            ← dumb renderer, no business logic
```

`ExperienceFAQ.js` becomes a pure rendering component. All item-building logic moves to `helpers/experienceFAQBuilder.js`. One file to update when FAQ logic changes.

---

## Recommended Changes (Prioritized)

### P0 — Remove hardcoded filler (30 min, frontend only)
**Remove** "Is this suitable for first-time visitors?" from `ExperienceFAQ.js`. Generic marketing copy, inaccurate for challenging tours.

### P1 — Fix cancellation FAQ with derived text (2hr, frontend only)
Build `buildCancellationSummary(cancellationDetails)` pure function:
- Input: `contract.cancellation_policies.cancellation_details[]`
- Output: 1–2 sentence string e.g. "Full refund if cancelled more than 48hrs before. No refund within 48hrs."
- Fallback if null: "Cancellation terms vary by tour. Contact us or check the booking panel for specific terms." (removes false promise)
- Wire via new prop: `DayTripDetailPage` passes `contract.cancellation_policies` to `ExperienceFAQ`

### P1 — Add `ageRestriction` to admin dashboard (2hr, admin-dashboard only)
4 files to touch:
- `components/contract/DayTripDetails.js` — add TextField input
- `hooks/useContractFormData.js` — add `ageRestriction: data?.age_restriction || ''`
- `utils/contractUtils.js` — add `ageRestriction: 'age_restriction'` to `DAY_TRIP_FIELDS` + `DAY_TRIP_FIELD_MAP`
- `constants/contractFieldHelp.js` — add helper text:
  > "Age requirements for participants. Leave blank if none. Example: Minimum age 7 years. Children under 12 must be accompanied by an adult."

Validation: `Yup.string().max(300).nullable()` — optional field.

### P2 — Extract `buildExperienceFAQItems()` utility (1hr, frontend)
Move inline item-building logic from `ExperienceFAQ.js` to `helpers/experienceFAQBuilder.js`. Pure function, independently testable, single place for all future FAQ changes.

### P2 — Deprecate `DayTripContent.js` (15min, frontend)
Add `@deprecated` comment block. Confirm no other imports with `grep -r "DayTripContent"`. Delete in follow-up.

### P3 — Move `age_restriction` to Participant Requirements section (3hr, frontend)
`age_restriction` is a booking-blocking constraint — parents with young children need to see it before booking, not buried in a collapsed FAQ. Move primary display to `WhyTravelersLove` or a new `ParticipantRequirements` card. Keep as secondary FAQ item too.

---

## Nice-to-Have

- Add `maxLength={300}` counter to `ageRestriction` admin field
- Link "Can I cancel?" FAQ answer to cancellation policy section in booking panel (anchor link)
- Add `See full cancellation terms` link in FAQ answer

---

## Implementation Complexity

| Change | Complexity | Repos |
|--------|-----------|-------|
| Remove "Is this suitable for first-time?" | Low | frontend (1 line) |
| Build `buildCancellationSummary()` + wire | Medium | frontend (3 files) |
| Add `ageRestriction` to admin form | Low-Medium | admin-dashboard (4 files) |
| Extract `buildExperienceFAQItems()` | Low | frontend (2 files) |
| Deprecate `DayTripContent.js` | Low | frontend (1 file) |
| Move `age_restriction` to Participant Req. section | Medium | frontend (1-2 components) |
| Generic `ContractFAQ` DB model | **High — defer** | All 3 repos |

---

## What Does NOT Need to Change

- Backend: zero changes. All fields exist and are exposed in API.
- `CancellationPolicy.js` component (used for transportation): untouched.
- Any existing booking/payment logic: untouched.

---

## Related

- [[experience-detail-page-redesign-2026-06-02]] — parent redesign
- [[experience-detail-ipad-mobile-redesign-2026-06-02]] — tablet/mobile layout

## Related Atoms (Extracted 2026-06-13)
- [[build-experience-faq-items-pure-function]] — pure `buildExperienceFAQItems(contract)` helper; derive cancellation text from structured data (legal liability pattern)
