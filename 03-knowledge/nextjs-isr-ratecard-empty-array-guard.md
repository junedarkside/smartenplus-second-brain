# Next.js ISR Ratecard Empty Array Guard

## Summary
`??` operator doesn't catch empty array `[]` — CSR response with `ratecard: []` wipes valid ISR data.

## Why It Matters
Active revenue risk. User sees ISR price in hero, CSR refresh returns empty ratecard, page crashes to "Pricing Unavailable" mid-session. Booking abandonment.

## Detail
```js
// WRONG — passes empty array through ??
ratecard: freshContract.ratecard ?? productData?.ratecard,

// CORRECT — treats empty array same as null/undefined
ratecard: (freshContract.ratecard?.length > 0)
  ? freshContract.ratecard
  : productData?.ratecard,
```

`??` only catches `null`/`undefined`. API returning `{ ratecard: [] }` passes the guard → `lowestRate` becomes `null` → entire page unmounts to error screen.

## Constraints / Gotchas
- Applies to any ISR/CSR merge where CSR can return empty arrays for valid ISR data
- General rule: use `?.length > 0` guard when merging array fields from CSR into ISR baseline
- File: `pages/trips/detail/[...slug].js` line ~89–102

## Related
- [[nextjs-patterns]]
- [[trip-detail-deep-review-2026-05-20]]
