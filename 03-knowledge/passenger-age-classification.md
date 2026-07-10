# Passenger Age Classification

## Summary

Passenger age boundaries (Adult/Child/Infant) are pure code convention — rate cards store no age. Boundaries are duplicated in **5 classifier implementations + hardcoded UI copy** across FE/BE/AD. Business change planned 2026-07-10: **Child 3–8, Adult ≥ 9** (adult boundary moves 12 → 9; infant boundary stays < 3).

## Context

- New business rule: `2 < child < 9` → **Infant 0–2 (age < 3) · Child 3–8 · Adult ≥ 9**
- Current canonical (majority of code): Infant < 3 · Child 3–11 · Adult ≥ 12
- `RateCard` values are `ADULT`/`CHILD`/`INFANT` only — ages never stored in DB. Every boundary lives in code or UI copy.
- Full 3-repo scan 2026-07-10 (FE + BE + AD) produced the checklist below.

## Problem

1. **5 duplicated classifiers** — no single source of truth. Any boundary change must touch all 5 or FE/BE disagree.
2. **Pre-existing bug:** FE `helpers/dateHelper.js` uses infant boundary **< 2** while everywhere else uses < 3. A 2-year-old classifies as "Child" in checkout Step 1 validation and account display, but "Infant" in passenger assignment validation and BE booking records — *within the same checkout flow*.
3. **Copy drift:** FE search `Passenger.js` says "Ages 2 to <12"/"Under 2" (matches the dateHelper bug); AD `rateCardConstants.js` says "2-12" (matches neither).

## Details — Change Checklist

### Classifiers (change adult boundary 12 → 9 in all 5)

| # | File | Current | Note |
|---|------|---------|------|
| 1 | BE `bookings/services.py:44-48` `get_age_category()` | ≥12 Adult, ≥3 Child | canonical BE classifier |
| 2 | BE `bookings/services.py:300` | `0 if age >= 12 else (1 if age >= 3 else 2)` | inline sort duplicate |
| 3 | FE `components/forms/checkout/PassengerAssignment.logic.js:31-34` `getAgeCategory()` | ≥12 Adult, ≥3 Child | consumed by `hooks/checkout/useStepValidation.js:106-116` |
| 4 | FE `components/forms/checkout/PassengerAssignment.js:112-116` | inline duplicate of #3 | dedup opportunity: import from `.logic` instead |
| 5 | FE `helpers/dateHelper.js:26-36` `ageCategory()` + `:44-77` `calculateAgeDetailed()` | **Infant <2 (bug)**, Child <12 | fix BOTH boundaries: infant <3, adult <9 |

### FE `dateHelper` consumers (fixed automatically once #5 changes)

- `helpers/checkout/passengerValidationHelper.js` — checkout Step 1 count + age-mismatch warnings
- `pages/account/passenger/PassengersList.js:530` — account age-category display
- `components/forms/checkout/Confirmation.js` · `components/forms/checkout/Passengers.js`
- `components/forms/form-components/DatePicker.js:66` — trip-date age preview (`calculateAgeDetailed` + `formatAgeDetailed`)

### UI copy (hardcoded ranges)

| File | Current | New |
|------|---------|-----|
| FE `components/activities/detail/DayTripBookingWidget.js:435,444` | "Children (3-11 years)" / "Infants (0-2 years)" | "Children (3-8 years)" / unchanged |
| FE `components/cart/EditableCartItem.js:253,260` | same | same fix |
| FE `components/forms/checkout/InlinePassengerSelector.js:255,271` | "3-11 years" / "0-2 years" | "3-8 years" / unchanged |
| FE `components/search/Passenger.js:256,263,270` | "12 and up" / "Ages 2 to <12" / "Under 2" | "9 and up" / "Ages 3 to 8" / "Under 3" |
| AD `components/contracts/rateCardConstants.js:70-71` | "Child (2-12 years)" / "ages 2-12" | "Child (3-8 years)" / "ages 3-8" |
| AD `components/forms/contract/RateCardFields.js:19-20` | "typically 3-11" / "typically 0-2" | "typically 3-8" / unchanged |

### Tests

- FE `__tests__/components/forms/checkout/PassengerAssignment.logic.test.js` + `PassengerAssignment.autoDetect.test.js` — boundary assertions at 12 need updating to 9.

### Does NOT change

- AD `components/booking/BookingItemEditor.js:14-18` + `components/booking/PassengerDetails.js:69-73` — months/days display switches at age 3 (infant boundary unchanged)
- BE `operators/models.py:749-750` `child_rate`/`infant_rate` + `RateCard` values — no age stored
- Cart `adult`/`child`/`infant` fields — counts, not ages
- BE `bookings/tasks.py:257` — reads stored `age_category`, safe

## Consequences

- **Forward-only change.** BE `bookings/models.py:91` denormalizes `passenger_details.age_category` into booking records — historical bookings keep the old classification. No migration needed; do not reclassify past data.
- **Pricing impact:** 9–11-year-olds move from Child rate to Adult rate on all future bookings. Operator contracts/rate cards need no data change (rates keyed by CHILD/INFANT value, not age).
- **Business review flag:** AD `components/contracts/constants.js:85-86` offers trip restrictions `MIN_AGE_5` / `MIN_AGE_12`. Separate concept from classification, but "Minimum age 12" reads oddly once adults start at 9 — confirm with business whether a `MIN_AGE_9` option is wanted.
- **Deploy order:** FE and BE classifiers must ship together (same-day) or checkout assignment validation (FE) and booking records (BE) disagree for 9–11-year-olds.

## Related

- [[README]] — SmartEnPlus 4-repo ecosystem
- [[multi-repo-gap-audit-methodology]] — scan approach used
