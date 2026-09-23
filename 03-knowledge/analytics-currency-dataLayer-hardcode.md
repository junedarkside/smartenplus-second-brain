---
name: analytics-currency-dataLayer-hardcode
description: GTM/GA4 dataLayer ecommerce events (purchase, add_to_cart, begin_checkout) hardcoded THB or had no fallback, corrupting revenue currency for non-THB viewers. Fixed 2026-09-23. Distinct surface from user-facing price display and JSON-LD — see currency-context-price-rendering-rule for those.
type: knowledge-atom
date: 2026-09-23
parent: multi-market-i18n-analytics-migration
---

# Analytics Currency — dataLayer Ecommerce Event Hardcode

## Summary
GA4/GTM ecommerce events are a **third distinct currency surface**, separate from user-facing price labels (`useFormatPrice()`) and JSON-LD `Offer.priceCurrency` — see `[[currency-context-price-rendering-rule]]` for those two. This note covers only the `dataLayer`/`sendGTMEvent` ecommerce payloads.

## Problem
Found during a codebase audit for the multi-market migration plan (`[[multi-market-i18n-analytics-migration]]`), independent of any migration work — a live bug affecting today's analytics accuracy for any non-THB viewer:

- `purchase` (`hooks/useOmisePayment.js:150`) — `currency: currentRate?.currency` with **no fallback**. If `CurrencyContext`'s async forex fetch hadn't resolved (or had errored permanently), this emitted `currency: undefined` on the **revenue event** — GA4 drops undefined currency, so the purchase loses monetization entirely rather than just mis-reporting it.
- `add_to_cart` (`components/UI/BookButton.js:209`) — hardcoded `currency: "THB"` regardless of the viewer's selected currency.
- `begin_checkout` (`pages/checkout/index.js:524`) — same, hardcoded `currency: 'THB'`.
- `view_cart` (`components/cart/CartButton.js:75,84`) and the now-fixed `purchase` already read dynamically — `CartButton.js:75`'s `currentRate?.currency || 'THB'` was the correct reference pattern, just not copied to the other three sites.

## Decision
Fixed 2026-09-23, branch `fix/analytics-currency-hardcode`, commit `996803eb`. Applied `currentRate?.currency || 'THB'` at all three sites, wiring `useCurrency()` into `BookButton.js` and `checkout/index.js` (neither previously imported it; `useOmisePayment.js` already had `currentRate` as an incoming hook parameter, zero plumbing needed there).

No shared helper extracted — `currentRate?.currency || 'THB'` is a 28-character null-guard with zero branching, fails the "eliminates real complexity" clause of the project's split test. Inlined at all 3 sites, matching the existing `CartButton.js:75` and `useOmisePayment.js:225` precedent.

## Scope boundaries (do not extend this fix to)
- **JSON-LD `Offer.priceCurrency`** (`hooks/useTripPricing.js:45,133`, `hooks/useDayTripSEO.js:172`) — hardcoded THB **by design**, per `[[currency-context-price-rendering-rule]]` Rule 2. Schema describes the merchant's offer in base currency; converting it would break Google Rich Results. A blanket "fix all THB hardcodes" sweep would be wrong here.
- **`hooks/useOmisePayment.js:213-299`** — the actual Omise charge currency validation (`config.currencies` gate) and the JPY zero-decimal special case (`:294-296`, which intentionally has no `'THB'` fallback). Different `currency` usage in the same file; the dataLayer fix must not touch this.
- **`view_item_list`** (`helpers/gtmUtils.js:36-51`) — has no `currency` field AND no `price`/`value` field at all, a different defect class (missing value data, not wrong currency). Needs its own fix threading prices into `formatGtmItem`; not part of this fix.
- **`checkout/index.js:521`'s `begin_checkout` push mechanism** — uses raw `window.dataLayer?.push` instead of the `isGTMEnabled()` + `sendGTMEvent` pattern every other event uses, meaning it fires in dev too. Left alone in this fix (changing it would shift *when* the event fires, a behaviour change, not a parity-preserving currency fix). Tracked separately in `master-state.md`.

## Verification
GA4 DebugView: switch currency via `CurrencySelector`, confirm `add_to_cart`/`begin_checkout`/`purchase` all carry the selected code; confirm a null-context case emits `'THB'` not `undefined`. `git diff hooks/useOmisePayment.js` should show exactly one changed line — if it shows more, the payment blast-radius boundary was violated.

## Related
- [[currency-context-price-rendering-rule]] — the two other currency surfaces (display + JSON-LD)
- [[multi-market-i18n-analytics-migration]] — parent audit this was found under
- [[gtm-purchase-item-category-attribute]] — sibling GTM dataLayer precedent (item_category, not currency)
