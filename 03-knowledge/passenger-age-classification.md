# Passenger Age Classification

## Summary

Passenger age rule: **Infant 0–1 (age < 2) · Child 2–8 (2 ≤ age < 9) · Adult ≥ 9**. Rate cards store no age — boundaries are code convention. Since 2026-07-11 each repo has a **single source of truth constant**; changing boundaries = edit 3 constants (one per repo), nothing else.

## Context

- Business decision 2026-07-10/11: child ends at 8, adult starts at 9 (was Child 3–11, Adult 12+). Infant boundary confirmed at <2 (a 2-year-old is Child).
- Previous state: 5 duplicated classifier implementations + 9 hardcoded copy files across FE/BE/AD with 3-way drift (BE said infant <3; FE dateHelper said infant <2; AD copy said "2-12"). SSOT refactor eliminated duplicates while applying new rule.
- Implemented on branch `feat/passenger-age-ssot` in all 3 repos (FE `c25dcd44`, BE `6ce3742`, AD `037a3f9`).

## The Contract — SSOT locations (keep in sync manually)

| Repo | File | Constant |
|------|------|----------|
| FE | `helpers/dateHelper.js` | `AGE_LIMITS = { CHILD_MIN: 2, ADULT_MIN: 9 }` + `AGE_RANGE_LABELS` + `getAgeCategory(age)` |
| BE | `bookings/services.py` | `CHILD_MIN_AGE = 2`, `ADULT_MIN_AGE = 9` |
| AD | `components/contracts/rateCardConstants.js` | `AGE_LIMITS = { CHILD_MIN: 2, ADULT_MIN: 9 }` |

Future boundary change = edit these 3 files + FE test boundary assertions. Everything else derives.

## Details — what derives from the SSOT

**FE** (`feat/passenger-age-ssot`, commit `c25dcd44`):
- `ageCategory(dob)` + `calculateAgeDetailed()` in dateHelper call shared `getAgeCategory`
- `PassengerAssignment.logic.js` imports/re-exports `getAgeCategory` (old local copy deleted); `PassengerAssignment.js` inline duplicate deleted, imports from `.logic`
- Labels via `AGE_RANGE_LABELS`: DayTripBookingWidget, EditableCartItem, InlinePassengerSelector; search `Passenger.js` derives "9 and up"/"Ages 2 to 8"/"Under 2" from `AGE_LIMITS`
- Consumers unchanged (derive automatically): passengerValidationHelper, PassengersList, Confirmation, Passengers, DatePicker, useStepValidation
- Tests: `PassengerAssignment.logic.test.js` + `autoDetect.test.js` — new boundaries, relative birthdates (`birthDateForAge(n)`) fix date-drift time bombs. 70/70 pass.

**BE** (commit `6ce3742`): `get_age_category()` + `_get_sorted_passengers()` use module constants. Only 2 classifier sites in whole repo (verified by scan).

**AD** (commit `037a3f9`): CHILD/INFANT labels + "under N years old" helper text in rateCardConstants, RateCardFields, SetDefaultRate, RateCardEditModal derive from `AGE_LIMITS`. AD has no classifier code — display only.

## Consequences

- **Deploy FE + BE same day.** Different boundaries between repos = 2-year-olds and 9–11-year-olds classify differently in checkout validation vs booking records.
- **Forward-only.** `bookings/models.py:91` denormalizes `passenger_details.age_category` into booking records — historical bookings keep old classification. No migration; do not reclassify.
- **Pricing impact:** 2-year-olds move Infant→Child rate (pay more); 9–11-year-olds move Child→Adult rate. Operator rate card data unchanged (rates keyed by ADULT/CHILD/INFANT value, not age).
- **Test note:** 1 pre-existing BE test failure (`test_passenger_assignment_fix`, uuid-vs-id assertion) exists on develop, unrelated to this change.

## Open business flags

- AD `components/contracts/constants.js:85-86` trip restrictions `MIN_AGE_5`/`MIN_AGE_12` — does "Minimum age 12" still make sense when adults start at 9? Consider `MIN_AGE_9`.
- AD `BookingItemEditor.js`/`PassengerDetails.js` show months/days for age < 3 (`months < 36`) — display formatting conceptually tied to infant boundary; consider `< 24`. Not changed.

## Related

- [[README]] — SmartEnPlus 4-repo ecosystem
- [[multi-repo-gap-audit-methodology]] — scan approach used
