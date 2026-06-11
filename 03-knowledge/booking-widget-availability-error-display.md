# Booking Widget Availability Error Display

## Summary

`DayTripBookingWidget` Alert renders 6 availability error cases. Missing any case = blank red box shown to user — no explanation.

## Problem

`useDayTripAvailability` returns 6 error flags. Original Alert only rendered 4:

```jsx
// MISSING — caused blank error UI
{availability.errors.nonOperatingDay && ...}
{availability.errors.advanceHourPassed && ...}
```

User selecting a date past the advance booking deadline saw a red alert with no text.

## Fix

Both constants exist in `AVAILABILITY_ERROR_MESSAGES` (`constants/dayTripConstants.js`).
`ADVANCE_HOUR_PASSED` was missing from the constants file — added.
Both lines added to Alert in `DayTripBookingWidget.js`.

## Advance Hour Logic

`advance_hr` stored as Django DurationField string: `"2 days, 0:00:00"` or `"12:00:00"`.
`convertAdvanceHourFormat()` parses both formats → total hours.
`hasAdvanceHourPassed2(date, departureTime, advance_hr)` — uses **local browser time** (no TZ conversion). Correct for Thai users (BKK = UTC+7). Latent drift for EU/US users — acceptable for Thai market.

### Advance Hour Calculation

```
deadline = trip.departure_datetime - advance_hr
if now > deadline → advanceHourPassed = true → isAvailable = false
```

Example: `advance_hr=2 days`, departure `08:00` on 06/13 → deadline = 06/11 08:00. Booking on 06/11 20:20 → blocked.

## Full Error Flag → Message Map

| Flag | Message key | Message |
|------|-------------|---------|
| `inactive` | `CONTRACT_INACTIVE` | "This tour is currently unavailable" |
| `beforeStart` | `DATE_BEFORE_START` | "This tour has not started yet" |
| `afterEnd` | `DATE_AFTER_END` | "This tour has ended" |
| `stopSale` | `STOP_SALE_DATE` | "Bookings not accepted for this date" |
| `nonOperatingDay` | `NO_OPERATIONAL_DAY` | "Not operating on this day of week" |
| `advanceHourPassed` | `ADVANCE_HOUR_PASSED` | "Booking deadline has passed for this date" |

## Files

- `components/activities/detail/DayTripBookingWidget.js` — Alert render
- `constants/dayTripConstants.js` — `AVAILABILITY_ERROR_MESSAGES`
- `hooks/useDayTripAvailability.js` — availability logic
- `helpers/checkAdvanceHour.js` — `hasAdvanceHourPassed2`, `convertAdvanceHourFormat`

## Related

[[recommendation-type-selection-by-service-category]] · [[operators]]
