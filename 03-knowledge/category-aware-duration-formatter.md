# Category-Aware Duration Formatter

## Summary
One helper formats a contract's duration per `service_category`; never lets a non-tour product display "X Days".

## Problem
Activities pages hardcoded `contract.tour_duration_days` (backend `PositiveIntegerField`, **default `1`**, in days) formatted as `"X Day(s)"` for **every** service category. So a spa (60–120 min) showed **"1 Day"** — user-reported nonsense. Worse: the public **list** serializer omits `tour_duration_days`, so browse cards saw `undefined` → ternary always fell through to `"1 Day"`. Same inline ternary was copy-pasted in 5 places (3 render components + 2 SEO JSON-LD builders), so any fix had to be centralized or it would drift.

## Decision
New `helpers/formatContractDuration.js` — single source of truth. `formatContractDuration(contract) -> string | null`. `null` = render nothing (callers gate with `{text && ...}`; `WhyTravelersLove` already `.filter(Boolean)`s its card array). Never throws (warns) per repo rule.

Gated by the **existing** `SERVICE_CATEGORY_CONFIG.showDuration` in `helpers/serviceCategoryHelper.js`, plus one new additive field `durationUnit`:

| Category | durationUnit | Output |
|---|---|---|
| DAY_TOUR / MULTI_DAY_TOUR / TRANSPORTATION | `days` | "3 Days" / "1 Day" (null if absent — no false "1 Day") |
| SPA_WELLNESS / FOOD_DINING | `time` | "2h 30m" from `duration` field |
| ACCOMMODATION | `nights` | "2 nights" |
| EVENT_TICKET / ATTRACTION_TICKET | (showDuration false) | hidden |
| OTHER | (flipped showDuration → false) | hidden — don't guess |

## Key facts (reusable)
- Backend `Contract.duration` is a `DurationField` set from `"HH:MM"` via `convert_to_timedelta` (`operators/views.py:1074`). DRF serializes it as **Django `str(timedelta)` = colon string** `"2:30:00"` — **NOT ISO8601** `"PT2H30M"`. So `customFormatDuration` (`helpers/formatTime.js`, splits on `:`) parses it directly. No ISO parser needed. (If a value ever comes back ISO8601, the helper's `|| null` guard prevents garbage.)
- `customFormatDuration('')` / zero → returns `'0m'`, not null — helper treats `'0m'` as null.
- Public LIST serializer (`ContractSerializer`) exposes `duration` but **not** `tour_duration_days`; DETAIL uses `fields='__all__'`. Hence frontend-only fix: day-tour cards omit day-count rather than lie. Showing "N Days" on browse cards needs backend Option B (add field to list serializer + ISR cache clear) — deferred follow-up.

## Tradeoffs
- Chose frontend-only (no backend deploy) → day-tour browse cards may omit duration when list lacks the field. Acceptable: omission > false "1 Day".
- Reused `customFormatDuration` + `SERVICE_CATEGORY_CONFIG` instead of new parser/config → minimal blast radius. Only behavior change: `OTHER.showDuration` true→false (read by `getSafeBookingData` too — correct: unknown category shouldn't claim a duration).

## Files
- new `helpers/formatContractDuration.js`
- `helpers/serviceCategoryHelper.js` (added `durationUnit`, flipped `OTHER.showDuration`)
- call sites: `components/activities/browse/DayTripCard.js`, `components/activities/detail/DayTripDetailHeader.js`, `components/activities/detail/WhyTravelersLove.js`, `helpers/seo/dayTripSEOUtils.js`, `hooks/useDayTripSEO.js`

## Related
- [[transportation-category-audit]]
- [[build-experience-faq-items-pure-function]] — same pattern: derive display text from structured contract data, central pure helper
