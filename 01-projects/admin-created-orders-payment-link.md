# Admin-created orders with payment link

## Summary
Requirement (2026-11-05): admin creates an order for a logged-in user or a guest (email), sends a payment link, and picks catalog products or adds a custom line for a product that does not exist. Replaces Omise Quick Links, which create orphan payments with no `GatewayCharge`. Reviewed by 3 read-only agents. **Status 2026-11-08 (#560): steps 1-4 + expiry + Sentry scrub LIVE in prod (BE `main` `0ce1317`); FE nginx token-log fix LIVE (FE `main` `06d0ef1f`). NOT built: step 5 page, 6, 7, 8. Start next session with step 5 (see sections below).**

## Design (all three agree)
- Admin creates a normal `Order`; customer pays on our own page through a signed, expiring, revocable token (`/pay/<token>`). Every charge goes through our charge path so it gets a `GatewayCharge`.
- Rejected: Omise Quick/Charge Links (orphans, no `GatewayCharge`); faking a cart (`unique_active_ordering_order_per_cart`).
- New: `OrderLineItem(order, kind product|custom, description, unit_price, qty, optional product ref)`, `Order.source`, `Order.created_by`, hashed pay-link token. `ManualAdjustment` (record only, no charge) and `ExtraItem` (integer amount, not in total) do not fit.

## Blockers found (agent code reads, not verified by me)
- B1 order with no bookings cannot be charged (`orders/validators.py:12`, `payments/views.py:120`).
- B2 no customer page pays an existing order; no-booking order looks "not found" (`orders/views.py:704`).
- B3 **underpay, live today:** client sends amount and fee; check `abs((amount-fee)-total)<=1` (`payments/services.py:688`) passes a negative fee and any amount when total is 0/None.
- B4 admin bookings flagged `order_stale` (`payments/order_guards.py:63`).
- B5 paying deletes the user's whole cart (`payments/services.py:398`).
- Major: guest/user ownership rules fit badly for a link; confirmation email reads `booking_item.contract.name` (`orders/utils.py:535`); admin order page and refund assume bookings and read legacy `cards.Charge`; edit after send changes what the old link charges (fix: no edit while `payment_pending`, bump link version).

## Owner decisions (2026-11-05)
No VAT added by system (price typed is final; tax invoice still an accountant question). Customer pays Omise fee (same setting as checkout). No approval step. Coupons later. Operator notice skipped (custom lines notify nobody). Link life 7 days. Refund rules undecided (left out).

## Build plan, one step at a time
1. Fix underpay check (B3), benefits today's checkout. Reproduce in a test first.
2. Order can hold custom lines (DB only).
3. Admin create-order API (no link).
4. Pay-link token, 7 days, send/resend/revoke.
5. Customer `/pay/[token]` page.
6. Admin create-order form + link actions.
7. Admin order page, cancel, refund for custom-only orders.
8. Supplement order (extra charge on an existing order): see section below.

Order to build: 5 -> 7 -> 6 -> 8 (customer can pay first; refund/cancel before the create form so a mistaken order can be undone).
Each step: branch off `develop`, tests, sonnet-or-above review (payment code).

## Finance notes (agent suggestions, mark as unconfirmed)
Self-orders blocked, log who the link was sent to, keep custom charges out of operator settlement, monthly reconcile vs Omise payout. Thresholds the agents named (5,000 / 3,000 / 100 THB) were guesses.

## Related
[[stuck-card-payment-csl4045824]] [[payment-gateway-charge-architecture]]

## Open decisions before step 5 (owner)
- BA6: account-owned orders: block issuing links for them, or show summary + login link.
- Refund rules for custom-only orders (undecided).
- Step 8 open questions: allowed parent statuses; does cancelling/refunding the parent touch supplements (default no); does the supplement email/page show the parent order number.
- Owner checks before deploy: `FRONTEND_URL` in Coolify, `NUM_PROXIES`, FE GitHub secret `NEXT_PUBLIC_VAT`.

## Step 5 plan (copied from session scratchpad, Revision 2 supersedes the first draft where it says so)

**Backend part of step 5 is already merged and LIVE** (`POST /payments/pay-link/resolve/` and `/charge/`, in BE `main` and `develop`; the "in review" wording below is stale). Includes the declined-card attempt cap. Still to build: BA3 (confirmation email for line-item-only orders, separate PR off develop), BA6 decision, and ALL of the frontend page below.

# Step 5 plan: customer pay-link page (`/pay/[token]`) + guest charge

Status: backend built (branch `feat/pay-link-charge`, commit on top of develop, 13 new tests pass, full suite running). Frontend NOT started. Decisions made by owner: token in URL path (A); phase 1 methods = card + PromptPay.

## Backend (done, in review)
- `POST /payments/pay-link/resolve/` {token} -> 200 summary {order_id, state payable|paid, currency, total, email(masked), owner_requires_login, lines[], expires_at} | 404 (unknown/revoked/expired/not payable). Headers no-store + no-referrer. Throttle 60/min.
- `POST /payments/pay-link/charge/` {token, payment_method: credit_card|debit_card|promptpay, card_token?} -> 201 charge body (same shape as order-charge: charge_id, authorize_uri, qr_code_uri/qr_code_image, expires_at, grand_total, currency THB, polling_interval) | 400 unsupported_method|card_token_required|amount_too_low | 403 login_required (order owned by an account) | 404 | 409 order_already_paid|payment_pending|amount_locked|... Amount, fee, currency, return URL are server-made. Card return_uri = `{FRONTEND_URL}/pay/<token>`. Throttle 20/min.
- Open: raw token sits in the Omise-stored return_uri (reviewer: medium). Candidate fix: revoke link when order is paid.
- Not covered: how the page learns the charge status after PromptPay scan or 3DS return (see F4).

## Frontend (to build; branch `feat/pay-link-page` off develop)
F1 `pages/pay/[token].js` (Pages Router, client-side fetch, NO getServerSideProps/getStaticProps so the token never appears in server-rendered props or ISR cache). States: loading, invalid/replaced (404), payable, paid, login-required, charge-in-progress (PromptPay QR / 3DS redirect), error.
F2 Summary card: order id, line items (description, qty, unit price, total), total THB, masked email. All text via `useT()` with en+th keys in a new `helpers/i18n/strings/payLink.{en,th}.js`, registered in strings/en.js + th.js.
F3 Pay buttons: card (Omise.js tokenization via existing OmiseScriptLoader, then POST charge, redirect to `authorize_uri` for 3DS) and PromptPay (POST charge, show QR with countdown from backend `expires_at`, poll). Reuse existing `QRPaymentForm`/polling pieces if their props allow; else a small dedicated component. Do NOT reuse `useOmisePayment` (it is wired to cart/checkout Redux and `resetCart`; never call resetCart here).
F4 Status after pay: PromptPay: poll `resolve` (state paid) every `polling_interval` while the QR is live. 3DS return: Omise sends the customer back to `/pay/<token>`; page re-resolves; `paid` -> success view; `payable` -> "payment not completed, try again" (charge may still be settling: show a short "checking" state before failure text). Treat `payment_pending` 409 as "payment in progress", not an error.
F5 `owner_requires_login`: show summary + "log in as the account holder to pay" with a login link that returns to the page. No pay buttons for anonymous users. (Paying itself for account orders goes through existing authenticated `order-charge`, which is NOT part of this step; if not wired, say "please sign in on the website" and stop. Decision needed.)
F6 Hardening of the page:
  - `<meta name="robots" content="noindex,nofollow">` (AuthHead alwaysNoindex pattern, in loading branch too).
  - Response header for `/pay/:path*` in next.config.js: `Referrer-Policy: no-referrer`, `Cache-Control: no-store`. The site-wide rule is `origin-when-cross-origin` (leaks full URL on same-origin requests) so the more specific rule must win.
  - GTM: `_app.js` loads GoogleTagManager globally; GTM reports page_location (with token) to Google. Do not load GTM / analytics on `/pay/*`; no custom events carrying the URL.
  - Never put the token in client logs, `console.*`, error toasts, Sentry breadcrumbs. Strip the token from any Sentry/URL capture (FE has no Sentry dep found; verify). Backend Sentry `before_send` scrub of `/pay/<token>` request URLs is a separate backend task.
  - After resolve, optionally `history.replaceState` to keep the token from staying in the visible URL? (Rejected: the 3DS return and refresh need it. Keep.)
  - Use `fetch` with the token in the POST body only; never in query string.
F7 Tests: jest for the page states (resolve 404 -> "link replaced", paid, login-required, payable), card flow (token + 201 + redirect), PromptPay flow (QR shown, poll -> paid), 409 handling, i18n key parity (`i18nStrings.test.js`), no analytics script on the page.

## Token-in-logs scrub (backend, separate small PR)
nginx access log: use `$uri` without args does not help (token is in the path). Options: log format that replaces `/pay/<token>` with `/pay/[redacted]` via a `map`; Sentry `before_send` redacting `/pay/` URLs and `pay-link` request bodies; Django request logger (`log Not Found: /payments/pay-link/resolve/` shows only the API path, token is in body, fine). Frontend nginx/Next access logs show `/pay/<token>` -> needs the nginx `map`. Owner owns nginx config (CSP is in nginx/sites-available); this is an ops change to hand to the owner.

## Order of work
1. Backend review fixes + full suite green + commit (in progress).
2. Frontend F1-F7 on `feat/pay-link-page`, jest for touched files, `npm run build`.
3. Nginx/Sentry scrub PR (backend + ops note).
4. Reviewer pass (sonnet+) on FE + BE together, owner merges to develop when told.

## Out of scope
Admin UI (steps 6, 7), supplement orders (step 8), non-card/PromptPay methods, multi-currency (admin orders are THB only), PR4 alert-only handlers.

---
# Revision 2 (after FE-feasibility + security review)

Replaces: "revoke on paid" idea, F3 reuse of useQRPolling/QRPaymentForm, F6 header/GTM details, F4 status flow.

## Backend additions (on feat/pay-link-charge unless noted)
BA1 Post-payment expiry: in finalize_payment success, `link.expires_at = min(expires_at, now+1h)` (keeps resolve state=paid for the success page, kills token copies in Omise/history/chat within 1h). Paid summary trimmed to order_id, state, total (no lines, no masked email).
BA2 Card-testing cap: in pay_link_charge_spec count the order's failed/expired GatewayCharge in last hour; >=5 -> 429 too_many_attempts.
BA3 (separate PR off develop, existing bug) Paid-order confirmation email for line-item-only admin orders: orders/utils.py:516-599 builds from BookingItem only, so total = fee only. Use order.get_total_cost_after_discount() + line items for source='admin'. Add finalize test with cart-less/booking-less admin order. Also verify Payment(user=None) is allowed (payments/services.py:894).
BA4 Param cut (done, uncommitted): pay_link_charge_spec(link, request_data), _success_body(order, spec, started).
BA5 Scrub: Sentry before_send redact /pay/ URLs + pay-link request data; confirm no logger prints request.data in these views. nginx `map` to redact /pay/<token> in access log (owner ops).
BA6 account-owned orders: decision pending (block issuing links for them vs summary + login link).

## Frontend (branch feat/pay-link-page)
- `_app.js`: when `router.pathname.startsWith('/pay/')` skip GTM, page_view push, ChatWidget, CookieConsentBanner, RefreshTokenHandler, CartMergeConflictContainer, full Layout; test it.
- New `usePayLinkPolling` (calls resolve, stops on paid / expires_at / unmount). Do NOT touch useQRPolling. useQRTimer reusable. QR image: small new presentational piece.
- 3DS return: set sessionStorage flag before redirect; on return poll resolve every 4s up to ~60s, then "not completed, try again". Handle 409 `pending_charge_exists` by resuming its authorize_uri; `payment_pending` = in progress. 404 text differs from network-error text.
- After state=paid: history.replaceState to /pay/done.
- Headers: next.config.js `/pay/:path*` rule placed AFTER `/(.*)`; nginx location ^~ /pay/ (hide upstream Referrer-Policy, add no-referrer, repeat HSTS/CSP/XFO); meta referrer no-referrer. Verify with curl.
- Split: pages/pay/[token].js + components/payLink/{Summary,PayButtons,QrPanel} + hooks/usePayLink; reducer/lookup instead of nested ifs; double-click guard; card popup onFormClosed; clear timers on unmount; AuthHead alwaysNoindex, no duplicate robots with DefaultSeo; generic OG; no cart reset / createCart.
- i18n: payLink.{en,th}.js for all error codes (amount_too_low, login_required, too_many_attempts, ...); do not reuse chargeConflict.js messages.

## Step 8 plan (copied from session scratchpad)

# Step 8: supplement order (extra charge on an existing order)

Owner decisions (2026-11-06): separate order and separate payment (yes); done as step 8, after steps 4 to 7; customer pays the Omise fee on the supplement amount, same as every order.

## Why not edit the existing order
- A paid order is finalized; its refunds hang off its own charge.
- User-wide payment guards (payment_pending, order_stale) would collide with a second payment on the same order.

## Design
- A supplement is a normal admin order (step 3: custom lines, source 'admin') plus a link to the original.
- New nullable field `Order.parent_order` (FK to self, SET_NULL or PROTECT, related_name 'supplements'). One migration.
- Own pay link (step 4), own charge, own fee (computed on the supplement total only), own refund (step 7).
- Parent must exist, belong to the same customer (same user, or same guest email), and not be cancelled. Rule for parent status (paid only, or any open status) is an open question.
- Admin order page (step 7) lists supplements under the parent; customer page (step 5) shows the link to the original order number.

## Known costs
- Customer pays a second fee. Mobile banking is a flat 10.70, so small supplements carry a large share of fee.
- Reports: supplement revenue must not mix into operator payout (same rule as custom lines).

## Open questions for later
- Allowed parent statuses.
- Does cancelling or refunding the parent touch supplements (default: no, independent).
- Does the supplement email/page reference the parent order number.
