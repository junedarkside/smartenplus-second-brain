# Build Experience FAQ Items as Pure Function

## Summary
Extract FAQ item-building logic from `ExperienceFAQ.js` to `helpers/experienceFAQBuilder.js` as a pure function `buildExperienceFAQItems(contract)`. Component becomes dumb renderer. Build `buildCancellationSummary(cancellationDetails)` companion function to derive "Full refund if cancelled >48hrs before. No refund within 48hrs." from structured data, NOT hardcoded "24 hours" string (legal risk for stricter operators).

## Context
`ExperienceFAQ.js` is a React component that renders FAQ items for a contract's experience page. The current implementation has FAQ building logic inline — it's mixed with rendering, hard to test, and contains at least one factually wrong hardcoded string (cancellation window).

## Problem
Two problems with the current implementation:
1. **Untestable logic.** FAQ items are built inline in the component, so testing requires rendering the whole component (with its MUI dependencies, theme, etc.). Pure functions are trivially testable.
2. **Legal/trust liability.** The current code has a hardcoded "24 hours" cancellation string. Some operators (luxury tours, government permits) have stricter policies (48hrs, 72hrs, no refund at all). A user cancelling a luxury tour within 24hrs, having read the FAQ that promised a refund, has a real case for "misleading representation." Legal risk for SmartEnPlus + the operator.

The hardcoded string is also a maintenance trap: when an operator updates their policy in the admin, the FAQ doesn't update.

## Details
Step 1: extract the builder:

```js
// helpers/experienceFAQBuilder.js
export function buildExperienceFAQItems(contract) {
  return [
    buildCancellationFAQ(contract.cancellation_details),
    buildPickupFAQ(contract.pickup_info),
    buildDurationFAQ(contract.duration_minutes),
    // ... etc
  ];
}

function buildCancellationFAQ(details) {
  return {
    question: 'What is the cancellation policy?',
    answer: buildCancellationSummary(details),
  };
}
```

Step 2: the cancellation summary function derives from structured data:

```js
export function buildCancellationSummary({ refund_window_hours, partial_refund_window_hours }) {
  if (!refund_window_hours && !partial_refund_window_hours) {
    return 'This experience is non-refundable.';
  }
  if (refund_window_hours && partial_refund_window_hours) {
    return `Full refund if cancelled >${refund_window_hours}hrs before. ` +
           `Partial refund if cancelled >${partial_refund_window_hours}hrs before. ` +
           `No refund within ${partial_refund_window_hours}hrs.`;
  }
  if (refund_window_hours) {
    return `Full refund if cancelled >${refund_window_hours}hrs before. ` +
           `No refund within ${refund_window_hours}hrs.`;
  }
  return 'Contact the operator for cancellation details.';
}
```

`cancellation_details` is structured data from the contract model — `refund_window_hours` and `partial_refund_window_hours` are nullable integers. The output reads naturally because the function composes the sentence from the data, not from a template.

Step 3: `ExperienceFAQ.js` becomes:

```jsx
import { buildExperienceFAQItems } from '../helpers/experienceFAQBuilder';

export function ExperienceFAQ({ contract }) {
  const items = buildExperienceFAQItems(contract);
  return <Accordion items={items} />;
}
```

Pure, testable, no business logic in the component.

## Decision
- All FAQ building logic moves to `helpers/experienceFAQBuilder.js` as pure functions
- Cancellation summary is derived from structured `cancellation_details`, never hardcoded
- Component is a dumb renderer (props in, JSX out)
- Add unit tests for each builder function, especially the cancellation edge cases

## Tradeoffs
- Pro: Pure functions are trivially testable
- Pro: Cancellation text reflects actual operator policy (no legal risk)
- Pro: Operator updates flow from admin → contract → FAQ automatically
- Pro: Component is small, easy to read, easy to swap (could move to MDX later)
- Con: More files for the logic to live in (builder, summary, component, tests)
- Con: Pure-function pattern is overkill for FAQ items that never change (e.g., "What language is the tour in?"). Apply selectively — builder functions only for items with operator-specific data.
- Con: The natural-language output of `buildCancellationSummary` may not read as smoothly as a hand-written string. Acceptable trade for correctness.

## Consequences
The pattern is reusable for any contract-derived FAQ item, and for any trust/legal-sensitive content (refund policies, age restrictions, accessibility info). Future FAQs added to the component should follow the builder-function pattern. The component stays presentation-only.

The hardcoded "24 hours" string is a bug — it must be removed AND replaced with a `buildCancellationSummary` call. Any new operator contract without `cancellation_details` populated will render "Contact the operator..." which is correct default behavior (better than a wrong number).

## Related
- [[structured-data-schema-patterns]] — sibling pattern for contract-derived structured data
