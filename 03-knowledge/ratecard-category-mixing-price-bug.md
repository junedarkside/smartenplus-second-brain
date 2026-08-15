---
name: ratecard-category-mixing-price-bug
description: A contract's ratecard array holds one row per passenger/vehicle category (ADULT/CHILD/INFANT/VEHICLE) simultaneously. Math.max/min across all rows picks whichever category has the biggest/smallest number, not the category the contract actually bills — must filter to the correct category first (ADULT for JOIN, VEHICLE for PRIVATE/CHARTER).
type: knowledge-atom
date: 2026-08-15
parent: trip-sort-filter-price-audit
---

# Ratecard Category-Mixing Price Bug

## Summary
`Contract_RateCard` rows are typed (`ADULT`/`CHILD`/`INFANT`/`VEHICLE`) and a single contract legitimately carries several rows at once — one per category it might sell. Any code that runs `Math.max(...ratecard.map(r => r.selling_rate))` or `Math.min(...)` across the whole array treats unrelated categories as competing candidates for "the price," and returns whichever number happens biggest/smallest that day — not the category the contract actually charges the customer for. The correct selector must first filter to one category, based on `contract.type`, then take min/max only within that category.

## Context
Found auditing `/trips/hatyai/koh-lipe` sort tabs (Recommended/Cheapest/Fastest/Early Departure/Top Rated) after a user report that results "didn't seem correct." `components/trips/FilteredTripList.js:97` computed the price used for filter+sort via `Math.max(...contract.ratecard.map(i => i.selling_rate))`. A second, independent copy of the same defect existed in `helpers/getMaxRate.js` (display-side, used by `TripItem.js`), and a third, unreferenced copy in `hooks/useFilteredAndSortedContracts.js` (dead code, deleted).

An earlier version of this same investigation wrongly suspected a *date*-mixing bug too (an off-date surcharge row leaking into today's price) — that was checked and retracted: the backend (`ContractSerializer.to_representation`, `smartenplus-backend/products/serializers.py:332-369`) already resolves ratecard rows to the searched date, per category, before the array reaches the frontend (confirmed reached via `context={'request': request}` in `products/views.py:283-289`, and the frontend always sends `?date=`). Date was never the live bug on this page — only category-mixing was.

## Problem

### Symptom
A JOIN (per-seat) contract today resolves to `[{ADULT, ฿500}, {CHILD, ฿350}, {VEHICLE, ฿1200}]` (the VEHICLE row is leftover/unrelated data on a mixed-transport contract). `Math.max(...)` picks ฿1,200 — a category this contract doesn't even sell tickets by. A user filtering "under ฿1,000" never sees this ฿500 ticket; "Cheapest" ranks it as the most expensive option on the page.

Flip the contract type and the same bug produces the opposite failure: a PRIVATE/CHARTER van with `[{ADULT, ฿300}, {VEHICLE, ฿2000}]` happens to return the right answer (฿2000) via `Math.max` today — but only because 2000 > 300. The method is wrong either way; it just doesn't always show.

### Root cause
No filter step separates "rows that price this contract" from "rows that exist on this contract for some other reason" before the min/max reduction runs.

## Decision

Filter to the category the contract actually bills **before** taking min/max — never across the raw array.

```js
// helpers/utils.js:14-27 — findMinSellingRate, already existed, now reused
export const findMinSellingRate = (routes) => {
  let minSellingRate = Infinity;
  routes?.forEach(route => {
    const isVehicleContract = route.type === 'PRIVATE' || route.type === 'CHARTER';
    route.ratecard?.forEach(rate => {
      const targetType = isVehicleContract ? 'VEHICLE' : 'ADULT';
      if (rate.ratecard === targetType && parseFloat(rate.selling_rate) > 0) {
        const sellingRate = parseFloat(rate.selling_rate);
        if (sellingRate < minSellingRate) minSellingRate = sellingRate;
      }
    });
  });
  return minSellingRate === Infinity ? null : minSellingRate;
};
```

Rule: `type === 'JOIN'` → correct category is `ADULT` (base per-seat fare). `type === 'PRIVATE' | 'CHARTER'` → correct category is `VEHICLE` (per-vehicle charter, price doesn't change with headcount below capacity). CHILD/INFANT rows only matter if computing a full party total (separate, bigger change — needs product decision on total-vs-per-unit display, not done in this pass).

### Fix applied (2026-08-15)
- `components/trips/FilteredTripList.js:97` — `rate: findMinSellingRate([contract])` replaces the inline `Math.max(...)`. Downstream: `sortContractsByRate` (`helpers/tripSorting.js`) now treats `null` (unpriced) as sort-last (`Number.MAX_VALUE`) instead of the old `|| 0` fallback that wrongly sorted unpriced contracts first; `filterContracts`'s price-range check gained an explicit `contract.rate != null` guard (JS coerces `null >= 0` to `true`, which would silently let unpriced contracts through the slider).
- `components/trips/TripItem.js` — replaced `getMaxRate(customSortData(...))` + the old 5-arg `getMainPrice` with a local `mainRatecardRow` memo that filters to the correct category then picks the min-selling-rate row, feeding both the displayed price and the struck-through bar-rate from the *same* row (previously `getMaxRate` picked the row for both, just the wrong row).
- Deleted `helpers/getMaxRate.js` (bug, second instance) and `hooks/useFilteredAndSortedContracts.js` (dead code, same bug, zero consumers — confirmed via grep before deletion).
- `helpers/getMainPrice.js` signature changed from `(contract, currentRateObj, formatCurrencyFunc, customSortDataFunc, getMaxRateFunc)` to `(contract, currentRateObj, formatCurrencyFunc)` — the injected-function indirection had exactly one caller; collapsed to a direct call.

## Still open (not fixed this pass — flagged, needs product/BD input)
- `hooks/useTripPricing.js`'s local `getMinRate` (trip-detail SEO title/description) still takes `Math.min` across the raw, category-mixed array — same bug, `min` instead of `max`, lower severity (SEO copy, not booking price) but not yet touched.
- Whether the displayed/sorted price should become a full party total (`adult_count × ADULT_rate + child_count × CHILD_rate`, matching what checkout actually charges via `components/search/Passenger.js:112-139`) instead of a single per-unit rate — changes what "Cheapest" means whenever child/adult pricing ratios differ across operators. Not an engineering call; needs BD sign-off before building.
- Price-range slider bounds (`hooks/useTripFilters.js:33-36`, seeded from backend `min_rate`/`max_rate`) are themselves category-unaware on the backend side too (`products/views.py:1909-1911` appends every ratecard row's `selling_rate` regardless of type) — `min_display_rate` (line 1913) is the already-correct, category-aware backend field, used elsewhere (`components/trips/RouteFAQ.js:24-25`) but not yet wired into the slider. Deferred alongside the party-total decision above.

## Real-World Triggers (audit checklist)
`grep` for any of these near a `ratecard` array — each is a category-mixing offender:
1. `Math.max(...` or `Math.min(...` directly over `.ratecard.map(...)` or `.ratecard.map(r => r.selling_rate)` with no `.filter()` by `rate.ratecard === <type>` first.
2. `.reduce(...)` over a raw ratecard array picking highest/lowest `selling_rate` without a preceding type filter.
3. Any price helper whose only branch on `contract.type`/`route.type` happens *after* the min/max reduction instead of before it.

Canonical correct pattern (reuse, don't reinvent): `helpers/utils.js` `findMinSellingRate` — the type-filter-then-reduce order is the whole fix.

## Related
- [[currency-context-price-rendering-rule]] — sibling atom from an earlier `/trips/hatyai/koh-lipe` audit; also flagged `getMainPrice`'s old 5-arg signature as "1 caller, not part of the surface area" — that caller is exactly what got simplified in this session's fix.
- `helpers/tripSorting.js` `findLowestSellingRate` — a second, near-duplicate correct implementation (same type-then-reduce logic, used by trip-detail "starting at" pricing) that already existed alongside `findMinSellingRate`; the two should eventually converge on one shared helper rather than staying as parallel correct-but-duplicated implementations.
