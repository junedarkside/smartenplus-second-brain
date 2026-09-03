---
name: omise-card-widget-return-uri-redirect
description: Omise's hosted Card.js widget does a full-page cross-origin redirect through api.omise.co (authorize → complete) straight to whatever return_uri the backend passed to Charge.create, immediately after ANY charge attempt resolves — success or fail. This happens before the calling page's own onCreateTokenSuccess promise resolution can update React state, making any in-page result UI (success/fail banners, retry buttons) built around that promise unreachable in practice.
metadata:
  type: knowledge
  status: active
  date: 2026-09-03
  parent: card-decline-dialog-retry
---

# Omise Card Widget `return_uri` Forces a Redirect Regardless of Charge Outcome

## Summary
Any card charge created with `return_uri` set causes Omise's Card.js widget to hard-redirect the browser to that URL once the charge attempt resolves — success or fail, 3DS or not. This is undocumented in Omise's own docs (which describe `return_uri` as "for 3-D Secure only"), but confirmed live: the browser navigated through `api.omise.co/payments/{id}/authorize?acs=false` → `api.omise.co/payments/{id}/complete` and landed on our app's `return_uri` even for a synchronous, non-3DS decline.

## Why It Matters
Any UI built to render inside the checkout page in response to `triggerCardPayment()`'s resolved promise (a failure banner, a retry button, a success message) will build correctly, lint clean, and pass code review — then never actually render for users, because the browser has already navigated away by the time React would update. This is not a bug in the calling code; it's the widget's own behavior. Confirmed via live reproduction with a real Omise test-mode declining card (`4111 1111 1112 0013`) after a backend fix correctly flipped the order to `payment_failed` — the checkout page's own `PaymentFailed` component (data flow verified correct) was never seen because the tab was already mid-navigation.

## Detail
**Symptom:** `onCreateTokenSuccess` in `OmiseCard.open({...})` resolves with the correct result object (`{success: false, cardDeclined: true, ...}`), but any `setState`/conditional render keyed off that result never becomes visible — the page has already redirected.

**Root cause (confirmed, not guessed):** the backend's `create_charge()` passes `return_uri` from the request payload straight into Omise's `Charge.create(...)` call. Omise's server-side charge object carries that URI, and the Card.js widget's iframe (served from `cdn.omise.co`) appears to always send the browser through its `authorize`/`complete` redirect chain once a charge exists with a `return_uri`, independent of whether 3DS was actually triggered.

**Fix (what actually works):** don't fight the redirect — design the result UI for wherever `return_uri` points, not for the checkout page. In this case: a dialog on the order-detail page (`PaymentResultDialog`), gated by `current_charge_status`/`order.status` from the already-fetched order data, shown once per `charge_id` via a sessionStorage flag. Retry re-enters checkout via the order's own `cart` UUID (already present in the orderdetails API response) rather than trying to resume in-place.

**What NOT to do:** don't attempt to strip `return_uri` to keep the user on the checkout page — 3DS-required cards genuinely need it for the bank-redirect step, and there's no reliable way to know in advance whether a given card will trigger 3DS.

## Related
- [[card-decline-dialog-retry]]
