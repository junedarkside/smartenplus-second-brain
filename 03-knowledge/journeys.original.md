# Journeys — Analytics Event Tracking

## Summary
`UserJourneyEvent` model tracks user journey events for analytics and monitoring. Flexible event_type + status + metadata. Reference IDs (cart, order, booking) all indexed. Used as dedup guard for email sending via `@log_email_event` decorator.

---

## Model: UserJourneyEvent

**Event types (50 choices):**
- Cart: `cart_created`, `cart_item_added`, `cart_item_updated`, `cart_item_removed`, `cart_abandoned`
- Order: `order_created`, `order_updated`
- Payment: `payment_initiated`, `payment_pending`, `payment_successful`, `payment_failed`, `payment_refunded`
- Booking: `booking_confirmed`, `booking_items_created`
- Email: `email_order_queued`, `email_order_sent`, `email_order_failed`, `email_booking_queued`, `email_booking_sent`, `email_booking_failed`
- Telegram: `telegram_sent`, `telegram_failed`
- Review: `review_invitation_sent`, `review_invitation_failed`

**Status:** `pending`, `success`, `failure`, `warning`

**Fields:**
- `event_type` (indexed), `status` (indexed)
- `user` FK (nullable — cart abandonment may have no user, indexed)
- `metadata` JSONField — flexible event context
- `cart_id`, `order_id`, `booking_slug` (all indexed)
- `timestamp` (indexed)

**Indexes:** 6 composite indexes for common query patterns. Ordered by `-timestamp`.

**Helper:** `metadata_summary` property — extracts important keys (to_email, template_name, subject, duration_ms, error, payment_method, amount, etc.) from metadata.

---

## Usage: Dedup Guard

`@log_email_event(email_type)` decorator on email tasks checks for existing `UserJourneyEvent` with matching `email_*_sent` event_type. Prevents duplicate email sends on task retry.

---

## Related
- [[celery-tasks]] (dedup guard pattern)
- [[orders]] (order_id reference)