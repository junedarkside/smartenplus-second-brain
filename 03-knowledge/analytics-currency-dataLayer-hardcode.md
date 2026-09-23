---
name: analytics-currency-dataLayer-hardcode
description: GTM/GA4 dataLayer ecommerce events (purchase, add_to_cart, begin_checkout) hardcoded THB or had no fallback, corrupting revenue currency for non-THB viewers. Fixed 2026-09-23; same-day addendum found and fixed a follow-on bug where begin_checkout's currency label was fixed but its value/price fields stayed raw THB, unconverted. Distinct surface from user-facing price display and JSON-LD — see currency-context-price-rendering-rule for those.
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

## Addendum: fixing the currency label alone made begin_checkout worse (found + fixed 2026-09-23, same day)

This fix corrected `begin_checkout`'s `currency` field but left `value`/`price` unconverted — the event's **numeric value was never in scope of this fix and stayed raw THB**. Post-fix the event said e.g. `{currency:"USD", value: 3500}` where `3500` was still baht — a self-contradicting payload, and *worse* than the pre-fix state (`{currency:"THB", value: 3500}`, wrong label but at least an internally consistent number). A BD-lens review caught this as a live-revenue-analytics risk before the branch reached `main`: inflated non-THB checkout values are exactly the shape that misdirects funnel/abandonment analysis, and GA4 history can't be corrected after the fact.

**Root cause of why this fix didn't catch it**: `value`/`price` are a *fourth* money field, not currency — this note's scope was explicitly "currency field only" (see Decision above), and the value-conversion gap was a separate, pre-existing defect (`value`/`price` were already `undefined` before this fix too, since the source fields referenced — `data.total_price`/`item.total_price` — don't exist in the cart API response at all).

**Fixed same day**, commit `9055a9bd`, branch `fix/analytics-begin-checkout-value-conversion`:
```js
const exchangeRate = (currentRate?.rate && currentRate.rate > 0) ? currentRate.rate : 1;
// currency: currentRate?.currency || 'THB',  (unchanged, from this fix)
value: data.grand_total / exchangeRate,        // was: data.total_price (field didn't exist)
price: item.sub_total / exchangeRate,          // was: item.total_price (field didn't exist)
```
Real field names (`grand_total`, `sub_total`) confirmed against the backend `CartSerializer`/`CartItemSerializer` and a same-file precedent (`checkout/index.js:1192` already reads `data.grand_total` for the sidebar total). The rate guard matches `CartButton.js:76`'s `(rate && rate > 0)` pattern rather than a bare `|| 1`, since `rate` arrives as a stringified Decimal from DRF and a corrupt `"0.000000"` would pass a truthy check. Live-verified with a real booking: `value`/`price` both captured as `1000` (finite), matching the `THB 1,000.00` shown in the Cart Summary sidebar for that cart.

**Lesson for future currency-surface fixes**: currency *label* and monetary *value* are two separate fields that must be verified together. Fixing one without checking the other can make an event actively misleading rather than merely incomplete — as happened here.

**Still not fixed, found during this addendum's review, separate tickets**: `begin_checkout`'s `item_id` uses the cart-item ID instead of `contract.id` (inconsistent with `add_to_cart`/`view_cart`/`purchase`); its `quantity` reads `item.children` instead of the serializer's `item.child` field.

## Related
- [[currency-context-price-rendering-rule]] — the two other currency surfaces (display + JSON-LD)
- [[multi-market-i18n-analytics-migration]] — parent audit this was found under
- [[gtm-purchase-item-category-attribute]] — sibling GTM dataLayer precedent (item_category, not currency)
