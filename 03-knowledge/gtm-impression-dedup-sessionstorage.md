# GTM Impression De-Dup via sessionStorage

## Problem

Component mounts on step 0. User navigates 0→1→0 (back-navigation). Component remounts → `hasFiredViewRef` resets → GTM view event fires again → double-counted impression.

## Solution

Persist fired flag in sessionStorage keyed by cart ID:

```js
const hasFiredViewRef = React.useRef(false);
useEffect(() => {
  if (hasFiredViewRef.current || recommendations.length === 0) return;
  if (sessionKey && sessionStorage.getItem(`${sessionKey}-view-fired`)) return; // de-dup
  hasFiredViewRef.current = true;
  if (sessionKey) sessionStorage.setItem(`${sessionKey}-view-fired`, '1');
  window.dataLayer.push({ event: 'checkout_recommendation_view', ... });
}, [recommendations, sessionKey]);
```

`sessionKey` = `checkout-cross-sell-${cartId}` — unique per cart, clears on new session.

## Also: persist open/closed state

```js
const [isExpanded, setIsExpanded] = useState(() => {
  if (sessionKey && typeof window !== 'undefined') {
    return sessionStorage.getItem(sessionKey) !== 'closed';
  }
  return !collapsed;
});
```

User collapses → navigates back → stays collapsed. Prevents jarring re-expansion.

## Context
SmartEnPlus `CheckoutRelatedTrips.js`, 2026-06-10. BD gate: 60-day GTM measurement.
