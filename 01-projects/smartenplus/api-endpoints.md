# API Endpoints — SmartEnPlus

## Summary
Django REST Framework API. Public, payment, cart/order, and admin endpoint groups. Language via `Accept-Language` header (12 langs: en, th, zh, ja, ko, es, fr, de, ru, ar, ms, vi). Auth: token-based (API), session-based (admin).

---

## Public Endpoints

### Tours & Contracts
- `GET /contract/` — list all active contracts. Query params: `?service_category=&operator=`.
- `GET /product-detail/{slug}/` — tour detail page by slug.
- `GET /contract/{id}/availability/?date=YYYY-MM-DD&people=N` — check availability. ID (not slug). Returns time slots + capacity.

### Auth
- `POST /api/auth/force-logout` — force logout (session invalidation). No auth required.
- `GET/PUT /api/user/` — self-profile read + update (token auth, no ID). Backend: `UserAPIView` (`RetrieveUpdateAPIView`). Frontend: `pages/account/profile.js`.
- `GET/PUT /api/users/{id}/` — admin-only (`IsAdminOrIsStaff`) since 2026-05-07.

---

## Payment Endpoints

- `POST /payments/order-charge/` → `ChargeOrderView` — initiate charge for an order. Body: `{order_id, payment_method, amount, currency}`. Creates `GatewayCharge`. Idempotent via `IdempotencyKey`.
- `POST /payments/webhook/` → `OmiseWebhookView` — Omise event receiver. Handles `charge.*`, `paymentlinking.*` events. WebhookEvent audit saved outside atomic.
- `POST /payments/order-charge/{charge_id}/expire/` → `ExpirePendingChargeView` — cancel pending QR charge. 6-case behavior table in [[payment-system]].
- `GET /payments/docs/` → Redoc API viewer (staff only). Spec: `payments/openapi.yaml`.
- `POST /payments/charge/` → `ChargeCreateView` — create charge directly (legacy).
- `GET /payments/charge/{gateway_charge_id}/` → `ChargeDetailView` — get charge details.
- `POST /payments/refund/` → `RefundCreateView` — create refund.
- `GET /payments/refund/{gateway_refund_id}/` → `RefundDetailView` — get refund details.

---

## Cart & Order Endpoints

- `GET /api/orders/{id}/` — order details + polling fallback for 3DS. Returns order with `GatewayCharge` status. If PAID → `finalize_payment()`. If PENDING → `reconcile_gateway_charge()` + `_sync_order_status()`.
- `POST /api/carts/{id}/cartitems/` — add item to cart.
- `PATCH /api/carts/{id}/cartitems/{item_id}/` — update cart item (passengers, date, time slot).
- `DELETE /api/carts/{id}/cartitems/{item_id}/` — remove item from cart.
- `POST /api/orders/` — create order from cart. Returns `Order` with `status=ordering`.

---

## Admin Endpoints

### Operators
- `POST/PATCH/DELETE /admin-dashboard-operators/contract-details/{slug}/` — CRUD contract.
- `POST /admin-dashboard-operators/contract-details/{slug}/copy/` — duplicate contract.

### Orders (admin)
- `GET /admin-dashboard-orders/order-summary/` — list orders (paginated).
- `GET /admin-dashboard-orders/order-detail/{order_id}/` — order detail.
- `POST /admin-dashboard-orders/order-detail/{order_id}/resend-confirmation-email/` — resend confirmation email.

### Charges (admin)
- `POST /admin-dashboard-charge/manual-adjustment/` — `ManualAdjustment`. Payload: `{order_id_str, amount, reason, note, extra_item_slug}`. Permission: `IsAdminOrIsStaff`. Replaces `ExtraItemAction`.

### Webhooks (admin)
- `POST /admin-dashboard-orders/payments/webhook/` — Omise webhook (same view as `/payments/webhook/`).
- `POST /admin-dashboard-orders/payments/webhook-legacy/` — legacy webhook (to be removed).

### Coupons
- `POST /admin-dashboard-orders/apply-coupon/` — apply coupon to order.
- `POST /admin-dashboard-orders/remove-coupon/` — remove coupon from order.

---

## Deprecated

- `GET /payments/stripe-webhook/` → 410 "Stripe not supported". Remove after confirming zero prod traffic.

---

## Related
- [[backend-architecture]]
- [[payment-system]] (payment endpoint details)
- [[cart]] (cart endpoints)
- [[bookings]] (booking lifecycle)