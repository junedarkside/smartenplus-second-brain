# Tickets — Support Tickets

## Summary
`Ticket` = support ticket model. GenericForeignKey attaches to any model (BookingItem, Order, Contract, etc.). HistoricalRecords for audit trail.

---

## Model: Ticket

**Fields:**
- `ticket_number` — UUID, auto-generated
- `title`, `description`
- `created_by` FK to User
- `assigned_to` FK (nullable)
- `ticket_status` — Active / Completed / Pending
- `is_resolved` — boolean
- `closed_date` — nullable datetime

**GenericForeignKey:**
```python
content_type = ForeignKey(ContentType)
object_id = PositiveIntegerField()
content_object = GenericForeignKey('content_type', 'object_id')
```

Attaches to any Django model. `BookingItem` has GenericRelation via `ticket` field.

**History:** `HistoricalRecords` — full audit trail of ticket changes.

---

## Usage

- `BookingItem.ticket` GenericRelation — booking can have tickets
- Any model can be ticket target via GenericForeignKey
- Tickets created by users, assigned to support staff

**Planned (CS Centralization — [[cs-centralization-stack]]):** Ticket is the extend target for CS tickets. ⚠️ r2 constraint: GenericFK `content_type`/`object_id` are **non-nullable** (`tickets/models.py:29-30`) → a booking-less account-help ticket cannot be created today; "extend" requires making the FK nullable first.

---

## Related
- [[bookings]] (BookingItem GenericRelation noted)
- [[accounts]] (User model for created_by/assigned_to)
- [[smarten-customer-os-thesis]] · [[cs-centralization-stack]] · [[r2-skeptic-review]] (Ticket = CS extend asset)