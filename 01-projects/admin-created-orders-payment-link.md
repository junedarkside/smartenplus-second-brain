# Admin-created orders with payment link

## Summary
Requirement (2026-11-05): admin creates an order for a logged-in user or a guest (email), sends a payment link, and picks catalog products or adds a custom line for a product that does not exist. Replaces Omise Quick Links, which create orphan payments with no `GatewayCharge`. Reviewed by 3 read-only agents. Nothing built yet.

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
Each step: branch off `develop`, tests, sonnet-or-above review (payment code).

## Finance notes (agent suggestions, mark as unconfirmed)
Self-orders blocked, log who the link was sent to, keep custom charges out of operator settlement, monthly reconcile vs Omise payout. Thresholds the agents named (5,000 / 3,000 / 100 THB) were guesses.

## Related
[[stuck-card-payment-csl4045824]] [[payment-gateway-charge-architecture]]
